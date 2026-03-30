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
                        else 'text-sm text-secondary'
                    )
                    ui.label(short_names[b]).classes(label_cls)
                    if is_current:
                        ui.badge('active', color='primary').props('dense')
    dlg.open()


_TIER_LABELS = {
    1: ("Powerful", "rocket_launch", "amber"),
    2: ("Balanced", "balance", "info"),
    3: ("Fast & Affordable", "bolt", "positive"),
}


def model_dialog(config, backend_info, save_config) -> None:
    """Open a dialog to switch the AI model with tiered grid layout."""
    with (
        ui.dialog() as dlg,
        ui.card().classes('min-w-[700px] max-w-[900px] p-6 rounded-xl'),
    ):
        ui.label('Switch Model').classes('text-xl font-bold mb-1')
        ui.label(f'AI Tool: {backend_info.name}').classes('text-secondary text-sm mb-4')

        # Group models by tier
        tiers: dict[int, list] = {1: [], 2: [], 3: []}
        for m in backend_info.models:
            tiers.setdefault(m.tier, []).append(m)

        for tier_num in (1, 2, 3):
            tier_models = tiers.get(tier_num, [])
            if not tier_models:
                continue
            label, icon, color = _TIER_LABELS[tier_num]
            with ui.row().classes('items-center gap-2 mt-3 mb-1'):
                ui.icon(icon, color=color).classes('text-lg')
                ui.label(label).classes('text-sm font-bold')

            with ui.row().classes('gap-3 flex-wrap w-full'):
                for m in tier_models:
                    is_current = m.alias == config.model

                    def _select(alias=m.alias, current=is_current):
                        if current:
                            return
                        config.model = alias
                        save_config(config)
                        dlg.close()
                        ui.navigate.to('/')

                    ring = ' ring-2 ring-primary' if is_current else ''
                    cursor = '' if is_current else ' cursor-pointer'
                    with (
                        ui.card()
                        .classes(
                            f'px-4 py-3 model-card min-w-[150px] '
                            f'flex-1{ring}{cursor}'
                        )
                        .on('click', _select)
                    ):
                        ui.label(m.display_name).classes('font-bold text-sm')
                        with ui.row().classes('items-center gap-2 mt-1'):
                            ui.label(f'{m.alias}').classes('text-secondary text-xs')
                            if is_current:
                                ui.badge('current', color='primary').props('dense')
                            if m.is_default:
                                ui.badge('default', color='grey').props('dense')

        ui.button('Cancel', on_click=dlg.close).props('flat').classes('mt-4')
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
