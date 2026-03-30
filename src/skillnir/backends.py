"""Multi-backend support for AI generation (Claude, Gemini, Copilot)."""

import functools
import json
import shutil
import subprocess
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
                "claude-opus-4-6", "opus", "Claude Opus 4.6", is_default=True, tier=1
            ),
            ModelInfo("claude-sonnet-4-6", "sonnet", "Claude Sonnet 4.6", tier=2),
            ModelInfo("claude-haiku-4-5-20251001", "haiku", "Claude Haiku 4.5", tier=3),
            ModelInfo("claude-opus-4-0-20250514", "opus-4.0", "Claude Opus 4", tier=1),
            ModelInfo(
                "claude-sonnet-4-0-20250514", "sonnet-4.0", "Claude Sonnet 4", tier=2
            ),
            ModelInfo(
                "claude-sonnet-4-5-20251001", "sonnet-4.5", "Claude Sonnet 4.5", tier=2
            ),
            ModelInfo(
                "claude-3-5-sonnet-20241022", "3.5-sonnet", "Claude 3.5 Sonnet", tier=2
            ),
            ModelInfo(
                "claude-3-5-haiku-20241022", "3.5-haiku", "Claude 3.5 Haiku", tier=3
            ),
            ModelInfo("claude-3-opus-20240229", "3-opus", "Claude 3 Opus", tier=1),
            ModelInfo("claude-3-haiku-20240307", "3-haiku", "Claude 3 Haiku", tier=3),
        ),
        default_model="sonnet",
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
            ModelInfo("auto", "auto", "Auto (recommended)", is_default=True, tier=2),
            ModelInfo("gpt-5.4", "gpt-5.4", "GPT-5.4", tier=1),
            ModelInfo("gpt-5.3-code", "gpt-5.3-code", "GPT-5.3 Code", tier=1),
            ModelInfo("claude-opus-4-6", "opus", "Claude Opus 4.6", tier=1),
            ModelInfo("claude-sonnet-4-6", "sonnet", "Claude Sonnet 4.6", tier=2),
            ModelInfo("gemini-2.5-pro", "gemini-pro", "Gemini 2.5 Pro", tier=2),
            ModelInfo("gpt-4o", "gpt-4o", "GPT-4o", tier=2),
            ModelInfo("o3", "o3", "o3", tier=1),
            ModelInfo("claude-haiku-4-5", "haiku", "Claude Haiku 4.5", tier=3),
            ModelInfo("gpt-5.3", "gpt-5.3", "GPT-5.3", tier=2),
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
            ModelInfo("gpt-4o", "gpt-4o", "GPT-4o", is_default=True, tier=2),
            ModelInfo("claude-sonnet-4", "claude-sonnet", "Claude Sonnet 4", tier=2),
            ModelInfo("o3", "o3", "o3", tier=1),
            ModelInfo("o4-mini", "o4-mini", "o4-mini", tier=3),
            ModelInfo("gpt-5.4", "gpt-5.4", "GPT-5.4", tier=1),
            ModelInfo("gpt-5.3", "gpt-5.3", "GPT-5.3", tier=2),
            ModelInfo("claude-opus-4-6", "claude-opus", "Claude Opus 4.6", tier=1),
            ModelInfo("gemini-2.5-pro", "gemini-pro", "Gemini 2.5 Pro", tier=1),
            ModelInfo("o3-pro", "o3-pro", "o3 Pro", tier=1),
            ModelInfo("gpt-4o-mini", "gpt-4o-mini", "GPT-4o Mini", tier=3),
        ),
        default_model="gpt-4o",
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


@dataclass
class AppConfig:
    """User's persisted backend/model preferences."""

    backend: AIBackend = AIBackend.CLAUDE
    model: str = "sonnet"
    prompt_version: str = field(default_factory=_default_prompt_version)

    def to_dict(self) -> dict:
        return {
            "backend": self.backend.value,
            "model": self.model,
            "prompt_version": self.prompt_version,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AppConfig":
        try:
            backend = AIBackend(d.get("backend", "claude"))
        except ValueError:
            backend = AIBackend.CLAUDE
        model = d.get("model", BACKENDS[backend].default_model)
        pv = d.get("prompt_version", _default_prompt_version())
        if pv not in get_prompt_versions():
            pv = _default_prompt_version()
        return cls(backend=backend, model=model, prompt_version=pv)


def load_config() -> AppConfig:
    """Load config from ~/.skillnir/config.json, or return defaults."""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return AppConfig.from_dict(data)
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
    """Persist config to ~/.skillnir/config.json."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )


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
) -> list[str]:
    """Build CLI command for the given backend."""
    info = BACKENDS[backend]
    model_id = (
        resolve_model_id(backend, model)
        if model
        else resolve_model_id(backend, info.default_model)
    )
    prompt, extra_flags = _apply_mode(prompt, mode, info)

    if backend == AIBackend.CLAUDE:
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
    elif backend == AIBackend.CURSOR:
        cmd = [
            info.cli_command,
            "-p",
            "--output-format",
            "stream-json",
            "--model",
            model_id,
            "--trust",
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
            _emit(on_progress, "text", result_text)
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
