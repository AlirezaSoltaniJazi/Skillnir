"""Delete skills page."""

from pathlib import Path

from nicegui import ui

from skillnir.remover import delete_skill, find_skill_installations
from skillnir.skills import discover_skills
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/delete-skill')
def page_delete_skill():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Delete Skills',
            'Remove skill(s) from a target project, including symlinks in all tool directories.',
            icon='delete',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        skill_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        state: dict = {'skills': [], 'selected': []}

        def scan_skills():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            state['skills'] = discover_skills(target)
            state['selected'] = []
            results_container.clear()
            skill_container.clear()
            if not state['skills']:
                with skill_container:
                    ui.label('No skills found in target project.').classes(
                        'text-gray-400'
                    )
                return
            with skill_container:
                ui.label(f"Found {len(state['skills'])} skill(s):").classes(
                    'font-medium mb-2'
                )
                for skill in state['skills']:
                    target_root = Path(target_input.value).resolve()
                    installations = find_skill_installations(
                        target_root, skill.dir_name
                    )
                    with ui.card().classes('w-full px-5 py-3 card-hover'):
                        with ui.row().classes('items-center w-full gap-4'):
                            cb = ui.checkbox(value=False)

                            def on_toggle(e, s=skill):
                                if e.value:
                                    if s not in state['selected']:
                                        state['selected'].append(s)
                                else:
                                    state['selected'] = [
                                        x for x in state['selected'] if x.name != s.name
                                    ]

                            cb.on_value_change(on_toggle)
                            with ui.column().classes('flex-1 gap-0'):
                                ui.label(skill.name).classes('font-bold')
                                ui.label(
                                    f'v{skill.version} · '
                                    f'{len(installations)} tool installation(s)'
                                ).classes('text-gray-400 text-sm')

        ui.button('Scan', on_click=scan_skills, icon='search').props(
            'unelevated rounded'
        )

        delete_data_cb = ui.checkbox(
            'Also delete skill data from .data/skills/', value=False
        )

        def do_delete():
            if not state['selected']:
                ui.notify('Select at least one skill.', type='warning')
                return
            target = Path(target_input.value).resolve()
            results_container.clear()
            with results_container:
                with (
                    ui.card()
                    .classes('w-full p-6 border-l-accent fade-in')
                    .style('border-left-color: #ef4444')
                ):
                    ui.label('Deletion Report').classes('text-xl font-bold mb-3')
                    for skill in state['selected']:
                        result = delete_skill(
                            target, skill.dir_name, delete_data=delete_data_cb.value
                        )
                        if result.error:
                            with ui.row().classes('items-center gap-2'):
                                ui.badge('error', color='negative')
                                ui.label(
                                    f'{result.skill_name}: {result.error}'
                                ).classes('text-red-400')
                        else:
                            with ui.row().classes('items-center gap-2'):
                                ui.badge('deleted', color='positive')
                                ui.label(result.skill_name).classes('font-medium')
                                ui.label(
                                    f'({len(result.removed_symlinks)} symlinks, '
                                    f'{len(result.cleaned_dirs)} dirs cleaned)'
                                ).classes('text-gray-400 text-sm')
            scan_skills()

        ui.button(
            'Delete Selected',
            on_click=do_delete,
            icon='delete',
        ).props('unelevated rounded color=negative')
