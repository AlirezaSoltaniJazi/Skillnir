"""Tests for skillnir.hooks -- Claude Code sound notification hooks."""

import json
from pathlib import Path

from skillnir.hooks import (
    _is_sound_command,
    disable_sound_hooks,
    enable_sound_hooks,
    has_sound_hook,
    is_sound_enabled,
    load_settings,
    remove_sound_hooks,
    save_settings,
)


class TestLoadSettings:
    def test_returns_empty_when_missing(self, tmp_path: Path):
        assert load_settings(tmp_path / "nope.json") == {}

    def test_returns_empty_on_corrupt_json(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json", encoding="utf-8")
        assert load_settings(bad) == {}

    def test_loads_valid_json(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        f.write_text('{"key": "val"}', encoding="utf-8")
        assert load_settings(f) == {"key": "val"}


class TestSaveSettings:
    def test_creates_parent_dirs(self, tmp_path: Path):
        f = tmp_path / "sub" / "dir" / "settings.json"
        save_settings({"a": 1}, f)
        assert json.loads(f.read_text(encoding="utf-8")) == {"a": 1}


class TestHasSoundHook:
    def test_false_when_no_hooks(self):
        assert has_sound_hook({}, "Stop") is False

    def test_false_when_no_afplay(self):
        settings = {
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo hi"}]}]}
        }
        assert has_sound_hook(settings, "Stop") is False

    def test_true_when_afplay_present(self):
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "afplay /System/Library/Sounds/Glass.aiff",
                            }
                        ]
                    }
                ]
            }
        }
        assert has_sound_hook(settings, "Stop") is True


class TestRemoveSoundHooks:
    def test_removes_afplay_hooks(self):
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "afplay /System/Library/Sounds/Glass.aiff",
                            }
                        ]
                    }
                ],
                "PermissionRequest": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "afplay /System/Library/Sounds/Glass.aiff",
                            }
                        ]
                    }
                ],
            }
        }
        result = remove_sound_hooks(settings)
        assert "hooks" not in result

    def test_preserves_non_afplay_hooks(self):
        settings = {
            "hooks": {
                "Stop": [
                    {"hooks": [{"type": "command", "command": "echo done"}]},
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "afplay /System/Library/Sounds/Glass.aiff",
                            }
                        ]
                    },
                ]
            }
        }
        result = remove_sound_hooks(settings)
        assert len(result["hooks"]["Stop"]) == 1
        assert "echo done" in result["hooks"]["Stop"][0]["hooks"][0]["command"]


class TestEnableDisable:
    def test_enable_creates_hooks(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        f.write_text("{}", encoding="utf-8")
        enable_sound_hooks(f)
        assert is_sound_enabled(f) is True

    def test_disable_removes_hooks(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        f.write_text("{}", encoding="utf-8")
        enable_sound_hooks(f)
        disable_sound_hooks(f)
        assert is_sound_enabled(f) is False

    def test_enable_is_idempotent(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        f.write_text("{}", encoding="utf-8")
        enable_sound_hooks(f)
        enable_sound_hooks(f)
        settings = load_settings(f)
        # Should have exactly one hook entry per event, not duplicates
        assert len(settings["hooks"]["Stop"]) == 1
        assert len(settings["hooks"]["PermissionRequest"]) == 1


class TestIsSoundEnabled:
    def test_false_when_no_file(self, tmp_path: Path):
        assert is_sound_enabled(tmp_path / "nope.json") is False

    def test_false_when_only_one_event(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "afplay /System/Library/Sounds/Glass.aiff",
                            }
                        ]
                    }
                ]
            }
        }
        f.write_text(json.dumps(settings), encoding="utf-8")
        assert is_sound_enabled(f) is False

    def test_true_when_both_events(self, tmp_path: Path):
        f = tmp_path / "settings.json"
        f.write_text("{}", encoding="utf-8")
        enable_sound_hooks(f)
        assert is_sound_enabled(f) is True


class TestIsSoundCommand:
    def test_afplay_detected(self):
        assert _is_sound_command("afplay /System/Library/Sounds/Glass.aiff") is True

    def test_paplay_detected(self):
        assert _is_sound_command("paplay /usr/share/sounds/complete.oga") is True

    def test_unrelated_command_not_detected(self):
        assert _is_sound_command("echo hello") is False

    def test_empty_string_not_detected(self):
        assert _is_sound_command("") is False


class TestHasSoundHookLinux:
    def test_detects_paplay_hook(self):
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "paplay /usr/share/sounds/complete.oga",
                            }
                        ]
                    }
                ]
            }
        }
        assert has_sound_hook(settings, "Stop") is True


class TestRemoveSoundHooksLinux:
    def test_removes_paplay_hooks(self):
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {
                                "type": "command",
                                "command": "paplay /usr/share/sounds/complete.oga",
                            }
                        ]
                    }
                ]
            }
        }
        result = remove_sound_hooks(settings)
        assert "hooks" not in result


class TestSoundCommandPlatform:
    def test_sound_command_is_string(self):
        from skillnir.hooks import SOUND_COMMAND

        assert isinstance(SOUND_COMMAND, str)
