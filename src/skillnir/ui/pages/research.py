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
from skillnir.i18n import t, get_current_language
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
    lang = get_current_language()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.research.title', lang),
            t('pages.research.subtitle', lang),
            icon='science',
        )

        with ui.row().classes('items-center gap-2'):
            ui.icon(backend_info.icon, size='sm').classes('text-secondary')
            ui.label(
                t(
                    'messages.using_backend',
                    lang,
                    name=backend_info.name,
                    model=config.model,
                )
            ).classes('text-sm text-secondary')

        # ── Topic chips ──
        selected_topics = list(TOPIC_LABELS.keys())
        selected_sources: list[str] = []

        with ui.row().classes('items-center gap-3'):
            ui.label(t('pages.research.topics_to_search', lang)).classes(
                'text-sm font-medium text-secondary'
            )

            def _select_all_topics():
                selected_topics.clear()
                selected_topics.extend(TOPIC_LABELS.keys())
                _rebuild_topic_chips()

            def _deselect_all_topics():
                selected_topics.clear()
                _rebuild_topic_chips()

            ui.button(
                t('buttons.select_all', lang),
                on_click=_select_all_topics,
                icon='check_box',
            ).props('flat rounded dense size=sm')
            ui.button(
                t('buttons.deselect_all', lang),
                on_click=_deselect_all_topics,
                icon='check_box_outline_blank',
            ).props('flat rounded dense size=sm')
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
        with ui.row().classes('items-center gap-3'):
            ui.label(t('pages.research.filter_by_source', lang)).classes(
                'text-sm font-medium text-secondary'
            )

            def _select_all_sources():
                selected_sources.clear()
                selected_sources.extend(SOURCE_FILTERS.keys())
                _rebuild_source_chips()

            def _deselect_all_sources():
                selected_sources.clear()
                _rebuild_source_chips()

            ui.button(
                t('buttons.select_all', lang),
                on_click=_select_all_sources,
                icon='check_box',
            ).props('flat rounded dense size=sm')
            ui.button(
                t('buttons.deselect_all', lang),
                on_click=_deselect_all_sources,
                icon='check_box_outline_blank',
            ).props('flat rounded dense size=sm')
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

        # ── Time range chips ──
        selected_date_range: dict[str, str | None] = {'value': None}

        _dateOptions: list[tuple[str, str | None]] = [
            ('All time', None),
            ('Last 1 month', 'published in the last 1 month'),
            ('Last 3 months', 'published in the last 3 months'),
            ('Last 6 months', 'published in the last 6 months'),
            ('Last 12 months', 'published in the last 12 months'),
            ('2026', 'published in 2026'),
            ('2025', 'published in 2025'),
            ('2024', 'published in 2024'),
        ]

        with ui.row().classes('items-center gap-3'):
            ui.label('Time range').classes('text-sm font-medium text-secondary')
        date_chips_container = ui.row().classes('gap-2 flex-wrap')

        def _rebuild_date_chips():
            date_chips_container.clear()
            with date_chips_container:
                for label, value in _dateOptions:

                    def _toggle(v=value):
                        selected_date_range['value'] = v
                        _rebuild_date_chips()

                    is_sel = selected_date_range['value'] == value
                    if is_sel:
                        ui.chip(
                            label, icon='check', color='accent', on_click=_toggle
                        ).props('clickable')
                    else:
                        ui.chip(label, on_click=_toggle).props('clickable outline')

        _rebuild_date_chips()

        # ── Existing articles ──
        research_dir = _get_research_dir()

        def _cache_bust_url() -> str:
            return f'/research-files/index.html?t={int(time.time())}'

        existing = _load_index(research_dir)
        if existing:
            with ui.row().classes('gap-4 flex-wrap'):
                stat_card(
                    str(len(existing)),
                    t('pages.research.articles_in_kb', lang),
                    icon='article',
                    color='info',
                )

            index_path = research_dir / 'index.html'
            if index_path.exists():

                with ui.row().classes('gap-3'):

                    def view_landing():
                        from skillnir.researcher import regenerate_landing

                        count, _ = regenerate_landing(research_dir)
                        if count:
                            ui.notify(
                                t(
                                    'pages.research.generated_html_pages',
                                    lang,
                                    count=str(count),
                                ),
                                type='positive',
                            )
                        ui.navigate.to(_cache_bust_url(), new_tab=True)

                    ui.button(
                        t('buttons.view_landing_page', lang),
                        on_click=view_landing,
                        icon='open_in_new',
                    ).props('flat rounded')

                    def generate_html_files():
                        from skillnir.researcher import regenerate_landing

                        count, _ = regenerate_landing(research_dir)
                        if count:
                            ui.notify(
                                t(
                                    'pages.research.generated_html_pages',
                                    lang,
                                    count=str(count),
                                ),
                                type='positive',
                            )
                        else:
                            ui.notify(
                                t('pages.research.all_articles_have_html', lang),
                                type='info',
                            )

                    ui.button(
                        t('buttons.generate_html_files', lang),
                        on_click=generate_html_files,
                        icon='code',
                    ).props('flat rounded')

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_research():
            start_time = time.time()
            if not selected_topics:
                ui.notify(
                    t('pages.research.select_at_least_one_topic', lang), type='warning'
                )
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
                date_range=selected_date_range['value'],
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)

            # Keep log visible
            progress_container.clear()
            with progress_container:
                log_visible = {'value': True}
                with ui.row().classes('items-center gap-3'):
                    ui.label(t('components.progress_panel.log_output', lang)).classes(
                        'text-sm font-medium text-secondary'
                    )

                    def toggle_log():
                        log_visible['value'] = not log_visible['value']
                        saved_log.set_visibility(log_visible['value'])
                        toggle_btn.text = (
                            t('buttons.hide_log', lang)
                            if log_visible['value']
                            else t('buttons.show_log', lang)
                        )

                    toggle_btn = ui.button(
                        t('buttons.hide_log', lang),
                        on_click=toggle_log,
                        icon='visibility_off',
                    ).props('flat rounded dense')
                saved_log = ui.log(max_lines=500).classes(
                    'w-full h-72 font-mono text-xs'
                )
                for prev_line in log_lines:
                    saved_log.push(prev_line)

            research_btn.enable()

            if result.success:
                grid = {
                    t('pages.research.grid_articles_found', lang): str(
                        result.articles_found
                    ),
                    t('pages.research.grid_new_articles', lang): str(
                        result.articles_new
                    ),
                    t('pages.research.grid_skipped_dedup', lang): str(
                        result.articles_skipped
                    ),
                    t('pages.research.grid_duration', lang): format_duration(secs),
                }
                result_card(
                    results_container,
                    True,
                    t('pages.research.result_success_title', lang),
                    grid_data=grid,
                )

                if result.index_path and result.index_path.exists():
                    with results_container:
                        ui.button(
                            t('buttons.open_landing_page', lang),
                            on_click=lambda: ui.navigate.to(
                                _cache_bust_url(), new_tab=True
                            ),
                            icon='open_in_new',
                        ).props('unelevated rounded color=positive').classes('mt-3')
            else:
                result_card(
                    results_container,
                    False,
                    t('pages.research.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.search_again', lang),
                        on_click=lambda: ui.navigate.to('/research'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="Research complete")

        research_btn = ui.button(
            t('buttons.search_latest_articles', lang),
            on_click=do_research,
            icon='travel_explore',
        ).props('unelevated rounded color=positive')
