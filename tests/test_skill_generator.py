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
            result, same_scope = _find_reference_skill("backend")
            assert result is not None
            assert same_scope is True
            assert "server" in result.name.lower() or "backend" in result.name.lower()

    def test_matches_camel_case_tokens(self, tmp_path: Path):
        skill_dir = tmp_path / "djangoBackend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: ref\n---\n")

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result, same_scope = _find_reference_skill("django")
            assert result == skill_dir
            assert same_scope is True

    def test_go_scope_does_not_match_django(self, tmp_path: Path):
        """Substring matching let 'go' pick any 'django*' skill."""
        skill_dir = tmp_path / "djangoBackend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: ref\n---\n")

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result, same_scope = _find_reference_skill("go")
            # Only the any-scope fallback remains — flagged as such.
            assert result == skill_dir
            assert same_scope is False

    def test_matches_frontmatter_description(self, tmp_path: Path):
        skill_dir = tmp_path / "gopherHelper"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: ref\ndescription: Golang goroutine patterns\n---\n"
        )

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result, same_scope = _find_reference_skill("go")
            assert result == skill_dir
            assert same_scope is True

    def test_falls_back_to_first_skill(self, tmp_path: Path):
        skill_dir = tmp_path / "unrelated-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: ref\n---\n")

        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            result, same_scope = _find_reference_skill("ios")
            assert result is not None
            assert same_scope is False

    def test_returns_none_when_no_skills(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator.get_source_skills_dir", return_value=tmp_path
        ):
            assert _find_reference_skill("backend") == (None, False)


# ── _build_user_prompt ───────────────────────────────────────


