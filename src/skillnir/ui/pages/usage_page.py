"""Token usage dashboard page."""

from nicegui import ui

from skillnir.ui.components.empty_state import empty_state
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.stat_card import stat_card
from skillnir.ui.layout import header
from skillnir.usage import session_tracker


@ui.page('/usage')
def page_usage():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Token Usage',
            'Session-level token usage across all AI backends.',
            icon='analytics',
        )

        all_usage = session_tracker.get_all()

        if not all_usage:
            empty_state(
                'info',
                'No AI requests yet',
                'Token usage will appear here after you generate docs, skills, or ask AI questions.',
            )
        else:
            # ── Summary ──
            total = session_tracker.get_total()
            ui.label('Session Summary').classes('text-lg font-semibold')
            with ui.row().classes('gap-4 flex-wrap'):
                stat_card(
                    f'{total.total_tokens:,}',
                    'Total Tokens',
                    icon='token',
                    color='primary',
                )
                stat_card(
                    f'{total.input_tokens:,}',
                    'Input Tokens',
                    icon='input',
                    color='info',
                )
                stat_card(
                    f'{total.output_tokens:,}',
                    'Output Tokens',
                    icon='output',
                    color='secondary',
                )
                stat_card(
                    f'${total.total_cost_usd:.4f}',
                    'Total Cost',
                    icon='attach_money',
                    color='positive',
                )
                stat_card(
                    str(total.num_requests), 'Requests', icon='send', color='warning'
                )

            # ── Per-Backend ──
            for backend_name, usage in all_usage.items():
                ui.separator().classes('my-2')
                ui.label(backend_name.capitalize()).classes('text-lg font-semibold')
                with ui.row().classes('gap-4 flex-wrap'):
                    stat_card(f'{usage.input_tokens:,}', 'Input Tokens', color='info')
                    stat_card(
                        f'{usage.output_tokens:,}', 'Output Tokens', color='secondary'
                    )
                    cache_tokens = (
                        usage.cache_creation_input_tokens
                        + usage.cache_read_input_tokens
                    )
                    stat_card(f'{cache_tokens:,}', 'Cache Tokens', color='grey')
                    stat_card(f'${usage.total_cost_usd:.4f}', 'Cost', color='positive')
                    stat_card(str(usage.num_requests), 'Requests', color='warning')

        # ── Actions ──
        with ui.row().classes('gap-3 mt-2'):

            def do_reset():
                session_tracker.reset()
                ui.navigate.to('/usage')

            ui.button('Reset', on_click=do_reset, icon='restart_alt').props(
                'flat rounded color=negative'
            )
            ui.button(
                'Refresh',
                on_click=lambda: ui.navigate.to('/usage'),
                icon='refresh',
            ).props('flat rounded color=primary')
