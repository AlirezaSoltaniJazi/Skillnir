"""AI interaction pages: Ask, Plan, and Check Skill."""

import asyncio
import time
from pathlib import Path

from nicegui import ui

from skillnir.i18n import t, get_current_language
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    make_on_progress,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.layout import header, play_notification


async def _run_subprocess_page(
    *,
    audio_el,
    sound_state: dict,
    backend_info,
    config,
    target: Path,
    cmd: list[str],
    progress_container,
    results_container,
    controls: list,
    success_title: str,
    fail_title: str,
    retry_route: str,
    max_log_lines: int = 500,
):
    """Shared async subprocess execution for ask/plan/check pages."""
    import subprocess

    for c in controls:
        c.disable()
    results_container.clear()

    start_time = time.time()
    counters = {'tools': 0, 'lines': 0}
    refs = progress_panel(progress_container, max_log_lines=max_log_lines)
    timer_ctl = start_elapsed_timer(refs, start_time)
    on_progress = make_on_progress(refs, counters)

    from skillnir.generator import _emit

    exit_code = None
    try:
        from skillnir.backends import parse_stream_line

        loop = asyncio.get_event_loop()

        def _run():
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=str(target),
            )
            for line in proc.stdout:
                parse_stream_line(config.backend, line, on_progress)
            proc.wait(timeout=600)
            return proc.returncode

        exit_code = await loop.run_in_executor(None, _run)
    except Exception as e:
        _emit(on_progress, 'error', str(e))

    timer_ctl['active'] = False
    progress_container.clear()

    if exit_code == 0:
        result_card(results_container, True, success_title)
    else:
        result_card(
            results_container,
            False,
            fail_title,
            error=t('messages.exit_code', code=str(exit_code)),
        )

    lang = get_current_language()
    with results_container:
        with ui.row().classes('gap-3 mt-4'):
            ui.button(
                t('buttons.try_again', lang),
                on_click=lambda: ui.navigate.to(retry_route),
                icon='refresh',
            ).props('unelevated rounded')
            ui.button(
                t('buttons.home', lang),
                on_click=lambda: ui.navigate.to('/'),
                icon='home',
            ).props('flat rounded')

    play_notification(audio_el, sound_state)
    for c in controls:
        c.enable()


@ui.page('/ask')
async def page_ask():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.ask.title', lang),
            t('pages.ask.subtitle', lang),
            icon='chat',
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
                    t('pages.ask.target_project_root', lang), value=str(Path.cwd())
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            question_input = (
                ui.textarea(
                    t('pages.ask.your_question', lang),
                    placeholder=t('pages.ask.question_placeholder', lang),
                )
                .classes('w-full max-w-xl')
                .props('rows=4 outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_ask():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return
            question = question_input.value.strip()
            if not question:
                ui.notify(t('pages.ask.enter_question', lang), type='warning')
                return

            cmd = build_subprocess_command(
                config.backend,
                question,
                model=config.model,
                mode='ask',
            )
            await _run_subprocess_page(
                audio_el=audio_el,
                sound_state=sound_state,
                backend_info=backend_info,
                config=config,
                target=target,
                cmd=cmd,
                progress_container=progress_container,
                results_container=results_container,
                controls=[ask_btn, target_input, question_input],
                success_title=t('pages.ask.result_success_title', lang),
                fail_title=t('pages.ask.result_fail_title', lang),
                retry_route='/ask',
            )

        ask_btn = ui.button(
            t('buttons.ask', lang),
            on_click=do_ask,
            icon='chat',
        ).props('unelevated rounded color=positive')


@ui.page('/plan')
async def page_plan():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.plan.title', lang),
            t('pages.plan.subtitle', lang),
            icon='map',
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
                    t('pages.plan.target_project_root', lang), value=str(Path.cwd())
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )
            task_input = (
                ui.textarea(
                    t('pages.plan.task_input_label', lang),
                    placeholder=t('pages.plan.task_placeholder', lang),
                )
                .classes('w-full max-w-xl')
                .props('rows=4 outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_plan():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return
            task = task_input.value.strip()
            if not task:
                ui.notify(t('pages.plan.describe_task', lang), type='warning')
                return

            cmd = build_subprocess_command(
                config.backend,
                task,
                model=config.model,
                mode='plan',
            )
            await _run_subprocess_page(
                audio_el=audio_el,
                sound_state=sound_state,
                backend_info=backend_info,
                config=config,
                target=target,
                cmd=cmd,
                progress_container=progress_container,
                results_container=results_container,
                controls=[plan_btn, target_input, task_input],
                success_title=t('pages.plan.result_success_title', lang),
                fail_title=t('pages.plan.result_fail_title', lang),
                retry_route='/plan',
            )

        plan_btn = ui.button(
            t('buttons.create_plan', lang),
            on_click=do_plan,
            icon='map',
        ).props('unelevated rounded color=positive')


@ui.page('/check-skill')
async def page_check_skill():
    audio_el, sound_state = header()
    lang = get_current_language()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            t('pages.check_skill.title', lang),
            t('pages.check_skill.subtitle', lang),
            icon='fact_check',
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
                    t('pages.check_skill.target_project_root', lang),
                    value=str(Path.cwd()),
                )
                .classes('w-full max-w-xl')
                .props('outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_check():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(
                    t('messages.directory_not_found', lang, path=str(target)),
                    type='negative',
                )
                return

            cmd = build_subprocess_command(
                config.backend,
                backend_info.slash_commands.get('skills', '/skills'),
                model=config.model,
            )
            await _run_subprocess_page(
                audio_el=audio_el,
                sound_state=sound_state,
                backend_info=backend_info,
                config=config,
                target=target,
                cmd=cmd,
                progress_container=progress_container,
                results_container=results_container,
                controls=[run_btn, target_input],
                success_title=t('pages.check_skill.result_success_title', lang),
                fail_title=t('pages.check_skill.result_fail_title', lang),
                retry_route='/check-skill',
                max_log_lines=300,
            )

        run_btn = ui.button(
            t('buttons.run_check', lang),
            on_click=do_check,
            icon='fact_check',
        ).props('unelevated rounded color=positive')
