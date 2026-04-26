"""Shared layout components and helpers for the NiceGUI web interface."""

from pathlib import Path

from skillnir.i18n import (
    t,
    get_current_language,
    is_rtl,
    SUPPORTED_LANGUAGES,
    set_language,
)
from skillnir.skills import Skill
from skillnir.syncer import SyncResult
from skillnir.tools import AITool, AUTO_INJECT_TOOL, TOOLS, detect_tools

# ---------------------------------------------------------------------------
# Helpers (no nicegui imports at module level — used by page modules)
# ---------------------------------------------------------------------------

SORT_MODES = {
    "default": "Default",
    "alpha": "Alphabetical (A-Z)",
    "alpha-desc": "Alphabetical (Z-A)",
}

# ── Navigation structure ──

NAV_GROUPS = [
    (
        'SKILL MANAGEMENT',
        [
            ('download', 'Install', '/install'),
            ('sync', 'Update', '/update'),
            ('fact_check', 'Check', '/check-skill'),
            ('delete', 'Delete', '/delete-skill'),
            ('psychology', 'Generate Skill', '/generate-skill'),
        ],
    ),
    (
        'AI CONTEXT',
        [
            ('gavel', 'Generate Rule', '/generate-rule'),
            ('auto_stories', 'Generate Docs', '/generate-docs'),
            ('menu_book', 'Generate Wiki', '/generate-wiki'),
            ('compress', 'Compress Docs', '/compress-docs'),
            ('auto_fix_high', 'Optimize Docs', '/optimize-docs'),
            ('delete_sweep', 'Delete Docs', '/delete-docs'),
            ('layers_clear', 'Delete Wiki', '/delete-wiki'),
        ],
    ),
    (
        'TEMPLATES',
        [
            ('note_add', 'Init Skill', '/init-skill'),
            ('description', 'Init Docs', '/init-docs'),
            ('visibility_off', 'Install Ignore', '/install-ignore'),
        ],
    ),
    (
        'AI ASSISTANT',
        [
            ('chat', 'Ask AI', '/ask'),
            ('map', 'Plan', '/plan'),
        ],
    ),
    (
        'TOOLS & DATA',
        [
            ('inventory_2', 'Skills Library', '/skills'),
            ('devices', 'Tools Registry', '/tools'),
            ('analytics', 'Usage', '/usage'),
            ('science', 'Research', '/research'),
            ('biotech', 'Testing Research', '/testing-research'),
            ('event', 'Events', '/events'),
            ('assessment', 'Benchmarks', '/benchmarks'),
            ('security', 'Security', '/security'),
        ],
    ),
]


def get_nav_groups(lang: str | None = None) -> list:
    """Return navigation groups with translated labels."""
    return [
        (
            t("nav.groups.skill_management", lang),
            [
                ("download", t("nav.items.install", lang), "/install"),
                ("sync", t("nav.items.update", lang), "/update"),
                ("fact_check", t("nav.items.check", lang), "/check-skill"),
                ("delete", t("nav.items.delete", lang), "/delete-skill"),
                ("psychology", t("nav.items.generate_skill", lang), "/generate-skill"),
            ],
        ),
        (
            t("nav.groups.ai_context", lang),
            [
                ("gavel", t("nav.items.generate_rule", lang), "/generate-rule"),
                ("auto_stories", t("nav.items.generate_docs", lang), "/generate-docs"),
                ("menu_book", t("nav.items.generate_wiki", lang), "/generate-wiki"),
                ("compress", t("nav.items.compress_docs", lang), "/compress-docs"),
                (
                    "auto_fix_high",
                    t("nav.items.optimize_docs", lang),
                    "/optimize-docs",
                ),
                ("delete_sweep", t("nav.items.delete_docs", lang), "/delete-docs"),
                ("layers_clear", t("nav.items.delete_wiki", lang), "/delete-wiki"),
            ],
        ),
        (
            t("nav.groups.templates", lang),
            [
                ("note_add", t("nav.items.init_skill", lang), "/init-skill"),
                ("description", t("nav.items.init_docs", lang), "/init-docs"),
                (
                    "visibility_off",
                    t("nav.items.install_ignore", lang),
                    "/install-ignore",
                ),
            ],
        ),
        (
            t("nav.groups.ai_assistant", lang),
            [
                ("chat", t("nav.items.ask_ai", lang), "/ask"),
                ("map", t("nav.items.plan", lang), "/plan"),
            ],
        ),
        (
            t("nav.groups.tools_data", lang),
            [
                ("inventory_2", t("nav.items.skills_library", lang), "/skills"),
                ("devices", t("nav.items.tools_registry", lang), "/tools"),
                ("analytics", t("nav.items.usage", lang), "/usage"),
                ("science", t("nav.items.research", lang), "/research"),
                (
                    "biotech",
                    t("nav.items.testing_research", lang),
                    "/testing-research",
                ),
                ("event", t("nav.items.events", lang), "/events"),
                ("assessment", t("nav.items.benchmarks", lang), "/benchmarks"),
                ("security", t("nav.items.security", lang), "/security"),
            ],
        ),
    ]


