# Changelog

All notable changes to Skillnir will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-29

First stable release of Skillnir -- a system for generating, managing, and injecting domain-specific AI skills into the configuration directories of 35+ AI coding tools.

### Core Platform

- **Multi-backend skill generation** using Claude Code, Cursor Agent, Gemini CLI, or GitHub Copilot as the AI engine
- **Symlink-based injection** -- one skill directory, symlinked into every supported tool's dotdir (`.claude/`, `.cursor/`, `.github/`, `.agents/`, etc.)
- **Version-aware synchronization** -- smart sync with copy/update/skip based on semver comparison
- **Interactive CLI** with 15 commands covering the full skill lifecycle
- **NiceGUI web interface** with 13 pages for visual skill management

### Skill Generation (26 Scopes)

Each scope has a dedicated AI prompt with three-phase generation: project scan, synthesis, and best-practice integration.

**Application Development**
- `backend` -- Python/Django/Go/Java server-side patterns
- `frontend` -- React/Vue/Angular/Svelte component patterns
- `android` -- Kotlin/Java with Jetpack Compose, coroutines, KMP
- `ios` -- Swift/SwiftUI/UIKit with structured concurrency
- `js` -- JavaScript/TypeScript full-stack (Node.js, React, Vue, Express)
- `python` -- FastAPI/Flask/scripts/data/CLI with modern Python 3.13+ features
- `go` -- Go idioms, goroutines/channels, modules, table-driven tests
- `cross-platform-mobile` -- React Native, Flutter, KMP shared logic

**Data & APIs**
- `database` -- schema design, migration safety, query optimization, ORM patterns
- `api-design` -- OpenAPI/Protobuf/GraphQL schema design and contract testing
- `data-science` -- Jupyter notebooks, pandas/polars, ML pipelines, experiment tracking

**Testing & Quality**
- `testing` -- generic E2E/API/integration test automation
- `test-design` -- test strategy, coverage analysis, scenario design
- `locator` -- element selector strategies across 5 frameworks
- `playwright` -- fixtures, POM, visual regression, API testing, tracing
- `wdio` -- WebDriverIO config, custom commands, services, BiDi
- `selenium` -- Selenium 4+, Grid, multi-language, PageFactory, Actions API
- `appium` -- Appium 2.0, XCUITest/UiAutomator2, gestures, hybrid apps

**Operations & Security**
- `infra` -- Docker, CI/CD, Terraform, Kubernetes, disaster recovery
- `security` -- cross-platform OWASP/NIST/CIS audit (read-only analysis)
- `observability` -- OpenTelemetry, distributed tracing, SLOs, alerting
- `performance` -- profiling, load testing, bundle analysis, caching

**Specialized**
- `chrome-extension` -- Manifest V3, content scripts, service workers, chrome.* APIs
- `accessibility` -- cross-platform WCAG 2.1 AA compliance audit
- `migration` -- framework upgrades, language migrations, architecture refactors
- `general-system` -- cross-cutting skill system rules and conventions

### AI Tool Support (35 Tools)

Skills inject into the configuration directories of:

- **Anthropic**: Claude Code
- **Anysphere**: Cursor
- **Codeium**: Windsurf
- **GitHub**: GitHub Copilot
- **OpenAI**: Codex CLI
- **Google**: Gemini CLI
- **JetBrains**: Junie AI Agent
- **Sourcegraph**: Amp
- **Amazon AWS**: Kiro
- **ByteDance**: Trae
- And 25 more community and enterprise tools

### Skill File Architecture

Generated skills follow a structured layout:

```
skill-name/
  SKILL.md          -- decision guide (<=300 lines, <3,500 tokens)
  INJECT.md         -- always-loaded quick reference (50-150 tokens)
  LEARNED.md        -- AI-accumulated corrections and preferences
  references/       -- detailed guides and code examples (5+ files)
  agents/           -- sub-agent definitions (up to 4)
  assets/           -- copy-as-is config templates
  scripts/          -- validation scripts
```

### Prompt System

- **Base scaffold** (`_base-skill-generator.md`) defining output structure, quality gates, adaptive interaction protocols, sub-agent delegation, and a 15-step execution order
- **7 adaptive interaction protocol subsections**: interaction modes, correction accumulation, preference elicitation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md
- **Freedom levels** (MUST/SHOULD/CAN) for constraint clarity
- **Progressive disclosure** -- SKILL.md for decisions, references/ for detailed code
- **Priority-numbered best practices** for trade-off ordering in every generator
- **Severity-classified security checklists** (Critical/High/Medium/Low with OWASP mapping)

### CLI Commands

| Command | Description |
| --- | --- |
| `install` | Sync skills from source + inject symlinks into tool directories |
| `update` | Sync skills only (version comparison) |
| `generate-skill` | Generate domain-specific SKILL.md with AI |
| `generate-docs` | Generate agents.md project documentation with AI |
| `generate-rule` | Generate Cursor .mdc rule files with AI |
| `check-skill` | Validate installed skills via AI backend |
| `ask` | Ask AI a read-only question about a project |
| `plan` | Get an AI-generated implementation plan |
| `research` | Search and summarize AI engineering news |
| `delete-skill` | Remove skill(s) from a project |
| `delete-docs` | Remove AI documentation from a project |
| `init-skill` | Create a blank skill scaffold |
| `init-docs` | Create a blank agents.md template |
| `config` | Manage backend and model settings |
| `sound` | Configure Claude Code sound notification hooks |
| `ui` | Launch the web interface |

### Web Interface

NiceGUI-based dashboard with pages for skill generation, installation, deletion, settings, tool browsing, usage tracking, and AI research.

### Install Flow Enhancements

- **Custom source path** -- choose where to fetch skills from during install (defaults to Skillnir's own `.data/skills/`, can point to any directory)
- **Auto-detection** -- tools already present in the project are pre-selected
- **Sort modes** -- sort tools by popularity, performance, price, or alphabetically

### Generate Flow Enhancements

- **"Also add to current project" checkbox** -- when generating a skill for a different project, optionally sync it back to the current project (default: on, hidden when target is the current directory)
- **Live preview** -- skill name previewed in real-time as you type
- **Prompt version selection** -- choose which prompt version to use for generation

### Non-Skill Generators

- `generate-ai-docs.md` -- four-phase generator for `agents.md` with AI-gotcha scanning, LEARNED.md awareness, and security sections
- `generate-rule-general.md` -- Cursor .mdc rule generator with cross-tool equivalents and LEARNED.md integration

### Quality & Consistency

- Unified "self-learning via LEARNED.md" terminology across all generators
- All generators include `ai-interaction-guide.md` in suggested reference files
- Disambiguation notes between `general.md` (skill-authoring guide) and `general-system.md` (meta-skill generator)
- Read-only philosophy for analysis sub-agents (no Edit/Write access)
- Flakiness prevention guidance in all test-writer sub-agents
- WCAG 2.1 AA mapping in Android and iOS accessibility sections
- Rollback strategy and cloud cost awareness in backend generator
- Severity classification in security sections across backend, frontend, and infra generators

[1.0.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.0.0
