"""Per-provider POST senders.

Every sender returns ``(success, error_message)`` — never raises.
Network errors, HTTP errors, timeouts are all normalized to the same
return shape so the dispatch loop in :func:`skillnir.ui.layout.play_notification`
can treat all providers uniformly.

Stdlib-only HTTP (``urllib.request``) — same idiom as :mod:`skillnir.usage`.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from skillnir.notifications.providers import (
    is_valid_cliq_webhook,
    is_valid_discord_webhook,
    is_valid_gchat_webhook,
    is_valid_slack_webhook,
    is_valid_teams_webhook,
    is_valid_telegram_chat_id,
    is_valid_telegram_token,
)

_DEFAULT_TIMEOUT = 10.0
_JSON_HEADERS = {"Content-Type": "application/json; charset=UTF-8"}


# ---------------------------------------------------------------------------
# Shared POST helper
# ---------------------------------------------------------------------------


def _post_json(
    url: str,
    payload: dict,
    timeout: float = _DEFAULT_TIMEOUT,
) -> tuple[bool, str | None]:
    """POST ``payload`` as JSON to ``url``.

    Returns ``(True, None)`` on HTTP 2xx, else ``(False, error_message)``.
    Never raises. Caller is responsible for validating ``url`` against a
    host allowlist before calling this function — ``_post_json`` does NOT
    re-validate (that's checked at the call site by the provider validator).
    """
    try:
        data = json.dumps(payload).encode("utf-8")
    except (TypeError, ValueError) as exc:
        return False, f"payload encode error: {exc}"

    req = urllib.request.Request(
        url,
        data=data,
        headers=_JSON_HEADERS,
        method="POST",
    )

    # B310 (urllib scheme check) is handled at the call-site by the per-provider
    # validator, which enforces https:// and a host allowlist before we open
    # a socket. Safe to suppress here.
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            status = getattr(resp, "status", 200)
            if 200 <= status < 300:
                return True, None
            return False, f"HTTP {status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return False, f"network error: {exc.reason}"
    except (TimeoutError, OSError) as exc:
        return False, f"connection error: {exc}"


# ---------------------------------------------------------------------------
# Google Chat — cards v2 payload (preserved from original notifier.py)
# ---------------------------------------------------------------------------


def _build_gchat_card(title: str, detail: str | None) -> dict:
    """Build a Google Chat cards-v2 payload with a header + optional detail."""
    widgets: list[dict] = []
    if detail:
        widgets.append({"textParagraph": {"text": detail}})

    sections: list[dict] = []
    if widgets:
        sections.append({"widgets": widgets})

    card: dict = {
        "header": {
            "title": "Skillnir",
            "subtitle": title,
        },
    }
    if sections:
        card["sections"] = sections

    return {
        "cardsV2": [
            {
                "cardId": "skillnir-notification",
                "card": card,
            }
        ]
    }


def send_gchat_notification(
    webhook_url: str,
    title: str,
    detail: str | None = None,
    *,
    timeout: float = _DEFAULT_TIMEOUT,
) -> tuple[bool, str | None]:
    """Back-compat Google Chat sender.

    Signature matches the pre-multi-provider API exactly so existing
    call sites and tests keep working through the shim in
    :mod:`skillnir.notifier`.
    """
    if not webhook_url:
        return False, "webhook URL not set"
    if not is_valid_gchat_webhook(webhook_url):
        return False, "invalid webhook URL"
    return _post_json(webhook_url, _build_gchat_card(title, detail), timeout)


def send_gchat_notification_spec(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """ProviderSpec-shaped wrapper around :func:`send_gchat_notification`."""
    return send_gchat_notification(
        creds.get("url", ""),
        title,
        detail,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Google Chat — intel item card (for CI: scripts/run_intel.py)
# ---------------------------------------------------------------------------


def _build_gchat_item_card(
    feature: str,
    title: str,
    description: str,
    reference_url: str,
) -> dict:
    """Build a Cards v2 payload for ONE intel item with a "View source" button.

    Shape: header("Skillnir" / feature subtitle) + textParagraph(title+description)
    + buttonList with one openLink button to ``reference_url``.
    """
    body_text = f"<b>{title}</b>\n\n{description}" if description else f"<b>{title}</b>"
    return {
        "cardsV2": [
            {
                "cardId": "skillnir-intel-item",
                "card": {
                    "header": {
                        "title": "Skillnir",
                        "subtitle": feature,
                    },
                    "sections": [
                        {
                            "widgets": [
                                {"textParagraph": {"text": body_text}},
                                {
                                    "buttonList": {
                                        "buttons": [
                                            {
                                                "text": "View source",
                                                "onClick": {
                                                    "openLink": {"url": reference_url}
                                                },
                                            }
                                        ]
                                    }
                                },
                            ]
                        }
                    ],
                },
            }
        ]
    }


def _build_gchat_item_fallback_card(
    feature: str,
    title: str,
    description: str,
    reference_url: str,
) -> dict:
    """Plain-text fallback for :func:`_build_gchat_item_card`.

    Used only if the primary card is rejected by Google Chat with a 4xx
    (e.g. unsupported widget schema on a given space configuration).
    URL is embedded as bare text — Google Chat auto-links bare URLs in
    ``textParagraph`` widgets.
    """
    parts = [f"<b>{title}</b>"]
    if description:
        parts.append(description)
    if reference_url:
        parts.append(reference_url)
    return {
        "cardsV2": [
            {
                "cardId": "skillnir-intel-item-fallback",
                "card": {
                    "header": {
                        "title": "Skillnir",
                        "subtitle": feature,
                    },
                    "sections": [
                        {"widgets": [{"textParagraph": {"text": "\n\n".join(parts)}}]}
                    ],
                },
            }
        ]
    }


def send_gchat_item(
    webhook_url: str,
    *,
    feature: str,
    title: str,
    description: str,
    reference_url: str,
    timeout: float = _DEFAULT_TIMEOUT,
) -> tuple[bool, str | None]:
    """POST a Cards v2 message representing ONE intel item.

    Primary attempt uses a ``buttonList`` widget with an openLink button.
    If the POST returns HTTP 4xx (malformed card, unsupported widget),
    automatically retries with a plain-text fallback card.

    Never raises. Returns ``(True, None)`` on success, ``(False, error)``
    on persistent failure.

    Parameters
    ----------
    webhook_url:
        Full Google Chat incoming webhook URL. Validated against the
        ``chat.googleapis.com`` host allowlist before any socket opens.
    feature:
        Short label for the header subtitle — e.g. ``"research"``,
        ``"events"``, ``"security"``.
    title:
        Item title. Rendered bold at the top of the card body.
    description:
        Item summary / description. Rendered below the title.
    reference_url:
        URL the "View source" button should open. Required.
    timeout:
        Per-POST timeout in seconds.
    """
    if not webhook_url:
        return False, "webhook URL not set"
    if not is_valid_gchat_webhook(webhook_url):
        return False, "invalid webhook URL"
    if not reference_url:
        return False, "reference_url not set"

    primary = _build_gchat_item_card(feature, title, description, reference_url)
    ok, err = _post_json(webhook_url, primary, timeout)
    if ok:
        return True, None

    # Retry with plain-text fallback only on 4xx (client-side rejection).
    # Server errors (5xx), network errors, and timeouts are not retried —
    # retrying with a different payload won't fix those.
    if err and err.startswith("HTTP 4"):
        fallback = _build_gchat_item_fallback_card(
            feature, title, description, reference_url
        )
        return _post_json(webhook_url, fallback, timeout)

    return False, err


# ---------------------------------------------------------------------------
# Slack — simple text payload
# ---------------------------------------------------------------------------


def send_slack_notification(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """POST a Slack incoming-webhook message (bold title + optional detail)."""
    url = (creds.get("url") or "").strip()
    if not url:
        return False, "webhook URL not set"
    if not is_valid_slack_webhook(url):
        return False, "invalid webhook URL"
    text = f"*{title}*\n{detail}" if detail else f"*{title}*"
    return _post_json(url, {"text": text}, timeout)


# ---------------------------------------------------------------------------
# Discord — embed payload
# ---------------------------------------------------------------------------


def send_discord_notification(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """POST a Discord webhook message as a rich embed."""
    url = (creds.get("url") or "").strip()
    if not url:
        return False, "webhook URL not set"
    if not is_valid_discord_webhook(url):
        return False, "invalid webhook URL"
    embed = {
        "title": title,
        "description": detail or "",
        "footer": {"text": "Skillnir"},
    }
    return _post_json(url, {"content": "", "embeds": [embed]}, timeout)


# ---------------------------------------------------------------------------
# Microsoft Teams — Power Automate workflow webhook
# ---------------------------------------------------------------------------


def send_teams_notification(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """POST to a Microsoft Teams Power Automate workflow webhook.

    The payload shape is a simple ``{title, detail, source}`` dict that the
    user's Power Automate flow is expected to consume via "When an HTTP
    request is received" trigger. This is a convention, not a standard —
    users whose workflows expect AdaptiveCards will receive a 2xx but
    see no rendered message.
    """
    url = (creds.get("url") or "").strip()
    if not url:
        return False, "webhook URL not set"
    if not is_valid_teams_webhook(url):
        return False, "invalid webhook URL"
    payload = {
        "title": title,
        "detail": detail or "",
        "source": "Skillnir",
    }
    return _post_json(url, payload, timeout)


# ---------------------------------------------------------------------------
# Telegram — Bot API
# ---------------------------------------------------------------------------


_TELEGRAM_API_BASE = "https://api.telegram.org"


def send_telegram_notification(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """POST a Telegram Bot API message via constructed URL.

    The bot token IS the URL credential — any error message that echoes
    the full URL leaks the token. This function wraps :func:`_post_json`
    and **redacts the token** from any returned error string before
    returning, so UI toasts and stderr logs never contain it.
    """
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

    # Construct the API URL ourselves. The user never pastes this.
    url = f"{_TELEGRAM_API_BASE}/bot{bot_token}/sendMessage"

    # Plain text, no parse_mode — avoids MarkdownV2 escaping bugs on
    # titles containing "(", ")", ":" (common in our model annotations).
    text = f"{title}\n\n{detail}" if detail else title
    payload = {"chat_id": chat_id, "text": text}

    ok, err = _post_json(url, payload, timeout)
    if err and bot_token in err:
        err = err.replace(bot_token, "<redacted>")
    return ok, err


# ---------------------------------------------------------------------------
# Zoho Cliq — incoming webhook
# ---------------------------------------------------------------------------


def send_cliq_notification(
    creds: dict[str, str],
    title: str,
    detail: str | None,
    timeout: float,
) -> tuple[bool, str | None]:
    """POST a Zoho Cliq incoming-webhook message."""
    url = (creds.get("url") or "").strip()
    if not url:
        return False, "webhook URL not set"
    if not is_valid_cliq_webhook(url):
        return False, "invalid webhook URL"
    text = f"**{title}**\n{detail}" if detail else f"**{title}**"
    return _post_json(url, {"text": text}, timeout)
