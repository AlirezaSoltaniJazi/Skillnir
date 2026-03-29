"""Toggleable chip group component for multi-select filtering."""

from nicegui import ui


def chip_selector(
    label: str,
    options: list[str],
    selected: list[str],
    on_change: callable | None = None,
    color: str = 'primary',
) -> None:
    """Render a row of toggleable chips for multi-select.

    Args:
        label: Group label shown above the chips.
        options: List of option strings.
        selected: Mutable list of currently selected options.
        on_change: Optional callback when selection changes.
        color: Quasar color name for selected chips.
    """
    ui.label(label).classes('text-sm font-medium text-gray-400 mb-1')
    with ui.row().classes('gap-2 flex-wrap'):
        for opt in options:
            is_selected = opt in selected

            def _toggle(option=opt):
                if option in selected:
                    selected.remove(option)
                else:
                    selected.append(option)
                if on_change:
                    on_change()

            if is_selected:
                ui.chip(opt, icon='check', color=color, on_click=_toggle).props(
                    'clickable'
                )
            else:
                ui.chip(opt, on_click=_toggle).props('clickable outline')
