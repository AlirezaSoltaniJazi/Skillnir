---
name: frontendEngineer
description: >-
  NiceGUI frontend development skill for the Skillnir project. Covers UI components,
  page routing, Tailwind/Quasar styling, dark/light theming, i18n, state management,
  async progress panels, form validation, and design system conventions. Activates
  when creating components, styling pages, adding routes, managing UI state, working
  with forms, progress panels, i18n translations, or any src/skillnir/ui/ source file.
compatibility: "Python 3.14+, NiceGUI 3.10+, Quasar, Tailwind CSS, Material Design Icons"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep Agent
sub-agents:
  - name: component-auditor
    file: agents/component-auditor.md
  - name: style-enforcer
    file: agents/style-enforcer.md
  - name: test-writer
    file: agents/test-writer.md
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It holds corrections, preferences, and conventions from previous sessions. Apply every rule there — they override this skill's defaults.

**Announce skill usage.** Always say "Using: frontendEngineer skill" at the very start of the response before doing any work.

## When to Use

1. Writing or modifying any file under `src/skillnir/ui/`
2. Creating new UI components in `src/skillnir/ui/components/`
3. Adding page routes with the `@ui.page('/route')` decorator
4. Styling with Tailwind classes, Quasar props, or custom CSS
5. Working with i18n translations, dark/light theming, or browser storage
6. Building async progress panels, form validation, or navigation flows

## Do NOT Use

- **Python backend modules** (CLI, backends, tools, syncer, injector) — use [backendEngineer](../backendEngineer/SKILL.md)
- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)
- **CI/CD, Docker, pre-commit hooks, workflows** — use [devopsEngineer](../devopsEngineer/SKILL.md)

## Architecture

`src/skillnir/ui/`: `__init__.py` = app setup + `_GLOBAL_CSS` theme + static routes + `run_ui()`; `layout.py` = `header()`, drawer nav, `NAV_GROUPS`, install/sync flow builders; `components/` = 13 reusable component functions (one per file); `pages/` = 23 `@ui.page` route modules.

**Data flow**: user interaction → `@ui.page` handler → component functions → NiceGUI elements → Quasar/Vue rendering. **Styling layers**: `_GLOBAL_CSS` → Tailwind `.classes()` → Quasar `.props()` → inline `.style()` (dynamic only).

Full tree + per-file map: [references/architecture-guide.md](references/architecture-guide.md).

## Key Patterns

| Pattern | Approach | Key Rule (and why) |
| --- | --- | --- |
| Component functions | `def name(params) -> None` with context managers | One component per file, type-hinted — keeps components discoverable and testable |
| Context manager wrap | `@contextmanager` + `yield` for wrapper cards | Use for container components (e.g., `form_card`) so callers nest content |
| Color maps | Module-level `_COLOR_HEX` dict constants | Map semantic names to hex — never hardcode, so the palette stays consistent |
| Page routing | `@ui.page('/route')` decorator | Import the module in `__init__.py` or the route never registers |
| Page layout | `header()` + content column with max-width | Every page MUST call `header()` first — else it loses the nav drawer, dark-mode toggle, and language switcher |
| State storage | `app.storage.user` for UI prefs | Dark mode, sound, language persist per-browser |
| Async progress | `progress_panel()` + `start_elapsed_timer()` | Callback-based via `on_progress: Callable` |
| i18n translations | `t('dot.key', lang, **kwargs)` | All user-facing strings via `t()` or 9 languages break; fallback to English |

See [references/component-patterns.md](references/component-patterns.md) and [references/state-patterns.md](references/state-patterns.md) for full examples.

## Code Style

| Rule | Convention |
| --- | --- |
| Python version | 3.14+ — use latest syntax features |
| Formatter | Black with `-S` (skips string normalization) |
| Quote style | Match the file's existing quotes — `-S` preserves, does not normalize (per-file inventory in code-style ref) |
| Import style | Absolute only — `from skillnir.ui.components.X import X` |
| Import order | stdlib → third-party (nicegui) → local (`skillnir.*`) |
| NiceGUI imports | `from nicegui import ui` at function level when needed |
| Naming — files | `snake_case.py`, one component/page per file |
| Naming — functions | `snake_case`, component name matches filename |
| Naming — constants | `SCREAMING_SNAKE_CASE` (`NAV_GROUPS`, `_COLOR_HEX`) |
| Naming — pages | `page_feature_name()` + `@ui.page('/route')` |
| Styling | `.classes()` = Tailwind, `.props()` = Quasar, `.style()` = dynamic values only |
| Type hints | `str \| None`, `list[X]`, `Callable \| None` — modern syntax |
| Docstrings | Google-style, module one-liners, function descriptions |

