"""Tests for skillnir.tools -- tool registry and detection."""

from pathlib import Path

from skillnir.tools import AITool, AUTO_INJECT_TOOL, TOOLS, detect_tools


class TestToolsRegistry:
    def test_tools_tuple_is_non_empty(self):
        assert len(TOOLS) > 0

    def test_auto_inject_tool_exists(self):
        assert AUTO_INJECT_TOOL.dotdir == ".agents"

    def test_all_tools_have_required_fields(self):
        for tool in TOOLS:
            assert tool.name
            assert tool.dotdir.startswith(".")
            assert tool.company

    def test_claude_code_in_registry(self):
        names = [t.name for t in TOOLS]
        assert "Claude Code" in names

    def test_cursor_in_registry(self):
        names = [t.name for t in TOOLS]
        assert "Cursor" in names


class TestAIToolDefaults:
    def test_default_skills_subpath(self):
        tool = AITool(name="X", dotdir=".x", company="Y")
        assert tool.skills_subpath == "skills"

    def test_default_scores_are_zero(self):
        tool = AITool(name="X", dotdir=".x", company="Y")
        assert tool.popularity == 0
        assert tool.performance == 0
        assert tool.price == 0

    def test_frozen_dataclass(self):
        tool = AITool(name="X", dotdir=".x", company="Y")
        with __import__("pytest").raises(AttributeError):
            tool.name = "Z"


class TestDetectTools:
    def test_detects_existing_dotdirs(self, tmp_path: Path):
        (tmp_path / ".claude").mkdir()
        (tmp_path / ".cursor").mkdir()
        found = detect_tools(tmp_path)
        names = [t.name for t in found]
        assert "Claude Code" in names
        assert "Cursor" in names

    def test_returns_empty_when_no_dotdirs(self, tmp_path: Path):
        assert detect_tools(tmp_path) == []

    def test_only_returns_matching_tools(self, tmp_path: Path):
        (tmp_path / ".gemini").mkdir()
        found = detect_tools(tmp_path)
        assert len(found) == 1
        assert found[0].name == "Gemini CLI"
