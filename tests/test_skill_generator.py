"""Tests for skillnir.skill_generator -- skill prompt loading, output checking."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.skill_generator import (
    SCOPE_CATEGORIES,
    SCOPE_LABELS,
    SKILL_SCOPES,
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

    def test_pure_mode_marker_present(self, tmp_path: Path):
        """Pure mode must include explicit instructions to skip the scan."""
        with patch("skillnir.skill_generator._find_reference_skill", return_value=None):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend", pure=True)
            assert "PURE MODE" in prompt
            assert "Do NOT scan" in prompt
            assert "YOUR_PROJECT" in prompt

    def test_default_mode_has_no_pure_marker(self, tmp_path: Path):
        with patch("skillnir.skill_generator._find_reference_skill", return_value=None):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "PURE MODE" not in prompt


class TestManualTesterScope:
    def test_in_skill_scopes(self):
        assert "manual-tester" in SKILL_SCOPES

    def test_has_label(self):
        assert "manual-tester" in SCOPE_LABELS
        assert "ISTQB" in SCOPE_LABELS["manual-tester"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("manual-tester", "v1")
        assert "ISTQB" in text
        assert "Manual Tester" in text or "manual tester" in text.lower()


class TestProjectManagerScope:
    def test_in_skill_scopes(self):
        assert "project-manager" in SKILL_SCOPES

    def test_has_label(self):
        assert "project-manager" in SCOPE_LABELS
        assert "PMBOK" in SCOPE_LABELS["project-manager"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("project-manager", "v1")
        assert "PMBOK" in text
        assert "Project Manager" in text or "project manager" in text.lower()


class TestDevopsEngineerScope:
    def test_in_skill_scopes(self):
        assert "devops-engineer" in SKILL_SCOPES

    def test_has_label(self):
        assert "devops-engineer" in SCOPE_LABELS
        assert "DORA" in SCOPE_LABELS["devops-engineer"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("devops-engineer", "v1")
        assert "DORA" in text
        assert "DevOps" in text or "devops" in text.lower()


class TestUiUxDesignerScope:
    def test_in_skill_scopes(self):
        assert "ui-ux-designer" in SKILL_SCOPES

    def test_has_label(self):
        assert "ui-ux-designer" in SCOPE_LABELS
        assert "WCAG" in SCOPE_LABELS["ui-ux-designer"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("ui-ux-designer", "v1")
        assert "WCAG" in text
        assert "Nielsen" in text or "NN/g" in text


class TestFinancialManagerScope:
    def test_in_skill_scopes(self):
        assert "financial-manager" in SKILL_SCOPES

    def test_has_label(self):
        assert "financial-manager" in SCOPE_LABELS
        assert "P&L" in SCOPE_LABELS["financial-manager"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("financial-manager", "v1")
        assert "ASC 606" in text or "IFRS 15" in text
        assert "SaaS" in text


class TestHrManagerScope:
    def test_in_skill_scopes(self):
        assert "hr-manager" in SKILL_SCOPES

    def test_has_label(self):
        assert "hr-manager" in SCOPE_LABELS
        assert "interview" in SCOPE_LABELS["hr-manager"].lower()

    def test_prompt_template_loads(self):
        text = load_skill_prompt("hr-manager", "v1")
        assert "Schmidt" in text
        assert "structured interview" in text.lower()


class TestScopeCategories:
    def test_every_scope_belongs_to_exactly_one_category(self):
        """Every entry in SKILL_SCOPES must appear in exactly one SCOPE_CATEGORIES bucket."""
        seen: dict[str, str] = {}
        for category_label, scope_keys in SCOPE_CATEGORIES:
            for key in scope_keys:
                assert key not in seen, (
                    f"scope {key!r} appears in both "
                    f"{seen[key]!r} and {category_label!r}"
                )
                seen[key] = category_label

        scopes_set = set(SKILL_SCOPES)
        seen_set = set(seen.keys())
        assert seen_set == scopes_set, (
            f"category coverage mismatch — "
            f"only-in-categories: {seen_set - scopes_set}, "
            f"only-in-scopes: {scopes_set - seen_set}"
        )

    def test_categories_are_non_empty(self):
        for category_label, scope_keys in SCOPE_CATEGORIES:
            assert scope_keys, f"category {category_label!r} has no scopes"

    def test_expected_categories_present(self):
        labels = {c for c, _ in SCOPE_CATEGORIES}
        for expected in (
            "Engineering Roles",
            "Quality & Testing",
            "Architecture & Platform",
            "Design",
            "Business & People",
        ):
            assert expected in labels, f"missing category {expected!r}"


# ── _check_skill_outputs ─────────────────────────────────────


class TestCheckSkillOutputs:
    def test_success_when_skill_md_exists_with_name(self, tmp_path: Path):
        skill_dir = tmp_path / ".data" / "skills" / "proj-backend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: proj-backend\n---\n")

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
