"""Section card component for the home page grid."""

from collections.abc import Callable

from nicegui import ui

# Map section colors to hex for the left border
_COLOR_HEX = {
    'primary': '#6366f1',
    'info': '#3b82f6',
    'secondary': '#8b5cf6',
    'amber': '#f59e0b',
    'teal': '#14b8a6',
    'positive': '#10b981',
    'deep-purple': '#7c3aed',
    'grey': '#6b7280',
    'accent': '#06b6d4',
}

# Map section colors to Tailwind bg/text for icon circle
_ICON_BG = {
    'primary': 'bg-indigo-500/10 text-indigo-400',
    'info': 'bg-blue-500/10 text-blue-400',
    'secondary': 'bg-violet-500/10 text-violet-400',
    'amber': 'bg-amber-500/10 text-amber-400',
    'teal': 'bg-teal-500/10 text-teal-400',
    'positive': 'bg-emerald-500/10 text-emerald-400',
    'deep-purple': 'bg-purple-500/10 text-purple-400',
    'grey': 'bg-gray-500/10 text-secondary',
    'accent': 'bg-cyan-500/10 text-cyan-400',
}


def section_card(
    icon: str,
    color: str,
    title: str,
    desc: str,
    items: list[tuple[str, str, str]],
    special_content: Callable | None = None,
) -> None:
    """Render a section card with colored left border, icon, title, and nav items."""
    hex_color = _COLOR_HEX.get(color, '#6b7280')
    icon_cls = _ICON_BG.get(color, 'bg-gray-500/10 text-secondary')

    with (
        ui.card()
        .classes('w-full p-5 border-l-accent card-hover')
        .style(f'border-left-color: {hex_color}')
    ):
        with ui.row().classes('items-center gap-3 mb-3'):
            ui.icon(icon).classes(f'text-2xl p-2 rounded-full {icon_cls}')
            ui.label(title).classes('text-lg font-semibold')
        ui.label(desc).classes('text-sm text-secondary mb-3')

        if special_content:
            special_content()
        elif items:
            with ui.column().classes('gap-0 w-full'):
                for item_icon, item_label, item_route in items:
                    with (
                        ui.row()
                        .classes(
                            'items-center gap-3 px-3 py-2 rounded-lg '
                            'cursor-pointer hover:bg-white/5 w-full '
                            'transition-all duration-150'
                        )
                        .on(
                            'click',
                            lambda route=item_route: ui.navigate.to(route),
                        )
                    ):
                        ui.icon(item_icon, color=color).classes('text-base')
                        ui.label(item_label).classes('text-sm flex-1')
                        ui.icon('chevron_right', color='grey').classes(
                            'text-sm opacity-40'
                        )
