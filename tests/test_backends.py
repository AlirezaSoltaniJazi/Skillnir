"""Tests for skillnir.backends -- config, command builder, stream parsers."""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


from skillnir.backends import (
    AIBackend,
    BACKENDS,
    AppConfig,
    _apply_mode,
    _parse_stream_json_line,
    _parse_text_line,
    build_subprocess_command,
    detect_available_backends,
    get_backend_version,
    get_prompt_version_labels,
    get_prompt_versions,
    load_config,
    parse_stream_line,
    resolve_model_id,
    save_config,
)

# ── AppConfig ────────────────────────────────────────────────


class TestAppConfig:
    def test_defaults(self):
        cfg = AppConfig()
        assert cfg.backend == AIBackend.CLAUDE
        assert cfg.model == "opus"
        assert cfg.prompt_version in get_prompt_versions()
        assert cfg.effort == "high"
        assert cfg.thinking_mode == "adaptive"

    def test_to_dict(self):
        cfg = AppConfig(backend=AIBackend.GEMINI, model="pro", prompt_version="v1")
        d = cfg.to_dict()
        assert d == {
            "backend": "gemini",
            "model": "pro",
            "prompt_version": "v1",
            "compress_prompts": False,
            "effort": "high",
            "thinking_mode": "adaptive",
            "gchat_webhook_cipher": "",
            "slack_webhook_cipher": "",
            "discord_webhook_cipher": "",
            "teams_webhook_cipher": "",
            "telegram_bot_token_cipher": "",
            "telegram_chat_id_cipher": "",
            "cliq_webhook_cipher": "",
            "notifications_enabled": False,
            "active_provider": "",
        }

    def test_webhook_url_round_trip_via_accessors(self):
        cfg = AppConfig()
        assert cfg.get_webhook_url() == ""
        cfg.set_webhook_url("https://chat.googleapis.com/v1/spaces/X/messages?key=Y")
        # Stored field is a cipher blob, not plaintext.
        assert cfg.gchat_webhook_cipher
        assert "chat.googleapis.com" not in cfg.gchat_webhook_cipher
        assert (
            cfg.get_webhook_url()
            == "https://chat.googleapis.com/v1/spaces/X/messages?key=Y"
        )

    def test_legacy_plaintext_field_migrates_to_cipher(self):
        legacy = {
            "backend": "claude",
            "gchat_webhook_url": "https://legacy.test/OLD",
            "notifications_enabled": True,
        }
        migrated = AppConfig.from_dict(legacy)
        assert migrated.gchat_webhook_cipher  # populated
        assert migrated.get_webhook_url() == "https://legacy.test/OLD"
        # to_dict() must NOT emit the legacy plaintext field.
        assert "gchat_webhook_url" not in migrated.to_dict()
        assert "gchat_webhook_cipher" in migrated.to_dict()

    def test_from_dict_round_trip(self):
        original = AppConfig(
            backend=AIBackend.COPILOT, model="claude-sonnet-4-5", prompt_version="v1"
        )
        restored = AppConfig.from_dict(original.to_dict())
        assert restored.backend == original.backend
        assert restored.model == original.model
        assert restored.prompt_version == original.prompt_version

    def test_from_dict_invalid_model_falls_back(self):
        cfg = AppConfig.from_dict(
            {"backend": "cursor", "model": "gpt-5.3"}  # stale, no longer in registry
        )
        assert cfg.backend == AIBackend.CURSOR
        assert cfg.model == BACKENDS[AIBackend.CURSOR].default_model

    def test_from_dict_invalid_backend_falls_back(self):
        cfg = AppConfig.from_dict({"backend": "nonexistent"})
        assert cfg.backend == AIBackend.CLAUDE

    def test_from_dict_invalid_prompt_version_falls_back(self):
        cfg = AppConfig.from_dict({"prompt_version": "v99"})
        assert cfg.prompt_version in get_prompt_versions()

    def test_from_dict_missing_keys_uses_defaults(self):
        cfg = AppConfig.from_dict({})
        assert cfg.backend == AIBackend.CLAUDE
        assert cfg.prompt_version in get_prompt_versions()


