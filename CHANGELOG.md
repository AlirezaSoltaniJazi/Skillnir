# Changelog

All notable changes to Skillnir will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-04-26

### Added

- **`testing-research` CLI command + `/testing-research` UI page** -- sibling of the existing `research` (AI-engineering) feature, scoped to **testing & QA** content. New module [src/skillnir/testing_researcher.py](src/skillnir/testing_researcher.py) clones the research pipeline (per-topic AI search, dedup by article ID, markdown + HTML article pages, filterable landing page, Google Chat/Slack/Discord/Teams/Telegram/Cliq notification cards via the existing `send_gchat_intel_report`). 16 topics: test-automation, manual-testing, ai-in-testing, performance, API/contract, mobile, accessibility, security, visual-regression, test-data-management, chaos-engineering, testops-cicd, BDD/TDD, quality-engineering, test-reporting, qa-conferences. 35-domain source allowlist (Ministry of Testing, DevelopSense, Satisfice, BrowserStack, Sauce Labs, Playwright/Cypress/WebdriverIO/Selenium docs, Mabl, Applitools, k6, etc.) grouped into 10 source filters. CI runner ([scripts/run_intel.py](scripts/run_intel.py)) gains `testing-research` dispatch + `AI_AGENT_TESTING_RESEARCH_TOPICS` / `AI_AGENT_TESTING_RESEARCH_DATE_RANGE` env vars. Storage at `.data/testing-research/`, served at `/testing-research-files/index.html`.
- **New skill scope `manual-tester`** -- generates an ISTQB-grounded manual testing skill (test case design, boundary value analysis, equivalence partitioning, decision tables, state transition, exploratory charters, defect reports). Scope catalog is now 27 entries. New prompt template at [.data/promptsv1/generate-skill-manual-tester.md](.data/promptsv1/generate-skill-manual-tester.md) covers Phase 1-8 with required reference files, asset templates, anti-patterns, and ISTQB technique tables.
- **Pure / generic skill mode** -- `generate-skill` now accepts a `pure: bool` flag (CLI prompt + UI checkbox). When enabled, the AI skips the project-scan phases and produces a generic, reusable skill grounded only in the system-prompt's best-practice patterns. Useful for building a skill library that's not tied to one codebase. Output still lands under `.data/skills/{name}/` so the user can install it into any project.
- **`compress-docs` CLI command + `/compress-docs` UI page** -- finds canonical AI-related docs across a target project (`agents.md`, `INJECT.md`, `llms.txt`, `docs/*.md`, `.cursor/rules/*.mdc`, `.data/skills/*/SKILL.md`, `INJECT.md`, `LEARNED.md`, `references/*.md`, etc.), runs the existing rule-based `compress_prompt()` on each, and optionally chains an AI tone-tightening pass through Claude. Symlinks skipped so canonical files are only rewritten once. Dry-run by default; explicit Apply step rewrites in place.
- **`optimize-docs` CLI command + `/optimize-docs` UI page** -- AI-driven audit of all AI-context docs in a project. Two modes: `report` (default, dry-run) writes `docs/ai-context-report.md` with findings (skill list drift, frontmatter issues, token-budget violations, missing cross-references, contradictions); `apply` mode also fixes inconsistencies in place via `Edit` (smallest possible diffs, never wholesale-rewrites generated files).
- **`docs_compressor.py` module** -- new `find_ai_docs()`, `compress_docs_dry_run()`, `compress_docs_apply()` (with optional AI tone pass via SDK / subprocess).
- **`docs_optimizer.py` module** -- mirrors the dual SDK / subprocess pattern of `wiki_generator.py`. `OptimizeDocsResult` dataclass tracks mode, report path, and files touched.
- **Two new prompt templates** -- `.data/promptsv1/compress-docs-tone.md` (tone tightener with strict preservation rules for code, frontmatter, and tables) and `.data/promptsv1/optimize-docs.md` (full audit + fix recipe).
- **`generate-wiki` CLI command + `/generate-wiki` UI page** -- scans a target project with the configured AI backend and emits an `llms.txt` index at the project root plus a `docs/` folder with 6 focused pages (architecture, modules, dataflow, extending, getting-started, troubleshooting). Token-efficient entry point for AI agents -- saves 5k-50k tokens per session compared to broad codebase crawling. Sibling to `generate-docs` and `generate-rule`. Mirrors the same dual-path execution (Claude SDK + subprocess fallback for Cursor/Gemini/Copilot).
- **`delete-wiki` CLI command + `/delete-wiki` UI page** -- removes `llms.txt` and the canonical `docs/*.md` pages produced by `generate-wiki`. Preserves any user-authored docs under `docs/` (only deletes the 6 canonical pages by name, then cleans the directory if empty).
- **Claude Opus 4.7 (`claude-opus-4-7`)** -- added as the new default tier-1 Claude model. Mirrored across Cursor and Copilot backends (both expose Claude models).
- **Claude Opus 4.5 and Opus 4.1** -- added to the active legacy model list.
- **Reasoning effort control** (Claude SDK only) -- new `effort` config field with `low | medium | high | max` levels. Persisted in `~/.skillnir/config.json`. Selectable from the Settings page; current value shown in the header backend chip. Default `high` (omitted from SDK calls so models that don't support effort don't error).
- **Thinking mode control** (Claude SDK only) -- new `thinking_mode` config field with `adaptive | disabled` options. Persisted in `~/.skillnir/config.json`. Selectable from the Settings page; current value shown in the header backend chip. Default `adaptive` (recommended for Opus 4.6/4.7 and Sonnet 4.6; required for Opus 4.7 since `budget_tokens` is removed there).
- **`--effort` flag passed to Claude subprocess** -- `build_subprocess_command()` now appends `--effort <level>` to Claude CLI invocations when the user has customized the value.
- **`build_claude_sdk_kwargs()` helper** in `backends.py` -- single source of truth for translating user config to `ClaudeAgentOptions` kwargs (effort + thinking). Used by all 4 SDK call sites (`generator`, `rule_generator`, `skill_generator`, `wiki_generator`).

