"""Tests for skillnir.syncer -- skill syncing with version comparison."""

from pathlib import Path


from skillnir.syncer import (
    _get_skill_version,
    get_source_skills_dir,
    sync_skill,
    sync_skills,
)

SKILL_MD_V1 = """\
---
name: alpha
description: Alpha skill
metadata:
  version: "1.0.0"
---
# Alpha
"""

SKILL_MD_V2 = """\
---
name: alpha
description: Alpha skill updated
metadata:
  version: "2.0.0"
---
# Alpha v2
"""


def _make_skill(parent: Path, name: str, content: str) -> Path:
    """Helper to create a skill directory with SKILL.md."""
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(content, encoding="utf-8")
    return d


class TestGetSkillVersion:
    def test_extracts_version(self, tmp_path: Path):
        _make_skill(tmp_path, "s", SKILL_MD_V1)
        assert _get_skill_version(tmp_path / "s") == "1.0.0"

    def test_returns_unknown_when_no_skill_md(self, tmp_path: Path):
        (tmp_path / "empty").mkdir()
        assert _get_skill_version(tmp_path / "empty") == "unknown"

    def test_returns_unknown_when_no_version_key(self, tmp_path: Path):
        d = tmp_path / "noversion"
        d.mkdir()
        (d / "SKILL.md").write_text("---\nname: noversion\n---\n")
        assert _get_skill_version(d) == "unknown"


class TestSyncSkill:
    def test_copies_when_target_missing(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        _make_skill(source_dir, "alpha", SKILL_MD_V1)

        result = sync_skill(source_dir, target_dir, "alpha")
        assert result.action == "copied"
        assert result.source_version == "1.0.0"
        assert (target_dir / "alpha" / "SKILL.md").exists()

    def test_skips_when_same_version(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        _make_skill(source_dir, "alpha", SKILL_MD_V1)
        _make_skill(target_dir, "alpha", SKILL_MD_V1)

        result = sync_skill(source_dir, target_dir, "alpha")
        assert result.action == "skipped"
        assert result.source_version == "1.0.0"
        assert result.target_version == "1.0.0"

    def test_updates_when_different_version(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        _make_skill(source_dir, "alpha", SKILL_MD_V2)
        _make_skill(target_dir, "alpha", SKILL_MD_V1)

        result = sync_skill(source_dir, target_dir, "alpha")
        assert result.action == "updated"
        assert result.source_version == "2.0.0"
        assert result.target_version == "1.0.0"
        content = (target_dir / "alpha" / "SKILL.md").read_text()
        assert "2.0.0" in content


class TestSyncSkills:
    def test_batch_sync(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        _make_skill(source_dir, "alpha", SKILL_MD_V1)
        _make_skill(source_dir, "beta", SKILL_MD_V2)

        results = sync_skills(source_dir, target_dir)
        assert len(results) == 2
        assert all(r.action == "copied" for r in results)

    def test_skips_non_skill_dirs(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "not-a-skill").mkdir()
        (source_dir / "not-a-skill" / "README.md").write_text("hi")
        target_dir = tmp_path / "target"

        results = sync_skills(source_dir, target_dir)
        assert results == []

    def test_empty_source_dir(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        target_dir = tmp_path / "target"

        assert sync_skills(source_dir, target_dir) == []

    def test_nonexistent_source_dir(self, tmp_path: Path):
        assert sync_skills(tmp_path / "nope", tmp_path / "target") == []

    def test_mixed_actions(self, tmp_path: Path):
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        _make_skill(source_dir, "new-skill", SKILL_MD_V1)
        _make_skill(source_dir, "same-skill", SKILL_MD_V1)
        _make_skill(target_dir, "same-skill", SKILL_MD_V1)
        _make_skill(source_dir, "old-skill", SKILL_MD_V2)
        _make_skill(target_dir, "old-skill", SKILL_MD_V1)

        results = sync_skills(source_dir, target_dir)
        actions = {r.skill_name: r.action for r in results}
        assert actions["new-skill"] == "copied"
        assert actions["same-skill"] == "skipped"
        assert actions["old-skill"] == "updated"


class TestSamePathSafety:
    """Verify that syncing with source == target does not destroy data."""

    def test_sync_skill_skips_when_same_path(self, tmp_path: Path):
        shared_dir = tmp_path / "skills"
        _make_skill(shared_dir, "alpha", SKILL_MD_V1)

        result = sync_skill(shared_dir, shared_dir, "alpha")
        assert result.action == "skipped"
        assert (shared_dir / "alpha" / "SKILL.md").exists()

    def test_sync_skills_returns_empty_when_same_path(self, tmp_path: Path):
        shared_dir = tmp_path / "skills"
        _make_skill(shared_dir, "alpha", SKILL_MD_V1)

        results = sync_skills(shared_dir, shared_dir)
        assert results == []
        assert (shared_dir / "alpha" / "SKILL.md").exists()


class TestGetSourceSkillsDir:
    def test_returns_path(self):
        result = get_source_skills_dir()
        assert isinstance(result, Path)
        assert result.name == "skills"
