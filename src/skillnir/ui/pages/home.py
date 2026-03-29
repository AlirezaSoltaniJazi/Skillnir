"""Home page for the NiceGUI web interface."""

from nicegui import ui

from skillnir.skills import discover_skills
from skillnir.syncer import get_source_skills_dir
from skillnir.tools import TOOLS
from skillnir.ui.components.backend_chip import backend_chip
from skillnir.ui.components.backend_picker import (
    backend_dialog,
    model_dialog,
    prompt_version_dialog,
)
from skillnir.ui.components.hero import hero
from skillnir.ui.components.section_card import section_card
from skillnir.ui.layout import header

# ── Section definitions ──

SECTIONS = [
    {
        'icon': 'inventory_2',
        'color': 'primary',
        'title': 'Skill',
        'desc': 'Install, update, check, delete, or generate skills for your projects.',
        'items': [
            ('download', 'Install', '/install'),
            ('sync', 'Update', '/update'),
            ('fact_check', 'Check', '/check-skill'),
            ('delete', 'Delete', '/delete-skill'),
            ('psychology', 'Generate Skill', '/generate-skill'),
        ],
    },
    {
        'icon': 'auto_stories',
        'color': 'info',
        'title': 'AI Context',
        'desc': 'Generate rules, AI docs, or delete existing docs from projects.',
        'items': [
            ('gavel', 'Generate Rule', '/generate-rule'),
            ('auto_stories', 'Generate AI Docs', '/generate-docs'),
            ('delete_sweep', 'Delete Docs', '/delete-docs'),
        ],
    },
    {
        'icon': 'note_add',
        'color': 'secondary',
        'title': 'Default Template',
        'desc': 'Scaffold blank skill or docs templates with commented placeholders.',
        'items': [
            ('note_add', 'Init Skill', '/init-skill'),
            ('description', 'Init Docs', '/init-docs'),
        ],
    },
    {
        'icon': 'terminal',
        'color': 'amber',
        'title': 'Claude Tools',
        'desc': 'Activate or deactivate Claude Code sound notifications.',
        'items': [],
    },
    {
        'icon': 'analytics',
        'color': 'teal',
        'title': 'Usage',
        'desc': 'View token stats and per-backend usage information.',
        'items': [
            ('analytics', 'Token Stats', '/usage'),
        ],
    },
    {
        'icon': 'devices',
        'color': 'positive',
        'title': 'Supported Tools',
        'desc': 'Browse all supported AI tools and their models.',
        'items': [
            ('devices', 'Models & Tools', '/tools'),
        ],
    },
    {
        'icon': 'science',
        'color': 'deep-purple',
        'title': 'Research',
        'desc': 'Do web research, view existing articles, or delete research data.',
        'items': [
            ('science', 'Research Hub', '/research'),
        ],
    },
    {
        'icon': 'settings',
        'color': 'grey',
        'title': 'Settings',
        'desc': 'Light/dark mode, notification toggle, and app preferences.',
        'items': [
            ('settings', 'Preferences', '/settings'),
        ],
    },
    {
        'icon': 'smart_toy',
        'color': 'accent',
        'title': 'AI Extra',
        'desc': 'Ask AI questions or get detailed implementation plans.',
        'items': [
            ('chat', 'Ask AI', '/ask'),
            ('map', 'Plan with AI', '/plan'),
        ],
    },
]


def _build_claude_tools_content():
    """Inline content for the Claude Tools section card."""
    from skillnir.hooks import (
        disable_sound_hooks,
        enable_sound_hooks,
        is_sound_enabled,
    )

    hook_enabled = is_sound_enabled()

    def on_hook_toggle(e):
        if e.value:
            enable_sound_hooks()
            ui.notify('Claude sound notifications enabled', type='positive')
        else:
            disable_sound_hooks()
            ui.notify('Claude sound notifications disabled', type='warning')

    with ui.row().classes('items-center gap-3'):
        ui.icon('notifications_active', color='amber').classes('text-lg')
        ui.label('Sound Notifications').classes('text-sm flex-1')
        ui.switch('', value=hook_enabled, on_change=on_hook_toggle)