### Changed

- **Manual-tester skill prompt enriched** ([.data/promptsv1/generate-skill-manual-tester.md](.data/promptsv1/generate-skill-manual-tester.md)) -- new "PHASE 2.5: ADDITIONAL CRAFT" section grounded in current web sources: ISTQB CTFL **v4.0** (May 2024 redesign, 6 chapters, 1135-min curriculum), Session-Based Test Management (SBTM 5-phase / 60-120 min sessions / 20-30 % time allocation rule), Bach + Bolton heuristic oracles (FEW HICCUPPS, SFDIPOT, CRUSSPIC STMPL), RIMGEA defect-report heuristic, AI-in-QA 2026 trends (GenAI test generation, autonomous QA, self-healing locators, visual validation AI, observability-driven quality, test orchestration over automation), WCAG 2.2 manual testing matrix (NVDA/JAWS/VoiceOver/TalkBack + ADA Title II April 24 2026 deadline), real-device cloud strategy (BrowserStack/Sauce Labs/LambdaTest/AWS Device Farm/Perfecto/Kobiton), test-data management (synthetic data, masking, GDPR/HIPAA), shift-left + shift-right in manual context, documentation modernization (mind maps, screen recording, AI-summarized session notes). Sources cited at the bottom of the prompt.
- **Default Claude model bumped from `sonnet` (4.6) to `opus` (4.7)** -- defaults users to the most capable model.
- **Cleaned up Claude model list** -- switched dated suffix IDs to clean aliases where supported by the API (`claude-haiku-4-5` instead of `claude-haiku-4-5-20251001`, `claude-opus-4-0` instead of `claude-opus-4-0-20250514`, `claude-sonnet-4-5` instead of `claude-sonnet-4-5-20251001`, etc.).

### Removed

