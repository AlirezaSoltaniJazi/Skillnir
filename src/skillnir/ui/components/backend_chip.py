"""Compact backend indicator chip for the app bar / home page."""

from nicegui import ui

from skillnir.backends import AIBackend


def backend_chip(config, backend_info, on_click_switch=None) -> None:
    """Render a compact chip showing AI tool icon + model name."""
    cls = 'items-center gap-3 px-4 py-2 rounded-xl cursor-pointer card-hover'
    with ui.card().classes(cls).on('click', on_click_switch or (lambda: None)):
        with ui.row().classes('items-center gap-3'):
            ui.icon(backend_info.icon, color='primary').classes('text-2xl')
            with ui.column().classes('gap-0'):
                ui.label(backend_info.name).classes('text-sm font-bold')
                ui.label(f'Model: {config.model}').classes('text-xs text-secondary')
                # Reasoning controls only meaningful for Claude SDK; hide for
                # other backends so the chip stays compact and accurate.
                if config.backend == AIBackend.CLAUDE:
                    ui.label(
                        f'Effort: {config.effort} · Thinking: {config.thinking_mode}'
                    ).classes('text-xs text-secondary')
            ui.icon('expand_more', color='grey').classes('text-lg')
