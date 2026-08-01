"""Tests for skillnir.generator -- prompt loading, output checking, orchestration."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.generator import (
    _build_user_prompt,
    _check_outputs,
    _emit,
    build_context_pack,
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

    def test_accepts_uppercase_agents_md(self, tmp_path: Path):
        """A model writing the industry-standard AGENTS.md is a success."""
        (tmp_path / "AGENTS.md").write_text("# Agents")
        result = _check_outputs(tmp_path, AIBackend.CLAUDE)
        assert result.success is True
        assert result.agents_md_path is not None
        assert result.agents_md_path.name.lower() == "agents.md"


# ── build_context_pack ───────────────────────────────────────


class TestBuildContextPack:
    def test_empty_project_returns_empty(self, tmp_path: Path):
        assert build_context_pack(tmp_path) == ""

    def test_lists_files_and_manifest(self, tmp_path: Path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("print('hi')\n")
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'demo'\n")
        (tmp_path / "README.md").write_text("# Demo\n\nA demo project.\n")

        pack = build_context_pack(tmp_path)
        assert "PROJECT INVENTORY" in pack
        assert "main.py" in pack
        assert "name = 'demo'" in pack
        assert "A demo project." in pack

    def test_skips_noise_directories(self, tmp_path: Path):
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "app.py").write_text("x = 1\n")
        junk = tmp_path / "node_modules" / "pkg"
        junk.mkdir(parents=True)
        (junk / "index.js").write_text("//\n")

        pack = build_context_pack(tmp_path)
        assert "app.py" in pack
        assert "node_modules" not in pack

    def test_capped_size(self, tmp_path: Path):
        for i in range(500):
            (tmp_path / f"file-with-a-fairly-long-name-{i:04d}.py").write_text("x\n")
        pack = build_context_pack(tmp_path)
        assert len(pack) < 4200

    def test_user_prompt_includes_pack(self, tmp_path: Path):
        (tmp_path / "main.py").write_text("x = 1\n")
        prompt = _build_user_prompt(tmp_path)
        assert str(tmp_path) in prompt
        assert "PROJECT INVENTORY" in prompt


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
