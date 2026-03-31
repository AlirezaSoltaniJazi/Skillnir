# Code Style — Skillnir Frontend

> Import order, Tailwind/Quasar conventions, and formatting rules with full examples.

---

## Import Order

Three groups, separated by blank lines:

```python
import asyncio
import time
from contextlib import contextmanager
from pathlib import Path

from nicegui import app, ui

from skillnir.i18n import get_current_language, is_rtl, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header
```

**Rules**:
- stdlib imports first
- Third-party imports second (`nicegui`)
- Local (`skillnir.*`) imports third
- Never use relative imports
- Never use wildcard imports
- In `layout.py`, import `nicegui` inside functions (lazy) to avoid import-time side effects

---

## Styling Chain

NiceGUI elements are styled via chained method calls:

```python
# ✅ Correct — Tailwind via .classes(), Quasar via .props(), dynamic via .style()
ui.card().classes('w-full p-5 card-hover').props('flat bordered')
ui.input('Label').props('outlined dense rounded').classes('w-full')
ui.element('div').classes('accent-bar w-12 mb-3').style(f'background: {hex_color}')

# ❌ Wrong — raw HTML attributes
ui.html('<div class="p-5" style="background: #6366f1">...</div>')
```

### Classes Priority

1. **Layout**: `w-full`, `flex-1`, `min-w-[160px]`, `max-w-5xl`, `mx-auto`
2. **Spacing**: `p-5`, `px-8`, `py-8`, `gap-6`, `mb-3`, `mt-1`
3. **Typography**: `text-3xl`, `font-bold`, `tracking-tight`, `leading-relaxed`
4. **Colors**: `text-secondary`, `text-info`, `text-positive`
5. **Effects**: `fade-in`, `card-hover`, `gradient-text`, `cursor-pointer`
6. **Borders**: `rounded-xl`, `rounded-lg`, `border-l-accent`

---

## Custom CSS Classes

Defined in `_GLOBAL_CSS` within `src/skillnir/ui/__init__.py`:

| Class             | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `fade-in`         | Entry animation (translateY + opacity)      |
| `card-hover`      | Hover lift + shadow effect on cards         |
| `gradient-text`   | Indigo→Violet→Cyan gradient text            |
| `accent-bar`      | Thin colored bar (3px height, rounded)      |
| `border-l-accent` | Left border with 4px solid + 12px radius    |
| `nav-active`      | Active navigation item highlight            |
| `model-card`      | Hover scale + border animation for pickers  |
| `text-secondary`  | Theme-adaptive secondary text color         |

---

## Color Palette

| Name        | Hex       | Tailwind Equivalent | Usage                    |
| ----------- | --------- | ------------------- | ------------------------ |
| `primary`   | `#6366f1` | indigo-600          | Primary actions, accents |
| `secondary` | `#8b5cf6` | violet-500          | Secondary elements       |
| `accent`    | `#06b6d4` | cyan-500            | Highlights, links        |
| `positive`  | `#10b981` | emerald-600         | Success states           |
| `negative`  | `#ef4444` | red-500             | Error states             |
| `warning`   | `#f59e0b` | amber-500           | Warnings, cautions       |
| `info`      | `#3b82f6` | blue-500            | Informational elements   |
| `grey`      | `#6b7280` | gray-500            | Disabled, muted          |

---

## Quasar Props

Common props passed via `.props()`:

```python
# Input fields
ui.input('Label').props('outlined dense rounded')

# Cards
ui.card().props('flat bordered')  # no shadow, visible border

# Buttons
ui.button('Action', icon='icon_name').props('flat rounded')
ui.button('Primary').props('rounded unelevated')

# Progress
ui.linear_progress().props('indeterminate color=primary rounded')

# Badges
ui.badge('Text', color='primary').props('rounded')
```

---

## Component File Template

```python
"""One-line description of the component."""

from nicegui import ui


def component_name(param: str, color: str = 'primary') -> None:
    """Render a brief description of what this component does."""
    with ui.card().classes('w-full p-5 card-hover'):
        ui.label(param).classes('text-lg font-semibold')
```

---

## Page File Template

```python
"""One-line description of the page."""

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/route-name')
def page_route_name():
    header()

    lang = get_current_language()
    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.route.title', lang),
            t('pages.route.subtitle', lang),
            icon='icon_name',
        )

        # ── Section ──
        with ui.card().classes('w-full p-5 card-hover'):
            pass
```

---

## Naming Conventions

| Entity          | Convention                           | Example                          |
| --------------- | ------------------------------------ | -------------------------------- |
| Component file  | `snake_case.py`                      | `stat_card.py`                   |
| Component func  | `snake_case` (matches filename)      | `def stat_card(...)`             |
| Page file       | `snake_case.py`                      | `generate_skill.py`              |
| Page func       | `page_feature_name`                  | `def page_generate_skill()`      |
| Constants       | `SCREAMING_SNAKE`                    | `NAV_GROUPS`, `SORT_MODES`       |
| Private consts  | `_SCREAMING_SNAKE`                   | `_COLOR_HEX`, `_ICON_BG`        |
| CSS classes     | `kebab-case`                         | `card-hover`, `fade-in`          |
| Route paths     | `kebab-case`                         | `/generate-skill`, `/check-skill`|
| i18n keys       | `dot.notation`                       | `pages.home.sections.skill.title`|
