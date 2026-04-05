# Changelog

All notable changes to Skillnir will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-04-05

### Added

- **AI Benchmarks page** (`/benchmarks`) -- search and compare top 30 AI models across 7 categories (Coding, Reasoning, Math, General Knowledge, Instruction Following, Multimodal, Agentic Tasks) with data from SWE-bench, Artificial Analysis, and Chatbot Arena
  - Sortable columns for all benchmark scores, pricing (input/output per 1M tokens), and context window
  - Provider filter chips (Anthropic, OpenAI, Google, Meta, Mistral, DeepSeek, xAI, Alibaba, Cohere, Amazon)
  - Color-coded scores: green (85+), amber (70-84), orange (50-69), red (<50)
  - Model count selector (Top 20/30/50)
  - Context window display: 1M/10M format instead of 1000K/10000K
- **Security Vulnerabilities page** (`/security`) -- search for critical CVEs, zero-day exploits, and security advisories across 10 categories
  - Categories: Critical CVEs, Zero-Day Exploits, Supply Chain Attacks, Web Security (OWASP), Cloud & Infrastructure, Malware & Ransomware, AI & LLM Security, Data Breaches, Authentication & Identity, Open Source Vulnerabilities
  - Sources: NIST NVD, CISA, GitHub Advisories, Bleeping Computer, Krebs on Security, Hacker News, The Record, Dark Reading
  - Severity color-coding (Critical/High/Medium/Low) with CVSS scores
  - Sortable and filterable table with category and severity chips
- **Prompt Compression** (`compress_prompts` setting) -- rule-based caveman compression that reduces pipeline prompt token usage by 30-50%
  - Pure Python module (`compressor.py`), no external dependencies, <100ms
  - Protected zones: code blocks, inline code, JSON templates, URLs, file paths, markdown headers never modified
  - Removes articles, auxiliaries, intensifiers, filler phrases while preserving negations, numbers, technical terms
  - Toggle in Settings page, integrated into `build_subprocess_command()` for all 6 pipelines
  - 38 unit tests covering compression rules and safety
- **promptCompressor skill** -- installable skill at `.data/skills/promptCompressor/` teaching AI assistants the compression rules and architecture
- **5 new research topics** -- Fine-Tuning & LoRA, AI Agent Frameworks & Tools, Open Source Models, Multimodal AI, AI Infrastructure & MLOps
- **3 new article sources** -- Dev Community (dev.to, hashnode.com), Tech News (TechCrunch, The Verge, VentureBeat), AI Newsletters (The Batch, TLDR AI, The AI Edge)
- **Website URLs** for all 40 AI tools in the registry (`website_url` field on `AITool` dataclass)
- **Local tool icons** -- all 30 tool logos downloaded to `src/skillnir/assets/icons/` and served locally instead of fetching from remote URLs
- **Select All / Deselect All buttons** on Research (topics + sources), Events (countries), Benchmarks (providers), and Security (categories + sources) pages
- **Communication Style section** added to base skill generator prompt -- all future generated skills enforce concise, caveman-style AI responses (no preamble, no filler, lead with answers)

### Changed

- **Tools Registry page** (`/tools`) -- removed Popularity, Performance, and Price columns; added Website column with clickable links
- **Install skill sorting** -- simplified to Default, Alphabetical (A-Z), and Alphabetical (Z-A); removed popularity/performance/price sort modes
- **Tool cards** -- replaced score badges (pop/perf/price) with dotdir path display
- **Research button** -- renamed "Search Latest News" to "Search Latest Articles" across all 9 locales
- **Events landing page** -- date column now color-coded (red=passed, amber=today, default=future) with new "Remaining" column (Passed/Today/Tomorrow/N days)
- **Events subtitle** -- "Next event" now skips past events
- **Claude Code icon** -- changed from remote `claude.ai` URL to local icon file

### Fixed

- **Open Landing Page button** on Research and Events pages -- `_cache_bust_url()` moved to broader scope so it works even on first search when no `index.html` existed at page load
- **Skill library overflow** -- long source paths now truncate with ellipsis and show full path on hover
- **Benchmarks fallback parser** -- extracts model JSON from raw stdout stream when normal text collection fails

## [1.1.2] - 2026-03-31

### Added

- **backendEngineer skill** -- AI-generated skill for Python backend development covering CLI patterns, dataclass conventions, multi-backend abstraction, async streaming, and testing with pytest
  - SKILL.md (236 lines), INJECT.md, references/ (7 files: code-style, patterns, test-patterns, security-checklist, common-issues, ai-interaction-guide, template.py)
  - Sub-agents: code-reviewer, test-writer, dependency-auditor
  - Validation script: `validate-backend.sh`
- **frontendEngineer skill** -- AI-generated skill for frontend/UI development with NiceGUI, Quasar components, and Tailwind CSS patterns
  - SKILL.md (238 lines), INJECT.md, LEARNED.md
- **devopsEngineer skill** -- updated with expanded documentation and process guides
- Symlinks injected for new skills across all tool dotdirs (.claude/, .cursor/, .github/, .agents/, .codex/, .gemini/, .opencode/)
- **CI: Bump Version & Tag** -- manual GitHub Actions workflow to bump version (patch/minor/major), update pyproject.toml, commit, and create git tag on main

