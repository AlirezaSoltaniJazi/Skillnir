"""Template scaffolding pages for skills and docs."""

from pathlib import Path

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/init-skill')
def page_init_skill():
    lang = get_current_language()
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.init_skill.title', lang),
            t('pages.init_skill.subtitle', lang),
            icon='note_add',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input(
                    t('pages.init_skill.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            name_input = (
                ui.input(t('pages.init_skill.skill_name_label', lang))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            name_error = ui.label('').classes('text-red-500 hidden')

        with ui.card().classes('w-full p-4').props('flat bordered'):
            ui.label(t('pages.init_skill.will_create', lang)).classes(
                'font-medium mb-2'
            )
            ui.code(
                'skill-name/\n'
                '├── SKILL.md       (main skill definition)\n'
                '├── INJECT.md      (always-loaded quick reference)\n'
                '├── references/    (supplemental docs)\n'
                '├── scripts/       (executable scripts)\n'
                '└── assets/        (static resources)\n',
                language='text',
            ).classes('w-full')

        results_container = ui.column().classes('w-full')

        def do_create():
            from skillnir.scaffold import init_skill, validate_skill_name

            name = name_input.value.strip()
            error = validate_skill_name(name)
            if error:
                name_error.text = error
                name_error.classes(remove='hidden')
                return
            name_error.classes(add='hidden')

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

            result = init_skill(target, name)
            results_container.clear()
            with results_container:
                if result.success:
                    with (
                        ui.card()
                        .classes('w-full p-5 border-l-accent fade-in')
                        .style('border-left-color: #10b981')
                    ):
                        ui.label(
                            t(
                                'pages.init_skill.scaffold_created',
                                lang,
                                path=str(result.created_path),
                            )
                        ).classes('text-positive font-medium')
                        for f in result.created_files:
                            ui.label(f'  + {f}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                else:
                    ui.label(
                        t(
                            'pages.init_skill.error_prefix',
                            lang,
                            error=result.error,
                        )
                    ).classes('text-red-400')

        ui.button(
            t('buttons.create_scaffold', lang),
            on_click=do_create,
            icon='note_add',
        ).props('unelevated rounded color=positive')


@ui.page('/init-docs')
def page_init_docs():
    lang = get_current_language()
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.init_docs.title', lang),
            t('pages.init_docs.subtitle', lang),
            icon='description',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input(
                    t('pages.init_docs.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        with ui.card().classes('w-full p-4').props('flat bordered'):
            ui.label(t('pages.init_docs.will_create', lang)).classes('font-medium mb-2')
            ui.code(
                'project/\n'
                '├── agents.md                          (template)\n'
                '├── .claude/claude.md                  (symlink → ../agents.md)\n'
                '└── .github/copilot-instructions.md    (symlink → ../agents.md)\n',
                language='text',
            ).classes('w-full')

        results_container = ui.column().classes('w-full')

        def do_create():
            from skillnir.scaffold import init_docs

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

            result = init_docs(target)
            results_container.clear()
            with results_container:
                if result.success:
                    with (
                        ui.card()
                        .classes('w-full p-5 border-l-accent fade-in')
                        .style('border-left-color: #10b981')
                    ):
                        ui.label(t('pages.init_docs.docs_created', lang)).classes(
                            'text-positive font-medium'
                        )
                        for f in result.created_files:
                            ui.label(f'  + {f}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                else:
                    ui.label(
                        t(
                            'pages.init_docs.error_prefix',
                            lang,
                            error=result.error,
                        )
                    ).classes('text-red-400')

        ui.button(
            t('buttons.create_docs_template', lang),
            on_click=do_create,
            icon='description',
        ).props('unelevated rounded color=positive')
