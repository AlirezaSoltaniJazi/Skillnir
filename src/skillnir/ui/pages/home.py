"""Home page for the NiceGUI web interface."""

from nicegui import ui

from skillnir.i18n import get_current_language, t
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


def get_sections(lang: str) -> list[dict]:
    """Return section definitions with translated titles, descriptions, and item labels."""
    return [
        {
            'icon': 'inventory_2',
            'color': 'primary',
            'title': t('pages.home.sections.skill.title', lang),
            'desc': t('pages.home.sections.skill.desc', lang),
            'items': [
                (
                    'download',
                    t('pages.home.sections.skill.items.install', lang),
                    '/install',
                ),
                ('sync', t('pages.home.sections.skill.items.update', lang), '/update'),
                (
                    'fact_check',
                    t('pages.home.sections.skill.items.check', lang),
                    '/check-skill',
                ),
                (
                    'delete',
                    t('pages.home.sections.skill.items.delete', lang),
                    '/delete-skill',
                ),
                (
                    'psychology',
                    t('pages.home.sections.skill.items.generate_skill', lang),
                    '/generate-skill',
                ),
            ],
        },
        {
            'icon': 'auto_stories',
            'color': 'info',
            'title': t('pages.home.sections.ai_context.title', lang),
            'desc': t('pages.home.sections.ai_context.desc', lang),
            'items': [
                (
                    'gavel',
                    t('pages.home.sections.ai_context.items.generate_rule', lang),
                    '/generate-rule',
                ),
                (
                    'auto_stories',
                    t('pages.home.sections.ai_context.items.generate_docs', lang),
                    '/generate-docs',
                ),
                (
                    'delete_sweep',
                    t('pages.home.sections.ai_context.items.delete_docs', lang),
                    '/delete-docs',
                ),
            ],
        },
        {
            'icon': 'note_add',
            'color': 'secondary',
            'title': t('pages.home.sections.default_template.title', lang),
            'desc': t('pages.home.sections.default_template.desc', lang),
            'items': [
                (
                    'note_add',
                    t('pages.home.sections.default_template.items.init_skill', lang),
                    '/init-skill',
                ),
                (
                    'description',
                    t('pages.home.sections.default_template.items.init_docs', lang),
                    '/init-docs',
                ),
            ],
        },
        {
            'icon': 'terminal',
            'color': 'amber',
            'title': t('pages.home.sections.claude_tools.title', lang),
            'desc': t('pages.home.sections.claude_tools.desc', lang),
            'items': [],
        },
        {
            'icon': 'analytics',
            'color': 'teal',
            'title': t('pages.home.sections.usage.title', lang),
            'desc': t('pages.home.sections.usage.desc', lang),
            'items': [
                (
                    'analytics',
                    t('pages.home.sections.usage.items.token_stats', lang),
                    '/usage',
                ),
            ],
        },
        {
            'icon': 'devices',
            'color': 'positive',
            'title': t('pages.home.sections.supported_tools.title', lang),
            'desc': t('pages.home.sections.supported_tools.desc', lang),
            'items': [
                (
                    'devices',
                    t('pages.home.sections.supported_tools.items.models_tools', lang),
                    '/tools',
                ),
            ],
        },
        {
            'icon': 'science',
            'color': 'deep-purple',
            'title': t('pages.home.sections.research.title', lang),
            'desc': t('pages.home.sections.research.desc', lang),
            'items': [
                (
                    'science',
                    t('pages.home.sections.research.items.research_hub', lang),
                    '/research',
                ),
            ],
        },
        {
            'icon': 'event',
            'color': 'orange',
            'title': t('pages.home.sections.events.title', lang),
            'desc': t('pages.home.sections.events.desc', lang),
            'items': [
                (
                    'event',
                    t('pages.home.sections.events.items.events_hub', lang),
                    '/events',
                ),
            ],
        },
        {
            'icon': 'settings',
            'color': 'grey',
            'title': t('pages.home.sections.settings.title', lang),
            'desc': t('pages.home.sections.settings.desc', lang),
            'items': [
                (
                    'settings',
                    t('pages.home.sections.settings.items.preferences', lang),
                    '/settings',
                ),
            ],
        },
        {
            'icon': 'smart_toy',
            'color': 'accent',
            'title': t('pages.home.sections.ai_extra.title', lang),
            'desc': t('pages.home.sections.ai_extra.desc', lang),
            'items': [
                ('chat', t('pages.home.sections.ai_extra.items.ask_ai', lang), '/ask'),
                (
                    'map',
                    t('pages.home.sections.ai_extra.items.plan_with_ai', lang),
                    '/plan',
                ),
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

    lang = get_current_language()
    hook_enabled = is_sound_enabled()

    def on_hook_toggle(e):
        if e.value:
            enable_sound_hooks()
            ui.notify(t('messages.claude_sound_enabled', lang), type='positive')
        else:
            disable_sound_hooks()
            ui.notify(t('messages.claude_sound_disabled', lang), type='warning')

    with ui.row().classes('items-center gap-3'):
        ui.icon('notifications_active', color='amber').classes('text-lg')
        ui.label(
            t('pages.home.sections.claude_tools.sound_notifications', lang)
        ).classes('text-sm flex-1')
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

    lang = get_current_language()
    source_dir = get_source_skills_dir()
    skills = discover_skills(source_dir.parent.parent)
    tool_count = len(TOOLS)
    config = load_config()
    backend_info = BACKENDS[config.backend]
    sections = get_sections(lang)

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
                t('buttons.switch_tool', lang),
                icon='swap_horiz',
                on_click=lambda: backend_dialog(
                    config, BACKENDS, detect_available_backends, save_config
                ),
            ).props('flat rounded dense')
            ui.button(
                t('buttons.switch_model', lang),
                icon='tune',
                on_click=lambda: model_dialog(config, backend_info, save_config),
            ).props('flat rounded dense')
            ui.button(
                t('buttons.prompts', lang),
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
                        ui.button(t('buttons.close', lang), on_click=dlg.close).props(
                            'flat'
                        ).classes('mt-3')
                    dlg.open()
                elif backend_info.usage_url:
                    ui.navigate.to(backend_info.usage_url, new_tab=True)
                else:
                    ui.notify(t('messages.no_usage_info', lang), type='warning')

            ui.button(
                t('buttons.usage', lang), icon='analytics', on_click=_show_usage
            ).props('flat rounded dense')

        # ── Quick actions ──
        with ui.row().classes('gap-3 flex-wrap'):
            ui.button(
                t('pages.home.quick_actions.install_skill', lang),
                icon='download',
                on_click=lambda: ui.navigate.to('/install'),
            ).props('unelevated rounded')
            ui.button(
                t('pages.home.quick_actions.generate_docs', lang),
                icon='auto_stories',
                on_click=lambda: ui.navigate.to('/generate-docs'),
            ).props('outline rounded')
            ui.button(
                t('pages.home.quick_actions.generate_skill', lang),
                icon='psychology',
                on_click=lambda: ui.navigate.to('/generate-skill'),
            ).props('outline rounded')
            ui.button(
                t('pages.home.quick_actions.ask_ai', lang),
                icon='chat',
                on_click=lambda: ui.navigate.to('/ask'),
            ).props('outline rounded')

        # ── Section cards grid ──
        claude_tools_title = t('pages.home.sections.claude_tools.title', lang)
        with ui.element('div').classes('w-full grid grid-cols-1 lg:grid-cols-2 gap-6'):
            for s in sections:
                special = None
                if s['title'] == claude_tools_title:
                    special = _build_claude_tools_content
                section_card(
                    icon=s['icon'],
                    color=s['color'],
                    title=s['title'],
                    desc=s['desc'],
                    items=s['items'],
                    special_content=special,
                )