@ui.page('/')
def page_home():
    _audio, _snd = header()

    from skillnir.ui.components.welcome_dialog import show_welcome_dialog

    ui.timer(0.5, show_welcome_dialog, once=True)

    from skillnir.backends import (
        BACKENDS,
        PROMPT_VERSION_LABELS,
        PROMPT_VERSIONS,
        detect_available_backends,
        get_backend_version,
        get_usage_info,
        load_config,
        save_config,
    )

    source_dir = get_source_skills_dir()
    skills = discover_skills(source_dir.parent.parent)
    tool_count = len(TOOLS)
    config = load_config()
    backend_info = BACKENDS[config.backend]

    with ui.column().classes('w-full max-w-6xl mx-auto px-8 py-8 gap-8'):
        # ── Hero ──
        hero(len(skills), tool_count, tool_count + 1)

        # ── Backend config row ──
        with ui.row().classes('items-center gap-4 flex-wrap'):
            backend_chip(
                config,
                backend_info,
                on_click_switch=lambda: backend_dialog(
                    config, BACKENDS, detect_available_backends, save_config
                ),
            )

            version = get_backend_version(config.backend)
            if version:
                ui.badge(version, color='grey').props('rounded dense')

            pv_label = PROMPT_VERSION_LABELS.get(
                config.prompt_version, config.prompt_version
            )
            ui.badge(f'Prompts: {pv_label}', color='grey').props('rounded dense')

            # Action buttons
            ui.button(
                'Switch Tool',
                icon='swap_horiz',
                on_click=lambda: backend_dialog(
                    config, BACKENDS, detect_available_backends, save_config
                ),
            ).props('flat rounded dense')
            ui.button(
                'Switch Model',
                icon='tune',
                on_click=lambda: model_dialog(config, backend_info, save_config),
            ).props('flat rounded dense')
            ui.button(
                'Prompts',
                icon='description',
                on_click=lambda: prompt_version_dialog(
                    config, PROMPT_VERSIONS, PROMPT_VERSION_LABELS, save_config
                ),
            ).props('flat rounded dense')

            def _show_usage():
                usage = get_usage_info(config.backend)
                if usage:
                    with (
                        ui.dialog() as dlg,
                        ui.card().classes('min-w-[440px] p-6 rounded-xl'),
                    ):
                        ui.label(f'{backend_info.name} Usage').classes(
                            'text-xl font-bold mb-3'
                        )
                        ui.html(
                            f'<pre style="white-space:pre-wrap;font-size:0.85rem;'
                            f'line-height:1.5;margin:0">{usage}</pre>'
                        )
                        ui.button('Close', on_click=dlg.close).props('flat').classes(
                            'mt-3'
                        )
                    dlg.open()
                elif backend_info.usage_url:
                    ui.navigate.to(backend_info.usage_url, new_tab=True)
                else:
                    ui.notify('No usage info available.', type='warning')

            ui.button('Usage', icon='analytics', on_click=_show_usage).props(
                'flat rounded dense'
            )

        # ── Quick actions ──
        with ui.row().classes('gap-3 flex-wrap'):
            ui.button(
                'Install Skill',
                icon='download',
                on_click=lambda: ui.navigate.to('/install'),
            ).props('unelevated rounded')
            ui.button(
                'Generate Docs',
                icon='auto_stories',
                on_click=lambda: ui.navigate.to('/generate-docs'),
            ).props('outline rounded')
            ui.button(
                'Generate Skill',
                icon='psychology',
                on_click=lambda: ui.navigate.to('/generate-skill'),
            ).props('outline rounded')
            ui.button(
                'Ask AI',
                icon='chat',
                on_click=lambda: ui.navigate.to('/ask'),
            ).props('outline rounded')

        # ── Section cards grid ──
        with ui.element('div').classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-6'):
            for s in SECTIONS:
                special = None
                if s['title'] == 'Claude Tools':
                    special = _build_claude_tools_content
                section_card(
                    icon=s['icon'],
                    color=s['color'],
                    title=s['title'],
                    desc=s['desc'],
                    items=s['items'],
                    special_content=special,
                )
