"""Remove skills and AI docs from target projects."""

import shutil
from dataclasses import dataclass, field
from pathlib import Path

from skillnir.tools import AUTO_INJECT_TOOL, TOOLS


@dataclass
class SkillRemovalResult:
    skill_name: str
    removed_symlinks: list[Path] = field(default_factory=list)
    removed_data: bool = False
    cleaned_dirs: list[Path] = field(default_factory=list)
    error: str | None = None


@dataclass
class DocsRemovalResult:
    removed_files: list[Path] = field(default_factory=list)
    cleaned_dirs: list[Path] = field(default_factory=list)
    error: str | None = None


@dataclass
class IgnoreRemovalResult:
    removed_symlinks: list[Path] = field(default_factory=list)
    removed_data: bool = False
    error: str | None = None


def find_skill_installations(project_root: Path, skill_name: str) -> list[Path]:
    """Return paths where a skill is installed across all tool dotdirs."""
    found: list[Path] = []
    for tool in (*TOOLS, AUTO_INJECT_TOOL):
        skill_path = project_root / tool.dotdir / tool.skills_subpath / skill_name
        if skill_path.exists() or skill_path.is_symlink():
            found.append(skill_path)
    return found


def _try_clean_empty_dir(directory: Path) -> bool:
    """Remove directory if it is empty. Returns True if removed."""
    try:
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
            return True
    except OSError:
        pass
    return False


def delete_skill(
    project_root: Path, skill_name: str, delete_data: bool = False
) -> SkillRemovalResult:
    """Delete a skill from a target project.

    1. Remove symlinks/dirs from all tool dotdirs
    2. Clean up empty skills/ directories (NEVER the dotdir itself)
    3. Optionally remove the actual skill data from .data/skills/
    """
    result = SkillRemovalResult(skill_name=skill_name)

    try:
        # Phase 1: Remove from tool dotdirs
        installations = find_skill_installations(project_root, skill_name)
        for path in installations:
            if path.is_symlink():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            result.removed_symlinks.append(path)

        # Phase 2: Clean empty skills/ dirs (never the dotdir itself)
        for tool in (*TOOLS, AUTO_INJECT_TOOL):
            skills_dir = project_root / tool.dotdir / tool.skills_subpath
            if _try_clean_empty_dir(skills_dir):
                result.cleaned_dirs.append(skills_dir)

        # Phase 3: Optionally remove from .data/skills/
        if delete_data:
            data_skill_dir = project_root / ".data" / "skills" / skill_name
            if data_skill_dir.exists():
                shutil.rmtree(data_skill_dir)
                result.removed_data = True

    except OSError as e:
        result.error = str(e)

    return result


def delete_skills(
    project_root: Path, skill_names: list[str], delete_data: bool = False
) -> list[SkillRemovalResult]:
    """Delete multiple skills from a target project."""
    return [delete_skill(project_root, name, delete_data) for name in skill_names]


def find_docs_installations(project_root: Path) -> list[Path]:
    """Return paths of AI doc files that exist in the project.

    Only includes symlinks if they actually point to ../agents.md.
    """
    found: list[Path] = []

    agents_md = project_root / "agents.md"
    if agents_md.exists():
        found.append(agents_md)

    symlink_paths = [
        project_root / ".claude" / "claude.md",
        project_root / ".github" / "copilot-instructions.md",
    ]
    for path in symlink_paths:
        if path.is_symlink():
            target = path.resolve()
            if target == agents_md.resolve():
                found.append(path)

    return found


def delete_docs(project_root: Path) -> DocsRemovalResult:
    """Delete AI docs from a target project.

    1. Remove symlinks (.claude/claude.md, .github/copilot-instructions.md)
       only if they point to ../agents.md
    2. Remove agents.md
    3. Clean up empty .claude/ or .github/ dirs (NEVER if they have content)
    """
    result = DocsRemovalResult()

    try:
        installations = find_docs_installations(project_root)

        # Remove symlinks first, then agents.md
        agents_md = project_root / "agents.md"
        for path in installations:
            if path != agents_md:
                path.unlink()
                result.removed_files.append(path)

        if agents_md in installations:
            agents_md.unlink()
            result.removed_files.append(agents_md)

        # Clean empty parent dirs (never if they still have content)
        for parent_dir in [
            project_root / ".claude",
            project_root / ".github",
        ]:
            if _try_clean_empty_dir(parent_dir):
                result.cleaned_dirs.append(parent_dir)

    except OSError as e:
        result.error = str(e)

    return result


def find_ignore_installations(project_root: Path) -> list[Path]:
    """Return ignore symlinks in the project root that point to .data/ignore/."""
    found: list[Path] = []
    ignore_dir = project_root / ".data" / "ignore"
    seen: set[str] = set()
    for tool in TOOLS:
        if not tool.ignore_file or tool.ignore_file in seen:
            continue
        seen.add(tool.ignore_file)
        path = project_root / tool.ignore_file
        if path.is_symlink():
            try:
                target = path.resolve()
                if ignore_dir in target.parents or target.parent == ignore_dir:
                    found.append(path)
            except OSError:
                found.append(path)
    return found


def delete_ignore(project_root: Path, delete_data: bool = False) -> IgnoreRemovalResult:
    """Delete ignore symlinks from project root.

    1. Remove symlinks that point to .data/ignore/
    2. Optionally remove .data/ignore/ directory
    """
    result = IgnoreRemovalResult()

    try:
        installations = find_ignore_installations(project_root)
        for path in installations:
            path.unlink()
            result.removed_symlinks.append(path)

        if delete_data:
            ignore_dir = project_root / ".data" / "ignore"
            if ignore_dir.exists():
                shutil.rmtree(ignore_dir)
                result.removed_data = True

    except OSError as e:
        result.error = str(e)

    return result
