"""Template scaffolding pages for skills and docs."""

from pathlib import Path

from nicegui import ui

from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page('/init-skill')
def page_init_skill():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Init Skill',
            'Create a default skill scaffold with commented placeholder files.',
            icon='note_add',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            name_input = (
                ui.input('Skill name (lowercase, hyphens only)')
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            name_error = ui.label('').classes('text-red-500 hidden')

        with ui.card().classes('w-full p-4').props('flat bordered'):
            ui.label('Will create:').classes('font-medium mb-2')
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
                ui.notify(f'Directory not found: {target}', type='negative')
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
                            f'Skill scaffold created at {result.created_path}'
                        ).classes('text-positive font-medium')
                        for f in result.created_files:
                            ui.label(f'  + {f}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                else:
                    ui.label(f'Error: {result.error}').classes('text-red-400')

        ui.button(
            'Create Scaffold',
            on_click=do_create,
            icon='note_add',
        ).props('unelevated rounded color=positive')


@ui.page('/init-docs')
def page_init_docs():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Init AI Docs',
            'Create a default agents.md template with commented sections and symlinks for AI tools.',
            icon='description',
        )

        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        with ui.card().classes('w-full p-4').props('flat bordered'):
            ui.label('Will create:').classes('font-medium mb-2')
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
                ui.notify(f'Directory not found: {target}', type='negative')
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
                        ui.label('AI docs template created!').classes(
                            'text-positive font-medium'
                        )
                        for f in result.created_files:
                            ui.label(f'  + {f}').classes(
                                'text-sm text-green-400 font-mono'
                            )
                else:
                    ui.label(f'Error: {result.error}').classes('text-red-400')

        ui.button(
            'Create Docs Template',
            on_click=do_create,
            icon='description',
        ).props('unelevated rounded color=positive')
