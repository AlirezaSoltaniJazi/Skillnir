"""Tests for skillnir.remover -- skill and docs deletion."""

from pathlib import Path

from skillnir.remover import (
    delete_docs,
    delete_skill,
    delete_skills,
    delete_wiki,
    find_docs_installations,
    find_skill_installations,
    find_wiki_installations,
)


def _setup_skill(tmp_path: Path, skill_name: str = "test-skill") -> None:
    """Create a skill in .data/skills/ and symlinks in a couple of tool dotdirs."""
    # Create actual skill data
    data_dir = tmp_path / ".data" / "skills" / skill_name
    data_dir.mkdir(parents=True)
    (data_dir / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")

    # Create symlinks in tool dotdirs
    for dotdir in (".claude", ".agents"):
        skills_dir = tmp_path / dotdir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        symlink = skills_dir / skill_name
        symlink.symlink_to(Path("..") / ".." / ".data" / "skills" / skill_name)


class TestFindSkillInstallations:
    def test_finds_symlinks(self, tmp_path: Path):
        _setup_skill(tmp_path)
        found = find_skill_installations(tmp_path, "test-skill")
        assert len(found) >= 2
        names = {p.parent.parent.name for p in found}
        assert ".claude" in names or ".agents" in names

    def test_finds_real_directories(self, tmp_path: Path):
        real_dir = tmp_path / ".cursor" / "skills" / "my-skill"
        real_dir.mkdir(parents=True)
        found = find_skill_installations(tmp_path, "my-skill")
        assert any(str(p).endswith("my-skill") for p in found)

    def test_returns_empty_when_not_installed(self, tmp_path: Path):
        found = find_skill_installations(tmp_path, "nonexistent")
        assert found == []


class TestDeleteSkill:
    def test_default_preserves_data(self, tmp_path: Path):
        _setup_skill(tmp_path)
        result = delete_skill(tmp_path, "test-skill")

        assert result.error is None
        assert result.removed_data is False
        assert len(result.removed_symlinks) >= 2
        # Symlinks removed
        assert not (tmp_path / ".claude" / "skills" / "test-skill").exists()
        assert not (tmp_path / ".agents" / "skills" / "test-skill").exists()
        # Data preserved
        assert (tmp_path / ".data" / "skills" / "test-skill").exists()

    def test_delete_data_removes_data(self, tmp_path: Path):
        _setup_skill(tmp_path)
        result = delete_skill(tmp_path, "test-skill", delete_data=True)

        assert result.error is None
        assert result.removed_data is True
        assert len(result.removed_symlinks) >= 2
        assert not (tmp_path / ".data" / "skills" / "test-skill").exists()
        assert not (tmp_path / ".claude" / "skills" / "test-skill").exists()
        assert not (tmp_path / ".agents" / "skills" / "test-skill").exists()

    def test_cleans_empty_skills_dir(self, tmp_path: Path):
        _setup_skill(tmp_path)
        result = delete_skill(tmp_path, "test-skill")

        # skills/ dirs should be cleaned up since they are now empty
        assert not (tmp_path / ".claude" / "skills").exists()
        assert not (tmp_path / ".agents" / "skills").exists()
        assert len(result.cleaned_dirs) >= 2

    def test_does_not_delete_dotdir(self, tmp_path: Path):
        _setup_skill(tmp_path)
        # Add another file to .claude/ so the dotdir is not empty
        (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
        delete_skill(tmp_path, "test-skill")

        # .claude/ should still exist (has settings.json)
        assert (tmp_path / ".claude").is_dir()
        assert (tmp_path / ".claude" / "settings.json").exists()

    def test_does_not_delete_skills_dir_with_other_skills(self, tmp_path: Path):
        _setup_skill(tmp_path, "skill-a")
        _setup_skill(tmp_path, "skill-b")
        delete_skill(tmp_path, "skill-a")

        # skills/ dir should still exist because skill-b is still there
        assert (tmp_path / ".claude" / "skills" / "skill-b").exists()

    def test_handles_missing_data_dir(self, tmp_path: Path):
        # Skill has symlinks but no .data/skills/ entry
        skills_dir = tmp_path / ".claude" / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        (skills_dir / "orphan-skill").mkdir()

        result = delete_skill(tmp_path, "orphan-skill")
        assert result.error is None
        assert result.removed_data is False

    def test_removes_real_directory_not_just_symlinks(self, tmp_path: Path):
        # Create a real directory (not symlink) in a tool dotdir
        real_dir = tmp_path / ".cursor" / "skills" / "copied-skill"
        real_dir.mkdir(parents=True)
        (real_dir / "SKILL.md").write_text("test", encoding="utf-8")

        data_dir = tmp_path / ".data" / "skills" / "copied-skill"
        data_dir.mkdir(parents=True)
        (data_dir / "SKILL.md").write_text("test", encoding="utf-8")

        result = delete_skill(tmp_path, "copied-skill", delete_data=True)
        assert not real_dir.exists()
        assert not data_dir.exists()


class TestDeleteSkills:
    def test_batch_deletion_preserves_data_by_default(self, tmp_path: Path):
        _setup_skill(tmp_path, "skill-a")
        _setup_skill(tmp_path, "skill-b")
        results = delete_skills(tmp_path, ["skill-a", "skill-b"])

        assert len(results) == 2
        assert all(not r.removed_data for r in results)
        assert (tmp_path / ".data" / "skills" / "skill-a").exists()
        assert (tmp_path / ".data" / "skills" / "skill-b").exists()

    def test_batch_deletion_with_delete_data(self, tmp_path: Path):
        _setup_skill(tmp_path, "skill-a")
        _setup_skill(tmp_path, "skill-b")
        results = delete_skills(tmp_path, ["skill-a", "skill-b"], delete_data=True)

        assert len(results) == 2
        assert all(r.removed_data for r in results)


class TestFindDocsInstallations:
    def test_finds_agents_md(self, tmp_path: Path):
        (tmp_path / "agents.md").write_text("# Test", encoding="utf-8")
        found = find_docs_installations(tmp_path)
        assert any(p.name == "agents.md" for p in found)

    def test_finds_symlinks_to_agents_md(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Test", encoding="utf-8")

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "claude.md").symlink_to(Path("..") / "agents.md")

        found = find_docs_installations(tmp_path)
        assert len(found) == 2

    def test_skips_non_symlink_claude_md(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Test", encoding="utf-8")

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        # Real file, not a symlink
        (claude_dir / "claude.md").write_text("# Custom", encoding="utf-8")

        found = find_docs_installations(tmp_path)
        assert len(found) == 1  # Only agents.md

    def test_returns_empty_when_no_docs(self, tmp_path: Path):
        found = find_docs_installations(tmp_path)
        assert found == []


class TestDeleteDocs:
    def test_removes_agents_md_and_symlinks(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Test", encoding="utf-8")

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "claude.md").symlink_to(Path("..") / "agents.md")

        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").symlink_to(Path("..") / "agents.md")

        result = delete_docs(tmp_path)
        assert result.error is None
        assert len(result.removed_files) == 3
        assert not agents.exists()
        assert not (claude_dir / "claude.md").exists()
        assert not (github_dir / "copilot-instructions.md").exists()

    def test_cleans_empty_dirs(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Test", encoding="utf-8")

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        (claude_dir / "claude.md").symlink_to(Path("..") / "agents.md")

        result = delete_docs(tmp_path)
        assert not claude_dir.exists()
        assert claude_dir in result.cleaned_dirs

    def test_does_not_delete_non_empty_dirs(self, tmp_path: Path):
        agents = tmp_path / "agents.md"
        agents.write_text("# Test", encoding="utf-8")

        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        (github_dir / "copilot-instructions.md").symlink_to(Path("..") / "agents.md")
        # Add workflow file so .github/ is not empty
        workflows = github_dir / "workflows"
        workflows.mkdir()
        (workflows / "ci.yml").write_text("name: CI", encoding="utf-8")

        result = delete_docs(tmp_path)
        assert github_dir.is_dir()  # Still exists
        assert (workflows / "ci.yml").exists()  # Workflow untouched
        assert github_dir not in result.cleaned_dirs

    def test_handles_no_docs(self, tmp_path: Path):
        result = delete_docs(tmp_path)
        assert result.error is None
        assert result.removed_files == []


# ── Wiki removal ─────────────────────────────────────────────


def _setup_wiki(tmp_path: Path) -> None:
    """Create a llms.txt + canonical docs/ pages."""
    (tmp_path / "llms.txt").write_text("# project\n", encoding="utf-8")
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in (
        "architecture.md",
        "modules.md",
        "dataflow.md",
        "extending.md",
        "getting-started.md",
        "troubleshooting.md",
    ):
        (docs / name).write_text(f"# {name}\n", encoding="utf-8")


class TestFindWikiInstallations:
    def test_finds_llms_and_canonical_docs(self, tmp_path: Path):
        _setup_wiki(tmp_path)
        found = find_wiki_installations(tmp_path)
        names = {p.name for p in found}
        assert "llms.txt" in names
        assert "architecture.md" in names
        assert "troubleshooting.md" in names

    def test_ignores_unrelated_docs_files(self, tmp_path: Path):
        (tmp_path / "llms.txt").write_text("# x")
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "user-guide.md").write_text("# user guide")
        found = find_wiki_installations(tmp_path)
        # Only llms.txt — user-guide.md is not part of the canonical wiki
        assert {p.name for p in found} == {"llms.txt"}

    def test_returns_empty_when_no_wiki(self, tmp_path: Path):
        assert find_wiki_installations(tmp_path) == []


class TestDeleteWiki:
    def test_removes_llms_and_docs(self, tmp_path: Path):
        _setup_wiki(tmp_path)
        result = delete_wiki(tmp_path)
        assert result.error is None
        assert len(result.removed_files) == 7  # llms.txt + 6 canonical pages
        assert not (tmp_path / "llms.txt").exists()
        assert not (tmp_path / "docs" / "architecture.md").exists()

    def test_cleans_empty_docs_dir(self, tmp_path: Path):
        _setup_wiki(tmp_path)
        result = delete_wiki(tmp_path)
        assert tmp_path / "docs" in result.cleaned_dirs
        assert not (tmp_path / "docs").exists()

    def test_preserves_docs_dir_with_other_content(self, tmp_path: Path):
        _setup_wiki(tmp_path)
        (tmp_path / "docs" / "user-guide.md").write_text("# user")
        result = delete_wiki(tmp_path)
        assert tmp_path / "docs" not in result.cleaned_dirs
        assert (tmp_path / "docs").exists()
        assert (tmp_path / "docs" / "user-guide.md").exists()

    def test_handles_no_wiki(self, tmp_path: Path):
        result = delete_wiki(tmp_path)
        assert result.error is None
        assert result.removed_files == []
