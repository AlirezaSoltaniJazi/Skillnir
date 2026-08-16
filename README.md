# Skillnir

[![CI - Tests](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/run-tests.yml)
[![CI - Style](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml/badge.svg)](https://github.com/AlirezaSoltaniJazi/Skillnir/actions/workflows/check-style.yml)
[![Python 3.14+](https://img.shields.io/badge/python-3.14%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Inject AI coding skills into any tool's dotdir.

## Overview

Skillnir generates, manages, and injects domain-specific AI skills into the configuration directories of multiple AI coding tools. A single skill works across Claude Code, Cursor, GitHub Copilot, Gemini, Codex, Windsurf, and Cline.

Skills are structured markdown files that teach AI assistants project-specific patterns, conventions, and workflows. Skillnir scans your project, generates skills with AI, and symlinks them into each tool's expected location.

## Tech Stack

| Component      | Technology                                                                                                             |
| -------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Language       | Python 3.14+                                                                                                           |
| Build          | hatchling + uv (package manager)                                                                                       |
| CLI            | argparse + questionary (interactive)                                                                                   |
| Web UI         | NiceGUI 3.10+ (Quasar/Vue-based Python web framework)                                                                  |
| AI Generation  | claude-agent-sdk + subprocess (Claude, Cursor, Gemini, Copilot)                                                        |
| i18n           | Custom module, 9 languages (EN, DE, NL, PL, FA, UK, SQ, FR, AR), RTL support                                           |
| Config Parsing | PyYAML (SKILL.md frontmatter)                                                                                          |
| Testing        | pytest + pytest-asyncio                                                                                                |
| Linting        | Black (-S), Pylint, Autoflake, Bandit, Prettier                                                                        |
| Pre-commit     | 12 hooks (whitespace, EOF, YAML, large-files, AST, merge-conflict, safety, bandit, autoflake, pylint, black, prettier) |

## Features

- **Multi-backend skill generation** -- generate skills using Claude Code, Cursor, Gemini, or GitHub Copilot
- **37 skill scopes** -- backend, frontend, android, ios, infra, testing, js, python, test-design, general-system, and more
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
- **Package vulnerabilities** -- track known-vulnerable dependencies across 10 package ecosystems (npm, PyPI, Maven, Go, and more) with affected/fixed version ranges
- **Prompt compression** -- rule-based 30-50% token reduction for pipeline prompts
- **Multi-provider notifications** -- webhook alerts to Google Chat, Slack, Discord, Teams, Telegram, Zoho Cliq when tasks complete
- **Ignore file management** -- scaffold and inject tool-specific ignore files (.claudeignore, .cursorignore, etc.)
- **Multi-language UI** -- 9 languages (English, German, Dutch, Polish, Persian, Ukrainian, Albanian, French, Arabic) with RTL support

## Quick Start

### Install

```bash
# Clone the repository
git clone git@github.com:AlirezaSoltaniJazi/Skillnir.git skillnir
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

| Command             | Description                                                                                          |
| ------------------- | ---------------------------------------------------------------------------------------------------- |
| `install`           | Sync skills and inject symlinks into AI tool directories (default)                                   |
| `install-ignore`    | Install ignore files into AI tool directories                                                        |
| `update`            | Sync skills only (version comparison, no symlink changes)                                            |
| `generate-docs`     | Generate `agents.md` with AI-powered project analysis                                                |
| `generate-skill`    | Generate a domain-specific `SKILL.md` with AI                                                        |
| `generate-rule`     | Generate Cursor rule files (`.mdc`) with AI                                                          |
| `generate-wiki`     | Generate project wiki (`llms.txt` + `docs/`) with AI                                                 |
| `compress-docs`     | Rule-based + AI tone compression of all AI-related docs                                              |
| `optimize-docs`     | Audit and (optionally) fix AI-doc inconsistencies + cross-refs                                       |
| `check-skill`       | Validate installed skill patterns via AI backend                                                     |
| `init-skill`        | Create a default skill scaffold with placeholder files                                               |
| `init-docs`         | Create a default `agents.md` template with tool symlinks                                             |
| `delete-skill`      | Remove skill(s) from a project                                                                       |
| `delete-docs`       | Remove AI docs from a project                                                                        |
| `delete-wiki`       | Remove project wiki (`llms.txt` + `docs/`) from a project                                            |
| `ask`               | Ask AI a question about a project (read-only)                                                        |
| `plan`              | Get a detailed implementation plan from AI                                                           |
| `research`          | Search latest AI engineering news and generate summaries                                             |
| `harness-research`  | Search latest AI agent / LLM harness-engineering articles and generate a landing page                |
| `testing-research`  | Search latest testing/QA news (manual, automation, AI-in-testing, perf, a11y)                        |
| `software-research` | Search latest software-engineering / architecture / craft articles and generate a landing page       |
| `cleanup-articles`  | AI-classify outdated research articles and move them to `outdated/` (report or apply, never deletes) |
| `package-vulns`     | Search package advisory DBs for vulnerable dependencies across ecosystems                            |
| `events`            | Search upcoming AI events and conferences worldwide                                                  |
| `news`              | Search fresh AI news headlines by category and recency                                               |
| `config`            | Manage backend and model configuration                                                               |
| `sound`             | Manage Claude Code sound notification hooks                                                          |
| `ui`                | Launch the web interface                                                                             |

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
│   ├── tools.py              # AI tool definitions (37 tools)
│   ├── usage.py              # Token usage tracking
│   ├── locales/              # Translation files (en, de, nl, pl, fa, uk, sq, fr, ar)
│   ├── ui/                   # NiceGUI web interface
│   └── resources/            # HTML templates and static assets
├── scripts/               # CI runner scripts (run_intel.py)
├── .data/
│   ├── skills/               # Source skill directories
│   ├── promptsv1/            # Skill generation prompts (44 templates)
│   ├── research/             # Research articles (organized by topic)
│   └── events/               # AI events data
├── tests/                    # pytest test suite (29 test files)
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

### Available Scopes (37)

| Category                | Scopes                                                                                                                         |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| Engineering Roles       | backend, frontend, js, python, django, go, android, android-google, ios, cross-platform-mobile, chrome-extension, data-science |
| Quality & Testing       | testing, test-design, manual-tester, locator, playwright, wdio, selenium, appium, accessibility, automation-review             |
| Architecture & Platform | infra, devops-engineer, database, api-design, migration, performance, observability, security, general-system                  |
| Design                  | ui-ux-designer                                                                                                                 |
| Business & People       | project-manager, financial-manager, hr-manager, deep-researcher, translator                                                    |

## CI / GitHub Actions Usage

Skillnir can be used as a library in CI pipelines via `scripts/run_intel.py` — a non-interactive runner that calls the async Python API directly (avoids the interactive CLI which would hang in CI).

### Quick Start (GitHub Actions)

```yaml
- name: Checkout Skillnir
  uses: actions/checkout@v6
  with:
    repository: AlirezaSoltaniJazi/Skillnir
    ref: main
    path: skillnir

- name: Install uv + Python + Skillnir
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv python install 3.14
    cd skillnir && uv venv --python 3.14 .venv
    . .venv/bin/activate && uv pip install -e .

- name: Install Cursor CLI
  run: curl https://cursor.com/install -fsSL | bash

- name: Run research pipeline
  env:
    AI_AGENT_TOOL: cursor
    AI_AGENT_API_KEY: ${{ secrets.AI_AGENT_API_KEY }}
    AI_AGENT_WEBHOOK_URL: ${{ secrets.AI_AGENT_WEBHOOK_URL }}
    AI_AGENT_MODEL: auto
  run: |
    cd skillnir && . .venv/bin/activate
    python scripts/run_intel.py research
```

### Supported Features

```bash
python scripts/run_intel.py research          # AI news articles
python scripts/run_intel.py harness-research  # AI agent / LLM harness-engineering articles
python scripts/run_intel.py testing-research  # Testing/QA news
python scripts/run_intel.py software-research # Software-engineering / architecture articles
python scripts/run_intel.py events            # AI conferences & meetups
python scripts/run_intel.py security          # CVEs & advisories
python scripts/run_intel.py package-vulns     # Vulnerable package advisories
python scripts/run_intel.py benchmarks        # AI model leaderboards
python scripts/run_intel.py news              # Fresh AI news headlines
```

### Environment Variables

| Variable                                | Required | Default                                 | Description                                                                   |
| --------------------------------------- | -------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| `AI_AGENT_API_KEY`                      | Yes      | —                                       | API key for the AI tool (e.g. Cursor API key)                                 |
| `AI_AGENT_TOOL`                         | No       | `cursor`                                | Which AI backend to use                                                       |
| `AI_AGENT_WEBHOOK_URL`                  | No       | —                                       | Google Chat webhook for notifications. Omit to skip                           |
| `AI_AGENT_MODEL`                        | No       | `auto`                                  | Primary model name                                                            |
| `AI_AGENT_MODEL_FALLBACK`               | No       | —                                       | Fallback model on primary failure                                             |
| `AI_AGENT_RESEARCH_DATE_RANGE`          | No       | —                                       | Date filter for research (e.g. `published after 2026-01-01`)                  |
| `AI_AGENT_RESEARCH_TOPICS`              | No       | all                                     | Comma-separated topic keys                                                    |
| `AI_AGENT_HARNESS_RESEARCH_TOPICS`      | No       | all                                     | Comma-separated harness-research topic keys                                   |
| `AI_AGENT_HARNESS_RESEARCH_DATE_RANGE`  | No       | —                                       | Date filter for harness-research                                              |
| `AI_AGENT_TESTING_RESEARCH_TOPICS`      | No       | all                                     | Comma-separated testing-research topic keys                                   |
| `AI_AGENT_TESTING_RESEARCH_DATE_RANGE`  | No       | —                                       | Date filter for testing-research                                              |
| `AI_AGENT_SOFTWARE_RESEARCH_TOPICS`     | No       | all                                     | Comma-separated software-research topic keys                                  |
| `AI_AGENT_SOFTWARE_RESEARCH_DATE_RANGE` | No       | —                                       | Date filter for software-research                                             |
| `AI_AGENT_EVENT_COUNTRIES`              | No       | all                                     | Comma-separated country codes (e.g. `uk,de`)                                  |
| `AI_AGENT_SECURITY_CATEGORIES`          | No       | all                                     | Comma-separated category keys                                                 |
| `AI_AGENT_PACKAGE_VULNS_ECOSYSTEMS`     | No       | all                                     | Comma-separated ecosystem keys (e.g. `npm,pypi,maven`)                        |
| `AI_AGENT_BENCHMARK_TOP_N`              | No       | `10`                                    | Number of top models to fetch                                                 |
| `AI_AGENT_NEWS_CATEGORIES`              | No       | all                                     | Comma-separated news category keys                                            |
| `AI_AGENT_NEWS_RECENCY`                 | No       | `7d`                                    | One of `24h`, `48h`, `7d`                                                     |
| `AI_AGENT_NOTIFY_CHUNK_SIZE`            | No       | `15`                                    | Items per Google Chat card (chunked to avoid 32KB limit)                      |
| `AI_AGENT_NOTIFY_BUTTON_TEXT`           | No       | `View source`                           | Label for the per-item link button                                            |
| `AI_AGENT_NOTIFY_SUBTITLE`              | No       | `{feature} — {count} new item(s)`       | Card header subtitle template. Placeholders: `{feature}`, `{count}`, `{part}` |
| `AI_AGENT_NOTIFY_OVERFLOW_TEXT`         | No       | `+{count} more — see workflow artifact` | Overflow footer text. Placeholder: `{count}`                                  |
| `AI_AGENT_NOTIFY_DESC_MAX`              | No       | `150`                                   | Max characters for item descriptions (truncated with `...`)                   |

### Notifications

When `AI_AGENT_WEBHOOK_URL` is set, the runner sends a single consolidated Google Chat card listing all new items discovered in the run. Each item includes title, description, and a clickable link button. Dedup is automatic via on-disk index files — running the same feature twice produces zero duplicate notifications. Card text (subtitle, button label, overflow message, description length) is customizable via the `AI_AGENT_NOTIFY_*` env vars above.

### Output

The final stdout line is a machine-readable JSON summary:

```
SUMMARY {"feature":"research","tool_used":"cursor","new_count":5,"notified":true,"model_used":"auto","fallback_used":false,...}
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, code style, and PR guidelines.

## License

[MIT](LICENSE)
