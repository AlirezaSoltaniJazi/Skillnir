"""Tests for skillnir.skill_generator -- skill prompt loading, output checking."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.skill_generator import (
    SKILL_SCOPES,
    SCOPE_LABELS,
    _build_user_prompt,
    _check_skill_outputs,
    _find_reference_skill,
    generate_skill,
    load_skill_prompt,
)

# ── load_skill_prompt ────────────────────────────────────────


class TestLoadSkillPrompt:
    def test_loads_v1_backend_prompt(self):
        text = load_skill_prompt("backend", "v1")
        assert len(text) > 0

    def test_invalid_scope_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid scope"):
            load_skill_prompt("nonexistent", "v1")

    def test_all_scopes_load_discovered_versions(self):
        from skillnir.backends import get_prompt_versions

        for version in get_prompt_versions():
            for scope in SKILL_SCOPES:
                text = load_skill_prompt(scope, version)
                assert len(text) > 0

    def test_raises_when_prompt_file_missing(self, tmp_path: Path):
        with patch("skillnir.skill_generator.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_skill_prompt("backend", "v1")


# ── SCOPE constants ──────────────────────────────────────────


class TestScopeConstants:
    def test_all_scopes_have_labels(self):
        for scope in SKILL_SCOPES:
            assert scope in SCOPE_LABELS


# ── _find_reference_skill ────────────────────────────────────


class TestFindReferenceSkill:
    def test_finds_matching_keyword(self, tmp_path: Path):
        skill_dir = tmp_path / "my-server-backend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: ref\n---\n")

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result = _find_reference_skill("backend")
            assert result is not None
            assert "server" in result.name.lower() or "backend" in result.name.lower()

    def test_falls_back_to_first_skill(self, tmp_path: Path):
        skill_dir = tmp_path / "unrelated-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: ref\n---\n")

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result = _find_reference_skill("ios")
            assert result is not None

    def test_returns_none_when_no_skills(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            assert _find_reference_skill("backend") is None


# ── _build_user_prompt ───────────────────────────────────────


class TestBuildUserPrompt:
    def test_contains_project_path(self, tmp_path: Path):
        with patch("skillnir.skill_generator._find_reference_skill", return_value=None):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert str(tmp_path) in prompt

    def test_contains_project_name(self, tmp_path: Path):
        with patch("skillnir.skill_generator._find_reference_skill", return_value=None):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "myproj" in prompt

    def test_contains_scope(self, tmp_path: Path):
        with patch("skillnir.skill_generator._find_reference_skill", return_value=None):
            prompt = _build_user_prompt(tmp_path, "myproj", "frontend")
            assert "frontend" in prompt

    def test_includes_reference_skill_when_found(self, tmp_path: Path):
        ref = tmp_path / "ref-skill"
        ref.mkdir()
        (ref / "SKILL.md").write_text("---\nname: ref\n---\n")
        with patch("skillnir.skill_generator._find_reference_skill", return_value=ref):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "ref-skill" in prompt


# ── _check_skill_outputs ─────────────────────────────────────


class TestCheckSkillOutputs:
    def test_success_when_skill_md_exists_with_name(self, tmp_path: Path):
        skill_dir = tmp_path / ".data" / "skills" / "proj-backend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: proj-backend\n---\n")

        with patch("skillnir.skill_generator._copy_to_source", return_value=None):
            result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
            assert result.success is True
            assert result.target_skill_path == skill_dir / "SKILL.md"

    def test_failure_when_skill_md_missing(self, tmp_path: Path):
        result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
        assert result.success is False
        assert "SKILL.md" in result.error

    def test_failure_when_no_name_in_frontmatter(self, tmp_path: Path):
        skill_dir = tmp_path / ".data" / "skills" / "proj-backend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\ndescription: no name\n---\n")

        with patch("skillnir.skill_generator._copy_to_source", return_value=None):
            result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
            assert result.success is False
            assert "name" in result.error


# ── generate_skill (mocked orchestration) ────────────────────


class TestGenerateSkill:
    @pytest.mark.asyncio
    async def test_returns_error_on_invalid_scope(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        with patch("skillnir.skill_generator.load_config", return_value=cfg):
            result = await generate_skill(tmp_path, "proj", "nonexistent")
            assert result.success is False
            assert "Invalid scope" in result.error

    @pytest.mark.asyncio
    async def test_uses_prompt_version_override(self, tmp_path: Path):
        cfg = AppConfig(prompt_version="v1")
        captured = {}

        def mock_load(scope, version=""):
            captured["version"] = version
            raise FileNotFoundError("stop early")

        with (
            patch("skillnir.skill_generator.load_config", return_value=cfg),
            patch("skillnir.skill_generator.load_skill_prompt", side_effect=mock_load),
        ):
            result = await generate_skill(
                tmp_path, "proj", "backend", prompt_version_override="v1"
            )
            assert captured["version"] == "v1"

    @pytest.mark.asyncio
    async def test_returns_error_when_cli_not_found(self, tmp_path: Path):
        cfg = AppConfig(backend=AIBackend.GEMINI, prompt_version="v1")
        with (
            patch("skillnir.skill_generator.load_config", return_value=cfg),
            patch("skillnir.skill_generator.load_skill_prompt", return_value="prompt"),
            patch("skillnir.skill_generator._claude_sdk_available", return_value=False),
            patch("skillnir.skill_generator.shutil.which", return_value=None),
        ):
            result = await generate_skill(tmp_path, "proj", "backend")
            assert result.success is False
            assert "not found" in result.error
