"""Tests for skillnir.wiki_generator -- prompt loading, snapshot, output checks."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend
from skillnir.wiki_generator import (
    _check_wiki_outputs,
    _snapshot_wiki,
    load_wiki_prompt,
)


class TestLoadWikiPrompt:
    def test_loads_v1_prompt(self):
        text = load_wiki_prompt("v1")
        assert len(text) > 0
        assert "llms.txt" in text

    def test_loads_default_prompt(self):
        text = load_wiki_prompt()
        assert len(text) > 0

    def test_raises_when_prompt_missing(self, tmp_path: Path):
        with patch("skillnir.wiki_generator.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_wiki_prompt("v1")


class TestSnapshotWiki:
    def test_empty_when_no_files(self, tmp_path: Path):
        assert _snapshot_wiki(tmp_path) == set()

    def test_includes_llms_txt(self, tmp_path: Path):
        (tmp_path / "llms.txt").write_text("# project")
        assert _snapshot_wiki(tmp_path) == {tmp_path / "llms.txt"}

    def test_includes_docs_markdown(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "architecture.md").write_text("# arch")
        (docs / "modules.md").write_text("# mods")
        snap = _snapshot_wiki(tmp_path)
        assert docs / "architecture.md" in snap
        assert docs / "modules.md" in snap

    def test_ignores_non_markdown_in_docs(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "image.png").write_bytes(b"")
        assert _snapshot_wiki(tmp_path) == set()


class TestCheckWikiOutputs:
    def test_success_when_llms_and_docs_present(self, tmp_path: Path):
        (tmp_path / "llms.txt").write_text("# x")
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "architecture.md").write_text("# arch")

        result = _check_wiki_outputs(tmp_path, set(), AIBackend.CLAUDE)
        assert result.success is True
        assert result.llms_txt_path == tmp_path / "llms.txt"
        assert result.docs_dir == tmp_path / "docs"
        assert result.backend_used == AIBackend.CLAUDE

    def test_fails_when_llms_missing(self, tmp_path: Path):
        (tmp_path / "docs").mkdir()
        (tmp_path / "docs" / "architecture.md").write_text("# arch")
        result = _check_wiki_outputs(tmp_path, set(), AIBackend.CLAUDE)
        assert result.success is False
        assert "llms.txt" in (result.error or "")

    def test_fails_when_docs_dir_empty(self, tmp_path: Path):
        (tmp_path / "llms.txt").write_text("# x")
        (tmp_path / "docs").mkdir()
        result = _check_wiki_outputs(tmp_path, set(), AIBackend.CLAUDE)
        assert result.success is False
        assert "docs" in (result.error or "")

    def test_files_created_diffs_against_before_set(self, tmp_path: Path):
        (tmp_path / "llms.txt").write_text("# x")
        (tmp_path / "docs").mkdir()
        old = tmp_path / "docs" / "old.md"
        old.write_text("# old")
        before = {old}

        new_page = tmp_path / "docs" / "architecture.md"
        new_page.write_text("# arch")

        result = _check_wiki_outputs(tmp_path, before, AIBackend.CLAUDE)
        assert result.success is True
        assert new_page in result.files_created
        assert old not in result.files_created
        assert tmp_path / "llms.txt" in result.files_created
