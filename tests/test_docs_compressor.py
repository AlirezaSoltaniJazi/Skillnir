"""Tests for skillnir.docs_compressor -- discovery + rule-based compression."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.docs_compressor import (
    compress_docs_apply_rule_based,
    compress_docs_dry_run,
    find_ai_docs,
    load_tone_prompt,
)


def _seed_ai_docs(tmp_path: Path) -> None:
    """Create a representative spread of AI docs in tmp_path."""
    (tmp_path / "agents.md").write_text(
        "# Agents\n\nThis is basically a very simple project that essentially "
        "does X.\n",
        encoding="utf-8",
    )
    (tmp_path / "INJECT.md").write_text(
        "# Inject\n\n- The thing is at /usr/bin\n- Run with the flag --verbose\n",
        encoding="utf-8",
    )
    (tmp_path / "llms.txt").write_text(
        "# Project\n\n> The project that simply does X.\n", encoding="utf-8"
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "architecture.md").write_text(
        "# Arch\n\nThe system basically uses a very simple pipeline.\n",
        encoding="utf-8",
    )
    cursor_rules = tmp_path / ".cursor" / "rules"
    cursor_rules.mkdir(parents=True)
    (cursor_rules / "general.mdc").write_text(
        "# Rule\n\nUse the framework that is provided.\n", encoding="utf-8"
    )
    skill = tmp_path / ".data" / "skills" / "mySkill"
    (skill / "references").mkdir(parents=True)
    (skill / "agents").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: my\n---\n# My\n", encoding="utf-8")
    (skill / "INJECT.md").write_text("# My quick ref\n", encoding="utf-8")
    (skill / "LEARNED.md").write_text("# Learned\n\nNothing yet.\n", encoding="utf-8")
    (skill / "references" / "guide.md").write_text(
        "# Guide\n\nThis is the guide.\n", encoding="utf-8"
    )
    (skill / "agents" / "helper.md").write_text("# Helper\n", encoding="utf-8")


class TestFindAIDocs:
    def test_returns_empty_for_empty_project(self, tmp_path: Path):
        assert find_ai_docs(tmp_path) == []

    def test_finds_seeded_docs(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        found = find_ai_docs(tmp_path)
        names = {p.name for p in found}
        assert "agents.md" in names
        assert "INJECT.md" in names
        assert "llms.txt" in names
        assert "architecture.md" in names
        assert "general.mdc" in names
        assert "SKILL.md" in names
        assert "guide.md" in names
        assert "helper.md" in names

    def test_skips_symlinks(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Agents\n", encoding="utf-8")
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "CLAUDE.md").symlink_to(Path("..") / "agents.md")

        found = find_ai_docs(tmp_path)
        names = {p.name for p in found}
        # agents.md is the canonical; the symlink under .claude is skipped
        assert "agents.md" in names
        # The symlinked .claude/CLAUDE.md must NOT appear as a separate entry
        symlink_paths = [p for p in found if p.is_symlink()]
        assert symlink_paths == []

    def test_returns_sorted_paths(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        found = find_ai_docs(tmp_path)
        assert found == sorted(found)

    def test_dedupes_case_insensitive_fs(self, tmp_path: Path):
        """On case-insensitive filesystems (macOS APFS, Windows NTFS), the
        ``agents.md`` and ``AGENTS.md`` glob entries both reach the same
        file. ``find_ai_docs`` must dedupe by inode so we don't process
        and rewrite the same file twice.
        """
        (tmp_path / "agents.md").write_text("# A\n", encoding="utf-8")
        # Probe the filesystem: if uppercase reaches the same file, the
        # bug condition exists and we can assert against it.
        if not (tmp_path / "AGENTS.md").is_file():
            pytest.skip("filesystem is case-sensitive; this bug doesn't apply")

        found = find_ai_docs(tmp_path)
        agents_entries = [p for p in found if p.name.lower() == "agents.md"]
        assert len(agents_entries) == 1


class TestCompressDocsDryRun:
    def test_writes_nothing(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        before = (tmp_path / "agents.md").read_text()
        result = compress_docs_dry_run(tmp_path)
        assert (tmp_path / "agents.md").read_text() == before
        # All reports should have written=False
        assert all(not r.written for r in result.files)

    def test_reports_per_file_reduction(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        result = compress_docs_dry_run(tmp_path)
        # agents.md has fillers ("basically", "very", "essentially") so it
        # must shrink. Find its report and check reduction > 0.
        agents = next(r for r in result.files if r.path.name == "agents.md")
        assert agents.original_chars > agents.compressed_chars
        assert agents.reduction_pct > 0

    def test_aggregates_totals(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        result = compress_docs_dry_run(tmp_path)
        assert result.total_original_chars == sum(
            r.original_chars for r in result.files if r.error is None
        )
        assert result.total_compressed_chars == sum(
            r.compressed_chars for r in result.files if r.error is None
        )
        assert 0.0 <= result.total_reduction_pct <= 100.0
        assert result.applied is False


class TestCompressDocsApplyRuleBased:
    def test_writes_compressed_content_in_place(self, tmp_path: Path):
        _seed_ai_docs(tmp_path)
        original = (tmp_path / "agents.md").read_text()
        result = compress_docs_apply_rule_based(tmp_path)
        new = (tmp_path / "agents.md").read_text()
        assert new != original
        assert len(new) < len(original)
        assert all(r.written for r in result.files if r.error is None)
        assert result.applied is True

    def test_no_files_no_writes(self, tmp_path: Path):
        result = compress_docs_apply_rule_based(tmp_path)
        assert result.files == []
        assert result.applied is True

    def test_handles_unreadable_file_gracefully(self, tmp_path: Path):
        # Create a binary "agents.md" that can't be decoded as UTF-8
        (tmp_path / "agents.md").write_bytes(b"\xff\xfe\x00\x01garbage")
        result = compress_docs_apply_rule_based(tmp_path)
        # File still listed, just with an error and no write
        agents = next(r for r in result.files if r.path.name == "agents.md")
        assert agents.error is not None
        assert agents.written is False


class TestLoadTonePrompt:
    def test_loads_v1_prompt(self):
        text = load_tone_prompt("v1")
        assert "Tone" in text or "tone" in text
        assert len(text) > 0

    def test_raises_when_missing(self, tmp_path: Path):
        with patch("skillnir.docs_compressor.get_prompts_dir", return_value=tmp_path):
            with pytest.raises(FileNotFoundError):
                load_tone_prompt("v1")
