"""Empty state placeholder component."""

from nicegui import ui


def empty_state(icon: str, title: str, subtitle: str = '') -> None:
    """Render a centered empty state with large icon, title, and optional subtitle."""
    with ui.column().classes('items-center justify-center py-16 gap-4 w-full fade-in'):
        ui.icon(icon, color='grey').classes('text-6xl opacity-40')
        ui.label(title).classes('text-xl font-medium text-gray-400')
        if subtitle:
            ui.label(subtitle).classes('text-sm text-gray-500 text-center max-w-md')