### Changed

- Version management moved to CI -- pyproject.toml tracks latest released version, CI bumps it on demand

### Removed

- **pythonDeveloper skill** -- replaced by the more specific backendEngineer skill

## [1.1.1] - 2026-03-30

### Fixed

- **Copilot CLI** -- changed `--quiet` to `--silent` (the correct flag for Copilot CLI 1.0.12+)
- **Copilot CLI** -- prompt now passed via `--prompt <text>` instead of positional `-- <text>` which caused "too many arguments" error
- **Model info tier** -- added `tier` field to `ModelInfo` dataclass (1=powerful, 2=balanced, 3=fast) for model picker categorization
- **Secondary text color** -- replaced `text-gray-400`/`text-gray-500` with theme-adaptive `.text-secondary` CSS class (indigo-600 light / indigo-300 dark)
- **Usage page** -- Claude Subscription Usage section now only shows when Claude is the selected backend
- **Usage tracking** -- subprocess flows (Claude CLI, Cursor, Gemini) now record token usage to session tracker via `_parse_stream_json_line`
- **Model picker redesign** -- clickable cards in 3-tier grid (Powerful/Balanced/Fast) with hover animations, replacing the old flat list with "Select" buttons
- **Version badge** -- now shows backend name alongside version (e.g., "2.1.87 (Claude Code)")
- **Language picker** -- redesigned from dropdown to icon button with menu, matching other header icons
- **Home badges** -- version and prompts badges changed from grey to deep-purple

### Added

- **Claude API usage** -- live subscription usage data from Anthropic OAuth API on the Usage page (5-hour window, 7-day window, Sonnet/Opus breakdown, extra credits)
- **Model card hover animation** -- new `.model-card` CSS class with scale, glow shadow, and tinted background on hover
- **Tech stack** -- added to README.md

## [1.1.0] - 2026-03-29

### Added

- **Events feature** -- search for upcoming AI conferences, meetups, workshops, and hackathons across 12 countries (UK, US, Germany, Netherlands, Poland, Iran, Ukraine, Albania, Canada, Australia, Austria, UAE)
  - New `events` CLI command with `--regenerate` flag and interactive country selection
  - Web UI page at `/events` with country chips, progress panel, and landing page viewer
  - Events landing page with three-filter system: topic, country, and free/paid
  - Individual event detail pages with registration links
  - Per-country AI search pipeline mirroring the research architecture
- **Country flags** -- 12 country flag icons (PNG) displayed in event chips, landing page badges, and filter chips
  - Iran uses the historical Lion and Sun (Shir-o-Khorshid) flag
- **Internationalization (i18n)** -- multi-language support for the web UI and CLI
  - 9 languages: English, German (Deutsch), Dutch (Nederlands), Polish (Polski), Persian (فارسی), Ukrainian (Українська), Albanian (Shqip), French (Français), Arabic (العربية)
  - ~540 translation keys covering all UI pages, navigation, buttons, and messages
  - `t()` translation function with dot-notation keys and English fallback
  - Language picker in header bar and settings page
  - RTL language support flagged for Arabic and Persian
  - Language preference persisted in user config
- **Research article categorization** -- articles organized into topic subdirectories (`articles/{topic}/`) instead of a flat directory, with automatic migration of existing data

### Changed

- Research landing page article links updated to `articles/{topic}/{id}.html` path structure
- Article HTML template back-link updated for new directory depth (`../../index.html`)
- Navigation updated with Events entry in "Tools & Data" group
- Home page updated with Events section card

### Fixed

- Welcome dialog `TimeoutError` when browser connection is slow (increased timeout to 3s with graceful fallback)
- `check-ast` pre-commit hook now excludes `.data/` and skills directories containing template files with non-Python syntax

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

- `chrome-extension` -- Manifest V3, content scripts, service workers, chrome.\* APIs
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

| Command          | Description                                                     |
| ---------------- | --------------------------------------------------------------- |
| `install`        | Sync skills from source + inject symlinks into tool directories |
| `update`         | Sync skills only (version comparison)                           |
| `generate-skill` | Generate domain-specific SKILL.md with AI                       |
| `generate-docs`  | Generate agents.md project documentation with AI                |
| `generate-rule`  | Generate Cursor .mdc rule files with AI                         |
| `check-skill`    | Validate installed skills via AI backend                        |
| `ask`            | Ask AI a read-only question about a project                     |
| `plan`           | Get an AI-generated implementation plan                         |
| `research`       | Search and summarize AI engineering news                        |
| `events`         | Search upcoming AI events and conferences worldwide             |
| `delete-skill`   | Remove skill(s) from a project                                  |
| `delete-docs`    | Remove AI documentation from a project                          |
| `init-skill`     | Create a blank skill scaffold                                   |
| `init-docs`      | Create a blank agents.md template                               |
| `config`         | Manage backend and model settings                               |
| `sound`          | Configure Claude Code sound notification hooks                  |
| `ui`             | Launch the web interface                                        |

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

[1.1.2]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.2
[1.1.1]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.1
[1.1.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.0
[1.0.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.0.0
