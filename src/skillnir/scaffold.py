"""Scaffold default skill and AI docs templates."""

import re
from dataclasses import dataclass, field
from pathlib import Path

# Default ignore templates directory (ships with the package)
_TEMPLATES_DIR = (
    Path(__file__).resolve().parent.parent.parent / ".data" / "ignore" / "templates"
)

# Template descriptions for UI and CLI display
IGNORE_TEMPLATES: dict[str, str] = {
    "python": "Python — __pycache__, .venv, dist, *.pyc, uv.lock",
    "java": "Java — target/, build/, .gradle/, .m2/, *.class",
    "javascript": "JavaScript/TypeScript — node_modules/, dist/, lock files",
    "go": "Go — vendor/, bin/, go.sum",
    "rust": "Rust — target/, Cargo.lock, .cargo/",
    "c-cpp": "C/C++ — build/, cmake-build-*/, *.o, *.so",
    "ruby": "Ruby — vendor/bundle/, .bundle/, Gemfile.lock",
    "php": "PHP — vendor/, composer.lock",
    "swift-ios": "Swift/iOS — DerivedData/, Pods/, .build/",
    "csharp-dotnet": "C#/.NET — bin/, obj/, packages/, .artifacts/",
    "ci-cd": "CI/CD — .github/workflows/, .gitlab-ci.yml, Jenkinsfile",
    "docker": "Docker — .docker/, docker/volumes/",
    "data-ml": "Data/ML — *.csv, *.h5, *.pkl, model weights, wandb/",
    "secrets": "Secrets — .env, *.key, *.pem, credentials.json",
    "ide": "IDE — .idea/, .vscode/, *.iml, .eclipse/",
    "docs-assets": "Docs/Assets — *.png, *.jpg, *.pdf, *.svg, fonts",
    "logs": "Logs — *.log, logs/, crash_reports/, *.dmp",
}

SKILL_MD_TEMPLATE = """\
---
name: {skill_name}
description: >-
  TODO: Describe WHAT this skill does and WHEN to use it (1-1024 chars).
  Example: "Django REST Framework backend patterns for the Acme platform.
  Covers models, serializers, views, services, and tests."
compatibility: "TODO: Python 3.13+, Django 5.x, etc."
metadata:
  author: your-team
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash Glob Grep
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. No code blocks >5 lines.
     Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

## When to Use

<!-- TODO: 4-6 trigger conditions for when this skill should activate. -->

## Do NOT Use

<!-- TODO: Cross-references to sibling skills (frontend, mobile, infra, etc.). -->

## Code Generation Rules

1. **Explain before generating** when the code involves unfamiliar patterns or security-sensitive logic
2. **Generate directly** when the pattern has been explained this session or the task is boilerplate
3. **Always include** inline comments for non-obvious logic (why, not what)
4. **On correction** — acknowledge the mistake, restate as a rule, apply to ALL subsequent outputs, then **write the correction to [LEARNED.md](LEARNED.md)** under `## Corrections` with today's date
5. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE targeted question, apply consistently, then **write the preference to [LEARNED.md](LEARNED.md)** under `## Preferences`

## Architecture

<!-- TODO: Describe the project's architecture patterns, key directories, data flow.
     Link to references/ for detailed guides. -->

## Key Patterns

<!-- TODO: Summary table (pattern name, approach, key rule). No code blocks here.
     Full code examples go in references/. -->

## Code Style

<!-- TODO: Rules table (naming, formatting, imports). Details in references/code-style.md. -->

## Testing

<!-- TODO: Testing rules and conventions. Full examples in references/test-patterns.md. -->

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:
- Corrections -> `## Corrections` section
- Preferences -> `## Preferences` section
- Discovered conventions -> `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

<!-- Remove this section if this skill doesn't need sub-agents.
     If sub-agents are used, add Agent to allowed-tools in frontmatter. -->

| Agent | Role | Spawn When |
|-------|------|------------|
<!-- | [code-reviewer](agents/code-reviewer.md) | Read-only code analysis | PR review, code audit | -->

### Delegation Rules
1. Delegate when task has distinct phases or needs security isolation
2. Stay inline for simple, single-focus tasks
3. Cap at 3-4 sub-agents per workflow
4. Pass ALL context explicitly — sub-agents don't see parent conversation
5. Sub-agents CANNOT spawn their own sub-agents (max depth = 1)

## References

| File | Description |
|------|-------------|
| [LEARNED.md](LEARNED.md) | **Auto-updated.** Corrections, preferences, conventions across sessions |

<!-- TODO: Add references/ files:
     - [architecture-guide](references/architecture-guide.md)
     - [code-style](references/code-style.md)
     - [common-issues](references/common-issues.md) -->
"""