class TestMultiProviderCredentials:
    """Multi-provider AppConfig API: get/set/clear/has_provider_credentials."""

    def test_set_and_get_gchat(self):
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "gchat", {"url": "https://chat.googleapis.com/v1/spaces/X"}
        )
        creds = cfg.get_provider_credentials("gchat")
        assert creds == {"url": "https://chat.googleapis.com/v1/spaces/X"}
        # Stored encrypted — plaintext NOT in the cipher field
        assert "chat.googleapis.com" not in cfg.gchat_webhook_cipher

    def test_set_and_get_slack(self):
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "slack", {"url": "https://hooks.slack.com/services/T/B/X"}
        )
        assert cfg.get_provider_credentials("slack") == {
            "url": "https://hooks.slack.com/services/T/B/X"
        }

    def test_set_and_get_telegram_two_fields(self):
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "telegram",
            {
                "bot_token": "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl",
                "chat_id": "-100999",
            },
        )
        creds = cfg.get_provider_credentials("telegram")
        assert creds["bot_token"] == "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl"
        assert creds["chat_id"] == "-100999"
        # Both cipher fields populated
        assert cfg.telegram_bot_token_cipher
        assert cfg.telegram_chat_id_cipher

    def test_round_trip_all_providers_via_dict(self):
        cfg = AppConfig()
        test_creds = {
            "gchat": {"url": "https://chat.googleapis.com/v1/a"},
            "slack": {"url": "https://hooks.slack.com/services/a"},
            "discord": {"url": "https://discord.com/api/webhooks/1/a"},
            "teams": {"url": "https://prod-1.westus.logic.azure.com/x"},
            "telegram": {
                "bot_token": "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl",
                "chat_id": "@mychannel",
            },
            "cliq": {"url": "https://cliq.zoho.com/api/v2/x?zapikey=abc"},
        }
        for provider_id, creds in test_creds.items():
            cfg.set_provider_credentials(provider_id, creds)

        # Round-trip through to_dict/from_dict
        restored = AppConfig.from_dict(cfg.to_dict())
        for provider_id, expected in test_creds.items():
            assert restored.get_provider_credentials(provider_id) == expected

    def test_clear_provider_credentials(self):
        cfg = AppConfig()
        cfg.set_provider_credentials("slack", {"url": "https://hooks.slack.com/a"})
        assert cfg.has_provider_credentials("slack") is True
        cfg.clear_provider_credentials("slack")
        assert cfg.has_provider_credentials("slack") is False
        assert cfg.slack_webhook_cipher == ""

    def test_has_provider_credentials_telegram_requires_both(self):
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "telegram",
            {
                "bot_token": "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl",
                "chat_id": "",
            },
        )
        # Only one of two fields populated → not complete
        assert cfg.has_provider_credentials("telegram") is False

    def test_unknown_provider_returns_empty(self):
        cfg = AppConfig()
        assert cfg.get_provider_credentials("myspace") == {}
        cfg.set_provider_credentials("myspace", {"url": "x"})  # no-op
        assert cfg.has_provider_credentials("myspace") is False

    def test_legacy_webhook_url_accessors_still_work(self):
        cfg = AppConfig()
        cfg.set_webhook_url("https://chat.googleapis.com/v1/spaces/X")
        assert cfg.get_webhook_url() == "https://chat.googleapis.com/v1/spaces/X"
        assert (
            cfg.get_provider_credentials("gchat")["url"]
            == "https://chat.googleapis.com/v1/spaces/X"
        )


class TestActiveProviderMigration:
    def test_empty_config_has_empty_active_provider(self):
        cfg = AppConfig.from_dict({})
        assert cfg.active_provider == ""

    def test_legacy_gchat_only_config_auto_promotes(self):
        """Users upgrading from the single-provider era should get
        active_provider auto-set to 'gchat' if they had gchat configured."""
        # Build a config with only gchat cipher set (simulates upgrade)
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "gchat", {"url": "https://chat.googleapis.com/v1/a"}
        )
        d = cfg.to_dict()
        d["active_provider"] = ""  # legacy config had no such field
        restored = AppConfig.from_dict(d)
        assert restored.active_provider == "gchat"

    def test_invalid_active_provider_normalized_to_empty(self):
        cfg = AppConfig.from_dict({"active_provider": "myspace"})
        assert cfg.active_provider == ""

    def test_valid_active_provider_preserved(self):
        cfg = AppConfig.from_dict({"active_provider": "slack"})
        assert cfg.active_provider == "slack"

    def test_first_non_empty_provider_wins_when_no_gchat(self):
        """If only discord is configured but active_provider is empty,
        auto-promote discord."""
        cfg = AppConfig()
        cfg.set_provider_credentials(
            "discord", {"url": "https://discord.com/api/webhooks/1/a"}
        )
        d = cfg.to_dict()
        d["active_provider"] = ""
        restored = AppConfig.from_dict(d)
        assert restored.active_provider == "discord"