def _sort_tools(tools: tuple[AITool, ...] | list[AITool], mode: str) -> list[AITool]:
    if mode == "alpha":
        return sorted(tools, key=lambda t: t.name.lower())
    if mode == "alpha-desc":
        return sorted(tools, key=lambda t: t.name.lower(), reverse=True)
    return list(tools)


def _action_badge_color(action: str) -> str:
    if action == "copied":
        return "positive"
    if action == "updated":
        return "info"
    return "grey"


def _count_skill_files(skill: Skill) -> int:
    return sum(1 for f in skill.path.rglob("*") if f.is_file())


# ---------------------------------------------------------------------------
# Shared layout — drawer navigation + app bar
# ---------------------------------------------------------------------------


def header() -> tuple:
    """Build the shared layout with drawer nav and return (audio_element, sound_state)."""
    from nicegui import app, ui

    from skillnir.backends import load_config, save_config
    from skillnir.ui import _GLOBAL_CSS

    is_dark = app.storage.user.get('dark_mode', True)
    dark = ui.dark_mode(is_dark)
    ui.run_javascript(
        f"localStorage.setItem('skillnir-theme', '{('dark' if is_dark else 'light')}')"
    )
    ui.colors(
        primary='#6366f1',
        secondary='#8b5cf6',
        accent='#06b6d4',
        positive='#10b981',
        negative='#ef4444',
        warning='#f59e0b',
        info='#3b82f6',
    )
    ui.add_head_html(_GLOBAL_CSS)

    sound_enabled = app.storage.user.get("sound_enabled", True)
    sound_state = {"enabled": sound_enabled}

    # Load persisted webhook preferences so the bell can reflect them.
    _app_cfg = load_config()
    # The bell is "ready" iff an active provider is selected AND that
    # provider has complete credentials stored. This generalizes the old
    # "gchat URL set" check to the multi-provider world.
    _webhook_url_set = bool(
        _app_cfg.active_provider
        and _app_cfg.has_provider_credentials(_app_cfg.active_provider)
    )
    _notif_enabled = _app_cfg.notifications_enabled and _webhook_url_set
    # Keep storage in sync with config so play_notification can read it fast.
    app.storage.user['notifications_enabled'] = _notif_enabled
    notif_state = {"enabled": _notif_enabled}

    # ── Detect current route for active highlighting ──
    current_path = ui.context.client.page.path
    lang = get_current_language()
    is_rtl(lang)
    nav_groups = get_nav_groups(lang)

    # ── Left Drawer ──
    with (
        ui.left_drawer(value=True)
        .classes('py-4 px-0')
        .props('width=240 show-if-above bordered') as drawer
    ):
        # Brand
        with ui.row().classes('items-center gap-3 px-5 mb-6'):
            ui.icon('auto_fix_high', color='primary').classes('text-2xl')
            ui.link('Skillnir', '/').classes(
                'text-xl font-bold no-underline gradient-text'
            )

        # Nav groups
        for group_label, items in nav_groups:
            ui.label(group_label).classes(
                'text-[10px] font-bold text-secondary tracking-widest px-5 mt-4 mb-1'
            )
            for icon, label, route in items:
                is_active = current_path == route
                active_cls = ' nav-active' if is_active else ''
                with (
                    ui.row()
                    .classes(
                        'items-center gap-3 px-5 py-2 cursor-pointer rounded-l-lg '
                        'hover:bg-white/5 mx-1 transition-all duration-150' + active_cls
                    )
                    .on('click', lambda r=route: ui.navigate.to(r))
                ):
                    color = 'primary' if is_active else 'grey'
                    ui.icon(icon, color=color).classes('text-lg')
                    text_cls = (
                        'text-sm font-medium' if is_active else 'text-sm text-secondary'
                    )
                    ui.label(label).classes(text_cls)

        # Settings at bottom
        ui.space()
        ui.separator().classes('mx-4')
        is_settings = current_path == '/settings'
        active_cls = ' nav-active' if is_settings else ''
        with (
            ui.row()
            .classes(
                'items-center gap-3 px-5 py-2 cursor-pointer rounded-l-lg '
                'hover:bg-white/5 mx-1 mt-2' + active_cls
            )
            .on('click', lambda: ui.navigate.to('/settings'))
        ):
            color = 'primary' if is_settings else 'grey'
            ui.icon('settings', color=color).classes('text-lg')
            text_cls = (
                'text-sm font-medium' if is_settings else 'text-sm text-secondary'
            )
            ui.label(t("nav.items.settings", lang)).classes(text_cls)

    # ── Top App Bar ──
    ui.add_head_html(
        '<style>'
        '.hdr-btn .q-icon { color: inherit !important; }'
        'body.body--dark .hdr-btn .q-icon { color: white !important; }'
        'body:not(.body--dark) .hdr-btn .q-icon { color: #1d1d1d !important; }'
        '</style>'
    )
    _hdr = 'flat round dense'

    with ui.header().classes('items-center justify-between px-4 h-12'):
        with ui.row().classes('items-center gap-2'):
            ui.button(icon='menu', on_click=drawer.toggle).props(_hdr).classes(
                'hdr-btn'
            )

        with ui.row().classes('items-center gap-1'):

            def _show_guide():
                from skillnir.ui.components.welcome_dialog import show_cli_guide_dialog

                show_cli_guide_dialog()

            ui.button(icon='help_outline', on_click=_show_guide).props(_hdr).classes(
                'hdr-btn'
            ).tooltip('CLI setup guide')

            def toggle_dark():
                is_dark_now = not dark.value
                dark.value = is_dark_now
                app.storage.user['dark_mode'] = is_dark_now
                dark_btn.props(f'icon={"dark_mode" if is_dark_now else "light_mode"}')
                theme = 'dark' if is_dark_now else 'light'
                ui.run_javascript(f"localStorage.setItem('skillnir-theme', '{theme}')")

            dark_btn = (
                ui.button(
                    icon='dark_mode' if is_dark else 'light_mode',
                    on_click=toggle_dark,
                )
                .props(_hdr)
                .classes('hdr-btn')
                .tooltip('Toggle dark/light mode')
            )

            def toggle_sound():
                sound_state["enabled"] = not sound_state["enabled"]
                app.storage.user["sound_enabled"] = sound_state["enabled"]
                sound_btn.props(
                    f'icon={"volume_up" if sound_state["enabled"] else "volume_off"}'
                )

            sound_btn = (
                ui.button(
                    icon="volume_up" if sound_state["enabled"] else "volume_off",
                    on_click=toggle_sound,
                )
                .props(_hdr)
                .classes('hdr-btn')
                .tooltip("Toggle notification sound")
            )

            with ui.element('div').classes('relative'):
                lang_menu = ui.menu().props('auto-close')
                with lang_menu:
                    for code, name in SUPPORTED_LANGUAGES.items():
                        is_active = code == lang

                        def _switch(c=code):
                            set_language(c)
                            ui.navigate.to(current_path)

                        with ui.menu_item(on_click=_switch).classes(
                            'font-bold' if is_active else ''
                        ):
                            with ui.row().classes('items-center gap-2'):
                                if is_active:
                                    ui.icon('check', size='xs').classes('text-primary')
                                ui.label(name)

                (
                    ui.button(icon='translate', on_click=lang_menu.open)
                    .props(_hdr)
                    .classes('hdr-btn')
                    .tooltip(SUPPORTED_LANGUAGES.get(lang, 'Language'))
                )

            # ── Webhook notifications toggle ──
            def _bell_icon() -> str:
                return (
                    'notifications' if notif_state["enabled"] else 'notifications_off'
                )

            def _bell_tooltip() -> str:
                if not _webhook_url_set:
                    return t('layout.tooltips.notifications_disabled', lang)
                if notif_state["enabled"]:
                    return t('layout.tooltips.notifications_on', lang)
                return t('layout.tooltips.notifications_off', lang)

            def toggle_notifications():
                if not _webhook_url_set:
                    ui.notify(
                        t('layout.tooltips.notifications_disabled', lang),
                        type='warning',
                    )
                    return
                notif_state["enabled"] = not notif_state["enabled"]
                app.storage.user['notifications_enabled'] = notif_state["enabled"]
                _app_cfg.notifications_enabled = notif_state["enabled"]
                try:
                    save_config(_app_cfg)
                except OSError:
                    pass
                bell_btn.props(f'icon={_bell_icon()}')
                bell_btn.tooltip(_bell_tooltip())

            bell_btn = (
                ui.button(icon=_bell_icon(), on_click=toggle_notifications)
                .props(_hdr)
                .classes('hdr-btn')
                .tooltip(_bell_tooltip())
            )
            if not _webhook_url_set:
                bell_btn.props('disable')

    audio_el = ui.audio("/static/notification.mp3").props("preload=auto")
    audio_el.set_visibility(False)

    return audio_el, sound_state


