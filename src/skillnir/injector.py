"""Core injection logic: create symlinks from tool dotdirs to central skills."""

from dataclasses import dataclass
from pathlib import Path

from skillnir.skills import Skill
from skillnir.tools import AITool, SOURCE_DOTDIR


@dataclass
class InjectionResult:
    tool: AITool
    symlink_path: Path
    created: bool
    error: str | None = None


def inject_skill(
    project_root: Path,
    skill: Skill,
    tools: list[AITool],
) -> list[InjectionResult]:
    results: list[InjectionResult] = []

    for tool in tools:
        tool_skills_dir = project_root / tool.dotdir / tool.skills_subpath
        symlink_path = tool_skills_dir / skill.dir_name

        if symlink_path.exists() or symlink_path.is_symlink():
            results.append(
                InjectionResult(
                    tool=tool,
                    symlink_path=symlink_path,
                    created=False,
                )
            )
            continue

        try:
            tool_skills_dir.mkdir(parents=True, exist_ok=True)
            target = Path("..") / ".." / SOURCE_DOTDIR / "skills" / skill.dir_name
            symlink_path.symlink_to(target)
            results.append(
                InjectionResult(
                    tool=tool,
                    symlink_path=symlink_path,
                    created=True,
                )
            )
        except OSError as e:
            results.append(
                InjectionResult(
                    tool=tool,
                    symlink_path=symlink_path,
                    created=False,
                    error=str(e),
                )
            )

    return results