INJECT_MD_TEMPLATE = """\
# {skill_name} — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: TODO: language + framework + key libs
- **Entry points**: TODO: main files/dirs
- **Key directories**: TODO: annotated 3-5 dirs
- **Patterns**: TODO: 3-5 bullet pattern summary
- **Never**: TODO: 2-3 critical anti-patterns
- **Sub-agents**: TODO: list agents or "none" — see [agents/](agents/) for delegation rules
- **Self-learning**: On correction -> write to LEARNED.md. On ambiguity -> check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for examples
"""

LEARNED_MD_TEMPLATE = """\
# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries — they accumulate over time.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

<!-- AI writes here when user corrects generated code -->

## Preferences

<!-- AI writes here when user states a preference -->

## Discovered Conventions

<!-- AI writes here when it discovers implicit project conventions through code analysis -->
"""

REFERENCES_GITKEEP_COMMENT = """\
# references/
# Put supplemental documentation here that agents load on demand.
# Examples: architecture-guide.md, testing-patterns.md, model-template.py
# These files are NOT loaded by default — only when referenced from SKILL.md.
"""

SCRIPTS_GITKEEP_COMMENT = """\
# scripts/
# Put executable scripts here that agents can run.
# Examples: validate-structure.sh, run-checks.py
# Agents execute these scripts — they are NOT loaded into context.
"""

ASSETS_GITKEEP_COMMENT = """\
# assets/
# Put static resources here: config templates, boilerplate, images, schemas.
# Examples: env-example, docker-compose-template.yml
# These are copy-as-is resources, not loaded into context by default.
"""

AGENTS_DIR_GITKEEP_COMMENT = """\
# agents/
# Sub-agent definition files for delegation workflows.
# Each .md file defines one sub-agent: role, tools, spawn conditions, context template.
# Skip this directory if the skill doesn't need sub-agent delegation.
"""

AGENTS_MD_TEMPLATE = """\
# {project_name}

<!-- This is the AI context document — the single source of truth for all
     AI coding assistants (Claude Code, Cursor, Copilot, Gemini CLI, etc.).
     Symlinks in .claude/ and .github/ point back to this file. -->

## What This Is

<!-- Brief description of the project: what it does, who uses it. -->

## Stack

<!-- Language, framework, package manager, build system, database, etc.
     Example:
     - **Language**: Python 3.13+
     - **Framework**: Django 5.x + DRF
     - **Package manager**: uv
     - **Database**: PostgreSQL 17 -->

## Project Structure

<!-- Annotated directory tree of the most important directories.
     Example:
     ```
     src/
     ├── api/          # REST API endpoints
     ├── models/       # Database models
     ├── services/     # Business logic
     └── tests/        # Test suite
     ``` -->

## How To Run

<!-- Commands to install, run, and test the project.
     ```bash
     # Install
     uv sync

     # Run
     uv run python manage.py runserver

     # Test
     uv run pytest
     ``` -->

## Development Conventions

<!-- Code style, naming conventions, import order, error handling patterns. -->

## Architecture Rules

<!-- Key architectural decisions and patterns that AI assistants must follow. -->

## Files To Know

<!-- Quick reference table of the most important files.
     | File | Purpose |
     |------|---------|
     | src/api/views.py | REST API endpoints |
     | src/models/user.py | User model | -->

## Known Gotchas

<!-- Things that are easy to get wrong or that surprise newcomers. -->
"""


@dataclass
class ScaffoldResult:
    success: bool
    created_path: Path | None = None
    created_files: list[Path] = field(default_factory=list)
    error: str | None = None


def validate_skill_name(name: str) -> str | None:
    """Validate a skill name against the spec.

    Returns None if valid, or an error message string if invalid.
    """
    if not name:
        return "Skill name cannot be empty."
    if len(name) > 64:
        return "Skill name must be 64 characters or fewer."
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        return (
            "Skill name must be lowercase letters, digits, and hyphens only. "
            "No leading, trailing, or consecutive hyphens."
        )
    return None


