"""Tests for ignore file injection system."""

from pathlib import Path
from unittest.mock import patch

from skillnir.injector import inject_ignore
from skillnir.remover import delete_ignore, find_ignore_installations
from skillnir.scaffold import assemble_ignore, get_ignore_templates, init_ignore
from skillnir.tools import AITool


def _make_templates(tmp_path: Path) -> Path:
    """Create a minimal set of ignore templates for testing."""
    tdir = tmp_path / "templates"
    tdir.mkdir(parents=True)
    (tdir / "common.txt").write_text("# Common\n.git/\n.DS_Store\n")
    (tdir / "python.txt").write_text("# Python\n__pycache__/\n.venv/\n")
    (tdir / "javascript.txt").write_text("# JS\nnode_modules/\ndist/\n")
    return tdir


def _tool_with_ignore(name: str = "TestTool", ignore_file: str = ".testignore") -> AITool:
    return AITool(name=name, dotdir=".testtool", company="Co", ignore_file=ignore_file)


def _tool_without_ignore(name: str = "NoIgnore") -> AITool:
    return AITool(name=name, dotdir=".noignore", company="Co")


class TestGetIgnoreTemplates:
    def test_returns_available_templates(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        templates = get_ignore_templates(tdir)
        assert "python" in templates
        assert "javascript" in templates

    def test_excludes_missing_templates(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        templates = get_ignore_templates(tdir)
        # "java" template not created in _make_templates
        assert "java" not in templates


class TestAssembleIgnore:
    def test_includes_common(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        content = assemble_ignore(["python"], tdir)
        assert ".git/" in content
        assert "__pycache__/" in content

    def test_combines_multiple(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        content = assemble_ignore(["python", "javascript"], tdir)
        assert "__pycache__/" in content
        assert "node_modules/" in content

    def test_empty_selection_has_common(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        content = assemble_ignore([], tdir)
        assert ".git/" in content

    def test_skips_missing_template(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        content = assemble_ignore(["python", "nonexistent"], tdir)
        assert "__pycache__/" in content


class TestInitIgnore:
    def test_creates_ignore_files(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        result = init_ignore(
            tmp_path, ["python"], [".claudeignore", ".cursorignore"], tdir
        )
        assert result.success is True
        assert (tmp_path / ".data" / "ignore" / ".claudeignore").is_file()
        assert (tmp_path / ".data" / "ignore" / ".cursorignore").is_file()

    def test_content_has_selected_templates(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        init_ignore(tmp_path, ["python"], [".testignore"], tdir)
        content = (tmp_path / ".data" / "ignore" / ".testignore").read_text()
        assert "__pycache__/" in content
        assert ".git/" in content  # common always included

    def test_deduplicates_ignore_files(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        result = init_ignore(
            tmp_path,
            ["python"],
            [".geminiignore", ".geminiignore"],
            tdir,
        )
        assert result.success is True
        assert len(result.created_files) == 1

    def test_skips_empty_ignore_files(self, tmp_path: Path):
        tdir = _make_templates(tmp_path)
        result = init_ignore(tmp_path, ["python"], ["", ".testignore"], tdir)
        assert result.success is True
        assert len(result.created_files) == 1


class TestInjectIgnore:
    def test_creates_symlink(self, tmp_path: Path):
        # Setup: create source ignore file
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".testignore").write_text("# test\n")

        tool = _tool_with_ignore()
        results = inject_ignore(tmp_path, [tool])

        assert len(results) == 1
        assert results[0].created is True
        assert (tmp_path / ".testignore").is_symlink()

    def test_skips_tool_without_ignore_file(self, tmp_path: Path):
        tool = _tool_without_ignore()
        results = inject_ignore(tmp_path, [tool])
        assert len(results) == 0

    def test_skips_existing_symlink(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".testignore").write_text("# test\n")

        tool = _tool_with_ignore()
        inject_ignore(tmp_path, [tool])
        results = inject_ignore(tmp_path, [tool])

        assert len(results) == 1
        assert results[0].created is False
        assert results[0].error is None

    def test_error_when_source_missing(self, tmp_path: Path):
        tool = _tool_with_ignore()
        results = inject_ignore(tmp_path, [tool])

        assert len(results) == 1
        assert results[0].created is False
        assert "Source not found" in results[0].error

    def test_deduplicates_same_ignore_file(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".geminiignore").write_text("# test\n")

        tool_a = AITool(
            name="Gemini CLI", dotdir=".gemini", company="Google",
            ignore_file=".geminiignore",
        )
        tool_b = AITool(
            name="Antigravity", dotdir=".agent", company="Google",
            ignore_file=".geminiignore",
        )
        results = inject_ignore(tmp_path, [tool_a, tool_b])

        # Only one symlink should be created (deduplicated by ignore_file name)
        assert len(results) == 1
        assert results[0].created is True

    def test_multiple_tools(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".claudeignore").write_text("# test\n")
        (ignore_dir / ".cursorignore").write_text("# test\n")

        tools = [
            AITool(name="Claude", dotdir=".claude", company="Anthropic",
                   ignore_file=".claudeignore"),
            AITool(name="Cursor", dotdir=".cursor", company="Anysphere",
                   ignore_file=".cursorignore"),
        ]
        results = inject_ignore(tmp_path, tools)

        assert len(results) == 2
        assert all(r.created for r in results)

    def test_handles_os_error(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".testignore").write_text("# test\n")

        tool = _tool_with_ignore()
        with patch.object(Path, "symlink_to", side_effect=OSError("permission denied")):
            results = inject_ignore(tmp_path, [tool])
            assert results[0].created is False
            assert "permission denied" in results[0].error


class TestDeleteIgnore:
    def test_removes_symlinks(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".claudeignore").write_text("# test\n")

        # Create symlink
        symlink = tmp_path / ".claudeignore"
        symlink.symlink_to(Path(".data") / "ignore" / ".claudeignore")
        assert symlink.is_symlink()

        result = delete_ignore(tmp_path)
        assert len(result.removed_symlinks) >= 1
        assert not symlink.exists()

    def test_removes_data_directory(self, tmp_path: Path):
        ignore_dir = tmp_path / ".data" / "ignore"
        ignore_dir.mkdir(parents=True)
        (ignore_dir / ".claudeignore").write_text("# test\n")

        result = delete_ignore(tmp_path, delete_data=True)
        assert result.removed_data is True
        assert not ignore_dir.exists()

    def test_no_error_when_nothing_to_remove(self, tmp_path: Path):
        (tmp_path / ".data").mkdir(parents=True)
        result = delete_ignore(tmp_path)
        assert result.error is None
        assert len(result.removed_symlinks) == 0


class TestAIToolIgnoreFile:
    def test_top_tools_have_ignore_file(self):
        from skillnir.tools import TOOLS

        top_tools = ["Claude Code", "Cursor", "Windsurf", "GitHub Copilot", "Cline"]
        for tool in TOOLS:
            if tool.name in top_tools:
                assert tool.ignore_file, f"{tool.name} should have ignore_file set"

    def test_ignore_file_starts_with_dot(self):
        from skillnir.tools import TOOLS

        for tool in TOOLS:
            if tool.ignore_file:
                assert tool.ignore_file.startswith("."), (
                    f"{tool.name}'s ignore_file should start with '.'"
                )
