"""Tests for skillnir.generator -- prompt loading, output checking, orchestration."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.generator import (
    _check_outputs,
    _emit,
    get_prompts_dir,
    generate_docs,
    load_prompt,
)

# ── get_prompts_dir ──────────────────────────────────────────


class TestGetPromptsDir:
    def test_v1_resolves_to_promptsv1(self):
        result = get_prompts_dir("v1")
        assert result.name == "promptsv1"

    def test_returns_path_instance(self):
        assert isinstance(get_prompts_dir("v1"), Path)

    def test_default_resolves_to_latest(self):
        result = get_prompts_dir()
        assert result.is_dir()


# ── load_prompt ──────────────────────────────────────────────


class TestLoadPrompt:
    def test_loads_v1_prompt(self):
        text = load_prompt("v1")
        assert len(text) > 0
        assert isinstance(text, str)

    def test_loads_default_prompt(self):
        text = load_prompt()
        assert len(text) > 0

    def test_raises_when_prompt_missing(self, tmp_path: Path):
        with patch("skillnir.generator.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_prompt("v1")


# ── _emit ────────────────────────────────────────────────────


class TestEmit:
    def test_calls_callback(self):
        events = []
        _emit(lambda p: events.append(p), "phase", "Loading...")
        assert len(events) == 1
        assert events[0].kind == "phase"
        assert events[0].content == "Loading..."

    def test_noop_when_callback_is_none(self):
        _emit(None, "phase", "Loading...")

    def test_tool_name_forwarded(self):
        events = []
        _emit(lambda p: events.append(p), "tool_use", "Using Read...", tool_name="Read")
        assert events[0].tool_name == "Read"


# ── _check_outputs ───────────────────────────────────────────


class TestCheckOutputs:
    def test_success_when_agents_md_exists(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("# Agents")
        result = _check_outputs(tmp_path, AIBackend.CLAUDE)
        assert result.success is True
        assert result.agents_md_path == tmp_path / "agents.md"
        assert result.backend_used == AIBackend.CLAUDE

    def test_failure_when_agents_md_missing(self, tmp_path: Path):
        result = _check_outputs(tmp_path, AIBackend.CLAUDE)
        assert result.success is False
        assert "agents.md" in result.error

    def test_detects_claude_md_symlink(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("# Agents")
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        claude_md = claude_dir / "claude.md"
        claude_md.symlink_to(tmp_path / "agents.md")

        result = _check_outputs(tmp_path, AIBackend.CLAUDE)
        assert result.success is True
        assert result.claude_md_path == claude_md

    def test_claude_md_none_when_not_present(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("# Agents")
        result = _check_outputs(tmp_path, AIBackend.CLAUDE)
        assert result.claude_md_path is None


# ── generate_docs (mocked orchestration) ─────────────────────


class TestGenerateDocs:
    @pytest.mark.asyncio
    async def test_returns_error_when_prompt_missing(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        with (
            patch("skillnir.generator.load_config", return_value=cfg),
            patch(
                "skillnir.generator.load_prompt",
                side_effect=FileNotFoundError("missing"),
            ),
        ):
            result = await generate_docs(tmp_path)
            assert result.success is False
            assert "missing" in result.error

    @pytest.mark.asyncio
    async def test_uses_prompt_version_override(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        captured_version = {}

        def mock_load(version):
            captured_version["v"] = version
            return "prompt content"

        with (
            patch("skillnir.generator.load_config", return_value=cfg),
            patch("skillnir.generator.load_prompt", side_effect=mock_load),
            patch("skillnir.generator._claude_sdk_available", return_value=False),
            patch("skillnir.generator.shutil.which", return_value=None),
        ):
            result = await generate_docs(tmp_path, prompt_version_override="v1")
            assert captured_version["v"] == "v1"

    @pytest.mark.asyncio
    async def test_returns_error_when_cli_not_found(self, tmp_path: Path):
        cfg = AppConfig(backend=AIBackend.GEMINI, prompt_version="v1")
        with (
            patch("skillnir.generator.load_config", return_value=cfg),
            patch("skillnir.generator.load_prompt", return_value="prompt"),
            patch("skillnir.generator._claude_sdk_available", return_value=False),
            patch("skillnir.generator.shutil.which", return_value=None),
        ):
            result = await generate_docs(tmp_path)
            assert result.success is False
            assert "not found" in result.error