def init_skill(project_root: Path, skill_name: str) -> ScaffoldResult:
    """Create a default skill scaffold at .data/skills/{skill_name}/."""
    error = validate_skill_name(skill_name)
    if error:
        return ScaffoldResult(success=False, error=error)

    skill_dir = project_root / ".data" / "skills" / skill_name
    if skill_dir.exists():
        return ScaffoldResult(
            success=False,
            error=f"Skill directory already exists: {skill_dir}",
        )

    created_files: list[Path] = []

    try:
        skill_dir.mkdir(parents=True, exist_ok=True)

        # SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            SKILL_MD_TEMPLATE.format(skill_name=skill_name), encoding="utf-8"
        )
        created_files.append(skill_md)

        # INJECT.md
        inject_md = skill_dir / "INJECT.md"
        inject_md.write_text(
            INJECT_MD_TEMPLATE.format(skill_name=skill_name), encoding="utf-8"
        )
        created_files.append(inject_md)

        # LEARNED.md
        learned_md = skill_dir / "LEARNED.md"
        learned_md.write_text(LEARNED_MD_TEMPLATE, encoding="utf-8")
        created_files.append(learned_md)

        # Subdirectories with .gitkeep
        for subdir, comment in [
            ("references", REFERENCES_GITKEEP_COMMENT),
            ("scripts", SCRIPTS_GITKEEP_COMMENT),
            ("assets", ASSETS_GITKEEP_COMMENT),
            ("agents", AGENTS_DIR_GITKEEP_COMMENT),
        ]:
            sub_path = skill_dir / subdir
            sub_path.mkdir(exist_ok=True)
            gitkeep = sub_path / ".gitkeep"
            gitkeep.write_text(comment, encoding="utf-8")
            created_files.append(gitkeep)

    except OSError as e:
        return ScaffoldResult(success=False, error=str(e))

    return ScaffoldResult(
        success=True, created_path=skill_dir, created_files=created_files
    )


def init_docs(project_root: Path) -> ScaffoldResult:
    """Create a default AI docs template (agents.md + symlinks)."""
    agents_md = project_root / "agents.md"
    if agents_md.exists():
        return ScaffoldResult(
            success=False,
            error=f"agents.md already exists: {agents_md}",
        )

    project_name = project_root.name
    created_files: list[Path] = []

    try:
        # Write agents.md
        agents_md.write_text(
            AGENTS_MD_TEMPLATE.format(project_name=project_name), encoding="utf-8"
        )
        created_files.append(agents_md)

        # Create .claude/claude.md symlink
        claude_dir = project_root / ".claude"
        claude_dir.mkdir(parents=True, exist_ok=True)
        claude_md = claude_dir / "claude.md"
        if not claude_md.exists():
            claude_md.symlink_to(Path("..") / "agents.md")
            created_files.append(claude_md)

        # Create .github/copilot-instructions.md symlink
        github_dir = project_root / ".github"
        github_dir.mkdir(parents=True, exist_ok=True)
        copilot_md = github_dir / "copilot-instructions.md"
        if not copilot_md.exists():
            copilot_md.symlink_to(Path("..") / "agents.md")
            created_files.append(copilot_md)

    except OSError as e:
        return ScaffoldResult(success=False, error=str(e))

    return ScaffoldResult(
        success=True, created_path=agents_md, created_files=created_files
    )


def get_ignore_templates(
    templates_dir: Path | None = None,
) -> dict[str, str]:
    """Return available template names mapped to their descriptions.

    Only returns templates whose .txt files exist on disk.
    """
    tdir = templates_dir or _TEMPLATES_DIR
    available: dict[str, str] = {}
    for name, desc in IGNORE_TEMPLATES.items():
        if (tdir / f"{name}.txt").is_file():
            available[name] = desc
    return available


def assemble_ignore(
    selected_templates: list[str],
    templates_dir: Path | None = None,
) -> str:
    """Assemble ignore content from common.txt + selected templates."""
    tdir = templates_dir or _TEMPLATES_DIR
    parts: list[str] = []

    # Always include common
    common_path = tdir / "common.txt"
    if common_path.is_file():
        parts.append(common_path.read_text(encoding="utf-8").strip())

    for name in selected_templates:
        tpl_path = tdir / f"{name}.txt"
        if tpl_path.is_file():
            parts.append(tpl_path.read_text(encoding="utf-8").strip())

    return "\n\n".join(parts) + "\n"


def init_ignore(
    project_root: Path,
    selected_templates: list[str],
    ignore_files: list[str],
    templates_dir: Path | None = None,
) -> ScaffoldResult:
    """Create .data/ignore/ with assembled ignore files for each tool.

    Args:
        project_root: Target project root directory.
        selected_templates: Template names to include (e.g. ["python", "secrets"]).
        ignore_files: Ignore file names to create (e.g. [".claudeignore", ".cursorignore"]).
        templates_dir: Override templates directory (for testing).

    Returns:
        ScaffoldResult with created file paths.
    """
    ignore_dir = project_root / ".data" / "ignore"
    created_files: list[Path] = []

    try:
        ignore_dir.mkdir(parents=True, exist_ok=True)

        content = assemble_ignore(selected_templates, templates_dir)

        # Deduplicate ignore file names (e.g. Gemini CLI and Antigravity share .geminiignore)
        seen: set[str] = set()
        for ignore_file in ignore_files:
            if not ignore_file or ignore_file in seen:
                continue
            seen.add(ignore_file)

            dest = ignore_dir / ignore_file
            dest.write_text(content, encoding="utf-8")
            created_files.append(dest)

    except OSError as e:
        return ScaffoldResult(success=False, error=str(e))

    return ScaffoldResult(
        success=True, created_path=ignore_dir, created_files=created_files
    )
