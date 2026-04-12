# Skillnir

[![CI - Tests](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml)
[![CI - Style](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Inject AI coding skills into any tool's dotdir.

## Overview

Skillnir generates, manages, and injects domain-specific AI skills into the configuration directories of multiple AI coding tools. A single skill works across Claude Code, Cursor, GitHub Copilot, Gemini, Codex, Aider, Windsurf, and Cline.

Skills are structured markdown files that teach AI assistants project-specific patterns, conventions, and workflows. Skillnir scans your project, generates skills with AI, and symlinks them into each tool's expected location.

## Tech Stack

| Component      | Technology                                                                                                             |
| -------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Language       | Python 3.14+                                                                                                           |
| Build          | hatchling + uv (package manager)                                                                                       |
| CLI            | argparse + questionary (interactive)                                                                                   |
| Web UI         | NiceGUI 2.0+ (Quasar/Vue-based Python web framework)                                                                   |
| AI Generation  | claude-agent-sdk + subprocess (Claude, Cursor, Gemini, Copilot)                                                        |
| i18n           | Custom module, 9 languages (EN, DE, NL, PL, FA, UK, SQ, FR, AR), RTL support                                           |
| Config Parsing | PyYAML (SKILL.md frontmatter)                                                                                          |
| Testing        | pytest + pytest-asyncio                                                                                                |
| Linting        | Black (-S), Pylint, Autoflake, Bandit, Prettier                                                                        |
| Pre-commit     | 12 hooks (whitespace, EOF, YAML, large-files, AST, merge-conflict, safety, bandit, autoflake, pylint, black, prettier) |

## Features

- **Multi-backend skill generation** -- generate skills using Claude Code, Cursor, Gemini, or GitHub Copilot
- **26 skill scopes** -- backend, frontend, android, ios, infra, testing, js, python, test-design, general-system, and more
- **Cross-tool injection** -- one skill, symlinked into `.claude/`, `.cursor/`, `.github/`, `.gemini/`, `.codex/`, `.agents/`, and more
- **Web UI** -- NiceGUI-based dashboard for all operations
- **CLI** -- full command set for scripting and automation
- **Version-aware sync** -- update skills across projects with version comparison
- **AI doc generation** -- generate `agents.md` with project-specific coding instructions
- **Cursor rule generation** -- generate `.mdc` rule files for Cursor
- **AI research** -- search and summarize AI engineering news, organized by topic
- **AI events** -- search upcoming AI conferences, meetups, and workshops across 12 countries with country flags and free/paid filtering
- **AI benchmarks** -- compare top AI models across 7 benchmark categories with pricing and context windows
- **Security vulnerabilities** -- search CVEs, zero-days, and advisories across 10 categories and 8 sources
- **Prompt compression** -- rule-based 30-50% token reduction for pipeline prompts
- **Multi-provider notifications** -- webhook alerts to Google Chat, Slack, Discord, Teams, Telegram, Zoho Cliq when tasks complete
- **Ignore file management** -- scaffold and inject tool-specific ignore files (.claudeignore, .cursorignore, etc.)
- **Multi-language UI** -- 9 languages (English, German, Dutch, Polish, Persian, Ukrainian, Albanian, French, Arabic) with RTL support

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
| `install-ignore` | Install ignore files into AI tool directories                      |
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
| `events`         | Search upcoming AI events and conferences worldwide                |
| `config`         | Manage backend and model configuration                             |
| `sound`          | Manage Claude Code sound notification hooks                        |
| `ui`             | Launch the web interface                                           |

## Project Structure

```
skillnir/
├── src/skillnir/          # Core Python package
│   ├── cli.py                # CLI entry point (argparse + questionary)
│   ├── backends.py           # Backend configuration
│   ├── benchmarks.py         # AI model benchmarks search pipeline
│   ├── compressor.py         # Rule-based prompt compression
│   ├── crypto.py             # Fernet encryption for credential storage
│   ├── events.py             # AI events search pipeline
│   ├── generator.py          # AI doc generation
│   ├── hooks.py              # Claude Code hook management
│   ├── i18n.py               # Internationalization (9 languages)
│   ├── injector.py           # Symlink injection logic
│   ├── notifications/        # Multi-provider webhook package
│   ├── researcher.py         # AI news research and summarization
│   ├── remover.py            # Skill and docs removal
│   ├── security.py           # Security vulnerability search pipeline
│   ├── skill_generator.py    # Multi-backend skill generation
│   ├── skills.py             # Skill discovery and parsing
│   ├── syncer.py             # Version-aware skill sync
│   ├── tools.py              # AI tool definitions (38 tools)
│   ├── usage.py              # Token usage tracking
│   ├── locales/              # Translation files (en, de, nl, pl, fa, uk, sq, fr, ar)
│   ├── ui/                   # NiceGUI web interface
│   └── resources/            # HTML templates and static assets
├── scripts/               # CI runner scripts (run_intel.py)
├── .data/
│   ├── skills/               # Source skill directories
│   ├── promptsv1/            # Skill generation prompts (32 templates)
│   ├── research/             # Research articles (organized by topic)
│   └── events/               # AI events data
├── tests/                    # pytest test suite (18 test files)
├── pyproject.toml            # Build config (hatchling)
└── .pre-commit-config.yaml
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

### Available Scopes (26)

| Category                | Scopes                                                                 |
| ----------------------- | ---------------------------------------------------------------------- |
| Application Development | backend, frontend, android, ios, js, python, go, cross-platform-mobile |
| Data & APIs             | database, api-design, data-science                                     |
| Testing & Quality       | testing, test-design, locator, playwright, wdio, selenium, appium      |
| Operations & Security   | infra, security, observability, performance                            |
| Specialized             | chrome-extension, accessibility, migration, general-system             |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.

## License

[MIT](LICENSE)
