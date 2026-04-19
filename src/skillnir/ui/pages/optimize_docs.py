"""Compress AI docs + optimize AI docs UI pages."""

import time
from pathlib import Path

from nicegui import ui

from skillnir.i18n import t, get_current_language
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    make_on_progress,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.layout import header, play_notification


@ui.page('/compress-docs')
async def page_compress_docs():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.compress_docs.title', lang),
            t('pages.compress_docs.subtitle', lang),
            icon='compress',
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
            target_input = (
                ui.input(
                    t('pages.compress_docs.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            ai_tone_cb = ui.checkbox(
                t('pages.compress_docs.with_ai_tone', lang), value=True
            )

        scan_container = ui.column().classes('w-full')
        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')
        state: dict = {'dry': None}

        def do_scan():
            from skillnir.docs_compressor import (
                compress_docs_dry_run,
                find_ai_docs,
            )

            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return
            docs = find_ai_docs(target)
            if not docs:
                scan_container.clear()
                with scan_container:
                    ui.label(t('pages.compress_docs.no_docs_found', lang)).classes(
                        'text-secondary'
                    )
                state['dry'] = None
                return

            dry = compress_docs_dry_run(target)
            state['dry'] = dry
            scan_container.clear()
            with scan_container:
                ui.label(
                    t(
                        'pages.compress_docs.scan_summary',
                        lang,
                        count=str(len(dry.files)),
                        original=str(dry.total_original_chars),
                        compressed=str(dry.total_compressed_chars),
                        pct=f'{dry.total_reduction_pct:.1f}',
                    )
                ).classes('font-medium mb-2')
                for r in dry.files:
                    rel = r.path.relative_to(target)
                    if r.error:
                        with ui.row().classes('items-center gap-2'):
                            ui.badge('error', color='negative')
                            ui.label(f'{rel}: {r.error}').classes(
                                'text-sm font-mono text-red-400'
                            )
                    else:
                        with ui.row().classes('items-center gap-2'):
                            ui.badge(
                                f'-{r.reduction_pct:.1f}%',
                                color='positive' if r.reduction_pct > 0 else 'grey',
                            )
                            ui.label(
                                f'{rel}: {r.original_chars} -> {r.compressed_chars}'
                            ).classes('text-sm font-mono')

        ui.button(t('buttons.scan', lang), on_click=do_scan, icon='search').props(
            'unelevated rounded'
        )

        async def do_apply():
            if not state.get('dry'):
                ui.notify(t('pages.compress_docs.scan_first', lang), type='warning')
                return
            target = Path(target_input.value).resolve()
            results_container.clear()

            apply_btn.disable()
            target_input.disable()
            ai_tone_cb.disable()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}
            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.docs_compressor import compress_docs_apply

            result = await compress_docs_apply(
                target,
                with_ai_tone=ai_tone_cb.value,
                on_progress=on_progress,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()
            apply_btn.enable()
            target_input.enable()
            ai_tone_cb.enable()

            written = sum(1 for r in result.files if r.written)
            grid = {
                'Files compressed': f'{written}/{len(result.files)}',
                'Original chars': str(result.total_original_chars),
                'Compressed chars': str(result.total_compressed_chars),
                'Reduction': f'{result.total_reduction_pct:.1f}%',
                'AI tone pass': 'applied' if result.ai_tone_applied else 'skipped',
                'Duration': format_duration(secs),
                'Tools used': str(counters['tools']),
            }
            if result.backend_used:
                grid['AI Tool'] = (
                    BACKENDS[result.backend_used].name
                    if result.backend_used in BACKENDS
                    else result.backend_used.value
                )

            success = not result.error or result.ai_tone_applied or written > 0
            result_card(
                results_container,
                success,
                t(
                    (
                        'pages.compress_docs.result_success_title'
                        if success
                        else 'pages.compress_docs.result_fail_title'
                    ),
                    lang,
                ),
                grid_data=grid,
                error=result.error if not success else None,
            )
            if result.error and success:
                with results_container:
                    ui.label(f'Note: {result.error}').classes(
                        'text-warning text-sm mt-2'
                    )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/compress-docs'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="AI docs compressed")

        apply_btn = ui.button(
            t('buttons.apply', lang),
            on_click=do_apply,
            icon='compress',
        ).props('unelevated rounded color=positive')


@ui.page('/optimize-docs')
async def page_optimize_docs():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.optimize_docs.title', lang),
            t('pages.optimize_docs.subtitle', lang),
            icon='auto_fix_high',
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
            target_input = (
                ui.input(
                    t('pages.optimize_docs.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            mode_select = (
                ui.select(
                    label=t('pages.optimize_docs.mode_label', lang),
                    options={
                        'report': t('pages.optimize_docs.mode_report', lang),
                        'apply': t('pages.optimize_docs.mode_apply', lang),
                    },
                    value='report',
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )
            version_select = (
                ui.select(
                    label=t('pages.optimize_docs.prompt_version', lang),
                    options=PROMPT_VERSION_LABELS,
                    value=config.prompt_version,
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_run():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return

            run_btn.disable()
            target_input.disable()
            mode_select.disable()
            version_select.disable()
            results_container.clear()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}
            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.docs_optimizer import optimize_docs

            result = await optimize_docs(
                target,
                mode=mode_select.value,
                on_progress=on_progress,
                prompt_version_override=version_select.value,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()
            run_btn.enable()
            target_input.enable()
            mode_select.enable()
            version_select.enable()

            if result.success:
                grid = {'Mode': result.mode}
                if result.report_path:
                    grid['Report'] = str(result.report_path)
                grid['Files touched'] = str(len(result.files_touched))
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
                    t('pages.optimize_docs.result_success_title', lang),
                    grid_data=grid,
                )
            else:
                result_card(
                    results_container,
                    False,
                    t('pages.optimize_docs.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/optimize-docs'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="AI docs optimized")

        run_btn = ui.button(
            t('buttons.optimize', lang),
            on_click=do_run,
            icon='auto_fix_high',
        ).props('unelevated rounded color=positive')