- **Retired Claude models pruned from the model list**:
  - `claude-3-opus-20240229` (retired Jan 5, 2026)
  - `claude-3-5-sonnet-20241022` (retired Oct 28, 2025)
  - `claude-3-5-haiku-20241022` (retired Feb 19, 2026)
  - `claude-3-haiku-20240307` (deprecated, retires Apr 19, 2026)

## [1.3.7] - 2026-04-12

### Added

- **`scripts/test_cards.py`** -- local test script to preview Google Chat card layouts without running AI pipelines. Reads existing index data from `.data/` and sends sample cards to `AI_AGENT_WEBHOOK_URL`. Supports per-feature testing (`python scripts/test_cards.py 3 research`) and item count override. Useful for iterating on card formatting without burning Cursor API credits.
- **Enriched card metadata for all features**:
  - Research: title prefixed with `[topic - published_date]`
  - Events: description prefixed with `[date - country - topic - Free/Paid]`
  - Security: description prefixed with `[SEVERITY - CVSS]`
  - Benchmarks: `[CODING]` tag + score + pricing + context window; per-item "View source" buttons replaced with single footer row of leaderboard links (Chatbot Arena, Artificial Analysis, SWE-bench); subtitle shows "benchmarks sorted by coding"
- **`footer_urls` parameter on `send_gchat_intel_report()`** -- optional list of `(label, url)` button pairs shown once on the last chunk. Used by benchmarks to display shared leaderboard sources instead of repeating per-item buttons.

## [1.3.6] - 2026-04-12

### Added

- **Customizable Google Chat notification cards** -- card text elements are now configurable via environment variables in CI. New env vars: `AI_AGENT_NOTIFY_BUTTON_TEXT` (button label, default `"View source"`), `AI_AGENT_NOTIFY_SUBTITLE` (header subtitle template with `{feature}`, `{count}`, `{part}` placeholders), `AI_AGENT_NOTIFY_OVERFLOW_TEXT` (overflow footer with `{count}` placeholder), and `AI_AGENT_NOTIFY_DESC_MAX` (max description character length, default `150`). All params are keyword-only with backward-compatible defaults on `send_gchat_intel_report()`. Header title ("Skillnir") remains hardcoded.

## [1.3.5] - 2026-04-12

### Fixed

- **`--sandbox disabled --force` moved to global Cursor command builder** -- previously these flags were only injected in `researcher.py`, so security, events, and benchmarks pipelines still had Cursor's network sandbox active and web tool calls were auto-rejected as `"User Rejected"`. Moved to `backends.py:build_subprocess_command()` so every Cursor invocation gets web access. Removed the now-redundant override from `researcher.py`.

## [1.3.4] - 2026-04-12

### Added

- **Chunked Google Chat notifications** -- `send_gchat_intel_report()` now splits items into chunks (default 15 per card) and sends them as separate messages with a 2-second delay between each. Avoids the 32KB Google Chat card limit that caused "View source" buttons to disappear when sending 100+ items in a single card. Each chunk header shows the part number (e.g. "research — 40 new item(s) (2/3)"). Chunk size is configurable via `AI_AGENT_NOTIFY_CHUNK_SIZE` env var in CI.

## [1.3.3] - 2026-04-12

### Fixed

- **Cursor agent rejects web tools in headless mode** -- `--sandbox disabled` only controls OS-level sandboxing; web tool calls (`webSearchRequestQuery`, `webFetchRequestQuery`) still require interactive user approval and are auto-rejected as `"User Rejected"` in `--print` mode. The research pipeline now also injects `--force` into the Cursor subprocess command to auto-approve all tool calls in headless mode.

## [1.3.2] - 2026-04-12

### Added