class TestConfigPersistence:
    def test_save_and_load_round_trip(self, tmp_path: Path):
        config_file = tmp_path / "config.json"
        config_dir = tmp_path

        with (
            patch("skillnir.backends.CONFIG_FILE", config_file),
            patch("skillnir.backends.CONFIG_DIR", config_dir),
        ):
            original = AppConfig(
                backend=AIBackend.GEMINI, model="flash", prompt_version="v1"
            )
            save_config(original)
            loaded = load_config()

            assert loaded.backend == AIBackend.GEMINI
            assert loaded.model == "flash"
            assert loaded.prompt_version == "v1"

    def test_load_config_returns_defaults_when_missing(self, tmp_path: Path):
        config_file = tmp_path / "nonexistent" / "config.json"
        with patch("skillnir.backends.CONFIG_FILE", config_file):
            cfg = load_config()
            assert cfg.backend == AIBackend.CLAUDE

    def test_load_config_handles_corrupt_json(self, tmp_path: Path):
        config_file = tmp_path / "config.json"
        config_file.write_text("not json!", encoding="utf-8")
        with patch("skillnir.backends.CONFIG_FILE", config_file):
            cfg = load_config()
            assert cfg.backend == AIBackend.CLAUDE

    @pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason="POSIX file mode not enforced on Windows",
    )
    def test_save_config_sets_owner_only_permissions(self, tmp_path: Path):
        config_file = tmp_path / "config.json"
        with (
            patch("skillnir.backends.CONFIG_FILE", config_file),
            patch("skillnir.backends.CONFIG_DIR", tmp_path),
        ):
            save_config(AppConfig())
        mode = os.stat(config_file).st_mode & 0o777
        assert mode == 0o600, f"expected 0o600, got {oct(mode)}"


# ── Prompt version constants ─────────────────────────────────


class TestPromptVersionDiscovery:
    def test_discovers_existing_versions(self):
        versions = get_prompt_versions()
        assert isinstance(versions, tuple)
        assert len(versions) >= 1
        assert "v1" in versions

    def test_labels_match_versions(self):
        versions = get_prompt_versions()
        labels = get_prompt_version_labels()
        assert set(labels.keys()) == set(versions)


# ── resolve_model_id ─────────────────────────────────────────


class TestResolveModelId:
    def test_alias_resolves_to_id(self):
        result = resolve_model_id(AIBackend.CLAUDE, "sonnet")
        assert result == "claude-sonnet-4-6"

    def test_unknown_alias_passed_through(self):
        result = resolve_model_id(AIBackend.CLAUDE, "custom-model-xyz")
        assert result == "custom-model-xyz"


# ── _apply_mode ──────────────────────────────────────────────


class TestApplyMode:
    def test_no_mode_returns_unchanged(self):
        info = BACKENDS[AIBackend.CLAUDE]
        prompt, flags = _apply_mode("hello", None, info)
        assert prompt == "hello"
        assert flags == []

    def test_cursor_ask_mode_returns_flags(self):
        info = BACKENDS[AIBackend.CURSOR]
        prompt, flags = _apply_mode("hello", "ask", info)
        assert prompt == "hello"
        assert "--mode" in flags
        assert "ask" in flags

    def test_claude_ask_mode_prepends_text(self):
        info = BACKENDS[AIBackend.CLAUDE]
        prompt, flags = _apply_mode("my question", "ask", info)
        assert "without making any changes" in prompt
        assert "my question" in prompt
        assert flags == []

    def test_claude_plan_mode_prepends_text(self):
        info = BACKENDS[AIBackend.CLAUDE]
        prompt, flags = _apply_mode("my task", "plan", info)
        assert "implementation plan" in prompt
        assert "my task" in prompt
        assert flags == []

    def test_unknown_mode_returns_unchanged(self):
        info = BACKENDS[AIBackend.CLAUDE]
        prompt, flags = _apply_mode("hello", "nonexistent", info)
        assert prompt == "hello"
        assert flags == []


# ── build_subprocess_command ─────────────────────────────────


