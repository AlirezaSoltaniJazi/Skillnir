"""AI events and conferences page."""

import time

from nicegui import ui

from skillnir.ui.components.page_header import page_header
from skillnir.ui.components.progress_panel import (
    format_duration,
    progress_panel,
    start_elapsed_timer,
)
from skillnir.ui.components.result_card import result_card
from skillnir.ui.components.stat_card import stat_card
from skillnir.i18n import t, get_current_language
from skillnir.ui.layout import header, play_notification


@ui.page("/events")
async def page_events():
    from skillnir.backends import BACKENDS, load_config
    from skillnir.events import (
        EVENT_COUNTRIES,
        _get_events_dir,
        _load_index,
        search_events,
    )

    audio_el, sound_state = header()
    config = load_config()
    backend_info = BACKENDS[config.backend]
    lang = get_current_language()

    with ui.column().classes("w-full max-w-5xl mx-auto px-8 py-8 gap-6"):
        page_header(
            t("pages.events.title", lang),
            t("pages.events.subtitle", lang),
            icon="event",
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

        # ── Country chips ──
        selected_countries = list(EVENT_COUNTRIES.keys())

        ui.label(t("pages.events.countries_to_search", lang)).classes(
            "text-sm font-medium text-secondary"
        )
        country_chips_container = ui.row().classes("gap-2 flex-wrap")

        def _rebuild_country_chips():
            country_chips_container.clear()
            with country_chips_container:
                for key, label in EVENT_COUNTRIES.items():
                    is_sel = key in selected_countries

                    def _toggle(k=key):
                        if k in selected_countries:
                            selected_countries.remove(k)
                        else:
                            selected_countries.append(k)
                        _rebuild_country_chips()

                    sel_cls = (
                        "bg-primary text-white"
                        if is_sel
                        else "bg-transparent text-secondary border border-gray-600"
                    )
                    with (
                        ui.element("div")
                        .classes(
                            f"flex items-center gap-1.5 px-3 py-1 rounded-full "
                            f"cursor-pointer select-none text-sm {sel_cls}"
                        )
                        .on("click", _toggle)
                    ):
                        ui.image(f"/static/flags/{key}.png").classes(
                            "w-5 h-3.5 rounded-sm"
                        ).style("flex-shrink:0")
                        if is_sel:
                            ui.icon("check", size="14px")
                        ui.label(label).classes("text-sm whitespace-nowrap")

        _rebuild_country_chips()

        # ── Existing events ──
        events_dir = _get_events_dir()
        existing = _load_index(events_dir)
        if existing:
            with ui.row().classes("gap-4 flex-wrap"):
                stat_card(
                    str(len(existing)),
                    t("pages.events.events_in_kb", lang),
                    icon="event",
                    color="info",
                )

            def _cache_bust_url() -> str:
                return f"/events-files/index.html?t={int(time.time())}"

            index_path = events_dir / "index.html"
            if index_path.exists():
                with ui.row().classes("gap-3"):

                    def view_landing():
                        from skillnir.events import regenerate_landing

                        count, _ = regenerate_landing(events_dir)
                        if count:
                            ui.notify(
                                t(
                                    "pages.events.generated_html_pages",
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

                    def generate_html_files():
                        from skillnir.events import regenerate_landing

                        count, _ = regenerate_landing(events_dir)
                        if count:
                            ui.notify(
                                t(
                                    "pages.events.generated_html_pages",
                                    lang,
                                    count=str(count),
                                ),
                                type="positive",
                            )
                        else:
                            ui.notify(
                                t("pages.events.all_events_have_html", lang),
                                type="info",
                            )

                    ui.button(
                        t("buttons.generate_html_files", lang),
                        on_click=generate_html_files,
                        icon="code",
                    ).props("flat rounded")

        progress_container = ui.column().classes("w-full")
        results_container = ui.column().classes("w-full")

        async def do_search():
            start_time = time.time()
            if not selected_countries:
                ui.notify(
                    t("pages.events.select_at_least_one_country", lang), type="warning"
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
                    elif p.content.startswith("  Skipped"):
                        skip_count["value"] += 1
                        refs["lines"].text = str(skip_count["value"])
                elif p.kind == "text":
                    for text_line in p.content.splitlines():
                        _log_push(text_line)
                elif p.kind == "error":
                    _log_push(f"[ERROR] {p.content}")

            result = await search_events(
                on_progress=on_progress,
                countries=selected_countries,
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
                    t("pages.events.grid_events_found", lang): str(result.events_found),
                    t("pages.events.grid_new_events", lang): str(result.events_new),
                    t("pages.events.grid_skipped_dedup", lang): str(
                        result.events_skipped
                    ),
                    t("pages.events.grid_duration", lang): format_duration(secs),
                }
                result_card(
                    results_container,
                    True,
                    t("pages.events.result_success_title", lang),
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
                    t("pages.events.result_fail_title", lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes("gap-3 mt-4"):
                    ui.button(
                        t("buttons.search_again", lang),
                        on_click=lambda: ui.navigate.to("/events"),
                        icon="refresh",
                    ).props("unelevated rounded")
                    ui.button(
                        t("buttons.home", lang),
                        on_click=lambda: ui.navigate.to("/"),
                        icon="home",
                    ).props("flat rounded")

            play_notification(audio_el, sound_state)

        search_btn = ui.button(
            t("buttons.search_events", lang),
            on_click=do_search,
            icon="travel_explore",
        ).props("unelevated rounded color=positive")
