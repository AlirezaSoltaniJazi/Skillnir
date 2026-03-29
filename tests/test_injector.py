"""Tests for skillnir.injector -- symlink creation."""

from pathlib import Path
from unittest.mock import patch


from skillnir.injector import inject_skill
from skillnir.skills import Skill
from skillnir.tools import AITool


def _make_skill(tmp_path: Path, name: str = "test-skill") -> Skill:
    skill_dir = tmp_path / ".data" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n")
    return Skill(name=name, description="", version="1.0", path=skill_dir)


class TestInjectSkill:
    def test_creates_symlink(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")
        results = inject_skill(tmp_path, skill, [tool])

        assert len(results) == 1
        assert results[0].created is True
        assert results[0].symlink_path.is_symlink()

    def test_creates_parent_directories(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")
        inject_skill(tmp_path, skill, [tool])

        parent = tmp_path / ".testtool" / "skills"
        assert parent.is_dir()

    def test_skips_existing_symlink(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")

        inject_skill(tmp_path, skill, [tool])
        results = inject_skill(tmp_path, skill, [tool])

        assert len(results) == 1
        assert results[0].created is False
        assert results[0].error is None

    def test_skips_existing_directory(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")
        existing = tmp_path / ".testtool" / "skills" / skill.dir_name
        existing.mkdir(parents=True)

        results = inject_skill(tmp_path, skill, [tool])
        assert results[0].created is False

    def test_multiple_tools(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tools = [
            AITool(name="A", dotdir=".a", company="Co"),
            AITool(name="B", dotdir=".b", company="Co"),
        ]
        results = inject_skill(tmp_path, skill, tools)
        assert len(results) == 2
        assert all(r.created for r in results)

    def test_symlink_uses_dir_name_not_yaml_name(self, tmp_path: Path):
        """When YAML name differs from directory name, symlink should use dir name."""
        skill_dir = tmp_path / ".data" / "skills" / "backendEngineer"
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text("---\nname: Backend Engineer\n---\n")
        skill = Skill(
            name="Backend Engineer",
            description="",
            version="1.0",
            path=skill_dir,
        )
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")
        results = inject_skill(tmp_path, skill, [tool])

        assert results[0].created is True
        symlink = results[0].symlink_path
        assert symlink.name == "backendEngineer"
        assert "backendEngineer" in str(symlink.readlink())

    def test_handles_os_error(self, tmp_path: Path):
        skill = _make_skill(tmp_path)
        tool = AITool(name="TestTool", dotdir=".testtool", company="Co")

        with patch.object(Path, "symlink_to", side_effect=OSError("permission denied")):
            results = inject_skill(tmp_path, skill, [tool])
            assert results[0].created is False
            assert "permission denied" in results[0].error