class TestBuildSubprocessCommand:
    def test_claude_command(self):
        cmd = build_subprocess_command(AIBackend.CLAUDE, "test prompt", model="sonnet")
        assert cmd[0] == "claude"
        assert "-p" in cmd
        assert "test prompt" in cmd
        assert "--output-format" in cmd
        assert "stream-json" in cmd
        assert "--model" in cmd
        assert "claude-sonnet-4-6" in cmd
        assert "--max-turns" in cmd

    def test_cursor_command(self):
        cmd = build_subprocess_command(AIBackend.CURSOR, "test prompt")
        assert cmd[0] == "agent"
        assert "--trust" in cmd
        assert "--output-format" in cmd

    def test_gemini_command(self):
        cmd = build_subprocess_command(AIBackend.GEMINI, "test prompt")
        assert cmd[0] == "gemini"
        assert "--approval-mode" in cmd
        assert "yolo" in cmd

    def test_copilot_command(self):
        cmd = build_subprocess_command(AIBackend.COPILOT, "test prompt")
        assert cmd[0] == "copilot"
        assert "--allow-all-tools" in cmd
        assert "--output-format" not in cmd

    def test_mode_flags_appended(self):
        cmd = build_subprocess_command(AIBackend.CURSOR, "test", mode="ask")
        assert "--mode" in cmd
        assert "ask" in cmd

    def test_max_turns_customizable(self):
        cmd = build_subprocess_command(AIBackend.CLAUDE, "test", max_turns=5)
        idx = cmd.index("--max-turns")
        assert cmd[idx + 1] == "5"

    def test_prompt_after_double_dash(self):
        """Prompt must come after '--' so content starting with dashes isn't misinterpreted."""
        cmd = build_subprocess_command(
            AIBackend.CLAUDE, "---\nmy prompt", model="sonnet"
        )
        assert cmd[-1] == "---\nmy prompt"
        assert cmd[-2] == "--"

    def test_prompt_position_all_backends(self):
        for backend in AIBackend:
            cmd = build_subprocess_command(backend, "hello world")
            if backend == AIBackend.COPILOT:
                # Copilot uses --prompt <text> inline
                assert "--prompt" in cmd, f"{backend.value}: missing --prompt"
                idx = cmd.index("--prompt")
                assert (
                    cmd[idx + 1] == "hello world"
                ), f"{backend.value}: prompt not after --prompt"
            else:
                assert cmd[-1] == "hello world", f"{backend.value}: prompt not last"
                assert cmd[-2] == "--", f"{backend.value}: missing -- separator"


# ── Stream parsers ───────────────────────────────────────────


class TestParseStreamLine:
    def test_copilot_uses_text_parser(self):
        events = []
        parse_stream_line(
            AIBackend.COPILOT, "hello world\n", lambda p: events.append(p)
        )
        assert len(events) == 1
        assert events[0].kind == "text"
        assert events[0].content == "hello world"

    def test_claude_uses_json_parser(self):
        event = {"type": "result", "result": "done"}
        line = json.dumps(event)
        events = []
        parse_stream_line(AIBackend.CLAUDE, line, lambda p: events.append(p))
        assert len(events) == 1
        assert events[0].content == "done"


class TestParseStreamJsonLine:
    def test_assistant_text_block(self):
        event = {
            "type": "assistant",
            "message": {"content": [{"type": "text", "text": "hello"}]},
        }
        events = []
        _parse_stream_json_line(json.dumps(event), lambda p: events.append(p))
        assert len(events) == 1
        assert events[0].kind == "text"
        assert events[0].content == "hello"

    def test_assistant_tool_use_block(self):
        event = {
            "type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": "Read"}]},
        }
        events = []
        _parse_stream_json_line(json.dumps(event), lambda p: events.append(p))
        assert len(events) == 1
        assert events[0].kind == "tool_use"
        assert "Read" in events[0].content

    def test_result_event(self):
        event = {"type": "result", "result": "Generation complete"}
        events = []
        _parse_stream_json_line(json.dumps(event), lambda p: events.append(p))
        assert len(events) == 1
        assert events[0].content == "Generation complete"

    def test_empty_line_ignored(self):
        events = []
        _parse_stream_json_line("   \n", lambda p: events.append(p))
        assert events == []

    def test_invalid_json_ignored(self):
        events = []
        _parse_stream_json_line("not json {{{", lambda p: events.append(p))
        assert events == []

    def test_no_callback_does_not_crash(self):
        event = {"type": "result", "result": "ok"}
        _parse_stream_json_line(json.dumps(event), None)


class TestParseTextLine:
    def test_strips_newline(self):
        events = []
        _parse_text_line("hello world\n", lambda p: events.append(p))
        assert events[0].content == "hello world"

    def test_empty_line_ignored(self):
        events = []
        _parse_text_line("\n", lambda p: events.append(p))
        assert events == []


# ── detect_available_backends ────────────────────────────────


