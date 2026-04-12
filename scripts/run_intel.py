#!/usr/bin/env python3
"""Non-interactive CI runner for Skillnir intel pipelines.

Entry point for GitHub Actions. Runs ``research``, ``events``, or
``security`` via the Python API (NOT the interactive CLI, which uses
questionary prompts and would hang in CI), diffs the on-disk index
before/after the run, and POSTs each new item as a Google Chat card
via :func:`skillnir.notifications.send_gchat_item`.

Environment variables
---------------------
AI_AGENT_API_KEY         (required) — API key for the active AI agent tool.
                         The runner exports it to the env var the underlying
                         CLI expects (e.g. ``CURSOR_API_KEY`` for cursor).
AI_AGENT_TOOL            (optional, default "cursor") — which AI agent backend
                         to drive. Currently only ``cursor`` is supported;
                         other tools will be added as Skillnir gains support.
AI_AGENT_WEBHOOK_URL     (optional) — Google Chat webhook; omit to skip notifications
AI_AGENT_MODEL           (optional, default "auto") — primary model
AI_AGENT_MODEL_FALLBACK  (optional) — fallback model if the primary fails

Usage
-----
    python scripts/run_intel.py <feature> [--notify-limit N]

Where ``<feature>`` is one of ``research``, ``events``, ``security``.

Exit codes
----------
0  success (zero or more items notified)
1  configuration error (missing env var, unknown feature, unsupported tool)
2  pipeline failure (primary and fallback both failed)

Output
------
Progress lines on stdout as ``[<kind>] <message>``.
Final line is a single ``SUMMARY {...}`` JSON object with the run summary,
parseable by the surrounding workflow.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any

from skillnir.backends import AIBackend
from skillnir.notifications.senders import send_gchat_item

# ---------------------------------------------------------------------------
# AI agent tool registry
# ---------------------------------------------------------------------------
#
# Maps the user-facing AI_AGENT_TOOL value to:
#   - the Skillnir AIBackend enum to pass as backend_override
#   - the env var name the underlying CLI reads its API key from
#
# Add a new entry here when Skillnir gains support for another tool. The runner
# itself stays generic; only this table changes.
_TOOL_REGISTRY: dict[str, tuple[AIBackend, str]] = {
    "cursor": (AIBackend.CURSOR, "CURSOR_API_KEY"),
    # Future:
    # "claude":  (AIBackend.CLAUDE,  "ANTHROPIC_API_KEY"),
    # "gemini":  (AIBackend.GEMINI,  "GEMINI_API_KEY"),
    # "copilot": (AIBackend.COPILOT, "GITHUB_TOKEN"),
}


def _resolve_tool() -> AIBackend:
    """Read AI_AGENT_TOOL + AI_AGENT_API_KEY and prep the environment.

    Side effect: sets the underlying CLI's expected env var (e.g.
    ``CURSOR_API_KEY``) from ``AI_AGENT_API_KEY`` so the Skillnir
    backend subprocess can pick it up natively.

    Exits with code 1 on any configuration error.
    """
    tool = (os.environ.get("AI_AGENT_TOOL") or "cursor").strip().lower()
    api_key = (os.environ.get("AI_AGENT_API_KEY") or "").strip()

    if not api_key:
        _err("AI_AGENT_API_KEY is not set")
        sys.exit(1)

    if tool not in _TOOL_REGISTRY:
        supported = ", ".join(sorted(_TOOL_REGISTRY.keys()))
        _err(f"AI_AGENT_TOOL={tool!r} is not supported (supported: {supported})")
        sys.exit(1)

    backend, native_env_var = _TOOL_REGISTRY[tool]
    os.environ[native_env_var] = api_key
    _log(f"tool={tool} backend={backend.value} (api key passed via {native_env_var})")
    return backend


# ---------------------------------------------------------------------------
# Progress / logging
# ---------------------------------------------------------------------------


def _emit_progress(event: Any) -> None:
    """Stdout logger for Skillnir's GenerationProgress callbacks."""
    kind = getattr(event, "kind", None)
    content = getattr(event, "content", None)
    if kind is not None:
        print(f"[{kind}] {content}", flush=True)
    else:
        print(f"[progress] {event}", flush=True)


