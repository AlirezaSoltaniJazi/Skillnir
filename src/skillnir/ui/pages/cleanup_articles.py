"""Cleanup research articles UI page — classify outdated articles and move them."""

import time
from datetime import date, timedelta

from nicegui import ui

from skillnir.i18n import t, get_current_language
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    make_on_progress,
    progress_panel,
    start_elapsed_timer,
    survive_disconnect,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.layout import header, play_notification


@ui.page('/cleanup-articles')
async def page_cleanup_articles():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.article_cleanup import DEFAULT_MAX_ARTICLES, STORE_SPECS
    from skillnir.backends import BACKENDS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.cleanup_articles.title', lang),
            t('pages.cleanup_articles.subtitle', lang),
            icon='cleaning_services',
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

        with ui.card().classes('w-full p-6').props('flat bordered'):
            store_select = (
                ui.select(
                    label=t('pages.cleanup_articles.store_label', lang),
                    options={key: spec.label for key, spec in STORE_SPECS.items()},
                    value='research',
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            mode_select = (
                ui.select(
                    label=t('pages.cleanup_articles.mode_label', lang),
                    options={
                        'report': t('pages.cleanup_articles.mode_report', lang),
                        'apply': t('pages.cleanup_articles.mode_apply', lang),
                    },
                    value='report',
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )
            topics_select = (
                ui.select(
                    label=t('pages.cleanup_articles.topics_label', lang),
                    options=dict(STORE_SPECS['research'].topic_labels),
                    multiple=True,
                    value=[],
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded use-chips')
            )
            older_select = (
                ui.select(
                    label=t('pages.cleanup_articles.older_than_label', lang),
                    options={
                        0: t('pages.cleanup_articles.older_all', lang),
                        182: t('pages.cleanup_articles.older_6m', lang),
                        365: t('pages.cleanup_articles.older_12m', lang),
                        548: t('pages.cleanup_articles.older_18m', lang),
                    },
                    value=0,
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )
            max_input = (
                ui.number(
                    label=t('pages.cleanup_articles.max_articles_label', lang),
                    value=DEFAULT_MAX_ARTICLES,
                    min=1,
                    max=2000,
                    precision=0,
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )

            def _on_store_change():
                spec = STORE_SPECS[store_select.value]
                topics_select.set_options(dict(spec.topic_labels), value=[])

            store_select.on_value_change(_on_store_change)

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        @survive_disconnect
        async def do_run():
            run_btn.disable()
            for el in (
                store_select,
                mode_select,
                topics_select,
                older_select,
                max_input,
            ):
                el.disable()
            results_container.clear()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}
            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.article_cleanup import cleanup_articles

            days = int(older_select.value or 0)
            older_than = (
                (date.today() - timedelta(days=days)).isoformat() if days else None
            )

            result = await cleanup_articles(
                store_select.value,
                mode=mode_select.value,
                topics=list(topics_select.value) or None,
                older_than=older_than,
                max_articles=int(max_input.value or DEFAULT_MAX_ARTICLES),
                on_progress=on_progress,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()
            run_btn.enable()
            for el in (
                store_select,
                mode_select,
                topics_select,
                older_select,
                max_input,
            ):
                el.enable()

            if result.success:
                grid = {
                    'Mode': result.mode,
                    'Scanned': f'{result.scanned} articles ({result.batches} batches)',
                    'Outdated': str(len(result.candidates)),
                    'Low confidence': str(len(result.low_confidence)),
                }
                if result.mode == 'apply':
                    grid['Files moved'] = str(result.moved)
                if result.report_md_path:
                    grid['Report'] = str(result.report_md_path)
                grid['Duration'] = format_duration(secs)
                grid['Tools used'] = str(counters['tools'])
                if result.backend_used:
                    grid['AI Tool'] = (
                        BACKENDS[result.backend_used].name
                        if result.backend_used in BACKENDS
                        else result.backend_used.value
                    )
                result_card(
                    results_container,
                    True,
                    t('pages.cleanup_articles.result_success_title', lang),
                    grid_data=grid,
                )
                if not result.candidates and not result.low_confidence:
                    with results_container:
                        ui.label(
                            t('pages.cleanup_articles.no_candidates', lang)
                        ).classes('text-secondary text-sm mt-2')
            else:
                result_card(
                    results_container,
                    False,
                    t('pages.cleanup_articles.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/cleanup-articles'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="Article cleanup finished")

        run_btn = ui.button(
            t('pages.cleanup_articles.start_button', lang),
            on_click=do_run,
            icon='cleaning_services',
        ).props('unelevated rounded color=positive')
