# Component Patterns — Skillnir Frontend

> Full code examples for UI component patterns used in the Skillnir project. Referenced from SKILL.md Key Patterns table.

---

## Standard Component Pattern

Components are pure Python functions that return `None` and use NiceGUI context managers:

```python
"""Page header component with title, subtitle, and separator."""

from nicegui import ui


def page_header(title: str, subtitle: str = '', icon: str = '') -> None:
    """Render a consistent page header with icon, title, subtitle, and separator."""
    with ui.column().classes('gap-1 mb-2 fade-in'):
        with ui.row().classes('items-center gap-3'):
            if icon:
                ui.icon(icon, color='primary').classes('text-3xl')
            ui.label(title).classes('text-3xl font-bold tracking-tight')
        if subtitle:
            ui.label(subtitle).classes('text-base text-secondary leading-relaxed')
        ui.separator().classes('mt-3')
```

**Rules**:

- One component per file, function name matches filename
- Module docstring describes purpose
- Type hints on all parameters
- Google-style function docstring
- Use `fade-in` class for entrance animations

---

## Color Map Pattern

Components with themed colors use module-level `_COLOR_HEX` dicts:

```python
"""Stat card component with accent bar, value, and label."""

from collections.abc import Callable

from nicegui import ui

# Map color names to hex for the accent bar
_COLOR_HEX = {
    'primary': '#6366f1',
    'secondary': '#8b5cf6',
    'accent': '#06b6d4',
    'positive': '#10b981',
    'negative': '#ef4444',
    'warning': '#f59e0b',
    'info': '#3b82f6',
    'grey': '#6b7280',
}


def stat_card(
    value: str,
    label: str,
    icon: str = '',
    color: str = 'primary',
    clickable: bool = False,
    on_click: Callable | None = None,
) -> None:
    """Render a stat card with colored accent bar, large value, and label."""
    hex_color = _COLOR_HEX.get(color, color)
    cls = 'p-5 rounded-xl flex-1 min-w-[160px]'
    if clickable:
        cls += ' cursor-pointer card-hover'

    card = ui.card().classes(cls)
    if clickable and on_click:
        card.on('click', on_click)

    with card:
        ui.element('div').classes('accent-bar w-12 mb-3').style(
            f'background: {hex_color}'
        )
        with ui.row().classes('items-end gap-3'):
            if icon:
                ui.icon(icon, color=color).classes('text-2xl')
            ui.label(value).classes('text-3xl font-bold').style(f'color: {hex_color}')
        ui.label(label).classes('text-sm text-secondary mt-1')
```

---

## Context Manager Component Pattern

Wrapper components use `@contextmanager` with `yield`:

```python
"""Styled form card wrapper component."""

from contextlib import contextmanager

from nicegui import ui


@contextmanager
def form_card():
    """Context manager that yields a styled card for form inputs.

    Usage::

        with form_card():
            ui.input('Target project').props('outlined dense rounded')
    """
    with ui.card().classes('w-full p-6 rounded-xl').props('flat bordered'):
        yield
```

---

## Page Route Pattern

Pages use `@ui.page` decorator and always call `header()`:

```python
"""Settings page for user preferences."""

from nicegui import app, ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/settings')
def page_settings():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header('Settings', 'Configure application preferences.', icon='settings')

        # ── Section cards follow ──
        with ui.card().classes('w-full p-5 card-hover'):
            # ... card content
            pass
```

**Rules**:

- Always call `header()` first (provides nav drawer, theme toggle)
- Wrap content in `ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6')`
- Use `page_header()` for consistent title sections
- Use comment separators (`# ── Section ──`) for visual structure

---

## Async Progress Pattern

Long-running operations use `progress_panel()` + `start_elapsed_timer()`:

```python
refs = progress_panel(container, max_log_lines=300)
control = start_elapsed_timer(refs, time.time())
counters = {'tools': 0, 'lines': 0}
on_progress = make_on_progress(refs, counters)

# Run async operation with callback
await run_operation(on_progress=on_progress)

# Stop timer
control['active'] = False
```

---

## Navigation Item Pattern

Navigation uses icon + label + route tuples:

```python
NAV_GROUPS = [
    (
        'SECTION TITLE',
        [
            ('icon_name', 'Label', '/route'),
            ('icon_name', 'Label', '/route'),
        ],
    ),
]
```

Programmatic navigation: `ui.navigate.to('/route')`

---

## Event Handler Pattern

Inline handlers with lambda for route-specific closures:

```python
# Lambda closure for loop variable binding
with ui.row().on(
    'click',
    lambda route=item_route: ui.navigate.to(route),
):
    ui.label(item_label)

# Named handler for state mutations
def on_dark_toggle(e):
    dark.value = e.value
    app.storage.user['dark_mode'] = e.value
    ui.notify('Dark mode enabled' if e.value else 'Light mode enabled', type='info')

ui.switch('', value=is_dark, on_change=on_dark_toggle)
```
