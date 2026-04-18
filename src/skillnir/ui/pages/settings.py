"""Settings page for user preferences."""

from nicegui import app, ui

from skillnir.i18n import SUPPORTED_LANGUAGES, get_current_language, set_language, t
from skillnir.notifications import PROVIDERS, NotificationProvider
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


def _render_notifications_card(config, save_config, lang) -> None:
    """Render the top-level Notifications card with per-provider panels.

    Contains:
    - An "Active provider" dropdown
    - One ``ui.expansion`` panel per provider in :data:`PROVIDERS` registry
      order. Each panel has credential inputs, Save, Test, Clear, and
      "Make active" buttons with per-provider validation.
    """

    def _reload():
        """Navigate back to /settings so the header bell picks up changes."""
        ui.navigate.to('/settings')

    with ui.card().classes('w-full p-5 card-hover'):
        with ui.column().classes('w-full gap-3'):
            # ── Card header ─────────────────────────────────────────────
            with ui.row().classes('items-center gap-4'):
                ui.icon('webhook', color='primary').classes('text-3xl')
                with ui.column().classes('gap-0'):
                    ui.label(t('pages.settings.webhook.title', lang)).classes(
                        'text-lg font-semibold'
                    )
                    ui.label(t('pages.settings.webhook.subtitle', lang)).classes(
                        'text-sm text-secondary'
                    )

            # ── Active provider dropdown ────────────────────────────────
            active_options: dict[str, str] = {
                '': t('pages.settings.webhook.active_provider_none', lang),
            }
            for pid, spec in PROVIDERS.items():
                active_options[pid.value] = spec.display_name

            def _on_active_change(e):
                new_active = e.value or ''
                if new_active and not config.has_provider_credentials(new_active):
                    ui.notify(
                        t(
                            'pages.settings.webhook.active_missing_creds',
                            lang,
                            provider=PROVIDERS[
                                NotificationProvider(new_active)
                            ].display_name,
                        ),
                        type='warning',
                    )
                config.active_provider = new_active
                if not new_active and config.notifications_enabled:
                    # Turning off all providers → also turn off the master toggle.
                    config.notifications_enabled = False
                    app.storage.user['notifications_enabled'] = False
                save_config(config)
                _reload()

            with ui.row().classes('items-center gap-3 w-full'):
                ui.label(
                    t('pages.settings.webhook.active_provider_label', lang)
                ).classes('text-sm font-medium')
                ui.select(
                    options=active_options,
                    value=config.active_provider,
                    on_change=_on_active_change,
                ).classes('flex-1')

            ui.separator()

            # ── Per-provider expansion panels ───────────────────────────
            for provider_id, spec in PROVIDERS.items():
                _render_provider_panel(provider_id, spec, config, save_config, lang)


