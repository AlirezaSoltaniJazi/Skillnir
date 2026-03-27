"""Tests for skillnir.scaffold -- skill and docs scaffolding."""

from pathlib import Path

from skillnir.scaffold import (
    init_docs,
    init_skill,
    validate_skill_name,
)


class TestValidateSkillName:
    def test_valid_names(self):
        assert validate_skill_name("my-skill") is None
        assert validate_skill_name("backend") is None
        assert validate_skill_name("e2e-testing") is None
        assert validate_skill_name("skill-v2") is None
        assert validate_skill_name("a") is None
        assert validate_skill_name("a1b2") is None

    def test_empty_name(self):
        assert validate_skill_name("") is not None

    def test_too_long(self):
        assert validate_skill_name("a" * 65) is not None
        assert validate_skill_name("a" * 64) is None

    def test_uppercase(self):
        assert validate_skill_name("My-Skill") is not None

    def test_underscores(self):
        assert validate_skill_name("my_skill") is not None

    def test_leading_hyphen(self):
        assert validate_skill_name("-my-skill") is not None

    def test_trailing_hyphen(self):
        assert validate_skill_name("my-skill-") is not None

    def test_consecutive_hyphens(self):
        assert validate_skill_name("my--skill") is not None

    def test_spaces(self):
        assert validate_skill_name("my skill") is not None


class TestInitSkill:
    def test_creates_correct_structure(self, tmp_path: Path):
        result = init_skill(tmp_path, "my-skill")

        assert result.success is True
        assert result.error is None

        skill_dir = tmp_path / ".data" / "skills" / "my-skill"
        assert skill_dir.is_dir()
        assert (skill_dir / "SKILL.md").exists()
        assert (skill_dir / "INJECT.md").exists()
        assert (skill_dir / "LEARNED.md").exists()
        assert (skill_dir / "references" / ".gitkeep").exists()
        assert (skill_dir / "scripts" / ".gitkeep").exists()
        assert (skill_dir / "assets" / ".gitkeep").exists()
        assert (skill_dir / "agents" / ".gitkeep").exists()

    def test_skill_md_contains_name(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "name: my-skill" in content

    def test_inject_md_contains_name(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "INJECT.md").read_text(
            encoding="utf-8"
        )
        assert "my-skill" in content

    def test_rejects_invalid_name(self, tmp_path: Path):
        result = init_skill(tmp_path, "Invalid_Name")
        assert result.success is False
        assert result.error is not None

    def test_rejects_existing_directory(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        result = init_skill(tmp_path, "my-skill")
        assert result.success is False
        assert "already exists" in result.error

    def test_learned_md_contains_sections(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "LEARNED.md").read_text(
            encoding="utf-8"
        )
        assert "## Corrections" in content
        assert "## Preferences" in content
        assert "## Discovered Conventions" in content

    def test_skill_md_references_learned(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "LEARNED.md" in content

    def test_skill_md_contains_sub_agent_section(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "Sub-Agent Delegation" in content

    def test_inject_md_contains_sub_agents_line(self, tmp_path: Path):
        init_skill(tmp_path, "my-skill")
        content = (tmp_path / ".data" / "skills" / "my-skill" / "INJECT.md").read_text(
            encoding="utf-8"
        )
        assert "Sub-agents" in content

    def test_created_files_list(self, tmp_path: Path):
        result = init_skill(tmp_path, "my-skill")
        assert (
            len(result.created_files) == 7
        )  # SKILL.md, INJECT.md, LEARNED.md, 4x .gitkeep


class TestInitDocs:
    def test_creates_agents_md_and_symlinks(self, tmp_path: Path):
        result = init_docs(tmp_path)

        assert result.success is True
        assert result.error is None
        assert (tmp_path / "agents.md").exists()
        assert (tmp_path / ".claude" / "claude.md").is_symlink()
        assert (tmp_path / ".github" / "copilot-instructions.md").is_symlink()

    def test_symlinks_point_to_agents_md(self, tmp_path: Path):
        init_docs(tmp_path)

        claude_md = tmp_path / ".claude" / "claude.md"
        assert claude_md.resolve() == (tmp_path / "agents.md").resolve()

        copilot_md = tmp_path / ".github" / "copilot-instructions.md"
        assert copilot_md.resolve() == (tmp_path / "agents.md").resolve()

    def test_agents_md_contains_project_name(self, tmp_path: Path):
        init_docs(tmp_path)
        content = (tmp_path / "agents.md").read_text(encoding="utf-8")
        assert tmp_path.name in content

    def test_rejects_existing_agents_md(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("existing", encoding="utf-8")
        result = init_docs(tmp_path)
        assert result.success is False
        assert "already exists" in result.error

    def test_does_not_overwrite_existing_claude_md(self, tmp_path: Path):
        # Pre-create .claude/claude.md as a real file
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "claude.md").write_text("custom", encoding="utf-8")

        result = init_docs(tmp_path)
        assert result.success is True
        # claude.md should be unchanged (real file, not overwritten)
        assert (claude_dir / "claude.md").read_text(encoding="utf-8") == "custom"

    def test_created_files_list(self, tmp_path: Path):
        result = init_docs(tmp_path)
        assert (
            len(result.created_files) == 3
        )  # agents.md, claude.md, copilot-instructions.md

    def test_symlinks_use_correct_relative_paths(self, tmp_path: Path):
        """Symlinks should use ../agents.md to correctly reference the project root."""
        init_docs(tmp_path)

        claude_md = tmp_path / ".claude" / "claude.md"
        copilot_md = tmp_path / ".github" / "copilot-instructions.md"

        # Both are one level deep, so ../agents.md should work
        assert str(claude_md.readlink()) == str(Path("..") / "agents.md")
        assert str(copilot_md.readlink()) == str(Path("..") / "agents.md")

        # Verify they actually resolve to the same file
        assert claude_md.resolve() == copilot_md.resolve()