See [references/code-style.md](references/code-style.md) for formatting examples and the per-file quote inventory.

## Common Recipes

1. **Add a component**: create `components/name.py` → `def name(params) -> None` → `with ui.X().classes()` → import in pages
2. **Add a page route**: create `pages/name.py` → `@ui.page('/route')` → call `header()` first → wrap content in max-width column → import module in `__init__.py`
3. **Add a nav item**: add entry to `NAV_GROUPS` in `layout.py` → add `get_nav_groups()` entry → add i18n keys to all locale JSON files
4. **Add a translated string**: add dot-key to `locales/en.json` → add to all 8 other locales → `t('key.path', lang)` in components
5. **Add a settings toggle**: card in `settings.py` → persist via `app.storage.user` → `ui.switch` with `on_change` → `ui.notify()`
6. **Add async generation page**: `async def page_name()` → `progress_panel()` → `start_elapsed_timer()` → `make_on_progress()` callback → `result_card()`

## Testing Standards

| Rule | Convention |
| --- | --- |
| Framework | pytest 9.0.3+ with `asyncio_mode = "auto"` |
| Test file naming | `test_{module}.py` in `tests/` |
| UI component tests | Test output indirectly via integration tests |
| Key fixtures | `tmp_path` for filesystem, `mock_config` for app config |
| Mocking | `unittest.mock.patch` for NiceGUI elements, storage |
| What to test | Component logic, color maps, state transitions, validation |
| What NOT to test | NiceGUI rendering internals, Quasar behavior, CSS output |

See [references/test-patterns.md](references/test-patterns.md) for full examples.

## Performance Rules

1. Lazy-import `nicegui` inside functions — avoids import-time side effects
2. Use `fade-in` CSS animation instead of JavaScript transitions
3. Set `max_lines` on `ui.log()` (default 300) to cap DOM growth
4. Use `asyncio.create_task()` for non-blocking timers (elapsed, polling)
5. Minimize `await ui.run_javascript()` — prefer the NiceGUI Python API
6. Serve static assets via `app.add_static_files()`, not inline base64
7. `.props('flat bordered')` on cards that don't need shadows (less paint)

## Security

- Validate user-provided paths with `Path.resolve()` before filesystem ops — blocks traversal
- Use `ui.notify()` for errors — never expose stack traces to the UI
- Set `storage_secret` for `app.storage.user` encryption
- Never put user input in `.style()` CSS expressions or `ui.run_javascript()` — XSS risk
- Never embed secrets in client-side storage

See [references/security-checklist.md](references/security-checklist.md) for severity-classified checklists.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
| --- | --- |
| Raw HTML instead of NiceGUI elements | Breaks reactivity and loses Quasar theming |
| Hardcoding hex colors in components | Use `_COLOR_HEX` maps — keeps palette consistent |
| Skipping `header()` on page functions | Pages lose nav drawer, dark-mode toggle, language switcher |
| Module-level `from nicegui import ui` in `layout.py` | Causes import-time side effects — import inside functions |
| `os.path` instead of `pathlib` | Project standardized on `Path` |
| Relative imports | Project uses absolute imports exclusively |
| React/Vue/JS frameworks | NiceGUI project — all UI is Python-defined |
| Page logic in `layout.py` | Pages belong in `pages/`; layout is shared nav only |
| Inline CSS for theme-level styles | Add to `_GLOBAL_CSS` — keeps theme centralized |
| Skipping `t()` for user-facing strings | Breaks i18n for 9 supported languages |

## Session Protocols

**Read [LEARNED.md](LEARNED.md) before generating any code.** Default to Teaching when uncertain; developer override always wins.

| Mode | Detection signals (frontend) | Behavior |
| --- | --- | --- |
| Teaching | "what is this class", "how does NiceGUI X work", first encounter with a pattern | Explain with project examples, then generate |
| Efficient | "another component like X", "same card as Z", Nth repeat of a known pattern | Replicate existing pattern, minimal prose |
| Diagnostic | "not rendering", "layout broken", "style missing", UI screenshot, traceback | Trace styling chain (CSS → classes → props), then fix |

