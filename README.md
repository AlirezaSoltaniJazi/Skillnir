# Skillnir

[![CI - Tests](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml)
[![CI - Style](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Inject AI coding skills into any tool's dotdir.

## Overview

Skillnir generates, manages, and injects domain-specific AI skills into the configuration directories of multiple AI coding tools. A single skill works across Claude Code, Cursor, GitHub Copilot, Gemini, Codex, Aider, Windsurf, and Cline.

Skills are structured markdown files that teach AI assistants project-specific patterns, conventions, and workflows. Skillnir scans your project, generates skills with AI, and symlinks them into each tool's expected location.

## Features

- **Multi-backend skill generation** -- generate skills using Claude Code, Cursor, Gemini, or GitHub Copilot
- **10 skill scopes** -- backend, frontend, android, ios, infra, testing, js, python, test-design, general-system
- **Cross-tool injection** -- one skill, symlinked into `.claude/`, `.cursor/`, `.github/`, `.gemini/`, `.codex/`, `.agents/`, and more
- **Web UI** -- NiceGUI-based dashboard for all operations
- **CLI** -- full command set for scripting and automation
- **Version-aware sync** -- update skills across projects with version comparison
- **AI doc generation** -- generate `agents.md` with project-specific coding instructions
- **Cursor rule generation** -- generate `.mdc` rule files for Cursor

## Quick Start

### Install

```bash
# Clone the repository
git clone git@github.com:AlirezaSoltaniJazi/Skillnir.git
cd skillnir

# Install with uv
uv sync

# Verify installation
uv run skillnir --help
```

### Generate a skill

```bash
uv run skillnir generate-skill
```

### Install skills into a project

```bash
uv run skillnir install
```

### Launch the web UI

```bash
uv run skillnir ui
```

### Run tests

```bash
uv run pytest
```

### Run style checks

```bash
# All checks at once (via pre-commit)
uv run pre-commit run --all-files

# Individual checks
black --check -S src/ tests/
autoflake --check --remove-all-unused-imports --remove-unused-variables -r src/ tests/
pylint -rn --rcfile=.pylintrc src/skillnir/
bandit -lll -iii -r src/
```

## CLI Commands

| Command          | Description                                                        |
| ---------------- | ------------------------------------------------------------------ |
| `install`        | Sync skills and inject symlinks into AI tool directories (default) |
| `update`         | Sync skills only (version comparison, no symlink changes)          |
| `generate-docs`  | Generate `agents.md` with AI-powered project analysis              |
| `generate-skill` | Generate a domain-specific `SKILL.md` with AI                      |
| `generate-rule`  | Generate Cursor rule files (`.mdc`) with AI                        |
| `check-skill`    | Validate installed skill patterns via AI backend                   |
| `init-skill`     | Create a default skill scaffold with placeholder files             |
| `init-docs`      | Create a default `agents.md` template with tool symlinks           |
| `delete-skill`   | Remove skill(s) from a project                                     |
| `delete-docs`    | Remove AI docs from a project                                      |
| `ask`            | Ask AI a question about a project (read-only)                      |
| `plan`           | Get a detailed implementation plan from AI                         |
| `research`       | Search latest AI engineering news and generate summaries           |
| `config`         | Manage backend and model configuration                             |
| `sound`          | Manage Claude Code sound notification hooks                        |
| `ui`             | Launch the web interface                                           |

## Project Structure

```
skillnir/
├── src/skillnir/       # Core Python package
│   ├── cli.py             # CLI entry point (argparse + questionary)
│   ├── ui.py              # Web UI (NiceGUI)
│   ├── injector.py        # Symlink injection logic
│   ├── syncer.py          # Version-aware skill sync
│   ├── remover.py         # Skill and docs removal
│   ├── skill_generator.py # Multi-backend skill generation
│   ├── generator.py       # AI doc generation
│   ├── hooks.py           # Claude Code hook management
│   ├── skills.py          # Skill discovery and parsing
│   ├── tools.py           # AI tool definitions
│   └── backends.py        # Backend configuration
├── .data/
│   ├── skills/            # Source skill directories
│   └── promptsv1/         # Skill generation prompts
├── .github/
│   ├── workflows/         # CI pipelines
│   └── actions/           # Reusable composite actions
├── tests/                 # pytest test suite
├── pyproject.toml         # Build config (hatchling)
├── uv.lock                # Dependency lock
├── .pre-commit-config.yaml
└── .pylintrc
```

## Skills

Skills are structured markdown directories that teach AI tools your project's patterns:

```
skillName/
├── SKILL.md       # Decision guide (loaded on activation)
├── INJECT.md      # Always-loaded quick reference
├── LEARNED.md     # Session-accumulated corrections and preferences
├── references/    # Detailed documentation and code examples
├── scripts/       # Validation and utility scripts
└── agents/        # Sub-agent definitions
```

### Available Scopes

| Scope          | Description                               |
| -------------- | ----------------------------------------- |
| backend        | Python/Django/Go/Java server-side         |
| frontend       | React/Vue/Angular/Svelte                  |
| android        | Kotlin/Java mobile                        |
| ios            | Swift/Obj-C mobile                        |
| infra          | Docker/CI/Terraform/K8s                   |
| testing        | E2E/API/Integration test automation       |
| js             | JavaScript/TypeScript (Node.js/React/Vue) |
| python         | Python (FastAPI/Flask/scripts/data/CLI)   |
| test-design    | Test strategy, coverage, scenarios        |
| general-system | Cross-cutting skill rules and conventions |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.

## License

[MIT](LICENSE)
