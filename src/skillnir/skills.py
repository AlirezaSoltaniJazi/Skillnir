"""Skill discovery from .data/skills/ directory."""

from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class Skill:
    name: str
    description: str
    version: str
    path: Path

    @property
    def dir_name(self) -> str:
        """The actual directory name on disk (used for filesystem operations)."""
        return self.path.name


def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3:end]) or {}


def discover_skills(project_root: Path) -> list[Skill]:
    skills_dir = project_root / ".data" / "skills"
    if not skills_dir.is_dir():
        return []
    results = []
    for entry in sorted(skills_dir.iterdir()):
        skill_md = entry / "SKILL.md"
        if entry.is_dir() and skill_md.exists():
            meta = parse_frontmatter(skill_md)
            metadata = meta.get("metadata", {}) or {}
            results.append(
                Skill(
                    name=meta.get("name", entry.name),
                    description=meta.get("description", ""),
                    version=metadata.get("version", "unknown"),
                    path=entry,
                )
            )
    return results