- **`date_range` parameter for research** -- `research()` now accepts an optional `date_range` string (e.g. `"published after 2026-01-01"`, `"published in the last 1 month"`, `"published in 2025"`). Injected into the AI prompt replacing the hardcoded "2025-2026 preferred" hint. When provided, the prompt adds "— strictly exclude older articles" to enforce the window. `None` preserves the previous default behavior. Driven from CI via `AI_AGENT_RESEARCH_DATE_RANGE` env var in `run_intel.py`.
- **Time range selector in research UI** -- new chip row on the research page with 8 options: All time (default), Last 1/3/6/12 months, 2026, 2025, 2024. Selection is passed as `date_range` to `research()`.
- **`notifier.send_gchat_intel_report()`** -- sends a single consolidated Google Chat cards-v2 message listing multiple intel items. Each item rendered with title, description, and a "View source" `buttonList` widget, separated by dividers. Includes overflow footer when items are truncated. Falls back to plain-text card on HTTP 4xx.
- **CI / GitHub Actions documentation** in README -- quick-start YAML snippet, full env var table, notification behavior, and output format.

### Fixed

- **Cursor sandbox blocks web access in research pipeline** -- the Cursor `agent` CLI runs with network sandbox enabled by default, which blocks all outbound HTTP (web search, fetch, curl). The research pipeline now injects `--sandbox disabled` into the Cursor subprocess command so the agent can perform live web searches. Only affects the research pipeline; other Skillnir features keep the sandbox on. Claude backend was unaffected (uses `--allowedTools` with `WebFetch,WebSearch` instead).

### Changed

- **Default `--notify-limit` raised from 10 to 100** in `scripts/run_intel.py` -- all new items now included in the notification card by default instead of truncating at 10.
- **Consolidated single-message notifications** -- `run_intel.py` now sends ONE Google Chat card listing all new items (via `send_gchat_intel_report`) instead of one card per item (via `send_gchat_item`).

## [1.3.1] - 2026-04-12

### Added

- **`scripts/run_intel.py` — CI runner for all four intel pipelines** (`research`, `events`, `security`, `benchmarks`). Non-interactive entry point for GitHub Actions. All customization is done via environment variables — no Skillnir code changes needed to adjust filters or behavior:
  - `AI_AGENT_TOOL` (default `cursor`) + `AI_AGENT_API_KEY` — tool-agnostic; the runner translates these into the backend's native env var (e.g. `CURSOR_API_KEY`). New tools are a one-line addition to the `_TOOL_REGISTRY` table.
  - `AI_AGENT_MODEL` / `AI_AGENT_MODEL_FALLBACK` — primary model with automatic fallback retry on failure.
  - `AI_AGENT_EVENT_COUNTRIES` — comma-separated country filter for events (e.g. `uk,de`). Empty = all.
  - `AI_AGENT_RESEARCH_TOPICS` — comma-separated topic filter for research. Empty = all.
  - `AI_AGENT_SECURITY_CATEGORIES` — comma-separated category filter for security. Empty = all.
  - `AI_AGENT_BENCHMARK_TOP_N` (default `10`) — how many top models to fetch for benchmarks.

## [1.3.0] - 2026-04-12

### Added

