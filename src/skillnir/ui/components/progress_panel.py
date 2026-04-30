"""Shared async progress panel component used by generation and research pages."""

import asyncio
import time

from nicegui import ui


def progress_panel(container, max_log_lines: int = 300) -> dict:
    """Build the standard progress UI inside *container*.

    Returns a dict of element references that pages can update::

        {
            'phase': ui.label,       # phase title (e.g. 'Generating...')
            'status': ui.label,      # status subtitle
            'elapsed': ui.label,     # elapsed time display
            'tools': ui.label,       # tools-used counter
            'lines': ui.label,       # lines-output counter
            'log': ui.log,           # live output log
        }
    """
    container.clear()
    refs = {}

    with container:
        with ui.card().classes('w-full p-5'):
            # ── Progress bar ──
            ui.linear_progress(value=0, show_value=False).props(
                'indeterminate color=primary rounded'
            ).classes('mb-4')

            with ui.row().classes('items-center gap-4'):
                with ui.column().classes('flex-1 gap-1'):
                    refs['phase'] = ui.label('Initializing...').classes(
                        'text-lg font-bold'
                    )
                    refs['status'] = ui.label('Preparing...').classes(
                        'text-secondary text-sm'
                    )
                with ui.column().classes('items-end gap-0'):
                    refs['elapsed'] = ui.label('0s').classes(
                        'text-2xl font-mono gradient-text'
                    )
                    ui.label('elapsed').classes('text-secondary text-xs')

        # ── Counter cards ──
        with ui.row().classes('gap-4 mt-3'):
            with ui.card().classes('flex-1 px-4 py-3'):
                ui.element('div').classes('accent-bar w-8 mb-2').style(
                    'background: #3b82f6'
                )
                refs['tools'] = ui.label('0').classes('text-xl font-bold text-info')
                ui.label('Tools used').classes('text-xs text-secondary')
            with ui.card().classes('flex-1 px-4 py-3'):
                ui.element('div').classes('accent-bar w-8 mb-2').style(
                    'background: #10b981'
                )
                refs['lines'] = ui.label('0').classes('text-xl font-bold text-positive')
                ui.label('Lines output').classes('text-xs text-secondary')

        # ── Log viewer ──
        with ui.card().classes('w-full p-4 mt-3'):
            with ui.row().classes('items-center justify-between mb-2'):
                ui.label('Live Output').classes('text-sm font-medium text-secondary')
            refs['log'] = ui.log(max_lines=max_log_lines).classes(
                'w-full h-72 font-mono text-xs'
            )

    return refs


def start_elapsed_timer(refs: dict, start_time: float) -> dict:
    """Start the elapsed-time ticker and return a control dict with 'active' flag.

    Call ``control['active'] = False`` to stop the timer.
    """
    control = {'active': True}

    async def _tick():
        while control['active']:
            try:
                secs = int(time.time() - start_time)
                if secs < 60:
                    refs['elapsed'].text = f'{secs}s'
                else:
                    refs['elapsed'].text = f'{secs // 60}m {secs % 60}s'
            except RuntimeError:
                control['active'] = False
                return
            await asyncio.sleep(1)

    asyncio.create_task(_tick())
    return control


def make_on_progress(refs: dict, counters: dict) -> callable:
    """Return a standard ``on_progress`` callback that updates *refs* labels.

    *counters* must be a dict with ``{'tools': 0, 'lines': 0}`` — it is mutated
    in-place so callers can read the final counts after the operation completes.
    """
    from skillnir.generator import GenerationProgress

    def on_progress(p: GenerationProgress) -> None:
        if p.kind == 'phase':
            refs['phase'].text = p.content
            refs['status'].text = ''
            refs['log'].push(f'--- {p.content} ---')
        elif p.kind == 'status':
            refs['status'].text = p.content
            refs['log'].push(f'[info] {p.content}')
        elif p.kind == 'tool_use':
            counters['tools'] += 1
            refs['tools'].text = str(counters['tools'])
            refs['status'].text = p.content
            refs['log'].push(f'[tool] {p.content}')
        elif p.kind == 'text':
            for text_line in p.content.splitlines():
                counters['lines'] += 1
                refs['log'].push(text_line)
            refs['lines'].text = str(counters['lines'])
        elif p.kind == 'error':
            refs['log'].push(f'[ERROR] {p.content}')

    return on_progress


def format_duration(secs: int) -> str:
    """Format seconds as a human-readable duration string."""
    if secs < 60:
        return f'{secs}s'
    return f'{secs // 60}m {secs % 60}s'