def _log(msg: str) -> None:
    print(f"[runner] {msg}", flush=True)


def _err(msg: str) -> None:
    print(f"[runner] ERROR: {msg}", file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Index file I/O
# ---------------------------------------------------------------------------


def _index_path_for(feature: str) -> Path:
    """Resolve the on-disk ``<feature>-index.json`` path.

    Uses Skillnir's own private directory resolvers so we locate the same
    path Skillnir itself writes to. Touching these underscore-prefixed
    helpers is a deliberate coupling — the alternative is duplicating the
    search logic.
    """
    if feature == "research":
        from skillnir.researcher import _get_research_dir

        return _get_research_dir() / "research-index.json"
    if feature == "events":
        from skillnir.events import _get_events_dir

        return _get_events_dir() / "events-index.json"
    if feature == "security":
        from skillnir.security import _get_security_dir

        return _get_security_dir() / "security-index.json"
    raise ValueError(f"unknown feature: {feature}")


def _load_index_items(index_path: Path) -> list[dict]:
    """Return the current list of items from an index file (empty on any error)."""
    if not index_path.exists():
        return []
    try:
        data = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        _err(f"failed to parse index at {index_path}: {exc}")
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def _ids_of(items: list[dict]) -> set[str]:
    return {str(item["id"]) for item in items if "id" in item}


# ---------------------------------------------------------------------------
# Feature → entry point dispatch
# ---------------------------------------------------------------------------


async def _run_feature(feature: str, model: str | None, backend: AIBackend) -> Any:
    """Invoke the matching Skillnir async entry point."""
    if feature == "research":
        from skillnir.researcher import research

        return await research(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
        )
    if feature == "events":
        from skillnir.events import search_events

        return await search_events(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
        )
    if feature == "security":
        from skillnir.security import search_security

        return await search_security(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
        )
    raise ValueError(f"unknown feature: {feature}")


def _run_with_fallback(feature: str, backend: AIBackend) -> tuple[Any, str, bool]:
    """Run the feature with the primary model; fall back on failure.

    Returns ``(result, model_used, fallback_used)``. Calls ``sys.exit(2)``
    if both the primary and fallback models fail.
    """
    primary = (os.environ.get("AI_AGENT_MODEL") or "auto").strip() or "auto"
    fallback = (os.environ.get("AI_AGENT_MODEL_FALLBACK") or "").strip() or None

    _log(
        f"feature={feature} primary_model={primary} "
        f"fallback_model={fallback or '<none>'}"
    )

    # Primary attempt
    try:
        result = asyncio.run(_run_feature(feature, primary, backend))
    except Exception as exc:  # noqa: BLE001 - we want to catch anything
        _err(f"primary model raised: {type(exc).__name__}: {exc}")
        result = None

    if result is not None and getattr(result, "success", False):
        return result, primary, False

    if result is not None:
        _err(f"primary model failed: {getattr(result, 'error', 'unknown error')}")

    if not fallback:
        _err("no fallback model configured; giving up")
        sys.exit(2)

    _log(f"retrying with fallback model: {fallback}")
    try:
        result = asyncio.run(_run_feature(feature, fallback, backend))
    except Exception as exc:  # noqa: BLE001
        _err(f"fallback model also raised: {type(exc).__name__}: {exc}")
        sys.exit(2)

    if not getattr(result, "success", False):
        _err(f"fallback model failed: {getattr(result, 'error', 'unknown')}")
        sys.exit(2)

    return result, fallback, True


# ---------------------------------------------------------------------------
# Per-feature field extraction for Google Chat cards
# ---------------------------------------------------------------------------


_DESCRIPTION_MAX_CHARS = 280


def _extract_card_fields(feature: str, item: dict) -> tuple[str, str, str]:
    """Map an index item dict to ``(title, description, reference_url)``.

    Handles feature-specific field names. Truncates description to keep
    Google Chat cards readable.
    """
    title = str(item.get("title") or "(no title)").strip()

    if feature == "research":
        description = str(item.get("summary") or "").strip()
        url = str(item.get("source_url") or "").strip()
    elif feature == "events":
        description = str(item.get("description") or "").strip()
        url = (
            str(item.get("event_url") or "").strip()
            or str(item.get("registration_url") or "").strip()
        )
    elif feature == "security":
        description = str(item.get("description") or "").strip()
        url = str(item.get("source_url") or "").strip()
    else:
        description = ""
        url = ""

    if len(description) > _DESCRIPTION_MAX_CHARS:
        description = description[: _DESCRIPTION_MAX_CHARS - 3].rstrip() + "..."

    return title, description, url


# ---------------------------------------------------------------------------
# Notification loop
# ---------------------------------------------------------------------------


def _notify_new_items(
    feature: str,
    new_items: list[dict],
    notify_limit: int,
) -> tuple[int, int, int]:
    """POST Google Chat cards for new items.

    Returns ``(notified, failures, truncated)`` where ``truncated`` is the
    number of items over the limit that were NOT posted.
    """
    webhook = (os.environ.get("AI_AGENT_WEBHOOK_URL") or "").strip()
    if not webhook:
        _log("AI_AGENT_WEBHOOK_URL not set; skipping notifications")
        return 0, 0, 0

    if not new_items:
        _log("no new items to notify about")
        return 0, 0, 0

    to_send = new_items[:notify_limit]
    truncated = max(0, len(new_items) - notify_limit)
    if truncated:
        _log(f"notifying {len(to_send)} item(s) (+{truncated} truncated, see artifact)")
    else:
        _log(f"notifying {len(to_send)} item(s)")

    notified = 0
    failures = 0
    for item in to_send:
        title, description, url = _extract_card_fields(feature, item)
        if not url:
            _log(f"skipping item without URL: {title}")
            continue
        ok, err = send_gchat_item(
            webhook,
            feature=feature,
            title=title,
            description=description,
            reference_url=url,
        )
        if ok:
            notified += 1
        else:
            failures += 1
            _err(f"notify failed for '{title}': {err}")

    return notified, failures, truncated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Non-interactive Skillnir intel runner (for CI)."
    )
    parser.add_argument(
        "feature",
        choices=["research", "events", "security"],
        help="Which intel pipeline to run.",
    )
    parser.add_argument(
        "--notify-limit",
        type=int,
        default=10,
        help="Maximum number of Google Chat cards to post per run (default: 10).",
    )
    args = parser.parse_args()

    backend = _resolve_tool()

    index_path = _index_path_for(args.feature)
    before_items = _load_index_items(index_path)
    before_ids = _ids_of(before_items)
    _log(f"pre-run index: {len(before_ids)} item(s) at {index_path}")

    result, model_used, fallback_used = _run_with_fallback(args.feature, backend)

    after_items = _load_index_items(index_path)
    after_ids = _ids_of(after_items)
    new_ids = after_ids - before_ids
    new_items = [item for item in after_items if item.get("id") in new_ids]
    _log(f"post-run index: {len(after_ids)} item(s), {len(new_items)} new")

    notified, failures, truncated = _notify_new_items(
        args.feature, new_items, args.notify_limit
    )

    summary = {
        "feature": args.feature,
        "tool_used": backend.value,
        "pre_run_count": len(before_ids),
        "post_run_count": len(after_ids),
        "new_count": len(new_items),
        "notified": notified,
        "notify_failures": failures,
        "truncated": truncated,
        "model_used": model_used,
        "fallback_used": fallback_used,
        "result_success": bool(getattr(result, "success", False)),
    }
    # Final line — machine-readable summary, prefixed so log scrapers can
    # find it reliably even if stdout contains other JSON blobs.
    print("SUMMARY " + json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
