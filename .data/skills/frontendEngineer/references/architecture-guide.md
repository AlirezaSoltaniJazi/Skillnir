# Architecture — Skillnir Frontend (`src/skillnir/ui/`)

> Full structure map for the NiceGUI web UI. SKILL.md carries only a 4-line summary; this is the complete tree.

## Entry Points & Data Flow

- `__init__.py` — app setup, `_GLOBAL_CSS` theme, static routes, `run_ui()`
- `layout.py` — `header()`, drawer nav, `NAV_GROUPS`, install/sync flow builders
- `components/` — 13 reusable component functions (one per file)
- `pages/` — 23 route modules (`@ui.page` handlers)

**Data flow**: User interaction → `@ui.page` handler → component functions → NiceGUI elements → Quasar/Vue rendering.

**Styling layers**: `_GLOBAL_CSS` (theme) → Tailwind utilities (`.classes()`) → Quasar props (`.props()`) → inline styles (`.style()`, dynamic values only).

## Full Tree

```
src/skillnir/ui/
├── __init__.py              # App setup, _GLOBAL_CSS, static routes, run_ui()
├── layout.py                # header(), drawer nav, NAV_GROUPS, install/sync flow builders (833 lines)
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
│   ├── backend_picker.py    # Backend/model/prompt dialogs
│   └── path_input.py        # Text input + persisted recent-paths chip list
└── pages/                   # 23 route pages
    ├── home.py                # / — dashboard with hero + section grid
    ├── skill.py               # /install, /update, /skills
    ├── delete_skill.py        # /delete-skill
    ├── generate_skill.py      # /generate-skill
    ├── ai_context.py          # /generate-rule, /generate-docs, /delete-docs
    ├── ai_extra.py            # /ask, /plan, /check-skill
    ├── settings.py            # /settings — preferences
    ├── supported.py           # /tools — tool registry browser
    ├── usage_page.py          # /usage
    ├── research.py            # /research
    ├── events.py              # /events
    ├── templates.py           # /init-skill, /init-docs
    ├── benchmarks.py          # /benchmarks — AI model benchmarks
    ├── cleanup_articles.py    # /cleanup-articles — classify + move outdated articles
    ├── harness_research.py    # /harness-research — harness-engineering research
    ├── ignore.py              # /install-ignore — install-ignore file editor
    ├── news.py                # /news — AI news by category/recency window
    ├── optimize_docs.py       # /compress-docs, /optimize-docs
    ├── package_vulns_page.py  # /package-vulns — package vulnerability research
    ├── security_page.py       # /security — security vulnerability research
    ├── software_research.py   # /software-research
    ├── testing_research.py    # /testing-research
    └── wiki.py                # /generate-wiki, /delete-wiki
```