**Self-Learning (non-negotiable, learnings are written not suggested):**
- **On correction**: acknowledge, restate as a rule, apply for the session, write under `## Corrections`.
- **On ambiguity**: check LEARNED.md, then project files (`CLAUDE.md`, existing code); ask ONE question; write under `## Preferences`.
- **On discovering an implicit convention**: state it, then write under `## Discovered Conventions`.
- Entry format: `- YYYY-MM-DD: rule description`.

Deeper guidance (proficiency calibration, anti-dependency nudges): [references/ai-interaction-guide.md](references/ai-interaction-guide.md).

## Communication Style

- **Lead with the answer** — no preamble, no "Let me explain", no "Great question"
- **Strip filler words** — remove "basically", "essentially", "actually", "just", "simply"
- **No trailing summaries** — the user can read the diff; don't restate what you did
- **Bullet points over paragraphs** — lists, tables, one-liners
- **Code over explanation** — show the fix, not a lecture about it
- **Maximum 2-3 sentences** per explanation unless asked "why" or in Teaching mode
- **No hedging** — say "do X", not "you might want to consider X"
- **No apologies** — don't say "sorry"; just fix it

## Sub-Agent Delegation

| Agent | Role | Spawn When | Tools |
| --- | --- | --- | --- |
| [component-auditor](agents/component-auditor.md) | Read-only component consistency analysis | UI consistency review, component pattern audit | Read Glob Grep |
| [style-enforcer](agents/style-enforcer.md) | Design system + Tailwind/Quasar compliance | Style audit, theme/color-palette check | Read Glob Grep |
| [test-writer](agents/test-writer.md) | UI component/integration test generation | "write tests for X", new component, coverage gaps | Read Edit Write Glob Grep Bash |

**Delegation rules:**
1. Delegate when the task is self-contained and won't need follow-up context
2. Stay inline for architectural decisions or simple single-focus edits
3. Pass ALL context explicitly — sub-agents don't see parent conversation
4. Cap at 3-4 sub-agents; they cannot spawn their own (max depth = 1)

## Freedom Levels

| Level | Scope | Examples |
| --- | --- | --- |
| **MUST** follow | `header()` on pages, absolute imports, `_COLOR_HEX` maps, `t()` for strings, Session Protocols (modes + LEARNED.md writes), sub-agent context rules | "MUST call `header()`", "MUST write corrections to LEARNED.md" |
| **SHOULD** follow | `fade-in` animation, `card-hover` class, max-width content column, mode detection signals | "SHOULD add fade-in", "SHOULD wrap in max-w-5xl" |
| **CAN** customize | Component internal layout, icon choice, spacing, animation timing, sub-agent tool sets | "CAN use a different gap", "CAN choose icon color" |

## References

| File | Description |
| --- | --- |
| [LEARNED.md](LEARNED.md) | **Auto-updated.** Corrections, preferences, conventions |
| [INJECT.md](INJECT.md) | Always-loaded quick reference (hallucination firewall) |
| [references/architecture-guide.md](references/architecture-guide.md) | Full `ui/` tree + per-file map |
| [references/component-patterns.md](references/component-patterns.md) | Component structure, context managers, lifecycle |
| [references/code-style.md](references/code-style.md) | Import order, Tailwind/Quasar, per-file quote inventory |
| [references/state-patterns.md](references/state-patterns.md) | Storage, async progress, callback patterns |
| [references/test-patterns.md](references/test-patterns.md) | UI testing strategies and mock patterns |
| [references/security-checklist.md](references/security-checklist.md) | XSS, storage, path-validation checklists |
| [references/common-issues.md](references/common-issues.md) | NiceGUI gotchas, async pitfalls, styling fixes |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols |
| [references/component-template.py](references/component-template.py) | Copy-paste component boilerplate |
| [assets/global-css-example.py](assets/global-css-example.py) | `_GLOBAL_CSS` template with theme variables |
| [scripts/validate-frontend.sh](scripts/validate-frontend.sh) | UI naming + structure convention checker |
| [agents/](agents/) | component-auditor, style-enforcer, test-writer definitions |