def play_notification(
    audio_el,
    sound_state: dict,
    *,
    title: str = "Task complete",
    detail: str | None = None,
) -> None:
    """Play the notification chime and optionally POST a webhook message.

    If sound is enabled, plays the local chime. If webhook notifications
    are enabled (top-bar bell is ON) AND a provider is active with
    valid credentials, also POSTs the message to that provider in a
    background thread (fire-and-forget). Errors log to stderr; the UI
    is never notified from the background thread.
    """
    if sound_state.get("enabled", True):
        audio_el.play()

    # Webhook dispatch — gated on the top-bar toggle state.
    try:
        from nicegui import app

        if not app.storage.user.get('notifications_enabled', False):
            return
    except RuntimeError, ImportError:
        # No NiceGUI request context — skip silently (e.g. unit tests).
        return

    try:
        from skillnir.backends import load_config
        from skillnir.notifications import PROVIDERS, NotificationProvider

        cfg = load_config()
        if not cfg.active_provider:
            return

        try:
            provider_id = NotificationProvider(cfg.active_provider)
        except ValueError:
            return

        spec = PROVIDERS.get(provider_id)
        if spec is None:
            return

        creds = cfg.get_provider_credentials(cfg.active_provider)
        if not creds or not all(creds.values()):
            return

        # Decorate the card title with the current model so the user knows
        # which backend produced the result at a glance.
        decorated_title = f"{title} (model: {cfg.model})"

        import threading

        def _post() -> None:
            ok, err = spec.sender(creds, decorated_title, detail, 10.0)
            if not ok:
                import sys

                print(
                    f"[skillnir] {provider_id.value} notification failed: {err}",
                    file=sys.stderr,
                )

        threading.Thread(target=_post, daemon=True).start()
    except (OSError, ImportError) as exc:
        import sys

        print(f"[skillnir] webhook dispatch error: {exc}", file=sys.stderr)


