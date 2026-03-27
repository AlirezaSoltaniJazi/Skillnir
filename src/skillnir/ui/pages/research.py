"""AI engineering research page."""

import time

from nicegui import ui

from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.components.stat_card import stat_card
from skillnir.ui.layout import header, play_notification


@ui.page('/research')
async def page_research():
    from skillnir.backends import BACKENDS, load_config
    from skillnir.researcher import (
        SOURCE_FILTERS,
        TOPIC_LABELS,
        _get_research_dir,
        _load_index,
        research,
    )

    audio_el, sound_state = header()
    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'AI Engineering Research',
            'Search latest AI engineering news, deep-read articles, and generate summaries',
            icon='science',
        )

        with ui.row().classes('items-center gap-2'):
            ui.icon(backend_info.icon, size='sm').classes('text-gray-400')
            ui.label(f'Using: {backend_info.name} ({config.model})').classes(
                'text-sm text-gray-400'
            )

        # ── Topic chips ──
        selected_topics = list(TOPIC_LABELS.keys())
        selected_sources: list[str] = []

        ui.label('Topics to search:').classes('text-sm font-medium text-gray-400')
        topic_chips_container = ui.row().classes('gap-2 flex-wrap')

        def _rebuild_topic_chips():
            topic_chips_container.clear()
            with topic_chips_container:
                for key, label in TOPIC_LABELS.items():
                    is_sel = key in selected_topics

                    def _toggle(k=key):
                        if k in selected_topics:
                            selected_topics.remove(k)
                        else:
                            selected_topics.append(k)
                        _rebuild_topic_chips()

                    if is_sel:
                        ui.chip(
                            label, icon='check', color='primary', on_click=_toggle
                        ).props('clickable')
                    else:
                        ui.chip(label, on_click=_toggle).props('clickable outline')

        _rebuild_topic_chips()

        # ── Source chips ──
        ui.label('Filter by source (optional):').classes(
            'text-sm font-medium text-gray-400'
        )
        source_chips_container = ui.row().classes('gap-2 flex-wrap')

        def _rebuild_source_chips():
            source_chips_container.clear()
            with source_chips_container:
                for key, label in SOURCE_FILTERS.items():
                    is_sel = key in selected_sources

                    def _toggle(k=key):
                        if k in selected_sources:
                            selected_sources.remove(k)
                        else:
                            selected_sources.append(k)
                        _rebuild_source_chips()

                    if is_sel:
                        ui.chip(
                            label, icon='check', color='secondary', on_click=_toggle
                        ).props('clickable')
                    else:
                        ui.chip(label, on_click=_toggle).props('clickable outline')

        _rebuild_source_chips()

        # ── Existing articles ──
        research_dir = _get_research_dir()
        existing = _load_index(research_dir)
        if existing:
            with ui.row().classes('gap-4 flex-wrap'):
                stat_card(
                    str(len(existing)),
                    'Articles in knowledge base',
                    icon='article',
                    color='info',
                )

            index_path = research_dir / 'index.html'
            if index_path.exists():

                def _cache_bust_url() -> str:
                    return f'/research-files/index.html?t={int(time.time())}'

                with ui.row().classes('gap-3'):

                    def view_landing():
                        from skillnir.researcher import regenerate_landing

                        count, _ = regenerate_landing(research_dir)
                        if count:
                            ui.notify(
                                f'Generated {count} HTML article page(s)',
                                type='positive',
                            )
                        ui.navigate.to(_cache_bust_url(), new_tab=True)

                    ui.button(
                        'View Landing Page',
                        on_click=view_landing,
                        icon='open_in_new',
                    ).props('flat rounded')

                    def generate_html_files():
                        from skillnir.researcher import regenerate_landing

                        count, _ = regenerate_landing(research_dir)
                        if count:
                            ui.notify(
                                f'Generated {count} HTML article page(s)',
                                type='positive',
                            )
                        else:
                            ui.notify(
                                'All articles already have HTML pages', type='info'
                            )

                    ui.button(
                        'Generate HTML Files',
                        on_click=generate_html_files,
                        icon='code',
                    ).props('flat rounded')

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_research():
            start_time = time.time()
            if not selected_topics:
                ui.notify('Select at least one topic', type='warning')
                return

            research_btn.disable()
            results_container.clear()

            new_count = {'value': 0}
            skip_count = {'value': 0}
            log_lines: list[str] = []

            refs = progress_panel(progress_container, max_log_lines=500)
            timer_ctl = start_elapsed_timer(refs, start_time)

            def _log_push(line: str) -> None:
                log_lines.append(line)
                refs['log'].push(line)

            def on_progress(p) -> None:
                if p.kind == 'phase':
                    refs['phase'].text = p.content
                    refs['status'].text = ''
                    _log_push(f'--- {p.content} ---')
                elif p.kind == 'status':
                    refs['status'].text = p.content
                    _log_push(f'  {p.content}')
                    if p.content.startswith('  New:'):
                        new_count['value'] += 1
                        refs['tools'].text = str(new_count['value'])
                    elif p.content.startswith('  Skipped'):
                        skip_count['value'] += 1
                        refs['lines'].text = str(skip_count['value'])
                elif p.kind == 'text':
                    for text_line in p.content.splitlines():
                        _log_push(text_line)
                elif p.kind == 'error':
                    _log_push(f'[ERROR] {p.content}')

            result = await research(
                on_progress=on_progress,
                topics=selected_topics,
                sources=selected_sources or None,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)

            # Keep log visible
            progress_container.clear()
            with progress_container:
                log_visible = {'value': True}
                with ui.row().classes('items-center gap-3'):
                    ui.label('Log Output').classes('text-sm font-medium text-gray-400')

                    def toggle_log():
                        log_visible['value'] = not log_visible['value']
                        saved_log.set_visibility(log_visible['value'])
                        toggle_btn.text = (
                            'Hide Log' if log_visible['value'] else 'Show Log'
                        )

                    toggle_btn = ui.button(
                        'Hide Log', on_click=toggle_log, icon='visibility_off'
                    ).props('flat rounded dense')
                saved_log = ui.log(max_lines=500).classes(
                    'w-full h-72 font-mono text-xs'
                )
                for prev_line in log_lines:
                    saved_log.push(prev_line)

            research_btn.enable()

            if result.success:
                grid = {
                    'Articles found': str(result.articles_found),
                    'New articles': str(result.articles_new),
                    'Skipped (dedup)': str(result.articles_skipped),
                    'Duration': format_duration(secs),
                }
                result_card(
                    results_container, True, 'Research Complete', grid_data=grid
                )

                if result.index_path and result.index_path.exists():
                    with results_container:
                        ui.button(
                            'Open Landing Page',
                            on_click=lambda: ui.navigate.to(
                                _cache_bust_url(), new_tab=True
                            ),
                            icon='open_in_new',
                        ).props('unelevated rounded color=positive').classes('mt-3')
            else:
                result_card(
                    results_container, False, 'Research Failed', error=result.error
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        'Search Again',
                        on_click=lambda: ui.navigate.to('/research'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')

            play_notification(audio_el, sound_state)

        research_btn = ui.button(
            'Search Latest News',
            on_click=do_research,
            icon='travel_explore',
        ).props('unelevated rounded color=positive')
