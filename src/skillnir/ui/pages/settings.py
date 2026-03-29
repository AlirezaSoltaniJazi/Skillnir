"""Settings page for user preferences."""

from nicegui import app, ui

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
                        ).classes('text-sm text-gray-400')

                dark = ui.dark_mode()
                is_dark = app.storage.user.get('dark_mode', True)
                dark.value = is_dark

                def on_dark_toggle(e):
                    dark.value = e.value
                    app.storage.user['dark_mode'] = e.value
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
                            'text-sm text-gray-400'
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

        with ui.card().classes('w-full p-5 card-hover'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.row().classes('items-center gap-4'):
                    ui.icon(backend_info.icon, color='secondary').classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label('AI Tool').classes('text-lg font-semibold')
                        ui.label(f'Currently using {backend_info.name}').classes(
                            'text-sm text-gray-400'
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
                            'text-sm text-gray-400'
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
                            'text-sm text-gray-400'
                        )
                ui.button(
                    'Switch',
                    icon='description',
                    on_click=lambda: prompt_version_dialog(
                        config, PROMPT_VERSIONS, PROMPT_VERSION_LABELS, save_config
                    ),
                ).props('flat rounded')
