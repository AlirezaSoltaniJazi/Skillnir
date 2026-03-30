---
name: frontendEngineer
description: >-
  NiceGUI frontend development skill for the Skillnir project. Covers UI components,
  page routing, Tailwind/Quasar styling, dark/light theming, i18n, state management,
  async progress panels, form validation, and design system conventions. Activates
  when creating components, styling pages, adding routes, managing UI state, working
  with forms, progress panels, i18n translations, or any src/skillnir/ui/ source file.
compatibility: "Python 3.14+, NiceGUI 2.0+, Quasar, Tailwind CSS, Material Design Icons"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep Agent
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: frontendEngineer skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying any file under `src/skillnir/ui/`
2. Creating new UI components in `src/skillnir/ui/components/`
3. Adding new page routes with `@ui.page('/route')` decorator
4. Styling with Tailwind classes, Quasar props, or custom CSS
5. Working with i18n translations, dark/light theming, or browser storage
6. Building async progress panels, form validation, or navigation flows

## Do NOT Use

- **Python backend modules** (CLI, backends, tools, syncer, injector) — use [backendEngineer](../backendEngineer/SKILL.md)
- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)
- **CI/CD, Docker, pre-commit hooks, workflows** — use [devopsEngineer](../devopsEngineer/SKILL.md)

## Architecture

```
src/skillnir/ui/
├── __init__.py              # App setup, _GLOBAL_CSS, static routes, run_ui()
├── layout.py                # header(), drawer nav, helpers, NAV_GROUPS (670 lines)
├── components/              # 13 reusable components
│   ├── page_header.py       # Title + icon + subtitle + separator
│   ├── stat_card.py         # Accent bar + value + label (clickable)
│   ├── section_card.py      # Left-bordered card with icon + nav items
│   ├── hero.py              # Gradient title + stat badges
│   ├── form_card.py         # @contextmanager styled card wrapper
│   ├── progress_panel.py    # Async progress UI (phase, elapsed, log)
│   ├── result_card.py       # Success/failure result display
│   ├── chip_selector.py     # Multi-select toggle chip group
│   ├── empty_state.py       # Centered empty state with icon
│   ├── welcome_dialog.py    # First-visit dialog + CLI install guide
│   ├── backend_chip.py      # Tool/model indicator chip
│   └── backend_picker.py    # Backend/model/prompt dialogs
└── pages/                   # 12 route pages
    ├── home.py              # / — dashboard with hero + section grid
    ├── skill.py             # /install, /update, /check-skill
    ├── delete_skill.py      # /delete-skill
    ├── generate_skill.py    # /generate-skill
    ├── ai_context.py        # /generate-rule, /generate-docs, /delete-docs
    ├── ai_extra.py          # /ask, /plan
    ├── settings.py          # /settings — preferences
    ├── supported.py         # /skills, /tools — registry browsers
    ├── usage_page.py        # /usage
    ├── research.py          # /research
    ├── events.py            # /events
    └── templates.py         # /init-skill, /init-docs
```

**Data flow**: User interaction → `@ui.page` handler → component functions → NiceGUI elements → Quasar/Vue rendering.

**Styling layers**: `_GLOBAL_CSS` (theme) → Tailwind utilities (`.classes()`) → Quasar props (`.props()`) → inline styles (`.style()`).

## Key Patterns

| Pattern              | Approach                                         | Key Rule                                              |
| -------------------- | ------------------------------------------------ | ----------------------------------------------------- |
| Component functions  | `def name(params) -> None` with context managers | One component per file, type-hinted params             |
| Context manager wrap | `@contextmanager` + `yield` for wrapper cards    | Use for container components (e.g., `form_card`)       |
| Color maps           | Module-level `_COLOR_HEX` dict constants         | Map semantic names to hex — never hardcode colors      |
| Page routing         | `@ui.page('/route')` decorator                   | Import module in `__init__.py` to register routes      |
| Page layout          | `header()` + content column with max-width       | Every page starts with `header()` call                 |
| State storage        | `app.storage.user` for UI prefs                  | Dark mode, sound, language stored per-browser          |
| Async progress       | `progress_panel()` + `start_elapsed_timer()`     | Callback-based via `on_progress: Callable`             |
| i18n translations    | `t('dot.key', lang, **kwargs)` function          | All user-facing strings via `t()`, fallback to English |

