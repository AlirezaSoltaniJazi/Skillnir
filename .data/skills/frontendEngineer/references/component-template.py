"""One-line description of the component."""

from collections.abc import Callable

from nicegui import ui

# Map color names to hex (if component uses themed colors)
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


def component_name(
    title: str,
    subtitle: str = '',
    icon: str = '',
    color: str = 'primary',
    on_click: Callable | None = None,
) -> None:
    """Render a brief description of what this component does.

    Args:
        title: Main text content.
        subtitle: Optional secondary text.
        icon: Material Design icon name.
        color: Semantic color name from _COLOR_HEX.
        on_click: Optional click handler.
    """
    hex_color = _COLOR_HEX.get(color, color)

    card = ui.card().classes('w-full p-5 card-hover')
    if on_click:
        card.on('click', on_click)

    with card:
        with ui.row().classes('items-center gap-3'):
            if icon:
                ui.icon(icon, color=color).classes('text-2xl')
            ui.label(title).classes('text-lg font-semibold')
        if subtitle:
            ui.label(subtitle).classes('text-sm text-secondary mt-1')
