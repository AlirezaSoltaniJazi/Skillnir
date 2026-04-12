"""Notification provider registry, validators, and credential schemas.

Supported providers:

- Google Chat (incoming webhook)
- Slack (incoming webhook)
- Discord (webhook)
- Microsoft Teams (Power Automate workflow HTTP trigger)
- Telegram (Bot API — uses ``bot_token`` + ``chat_id``)
- Zoho Cliq (incoming webhook, regional hosts)

Each provider is a :class:`ProviderSpec` in :data:`PROVIDERS`.  Validators
are strict HTTPS + host-allowlist checks to block plaintext leaks and
SSRF-adjacent schemes (``http://``, ``file://``, ``ftp://``, userinfo
masquerades, suffix-forgery tricks).

This module has no network side effects — validators are pure functions.
Senders live in :mod:`skillnir.notifications.senders`.
"""

from __future__ import annotations

import re
import urllib.parse
from dataclasses import dataclass
from enum import Enum
from typing import Callable

# ---------------------------------------------------------------------------
# Provider identity
# ---------------------------------------------------------------------------


class NotificationProvider(str, Enum):
    """Stable provider identifiers.

    Subclasses ``str`` so values round-trip cleanly through JSON /
    ``AppConfig.active_provider`` without explicit coercion.
    """

    GCHAT = "gchat"
    SLACK = "slack"
    DISCORD = "discord"
    TEAMS = "teams"
    TELEGRAM = "telegram"
    CLIQ = "cliq"


# ---------------------------------------------------------------------------
# Generic URL validators (stateless, reusable)
# ---------------------------------------------------------------------------


def _parse_https(url: str) -> urllib.parse.SplitResult | None:
    """Return a parsed URL iff the scheme is https and parsing succeeded."""
    if not url:
        return None
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if parts.scheme != "https":
        return None
    return parts


def _validate_https_host_exact(url: str, host: str) -> bool:
    """True iff ``url`` is ``https://<host>/...`` (case-insensitive)."""
    parts = _parse_https(url)
    if parts is None:
        return False
    return (parts.hostname or "").lower() == host.lower()


def _validate_https_host_in(url: str, hosts: frozenset[str]) -> bool:
    """True iff ``url`` host is one of ``hosts`` (case-insensitive)."""
    parts = _parse_https(url)
    if parts is None:
        return False
    return (parts.hostname or "").lower() in hosts


def _validate_https_host_suffix(url: str, suffix: str) -> bool:
    """True iff ``url`` host ends with ``suffix`` (leading-dot enforced).

    ``suffix`` must start with a dot (e.g. ``.logic.azure.com``). Blocks
    forgery like ``evillogic.azure.com`` by requiring a literal dot
    boundary before the suffix.
    """
    if not suffix.startswith("."):
        raise ValueError(f"suffix must start with '.': {suffix!r}")
    parts = _parse_https(url)
    if parts is None:
        return False
    host = (parts.hostname or "").lower()
    return host.endswith(suffix.lower()) and len(host) > len(suffix)


# ---------------------------------------------------------------------------
# Per-provider credential validators
# ---------------------------------------------------------------------------

# Google Chat
_GCHAT_HOST = "chat.googleapis.com"


def is_valid_gchat_webhook(url: str) -> bool:
    """Return True iff ``url`` is an ``https://chat.googleapis.com/...`` URL.

    Preserved at module level for backward compatibility with existing
    imports in :mod:`skillnir.notifier` and :mod:`skillnir.ui.pages.settings`.
    """
    return _validate_https_host_exact(url, _GCHAT_HOST)


# Slack
_SLACK_HOST = "hooks.slack.com"


def is_valid_slack_webhook(url: str) -> bool:
    """True iff ``url`` is an ``https://hooks.slack.com/...`` URL."""
    return _validate_https_host_exact(url, _SLACK_HOST)


# Discord
_DISCORD_HOSTS = frozenset({"discord.com", "discordapp.com"})


def is_valid_discord_webhook(url: str) -> bool:
    """True iff ``url`` host is ``discord.com`` or ``discordapp.com``."""
    return _validate_https_host_in(url, _DISCORD_HOSTS)


