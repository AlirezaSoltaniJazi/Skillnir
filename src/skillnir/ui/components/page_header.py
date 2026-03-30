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
