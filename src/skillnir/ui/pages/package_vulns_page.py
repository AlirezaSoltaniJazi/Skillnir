"""Package vulnerabilities research page."""

import time

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    progress_panel,
    start_elapsed_timer,
    survive_disconnect,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.components.stat_card import stat_card
from skillnir.ui.layout import header, play_notification


@ui.page("/package-vulns")
async def page_package_vulns():
    from skillnir.backends import BACKENDS, load_config
    from skillnir.package_vulns import (
        ECOSYSTEMS,
        _get_package_vulns_dir,
        _load_index,
        search_package_vulns,
    )

    audio_el, sound_state = header()
    config = load_config()
    backend_info = BACKENDS[config.backend]
    lang = get_current_language()

    with ui.column().classes("w-full max-w-5xl mx-auto px-8 py-8 gap-6"):
        page_header(
            t("pages.package_vulns.title", lang),
            t("pages.package_vulns.subtitle", lang),
            icon="inventory_2",
        )

        with ui.row().classes("items-center gap-2"):
            ui.icon(backend_info.icon, size="sm").classes("text-secondary")
            ui.label(
                t(
                    "messages.using_backend",
                    lang,
                    name=backend_info.name,
                    model=config.model,
                )
            ).classes("text-sm text-secondary")

        # ── Ecosystem chips ──
        selected_ecosystems = list(ECOSYSTEMS.keys())

        with ui.row().classes("items-center gap-3"):
            ui.label(t("pages.package_vulns.ecosystems_label", lang)).classes(
                "text-sm font-medium text-secondary"
            )

            def _select_all_ecosystems():
                selected_ecosystems.clear()
                selected_ecosystems.extend(ECOSYSTEMS.keys())
                _rebuild_ecosystem_chips()

            def _deselect_all_ecosystems():
                selected_ecosystems.clear()
                _rebuild_ecosystem_chips()

            ui.button(
                t("buttons.select_all", lang),
                on_click=_select_all_ecosystems,
                icon="check_box",
            ).props("flat rounded dense size=sm")
            ui.button(
                t("buttons.deselect_all", lang),
                on_click=_deselect_all_ecosystems,
                icon="check_box_outline_blank",
            ).props("flat rounded dense size=sm")
        ecosystem_chips_container = ui.row().classes("gap-2 flex-wrap")

        def _rebuild_ecosystem_chips():
            ecosystem_chips_container.clear()
            with ecosystem_chips_container:
                for key, label in ECOSYSTEMS.items():
                    is_sel = key in selected_ecosystems

                    def _toggle(k=key):
                        if k in selected_ecosystems:
                            selected_ecosystems.remove(k)
                        else:
                            selected_ecosystems.append(k)
                        _rebuild_ecosystem_chips()

                    if is_sel:
                        ui.chip(
                            label, icon="check", color="primary", on_click=_toggle
                        ).props("clickable")
                    else:
                        ui.chip(label, on_click=_toggle).props("clickable outline")

        _rebuild_ecosystem_chips()

        # ── Existing advisories ──
        pkg_dir = _get_package_vulns_dir()

        def _cache_bust_url() -> str:
            return f"/package-vulns-files/index.html?t={int(time.time())}"

        existing = _load_index(pkg_dir)
        if existing:
            with ui.row().classes("gap-4 flex-wrap"):
                stat_card(
                    str(len(existing)),
                    t("pages.package_vulns.vulns_in_kb", lang),
                    icon="inventory_2",
                    color="negative",
                )

            index_path = pkg_dir / "index.html"
            if index_path.exists():
                with ui.row().classes("gap-3"):

                    def view_landing():
                        from skillnir.package_vulns import regenerate_landing

                        count, _ = regenerate_landing(pkg_dir)
                        if count:
                            ui.notify(
                                t(
                                    "pages.package_vulns.regenerated_landing",
                                    lang,
                                    count=str(count),
                                ),
                                type="positive",
                            )
                        ui.navigate.to(_cache_bust_url(), new_tab=True)

                    ui.button(
                        t("buttons.view_landing_page", lang),
                        on_click=view_landing,
                        icon="open_in_new",
                    ).props("flat rounded")

        progress_container = ui.column().classes("w-full")
        results_container = ui.column().classes("w-full")

        @survive_disconnect
        async def do_search():
            start_time = time.time()
            if not selected_ecosystems:
                ui.notify(
                    t("pages.package_vulns.select_at_least_one_ecosystem", lang),
                    type="warning",
                )
                return

            search_btn.disable()
            results_container.clear()

            new_count = {"value": 0}
            skip_count = {"value": 0}
            log_lines: list[str] = []

            refs = progress_panel(progress_container, max_log_lines=500)
            timer_ctl = start_elapsed_timer(refs, start_time)

            def _log_push(line: str) -> None:
                log_lines.append(line)
                refs["log"].push(line)

            def on_progress(p) -> None:
                if p.kind == "phase":
                    refs["phase"].text = p.content
                    refs["status"].text = ""
                    _log_push(f"--- {p.content} ---")
                elif p.kind == "status":
                    refs["status"].text = p.content
                    _log_push(f"  {p.content}")
                    if p.content.startswith("  New:"):
                        new_count["value"] += 1
                        refs["tools"].text = str(new_count["value"])
                    elif p.content.startswith("  Updated:"):
                        skip_count["value"] += 1
                        refs["lines"].text = str(skip_count["value"])
                elif p.kind == "text":
                    for text_line in p.content.splitlines():
                        _log_push(text_line)
                elif p.kind == "error":
                    _log_push(f"[ERROR] {p.content}")

            result = await search_package_vulns(
                on_progress=on_progress,
                ecosystems=selected_ecosystems,
            )

            timer_ctl["active"] = False
            secs = int(time.time() - start_time)

            # Keep log visible
            progress_container.clear()
            with progress_container:
                log_visible = {"value": True}
                with ui.row().classes("items-center gap-3"):
                    ui.label(t("components.progress_panel.log_output", lang)).classes(
                        "text-sm font-medium text-secondary"
                    )

                    def toggle_log():
                        log_visible["value"] = not log_visible["value"]
                        saved_log.set_visibility(log_visible["value"])
                        toggle_btn.text = (
                            t("buttons.hide_log", lang)
                            if log_visible["value"]
                            else t("buttons.show_log", lang)
                        )

                    toggle_btn = ui.button(
                        t("buttons.hide_log", lang),
                        on_click=toggle_log,
                        icon="visibility_off",
                    ).props("flat rounded dense")
                saved_log = ui.log(max_lines=500).classes(
                    "w-full h-72 font-mono text-xs"
                )
                for prev_line in log_lines:
                    saved_log.push(prev_line)

            search_btn.enable()

            if result.success:
                grid = {
                    t("pages.package_vulns.grid_vulns_found", lang): str(
                        result.vulns_found
                    ),
                    t("pages.package_vulns.grid_new_vulns", lang): str(
                        result.vulns_new
                    ),
                    t("pages.package_vulns.grid_updated", lang): str(
                        result.vulns_skipped
                    ),
                    t("pages.package_vulns.grid_duration", lang): format_duration(secs),
                }
                result_card(
                    results_container,
                    True,
                    t("pages.package_vulns.result_success_title", lang),
                    grid_data=grid,
                )

                if result.index_path and result.index_path.exists():
                    with results_container:
                        ui.button(
                            t("buttons.open_landing_page", lang),
                            on_click=lambda: ui.navigate.to(
                                _cache_bust_url(), new_tab=True
                            ),
                            icon="open_in_new",
                        ).props("unelevated rounded color=positive").classes("mt-3")
            else:
                result_card(
                    results_container,
                    False,
                    t("pages.package_vulns.result_fail_title", lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes("gap-3 mt-4"):
                    ui.button(
                        t("buttons.search_again", lang),
                        on_click=lambda: ui.navigate.to("/package-vulns"),
                        icon="refresh",
                    ).props("unelevated rounded")
                    ui.button(
                        t("buttons.home", lang),
                        on_click=lambda: ui.navigate.to("/"),
                        icon="home",
                    ).props("flat rounded")

            play_notification(audio_el, sound_state, title="Package scan complete")

        search_btn = ui.button(
            t("buttons.search_package_vulns", lang),
            on_click=do_search,
            icon="inventory_2",
        ).props("unelevated rounded color=negative")