See [references/component-patterns.md](references/component-patterns.md) for full code examples.

## Code Style

| Rule                  | Convention                                                        |
| --------------------- | ----------------------------------------------------------------- |
| Python version        | 3.14+ — use latest syntax features                                |
| Formatter             | Black with `-S` flag (single quotes, no string normalization)     |
| Import style          | Absolute only — `from skillnir.ui.components.X import X`         |
| Import order          | stdlib → third-party (nicegui) → local (skillnir.*)              |
| NiceGUI imports       | `from nicegui import ui` — at function level when needed          |
| Naming — files        | `snake_case.py` (one component/page per file)                    |
| Naming — functions    | `snake_case` — component name matches filename                   |
| Naming — constants    | `SCREAMING_SNAKE_CASE` (e.g., `NAV_GROUPS`, `_COLOR_HEX`)        |
| Naming — pages        | `page_feature_name()` with `@ui.page('/route')` decorator        |
| Styling — classes     | `.classes('tailwind-utilities custom-classes')`                   |
| Styling — props       | `.props('outlined dense rounded')` for Quasar props               |
| Styling — inline      | `.style(f'color: {hex_color}')` only for dynamic values           |
| Type hints            | `str \| None`, `list[X]`, `Callable \| None` — modern syntax     |
| Strings               | Single quotes (Black -S enforced)                                 |
| Docstrings            | Google-style, module one-liners, function descriptions             |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new component**: Create `src/skillnir/ui/components/name.py` → define `def name(params) -> None` → use `with ui.X().classes()` pattern → import in pages
2. **Add a new page route**: Create `src/skillnir/ui/pages/name.py` → add `@ui.page('/route')` → call `header()` first → wrap content in max-width column → import module in `__init__.py`
3. **Add a nav item**: Add entry to `NAV_GROUPS` in `layout.py` → add translated `get_nav_groups()` entry → add i18n keys to all locale JSON files
4. **Add a translated string**: Add dot-notation key to `src/skillnir/locales/en.json` → add to all 8 other locale files → use `t('key.path', lang)` in components
5. **Add a settings toggle**: Create card in `settings.py` → use `app.storage.user` for persistence → add `ui.switch` with `on_change` callback → show `ui.notify()`
6. **Add async generation page**: Use `async def page_name()` → build `progress_panel()` → `start_elapsed_timer()` → `make_on_progress()` callback → handle result with `result_card()`

## Testing Standards

| Rule                     | Convention                                                   |
| ------------------------ | ------------------------------------------------------------ |
| Framework                | pytest 9.0.2+ with `asyncio_mode = "auto"`                  |
| Test file naming         | `test_{{module}}.py` in `tests/`                             |
| UI component tests       | Test function output indirectly via integration tests        |
| Key fixtures             | `tmp_path` for filesystem, `mock_config` for app config      |
| Mocking                  | `unittest.mock.patch` for NiceGUI elements, storage          |
| What to test             | Component logic, color maps, state transitions, validation   |
| What NOT to test         | NiceGUI rendering internals, Quasar behavior, CSS output     |

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance Rules

- Lazy-import `nicegui` inside functions — not at module level (prevents import-time side effects)
- Use `fade-in` CSS animation instead of JavaScript transitions
- Set `max_lines` on `ui.log()` to prevent unbounded DOM growth (default: 300)
- Use `asyncio.create_task()` for non-blocking timers (elapsed time, polling)
- Minimize `await ui.run_javascript()` calls — prefer NiceGUI Python API
- Serve static assets via `app.add_static_files()` — not inline base64
- Use `.props('flat bordered')` on cards that don't need shadows (reduces paint)

## Security

