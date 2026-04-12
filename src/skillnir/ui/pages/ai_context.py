"""AI context generation and deletion pages."""

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


@ui.page('/generate-docs')
async def page_generate_docs():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.generate_docs.title', lang),
            t('pages.generate_docs.subtitle', lang),
            icon='auto_stories',
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
                    t('pages.generate_docs.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            version_select = (
                ui.select(
                    label=t('pages.generate_docs.prompt_version', lang),
                    options=PROMPT_VERSION_LABELS,
                    value=config.prompt_version,
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_generate():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return

            generate_btn.disable()
            target_input.disable()
            version_select.disable()
            results_container.clear()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}
            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.generator import generate_docs

            result = await generate_docs(
                target,
                on_progress=on_progress,
                prompt_version_override=version_select.value,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()
            generate_btn.enable()
            target_input.enable()
            version_select.enable()

            if result.success:
                grid = {'agents.md': str(result.agents_md_path)}
                if result.claude_md_path:
                    grid['.claude/claude.md'] = str(result.claude_md_path)
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
                    t('pages.generate_docs.result_success_title', lang),
                    grid_data=grid,
                )
            else:
                result_card(
                    results_container,
                    False,
                    t('pages.generate_docs.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/generate-docs'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="AI docs generated")

        generate_btn = ui.button(
            t('buttons.generate_ai_docs', lang),
            on_click=do_generate,
            icon='auto_stories',
        ).props('unelevated rounded color=positive')


@ui.page('/generate-rule')
async def page_generate_rule():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.generate_rule.title', lang),
            t('pages.generate_rule.subtitle', lang),
            icon='gavel',
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
                    t('pages.generate_rule.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            topic_input = (
                ui.textarea(
                    t('pages.generate_rule.rule_topic', lang),
                    placeholder=t('pages.generate_rule.rule_topic_placeholder', lang),
                )
                .classes('w-full max-w-xl')
                .props('rows=3 outlined dense rounded')
            )
            rule_version_select = (
                ui.select(
                    label=t('pages.generate_rule.prompt_version', lang),
                    options=PROMPT_VERSION_LABELS,
                    value=config.prompt_version,
                )
                .classes('w-64')
                .props('outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_generate():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return
            rule_topic = topic_input.value.strip()
            if not rule_topic:
                ui.notify(
                    t('pages.generate_rule.enter_rule_topic', lang), type='warning'
                )
                return

            generate_btn.disable()
            target_input.disable()
            topic_input.disable()
            rule_version_select.disable()
            results_container.clear()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}
            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.rule_generator import generate_rule

            result = await generate_rule(
                target,
                rule_topic,
                on_progress=on_progress,
                prompt_version_override=rule_version_select.value,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()
            generate_btn.enable()
            target_input.enable()
            topic_input.enable()
            rule_version_select.enable()

            if result.success:
                grid = {}
                for i, rf in enumerate(result.rule_files):
                    grid[f'Rule file {i + 1}'] = str(rf)
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
                    t('pages.generate_rule.result_success_title', lang),
                    grid_data=grid,
                )
            else:
                result_card(
                    results_container,
                    False,
                    t('pages.generate_rule.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/generate-rule'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state, title="AI rule generated")

        generate_btn = ui.button(
            t('buttons.generate_rule', lang),
            on_click=do_generate,
            icon='gavel',
        ).props('unelevated rounded color=positive')


@ui.page('/delete-docs')
def page_delete_docs():
    header()
    lang = get_current_language()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.delete_docs.title', lang),
            t('pages.delete_docs.subtitle', lang),
            icon='delete_sweep',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input(
                    t('pages.delete_docs.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        scan_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')
        state: dict = {'installations': []}

        def scan_docs():
            from skillnir.remover import find_docs_installations

            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return
            state['installations'] = find_docs_installations(target)
            results_container.clear()
            scan_container.clear()
            if not state['installations']:
                with scan_container:
                    ui.label(t('pages.delete_docs.no_docs_found', lang)).classes(
                        'text-secondary'
                    )
                return
            with scan_container:
                ui.label(t('pages.delete_docs.found_label', lang)).classes(
                    'font-medium mb-2'
                )
                for path in state['installations']:
                    label = (
                        t('pages.delete_docs.symlink', lang)
                        if path.is_symlink()
                        else t('pages.delete_docs.file', lang)
                    )
                    with ui.row().classes('items-center gap-2'):
                        ui.badge(label, color='info' if label == 'symlink' else 'grey')
                        ui.label(str(path)).classes('text-sm font-mono')

        ui.button(t('buttons.scan', lang), on_click=scan_docs, icon='search').props(
            'unelevated rounded'
        )

        def do_delete():
            from skillnir.remover import delete_docs

            if not state['installations']:
                ui.notify(
                    t('pages.delete_docs.no_docs_to_delete', lang), type='warning'
                )
                return
            target = Path(target_input.value).resolve()
            result = delete_docs(target)
            results_container.clear()
            with results_container:
                if result.error:
                    result_card(
                        results_container,
                        False,
                        t('pages.delete_docs.deletion_failed', lang),
                        error=result.error,
                    )
                else:
                    with (
                        ui.card()
                        .classes('w-full p-6 border-l-accent fade-in')
                        .style('border-left-color: #10b981')
                    ):
                        with ui.row().classes('items-center gap-3 mb-3'):
                            ui.icon('check_circle', color='positive').classes(
                                'text-2xl'
                            )
                            ui.label(
                                t('pages.delete_docs.deletion_complete', lang)
                            ).classes('text-xl font-bold')
                        ui.label(
                            t(
                                'pages.delete_docs.removed_files',
                                lang,
                                count=str(len(result.removed_files)),
                            )
                        ).classes('text-positive font-medium')
                        for path in result.removed_files:
                            ui.label(f'  - {path}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                        if result.cleaned_dirs:
                            ui.label(
                                t(
                                    'pages.delete_docs.cleaned_dirs',
                                    lang,
                                    count=str(len(result.cleaned_dirs)),
                                )
                            ).classes('text-secondary mt-2')
            scan_docs()

        ui.button(
            t('buttons.delete_docs', lang),
            on_click=do_delete,
            icon='delete_sweep',
        ).props('unelevated rounded color=negative')
