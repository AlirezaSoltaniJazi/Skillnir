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
    cls = 'p-5 rounded-xl flex-1 min-w-[160px]'
    if clickable:
        cls += ' cursor-pointer card-hover'

    card = ui.card().classes(cls)
    if clickable and on_click:
        card.on('click', on_click)

    hex_color = _COLOR_HEX.get(color, color)
    with card:
        ui.element('div').classes('accent-bar w-12 mb-3').style(
            f'background: {hex_color}'
        )
        with ui.row().classes('items-end gap-3'):
            if icon:
                ui.icon(icon, color=color).classes('text-2xl')
            ui.label(value).classes('text-3xl font-bold').style(f'color: {hex_color}')
        ui.label(label).classes('text-sm text-gray-400 mt-1')
