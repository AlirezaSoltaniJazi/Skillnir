"""AI interaction pages: Ask, Plan, and Check Skill."""

import asyncio
import time
from pathlib import Path

from nicegui import ui

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
            error=f'Exit code: {exit_code}',
        )

    with results_container:
        with ui.row().classes('gap-3 mt-4'):
            ui.button(
                'Try Again',
                on_click=lambda: ui.navigate.to(retry_route),
                icon='refresh',
            ).props('unelevated rounded')
            ui.button('Home', on_click=lambda: ui.navigate.to('/'), icon='home').props(
                'flat rounded'
            )

    play_notification(audio_el, sound_state)
    for c in controls:
        c.enable()


@ui.page('/ask')
async def page_ask():
    audio_el, sound_state = header()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Ask AI',
            'Ask a question about a project. AI answers without making changes.',
            icon='chat',
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
            question_input = (
                ui.textarea(
                    'Your question',
                    placeholder='e.g., How does the authentication module work?',
                )
                .classes('w-full max-w-xl')
                .props('rows=4 outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_ask():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            question = question_input.value.strip()
            if not question:
                ui.notify('Please enter a question.', type='warning')
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
                success_title='Answer Complete',
                fail_title='Ask Failed',
                retry_route='/ask',
            )

        ask_btn = ui.button(
            'Ask',
            on_click=do_ask,
            icon='chat',
        ).props('unelevated rounded color=positive')


@ui.page('/plan')
async def page_plan():
    audio_el, sound_state = header()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Plan',
            'Get a detailed implementation plan from AI for a task or feature.',
            icon='map',
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
            task_input = (
                ui.textarea(
                    'What do you need a plan for?',
                    placeholder='e.g., Add user authentication with JWT tokens',
                )
                .classes('w-full max-w-xl')
                .props('rows=4 outlined dense rounded')
            )

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_plan():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
                return
            task = task_input.value.strip()
            if not task:
                ui.notify('Please describe the task.', type='warning')
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
                success_title='Plan Complete',
                fail_title='Planning Failed',
                retry_route='/plan',
            )

        plan_btn = ui.button(
            'Create Plan',
            on_click=do_plan,
            icon='map',
        ).props('unelevated rounded color=positive')


@ui.page('/check-skill')
async def page_check_skill():
    audio_el, sound_state = header()

    from skillnir.backends import BACKENDS, build_subprocess_command, load_config

    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header(
            'Check Skill',
            'Run /skills via AI backend on a target project.',
            icon='fact_check',
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

        progress_container = ui.column().classes('w-full')
        results_container = ui.column().classes('w-full')

        async def do_check():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f'Directory not found: {target}', type='negative')
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
                success_title='Skill Check Complete',
                fail_title='Skill Check Failed',
                retry_route='/check-skill',
                max_log_lines=300,
            )

        run_btn = ui.button(
            'Run Check',
            on_click=do_check,
            icon='fact_check',
        ).props('unelevated rounded color=positive')
