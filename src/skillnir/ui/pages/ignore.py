"""Install ignore files page for the NiceGUI web interface."""

from pathlib import Path

from nicegui import ui

from skillnir.i18n import get_current_language
from skillnir.ui.components.page_header import page_header
from skillnir.ui.layout import header


@ui.page("/install-ignore")
def page_install_ignore():
    get_current_language()
    header()

    from skillnir.injector import inject_ignore
    from skillnir.scaffold import (
        get_ignore_templates,
        init_ignore,
    )
    from skillnir.tools import TOOLS, detect_tools

    templates = get_ignore_templates()
    tools_with_ignore = [t for t in TOOLS if t.ignore_file]

    # State
    selected_templates: dict[str, bool] = {name: False for name in templates}
    selected_tools: dict[str, bool] = {}
    preview_code = ui.element  # placeholder

    with ui.column().classes("w-full max-w-5xl mx-auto px-8 py-8 gap-6"):
        page_header(
            "Install Ignore Files",
            "Select ignore templates and AI tools, then inject ignore files into your project",
            icon="visibility_off",
        )

        # ── Target project root ──
        with ui.card().classes("w-full p-6").props("flat bordered"):
            target_input = (
                ui.input("Target project root", value=str(Path.cwd()))
                .classes("w-full max-w-xl")
                .props("outlined dense rounded")
            )

        # ── Template selection ──
        with ui.card().classes("w-full p-6").props("flat bordered"):
            ui.label("Ignore Templates").classes("text-lg font-semibold mb-1")
            ui.label(
                "Select which file types to ignore. Common patterns (Skillnir data, .git, OS files) are always included."
            ).classes("text-sm text-secondary mb-4")

            with ui.row().classes("gap-2 mb-4"):

                def select_all():
                    for name in selected_templates:
                        selected_templates[name] = True
                    for cb in template_checkboxes.values():
                        cb.value = True
                    update_preview()

                def deselect_all():
                    for name in selected_templates:
                        selected_templates[name] = False
                    for cb in template_checkboxes.values():
                        cb.value = False
                    update_preview()

                ui.button("Select All", on_click=select_all, icon="check_box").props(
                    "flat dense size=sm"
                )
                ui.button(
                    "Deselect All",
                    on_click=deselect_all,
                    icon="check_box_outline_blank",
                ).props("flat dense size=sm")

            template_checkboxes: dict[str, ui.checkbox] = {}
            with ui.grid(columns=2).classes("w-full gap-2"):
                for name, desc in templates.items():

                    def make_handler(n):
                        def handler(e):
                            selected_templates[n] = e.value
                            update_preview()

                        return handler

                    cb = ui.checkbox(desc, on_change=make_handler(name))
                    template_checkboxes[name] = cb

        # ── Tool selection ──
        with ui.card().classes("w-full p-6").props("flat bordered"):
            ui.label("AI Tools").classes("text-lg font-semibold mb-1")
            ui.label(
                "Select which tools to create ignore files for. "
                "Only tools with documented ignore file support are shown."
            ).classes("text-sm text-secondary mb-4")

            def detect_and_select():
                target = Path(target_input.value).resolve()
                detected = detect_tools(target)
                detected_names = {t.name for t in detected}
                for tool in tools_with_ignore:
                    if tool.name in detected_names:
                        selected_tools[tool.name] = True
                        if tool.name in tool_checkboxes:
                            tool_checkboxes[tool.name].value = True

            ui.button(
                "Auto-detect installed tools",
                on_click=detect_and_select,
                icon="search",
            ).props("flat dense size=sm").classes("mb-4")

            with ui.row().classes("gap-2 mb-4"):

                def select_all_tools():
                    for tool in tools_with_ignore:
                        selected_tools[tool.name] = True
                        if tool.name in tool_checkboxes:
                            tool_checkboxes[tool.name].value = True

                def deselect_all_tools():
                    for tool in tools_with_ignore:
                        selected_tools[tool.name] = False
                        if tool.name in tool_checkboxes:
                            tool_checkboxes[tool.name].value = False

                ui.button(
                    "Select All", on_click=select_all_tools, icon="check_box"
                ).props("flat dense size=sm")
                ui.button(
                    "Deselect All",
                    on_click=deselect_all_tools,
                    icon="check_box_outline_blank",
                ).props("flat dense size=sm")

            tool_checkboxes: dict[str, ui.checkbox] = {}
            with ui.grid(columns=3).classes("w-full gap-2"):
                for tool in tools_with_ignore:

                    def make_tool_handler(tool_name):
                        def handler(e):
                            selected_tools[tool_name] = e.value

                        return handler

                    cb = ui.checkbox(
                        f"{tool.name} ({tool.ignore_file})",
                        on_change=make_tool_handler(tool.name),
                    )
                    tool_checkboxes[tool.name] = cb

        # ── Preview ──
        with ui.card().classes("w-full p-6").props("flat bordered"):
            ui.label("Preview").classes("text-lg font-semibold mb-2")
            preview_container = ui.column().classes("w-full")
            with preview_container:
                preview_code = ui.code(
                    "# Select templates above to preview", language="bash"
                ).classes("w-full")

        def update_preview():
            from skillnir.scaffold import assemble_ignore

            chosen = [n for n, v in selected_templates.items() if v]
            if chosen:
                content = assemble_ignore(chosen)
            else:
                content = "# Select templates above to preview"
            preview_container.clear()
            with preview_container:
                ui.code(content, language="bash").classes("w-full")

        # ── Results ──
        results_container = ui.column().classes("w-full")

        def do_install():
            target = Path(target_input.value).resolve()
            if not target.is_dir():
                ui.notify(f"Directory not found: {target}", type="negative")
                return

            chosen_templates = [n for n, v in selected_templates.items() if v]
            if not chosen_templates:
                ui.notify("No templates selected.", type="warning")
                return

            chosen_tools = [t for t in tools_with_ignore if selected_tools.get(t.name)]
            if not chosen_tools:
                ui.notify("No tools selected.", type="warning")
                return

            ignore_files = [t.ignore_file for t in chosen_tools]

            # Step 1: Create .data/ignore/ with assembled content
            scaffold_result = init_ignore(target, chosen_templates, ignore_files)
            if not scaffold_result.success:
                ui.notify(
                    f"Error creating ignore files: {scaffold_result.error}",
                    type="negative",
                )
                return

            # Step 2: Create symlinks
            inject_results = inject_ignore(target, chosen_tools)

            results_container.clear()
            with results_container:
                created = [r for r in inject_results if r.created]
                skipped = [r for r in inject_results if not r.created and not r.error]
                errors = [r for r in inject_results if r.error]

                with ui.card().classes("w-full p-5 fade-in").props("flat bordered"):
                    ui.label("Injection Report").classes("text-lg font-semibold mb-3")

                    if created:
                        ui.label(f"Created ({len(created)}):").classes(
                            "font-medium text-positive"
                        )
                        for r in created:
                            ui.label(f"  + {r.symlink_path}").classes(
                                "text-sm text-green-400 font-mono"
                            )

                    if skipped:
                        ui.label(f"Already existed ({len(skipped)}):").classes(
                            "font-medium text-secondary mt-2"
                        )
                        for r in skipped:
                            ui.label(f"  = {r.symlink_path}").classes(
                                "text-sm text-secondary font-mono"
                            )

                    if errors:
                        ui.label(f"Errors ({len(errors)}):").classes(
                            "font-medium text-negative mt-2"
                        )
                        for r in errors:
                            ui.label(f"  ! {r.tool.name}: {r.error}").classes(
                                "text-sm text-red-400 font-mono"
                            )

                    ui.label(
                        f"\n{len(created)} created, {len(skipped)} skipped, {len(errors)} errors."
                    ).classes("mt-3 font-medium")

            ui.notify(
                f"Done! {len(created)} ignore files injected.",
                type="positive",
            )

        ui.button(
            "Install Ignore Files",
            on_click=do_install,
            icon="visibility_off",
        ).props("unelevated rounded color=positive")
