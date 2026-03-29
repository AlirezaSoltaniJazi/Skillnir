"""Hero section component for the home page."""

from nicegui import ui

from skillnir.i18n import get_current_language, t


def hero(skills_count: int, tools_count: int, dotdirs_count: int) -> None:
    """Render the hero section with gradient title and inline stat chips."""
    lang = get_current_language()
    with ui.column().classes('gap-3 fade-in'):
        ui.label(t('components.hero.title', lang)).classes(
            'text-5xl font-bold gradient-text tracking-tight'
        )
        ui.label(t('components.hero.tagline', lang)).classes(
            'text-lg text-gray-400 leading-relaxed'
        )
        with ui.row().classes('gap-3 mt-1'):
            ui.badge(
                t('components.hero.skills_badge', lang, count=str(skills_count)),
                color='primary',
            ).props('rounded')
            ui.badge(
                t('components.hero.tools_badge', lang, count=str(tools_count)),
                color='positive',
            ).props('rounded')
            ui.badge(
                t('components.hero.dotdirs_badge', lang, count=str(dotdirs_count)),
                color='warning',
            ).props('rounded')
