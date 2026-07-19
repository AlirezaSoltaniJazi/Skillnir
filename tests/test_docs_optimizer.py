"""Tests for skillnir.docs_optimizer -- prompt loading + output checks."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend
from skillnir.docs_optimizer import (
    REPORT_FILENAME,
    _check_outputs,
    _is_max_turns_error,
    _max_turns_for,
    _partial_outputs,
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
        assert _snapshot_docs(tmp_path) == {}

    def test_includes_existing_report(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Report\n", encoding="utf-8")
        snap = _snapshot_docs(tmp_path)
        assert report.resolve() in snap


class TestCheckOutputs:
    def test_fails_when_report_missing(self, tmp_path: Path):
        result = _check_outputs(tmp_path, "report", {}, AIBackend.CLAUDE)
        assert result.success is False
        assert REPORT_FILENAME in (result.error or "")

    def test_succeeds_when_report_present(self, tmp_path: Path):
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Report\n", encoding="utf-8")

        result = _check_outputs(tmp_path, "report", {}, AIBackend.CLAUDE)
        assert result.success is True
        assert result.report_path == report
        assert result.mode == "report"
        assert result.backend_used == AIBackend.CLAUDE

    def test_files_touched_diff_against_before_snapshot(self, tmp_path: Path):
        # Pre-existing agents.md
        agents = tmp_path / "agents.md"
        agents.write_text("# A\n", encoding="utf-8")
        before = _snapshot_docs(tmp_path)

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

    def test_files_touched_includes_in_place_edits(self, tmp_path: Path):
        """Apply mode edits files in place — those edits must be reported."""
        agents = tmp_path / "agents.md"
        agents.write_text("# A\n\nStale skill list.\n", encoding="utf-8")
        untouched = tmp_path / "INJECT.md"
        untouched.write_text("# I\n", encoding="utf-8")
        before = _snapshot_docs(tmp_path)

        agents.write_text("# A\n\nSynced skill list with more entries.\n")
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / REPORT_FILENAME).write_text("# Report\n", encoding="utf-8")

        result = _check_outputs(tmp_path, "apply", before, AIBackend.CLAUDE)
        assert result.success is True
        assert agents.resolve() in result.files_touched
        assert untouched.resolve() not in result.files_touched


class TestMaxTurnsForScaling:
    def test_apply_scales_with_doc_count(self):
        # 28 docs * 3 = 84, above the floor.
        assert _max_turns_for("apply", 28) == 84

    def test_report_scales_with_doc_count(self):
        # 28 docs * 2 = 56, above the floor.
        assert _max_turns_for("report", 28) == 56

    def test_apply_floor_for_tiny_projects(self):
        assert _max_turns_for("apply", 2) == 40

    def test_report_floor_for_tiny_projects(self):
        assert _max_turns_for("report", 2) == 20

    def test_apply_budget_exceeds_report_budget(self):
        assert _max_turns_for("apply", 50) > _max_turns_for("report", 50)


class TestIsMaxTurnsError:
    def test_matches_sdk_process_error_text(self):
        assert _is_max_turns_error(
            "Claude Code returned an error result: Reached maximum number of turns (30)"
        )

    def test_matches_case_insensitively(self):
        assert _is_max_turns_error("MAX TURNS exceeded")

    def test_ignores_unrelated_errors(self):
        assert not _is_max_turns_error("connection refused")
        assert not _is_max_turns_error("")


class TestPartialOutputs:
    def test_salvages_report_written_before_limit(self, tmp_path: Path):
        before = _snapshot_docs(tmp_path)
        docs = tmp_path / "docs"
        docs.mkdir()
        report = docs / REPORT_FILENAME
        report.write_text("# Partial report\n", encoding="utf-8")

        result = _partial_outputs(tmp_path, "report", before, AIBackend.CLAUDE, 20)
        assert result.success is True
        assert result.report_path == report
        assert result.warning is not None
        assert "20-turn limit" in result.warning
        assert result.error is None

    def test_salvages_in_place_edits_without_report(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# A\n\nStale.\n", encoding="utf-8")
        before = _snapshot_docs(tmp_path)

        # Apply mode edited a doc but ran out of turns before writing the report.
        agents.write_text("# A\n\nSynced with new entries.\n", encoding="utf-8")

        result = _partial_outputs(tmp_path, "apply", before, AIBackend.CLAUDE, 40)
        assert result.success is True
        assert result.report_path is None  # no report was written
        assert agents.resolve() in result.files_touched
        assert result.warning is not None

    def test_fails_when_nothing_was_produced(self, tmp_path: Path):
        before = _snapshot_docs(tmp_path)
        result = _partial_outputs(tmp_path, "apply", before, AIBackend.CLAUDE, 40)
        assert result.success is False
        assert result.warning is None
        assert "40-turn limit" in (result.error or "")

    def test_stale_report_from_prior_run_does_not_fake_success(self, tmp_path: Path):
        """A leftover report must not count as this run's output."""
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / REPORT_FILENAME).write_text("# Old report\n", encoding="utf-8")
        # Snapshot AFTER the stale report exists — this run then changes nothing.
        before = _snapshot_docs(tmp_path)

        result = _partial_outputs(tmp_path, "report", before, AIBackend.CLAUDE, 20)
        assert result.success is False
        assert result.report_path is None
        assert "20-turn limit" in (result.error or "")