# Microsoft Teams (Power Automate workflow HTTP trigger)
_TEAMS_HOST_SUFFIX = ".logic.azure.com"


def is_valid_teams_webhook(url: str) -> bool:
    """True iff ``url`` host ends in ``.logic.azure.com`` (exact dot boundary).

    Power Automate workflow webhook URLs look like
    ``https://prod-20.westus.logic.azure.com/workflows/<id>/...``.
    The leading-dot requirement blocks forgery like
    ``https://evillogic.azure.com/...``.
    """
    return _validate_https_host_suffix(url, _TEAMS_HOST_SUFFIX)


# Zoho Cliq (regional hosts)
_CLIQ_HOSTS = frozenset(
    {
        "cliq.zoho.com",
        "cliq.zoho.eu",
        "cliq.zoho.in",
        "cliq.zoho.com.au",
        "cliq.zoho.com.cn",
        "cliq.zoho.jp",
        "cliq.zoho.sa",  # Saudi Arabia (on Zoho roadmap — future-proof)
        "cliq.zohocloud.ca",  # Canada
    }
)


def is_valid_cliq_webhook(url: str) -> bool:
    """True iff ``url`` host is a known Cliq region AND has a ``zapikey`` query param.

    Cliq incoming webhooks always carry ``?zapikey=...`` — requiring it
    catches obviously malformed URLs at validation time.
    """
    parts = _parse_https(url)
    if parts is None:
        return False
    host = (parts.hostname or "").lower()
    if host not in _CLIQ_HOSTS:
        return False
    query = urllib.parse.parse_qs(parts.query)
    return bool(query.get("zapikey"))


# Telegram — no URL from user; validate the (bot_token, chat_id) pair
_TELEGRAM_TOKEN_RE = re.compile(r"^\d+:[A-Za-z0-9_-]{30,}$")
_TELEGRAM_CHAT_ID_RE = re.compile(r"^(-?\d+|@[A-Za-z][A-Za-z0-9_]{4,})$")


def is_valid_telegram_token(token: str) -> bool:
    """True iff ``token`` matches Telegram bot token format ``<digits>:<base62>``."""
    if not token:
        return False
    return bool(_TELEGRAM_TOKEN_RE.match(token))


def is_valid_telegram_chat_id(chat_id: str) -> bool:
    """True iff ``chat_id`` is a signed int or ``@username`` (>=5 chars)."""
    if not chat_id:
        return False
    return bool(_TELEGRAM_CHAT_ID_RE.match(chat_id))


# ---------------------------------------------------------------------------
# Uniform validator interface — all providers adapt to a single signature
# so :class:`ProviderSpec` can hold them without special-casing.
# ---------------------------------------------------------------------------


def _validator_single_url(
    check: Callable[[str], bool],
) -> Callable[[dict[str, str]], tuple[bool, str | None]]:
    """Wrap a single-URL validator into the dict-based ProviderSpec signature."""

    def _run(creds: dict[str, str]) -> tuple[bool, str | None]:
        url = (creds.get("url") or "").strip()
        if not url:
            return False, "webhook URL not set"
        if not check(url):
            return False, "invalid webhook URL"
        return True, None

    return _run


def _validate_telegram_creds(creds: dict[str, str]) -> tuple[bool, str | None]:
    """Validate Telegram's two-secret credential dict."""
    bot_token = (creds.get("bot_token") or "").strip()
    chat_id = (creds.get("chat_id") or "").strip()
    if not bot_token:
        return False, "bot token not set"
    if not is_valid_telegram_token(bot_token):
        return False, "invalid bot token format"
    if not chat_id:
        return False, "chat ID not set"
    if not is_valid_telegram_chat_id(chat_id):
        return False, "invalid chat ID format"
    return True, None


# ---------------------------------------------------------------------------
# Provider registry
# ---------------------------------------------------------------------------

# Forward-declared Callable so senders.py can populate after import;
# avoid circular imports by binding the senders lazily.
SenderFn = Callable[
    [dict[str, str], str, "str | None", float],
    tuple[bool, "str | None"],
]