def _render_provider_panel(provider_id, spec, config, save_config, lang) -> None:
    """Render one ``ui.expansion`` panel for a single provider."""

    is_active = config.active_provider == provider_id.value
    existing_creds = config.get_provider_credentials(provider_id.value)

    # Expansion label with active badge
    with ui.expansion(spec.display_name, icon=spec.icon, value=is_active).classes(
        'w-full'
    ) as panel:
        # Active badge shown inside the expansion body (right after header)
        if is_active:
            with ui.row().classes('items-center gap-2 w-full'):
                ui.badge(
                    t('pages.settings.webhook.active_badge', lang),
                    color='positive',
                )

        # Credential inputs (one per spec.credential_fields entry)
        input_refs: dict[str, object] = {}
        for field_key in spec.credential_fields:
            label = t(
                f'pages.settings.webhook.providers.{provider_id.value}.{field_key}_label',
                lang,
            )
            placeholder = t(
                f'pages.settings.webhook.providers.{provider_id.value}.{field_key}_placeholder',
                lang,
            )
            input_el = (
                ui.input(
                    label=label,
                    placeholder=placeholder,
                    value=existing_creds.get(field_key, ''),
                    password=True,
                    password_toggle_button=True,
                )
                .props('clearable')
                .classes('w-full')
            )
            input_refs[field_key] = input_el

        # Help text + link
        help_text = t(
            f'pages.settings.webhook.providers.{provider_id.value}.setup_help',
            lang,
        )
        with ui.row().classes('items-center gap-2'):
            ui.label(help_text).classes('text-xs text-secondary')
            ui.link(
                t('pages.settings.webhook.help_link', lang),
                spec.help_url,
                new_tab=True,
            ).classes('text-xs')

        # ── Button row ──────────────────────────────────────────────────
        def _gather_creds() -> dict[str, str]:
            return {
                k: (getattr(ref, 'value', '') or '').strip()
                for k, ref in input_refs.items()
            }

        def _save():
            creds = _gather_creds()
            if any(creds.values()):
                ok, err = spec.validator(creds)
                if not ok:
                    ui.notify(
                        t(
                            'pages.settings.webhook.test_failed',
                            lang,
                            error=err or 'invalid credentials',
                        ),
                        type='negative',
                    )
                    return
                config.set_provider_credentials(provider_id.value, creds)
            else:
                # All fields empty → clear
                config.clear_provider_credentials(provider_id.value)
                # If this was the active provider, turn off dispatch.
                if config.active_provider == provider_id.value:
                    config.active_provider = ''
                    if config.notifications_enabled:
                        config.notifications_enabled = False
                        app.storage.user['notifications_enabled'] = False
            save_config(config)
            ui.notify(
                t('pages.settings.webhook.saved', lang),
                type='positive',
            )
            _reload_settings()

        def _test():
            creds = _gather_creds()
            if not any(creds.values()):
                ui.notify(
                    t(
                        'pages.settings.webhook.test_failed',
                        lang,
                        error='credentials not set',
                    ),
                    type='negative',
                )
                return
            ok, err = spec.validator(creds)
            if not ok:
                ui.notify(
                    t(
                        'pages.settings.webhook.test_failed',
                        lang,
                        error=err or 'invalid credentials',
                    ),
                    type='negative',
                )
                return
            test_title = f"Test message (model: {config.model})"
            ok, err = spec.sender(
                creds,
                test_title,
                'This is a test from Skillnir settings.',
                10.0,
            )
            if ok:
                ui.notify(
                    t('pages.settings.webhook.test_success', lang),
                    type='positive',
                )
            else:
                ui.notify(
                    t(
                        'pages.settings.webhook.test_failed',
                        lang,
                        error=err or 'unknown error',
                    ),
                    type='negative',
                )

        def _clear():
            config.clear_provider_credentials(provider_id.value)
            if config.active_provider == provider_id.value:
                config.active_provider = ''
                if config.notifications_enabled:
                    config.notifications_enabled = False
                    app.storage.user['notifications_enabled'] = False
            save_config(config)
            ui.notify(
                t('pages.settings.webhook.cleared', lang),
                type='info',
            )
            _reload_settings()

        def _make_active():
            creds = _gather_creds()
            # If the form has values that haven't been saved, save first.
            if any(creds.values()):
                ok, err = spec.validator(creds)
                if not ok:
                    ui.notify(
                        t(
                            'pages.settings.webhook.test_failed',
                            lang,
                            error=err or 'invalid credentials',
                        ),
                        type='negative',
                    )
                    return
                config.set_provider_credentials(provider_id.value, creds)
            elif not config.has_provider_credentials(provider_id.value):
                ui.notify(
                    t(
                        'pages.settings.webhook.test_failed',
                        lang,
                        error='save credentials before activating',
                    ),
                    type='negative',
                )
                return
            config.active_provider = provider_id.value
            save_config(config)
            ui.notify(
                t(
                    'pages.settings.webhook.now_active',
                    lang,
                    provider=spec.display_name,
                ),
                type='positive',
            )
            _reload_settings()

        with ui.row().classes('gap-2 justify-end w-full mt-2'):
            ui.button(
                t('pages.settings.webhook.clear_button', lang),
                icon='delete_outline',
                on_click=_clear,
            ).props('flat rounded color=negative')
            ui.button(
                t('pages.settings.webhook.test_button', lang),
                icon='send',
                on_click=_test,
            ).props('flat rounded')
            ui.button(
                t('pages.settings.webhook.save_button', lang),
                icon='save',
                on_click=_save,
            ).props('unelevated rounded')
            make_active_btn = ui.button(
                t('pages.settings.webhook.make_active_button', lang),
                icon='check_circle',
                on_click=_make_active,
            ).props('unelevated rounded color=positive')
            if is_active:
                make_active_btn.props('disable')

    # Prevent an unused-variable warning on ``panel`` while keeping the
    # context manager for future styling.
    _ = panel