def tool_icon(tool: AITool) -> None:
    """Render a tool's icon or avatar fallback."""
    from nicegui import ui

    if tool.icon_url:
        ui.image(tool.icon_url).classes("w-8 h-8 rounded")
    else:
        ui.avatar(tool.name[0].upper(), color="primary").props("size=32px")


# ---------------------------------------------------------------------------
# Install wizard helpers (used by skill pages)
# ---------------------------------------------------------------------------


def build_skill_cards(container, state, stepper, tool_container) -> None:
    """Build skill selection cards for the install wizard."""
    from nicegui import ui

    from skillnir.remover import find_skill_installations

    container.clear()
    with container:
        with ui.row().classes("gap-2 mb-3"):

            def select_all_skills():
                state["selected_skills"] = list(state["skills"])
                build_skill_cards(container, state, stepper, tool_container)

            def deselect_all_skills():
                state["selected_skills"] = []
                build_skill_cards(container, state, stepper, tool_container)

            ui.button(
                "Select All", on_click=select_all_skills, icon="select_all"
            ).props("flat dense")
            ui.button(
                "Deselect All", on_click=deselect_all_skills, icon="deselect"
            ).props("flat dense")
            ui.label(f"{len(state['selected_skills'])} selected").classes(
                "text-secondary ml-4 self-center"
            )

        selected_names = {s.name for s in state["selected_skills"]}
        target_root = Path(state["target_root"])

        for skill in state["skills"]:
            file_count = _count_skill_files(skill)
            is_selected = skill.name in selected_names
            is_installed = bool(find_skill_installations(target_root, skill.dir_name))
            card_cls = "w-full px-5 py-3 card-hover"
            if is_selected:
                card_cls += " ring-2 ring-primary"

            with ui.card().classes(card_cls):
                with ui.row().classes("items-center w-full gap-4"):
                    cb = ui.checkbox(value=is_selected)

                    def on_toggle(e, s=skill):
                        if e.value:
                            if s not in state["selected_skills"]:
                                state["selected_skills"].append(s)
                        else:
                            state["selected_skills"] = [
                                x for x in state["selected_skills"] if x.name != s.name
                            ]
                        build_skill_cards(container, state, stepper, tool_container)

                    cb.on_value_change(on_toggle)

                    with ui.column().classes("flex-1 gap-1"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(skill.name).classes("text-lg font-bold")
                            ui.badge(f"v{skill.version}", color="primary")
                            ui.badge(f"{file_count} files", color="grey")
                            if is_installed:
                                ui.badge("Installed", color="positive")
                        ui.label(skill.description).classes("text-secondary text-sm")

        with ui.row().classes("mt-4 gap-2"):

            def next_skills():
                if not state["selected_skills"]:
                    ui.notify("Select at least one skill.", type="warning")
                    return
                build_tool_table(tool_container, state)
                stepper.next()

            ui.button(
                "Next — Select Tools", on_click=next_skills, icon="arrow_forward"
            ).props('unelevated rounded')


def build_tool_table(container, state: dict) -> None:
    """Build tool selection table for the install wizard."""
    from nicegui import ui

    container.clear()
    sorted_tools = _sort_tools(TOOLS, state["sort_mode"])

    with container:
        with ui.row().classes("gap-2 mb-3"):

            def select_all():
                state["selected_tools"] = list(sorted_tools)
                build_tool_table(container, state)

            def deselect_all():
                state["selected_tools"] = []
                build_tool_table(container, state)

            ui.button("Select All", on_click=select_all, icon="select_all").props(
                "flat dense"
            )
            ui.button("Deselect All", on_click=deselect_all, icon="deselect").props(
                "flat dense"
            )

            def auto_detect():
                target = Path(state["target_root"])
                detected = detect_tools(target)
                if detected:
                    existing_names = {t.name for t in state["selected_tools"]}
                    for t in detected:
                        if t.name not in existing_names:
                            state["selected_tools"].append(t)
                    ui.notify(
                        f"Found {len(detected)} tools in {target.name}/",
                        type="positive",
                    )
                else:
                    ui.notify("No tool directories found in target.", type="info")
                build_tool_table(container, state)

            ui.button("Auto-detect", on_click=auto_detect, icon="search").props(
                "flat dense"
            )
            ui.label(f"{len(state['selected_tools'])} selected").classes(
                "text-secondary ml-4 self-center"
            )

        selected_names = {t.name for t in state["selected_tools"]}

        for tool in sorted_tools:
            is_selected = tool.name in selected_names
            card_cls = "w-full px-5 py-3 card-hover"
            if is_selected:
                card_cls += " ring-2 ring-primary"

            with ui.card().classes(card_cls):
                with ui.row().classes("items-center w-full gap-4"):
                    cb = ui.checkbox(value=is_selected)

                    def on_toggle(e, t=tool):
                        if e.value:
                            if t not in state["selected_tools"]:
                                state["selected_tools"].append(t)
                        else:
                            state["selected_tools"] = [
                                x for x in state["selected_tools"] if x.name != t.name
                            ]
                        build_tool_table(container, state)

                    cb.on_value_change(on_toggle)

                    tool_icon(tool)

                    with ui.column().classes("flex-1 gap-0"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(tool.name).classes("font-bold")
                            ui.label(f"({tool.dotdir}/)").classes(
                                "text-secondary text-sm"
                            )
                        ui.label(tool.company).classes("text-secondary text-sm")

                    ui.label(tool.dotdir + "/").classes(
                        "text-xs text-secondary font-mono"
                    )


def build_confirm(container, state: dict) -> None:
    """Build injection confirmation summary."""
    from nicegui import ui

    container.clear()
    skills = state["selected_skills"]
    target = state["target_root"]
    tools = state["selected_tools"]

    with container:
        with ui.card().classes("w-full p-6"):
            ui.label("Injection Summary").classes("text-xl font-bold mb-4")
            with ui.grid(columns=2).classes("gap-x-6 gap-y-2"):
                ui.label("Target:").classes("font-medium")
                ui.label(target).classes("text-gray-300 font-mono text-sm")
                ui.label("Skills:").classes("font-medium")
                with ui.column().classes("gap-1"):
                    for skill in skills:
                        with ui.row().classes("items-center gap-2"):
                            ui.label(skill.name)
                            ui.badge(f"v{skill.version}", color="primary")
                ui.label("Tools:").classes("font-medium")
                ui.label(f"{len(tools)} selected + .agents/ (auto)")

        ui.label("Symlinks to create:").classes("font-medium mt-4 mb-2")
        with ui.column().classes("gap-2 pl-4"):
            for skill in skills:
                ui.label(skill.name).classes("text-sm font-medium text-gray-300 mt-2")
                with ui.row().classes("items-center gap-2"):
                    tool_icon(AUTO_INJECT_TOOL)
                    ui.label(
                        f"{AUTO_INJECT_TOOL.name} → "
                        f"{AUTO_INJECT_TOOL.dotdir}/{AUTO_INJECT_TOOL.skills_subpath}/{skill.dir_name}"
                    ).classes("text-sm text-secondary")
                for t in tools:
                    with ui.row().classes("items-center gap-2"):
                        tool_icon(t)
                        ui.label(
                            f"{t.name} → {t.dotdir}/{t.skills_subpath}/{skill.dir_name}"
                        ).classes("text-sm text-secondary")


def build_results(container, all_results: list[tuple[Skill, list]]) -> None:
    """Build injection results report."""
    from nicegui import ui

    from skillnir.ui.components.stat_card import stat_card

    container.clear()
    total_created = sum(len([r for r in res if r.created]) for _, res in all_results)
    total_skipped = sum(
        len([r for r in res if not r.created and not r.error]) for _, res in all_results
    )
    total_errors = sum(len([r for r in res if r.error]) for _, res in all_results)

    with container:
        ui.label("Injection Report").classes("text-xl font-bold mb-4")

        with ui.row().classes("gap-4 mb-4 flex-wrap"):
            stat_card(
                str(total_created), 'Created', icon='check_circle', color='positive'
            )
            stat_card(str(total_skipped), 'Skipped', icon='skip_next', color='grey')
            stat_card(str(total_errors), 'Errors', icon='error', color='negative')

        for skill, results in all_results:
            created = [r for r in results if r.created]
            skipped = [r for r in results if not r.created and not r.error]
            errors = [r for r in results if r.error]

            ui.separator().classes("my-3")
            ui.label(skill.name).classes("font-bold text-lg")

            if created:
                ui.label("Created:").classes("font-medium mt-1")
                for r in created:
                    with ui.row().classes("items-center gap-2"):
                        tool_icon(r.tool)
                        ui.label(f"+ {r.symlink_path}").classes(
                            "text-sm text-green-400 font-mono"
                        )
            if skipped:
                ui.label("Already existed:").classes("font-medium mt-1")
                for r in skipped:
                    with ui.row().classes("items-center gap-2"):
                        tool_icon(r.tool)
                        ui.label(f"= {r.symlink_path}").classes(
                            "text-sm text-secondary font-mono"
                        )
            if errors:
                ui.label("Errors:").classes("font-medium mt-1")
                for r in errors:
                    with ui.row().classes("items-center gap-2"):
                        tool_icon(r.tool)
                        ui.label(f"! {r.tool.name}: {r.error}").classes(
                            "text-sm text-red-400 font-mono"
                        )


def build_sync_report(container, results: list[SyncResult]) -> None:
    """Build skill sync results report."""
    from nicegui import ui

    from skillnir.ui.components.stat_card import stat_card

    container.clear()
    with container:
        if not results:
            ui.label("No skills found in source.").classes("text-secondary")
            return

        ui.separator().classes("my-4")
        ui.label("Sync Report").classes("text-xl font-bold mb-4")

        copied = sum(1 for r in results if r.action == "copied")
        updated = sum(1 for r in results if r.action == "updated")
        skipped_n = sum(1 for r in results if r.action == "skipped")

        with ui.row().classes("gap-4 mb-4 flex-wrap"):
            stat_card(str(copied), 'Copied', icon='content_copy', color='positive')
            stat_card(str(updated), 'Updated', icon='update', color='info')
            stat_card(str(skipped_n), 'Skipped', icon='skip_next', color='grey')

        for r in results:
            color = _action_badge_color(r.action)
            with ui.row().classes("items-center gap-2"):
                ui.badge(r.action, color=color)
                ui.label(r.skill_name).classes("font-medium")
                ui.label(f"v{r.source_version}").classes("text-secondary")
                if r.action == "updated" and r.target_version:
                    ui.label(f"(was v{r.target_version})").classes(
                        "text-secondary text-sm"
                    )
