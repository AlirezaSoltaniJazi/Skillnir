"""Skill generation page."""

import time
from pathlib import Path

from nicegui import ui

from skillnir.i18n import t, get_current_language
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
    lang = get_current_language()

    from skillnir.backends import BACKENDS, PROMPT_VERSION_LABELS, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.generate_skill.title', lang),
            t('pages.generate_skill.subtitle', lang),
            icon='psychology',
        )

        # ── Backend info ──
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

        # ── Form ──
        with ui.card().classes('w-full p-6').props('flat bordered'):
            target_input = (
                ui.input(
                    t('pages.generate_skill.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

            add_to_current_cb = ui.checkbox(
                t('pages.generate_skill.also_add_to_current', lang), value=True
            ).classes('hidden')

            def _on_target_change():
                target = Path(target_input.value).resolve()
                if target != Path.cwd().resolve():
                    add_to_current_cb.classes(remove='hidden')
                else:
                    add_to_current_cb.classes(add='hidden')

            target_input.on_value_change(lambda _: _on_target_change())

            name_input = (
                ui.input(
                    t('pages.generate_skill.project_name', lang),
                    value=Path.cwd().name,
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

            from skillnir.skill_generator import SCOPE_LABELS

            with ui.row().classes('gap-4'):
                scope_select = (
                    ui.select(
                        label=t('pages.generate_skill.skill_scope', lang),
                        options={k: v for k, v in SCOPE_LABELS.items()},
                        value='backend',
                    )
                    .classes('w-64')
                    .props('outlined dense rounded')
                )

                skill_version_select = (
                    ui.select(
                        label=t('pages.generate_skill.prompt_version', lang),
                        options=PROMPT_VERSION_LABELS,
                        value=config.prompt_version,
                    )
                    .classes('w-64')
                    .props('outlined dense rounded')
                )

            skill_name_label = ui.label(
                t(
                    'pages.generate_skill.skill_name_preview',
                    lang,
                    name=f'{Path.cwd().name}-backend',
                )
            ).classes('text-lg font-medium gradient-text')

            def update_preview():
                from skillnir.skill_generator import to_camel_case

                name = name_input.value or Path(target_input.value).name
                skill_name_label.text = t(
                    'pages.generate_skill.skill_name_preview',
                    lang,
                    name=to_camel_case(name),
                )

            target_input.on_value_change(lambda _: update_preview())
            name_input.on_value_change(lambda _: update_preview())

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
                    t('pages.generate_skill.grid_skill_name', lang): result.skill_name,
                    t('pages.generate_skill.grid_target_skill_md', lang): str(
                        result.target_skill_path
                    ),
                }
                if result.source_skill_path:
                    grid[t('pages.generate_skill.grid_source_skill_md', lang)] = str(
                        result.source_skill_path
                    )
                grid[t('pages.generate_skill.grid_duration', lang)] = format_duration(
                    secs
                )
                grid[t('pages.generate_skill.grid_tools_used', lang)] = str(
                    counters['tools']
                )
                if result.backend_used:
                    grid[t('pages.generate_skill.grid_backend', lang)] = (
                        BACKENDS[result.backend_used].name
                        if result.backend_used in BACKENDS
                        else result.backend_used.value
                    )
                result_card(
                    results_container,
                    success=True,
                    title=t('pages.generate_skill.result_success_title', lang),
                    grid_data=grid,
                    footer_text=t('pages.generate_skill.result_footer', lang),
                )
            else:
                result_card(
                    results_container,
                    success=False,
                    title=t('pages.generate_skill.result_fail_title', lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes('gap-3 mt-4'):
                    ui.button(
                        t('buttons.try_again', lang),
                        on_click=lambda: ui.navigate.to('/generate-skill'),
                        icon='refresh',
                    ).props('unelevated rounded')
                    ui.button(
                        t('buttons.home', lang),
                        on_click=lambda: ui.navigate.to('/'),
                        icon='home',
                    ).props('flat rounded')

            play_notification(audio_el, sound_state)

        generate_btn = ui.button(
            t('buttons.generate_skill', lang),
            on_click=do_generate,
            icon='psychology',
        ).props('unelevated rounded color=positive')
