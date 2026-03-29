"""Skill install, update, and browser pages for the NiceGUI web interface."""

from pathlib import Path

from nicegui import ui

from skillnir.injector import inject_skill
from skillnir.skills import discover_skills_from_dir
from skillnir.syncer import get_source_skills_dir, sync_skill, sync_skills
from skillnir.tools import AUTO_INJECT_TOOL
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import (
    SORT_MODES,
    _count_skill_files,
    build_confirm,
    build_results,
    build_skill_cards,
    build_sync_report,
    build_tool_table,
    header,
    play_notification,
)


@ui.page('/install')
def page_install():
    audio_el, sound_state = header()

    state = {
        'target_root': str(Path.cwd()),
        'skills': [],
        'selected_skills': [],
        'sort_mode': 'default',
        'selected_tools': [],
        'injection_results': None,
    }

    default_source = str(get_source_skills_dir())

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Install Skills',
            'Inject AI coding skills into your project.',
            icon='download',
        )

        with ui.stepper().props('vertical animated').classes('w-full') as stepper:

            # Step 1: Target Project & Source
            with ui.step('Target & Source'):
                ui.label('Enter the root path of the target project.').classes(
                    'text-gray-400 mb-2'
                )
                target_input = (
                    ui.input('Project root', value=state['target_root'])
                    .classes('w-full max-w-xl')
                    .props('outlined dense rounded')
                )
                ui.label(
                    'Source skills path (where to fetch generated skills from).'
                ).classes('text-gray-400 mb-2 mt-4')
                source_input = (
                    ui.input('Source skills path', value=default_source)
                    .classes('w-full max-w-xl')
                    .props('outlined dense rounded')
                )
                target_error = ui.label('').classes('text-red-500 hidden')

                def validate_and_next():
                    path = Path(target_input.value).resolve()
                    if not path.is_dir():
                        target_error.text = f'Directory not found: {path}'
                        target_error.classes(remove='hidden')
                        return
                    src = Path(source_input.value).resolve()
                    if not src.is_dir():
                        target_error.text = f'Source directory not found: {src}'
                        target_error.classes(remove='hidden')
                        return
                    target_error.classes(add='hidden')
                    state['target_root'] = str(path)
                    state['skills'] = discover_skills_from_dir(src)
                    if not state['skills']:
                        target_error.text = 'No skills found in source.'
                        target_error.classes(remove='hidden')
                        return
                    build_skill_cards(skill_container, state, stepper, tool_container)
                    stepper.next()

                with ui.row().classes('mt-4'):
                    ui.button(
                        'Next', on_click=validate_and_next, icon='arrow_forward'
                    ).props('unelevated rounded')

            # Step 2: Select Skills
            with ui.step('Select Skills'):
                ui.label('Choose skills to inject (select one or more).').classes(
                    'text-gray-400 mb-2'
                )
                skill_container = ui.column().classes('w-full gap-3')

            # Step 3: Select Tools
            with ui.step('Select Tools'):
                ui.label('Choose AI tools to inject symlinks into.').classes(
                    'text-gray-400 mb-2'
                )
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.label('Sort by:').classes('font-medium')
                    sort_select = (
                        ui.select(options=SORT_MODES, value='default')
                        .classes('w-48')
                        .props('outlined dense rounded')
                    )

                    def on_sort_change(e):
                        state['sort_mode'] = e.value
                        build_tool_table(tool_container, state)

                    sort_select.on_value_change(on_sort_change)

                tool_container = ui.column().classes('w-full')

                with ui.row().classes('mt-4 gap-2'):
                    ui.button(
                        'Back', on_click=stepper.previous, icon='arrow_back'
                    ).props('flat rounded')

                    def go_to_confirm():
                        if not state['selected_tools']:
                            ui.notify('Select at least one tool.', type='warning')
                            return
                        build_confirm(confirm_container, state)
                        stepper.next()

                    ui.button(
                        'Next — Confirm',
                        on_click=go_to_confirm,
                        icon='arrow_forward',
                    ).props('unelevated rounded')

            # Step 4: Confirm & Execute
            with ui.step('Confirm & Execute'):
                confirm_container = ui.column().classes('w-full')
                execute_progress_container = ui.column().classes('w-full')

                with ui.row().classes('mt-4 gap-2'):
                    ui.button(
                        'Back', on_click=stepper.previous, icon='arrow_back'
                    ).props('flat rounded')

                    def do_execute():
                        execute_btn.disable()
                        execute_progress_container.clear()
                        with execute_progress_container:
                            with ui.row().classes('items-center gap-3 mt-2'):
                                ui.spinner('dots', size='lg')
                                progress_label = ui.label('Starting...')

                        target_root = Path(state['target_root'])
                        total = len(state['selected_skills'])

                        # Phase 1: Sync
                        source_dir_inner = Path(source_input.value).resolve()
                        target_skills_dir = target_root / '.data' / 'skills'
                        for i, s in enumerate(state['selected_skills'], 1):
                            progress_label.text = (
                                f'Syncing skill {i}/{total}: {s.name}...'
                            )
                            result = sync_skill(
                                source_dir_inner, target_skills_dir, s.dir_name
                            )
                            if result.action == 'copied':
                                ui.notify(
                                    f"'{result.skill_name}' v{result.source_version} — copied",
                                    type='positive',
                                )
                            elif result.action == 'updated':
                                ui.notify(
                                    f"'{result.skill_name}' — updated", type='info'
                                )

                        # Phase 2: Inject
                        all_tools = [AUTO_INJECT_TOOL] + state['selected_tools']
                        all_results = []
                        for i, skill in enumerate(state['selected_skills'], 1):
                            progress_label.text = (
                                f'Injecting skill {i}/{total}: {skill.name}...'
                            )
                            results = inject_skill(target_root, skill, all_tools)
                            all_results.append((skill, results))

                        execute_progress_container.clear()
                        execute_btn.enable()
                        state['injection_results'] = all_results
                        build_results(results_container, all_results)
                        play_notification(audio_el, sound_state)
                        stepper.next()

                    execute_btn = ui.button(
                        'Execute',
                        on_click=do_execute,
                        icon='rocket_launch',
                    ).props('unelevated rounded color=positive')

            # Step 5: Results
            with ui.step('Results'):
                results_container = ui.column().classes('w-full')
                with ui.row().classes('mt-4 gap-2'):
                    ui.button(
                        'Start Over',
                        on_click=lambda: ui.navigate.to('/install'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')


@ui.page('/update')
def page_update():
    audio_el, sound_state = header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Update Skills',
            'Sync all skills from source to a target project.',
            icon='sync',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        update_progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        def do_update():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            update_btn.disable()
            results_container.clear()
            update_progress_container.clear()
            with update_progress_container:
                with ui.row().classes('items-center gap-3 mt-2'):
                    ui.spinner('dots', size='lg')
                    ui.label('Updating skills...')

            source_dir = get_source_skills_dir()
            target_skills_dir = target / '.data' / 'skills'
            sync_results = sync_skills(source_dir, target_skills_dir)

            update_progress_container.clear()
            update_btn.enable()
            build_sync_report(results_container, sync_results)
            play_notification(audio_el, sound_state)
            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        'Try Again',
                        on_click=lambda: ui.navigate.to('/update'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')

        update_btn = ui.button(
            'Update All Skills',
            on_click=do_update,
            icon='sync',
        ).props('unelevated rounded color=positive')


@ui.page('/skills')
def page_skills():
    _audio, _snd = header()
    source_dir = get_source_skills_dir()
    skills = discover_skills(source_dir.parent.parent)

    with ui.column().classes('w-full max-w-6xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Skills Library', f'{len(skills)} skills available', icon='inventory_2'
        )

        # ── Search ──
        search_input = (
            ui.input(
                placeholder='Search skills...',
            )
            .classes('w-64')
            .props('outlined dense rounded clearable')
        )

        skills_grid = ui.element('div').classes(
            'w-full grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
        )

        def _render_skills(query: str = ''):
            skills_grid.clear()
            q = query.lower()
            filtered = (
                [s for s in skills if q in s.name.lower() or q in s.description.lower()]
                if q
                else skills
            )
            with skills_grid:
                for skill in filtered:
                    file_count = _count_skill_files(skill)
                    with ui.card().classes('p-5 card-hover'):
                        with ui.row().classes('items-center gap-2 mb-3'):
                            ui.icon('extension', color='primary').classes('text-xl')
                            ui.label(skill.name).classes('text-lg font-bold')
                        with ui.row().classes('gap-2 mb-3'):
                            ui.badge(f'v{skill.version}', color='primary').props(
                                'rounded'
                            )
                            ui.badge(f'{file_count} files', color='grey').props(
                                'rounded'
                            )
                        ui.label(skill.description).classes(
                            'text-sm text-gray-400 mb-2'
                        )
                        ui.label(str(skill.path)).classes(
                            'text-gray-600 text-xs font-mono'
                        )

                        skill_md_path = skill.path / 'SKILL.md'
                        if skill_md_path.exists():

                            def show_skill_md(path=skill_md_path, name=skill.name):
                                try:
                                    content = path.read_text(encoding='utf-8')
                                    with (
                                        ui.dialog() as dlg,
                                        ui.card().classes(
                                            'w-full max-w-3xl max-h-[80vh] p-6 rounded-xl'
                                        ),
                                    ):
                                        with ui.row().classes(
                                            'items-center justify-between w-full mb-3'
                                        ):
                                            ui.label(f'{name} — SKILL.md').classes(
                                                'text-lg font-bold'
                                            )
                                            ui.button(
                                                icon='close', on_click=dlg.close
                                            ).props('flat round dense')
                                        ui.markdown(content).classes(
                                            'overflow-auto max-h-[60vh]'
                                        )
                                    dlg.open()
                                except Exception as e:
                                    ui.notify(
                                        f'Error reading SKILL.md: {e}', type='negative'
                                    )

                            ui.button(
                                'View SKILL.md',
                                on_click=show_skill_md,
                                icon='description',
                            ).props('flat dense rounded').classes('mt-2')
                        else:
                            ui.button('SKILL.md not found', icon='error_outline').props(
                                'flat dense disabled'
                            ).classes('mt-2 text-gray-600')

        _render_skills()
        search_input.on_value_change(lambda e: _render_skills(e.value or ''))