@dataclass(frozen=True)
class ProviderSpec:
    """Everything the UI + dispatch loop need to handle a provider uniformly."""

    id: NotificationProvider
    display_name: str
    icon: str  # Material icon name (matches BackendInfo.icon convention)
    credential_fields: tuple[str, ...]
    validator: Callable[[dict[str, str]], tuple[bool, str | None]]
    sender: SenderFn
    help_url: str


def _build_registry() -> dict[NotificationProvider, ProviderSpec]:
    """Assemble the registry. Imported lazily to avoid circular deps."""
    # Import senders here to break the providers <-> senders cycle.
    # senders.py imports the validators above; we import the sender
    # functions inside this builder.
    from skillnir.notifications import (
        senders,
    )  # pylint: disable=import-outside-toplevel

    return {
        NotificationProvider.GCHAT: ProviderSpec(
            id=NotificationProvider.GCHAT,
            display_name="Google Chat",
            icon="chat",
            credential_fields=("url",),
            validator=_validator_single_url(is_valid_gchat_webhook),
            sender=senders.send_gchat_notification_spec,
            help_url="https://developers.google.com/workspace/chat/quickstart/webhooks",
        ),
        NotificationProvider.SLACK: ProviderSpec(
            id=NotificationProvider.SLACK,
            display_name="Slack",
            icon="tag",
            credential_fields=("url",),
            validator=_validator_single_url(is_valid_slack_webhook),
            sender=senders.send_slack_notification,
            help_url="https://api.slack.com/messaging/webhooks",
        ),
        NotificationProvider.DISCORD: ProviderSpec(
            id=NotificationProvider.DISCORD,
            display_name="Discord",
            icon="forum",
            credential_fields=("url",),
            validator=_validator_single_url(is_valid_discord_webhook),
            sender=senders.send_discord_notification,
            help_url=(
                "https://support.discord.com/hc/en-us/articles/"
                "228383668-Intro-to-Webhooks"
            ),
        ),
        NotificationProvider.TEAMS: ProviderSpec(
            id=NotificationProvider.TEAMS,
            display_name="Microsoft Teams",
            icon="groups",
            credential_fields=("url",),
            validator=_validator_single_url(is_valid_teams_webhook),
            sender=senders.send_teams_notification,
            help_url=(
                "https://learn.microsoft.com/en-us/power-automate/"
                "trigger-flow-http-request"
            ),
        ),
        NotificationProvider.TELEGRAM: ProviderSpec(
            id=NotificationProvider.TELEGRAM,
            display_name="Telegram",
            icon="send",
            credential_fields=("bot_token", "chat_id"),
            validator=_validate_telegram_creds,
            sender=senders.send_telegram_notification,
            help_url="https://core.telegram.org/bots/features#creating-a-new-bot",
        ),
        NotificationProvider.CLIQ: ProviderSpec(
            id=NotificationProvider.CLIQ,
            display_name="Zoho Cliq",
            icon="chat_bubble",
            credential_fields=("url",),
            validator=_validator_single_url(is_valid_cliq_webhook),
            sender=senders.send_cliq_notification,
            help_url=("https://www.zoho.com/cliq/help/platform/incoming-webhooks.html"),
        ),
    }


# Populated on first access to avoid import-time cycles with senders.py.
_REGISTRY: dict[NotificationProvider, ProviderSpec] | None = None


def _get_registry() -> dict[NotificationProvider, ProviderSpec]:
    global _REGISTRY  # pylint: disable=global-statement
    if _REGISTRY is None:
        _REGISTRY = _build_registry()
    return _REGISTRY


class _ProvidersProxy:
    """Lazy dict proxy so ``PROVIDERS`` works as a module-level constant."""

    def __getitem__(self, key: NotificationProvider) -> ProviderSpec:
        return _get_registry()[key]

    def __contains__(self, key: object) -> bool:
        return key in _get_registry()

    def __iter__(self):
        return iter(_get_registry())

    def __len__(self) -> int:
        return len(_get_registry())

    def items(self):
        return _get_registry().items()

    def keys(self):
        return _get_registry().keys()

    def values(self):
        return _get_registry().values()

    def get(
        self, key: NotificationProvider, default: ProviderSpec | None = None
    ) -> ProviderSpec | None:
        return _get_registry().get(key, default)


PROVIDERS: _ProvidersProxy = _ProvidersProxy()
