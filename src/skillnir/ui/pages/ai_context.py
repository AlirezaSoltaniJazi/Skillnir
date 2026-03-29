"""AI context generation and deletion pages."""

import time
from pathlib import Path

from nicegui import ui

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

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Generate AI Docs',
            'Scan a project with AI and generate agents.md + .claude/claude.md',
            icon='auto_stories',
        )

        with ui.row().classes('items-center gap-2'):
            ui.icon(backend_info.icon, size='sm').classes('text-gray-400')
            ui.label(f'Using: {backend_info.name} ({config.model})').classes(
                'text-sm text-gray-400'
            )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            version_select = (
                ui.select(
                    label='Prompt version',
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
                ui.notify(f'Directory not found: {target}', type='negative')
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
                    results_container, True, 'Generation Complete', grid_data=grid
                )
            else:
                result_card(
                    results_container, False, 'Generation Failed', error=result.error
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        'Try Again',
                        on_click=lambda: ui.navigate.to('/generate-docs'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')

            play_notification(audio_el, sound_state)

        generate_btn = ui.button(
            'Generate AI Docs',
            on_click=do_generate,
            icon='auto_stories',
        ).props('unelevated rounded color=positive')


@ui.page('/generate-rule')
async def page_generate_rule():
    audio_el, sound_state = header()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Generate Rule',
            'Scan a project with AI and generate Cursor rule files (.mdc)',
            icon='gavel',
        )

        with ui.row().classes('items-center gap-2'):
            ui.icon(backend_info.icon, size='sm').classes('text-gray-400')
            ui.label(f'Using: {backend_info.name} ({config.model})').classes(
                'text-sm text-gray-400'
            )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            topic_input = (
                ui.textarea(
                    'Rule topic',
                    placeholder='e.g., error handling standards, React component patterns',
                )
                .classes('w-full max-w-xl')
                .props('rows=3 outlined dense rounded')
            )
            rule_version_select = (
                ui.select(
                    label='Prompt version',
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
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            rule_topic = topic_input.value.strip()
            if not rule_topic:
                ui.notify('Please enter a rule topic.', type='warning')
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
                    results_container, True, 'Rule Generation Complete', grid_data=grid
                )
            else:
                result_card(
                    results_container,
                    False,
                    'Rule Generation Failed',
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        'Try Again',
                        on_click=lambda: ui.navigate.to('/generate-rule'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')

            play_notification(audio_el, sound_state)

        generate_btn = ui.button(
            'Generate Rule',
            on_click=do_generate,
            icon='gavel',
        ).props('unelevated rounded color=positive')


@ui.page('/delete-docs')
def page_delete_docs():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Delete AI Docs',
            'Remove agents.md and its symlinks from a target project.',
            icon='delete_sweep',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
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
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            state['installations'] = find_docs_installations(target)
            results_container.clear()
            scan_container.clear()
            if not state['installations']:
                with scan_container:
                    ui.label('No AI docs found in target project.').classes(
                        'text-gray-400'
                    )
                return
            with scan_container:
                ui.label('Found:').classes('font-medium mb-2')
                for path in state['installations']:
                    label = 'symlink' if path.is_symlink() else 'file'
                    with ui.row().classes('items-center gap-2'):
                        ui.badge(label, color='info' if label == 'symlink' else 'grey')
                        ui.label(str(path)).classes('text-sm font-mono')

        ui.button('Scan', on_click=scan_docs, icon='search').props('unelevated rounded')

        def do_delete():
            from skillnir.remover import delete_docs

            if not state['installations']:
                ui.notify('No docs found to delete.', type='warning')
                return
            target = Path(target_input.value).resolve()
            result = delete_docs(target)
            results_container.clear()
            with results_container:
                if result.error:
                    result_card(
                        results_container,
                        False,
                        'Deletion Failed',
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
                            ui.label('Deletion Complete').classes('text-xl font-bold')
                        ui.label(
                            f'Removed {len(result.removed_files)} file(s)'
                        ).classes('text-positive font-medium')
                        for path in result.removed_files:
                            ui.label(f'  - {path}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                        if result.cleaned_dirs:
                            ui.label(
                                f'Cleaned {len(result.cleaned_dirs)} empty dir(s)'
                            ).classes('text-gray-400 mt-2')
            scan_docs()

        ui.button(
            'Delete Docs',
            on_click=do_delete,
            icon='delete_sweep',
        ).props('unelevated rounded color=negative')
