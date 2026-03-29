"""Sync skills from skillnir source to target project."""

import shutil
from dataclasses import dataclass
from pathlib import Path

from skillnir.skills import parse_frontmatter


@dataclass
class SyncResult:
    skill_name: str
    action: str  # "copied" | "updated" | "skipped"
    source_version: str
    target_version: str | None = None


def get_source_skills_dir() -> Path:
    """Find skillnir's own .data/skills/ directory.

    Walks up from the package location to find .data/skills/.
    Falls back to cwd/.data/skills/ if not found.
    """
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / "skills"
        if candidate.is_dir():
            return candidate
        current = current.parent
    return Path.cwd() / ".data" / "skills"


def _get_skill_version(skill_dir: Path) -> str:
    """Extract version from a skill's SKILL.md frontmatter."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return "unknown"
    meta = parse_frontmatter(skill_md)
    metadata = meta.get("metadata", {}) or {}
    return metadata.get("version", "unknown")


def sync_skill(source_dir: Path, target_dir: Path, skill_name: str) -> SyncResult:
    """Sync a single skill from source to target with version comparison."""
    source_skill_dir = source_dir / skill_name
    target_dir.mkdir(parents=True, exist_ok=True)
    source_version = _get_skill_version(source_skill_dir)

    # Skip if source and target are the same directory to avoid
    # rmtree deleting the only copy before copytree can read it.
    if source_dir.resolve() == target_dir.resolve():
        return SyncResult(
            skill_name=skill_name,
            action="skipped",
            source_version=source_version,
        )
    target_skill_dir = target_dir / skill_name

    if not target_skill_dir.exists():
        shutil.copytree(source_skill_dir, target_skill_dir)
        return SyncResult(
            skill_name=skill_name,
            action="copied",
            source_version=source_version,
        )

    target_version = _get_skill_version(target_skill_dir)
    if source_version == target_version:
        return SyncResult(
            skill_name=skill_name,
            action="skipped",
            source_version=source_version,
            target_version=target_version,
        )

    shutil.rmtree(target_skill_dir)
    shutil.copytree(source_skill_dir, target_skill_dir)
    return SyncResult(
        skill_name=skill_name,
        action="updated",
        source_version=source_version,
        target_version=target_version,
    )


def sync_skills(source_dir: Path, target_dir: Path) -> list[SyncResult]:
    """Sync skills from source to target with version comparison.

    For each skill in source_dir:
    - Missing in target → copy entire directory
    - Same version → skip
    - Different version → remove old + copy new
    """
    if not source_dir.is_dir():
        return []

    # Skip if source and target are the same directory to avoid
    # rmtree deleting the only copy before copytree can read it.
    if source_dir.resolve() == target_dir.resolve():
        return []

    target_dir.mkdir(parents=True, exist_ok=True)
    results: list[SyncResult] = []

    for entry in sorted(source_dir.iterdir()):
        skill_md = entry / "SKILL.md"
        if not entry.is_dir() or not skill_md.exists():
            continue

        skill_name = entry.name
        source_version = _get_skill_version(entry)
        target_skill_dir = target_dir / skill_name

        if not target_skill_dir.exists():
            shutil.copytree(entry, target_skill_dir)
            results.append(
                SyncResult(
                    skill_name=skill_name,
                    action="copied",
                    source_version=source_version,
                )
            )
        else:
            target_version = _get_skill_version(target_skill_dir)
            if source_version == target_version:
                results.append(
                    SyncResult(
                        skill_name=skill_name,
                        action="skipped",
                        source_version=source_version,
                        target_version=target_version,
                    )
                )
            else:
                shutil.rmtree(target_skill_dir)
                shutil.copytree(entry, target_skill_dir)
                results.append(
                    SyncResult(
                        skill_name=skill_name,
                        action="updated",
                        source_version=source_version,
                        target_version=target_version,
                    )
                )

    return results
