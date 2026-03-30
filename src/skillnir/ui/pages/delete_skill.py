"""Delete skills page."""

from pathlib import Path

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.remover import delete_skill, find_skill_installations
from skillnir.skills import discover_skills
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/delete-skill')
def page_delete_skill():
    lang = get_current_language()
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.delete_skill.title', lang),
            t('pages.delete_skill.subtitle', lang),
            icon='delete',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input(
                    t('pages.delete_skill.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        skill_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        state: dict = {'skills': [], 'selected': []}

        def scan_skills():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t(
                        'messages.directory_not_found',
                        lang,
                        path=str(target),
                    ),
                    type='negative',
                )
                return
            state['skills'] = discover_skills(target)
            state['selected'] = []
            results_container.clear()
            skill_container.clear()
            if not state['skills']:
                with skill_container:
                    ui.label(t('pages.delete_skill.no_skills_found', lang)).classes(
                        'text-secondary'
                    )
                return
            with skill_container:
                ui.label(
                    t(
                        'pages.delete_skill.found_skills',
                        lang,
                        count=str(len(state['skills'])),
                    )
                ).classes('font-medium mb-2')
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
                                    + t(
                                        'pages.delete_skill.tool_installations',
                                        lang,
                                        count=str(len(installations)),
                                    )
                                ).classes('text-secondary text-sm')

        ui.button(t('buttons.scan', lang), on_click=scan_skills, icon='search').props(
            'unelevated rounded'
        )

        delete_data_cb = ui.checkbox(
            t('pages.delete_skill.also_delete_data', lang), value=False
        )

        def do_delete():
            if not state['selected']:
                ui.notify(
                    t('pages.delete_skill.select_at_least_one', lang),
                    type='warning',
                )
                return
            target = Path(target_input.value).resolve()
            results_container.clear()
            with results_container:
                with (
                    ui.card()
                    .classes('w-full p-6 border-l-accent fade-in')
                    .style('border-left-color: #ef4444')
                ):
                    ui.label(t('pages.delete_skill.deletion_report', lang)).classes(
                        'text-xl font-bold mb-3'
                    )
                    for skill in state['selected']:
                        result = delete_skill(
                            target, skill.dir_name, delete_data=delete_data_cb.value
                        )
                        if result.error:
                            with ui.row().classes('items-center gap-2'):
                                ui.badge(
                                    t('pages.delete_skill.error_badge', lang),
                                    color='negative',
                                )
                                ui.label(
                                    f'{result.skill_name}: {result.error}'
                                ).classes('text-red-400')
                        else:
                            with ui.row().classes('items-center gap-2'):
                                ui.badge(
                                    t('pages.delete_skill.deleted_badge', lang),
                                    color='positive',
                                )
                                ui.label(result.skill_name).classes('font-medium')
                                ui.label(
                                    t(
                                        'pages.delete_skill.deleted_summary',
                                        lang,
                                        symlinks=str(len(result.removed_symlinks)),
                                        dirs=str(len(result.cleaned_dirs)),
                                    )
                                ).classes('text-secondary text-sm')
            scan_skills()

        ui.button(
            t('buttons.delete_selected', lang),
            on_click=do_delete,
            icon='delete',
        ).props('unelevated rounded color=negative')
