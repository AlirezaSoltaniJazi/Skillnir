"""Dialogs for switching AI backend, model, and prompt version."""

from nicegui import ui


def backend_dialog(config, backends, detect_available_backends, save_config) -> None:
    """Open a dialog to switch AI tool backend."""
    from skillnir.backends import AIBackend

    available = detect_available_backends()
    short_names = {
        AIBackend.CLAUDE: 'Claude',
        AIBackend.CURSOR: 'Cursor',
        AIBackend.GEMINI: 'Gemini',
        AIBackend.COPILOT: 'Copilot',
    }
    with ui.dialog() as dlg, ui.card().classes('p-6 min-w-[480px] rounded-xl'):
        ui.label('Switch AI Tool').classes('text-xl font-bold mb-6 text-center w-full')
        with ui.row().classes('gap-6 justify-center w-full'):
            for b in AIBackend:
                b_info = backends[b]
                is_available = b in available
                is_current = b == config.backend

                def _select(backend=b, avail=is_available, cur=is_current):
                    if not avail or cur:
                        return
                    config.backend = backend
                    config.model = backends[backend].default_model
                    save_config(config)
                    dlg.close()
                    ui.navigate.to('/')

                opacity = '' if is_available else ' opacity-30'
                cursor = ' cursor-pointer' if is_available and not is_current else ''
                ring = ' ring-2 ring-primary' if is_current else ''
                with (
                    ui.column()
                    .classes(
                        f'items-center gap-2 p-4 rounded-xl{opacity}{cursor}{ring} card-hover'
                    )
                    .on('click', _select)
                ):
                    color = 'primary' if is_current else 'grey'
                    ui.icon(b_info.icon, color=color).classes('text-4xl')
                    label_cls = (
                        'text-sm font-bold text-primary'
                        if is_current
                        else 'text-sm text-gray-400'
                    )
                    ui.label(short_names[b]).classes(label_cls)
                    if is_current:
                        ui.badge('active', color='primary').props('dense')
    dlg.open()


def model_dialog(config, backend_info, save_config) -> None:
    """Open a dialog to switch the AI model."""
    with ui.dialog() as dlg, ui.card().classes('min-w-[400px] p-6 rounded-xl'):
        ui.label('Switch Model').classes('text-xl font-bold mb-2')
        ui.label(f'AI Tool: {backend_info.name}').classes('text-gray-400 text-sm mb-4')
        for m in backend_info.models:
            is_current = m.alias == config.model
            ring = ' ring-2 ring-primary' if is_current else ''
            with ui.card().classes(f'w-full px-4 py-3 card-hover{ring}'):
                with ui.row().classes('items-center gap-3 w-full'):
                    ui.label(m.display_name).classes('font-bold flex-1')
                    ui.label(f'({m.alias})').classes('text-gray-500 text-sm')
                    if is_current:
                        ui.badge('current', color='primary')
                    if m.is_default:
                        ui.badge('default', color='grey')
                if not is_current:

                    def select_model(alias=m.alias):
                        config.model = alias
                        save_config(config)
                        dlg.close()
                        ui.navigate.to('/')

                    ui.button('Select', on_click=select_model).props(
                        'flat dense'
                    ).classes('mt-1')
        ui.button('Cancel', on_click=dlg.close).props('flat').classes('mt-3')
    dlg.open()


def prompt_version_dialog(
    config, prompt_versions, prompt_version_labels, save_config
) -> None:
    """Open a dialog to switch prompt version."""
    with ui.dialog() as dlg, ui.card().classes('min-w-[400px] p-6 rounded-xl'):
        ui.label('Switch Prompt Version').classes('text-xl font-bold mb-4')
        for v in prompt_versions:
            is_current = v == config.prompt_version
            ring = ' ring-2 ring-primary' if is_current else ''
            with ui.card().classes(f'w-full px-4 py-3 card-hover{ring}'):
                with ui.row().classes('items-center gap-3 w-full'):
                    ui.label(prompt_version_labels[v]).classes('font-bold flex-1')
                    if is_current:
                        ui.badge('current', color='primary')
                if not is_current:

                    def select_pv(ver=v):
                        config.prompt_version = ver
                        save_config(config)
                        dlg.close()
                        ui.navigate.to('/')

                    ui.button('Select', on_click=select_pv).props('flat dense').classes(
                        'mt-1'
                    )
        ui.button('Cancel', on_click=dlg.close).props('flat').classes('mt-3')
    dlg.open()
