"""Success / failure result card component."""

from nicegui import ui


def result_card(
    container,
    success: bool,
    title: str,
    grid_data: dict[str, str] | None = None,
    error: str | None = None,
    footer_text: str | None = None,
) -> None:
    """Render a success or failure result card inside *container*.

    Args:
        container: NiceGUI container to render into.
        success: Whether the operation succeeded.
        title: Card title (e.g. 'Generation Complete').
        grid_data: Key-value pairs to display in a 2-column grid (success case).
        error: Error message to display (failure case).
        footer_text: Optional footer text shown below the grid.
    """
    container.clear()

    with container:
        if success:
            border_color = '#10b981'
            with (
                ui.card()
                .classes('w-full p-6 border-l-accent fade-in')
                .style(f'border-left-color: {border_color}')
            ):
                with ui.row().classes('items-center gap-3 mb-4'):
                    ui.icon('check_circle', color='positive').classes('text-2xl')
                    ui.label(title).classes('text-xl font-bold')
                if grid_data:
                    with ui.grid(columns=2).classes('gap-x-6 gap-y-2'):
                        for key, value in grid_data.items():
                            ui.label(f'{key}:').classes('font-medium')
                            ui.label(str(value)).classes(
                                'text-gray-300 font-mono text-sm'
                            )
                if footer_text:
                    ui.label(footer_text).classes('text-gray-400 text-sm mt-4')
        else:
            border_color = '#ef4444'
            with (
                ui.card()
                .classes('w-full p-6 border-l-accent fade-in')
                .style(f'border-left-color: {border_color}')
            ):
                with ui.row().classes('items-center gap-3 mb-4'):
                    ui.icon('error', color='negative').classes('text-2xl')
                    ui.label(title).classes('text-xl font-bold')
                if error:
                    ui.html(
                        f'<pre style="white-space:pre-wrap;font-size:0.85rem;'
                        f'color:#f87171;margin:0">{error}</pre>'
                    )
