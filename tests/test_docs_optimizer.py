"""Tests for skillnir.docs_optimizer -- prompt loading + output checks."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend
from skillnir.docs_optimizer import (
    REPORT_FILENAME,
    _check_outputs,
    _snapshot_docs,
    load_optimize_prompt,
)


class TestLoadOptimizePrompt:
    def test_loads_v1_prompt(self):
        text = load_optimize_prompt("v1")
        assert len(text) > 0
        assert "ai-context-report.md" in text or "AI" in text

    def test_raises_when_missing(self, tmp_path: Path):
        with patch("skillnir.docs_optimizer.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_optimize_prompt("v1")


class TestSnapshotDocs:
    def test_empty_for_empty_project(self, tmp_path: Path):
        assert _snapshot_docs(tmp_path) == set()

    def test_includes_existing_report(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Report\n", encoding="utf-8")
        snap = _snapshot_docs(tmp_path)
        assert report.resolve() in snap


class TestCheckOutputs:
    def test_fails_when_report_missing(self, tmp_path: Path):
        result = _check_outputs(tmp_path, "report", set(), AIBackend.CLAUDE)
        assert result.success is False
        assert REPORT_FILENAME in (result.error or "")

    def test_succeeds_when_report_present(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Report\n", encoding="utf-8")

        result = _check_outputs(tmp_path, "report", set(), AIBackend.CLAUDE)
        assert result.success is True
        assert result.report_path == report
        assert result.mode == "report"
        assert result.backend_used == AIBackend.CLAUDE

    def test_files_touched_diff_against_before_set(self, tmp_path: Path):
        # Pre-existing agents.md
        agents = tmp_path / "agents.md"
        agents.write_text("# A\n", encoding="utf-8")
        before = {agents.resolve()}

        # AI added a new file + the report
        new_file = tmp_path / "INJECT.md"
        new_file.write_text("# I\n", encoding="utf-8")
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Report\n", encoding="utf-8")

        result = _check_outputs(tmp_path, "apply", before, AIBackend.CLAUDE)
        assert result.success is True
        assert new_file.resolve() in result.files_touched
        assert report.resolve() in result.files_touched
        assert agents.resolve() not in result.files_touched