- Validate all user-provided paths with `Path.resolve()` before filesystem operations
- Use `ui.notify()` for error display — never expose stack traces to UI
- Set `storage_secret` for `app.storage.user` encryption
- Sanitize dynamic content in `.style()` — no user input in CSS expressions
- Never use `ui.run_javascript()` with unsanitized user data (XSS risk)
- Never embed secrets in client-side storage

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern                                | Why It's Wrong                                                      |
| ------------------------------------------- | ------------------------------------------------------------------- |
| Using raw HTML instead of NiceGUI elements  | Breaks reactivity and loses Quasar theming                          |
| Hardcoding hex colors in components         | Use `_COLOR_HEX` maps — keeps palette consistent and maintainable   |
| Skipping `header()` on page functions       | Pages lose navigation drawer, dark mode toggle, language switcher   |
| Module-level `from nicegui import ui`       | Causes import-time side effects — import inside functions            |
| Using `os.path` instead of `pathlib`        | Project standardized on `Path` — consistency and readability        |
| Using relative imports                      | Project uses absolute imports exclusively                           |
| Using JavaScript frameworks (React/Vue)     | This is a NiceGUI project — all UI is Python-defined                |
| Putting page logic directly in `layout.py`  | Pages belong in `pages/` — layout is for shared navigation only     |
| Inline CSS for theme-level styles           | Add to `_GLOBAL_CSS` in `__init__.py` — keeps theme centralized     |
| Skipping i18n `t()` for user-facing strings | Breaks internationalization for 9 supported languages               |

## Code Generation Rules

1. **Read before writing** — always read the target file and related components before changes
2. **Match existing style** — follow Black `-S`, Tailwind classes, Quasar props patterns exactly
3. **One component per file** — each component in its own file with matching function name
4. **Type everything** — use modern type hints on all function signatures
5. **Use color maps** — create `_COLOR_HEX` dicts for any new color-themed components
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                    | Behavior                                                              |
| ---------- | ------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Diagnostic | "not rendering", "layout broken", "style missing", UI screenshot    | Read component + CSS, trace styling chain, fix with minimal changes   |
| Efficient  | "another component like X", "add page for Y", "same card as Z"     | Minimal explanation, replicate existing patterns, apply conventions    |
| Teaching   | "what is this class", "how does NiceGUI X work", "explain layout"  | Explain with project examples, link to references/                    |
| Review     | "review this component", "check my page", "audit styling"          | Read-only analysis, check against conventions, report without changes |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent              | Role                                              | Spawn When                                            | Tools                          |
| ------------------ | ------------------------------------------------- | ----------------------------------------------------- | ------------------------------ |
| component-auditor  | Read-only component analysis for consistency      | UI consistency review, component pattern audit         | Read Glob Grep                 |
| style-enforcer     | Design system and Tailwind/Quasar compliance      | Style audit, theme consistency check, color palette    | Read Glob Grep                 |
| test-writer        | UI component and integration test generation      | "write tests for X", new component, coverage gaps     | Read Edit Write Glob Grep Bash |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                          | Examples                                                          |
| ----------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------------- |
| **MUST** follow   | `header()` on pages, absolute imports, `_COLOR_HEX` maps, `t()` for strings  | "MUST call header()", "MUST use color maps"                       |
| **SHOULD** follow | `fade-in` animation, `card-hover` class, max-width content column              | "SHOULD add fade-in", "SHOULD wrap in max-w-5xl"                  |
| **CAN** customize | Component internal layout, icon choice, spacing values, animation timing       | "CAN use different gap", "CAN choose icon color"                  |

## References

| File                                                                     | Description                                                        |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions            |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)             |
| [references/component-patterns.md](references/component-patterns.md)     | Component structure, context managers, lifecycle with examples      |
| [references/code-style.md](references/code-style.md)                     | Import order, Tailwind/Quasar conventions, formatting examples     |
| [references/state-patterns.md](references/state-patterns.md)             | Storage, async progress, callback patterns with examples           |
| [references/test-patterns.md](references/test-patterns.md)               | UI component testing strategies and mock patterns                  |
| [references/security-checklist.md](references/security-checklist.md)     | XSS prevention, storage safety, path validation checklists         |
| [references/common-issues.md](references/common-issues.md)               | NiceGUI gotchas, async pitfalls, styling troubleshooting           |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols                   |
| [references/component-template.py](references/component-template.py)     | Copy-paste component boilerplate                                   |
| [assets/global-css-example.py](assets/global-css-example.py)             | _GLOBAL_CSS template with theme variables                          |
| [scripts/validate-frontend.sh](scripts/validate-frontend.sh)             | UI naming + structure convention checker                            |
| [agents/component-auditor.md](agents/component-auditor.md)               | Read-only UI component analysis agent                              |
| [agents/style-enforcer.md](agents/style-enforcer.md)                     | Design system compliance agent                                     |
| [agents/test-writer.md](agents/test-writer.md)                           | UI component test generation agent                                 |
