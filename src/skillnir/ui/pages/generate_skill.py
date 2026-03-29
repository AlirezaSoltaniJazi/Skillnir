"""Skill generation page."""

import time
from pathlib import Path

from nicegui import ui

from skillnir.syncer import sync_skill
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    make_on_progress,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.layout import header, play_notification


@ui.page('/generate-skill')
async def page_generate_skill():
    audio_el, sound_state = header()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Generate Skill',
            'Scan a project with AI and generate a domain-specific SKILL.md',
            icon='psychology',
        )

        # ── Backend info ──
        with ui.row().classes('items-center gap-2'):
            ui.icon(backend_info.icon, size='sm').classes('text-gray-400')
            ui.label(f'Using: {backend_info.name} ({config.model})').classes(
                'text-sm text-gray-400'
            )

        # ── Form ──
        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input('Target project root', value=str(Path.cwd()))
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

            add_to_current_cb = ui.checkbox(
                'Also add skill to current project', value=True
            ).classes('hidden')

            def _on_target_change():
                target = Path(target_input.value).resolve()
                if target != Path.cwd().resolve():
                    add_to_current_cb.classes(remove='hidden')
                else:
                    add_to_current_cb.classes(add='hidden')

            target_input.on_value_change(lambda _: _on_target_change())

            name_input = (
                ui.input('Project name', value=Path.cwd().name)
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

            from skillnir.skill_generator import SCOPE_LABELS

            with ui.row().classes('gap-4'):
                scope_select = (
                    ui.select(
                        label='Skill scope',
                        options={k: v for k, v in SCOPE_LABELS.items()},
                        value='backend',
                    )
                    .classes('w-64')
                    .props('outlined dense rounded')
                )

                skill_version_select = (
                    ui.select(
                        label='Prompt version',
                        options=PROMPT_VERSION_LABELS,
                        value=config.prompt_version,
                    )
                    .classes('w-64')
                    .props('outlined dense rounded')
                )

            skill_name_label = ui.label(
                f'Skill name: {Path.cwd().name}-backend'
            ).classes('text-lg font-medium gradient-text')

            def update_preview():
                from skillnir.skill_generator import to_camel_case

                name = name_input.value or Path(target_input.value).name
                skill_name_label.text = f'Skill name: {to_camel_case(name)}'

            target_input.on_value_change(lambda _: update_preview())
            name_input.on_value_change(lambda _: update_preview())

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_generate():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
                return

            project_name = name_input.value or target.name
            scope = scope_select.value

            generate_btn.disable()
            target_input.disable()
            name_input.disable()
            scope_select.disable()
            skill_version_select.disable()
            results_container.clear()

            start_time = time.time()
            counters = {'tools': 0, 'lines': 0}

            refs = progress_panel(progress_container)
            timer_ctl = start_elapsed_timer(refs, start_time)
            on_progress = make_on_progress(refs, counters)

            from skillnir.skill_generator import generate_skill

            result = await generate_skill(
                target,
                project_name,
                scope,
                on_progress=on_progress,
                prompt_version_override=skill_version_select.value,
            )

            timer_ctl['active'] = False
            secs = int(time.time() - start_time)
            progress_container.clear()

            generate_btn.enable()
            target_input.enable()
            name_input.enable()
            scope_select.enable()
            skill_version_select.enable()

            if result.success:
                # Sync to current project if requested
                if add_to_current_cb.value and target != Path.cwd().resolve():
                    sync_skill(
                        target / '.data' / 'skills',
                        Path.cwd() / '.data' / 'skills',
                        result.skill_name,
                    )

                grid = {
                    'Skill name': result.skill_name,
                    'Target SKILL.md': str(result.target_skill_path),
                }
                if result.source_skill_path:
                    grid['Source SKILL.md'] = str(result.source_skill_path)
                grid['Duration'] = format_duration(secs)
                grid['Tools used'] = str(counters['tools'])
                if result.backend_used:
                    grid['Backend'] = (
                        BACKENDS[result.backend_used].name
                        if result.backend_used in BACKENDS
                        else result.backend_used.value
                    )
                result_card(
                    results_container,
                    success=True,
                    title='Skill Generation Complete',
                    grid_data=grid,
                    footer_text="Run 'skillnir install' to inject this skill into AI tools.",
                )
            else:
                result_card(
                    results_container,
                    success=False,
                    title='Skill Generation Failed',
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        'Try Again',
                        on_click=lambda: ui.navigate.to('/generate-skill'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        'Home', on_click=lambda: ui.navigate.to('/'), icon='home'
                    ).props('flat rounded')

            play_notification(audio_el, sound_state)

        generate_btn = ui.button(
            'Generate Skill',
            on_click=do_generate,
            icon='psychology',
        ).props('unelevated rounded color=positive')