def _reload_settings() -> None:
    """Reload the Settings page so header bell + badges refresh."""
    ui.navigate.to('/settings')


@ui.page('/settings')
def page_settings():
    header()

    with ui.column().classes('w-full max-w-5xl mx-auto px-8 py-8 gap-6'):
        page_header('Settings', 'Configure application preferences.', icon='settings')

        # ── Dark / Light Mode ──
        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('dark_mode', color='amber').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('Dark Mode').classes('text-lg font-semibold')
                        ui.label(
                            'Toggle between dark and light interface theme.'
                        ).classes('text-sm text-secondary')

                dark = ui.dark_mode()
                is_dark = app.storage.user.get('dark_mode', True)
                dark.value = is_dark

                def on_dark_toggle(e):
                    dark.value = e.value
                    app.storage.user['dark_mode'] = e.value
                    theme = 'dark' if e.value else 'light'
                    ui.run_javascript(
                        f"localStorage.setItem('skillnir-theme', '{theme}')"
                    )
                    ui.notify(
                        'Dark mode enabled' if e.value else 'Light mode enabled',
                        type='info',
                    )

                ui.switch('', value=is_dark, on_change=on_dark_toggle)

        # ── Sound Notifications ──
        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('volume_up', color='primary').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('Process Notifications').classes(
                            'text-lg font-semibold'
                        )
                        ui.label('Play a sound when AI generation completes.').classes(
                            'text-sm text-secondary'
                        )

                sound_enabled = app.storage.user.get('sound_enabled', True)

                def on_sound_toggle(e):
                    app.storage.user['sound_enabled'] = e.value
                    ui.notify(
                        (
                            'Sound notifications enabled'
                            if e.value
                            else 'Sound notifications disabled'
                        ),
                        type='info',
                    )

                ui.switch('', value=sound_enabled, on_change=on_sound_toggle)

        # ── Backend & Model ──
        from skillnir.backends import (
            BACKENDS,
            PROMPT_VERSION_LABELS,
            PROMPT_VERSIONS,
            load_config,
            save_config,
        )
        from skillnir.ui.components.backend_picker import (
            backend_dialog,
            model_dialog,
            prompt_version_dialog,
        )
        from skillnir.backends import detect_available_backends

        config = load_config()
        backend_info = BACKENDS[config.backend]

        # ── Notifications (multi-provider) ──
        _lang_wh = get_current_language()
        _render_notifications_card(config, save_config, _lang_wh)

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon(backend_info.icon, color='secondary').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('AI Tool').classes('text-lg font-semibold')
                        ui.label(f'Currently using {backend_info.name}').classes(
                            'text-sm text-secondary'
                        )
                ui.button(
                    'Switch',
                    icon='swap_horiz',
                    on_click=lambda: backend_dialog(
                        config, BACKENDS, detect_available_backends, save_config
                    ),
                ).props('flat rounded')

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('tune', color='info').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('Model').classes('text-lg font-semibold')
                        ui.label(f'Currently using {config.model}').classes(
                            'text-sm text-secondary'
                        )
                ui.button(
                    'Switch',
                    icon='tune',
                    on_click=lambda: model_dialog(config, backend_info, save_config),
                ).props('flat rounded')

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('description', color='accent').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('Prompt Version').classes('text-lg font-semibold')
                        pv_label = PROMPT_VERSION_LABELS.get(
                            config.prompt_version, config.prompt_version
                        )
                        ui.label(f'Currently using {pv_label}').classes(
                            'text-sm text-secondary'
                        )
                ui.button(
                    'Switch',
                    icon='description',
                    on_click=lambda: prompt_version_dialog(
                        config, PROMPT_VERSIONS, PROMPT_VERSION_LABELS, save_config
                    ),
                ).props('flat rounded')

        # ── Prompt Compression ──
        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('compress', color='teal').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        _lang = get_current_language()
                        ui.label(
                            t('pages.settings.compression_title', _lang)
                            or 'Prompt Compression'
                        ).classes('text-lg font-semibold')
                        ui.label(
                            t('pages.settings.compression_subtitle', _lang)
                            or 'Compress prompts before sending to AI backends (saves tokens)'
                        ).classes('text-sm text-secondary')

                def on_compress_toggle(e):
                    config.compress_prompts = e.value
                    save_config(config)
                    ui.notify(
                        (
                            'Prompt compression enabled'
                            if e.value
                            else 'Prompt compression disabled'
                        ),
                        type='info',
                    )

                ui.switch(
                    '', value=config.compress_prompts, on_change=on_compress_toggle
                )

        # ── Effort (Claude SDK only) ──
        from skillnir.backends import (
            AIBackend,
            EFFORT_LEVELS,
            THINKING_MODES,
        )

        _claude_only = config.backend == AIBackend.CLAUDE

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('speed', color='orange').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label(
                            t('pages.settings.effort.title', get_current_language())
                        ).classes('text-lg font-semibold')
                        ui.label(
                            t(
                                'pages.settings.effort.description',
                                get_current_language(),
                                value=config.effort,
                            )
                        ).classes('text-sm text-secondary')
                        if not _claude_only:
                            ui.label(
                                t(
                                    'pages.settings.effort.claude_only',
                                    get_current_language(),
                                )
                            ).classes('text-xs text-warning')

                def on_effort_change(e):
                    config.effort = e.value
                    save_config(config)
                    ui.notify(f'Effort set to {e.value}', type='info')
                    ui.navigate.to('/settings')

                ui.select(
                    options=list(EFFORT_LEVELS),
                    value=config.effort,
                    on_change=on_effort_change,
                ).classes('w-32').props('outlined dense rounded')

        # ── Thinking mode (Claude SDK only) ──
        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('psychology', color='deep-purple').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label(
                            t(
                                'pages.settings.thinking.title',
                                get_current_language(),
                            )
                        ).classes('text-lg font-semibold')
                        ui.label(
                            t(
                                'pages.settings.thinking.description',
                                get_current_language(),
                                value=config.thinking_mode,
                            )
                        ).classes('text-sm text-secondary')
                        if not _claude_only:
                            ui.label(
                                t(
                                    'pages.settings.thinking.claude_only',
                                    get_current_language(),
                                )
                            ).classes('text-xs text-warning')

                def on_thinking_change(e):
                    config.thinking_mode = e.value
                    save_config(config)
                    ui.notify(f'Thinking set to {e.value}', type='info')
                    ui.navigate.to('/settings')

                ui.select(
                    options=list(THINKING_MODES),
                    value=config.thinking_mode,
                    on_change=on_thinking_change,
                ).classes('w-40').props('outlined dense rounded')

        # ── Language ──
        lang = get_current_language()
        lang_name = SUPPORTED_LANGUAGES.get(lang, lang)

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('translate', color='deep-purple').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label(t('pages.settings.language_title', lang)).classes(
                            'text-lg font-semibold'
                        )
                        ui.label(
                            t('pages.settings.language_current', lang, name=lang_name)
                        ).classes('text-sm text-secondary')

                lang_options = {
                    code: name for code, name in SUPPORTED_LANGUAGES.items()
                }

                def on_language_change(e):
                    new_code = e.value
                    set_language(new_code)
                    new_name = SUPPORTED_LANGUAGES.get(new_code, new_code)
                    ui.notify(
                        f'Language changed to {new_name}',
                        type='info',
                    )
                    ui.navigate.to('/settings')

                ui.select(
                    options=lang_options,
                    value=lang,
                    on_change=on_language_change,
                ).classes('w-40')
