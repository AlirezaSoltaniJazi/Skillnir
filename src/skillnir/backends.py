"""Multi-backend support for AI generation (Claude, Gemini, Copilot)."""

import functools
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable


class AIBackend(Enum):
    """Supported generation backends."""

    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    COPILOT = "copilot"


@dataclass(frozen=True)
class ModelInfo:
    """A model available in a backend."""

    id: str
    alias: str
    display_name: str
    is_default: bool = False
    tier: int = 2  # 1=powerful/expensive, 2=balanced, 3=cheap/fast


@dataclass(frozen=True)
class BackendInfo:
    """Static metadata for a backend."""

    id: AIBackend
    name: str
    cli_command: str
    supports_stream_json: bool
    models: tuple[ModelInfo, ...]
    default_model: str  # alias of the default model
    usage_command: tuple[str, ...] | None
    usage_url: str | None
    version_command: tuple[str, ...]
    icon: str  # material icon name
    slash_commands: dict[str, str] = field(default_factory=dict)
    mode_flags: dict[str, list[str]] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Backend registry
# ---------------------------------------------------------------------------

BACKENDS: dict[AIBackend, BackendInfo] = {
    AIBackend.CLAUDE: BackendInfo(
        id=AIBackend.CLAUDE,
        name="Claude Code",
        cli_command="claude",
        supports_stream_json=True,
        models=(
            ModelInfo(
                "claude-opus-4-7", "opus", "Claude Opus 4.7", is_default=True, tier=1
            ),
            ModelInfo("claude-opus-4-6", "opus-4.6", "Claude Opus 4.6", tier=1),
            ModelInfo("claude-sonnet-4-6", "sonnet", "Claude Sonnet 4.6", tier=2),
            ModelInfo("claude-haiku-4-5", "haiku", "Claude Haiku 4.5", tier=3),
            ModelInfo("claude-opus-4-5", "opus-4.5", "Claude Opus 4.5", tier=1),
            ModelInfo("claude-opus-4-1", "opus-4.1", "Claude Opus 4.1", tier=1),
            ModelInfo("claude-opus-4-0", "opus-4.0", "Claude Opus 4", tier=1),
            ModelInfo("claude-sonnet-4-5", "sonnet-4.5", "Claude Sonnet 4.5", tier=2),
            ModelInfo("claude-sonnet-4-0", "sonnet-4.0", "Claude Sonnet 4", tier=2),
        ),
        default_model="opus",
        usage_command=None,
        usage_url="https://console.anthropic.com/settings/billing",
        version_command=("claude", "--version"),
        icon="smart_toy",
        slash_commands={
            "skills": "List all project skills found in .claude/skills/ directory. Show each skill name and description."
        },
        mode_flags={},
    ),
    AIBackend.CURSOR: BackendInfo(
        id=AIBackend.CURSOR,
        name="Cursor Agent",
        cli_command="agent",
        supports_stream_json=True,
        models=(
            # Tier 2 — balanced (default)
            ModelInfo("auto", "auto", "Auto (recommended)", is_default=True, tier=2),
            ModelInfo("composer-2", "composer-2", "Composer 2", tier=2),
            ModelInfo(
                "claude-4.6-sonnet-medium",
                "claude-4.6-sonnet-medium",
                "Claude 4.6 Sonnet",
                tier=2,
            ),
            ModelInfo(
                "claude-4.6-sonnet-medium-thinking",
                "claude-4.6-sonnet-medium-thinking",
                "Claude 4.6 Sonnet (thinking)",
                tier=2,
            ),
            ModelInfo("gpt-5.4-medium", "gpt-5.4-medium", "GPT-5.4 Medium", tier=2),
            ModelInfo("gpt-5.3-codex", "gpt-5.3-codex", "GPT-5.3 Codex", tier=2),
            ModelInfo(
                "claude-4.5-sonnet", "claude-4.5-sonnet", "Claude 4.5 Sonnet", tier=2
            ),
            # Tier 1 — powerful
            ModelInfo(
                "claude-4.6-opus-max",
                "claude-4.6-opus-max",
                "Claude 4.6 Opus Max",
                tier=1,
            ),
            ModelInfo(
                "claude-4.6-opus-max-thinking",
                "claude-4.6-opus-max-thinking",
                "Claude 4.6 Opus Max (thinking)",
                tier=1,
            ),
            ModelInfo("gpt-5.5-high", "gpt-5.5-high", "GPT-5.5 High", tier=1),
            ModelInfo(
                "gpt-5.5-extra-high", "gpt-5.5-extra-high", "GPT-5.5 Extra High", tier=1
            ),
            ModelInfo("gpt-5.4-xhigh", "gpt-5.4-xhigh", "GPT-5.4 XHigh", tier=1),
            ModelInfo("gemini-3.1-pro", "gemini-3.1-pro", "Gemini 3.1 Pro", tier=1),
            ModelInfo(
                "grok-4-20-thinking",
                "grok-4-20-thinking",
                "Grok 4-20 (thinking)",
                tier=1,
            ),
            # Tier 3 — fast / cheap
            ModelInfo("composer-2-fast", "composer-2-fast", "Composer 2 Fast", tier=3),
            ModelInfo(
                "gpt-5.4-mini-medium", "gpt-5.4-mini-medium", "GPT-5.4 Mini", tier=3
            ),
            ModelInfo("gpt-5-mini", "gpt-5-mini", "GPT-5 Mini", tier=3),
            ModelInfo(
                "gpt-5.4-nano-medium", "gpt-5.4-nano-medium", "GPT-5.4 Nano", tier=3
            ),
            ModelInfo("gemini-3-flash", "gemini-3-flash", "Gemini 3 Flash", tier=3),
        ),
        default_model="auto",
        usage_command=None,
        usage_url="https://www.cursor.com/settings",
        version_command=("agent", "--version"),
        icon="code",
        slash_commands={"usage": "/usage", "skills": "/skill"},
        mode_flags={"ask": ["--mode", "ask"], "plan": ["--mode", "plan"]},
    ),
    AIBackend.GEMINI: BackendInfo(
        id=AIBackend.GEMINI,
        name="Gemini CLI",
        cli_command="gemini",
        supports_stream_json=True,
        models=(
            ModelInfo("auto", "auto", "Auto (recommended)", is_default=True, tier=2),
            ModelInfo("gemini-2.5-pro", "pro", "Gemini 2.5 Pro", tier=1),
            ModelInfo("gemini-2.5-flash", "flash", "Gemini 2.5 Flash", tier=2),
            ModelInfo(
                "gemini-2.5-flash-lite", "flash-lite", "Gemini 2.5 Flash Lite", tier=3
            ),
            ModelInfo("gemini-3-pro-preview", "3-pro", "Gemini 3 Pro Preview", tier=1),
            ModelInfo(
                "gemini-3-flash-preview", "3-flash", "Gemini 3 Flash Preview", tier=2
            ),
            ModelInfo("gemini-2.0-pro", "2.0-pro", "Gemini 2.0 Pro", tier=1),
            ModelInfo("gemini-2.0-flash", "2.0-flash", "Gemini 2.0 Flash", tier=3),
            ModelInfo(
                "gemini-2.0-flash-lite",
                "2.0-flash-lite",
                "Gemini 2.0 Flash Lite",
                tier=3,
            ),
            ModelInfo(
                "gemini-2.5-pro-preview",
                "pro-preview",
                "Gemini 2.5 Pro Preview",
                tier=1,
            ),
        ),
        default_model="auto",
        usage_command=None,
        usage_url="https://ai.google.dev",
        version_command=("gemini", "--version"),
        icon="diamond",
        slash_commands={
            "usage": "/stats",
            "skills": "List all project skills or extensions found in this directory. Show each name and description.",
        },
        mode_flags={},
    ),
    AIBackend.COPILOT: BackendInfo(
        id=AIBackend.COPILOT,
        name="GitHub Copilot",
        cli_command="copilot",
        supports_stream_json=False,
        models=(
            # Names match the identifiers shown by Copilot CLI's /model picker.
            # Tier 2 — balanced (default)
            ModelInfo(
                "claude-sonnet-4-5",
                "claude-sonnet-4-5",
                "Claude Sonnet 4.5",
                is_default=True,
                tier=2,
            ),
            ModelInfo("claude-sonnet-4", "claude-sonnet-4", "Claude Sonnet 4", tier=2),
            ModelInfo("gpt-5", "gpt-5", "GPT-5", tier=2),
            ModelInfo("gpt-4.1", "gpt-4.1", "GPT-4.1", tier=2),
            # Tier 1 — powerful
            ModelInfo("claude-opus-4-1", "claude-opus-4-1", "Claude Opus 4.1", tier=1),
            ModelInfo("claude-opus-4", "claude-opus-4", "Claude Opus 4", tier=1),
            ModelInfo("gemini-2.5-pro", "gemini-2.5-pro", "Gemini 2.5 Pro", tier=1),
            # Tier 3 — fast / cheap
            ModelInfo("gpt-5-mini", "gpt-5-mini", "GPT-5 Mini", tier=3),
            ModelInfo("o4-mini", "o4-mini", "o4-mini", tier=3),
        ),
        default_model="claude-sonnet-4-5",
        usage_command=None,
        usage_url="https://github.com/settings/billing",
        version_command=("copilot", "--version"),
        icon="hub",
        slash_commands={"usage": "/usage", "skills": "/skill list"},
        mode_flags={},
    ),
}