class TestDetectAvailableBackends:
    def test_finds_cli_in_path(self):
        def mock_which(cmd):
            return "/usr/bin/claude" if cmd == "claude" else None

        with (
            patch("skillnir.backends.shutil.which", side_effect=mock_which),
            patch.dict("sys.modules", {"claude_agent_sdk": None}),
        ):
            result = detect_available_backends()
            assert AIBackend.CLAUDE in result

    def test_no_cli_returns_empty(self):
        with (
            patch("skillnir.backends.shutil.which", return_value=None),
            patch("builtins.__import__", side_effect=ImportError),
        ):
            result = detect_available_backends()
            assert AIBackend.CLAUDE not in result


# ── get_backend_version ──────────────────────────────────────


class TestGetBackendVersion:
    def test_returns_version_string(self):
        mock_result = MagicMock(returncode=0, stdout="claude v1.2.3\n")
        with patch("skillnir.backends.subprocess.run", return_value=mock_result):
            version = get_backend_version(AIBackend.CLAUDE)
            assert version == "claude v1.2.3"

    def test_returns_none_on_failure(self):
        mock_result = MagicMock(returncode=1, stdout="")
        with patch("skillnir.backends.subprocess.run", return_value=mock_result):
            assert get_backend_version(AIBackend.CLAUDE) is None

    def test_returns_none_when_cli_not_found(self):
        with patch("skillnir.backends.subprocess.run", side_effect=FileNotFoundError):
            assert get_backend_version(AIBackend.CLAUDE) is None


# ── BackendInfo defaults ──────────────────────────────────


class TestBackendInfoDefaults:
    def test_default_slash_commands_is_empty_dict(self):
        from skillnir.backends import BackendInfo, ModelInfo

        info = BackendInfo(
            id=AIBackend.CLAUDE,
            name="Test",
            cli_command="test",
            supports_stream_json=False,
            models=(ModelInfo("m1", "m1", "M1"),),
            default_model="m1",
            usage_command=None,
            usage_url=None,
            version_command=("test", "--version"),
            icon="test",
        )
        assert info.slash_commands == {}
        assert isinstance(info.slash_commands, dict)

    def test_default_mode_flags_is_empty_dict(self):
        from skillnir.backends import BackendInfo, ModelInfo

        info = BackendInfo(
            id=AIBackend.CLAUDE,
            name="Test",
            cli_command="test",
            supports_stream_json=False,
            models=(ModelInfo("m1", "m1", "M1"),),
            default_model="m1",
            usage_command=None,
            usage_url=None,
            version_command=("test", "--version"),
            icon="test",
        )
        assert info.mode_flags == {}
        assert isinstance(info.mode_flags, dict)

    def test_all_backends_have_dict_slash_commands(self):
        for backend, info in BACKENDS.items():
            assert isinstance(
                info.slash_commands, dict
            ), f"{backend}: slash_commands not dict"

    def test_all_backends_have_dict_mode_flags(self):
        for backend, info in BACKENDS.items():
            assert isinstance(info.mode_flags, dict), f"{backend}: mode_flags not dict"


class TestEffortAndThinking:
    """Effort + thinking_mode persistence and SDK kwargs translation."""

    def test_invalid_effort_falls_back_to_default(self):
        cfg = AppConfig.from_dict({"effort": "ludicrous"})
        assert cfg.effort == "high"

    def test_invalid_thinking_mode_falls_back_to_default(self):
        cfg = AppConfig.from_dict({"thinking_mode": "telepathy"})
        assert cfg.thinking_mode == "adaptive"

    def test_valid_effort_and_thinking_round_trip(self):
        original = AppConfig(effort="max", thinking_mode="disabled")
        restored = AppConfig.from_dict(original.to_dict())
        assert restored.effort == "max"
        assert restored.thinking_mode == "disabled"

    def test_sdk_kwargs_default_omits_effort(self):
        # Default effort ("high") is implicit on the CLI/SDK side, so we
        # must NOT pass it explicitly (avoids errors on models without it).
        from skillnir.backends import build_claude_sdk_kwargs

        kwargs = build_claude_sdk_kwargs(AppConfig())
        assert "effort" not in kwargs
        assert kwargs["thinking"] == {"type": "adaptive"}

    def test_sdk_kwargs_custom_effort_passed_through(self):
        from skillnir.backends import build_claude_sdk_kwargs

        kwargs = build_claude_sdk_kwargs(AppConfig(effort="max"))
        assert kwargs["effort"] == "max"

    def test_sdk_kwargs_disabled_thinking(self):
        from skillnir.backends import build_claude_sdk_kwargs

        kwargs = build_claude_sdk_kwargs(AppConfig(thinking_mode="disabled"))
        assert kwargs["thinking"] == {"type": "disabled"}