- **`scripts/run_intel.py`** -- non-interactive CI runner for the `research`, `events`, and `security` pipelines. Invokes the async Python API directly (avoids the interactive `skillnir` CLI, which uses `questionary` prompts and would hang in CI). Diffs the on-disk `<feature>-index.json` before and after the run to determine which items are new, then POSTs each one as a Google Chat card via `send_gchat_item`. Tool-agnostic: reads `AI_AGENT_TOOL` (default `cursor`) and `AI_AGENT_API_KEY` and translates them into the env var the underlying CLI expects (e.g. `CURSOR_API_KEY`). Currently only `cursor` is wired up; the `_TOOL_REGISTRY` table at the top of the script is the single place to add new tools as Skillnir gains support for them. Also reads `AI_AGENT_WEBHOOK_URL`, `AI_AGENT_MODEL`, `AI_AGENT_MODEL_FALLBACK`. Includes fallback-model retry logic: if the primary model fails, the runner retries once with `AI_AGENT_MODEL_FALLBACK` before giving up. Final stdout line is a machine-readable `SUMMARY {...}` JSON object (feature, tool used, pre/post counts, new count, notified, failures, model used, fallback used) so surrounding workflows can parse it. Intended for GitHub Actions.
- **`notifier.send_gchat_item()`** -- sends a single intel item (title + description + reference URL) as a Google Chat cards-v2 message with a clickable "View source" button (`buttonList` widget with `openLink`). If the primary POST returns HTTP 4xx (malformed card / unsupported widget on the target space), automatically retries with a plain-text fallback card where the URL is inlined as bare text (Google Chat auto-links). 5xx errors and network errors are NOT retried with the fallback — retrying with a different payload can't fix server-side or connection problems. Reuses `is_valid_gchat_webhook()` validation and the shared `_post_json()` helper. Exported from both `skillnir.notifications` and the back-compat `skillnir.notifier` shim.
- **Multi-provider webhook notifications** -- receive a message in your team chat when long-running tasks complete. Six providers supported: **Google Chat, Slack, Discord, Microsoft Teams (Power Automate), Telegram, Zoho Cliq**.
  - New `skillnir.notifications` package splits the subsystem into `providers` (registry + validators) and `senders` (per-provider POST functions) with a shared `_post_json` helper
  - **Per-provider expansion panels** on the Settings page -- one collapsible card per provider with its own credential inputs, Save, Test, Clear, and "Make active" buttons
  - **Active provider dropdown** at the top of the Notifications card -- save credentials for any/all providers but dispatch goes to the one marked active
  - Bell icon in the top app bar toggles notifications on/off globally; disabled until the active provider has complete credentials
  - Wired into every existing sound-notification trigger: skill injection, skill sync, skill generation, research, events, security, benchmarks, AI docs, AI rule, AI assistant
  - Webhook POSTs run in a background thread -- UI never blocks on network
  - Failures log to stderr; the Test button in Settings surfaces errors visibly for configuration-time validation
  - Message titles include the active model in the form `Task title (model: <model-id>)` so you can tell which backend produced the result at a glance
  - **Provider-specific payload shapes**: Google Chat cards-v2, Slack text with bold title, Discord rich embeds, Teams `{title,detail,source}` dict (user's Power Automate flow renders), Telegram Bot API plain text, Zoho Cliq text
  - **Telegram credentials are split**: bot token + chat ID are stored as two separate encrypted fields, not combined into one
  - **Automatic active-provider migration** for users upgrading from the single-provider era: if only `gchat_webhook_cipher` is set, `active_provider` auto-promotes to `"gchat"` on first load
- **At-rest encryption for the webhook URL** (`skillnir.crypto` module) -- the webhook URL is now stored encrypted in `~/.skillnir/config.json` under `gchat_webhook_cipher`
  - Fernet symmetric encryption keyed from a **per-install UUID** at `~/.skillnir/client_id` combined with a **machine fingerprint** (hostname, username, platform, home path)
  - A copied `config.json` cannot be decrypted on another machine -- mitigates the "config accidentally committed to git / synced to Dropbox / pasted in a log" leak vector
  - Client UUID is generated on first access; file is written with `0600` permissions on POSIX
  - Automatic one-shot migration: legacy plaintext `gchat_webhook_url` fields are encrypted and the plaintext field is removed on first `load_config()`
  - New `AppConfig.get_webhook_url()` / `AppConfig.set_webhook_url(url)` accessor methods replace direct field access
  - **Threat model caveat**: this protects against at-rest file leaks and cross-machine copies, but NOT against malware running as the same user on the same machine -- treat webhook URLs as rotatable secrets regardless
- **`AppConfig` multi-provider credential fields** in `~/.skillnir/config.json`: `gchat_webhook_cipher`, `slack_webhook_cipher`, `discord_webhook_cipher`, `teams_webhook_cipher`, `telegram_bot_token_cipher`, `telegram_chat_id_cipher`, `cliq_webhook_cipher`, plus `active_provider` and `notifications_enabled`. All default to empty so existing users see zero behavior change on upgrade.
- **Generic credential accessors** on `AppConfig`: `get_provider_credentials(provider)`, `set_provider_credentials(provider, creds)`, `clear_provider_credentials(provider)`, `has_provider_credentials(provider)`. Each credential is independently encrypted using the same machine-bound Fernet key. Legacy `get_webhook_url()` / `set_webhook_url()` remain as deprecated wrappers that delegate to the `"gchat"` provider.
- **`skillnir.notifications` package** with `providers.py` (registry + per-provider validators) and `senders.py` (per-provider POST senders + `_post_json` helper). The original `skillnir.notifier` module becomes a thin back-compat re-export shim so existing call sites and tests keep working unchanged.
- **`cryptography>=45.0.0`** as a direct project dependency (was previously transitive via `claude-agent-sdk`)

### Security

- **Webhook URL validation (SSRF hardening) — per provider** -- every sender in `skillnir.notifications.senders` rejects URLs outside its provider's host allowlist before opening a socket
  - Google Chat: exact-host match on `chat.googleapis.com`
  - Slack: exact-host match on `hooks.slack.com`
  - Discord: host in `{discord.com, discordapp.com}`
  - Microsoft Teams: host ends in `.logic.azure.com` with enforced dot boundary (blocks `evillogic.azure.com` suffix forgery)
  - Zoho Cliq: host in the known regional set (`cliq.zoho.{com,eu,in,com.au,com.cn,jp,sa}`, `cliq.zohocloud.ca`) AND URL must include the `zapikey` query parameter
  - Telegram: URL is constructed internally from a validated `bot_token` (regex `^\d+:[A-Za-z0-9_-]{30,}$`) and `chat_id` (signed int or `@username`); the user never pastes a URL
  - All validators enforce `https://` scheme and strip userinfo/port via `urllib.parse.urlsplit`, blocking `http://` (plaintext token leak), `file://` (local file read via urllib), `ftp://`, foreign hosts, `127.0.0.1`/metadata probes, suffix tricks, and userinfo masquerades
  - Settings page validates on both "Save" and "Test" so a typo can't silently persist an unsafe URL
- **Telegram bot token redaction in error messages** -- the Telegram sender post-processes any error string and replaces the bot token with `<redacted>` before returning. Bot tokens ARE capability tokens — a stack trace or UI toast echoing the full URL would leak credentials. Enforced by a hard test assertion in `tests/test_notifications_senders.py::TestSendTelegram::test_error_redacts_bot_token`.
- **NiceGUI server now binds to `127.0.0.1` only** -- previously `ui.run()` used NiceGUI's default (`0.0.0.0`), which exposed the unauthenticated Settings page (and its decrypted webhook URL) to anyone on the same LAN
- **`~/.skillnir/config.json` is now written with `0o600` permissions** -- previously inherited the process umask (typically world-readable), which combined with the same-user-readable `client_id` was enough for a local attacker to decrypt the webhook cipher. Now matches `client_id`'s permissions
- **Loud migration failure for legacy plaintext webhooks** -- if `save_config()` fails while migrating a legacy `gchat_webhook_url` plaintext field to `gchat_webhook_cipher`, skillnir now prints a stderr warning so the user knows to rotate the webhook in Google Chat (previously failed silently, leaving plaintext on disk)
- **`pytest` removed from runtime dependencies** -- was accidentally listed alongside production deps in `pyproject.toml`, pulling the full test framework into every end-user install. pytest stays in `[project.optional-dependencies].dev` and `[dependency-groups].dev`

### Fixed

- **Settings page language section** rendered the literal key `pages.settings.language_title` because it was missing from every locale file
  - Added `language_title`, `language_description`, and `language_current` keys across all 9 locales (en, de, nl, pl, fa, uk, sq, fr, ar)
  - Non-English locales ship English fallbacks with a `_todo_translate` marker for follow-up translation work

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

[1.3.6]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.6
[1.3.5]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.5
[1.3.4]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.4
[1.3.3]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.3
[1.3.2]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.2
[1.3.1]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.1
[1.3.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.3.0
[1.2.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.2.0
[1.1.2]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.2
[1.1.1]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.1
[1.1.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.1.0
[1.0.0]: https://github.com/AlirezaSoltaniJazi/Skillnir/releases/tag/v1.0.0
