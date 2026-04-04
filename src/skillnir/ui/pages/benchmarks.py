"""AI model benchmarks page."""

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


@ui.page("/benchmarks")
async def page_benchmarks():
    from skillnir.backends import BACKENDS, load_config
    from skillnir.benchmarks import (
        BENCHMARK_CATEGORIES,
        PROVIDER_LABELS,
        _get_benchmarks_dir,
        _load_index,
        search_benchmarks,
    )

    audio_el, sound_state = header()
    config = load_config()
    backend_info = BACKENDS[config.backend]
    lang = get_current_language()

    with ui.column().classes("w-full max-w-5xl mx-auto px-8 py-8 gap-6"):
        page_header(
            t("pages.benchmarks.title", lang),
            t("pages.benchmarks.subtitle", lang),
            icon="assessment",
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

        # ── Category chips (display only) ──
        ui.label(t("pages.benchmarks.categories_label", lang)).classes(
            "text-sm font-medium text-secondary"
        )
        with ui.row().classes("gap-2 flex-wrap"):
            for key, label in BENCHMARK_CATEGORIES.items():
                ui.chip(label, icon="check", color="primary").props("clickable=false")

        # ── Provider chips ──
        selected_providers: list[str] = []

        with ui.row().classes("items-center gap-3"):
            ui.label(t("pages.benchmarks.filter_by_provider", lang)).classes(
                "text-sm font-medium text-secondary"
            )

            def _select_all_providers():
                selected_providers.clear()
                selected_providers.extend(PROVIDER_LABELS.keys())
                _rebuild_provider_chips()

            def _deselect_all_providers():
                selected_providers.clear()
                _rebuild_provider_chips()

            ui.button(
                t("buttons.select_all", lang),
                on_click=_select_all_providers,
                icon="check_box",
            ).props("flat rounded dense size=sm")
            ui.button(
                t("buttons.deselect_all", lang),
                on_click=_deselect_all_providers,
                icon="check_box_outline_blank",
            ).props("flat rounded dense size=sm")
        provider_chips_container = ui.row().classes("gap-2 flex-wrap")

        def _rebuild_provider_chips():
            provider_chips_container.clear()
            with provider_chips_container:
                for key, label in PROVIDER_LABELS.items():
                    is_sel = key in selected_providers

                    def _toggle(k=key):
                        if k in selected_providers:
                            selected_providers.remove(k)
                        else:
                            selected_providers.append(k)
                        _rebuild_provider_chips()

                    if is_sel:
                        ui.chip(
                            label, icon="check", color="secondary", on_click=_toggle
                        ).props("clickable")
                    else:
                        ui.chip(label, on_click=_toggle).props("clickable outline")

        _rebuild_provider_chips()

        # ── Model count selector ──
        with ui.row().classes("items-center gap-3"):
            ui.label(t("pages.benchmarks.model_count_label", lang)).classes(
                "text-sm font-medium text-secondary"
            )
            model_count_select = (
                ui.select(
                    options={20: "Top 20", 30: "Top 30", 50: "Top 50"},
                    value=30,
                )
                .classes("w-32")
                .props("outlined dense rounded")
            )

        # ── Existing benchmarks ──
        benchmarks_dir = _get_benchmarks_dir()

        def _cache_bust_url() -> str:
            return f"/benchmarks-files/index.html?t={int(time.time())}"

        existing = _load_index(benchmarks_dir)
        if existing:
            with ui.row().classes("gap-4 flex-wrap"):
                stat_card(
                    str(len(existing)),
                    t("pages.benchmarks.models_in_kb", lang),
                    icon="assessment",
                    color="info",
                )

            index_path = benchmarks_dir / "index.html"
            if index_path.exists():
                with ui.row().classes("gap-3"):

                    def view_landing():
                        from skillnir.benchmarks import regenerate_landing

                        count, _ = regenerate_landing(benchmarks_dir)
                        if count:
                            ui.notify(
                                t(
                                    "pages.benchmarks.regenerated_landing",
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

            result = await search_benchmarks(
                on_progress=on_progress,
                model_count=model_count_select.value,
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
                    t("pages.benchmarks.grid_models_found", lang): str(
                        result.models_found
                    ),
                    t("pages.benchmarks.grid_new_models", lang): str(result.models_new),
                    t("pages.benchmarks.grid_updated", lang): str(
                        result.models_skipped
                    ),
                    t("pages.benchmarks.grid_duration", lang): format_duration(secs),
                }
                result_card(
                    results_container,
                    True,
                    t("pages.benchmarks.result_success_title", lang),
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
                    t("pages.benchmarks.result_fail_title", lang),
                    error=result.error,
                )

            with results_container:
                with ui.row().classes("gap-3 mt-4"):
                    ui.button(
                        t("buttons.search_again", lang),
                        on_click=lambda: ui.navigate.to("/benchmarks"),
                        icon="refresh",
                    ).props("unelevated rounded")
                    ui.button(
                        t("buttons.home", lang),
                        on_click=lambda: ui.navigate.to("/"),
                        icon="home",
                    ).props("flat rounded")

            play_notification(audio_el, sound_state)

        search_btn = ui.button(
            t("buttons.search_benchmarks", lang),
            on_click=do_search,
            icon="assessment",
        ).props("unelevated rounded color=positive")
