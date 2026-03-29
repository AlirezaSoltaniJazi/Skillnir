"""Tests for skillnir.skills -- frontmatter parsing, skill discovery."""

from pathlib import Path


from skillnir.skills import discover_skills, parse_frontmatter


class TestParseFrontmatter:
    def test_valid_frontmatter(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text(
            "---\nname: my-skill\ndescription: A skill\nmetadata:\n  version: '1.0'\n---\n# Body\n",
            encoding="utf-8",
        )
        result = parse_frontmatter(md)
        assert result["name"] == "my-skill"
        assert result["description"] == "A skill"
        assert result["metadata"]["version"] == "1.0"

    def test_no_frontmatter_returns_empty(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("# Just markdown\nNo frontmatter here.\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}

    def test_empty_frontmatter_returns_empty(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\n---\n# Body\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}

    def test_nested_metadata(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text(
            "---\nname: deep\nmetadata:\n  version: '2.0'\n  author: test\n---\n",
            encoding="utf-8",
        )
        result = parse_frontmatter(md)
        assert result["metadata"]["version"] == "2.0"
        assert result["metadata"]["author"] == "test"


class TestDiscoverSkills:
    def test_finds_skills(self, tmp_project: Path):
        skills = discover_skills(tmp_project)
        assert len(skills) == 1
        assert skills[0].name == "test-skill"
        assert skills[0].version == "1.0.0"

    def test_returns_empty_when_no_skills_dir(self, tmp_path: Path):
        assert discover_skills(tmp_path) == []

    def test_ignores_dirs_without_skill_md(self, tmp_path: Path):
        skills_dir = tmp_path / ".data" / "skills"
        (skills_dir / "no-skill-md").mkdir(parents=True)
        (skills_dir / "no-skill-md" / "README.md").write_text("hi")
        assert discover_skills(tmp_path) == []

    def test_ignores_files_in_skills_dir(self, tmp_path: Path):
        skills_dir = tmp_path / ".data" / "skills"
        skills_dir.mkdir(parents=True)
        (skills_dir / "not-a-dir.txt").write_text("hi")
        assert discover_skills(tmp_path) == []

    def test_sorts_by_directory_name(self, tmp_path: Path):
        skills_dir = tmp_path / ".data" / "skills"
        for name in ("z-skill", "a-skill"):
            d = skills_dir / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text(
                f"---\nname: {name}\ndescription: ''\nmetadata:\n  version: '1.0'\n---\n"
            )
        skills = discover_skills(tmp_path)
        assert [s.name for s in skills] == ["a-skill", "z-skill"]

    def test_uses_dir_name_when_frontmatter_has_no_name(self, tmp_path: Path):
        d = tmp_path / ".data" / "skills" / "fallback-name"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\ndescription: no name\n---\n")
        skills = discover_skills(tmp_path)
        assert skills[0].name == "fallback-name"


class TestParseFrontmatterEdgeCases:
    def test_no_closing_fence_returns_empty(self, tmp_path: Path):
        """Malformed YAML with opening --- but no closing --- should not crash."""
        md = tmp_path / "SKILL.md"
        md.write_text("---\nname: broken\ndescription: oops\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}

    def test_empty_file_returns_empty(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("", encoding="utf-8")
        assert parse_frontmatter(md) == {}

    def test_only_dashes_returns_empty(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}

    def test_fence_with_only_whitespace_between(self, tmp_path: Path):
        md = tmp_path / "SKILL.md"
        md.write_text("---\n   \n---\n", encoding="utf-8")
        assert parse_frontmatter(md) == {}


class TestDiscoverSkillsEdgeCases:
    def test_skill_with_malformed_frontmatter(self, tmp_path: Path):
        """Skills with missing closing --- should still be discovered with defaults."""
        d = tmp_path / ".data" / "skills" / "broken-skill"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text("---\nname: broken\n", encoding="utf-8")
        skills = discover_skills(tmp_path)
        assert len(skills) == 1
        assert skills[0].name == "broken-skill"  # falls back to dir name
        assert skills[0].version == "unknown"
