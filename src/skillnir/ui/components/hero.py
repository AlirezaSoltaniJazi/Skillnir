"""Hero section component for the home page."""

from nicegui import ui


def hero(skills_count: int, tools_count: int, dotdirs_count: int) -> None:
    """Render the hero section with gradient title and inline stat chips."""
    with ui.column().classes('gap-3 fade-in'):
        ui.label('Skillnir').classes('text-5xl font-bold gradient-text tracking-tight')
        ui.label('Inject AI coding skills into any tool\'s dotdir.').classes(
            'text-lg text-gray-400 leading-relaxed'
        )
        with ui.row().classes('gap-3 mt-1'):
            ui.badge(f'{skills_count} Skills', color='primary').props('rounded')
            ui.badge(f'{tools_count} AI Tools', color='positive').props('rounded')
            ui.badge(f'{dotdirs_count} Dotdirs', color='warning').props('rounded')
