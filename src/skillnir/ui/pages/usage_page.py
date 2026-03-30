"""Token usage dashboard page."""

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.empty_state import empty_state
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.stat_card import stat_card
from skillnir.ui.layout import header
from skillnir.usage import ClaudeApiUsage, fetch_claude_api_usage, session_tracker


@ui.page('/usage')
def page_usage():
    lang = get_current_language()
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.usage.title', lang),
            t('pages.usage.subtitle', lang),
            icon='analytics',
        )

        all_usage = session_tracker.get_all()

        if not all_usage:
            empty_state(
                'info',
                t('pages.usage.no_requests_title', lang),
                t('pages.usage.no_requests_subtitle', lang),
            )
        else:
            # ── Summary ──
            total = session_tracker.get_total()
            ui.label(t('pages.usage.session_summary', lang)).classes(
                'text-lg font-semibold'
            )
            with ui.row().classes('gap-4 flex-wrap'):
                stat_card(
                    f'{total.total_tokens:,}',
                    t('pages.usage.total_tokens', lang),
                    icon='token',
                    color='primary',
                )
                stat_card(
                    f'{total.input_tokens:,}',
                    t('pages.usage.input_tokens', lang),
                    icon='input',
                    color='info',
                )
                stat_card(
                    f'{total.output_tokens:,}',
                    t('pages.usage.output_tokens', lang),
                    icon='output',
                    color='secondary',
                )
                stat_card(
                    f'${total.total_cost_usd:.4f}',
                    t('pages.usage.total_cost', lang),
                    icon='attach_money',
                    color='positive',
                )
                stat_card(
                    str(total.num_requests),
                    t('pages.usage.requests', lang),
                    icon='send',
                    color='warning',
                )

            # ── Per-Backend ──
            for backend_name, usage in all_usage.items():
                ui.separator().classes('my-2')
                ui.label(backend_name.capitalize()).classes('text-lg font-semibold')
                with ui.row().classes('gap-4 flex-wrap'):
                    stat_card(
                        f'{usage.input_tokens:,}',
                        t('pages.usage.input_tokens', lang),
                        color='info',
                    )
                    stat_card(
                        f'{usage.output_tokens:,}',
                        t('pages.usage.output_tokens', lang),
                        color='secondary',
                    )
                    cache_tokens = (
                        usage.cache_creation_input_tokens
                        + usage.cache_read_input_tokens
                    )
                    stat_card(
                        f'{cache_tokens:,}',
                        t('pages.usage.cache_tokens', lang),
                        color='grey',
                    )
                    stat_card(
                        f'${usage.total_cost_usd:.4f}',
                        t('pages.usage.cost', lang),
                        color='positive',
                    )
                    stat_card(
                        str(usage.num_requests),
                        t('pages.usage.requests', lang),
                        color='warning',
                    )

        # ── Claude API Usage ──
        api_container = ui.column().classes('w-full')

        def _load_claude_api_usage():
            api_container.clear()
            with api_container:
                ui.separator().classes('my-4')
                ui.label('Claude API Usage (Live)').classes('text-lg font-semibold')
                api_usage = fetch_claude_api_usage()
                if api_usage is None:
                    ui.label(
                        'Could not fetch Claude API usage. '
                        'Ensure Claude Code is logged in.'
                    ).classes('text-secondary text-sm')
                else:
                    _render_api_usage(api_usage)

        def _render_api_usage(u: ClaudeApiUsage) -> None:
            def _bar_color(pct: float) -> str:
                if pct >= 90:
                    return 'negative'
                if pct >= 70:
                    return 'warning'
                if pct >= 50:
                    return 'amber'
                return 'positive'

            with ui.row().classes('gap-4 flex-wrap w-full'):
                with ui.card().classes('p-4 min-w-[200px]'):
                    ui.label('5-Hour Window').classes('text-sm font-medium')
                    pct = u.five_hour_utilization
                    ui.linear_progress(value=pct / 100, color=_bar_color(pct)).props(
                        'rounded size=20px'
                    ).classes('mt-2')
                    ui.label(f'{pct:.1f}%').classes('text-2xl font-bold mt-1')
                    if u.five_hour_resets_at:
                        ui.label(f'Resets: {u.five_hour_resets_at}').classes(
                            'text-secondary text-xs'
                        )

                with ui.card().classes('p-4 min-w-[200px]'):
                    ui.label('7-Day Window').classes('text-sm font-medium')
                    pct = u.seven_day_utilization
                    ui.linear_progress(value=pct / 100, color=_bar_color(pct)).props(
                        'rounded size=20px'
                    ).classes('mt-2')
                    ui.label(f'{pct:.1f}%').classes('text-2xl font-bold mt-1')
                    if u.seven_day_resets_at:
                        ui.label(f'Resets: {u.seven_day_resets_at}').classes(
                            'text-secondary text-xs'
                        )

                with ui.card().classes('p-4 min-w-[200px]'):
                    ui.label('7-Day Sonnet').classes('text-sm font-medium')
                    pct = u.seven_day_sonnet_utilization
                    ui.linear_progress(value=pct / 100, color=_bar_color(pct)).props(
                        'rounded size=20px'
                    ).classes('mt-2')
                    ui.label(f'{pct:.1f}%').classes('text-2xl font-bold mt-1')

                with ui.card().classes('p-4 min-w-[200px]'):
                    ui.label('7-Day Opus').classes('text-sm font-medium')
                    pct = u.seven_day_opus_utilization
                    ui.linear_progress(value=pct / 100, color=_bar_color(pct)).props(
                        'rounded size=20px'
                    ).classes('mt-2')
                    ui.label(f'{pct:.1f}%').classes('text-2xl font-bold mt-1')

            if u.extra_usage_enabled:
                with ui.row().classes('gap-4 mt-2'):
                    with ui.card().classes('p-4 min-w-[200px]'):
                        ui.label('Extra Usage Credits').classes('text-sm font-medium')
                        ui.label(
                            f'${u.extra_usage_used:.2f} / ${u.extra_usage_limit:.2f}'
                        ).classes('text-lg font-bold mt-1')

        _load_claude_api_usage()

        # ── Actions ──
        with ui.row().classes('gap-3 mt-2'):

            def do_reset():
                session_tracker.reset()
                ui.navigate.to('/usage')

            ui.button(
                t('buttons.reset', lang), on_click=do_reset, icon='restart_alt'
            ).props('flat rounded color=negative')
            ui.button(
                t('buttons.refresh', lang),
                on_click=lambda: ui.navigate.to('/usage'),
                icon='refresh',
            ).props('flat rounded color=primary')
            ui.button(
                'Refresh Claude API',
                on_click=_load_claude_api_usage,
                icon='cloud_sync',
            ).props('flat rounded color=info')
