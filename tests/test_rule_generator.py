"""Tests for skillnir.rule_generator -- rule prompt loading, snapshot, output checking."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.rule_generator import (
    _build_rule_user_prompt,
    _check_rule_outputs,
    _snapshot_rules,
    generate_rule,
    load_rule_prompt,
)

# ── load_rule_prompt ─────────────────────────────────────────


class TestLoadRulePrompt:
    def test_loads_v1_prompt(self):
        text = load_rule_prompt("v1")
        assert len(text) > 0

    def test_loads_default_prompt(self):
        text = load_rule_prompt()
        assert len(text) > 0

    def test_raises_when_prompt_missing(self, tmp_path: Path):
        with patch("skillnir.rule_generator.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_rule_prompt("v1")


# ── _build_rule_user_prompt ──────────────────────────────────


class TestBuildRuleUserPrompt:
    def test_contains_target_path(self, tmp_path: Path):
        prompt = _build_rule_user_prompt(tmp_path, "error handling")
        assert str(tmp_path) in prompt

    def test_contains_rule_topic(self, tmp_path: Path):
        prompt = _build_rule_user_prompt(tmp_path, "React patterns")
        assert "React patterns" in prompt

    def test_contains_mkdir_instruction(self, tmp_path: Path):
        prompt = _build_rule_user_prompt(tmp_path, "topic")
        assert "mkdir" in prompt
        assert ".cursor/rules" in prompt


# ── _snapshot_rules ──────────────────────────────────────────


class TestSnapshotRules:
    def test_returns_mdc_files(self, tmp_path: Path):
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "error-handling.mdc").write_text("rule content")
        (rules_dir / "react.mdc").write_text("rule content")
        (rules_dir / "not-a-rule.txt").write_text("ignored")

        result = _snapshot_rules(tmp_path)
        assert len(result) == 2
        names = {p.name for p in result}
        assert "error-handling.mdc" in names
        assert "react.mdc" in names
        assert "not-a-rule.txt" not in names

    def test_returns_empty_when_dir_missing(self, tmp_path: Path):
        assert _snapshot_rules(tmp_path) == set()

    def test_returns_empty_when_no_mdc_files(self, tmp_path: Path):
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        assert _snapshot_rules(tmp_path) == set()


# ── _check_rule_outputs ──────────────────────────────────────


class TestCheckRuleOutputs:
    def test_success_when_new_files_created(self, tmp_path: Path):
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)

        before = set()
        (rules_dir / "new-rule.mdc").write_text("content")

        result = _check_rule_outputs(tmp_path, before, AIBackend.CLAUDE)
        assert result.success is True
        assert len(result.rule_files) == 1
        assert result.rule_files[0].name == "new-rule.mdc"

    def test_failure_when_no_new_files(self, tmp_path: Path):
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "existing.mdc").write_text("content")

        before = {rules_dir / "existing.mdc"}
        result = _check_rule_outputs(tmp_path, before, AIBackend.CLAUDE)
        assert result.success is False
        assert "No new .mdc files" in result.error

    def test_detects_only_new_files(self, tmp_path: Path):
        rules_dir = tmp_path / ".cursor" / "rules"
        rules_dir.mkdir(parents=True)
        (rules_dir / "old.mdc").write_text("old")
        before = {rules_dir / "old.mdc"}

        (rules_dir / "new1.mdc").write_text("new1")
        (rules_dir / "new2.mdc").write_text("new2")

        result = _check_rule_outputs(tmp_path, before, AIBackend.GEMINI)
        assert result.success is True
        assert len(result.rule_files) == 2
        assert result.backend_used == AIBackend.GEMINI


# ── generate_rule (mocked orchestration) ─────────────────────


class TestGenerateRule:
    @pytest.mark.asyncio
    async def test_returns_error_when_prompt_missing(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        with (
            patch("skillnir.rule_generator.load_config", return_value=cfg),
            patch(
                "skillnir.rule_generator.load_rule_prompt",
                side_effect=FileNotFoundError("missing"),
            ),
        ):
            result = await generate_rule(tmp_path, "error handling")
            assert result.success is False
            assert "missing" in result.error

    @pytest.mark.asyncio
    async def test_uses_prompt_version_override(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        captured = {}

        def mock_load(version):
            captured["version"] = version
            raise FileNotFoundError("stop early")

        with (
            patch("skillnir.rule_generator.load_config", return_value=cfg),
            patch("skillnir.rule_generator.load_rule_prompt", side_effect=mock_load),
        ):
            await generate_rule(tmp_path, "topic", prompt_version_override="v1")
            assert captured["version"] == "v1"

    @pytest.mark.asyncio
    async def test_returns_error_when_cli_not_found(self, tmp_path: Path):
        cfg = AppConfig(backend=AIBackend.GEMINI, prompt_version="v1")
        with (
            patch("skillnir.rule_generator.load_config", return_value=cfg),
            patch("skillnir.rule_generator.load_rule_prompt", return_value="prompt"),
            patch("skillnir.rule_generator._claude_sdk_available", return_value=False),
            patch("skillnir.rule_generator.shutil.which", return_value=None),
        ):
            result = await generate_rule(tmp_path, "topic")
            assert result.success is False
            assert "not found" in result.error
