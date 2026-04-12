"""Settings page for user preferences."""

from nicegui import app, ui

from skillnir.i18n import SUPPORTED_LANGUAGES, get_current_language, set_language, t
from skillnir.notifier import is_valid_gchat_webhook, send_gchat_notification
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


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

        # ── Setup webhook (Google Chat) ──
        _lang_wh = get_current_language()
        with ui.card().classes('w-full p-5 card-hover'):
            with ui.column().classes('w-full gap-3'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon('webhook', color='primary').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label(t('pages.settings.webhook.title', _lang_wh)).classes(
                            'text-lg font-semibold'
                        )
                        ui.label(
                            t('pages.settings.webhook.subtitle', _lang_wh)
                        ).classes('text-sm text-secondary')

                with ui.row().classes('items-center gap-2'):
                    ui.label(
                        t('pages.settings.webhook.provider_label', _lang_wh) + ':'
                    ).classes('text-sm font-medium')
                    ui.badge(
                        t('pages.settings.webhook.provider_value', _lang_wh),
                        color='primary',
                    )
                    ui.label(
                        t('pages.settings.webhook.provider_note', _lang_wh)
                    ).classes('text-xs text-secondary ml-2')

                webhook_input = (
                    ui.input(
                        label=t('pages.settings.webhook.url_label', _lang_wh),
                        placeholder=t(
                            'pages.settings.webhook.url_placeholder', _lang_wh
                        ),
                        value=config.get_webhook_url(),
                    )
                    .props('clearable')
                    .classes('w-full')
                )
                ui.label(t('pages.settings.webhook.url_help', _lang_wh)).classes(
                    'text-xs text-secondary'
                )

                def _save_webhook():
                    new_url = (webhook_input.value or '').strip()
                    if new_url and not is_valid_gchat_webhook(new_url):
                        ui.notify(
                            t(
                                'pages.settings.webhook.test_failed',
                                _lang_wh,
                                error='invalid webhook URL',
                            ),
                            type='negative',
                        )
                        return
                    config.set_webhook_url(new_url)
                    if not new_url and config.notifications_enabled:
                        # Can't have notifications on with no URL.
                        config.notifications_enabled = False
                        app.storage.user['notifications_enabled'] = False
                    save_config(config)
                    ui.notify(
                        (
                            t('pages.settings.webhook.saved', _lang_wh)
                            if new_url
                            else t('pages.settings.webhook.cleared', _lang_wh)
                        ),
                        type='positive',
                    )
                    # Reload so the top-bar bell picks up the new URL state.
                    ui.navigate.to('/settings')

                def _test_webhook():
                    url = (webhook_input.value or '').strip()
                    if not url:
                        ui.notify(
                            t(
                                'pages.settings.webhook.test_failed',
                                _lang_wh,
                                error='webhook URL not set',
                            ),
                            type='negative',
                        )
                        return
                    if not is_valid_gchat_webhook(url):
                        ui.notify(
                            t(
                                'pages.settings.webhook.test_failed',
                                _lang_wh,
                                error='invalid webhook URL',
                            ),
                            type='negative',
                        )
                        return
                    test_title = f"Test message (model: {config.model})"
                    ok, err = send_gchat_notification(
                        url,
                        test_title,
                        'This is a test from Skillnir settings.',
                    )
                    if ok:
                        ui.notify(
                            t('pages.settings.webhook.test_success', _lang_wh),
                            type='positive',
                        )
                    else:
                        ui.notify(
                            t(
                                'pages.settings.webhook.test_failed',
                                _lang_wh,
                                error=err or 'unknown error',
                            ),
                            type='negative',
                        )

                with ui.row().classes('gap-2 justify-end w-full'):
                    ui.button(
                        t('pages.settings.webhook.test_button', _lang_wh),
                        icon='send',
                        on_click=_test_webhook,
                    ).props('flat rounded')
                    ui.button(
                        t('pages.settings.webhook.save_button', _lang_wh),
                        icon='save',
                        on_click=_save_webhook,
                    ).props('unelevated rounded')

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
