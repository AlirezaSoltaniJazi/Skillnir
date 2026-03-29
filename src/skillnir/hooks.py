"""Manage Claude Code sound notification hooks in ~/.claude/settings.json."""

import json
import platform
import shutil
from pathlib import Path

SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

if platform.system() == "Darwin":
    SOUND_COMMAND = "afplay /System/Library/Sounds/Glass.aiff"
elif shutil.which("paplay"):
    SOUND_COMMAND = "paplay /usr/share/sounds/freedesktop/stereo/complete.oga"
else:
    SOUND_COMMAND = ""
_AGENRIX_TAG = "skillnir-sound"
HOOK_ENTRY = {
    "hooks": [
        {
            "type": "command",
            "command": SOUND_COMMAND,
            "timeout": 5,
        }
    ],
    "matcher": _AGENRIX_TAG,
}
HOOK_EVENTS = ("Stop", "PermissionRequest")


def load_settings(settings_file: Path = SETTINGS_FILE) -> dict:
    """Load Claude settings from JSON file."""
    if settings_file.exists():
        try:
            return json.loads(settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError, ValueError:
            pass
    return {}


def save_settings(data: dict, settings_file: Path = SETTINGS_FILE) -> None:
    """Write Claude settings to JSON file."""
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    settings_file.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


_SOUND_MARKERS = ("afplay", "paplay")


def _is_sound_command(command: str) -> bool:
    """Check if a command string is a known sound notification command."""
    return any(marker in command for marker in _SOUND_MARKERS)


def _is_skillnir_hook(matcher: dict) -> bool:
    """Check if a matcher dict is an skillnir-managed sound hook."""
    if matcher.get("matcher") == _AGENRIX_TAG:
        return True
    return any(
        _is_sound_command(h.get("command", ""))
        for h in matcher.get("hooks", [])
        if h.get("type") == "command"
    )


def has_sound_hook(settings: dict, event: str) -> bool:
    """Check if a sound hook exists for the given event."""
    return any(
        _is_skillnir_hook(matcher)
        for matcher in settings.get("hooks", {}).get(event, [])
    )


def remove_sound_hooks(settings: dict) -> dict:
    """Remove all sound hooks from settings."""
    hooks = settings.get("hooks", {})
    for event in HOOK_EVENTS:
        if event in hooks:
            hooks[event] = [
                matcher for matcher in hooks[event] if not _is_skillnir_hook(matcher)
            ]
            if not hooks[event]:
                del hooks[event]
    if not hooks:
        settings.pop("hooks", None)
    return settings


def is_sound_enabled(settings_file: Path = SETTINGS_FILE) -> bool:
    """Check if sound hooks are enabled for both Stop and PermissionRequest."""
    settings = load_settings(settings_file)
    return all(has_sound_hook(settings, event) for event in HOOK_EVENTS)


def enable_sound_hooks(settings_file: Path = SETTINGS_FILE) -> None:
    """Enable sound hooks for Stop and PermissionRequest events."""
    settings = load_settings(settings_file)
    hooks = settings.setdefault("hooks", {})
    for event in HOOK_EVENTS:
        if not has_sound_hook(settings, event):
            hooks.setdefault(event, []).append(HOOK_ENTRY)
    save_settings(settings, settings_file)


def disable_sound_hooks(settings_file: Path = SETTINGS_FILE) -> None:
    """Disable sound hooks by removing them from settings."""
    settings = load_settings(settings_file)
    settings = remove_sound_hooks(settings)
    save_settings(settings, settings_file)
