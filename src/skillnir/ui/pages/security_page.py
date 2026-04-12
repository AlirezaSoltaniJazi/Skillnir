"""Security vulnerabilities research page."""

import time

from nicegui import ui

from skillnir.i18n import get_current_language, t
from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.components.stat_card import stat_card
from skillnir.ui.layout import header, play_notification


@ui.page("/security")
async def page_security():
    from skillnir.backends import BACKENDS, load_config
    from skillnir.security import (
        SECURITY_CATEGORIES,
        SECURITY_SOURCES,
        _get_security_dir,
        _load_index,
        search_security,
    )

    audio_el, sound_state = header()
    config = load_config()
    backend_info = BACKENDS[config.backend]
    lang = get_current_language()

    with ui.column().classes("w-full max-w-5xl mx-auto px-8 py-8 gap-6"):
        page_header(
            t("pages.security.title", lang),
            t("pages.security.subtitle", lang),
            icon="security",
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

        # ── Category chips ──
        selected_categories = list(SECURITY_CATEGORIES.keys())

        with ui.row().classes("items-center gap-3"):
            ui.label(t("pages.security.categories_label", lang)).classes(
                "text-sm font-medium text-secondary"
            )

            def _select_all_categories():
                selected_categories.clear()
                selected_categories.extend(SECURITY_CATEGORIES.keys())
                _rebuild_category_chips()

            def _deselect_all_categories():
                selected_categories.clear()
                _rebuild_category_chips()

            ui.button(
                t("buttons.select_all", lang),
                on_click=_select_all_categories,
                icon="check_box",
            ).props("flat rounded dense size=sm")
            ui.button(
                t("buttons.deselect_all", lang),
                on_click=_deselect_all_categories,
                icon="check_box_outline_blank",
            ).props("flat rounded dense size=sm")
        category_chips_container = ui.row().classes("gap-2 flex-wrap")

        def _rebuild_category_chips():
            category_chips_container.clear()
            with category_chips_container:
                for key, label in SECURITY_CATEGORIES.items():
                    is_sel = key in selected_categories

                    def _toggle(k=key):
                        if k in selected_categories:
                            selected_categories.remove(k)
                        else:
                            selected_categories.append(k)
                        _rebuild_category_chips()

                    if is_sel:
                        ui.chip(
                            label, icon="check", color="primary", on_click=_toggle
                        ).props("clickable")
                    else:
                        ui.chip(label, on_click=_toggle).props("clickable outline")

        _rebuild_category_chips()

        # ── Source chips ──
        selected_sources: list[str] = []

        with ui.row().classes("items-center gap-3"):
            ui.label(t("pages.security.filter_by_source", lang)).classes(
                "text-sm font-medium text-secondary"
            )

            def _select_all_sources():
                selected_sources.clear()
                selected_sources.extend(SECURITY_SOURCES.keys())
                _rebuild_source_chips()

            def _deselect_all_sources():
                selected_sources.clear()
                _rebuild_source_chips()

            ui.button(
                t("buttons.select_all", lang),
                on_click=_select_all_sources,
                icon="check_box",
            ).props("flat rounded dense size=sm")
            ui.button(
                t("buttons.deselect_all", lang),
                on_click=_deselect_all_sources,
                icon="check_box_outline_blank",
            ).props("flat rounded dense size=sm")
        source_chips_container = ui.row().classes("gap-2 flex-wrap")

        def _rebuild_source_chips():
            source_chips_container.clear()
            with source_chips_container:
                for key, label in SECURITY_SOURCES.items():
                    is_sel = key in selected_sources

                    def _toggle(k=key):
                        if k in selected_sources:
                            selected_sources.remove(k)
                        else:
                            selected_sources.append(k)
                        _rebuild_source_chips()

                    if is_sel:
                        ui.chip(
                            label, icon="check", color="secondary", on_click=_toggle
                        ).props("clickable")
                    else:
                        ui.chip(label, on_click=_toggle).props("clickable outline")

        _rebuild_source_chips()

        # ── Existing vulnerabilities ──
        security_dir = _get_security_dir()

        def _cache_bust_url() -> str:
            return f"/security-files/index.html?t={int(time.time())}"

        existing = _load_index(security_dir)
        if existing:
            with ui.row().classes("gap-4 flex-wrap"):
                stat_card(
                    str(len(existing)),
                    t("pages.security.vulns_in_kb", lang),
                    icon="security",
                    color="negative",
                )

            index_path = security_dir / "index.html"
            if index_path.exists():
                with ui.row().classes("gap-3"):

                    def view_landing():
                        from skillnir.security import regenerate_landing

                        count, _ = regenerate_landing(security_dir)
                        if count:
                            ui.notify(
                                t(
                                    "pages.security.regenerated_landing",
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

        async def do_search():
            start_time = time.time()
            if not selected_categories:
                ui.notify(
                    t("pages.security.select_at_least_one_category", lang),
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

            result = await search_security(
                on_progress=on_progress,
                categories=selected_categories,
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
                    t("pages.security.grid_vulns_found", lang): str(result.vulns_found),
                    t("pages.security.grid_new_vulns", lang): str(result.vulns_new),
                    t("pages.security.grid_updated", lang): str(result.vulns_skipped),
                    t("pages.security.grid_duration", lang): format_duration(secs),
                }
                result_card(
                    results_container,
                    True,
                    t("pages.security.result_success_title", lang),
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
                    t("pages.security.result_fail_title", lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes("gap-3 mt-4"):
                    ui.button(
                        t("buttons.search_again", lang),
                        on_click=lambda: ui.navigate.to("/security"),
                        icon="refresh",
                    ).props("unelevated rounded")
                    ui.button(
                        t("buttons.home", lang),
                        on_click=lambda: ui.navigate.to("/"),
                        icon="home",
                    ).props("flat rounded")

            play_notification(audio_el, sound_state, title="Security scan complete")

        search_btn = ui.button(
            t("buttons.search_security", lang),
            on_click=do_search,
            icon="security",
        ).props("unelevated rounded color=negative")