# ---------------------------------------------------------------------------
# Configuration persistence (~/.skillnir/config.json)
# ---------------------------------------------------------------------------

CONFIG_DIR = Path.home() / ".skillnir"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _find_data_dir() -> Path | None:
    """Walk up from this file to find .data/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data"
        if candidate.is_dir():
            return candidate
        current = current.parent
    cwd_candidate = Path.cwd() / ".data"
    return cwd_candidate if cwd_candidate.is_dir() else None


def _discover_prompt_versions() -> tuple[str, ...]:
    """Scan .data/promptsv* directories and return sorted version tuple."""
    data_dir = _find_data_dir()
    if not data_dir or not data_dir.is_dir():
        return ("v1",)
    versions: list[str] = []
    for d in sorted(data_dir.iterdir()):
        if d.is_dir() and d.name.startswith("promptsv"):
            num = d.name.removeprefix("promptsv")
            versions.append(f"v{num}")
    return tuple(versions) if versions else ("v1",)


@functools.lru_cache(maxsize=1)
def get_prompt_versions() -> tuple[str, ...]:
    """Return discovered prompt versions (cached after first call)."""
    return _discover_prompt_versions()


def get_prompt_version_labels() -> dict[str, str]:
    """Generate labels from discovered versions."""
    return {v: v for v in get_prompt_versions()}


def _default_prompt_version() -> str:
    """Return the latest discovered prompt version."""
    return get_prompt_versions()[-1]


PROMPT_VERSIONS = get_prompt_versions()
PROMPT_VERSION_LABELS = get_prompt_version_labels()


# Per-provider cipher field mapping. Ordered dict so iteration is
# stable in the Settings UI (expansion panel order matches registry).
# Keep this in sync with ``skillnir.notifications.providers.PROVIDERS``.
_CIPHER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "gchat": ("gchat_webhook_cipher",),
    "slack": ("slack_webhook_cipher",),
    "discord": ("discord_webhook_cipher",),
    "teams": ("teams_webhook_cipher",),
    "telegram": ("telegram_bot_token_cipher", "telegram_chat_id_cipher"),
    "cliq": ("cliq_webhook_cipher",),
}

# Maps each cipher field to its logical credential key name. Used by
# ``get_provider_credentials`` to zip back into ``{"url": ...}`` or
# ``{"bot_token": ..., "chat_id": ...}`` dicts for the Settings UI and
# sender signatures.
_CIPHER_FIELD_TO_KEY: dict[str, str] = {
    "gchat_webhook_cipher": "url",
    "slack_webhook_cipher": "url",
    "discord_webhook_cipher": "url",
    "teams_webhook_cipher": "url",
    "telegram_bot_token_cipher": "bot_token",
    "telegram_chat_id_cipher": "chat_id",
    "cliq_webhook_cipher": "url",
}

_VALID_PROVIDER_IDS: frozenset[str] = frozenset(_CIPHER_FIELD_MAP.keys()) | {""}

# ── Effort + thinking config (Claude SDK only) ──
EFFORT_LEVELS: tuple[str, ...] = ("low", "medium", "high", "max")
THINKING_MODES: tuple[str, ...] = ("adaptive", "disabled")
DEFAULT_EFFORT = "high"
DEFAULT_THINKING_MODE = "adaptive"


@dataclass
class AppConfig:
    """User's persisted backend/model + notification preferences.

    Per-provider credentials are stored encrypted at rest as Fernet tokens
    bound to the local machine + per-install UUID. Use
    :meth:`get_provider_credentials` / :meth:`set_provider_credentials`
    instead of touching the cipher fields directly.
    """

    backend: AIBackend = AIBackend.CLAUDE
    model: str = "opus"
    prompt_version: str = field(default_factory=_default_prompt_version)
    compress_prompts: bool = False
    # ── Claude SDK reasoning controls (other backends ignore) ──
    effort: str = DEFAULT_EFFORT  # low | medium | high | max
    thinking_mode: str = DEFAULT_THINKING_MODE  # adaptive | disabled
    # ── Notification credentials (one cipher field per secret) ──
    gchat_webhook_cipher: str = ""
    slack_webhook_cipher: str = ""
    discord_webhook_cipher: str = ""
    teams_webhook_cipher: str = ""
    telegram_bot_token_cipher: str = ""
    telegram_chat_id_cipher: str = ""
    cliq_webhook_cipher: str = ""
    notifications_enabled: bool = False
    active_provider: str = ""  # "" | "gchat" | "slack" | ... | "cliq"

    # ── Generic per-provider credential accessors ────────────────────────

    def get_provider_credentials(self, provider: str) -> dict[str, str]:
        """Decrypt and return the named provider's credentials as a dict.

        Returns ``{}`` if the provider id is unknown, or a dict like
        ``{"url": "..."}`` / ``{"bot_token": "...", "chat_id": "..."}``.
        Missing or decrypt-failing fields come back as empty strings.
        """
        from skillnir.crypto import decrypt_string

        cipher_fields = _CIPHER_FIELD_MAP.get(provider)
        if not cipher_fields:
            return {}
        creds: dict[str, str] = {}
        for cipher_field in cipher_fields:
            key = _CIPHER_FIELD_TO_KEY[cipher_field]
            cipher = getattr(self, cipher_field, "") or ""
            creds[key] = decrypt_string(cipher) if cipher else ""
        return creds

    def set_provider_credentials(self, provider: str, creds: dict[str, str]) -> None:
        """Encrypt and store ``creds`` for the named provider.

        Missing keys in ``creds`` are treated as empty strings (which
        clears that field's cipher).
        """
        from skillnir.crypto import encrypt_string

        cipher_fields = _CIPHER_FIELD_MAP.get(provider)
        if not cipher_fields:
            return
        for cipher_field in cipher_fields:
            key = _CIPHER_FIELD_TO_KEY[cipher_field]
            value = (creds.get(key) or "").strip()
            setattr(self, cipher_field, encrypt_string(value) if value else "")

    def clear_provider_credentials(self, provider: str) -> None:
        """Wipe all cipher fields for the named provider."""
        cipher_fields = _CIPHER_FIELD_MAP.get(provider)
        if not cipher_fields:
            return
        for cipher_field in cipher_fields:
            setattr(self, cipher_field, "")

    def has_provider_credentials(self, provider: str) -> bool:
        """True iff all required cipher fields for ``provider`` are non-empty."""
        cipher_fields = _CIPHER_FIELD_MAP.get(provider)
        if not cipher_fields:
            return False
        return all(getattr(self, f, "") for f in cipher_fields)

    # ── Legacy single-URL accessors (back-compat shims) ──────────────────

    def get_webhook_url(self) -> str:
        """Decrypt and return the *Google Chat* webhook URL.

        Deprecated: prefer :meth:`get_provider_credentials`. Kept so
        existing tests and third-party call sites keep working.
        """
        return self.get_provider_credentials("gchat").get("url", "")

    def set_webhook_url(self, url: str) -> None:
        """Encrypt and store the *Google Chat* webhook URL.

        Deprecated: prefer :meth:`set_provider_credentials`.
        """
        self.set_provider_credentials("gchat", {"url": url})

    # ── Serialization ────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "backend": self.backend.value,
            "model": self.model,
            "prompt_version": self.prompt_version,
            "compress_prompts": self.compress_prompts,
            "effort": self.effort,
            "thinking_mode": self.thinking_mode,
            "gchat_webhook_cipher": self.gchat_webhook_cipher,
            "slack_webhook_cipher": self.slack_webhook_cipher,
            "discord_webhook_cipher": self.discord_webhook_cipher,
            "teams_webhook_cipher": self.teams_webhook_cipher,
            "telegram_bot_token_cipher": self.telegram_bot_token_cipher,
            "telegram_chat_id_cipher": self.telegram_chat_id_cipher,
            "cliq_webhook_cipher": self.cliq_webhook_cipher,
            "notifications_enabled": self.notifications_enabled,
            "active_provider": self.active_provider,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        try:
            backend = AIBackend(d.get("backend", "claude"))
        except ValueError:
            backend = AIBackend.CLAUDE
        model = d.get("model", BACKENDS[backend].default_model)
        valid_aliases = {m.alias for m in BACKENDS[backend].models}
        if model not in valid_aliases:
            model = BACKENDS[backend].default_model
        pv = d.get("prompt_version", _default_prompt_version())
        if pv not in get_prompt_versions():
            pv = _default_prompt_version()
        compress = bool(d.get("compress_prompts", False))
        effort = str(d.get("effort", DEFAULT_EFFORT))
        if effort not in EFFORT_LEVELS:
            effort = DEFAULT_EFFORT
        thinking_mode = str(d.get("thinking_mode", DEFAULT_THINKING_MODE))
        if thinking_mode not in THINKING_MODES:
            thinking_mode = DEFAULT_THINKING_MODE
        gchat_cipher = str(d.get("gchat_webhook_cipher", ""))
        slack_cipher = str(d.get("slack_webhook_cipher", ""))
        discord_cipher = str(d.get("discord_webhook_cipher", ""))
        teams_cipher = str(d.get("teams_webhook_cipher", ""))
        telegram_bot_token_cipher = str(d.get("telegram_bot_token_cipher", ""))
        telegram_chat_id_cipher = str(d.get("telegram_chat_id_cipher", ""))
        cliq_cipher = str(d.get("cliq_webhook_cipher", ""))
        notif_enabled = bool(d.get("notifications_enabled", False))
        active_provider = str(d.get("active_provider", ""))

        # ── One-shot migration from legacy plaintext field ────────────────
        # Previous builds stored the webhook URL in plaintext under
        # ``gchat_webhook_url``. If we see that and no cipher yet, encrypt
        # it on the fly. ``load_config()`` will persist the migration.
        legacy_plaintext = str(d.get("gchat_webhook_url", ""))
        if legacy_plaintext and not gchat_cipher:
            from skillnir.crypto import encrypt_string

            gchat_cipher = encrypt_string(legacy_plaintext)

        # ── Normalize active_provider ─────────────────────────────────────
        if active_provider not in _VALID_PROVIDER_IDS:
            active_provider = ""

        # ── Default active_provider for legacy single-provider configs ────
        # If the user upgrades from the single-provider era (they had gchat
        # configured but `active_provider` didn't exist), auto-set it so
        # their notifications keep working after the upgrade.
        if not active_provider:
            cipher_map = {
                "gchat": gchat_cipher,
                "slack": slack_cipher,
                "discord": discord_cipher,
                "teams": teams_cipher,
                "telegram": telegram_bot_token_cipher and telegram_chat_id_cipher,
                "cliq": cliq_cipher,
            }
            # Prefer gchat (the only pre-existing provider), then the
            # first non-empty in registry order.
            for provider_id in (
                "gchat",
                "slack",
                "discord",
                "teams",
                "telegram",
                "cliq",
            ):
                if cipher_map[provider_id]:
                    active_provider = provider_id
                    break

        return cls(
            backend=backend,
            model=model,
            prompt_version=pv,
            compress_prompts=compress,
            effort=effort,
            thinking_mode=thinking_mode,
            gchat_webhook_cipher=gchat_cipher,
            slack_webhook_cipher=slack_cipher,
            discord_webhook_cipher=discord_cipher,
            teams_webhook_cipher=teams_cipher,
            telegram_bot_token_cipher=telegram_bot_token_cipher,
            telegram_chat_id_cipher=telegram_chat_id_cipher,
            cliq_webhook_cipher=cliq_cipher,
            notifications_enabled=notif_enabled,
            active_provider=active_provider,
        )


def load_config() -> AppConfig:
    """Load config from ~/.skillnir/config.json, or return defaults."""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            config = AppConfig.from_dict(data)
            # If we just migrated a legacy plaintext webhook URL, persist
            # immediately so the plaintext stops sitting on disk.
            if "gchat_webhook_url" in data:
                try:
                    save_config(config)
                except OSError as exc:
                    # Don't swallow silently: the plaintext webhook URL
                    # is still on disk and the user should know so they
                    # can rotate the webhook in Google Chat.
                    print(
                        "skillnir: WARNING — failed to re-persist config after "
                        f"migrating legacy plaintext webhook URL: {exc}. "
                        "Rotate the webhook in Google Chat and fix "
                        f"{CONFIG_FILE} permissions.",
                        file=sys.stderr,
                    )
            return config
        except json.JSONDecodeError, ValueError, KeyError:
            pass
    # Migrate from old config locations if they exist
    for old_dir_name in (".agenrix", ".ai-injector"):
        old_config = Path.home() / old_dir_name / "config.json"
        if old_config.exists():
            try:
                data = json.loads(old_config.read_text(encoding="utf-8"))
                config = AppConfig.from_dict(data)
                try:
                    save_config(config)
                except OSError:
                    pass
                return config
            except json.JSONDecodeError, ValueError, KeyError:
                pass
    return AppConfig()


def save_config(config: AppConfig) -> None:
    """Persist config to ~/.skillnir/config.json (owner-read/write only)."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    # Restrict to owner read/write on POSIX; best-effort on Windows.
    # The file contains ``gchat_webhook_cipher``, which — together with
    # the same-user-readable ``client_id`` and machine fingerprint — is
    # enough to recover the webhook URL. Keep its permissions in sync
    # with crypto.CLIENT_ID_FILE (also 0o600).
    try:
        CONFIG_FILE.chmod(0o600)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Detection and info
# ---------------------------------------------------------------------------


def detect_available_backends() -> list[AIBackend]:
    """Return backends whose CLI is found in PATH."""
    available: list[AIBackend] = []
    for backend_id, info in BACKENDS.items():
        if shutil.which(info.cli_command):
            available.append(backend_id)
    # For Claude, also check SDK availability
    if AIBackend.CLAUDE not in available:
        try:
            import claude_agent_sdk  # noqa: F401

            available.insert(0, AIBackend.CLAUDE)
        except ImportError:
            pass
    return available


def get_backend_version(backend: AIBackend) -> str | None:
    """Run --version for the backend CLI and return output."""
    info = BACKENDS[backend]
    try:
        result = subprocess.run(
            list(info.version_command),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except FileNotFoundError, subprocess.TimeoutExpired:
        return None


def get_usage_info(backend: AIBackend) -> str | None:
    """Try to fetch usage info from the backend CLI.

    1. Try slash command via ``cli -p "/usage"`` (works for Copilot, Cursor, Gemini).
    2. Fall back to dedicated usage_command if set.
    3. Return None so the UI can fall back to opening usage_url.
    """
    info = BACKENDS[backend]

    # Try slash command via -p
    usage_slash = info.slash_commands.get("usage")
    if usage_slash:
        try:
            cmd = [info.cli_command, "-p", usage_slash]
            # Cursor needs --trust to avoid workspace-trust prompt
            if backend == AIBackend.CURSOR:
                cmd.append("--trust")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip() or result.stderr.strip()
            # Reject error responses (e.g. "Unknown skill: usage" from Claude)
            if (
                output
                and result.returncode == 0
                and "unknown skill" not in output.lower()
            ):
                return output
        except FileNotFoundError, subprocess.TimeoutExpired:
            pass

    # Fall back to dedicated usage_command
    if info.usage_command:
        try:
            result = subprocess.run(
                list(info.usage_command),
                capture_output=True,
                text=True,
                timeout=10,
            )
            output = result.stdout.strip() or result.stderr.strip()
            return output if output else None
        except FileNotFoundError, subprocess.TimeoutExpired:
            pass

    return None


def build_claude_sdk_kwargs(config: "AppConfig | None" = None) -> dict:
    """Return ``ClaudeAgentOptions`` kwargs for ``effort`` and ``thinking``.

    Centralizes the per-config translation so every Claude SDK call site
    stays consistent. Returns an empty dict when both knobs are at their
    defaults so we don't pin parameters the user hasn't customized.
    """
    if config is None:
        config = load_config()
    kwargs: dict = {}
    if config.effort and config.effort != DEFAULT_EFFORT:
        kwargs["effort"] = config.effort
    if config.thinking_mode == "adaptive":
        kwargs["thinking"] = {"type": "adaptive"}
    elif config.thinking_mode == "disabled":
        kwargs["thinking"] = {"type": "disabled"}
    return kwargs


def resolve_model_id(backend: AIBackend, alias_or_id: str) -> str:
    """Resolve a model alias to its full ID. Returns as-is if not an alias."""
    info = BACKENDS[backend]
    for m in info.models:
        if m.alias == alias_or_id:
            return m.id
    return alias_or_id


# ---------------------------------------------------------------------------
# Command builder
# ---------------------------------------------------------------------------


def _apply_mode(
    prompt: str,
    mode: str | None,
    info: BackendInfo,
) -> tuple[str, list[str]]:
    """Apply mode to prompt/flags. Returns (modified_prompt, extra_flags)."""
    if not mode:
        return prompt, []
    if mode in info.mode_flags:
        return prompt, list(info.mode_flags[mode])
    # Fallback: prepend instructions for backends without native mode support
    if mode == "ask":
        return (
            "Answer the following question without making any changes "
            f"to the codebase:\n\n{prompt}"
        ), []
    if mode == "plan":
        return (
            "Create a detailed implementation plan for the following. "
            f"Do not make any changes yet:\n\n{prompt}"
        ), []
    return prompt, []


def build_subprocess_command(
    backend: AIBackend,
    prompt: str,
    model: str | None = None,
    max_turns: int = 15,
    mode: str | None = None,
    compress: bool | None = None,
) -> list[str]:
    """Build CLI command for the given backend."""
    if compress is None:
        compress = load_config().compress_prompts
    if compress:
        from skillnir.compressor import compress_prompt

        prompt = compress_prompt(prompt).compressed

    info = BACKENDS[backend]
    model_id = (
        resolve_model_id(backend, model)
        if model
        else resolve_model_id(backend, info.default_model)
    )
    prompt, extra_flags = _apply_mode(prompt, mode, info)

    if backend == AIBackend.CLAUDE:
        cfg = load_config()
        cmd = [
            info.cli_command,
            "-p",
            "--output-format",
            "stream-json",
            "--model",
            model_id,
            "--allowedTools",
            "Read,Glob,Grep,Bash,Write",
            "--max-turns",
            str(max_turns),
            "--verbose",
        ]
        # Pass --effort only when user customized it; keeps default behavior
        # unchanged for users on the older default ("high" is implicit).
        if cfg.effort and cfg.effort != DEFAULT_EFFORT:
            cmd += ["--effort", cfg.effort]
    elif backend == AIBackend.CURSOR:
        cmd = [
            info.cli_command,
            "-p",
            "--output-format",
            "stream-json",
            "--model",
            model_id,
            "--trust",
            "--sandbox",
            "disabled",
            "--force",
        ]
    elif backend == AIBackend.GEMINI:
        cmd = [
            info.cli_command,
            "-p",
            "--output-format",
            "stream-json",
            "--model",
            model_id,
            "--approval-mode",
            "yolo",
        ]
    elif backend == AIBackend.COPILOT:
        # Copilot uses --prompt <text> (not positional), so prompt goes inline.
        cmd = [
            info.cli_command,
            "--prompt",
            prompt,
            "--model",
            model_id,
            "--allow-all-tools",
            "--silent",
        ]
        return cmd + extra_flags
    else:
        raise ValueError(f"Unknown backend: {backend}")

    # Positional prompt goes after "--" to prevent content starting with
    # dashes from being misinterpreted as CLI flags.
    return cmd + extra_flags + ["--", prompt]


# ---------------------------------------------------------------------------
# Stream parsers
# ---------------------------------------------------------------------------


def parse_stream_line(
    backend: AIBackend,
    line: str,
    on_progress: Callable | None,
) -> None:
    """Parse a single stdout line from the backend CLI and emit progress."""
    if backend == AIBackend.COPILOT:
        _parse_text_line(line, on_progress)
    else:
        # Claude, Cursor, and Gemini use stream-json
        _parse_stream_json_line(line, on_progress, backend)


def _parse_stream_json_line(
    line: str,
    on_progress: Callable | None,
    backend: AIBackend | None = None,
) -> None:
    """Parse stream-json format (Claude / Gemini)."""
    from skillnir.generator import _emit

    if not line.strip():
        return
    try:
        event = json.loads(line)
    except json.JSONDecodeError:
        return

    event_type = event.get("type", "")

    if event_type == "assistant":
        message = event.get("message", {})
        for block in message.get("content", []):
            if block.get("type") == "text":
                text = block.get("text", "")
                if text:
                    _emit(on_progress, "text", text)
            elif block.get("type") == "tool_use":
                name = block.get("name", "unknown")
                _emit(on_progress, "tool_use", f"Using {name}...", tool_name=name)
    elif event_type == "result":
        result_text = event.get("result", "")
        if result_text:
            _emit(on_progress, "result_text", result_text)
        usage = event.get("usage")
        if usage:
            _emit(on_progress, "usage", json.dumps(usage))
            # Record usage to session tracker for all backends
            try:
                from skillnir.usage import session_tracker

                backend_name = backend.value if backend else "cli"
                session_tracker.record(backend_name, usage)
            except Exception:
                pass


def _parse_text_line(
    line: str,
    on_progress: Callable | None,
) -> None:
    """Parse plain text output (Copilot)."""
    from skillnir.generator import _emit

    stripped = line.rstrip("\n")
    if stripped:
        _emit(on_progress, "text", stripped)
