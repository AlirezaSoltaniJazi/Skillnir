"""Path input with a browser-persisted recent-paths history.

A single reusable element for every "target project root" field. It renders a
normal text input plus a list of recently-used paths (persisted per browser via
``app.storage.user``). Each recent path is a clickable chip that fills the input,
with a built-in remove (✕) button to drop it from the history.

The pure list logic lives in :func:`merge_recent_paths` so it is unit-testable
without a NiceGUI runtime.
"""

from functools import partial
from pathlib import Path
from typing import Callable

from nicegui import app, ui

from skillnir.i18n import get_current_language, t

DEFAULT_STORAGE_KEY = "recent_target_paths"
MAX_RECENT = 10


def merge_recent_paths(
    existing: list[str], new_path: str, max_items: int = MAX_RECENT
) -> list[str]:
    """Return ``existing`` with ``new_path`` moved to the front (deduped, capped).

    Pure function — no storage, no UI. Empty / whitespace paths are ignored.
    ``~`` is expanded so the same directory is never stored twice.
    """
    norm = (new_path or "").strip()
    if not norm:
        return list(existing)
    norm = str(Path(norm).expanduser())
    deduped = [p for p in existing if p != norm]
    deduped.insert(0, norm)
    return deduped[:max_items]


def _load_recent(storage_key: str) -> list[str]:
    """Read the recent-paths list from per-browser storage (empty on any error)."""
    try:
        value = app.storage.user.get(storage_key, [])
    except Exception:
        return []
    if not isinstance(value, list):
        return []
    return [str(p) for p in value]


def _store_recent(storage_key: str, paths: list[str]) -> None:
    """Persist the recent-paths list to per-browser storage (best-effort)."""
    try:
        app.storage.user[storage_key] = paths
    except Exception:
        pass


def _display(path: str) -> str:
    """Collapse the home directory to ``~`` for a shorter chip label."""
    try:
        home = str(Path.home())
        if path == home:
            return "~"
        if path.startswith(home + "/"):
            return "~" + path[len(home) :]
    except Exception:
        pass
    return path


def path_input_with_history(
    label: str,
    *,
    value: str = "",
    storage_key: str = DEFAULT_STORAGE_KEY,
    lang: str | None = None,
    max_items: int = MAX_RECENT,
    only_existing_dirs: bool = True,
    on_select: Callable[[str], None] | None = None,
    classes: str = "w-full max-w-xl",
    props: str = "outlined dense rounded",
) -> ui.input:
    """Render a path input plus a browser-persisted recent-paths list.

    Returns the underlying :class:`ui.input` so callers read ``.value`` exactly as
    they did before adopting this component. A path is remembered when the input
    loses focus (and, when ``only_existing_dirs`` is set, only if it resolves to a
    real directory — so half-typed paths are not stored).
    """
    if lang is None:
        lang = get_current_language()

    field = ui.input(label, value=value).classes(classes).props(props)
    recent_container = ui.column().classes("w-full max-w-xl gap-1 mt-1")

    def _render() -> None:
        recent_container.clear()
        paths = _load_recent(storage_key)
        if not paths:
            return
        with recent_container:
            ui.label(t("components.path_history.recent", lang)).classes(
                "text-xs uppercase tracking-wide text-secondary"
            )
            with ui.row().classes("w-full flex-wrap gap-2 items-center"):
                for stored in paths:
                    chip = (
                        ui.chip(
                            _display(stored),
                            icon="folder",
                            removable=True,
                            on_click=partial(_choose, stored),
                        )
                        .props("clickable")
                        .classes("cursor-pointer normal-case")
                    )
                    chip.tooltip(stored)
                    chip.on("remove", partial(_delete, stored))

    def _choose(stored: str) -> None:
        field.value = stored
        if on_select is not None:
            on_select(stored)

    def _delete(stored: str) -> None:
        remaining = [p for p in _load_recent(storage_key) if p != stored]
        _store_recent(storage_key, remaining)
        _render()

    def _remember() -> None:
        raw = (field.value or "").strip()
        if not raw:
            return
        if only_existing_dirs and not Path(raw).expanduser().is_dir():
            return
        merged = merge_recent_paths(_load_recent(storage_key), raw, max_items)
        _store_recent(storage_key, merged)
        _render()

    field.on("blur", lambda: _remember())
    _render()
    return field
