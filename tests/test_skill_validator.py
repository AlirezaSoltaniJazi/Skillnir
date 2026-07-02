"""Tests for skillnir.skill_validator -- contract gates for generated skills."""

from pathlib import Path

from skillnir.skill_validator import (
    INJECT_MD_HARD_MAX_TOKENS,
    SKILL_MD_MAX_LINES,
    estimate_tokens,
    validate_skill_dir,
)


def _seed_skill(
    tmp_path: Path,
    name: str = "mySkill",
    skill_md: str | None = None,
    inject_md: str | None = None,
    learned_md: str | None = None,
    reference_count: int = 5,
) -> Path:
    skill_dir = tmp_path / name
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "scripts").mkdir()
    (skill_dir / "SKILL.md").write_text(
        skill_md
        if skill_md is not None
        else f"---\nname: {name}\ndescription: A test skill\n---\n# Body\n"
    )
    (skill_dir / "INJECT.md").write_text(
        inject_md
        if inject_md is not None
        else (
            "# Quick Reference\n\n"
            "- **Stack**: Python 3.14, pytest, questionary, NiceGUI web layer\n"
            "- **Entry points**: src/skillnir/cli.py main dispatch function\n"
            "- **Patterns**: result dataclasses, absolute imports, pathlib\n"
            "- **Never**: edit generated files, use relative imports here\n"
            "- **FIRST**: read LEARNED.md before generating any code\n"
        )
    )
    (skill_dir / "LEARNED.md").write_text(
        learned_md
        if learned_md is not None
        else (
            "# Learned\n\n## Corrections\n\n## Preferences\n\n"
            "## Discovered Conventions\n"
        )
    )
    for i in range(reference_count):
        (skill_dir / "references" / f"ref-{i}.md").write_text(f"# Ref {i}\n")
    (skill_dir / "scripts" / "validate-structure.sh").write_text("#!/bin/sh\n")
    return skill_dir


class TestValidateSkillDir:
    def test_conforming_skill_passes(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        report = validate_skill_dir(skill_dir, expected_name="mySkill")
        assert report.ok, report.violations
        assert report.warnings == []

    def test_missing_skill_md_is_violation(self, tmp_path: Path):
        report = validate_skill_dir(tmp_path / "nope")
        assert not report.ok
        assert any("SKILL.md is missing" in v for v in report.violations)

    def test_invalid_yaml_frontmatter_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(
            tmp_path, skill_md="---\nname: [unclosed\n---\n# Body\n"
        )
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("not valid YAML" in v for v in report.violations)

    def test_missing_frontmatter_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, skill_md="# Just a body, no frontmatter\n")
        report = validate_skill_dir(skill_dir)
        assert not report.ok

    def test_non_mapping_frontmatter_is_violation_not_crash(self, tmp_path: Path):
        """yaml.safe_load can return a list or scalar — must not AttributeError."""
        skill_dir = _seed_skill(
            tmp_path, skill_md="---\n- name: x\n- description: y\n---\n# B\n"
        )
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("YAML mapping" in v for v in report.violations)

        skill_dir2 = _seed_skill(
            tmp_path / "second", skill_md="---\njust a title\n---\n# B\n"
        )
        report2 = validate_skill_dir(skill_dir2)
        assert not report2.ok

    def test_exactly_300_lines_is_within_budget(self, tmp_path: Path):
        """A 300-line newline-terminated file must NOT trip the ≤300 gate."""
        lines = ["---", "name: mySkill", "description: d", "---"]
        lines += [f"- rule {i}" for i in range(SKILL_MD_MAX_LINES - len(lines))]
        content = "\n".join(lines) + "\n"
        assert len(content.splitlines()) == SKILL_MD_MAX_LINES
        skill_dir = _seed_skill(tmp_path, skill_md=content)
        report = validate_skill_dir(skill_dir)
        assert not any("lines" in v for v in report.violations), report.violations

    def test_name_mismatch_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        report = validate_skill_dir(skill_dir, expected_name="otherName")
        assert not report.ok
        assert any("expected 'otherName'" in v for v in report.violations)

    def test_missing_description_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, skill_md="---\nname: mySkill\n---\n# B\n")
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("description" in v for v in report.violations)

    def test_skill_md_over_line_budget_is_violation(self, tmp_path: Path):
        body = "\n".join(f"- rule {i}" for i in range(SKILL_MD_MAX_LINES + 10))
        skill_dir = _seed_skill(
            tmp_path,
            skill_md=f"---\nname: mySkill\ndescription: d\n---\n{body}\n",
        )
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("lines" in v for v in report.violations)

    def test_missing_inject_md_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        (skill_dir / "INJECT.md").unlink()
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("INJECT.md is missing" in v for v in report.violations)

    def test_oversized_inject_md_is_violation(self, tmp_path: Path):
        huge = "- bullet point with plenty of words in it\n" * 60
        assert estimate_tokens(huge) > INJECT_MD_HARD_MAX_TOKENS
        skill_dir = _seed_skill(tmp_path, inject_md=huge)
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("INJECT.md" in v for v in report.violations)

    def test_slightly_off_inject_budget_is_warning(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, inject_md="# tiny\n")
        report = validate_skill_dir(skill_dir)
        assert report.ok
        assert any("INJECT.md" in w for w in report.warnings)

    def test_missing_learned_md_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        (skill_dir / "LEARNED.md").unlink()
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("LEARNED.md is missing" in v for v in report.violations)

    def test_learned_md_missing_sections_is_warning(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, learned_md="# Learned\n\n## Corrections\n")
        report = validate_skill_dir(skill_dir)
        assert report.ok
        assert any("Preferences" in w for w in report.warnings)

    def test_empty_references_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, reference_count=0)
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("references/" in v for v in report.violations)

    def test_few_references_is_warning(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path, reference_count=2)
        report = validate_skill_dir(skill_dir)
        assert report.ok
        assert any("references/" in w for w in report.warnings)

    def test_too_many_sub_agents_is_violation(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        agents = skill_dir / "agents"
        agents.mkdir()
        for i in range(5):
            (agents / f"agent-{i}.md").write_text("# Agent\n")
        report = validate_skill_dir(skill_dir)
        assert not report.ok
        assert any("sub-agents" in v for v in report.violations)

    def test_agents_without_agent_tool_is_warning(self, tmp_path: Path):
        skill_dir = _seed_skill(
            tmp_path,
            skill_md=(
                "---\nname: mySkill\ndescription: d\n"
                "allowed-tools: Read Edit Write\n---\n# B\n"
            ),
        )
        (skill_dir / "agents").mkdir()
        (skill_dir / "agents" / "reviewer.md").write_text("# Agent\n")
        report = validate_skill_dir(skill_dir)
        assert report.ok
        assert any("allowed-tools" in w for w in report.warnings)

    def test_missing_validate_script_is_warning(self, tmp_path: Path):
        skill_dir = _seed_skill(tmp_path)
        (skill_dir / "scripts" / "validate-structure.sh").unlink()
        report = validate_skill_dir(skill_dir)
        assert report.ok
        assert any("validate-" in w for w in report.warnings)
