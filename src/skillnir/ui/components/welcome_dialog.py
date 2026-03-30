"""Welcome popup and CLI installation guide dialogs."""

_CLI_SETUP_INFO: tuple[dict, ...] = (
    {
        'name': 'Claude Code',
        'icon': 'smart_toy',
        'install': 'npm install -g @anthropic-ai/claude-code',
        'install_alt': 'brew install claude-code',
        'login': 'claude login',
        'verify': 'claude --version',
        'notes': 'Requires Node.js 18+. You can also install via Homebrew.',
    },
    {
        'name': 'Cursor Agent',
        'icon': 'code',
        'install': 'npm install -g @anthropic-ai/cursor-agent',
        'install_alt': 'Also available via Cursor IDE (ships with the IDE)',
        'login': 'agent login',
        'verify': 'agent --version',
        'notes': 'Requires Node.js 18+. Can also be used through the Cursor IDE.',
    },
    {
        'name': 'Gemini CLI',
        'icon': 'diamond',
        'install': 'npm install -g @anthropic-ai/gemini-cli',
        'install_alt': None,
        'login': 'gemini login',
        'verify': 'gemini --version',
        'notes': 'Requires Node.js 18+ and a Google AI account.',
    },
    {
        'name': 'GitHub Copilot',
        'icon': 'hub',
        'install': 'npm install -g @anthropic-ai/copilot-cli',
        'install_alt': None,
        'login': 'copilot login',
        'verify': 'copilot --version',
        'notes': 'Requires a GitHub account with Copilot access.',
    },
)


def _cli_install_content() -> None:
    """Render per-backend CLI install/login/verify guides as expansion panels."""
    from nicegui import ui

    for info in _CLI_SETUP_INFO:
        with ui.expansion(info['name'], icon=info['icon']).classes('w-full'):
            with ui.column().classes('gap-2 w-full'):
                ui.label('Install').classes('text-sm font-bold text-secondary')
                ui.code(info['install']).classes('text-sm w-full')
                if info['install_alt']:
                    ui.label('or').classes('text-xs text-secondary')
                    ui.code(info['install_alt']).classes('text-sm w-full')

                ui.label('Login').classes('text-sm font-bold text-secondary mt-2')
                ui.code(info['login']).classes('text-sm w-full')

                ui.label('Verify').classes('text-sm font-bold text-secondary mt-2')
                ui.code(info['verify']).classes('text-sm w-full')

                if info['notes']:
                    ui.label(info['notes']).classes(
                        'text-xs text-secondary italic mt-1'
                    )


async def show_welcome_dialog() -> None:
    """Show a first-visit welcome popup. Skips if user dismissed it before."""
    from nicegui import ui

    try:
        dismissed = await ui.run_javascript(
            'localStorage.getItem("skillnir_welcome_dismissed")',
            timeout=3.0,
        )
        if dismissed == 'true':
            return
    except TimeoutError:
        return

    dont_show = {'checked': False}

    with (
        ui.dialog() as dlg,
        ui.card().classes('p-6 min-w-[540px] max-w-[640px] rounded-xl'),
    ):
        with ui.column().classes('items-center gap-1 w-full mb-2'):
            ui.icon('auto_fix_high', color='primary').classes('text-4xl')
            ui.label('Welcome to Skillnir').classes('text-2xl font-bold gradient-text')
        ui.label(
            'Skillnir orchestrates AI coding tools via their CLI runners. '
            'To get started, install the CLI for at least one backend below '
            'and sign in to your account.'
        ).classes('text-sm text-secondary text-center mb-4')

        _cli_install_content()

        ui.separator().classes('my-3')
        with ui.row().classes('items-center justify-between w-full'):
            ui.checkbox(
                "Don't show this again",
                on_change=lambda e: dont_show.update(checked=e.value),
            )
            ui.button('Got it', on_click=lambda: _dismiss(dlg, dont_show)).props(
                'color=primary'
            )

    dlg.open()


def _dismiss(dlg, dont_show: dict) -> None:
    """Close welcome dialog and optionally persist dismissal in browser localStorage."""
    from nicegui import ui

    if dont_show['checked']:
        ui.run_javascript('localStorage.setItem("skillnir_welcome_dismissed", "true")')
    dlg.close()


def show_cli_guide_dialog() -> None:
    """Open the CLI installation guide dialog (always, no storage check)."""
    from nicegui import ui

    with (
        ui.dialog() as dlg,
        ui.card().classes('p-6 min-w-[540px] max-w-[640px] rounded-xl'),
    ):
        with ui.row().classes('items-center justify-between w-full mb-4'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('terminal', color='primary').classes('text-2xl')
                ui.label('CLI Installation Guide').classes('text-xl font-bold')
            ui.button(icon='close', on_click=dlg.close).props('flat round dense')

        ui.label(
            'Install and sign in to the CLI runner for each AI backend '
            'you want to use with Skillnir.'
        ).classes('text-sm text-secondary mb-4')

        _cli_install_content()

    dlg.open()