class TestBuildUserPrompt:
    def test_contains_project_path(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert str(tmp_path) in prompt

    def test_contains_project_name(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "myproj" in prompt

    def test_contains_scope(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "frontend")
            assert "frontend" in prompt

    def test_includes_reference_skill_when_found(self, tmp_path: Path):
        ref = tmp_path / "ref-skill"
        ref.mkdir()
        (ref / "SKILL.md").write_text("---\nname: ref\n---\n")
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(ref, True),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "ref-skill" in prompt
            assert "DIFFERENT domain" not in prompt

    def test_fallback_reference_is_marked_structure_only(self, tmp_path: Path):
        ref = tmp_path / "other-domain-skill"
        ref.mkdir()
        (ref / "SKILL.md").write_text("---\nname: ref\n---\n")
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(ref, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "DIFFERENT domain" in prompt

    def test_pure_mode_marker_present(self, tmp_path: Path):
        """Pure mode must include explicit instructions to skip the scan."""
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend", pure=True)
            assert "PURE MODE" in prompt
            assert "Do NOT scan" in prompt
            assert "YOUR_PROJECT" in prompt

    def test_default_mode_has_no_pure_marker(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "PURE MODE" not in prompt

    def test_inlines_existing_learned_md(self, tmp_path: Path):
        """Regeneration must carry accumulated corrections forward."""
        skill_dir = tmp_path / ".data" / "skills" / "myproj"
        skill_dir.mkdir(parents=True)
        (skill_dir / "LEARNED.md").write_text(
            "# Learned\n\n## Corrections\n\n- 2026-06-01: always use httpx\n"
        )
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "EXISTING LEARNED.md" in prompt
            assert "always use httpx" in prompt

    def test_empty_learned_template_not_inlined(self, tmp_path: Path):
        skill_dir = tmp_path / ".data" / "skills" / "myproj"
        skill_dir.mkdir(parents=True)
        (skill_dir / "LEARNED.md").write_text(
            "# Learned\n\n## Corrections\n\n## Preferences\n"
        )
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(tmp_path, "myproj", "backend")
            assert "EXISTING LEARNED.md" not in prompt

    def test_extra_instructions_appended(self, tmp_path: Path):
        with patch(
            "skillnir.skill_generator._find_reference_skill",
            return_value=(None, False),
        ):
            prompt = _build_user_prompt(
                tmp_path,
                "myproj",
                "backend",
                extra_instructions="REPAIR PASS — fix INJECT.md",
            )
            assert "REPAIR PASS — fix INJECT.md" in prompt


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


class TestDjangoScope:
    def test_in_skill_scopes(self):
        assert "django" in SKILL_SCOPES

    def test_has_label(self):
        assert "django" in SCOPE_LABELS
        assert "Django" in SCOPE_LABELS["django"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("django", "v1")
        assert "Django" in text
        assert "DRF" in text or "Django REST Framework" in text
        assert "migration" in text.lower()

    def test_in_engineering_roles_category(self):
        engineering = dict(SCOPE_CATEGORIES).get("Engineering Roles", ())
        assert "django" in engineering


class TestDeepResearcherScope:
    def test_in_skill_scopes(self):
        assert "deep-researcher" in SKILL_SCOPES

    def test_has_label(self):
        assert "deep-researcher" in SCOPE_LABELS
        assert "methodology" in SCOPE_LABELS["deep-researcher"].lower()

    def test_prompt_template_loads(self):
        text = load_skill_prompt("deep-researcher", "v1")
        assert "SIFT" in text or "CRAAP" in text
        assert "triangulation" in text.lower() or "independent sources" in text.lower()

    def test_in_business_and_people_category(self):
        business = dict(SCOPE_CATEGORIES).get("Business & People", ())
        assert "deep-researcher" in business


class TestTranslatorScope:
    def test_in_skill_scopes(self):
        assert "translator" in SKILL_SCOPES

    def test_has_label(self):
        assert "translator" in SCOPE_LABELS
        assert (
            "ICU" in SCOPE_LABELS["translator"] or "i18n" in SCOPE_LABELS["translator"]
        )

    def test_prompt_template_loads(self):
        text = load_skill_prompt("translator", "v1")
        assert "CLDR" in text
        assert "ICU" in text
        assert "RTL" in text

    def test_in_business_and_people_category(self):
        business = dict(SCOPE_CATEGORIES).get("Business & People", ())
        assert "translator" in business


class TestAndroidGoogleScope:
    def test_in_skill_scopes(self):
        assert "android-google" in SKILL_SCOPES

    def test_has_label(self):
        assert "android-google" in SCOPE_LABELS
        assert "Google" in SCOPE_LABELS["android-google"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("android-google", "v1")
        assert "github.com/android/skills" in text
        assert "Journeys" in text
        assert "Glimmer" in text
        assert "Agent Mode" in text

    def test_in_engineering_roles_category(self):
        engineering = dict(SCOPE_CATEGORIES).get("Engineering Roles", ())
        assert "android-google" in engineering


class TestAutomationReviewScope:
    def test_in_skill_scopes(self):
        assert "automation-review" in SKILL_SCOPES

    def test_has_label(self):
        assert "automation-review" in SCOPE_LABELS
        assert "Review" in SCOPE_LABELS["automation-review"]

    def test_prompt_template_loads(self):
        text = load_skill_prompt("automation-review", "v1")
        assert "ISTQB" in text
        assert "IEEE 829" in text or "29119" in text
        assert "SOLID" in text
        assert "DRY" in text
        assert "YAGNI" in text
        assert "candidate" in text.lower()
        assert ".html" in text or "HTML report" in text
        assert "Challenge Question" in text or "challenge question" in text.lower()
        assert "WebSearch" in text or "self-exten" in text.lower()

    def test_in_quality_and_testing_category(self):
        quality = dict(SCOPE_CATEGORIES).get("Quality & Testing", ())
        assert "automation-review" in quality


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


def _make_valid_skill(tmp_path: Path, skill_name: str) -> Path:
    """Create a minimal skill directory that satisfies the contract gates."""
    skill_dir = tmp_path / ".data" / "skills" / skill_name
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {skill_name}\ndescription: Test skill for unit tests\n---\n"
        "# Skill\n\nBody.\n"
    )
    (skill_dir / "INJECT.md").write_text(
        "# Quick Reference\n\n"
        "- **Stack**: Python 3.14 plus pytest and questionary for prompts\n"
        "- **Entry points**: src/main.py and the cli module\n"
        "- **Patterns**: result dataclasses, absolute imports, pathlib only\n"
        "- **Never**: edit generated SKILL.md files manually\n"
        "- **FIRST**: read LEARNED.md before generating any code\n"
    )
    (skill_dir / "LEARNED.md").write_text(
        "# Learned\n\n## Corrections\n\n## Preferences\n\n"
        "## Discovered Conventions\n"
    )
    (skill_dir / "references" / "patterns.md").write_text("# Patterns\n")
    return skill_dir


class TestCheckSkillOutputs:
    def test_success_for_contract_conforming_skill(self, tmp_path: Path):
        skill_dir = _make_valid_skill(tmp_path, "proj-backend")

        result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
        assert result.success is True
        assert result.target_skill_path == skill_dir / "SKILL.md"
        assert result.violations == []

    def test_failure_when_skill_md_missing(self, tmp_path: Path):
        result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
        assert result.success is False
        assert "SKILL.md" in result.error
        assert result.violations == []  # infra failure, not a repairable one

    def test_failure_when_no_name_in_frontmatter(self, tmp_path: Path):
        _make_valid_skill(tmp_path, "proj-backend")
        skill_dir = tmp_path / ".data" / "skills" / "proj-backend"
        (skill_dir / "SKILL.md").write_text("---\ndescription: no name\n---\n")

        result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
        assert result.success is False
        assert "name" in result.error
        assert result.violations

    def test_bare_skill_md_no_longer_passes(self, tmp_path: Path):
        """Existence-only validation let a lone SKILL.md report success."""
        skill_dir = tmp_path / ".data" / "skills" / "proj-backend"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: proj-backend\ndescription: d\n---\n"
        )

        result = _check_skill_outputs(tmp_path, "proj-backend", AIBackend.CLAUDE)
        assert result.success is False
        assert any("INJECT.md" in v for v in result.violations)
        assert any("LEARNED.md" in v for v in result.violations)
        assert any("references/" in v for v in result.violations)


class TestScopeTemplateBijection:
    def test_every_scope_has_template_and_every_template_has_scope(self):
        """generate-skill-*.md files and SKILL_SCOPES must stay in lockstep."""
        from skillnir.backends import get_prompt_versions
        from skillnir.generator import get_prompts_dir

        for version in get_prompt_versions():
            prompts_dir = get_prompts_dir(version)
            template_scopes = {
                p.stem.removeprefix("generate-skill-")
                for p in prompts_dir.glob("generate-skill-*.md")
            }
            assert template_scopes == set(SKILL_SCOPES), (
                f"{prompts_dir.name}: templates and SKILL_SCOPES drifted — "
                f"templates without scope: {template_scopes - set(SKILL_SCOPES)}, "
                f"scopes without template: {set(SKILL_SCOPES) - template_scopes}"
            )


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

    @pytest.mark.asyncio
    async def test_retries_once_on_contract_violations(self, tmp_path: Path):
        """A violating first attempt triggers exactly one repair pass."""
        from skillnir.skill_generator import SkillGenerationResult

        cfg = AppConfig(backend=AIBackend.CLAUDE, prompt_version="v1")
        calls: list[str] = []

        async def fake_sdk(*args, **kwargs):
            calls.append(kwargs.get("extra_instructions", ""))
            if len(calls) == 1:
                return SkillGenerationResult(
                    success=False,
                    skill_name="proj",
                    error="violations",
                    violations=["INJECT.md is missing (always-loaded summary)"],
                )
            return SkillGenerationResult(success=True, skill_name="proj")

        with (
            patch("skillnir.skill_generator.load_config", return_value=cfg),
            patch("skillnir.skill_generator.load_skill_prompt", return_value="p"),
            patch("skillnir.skill_generator._claude_sdk_available", return_value=True),
            patch("skillnir.skill_generator.generate_skill_sdk", side_effect=fake_sdk),
        ):
            result = await generate_skill(tmp_path, "proj", "backend")

        assert result.success is True
        assert len(calls) == 2
        assert calls[0] == ""
        assert "REPAIR PASS" in calls[1]
        assert "INJECT.md" in calls[1]

    @pytest.mark.asyncio
    async def test_no_retry_on_infrastructure_error(self, tmp_path: Path):
        from skillnir.skill_generator import SkillGenerationResult

        cfg = AppConfig(backend=AIBackend.CLAUDE, prompt_version="v1")
        calls: list[int] = []

        async def fake_sdk(*args, **kwargs):
            calls.append(1)
            return SkillGenerationResult(
                success=False, skill_name="proj", error="CLI exploded"
            )

        with (
            patch("skillnir.skill_generator.load_config", return_value=cfg),
            patch("skillnir.skill_generator.load_skill_prompt", return_value="p"),
            patch("skillnir.skill_generator._claude_sdk_available", return_value=True),
            patch("skillnir.skill_generator.generate_skill_sdk", side_effect=fake_sdk),
        ):
            result = await generate_skill(tmp_path, "proj", "backend")

        assert result.success is False
        assert len(calls) == 1
