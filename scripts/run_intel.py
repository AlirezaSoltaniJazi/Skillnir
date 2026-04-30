#!/usr/bin/env python3
"""Non-interactive CI runner for Skillnir intel pipelines.

Entry point for GitHub Actions. Runs ``research``, ``events``,
``security``, or ``benchmarks`` via the Python API (NOT the interactive
CLI, which uses questionary prompts and would hang in CI), diffs the
on-disk index before/after the run, and POSTs a single consolidated
Google Chat message listing all new items.

Environment variables
---------------------
AI_AGENT_API_KEY              (required) — API key for the active AI agent tool.
AI_AGENT_TOOL                 (optional, default "cursor") — which AI agent backend.
AI_AGENT_WEBHOOK_URL          (optional) — Google Chat webhook; omit to skip notifications.
AI_AGENT_MODEL                (optional, default "auto") — primary model.
AI_AGENT_MODEL_FALLBACK       (optional) — fallback model if the primary fails.
AI_AGENT_EVENT_COUNTRIES      (optional) — comma-separated country codes (e.g. "uk,de").
                               Empty or unset = all countries.
AI_AGENT_RESEARCH_TOPICS      (optional) — comma-separated research topic keys.
                               Empty or unset = all topics.
AI_AGENT_TESTING_RESEARCH_TOPICS  (optional) — comma-separated testing-research topic keys.
                                   Empty or unset = all topics.
AI_AGENT_TESTING_RESEARCH_DATE_RANGE  (optional) — date-range filter string.
AI_AGENT_SECURITY_CATEGORIES  (optional) — comma-separated security category keys.
                               Empty or unset = all categories.
AI_AGENT_BENCHMARK_TOP_N      (optional, default "10") — how many top models to fetch.
AI_AGENT_NEWS_CATEGORIES      (optional) — comma-separated news category keys.
                               Empty or unset = all categories.
AI_AGENT_NEWS_RECENCY         (optional, default "7d") — one of "24h", "48h", "7d".

Usage
-----
    python scripts/run_intel.py <feature> [--notify-limit N]

Where ``<feature>`` is one of ``research``, ``testing-research``, ``events``,
``security``, ``benchmarks``, ``news``.

Exit codes
----------
0  success (zero or more items notified)
1  configuration error (missing env var, unknown feature, unsupported tool)
2  pipeline failure (primary and fallback both failed)
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
from skillnir.notifications.senders import send_gchat_intel_report

# ---------------------------------------------------------------------------
# AI agent tool registry
# ---------------------------------------------------------------------------

_TOOL_REGISTRY: dict[str, tuple[AIBackend, str]] = {
    "cursor": (AIBackend.CURSOR, "CURSOR_API_KEY"),
    # Future:
    # "claude":  (AIBackend.CLAUDE,  "ANTHROPIC_API_KEY"),
    # "gemini":  (AIBackend.GEMINI,  "GEMINI_API_KEY"),
    # "copilot": (AIBackend.COPILOT, "GITHUB_TOKEN"),
}


def _resolve_tool() -> AIBackend:
    """Read AI_AGENT_TOOL + AI_AGENT_API_KEY and prep the environment."""
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
# Env-var driven filter helpers
# ---------------------------------------------------------------------------


def _csv_env(name: str) -> list[str] | None:
    """Read a comma-separated env var. Returns None (= all) if unset/empty."""
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return None
    return [v.strip().lower() for v in raw.split(",") if v.strip()]


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
    """Resolve the on-disk ``<feature>-index.json`` path."""
    if feature == "research":
        from skillnir.researcher import _get_research_dir

        return _get_research_dir() / "research-index.json"
    if feature == "testing-research":
        from skillnir.testing_researcher import _get_testing_research_dir

        return _get_testing_research_dir() / "testing-research-index.json"
    if feature == "events":
        from skillnir.events import _get_events_dir

        return _get_events_dir() / "events-index.json"
    if feature == "security":
        from skillnir.security import _get_security_dir

        return _get_security_dir() / "security-index.json"
    if feature == "benchmarks":
        from skillnir.benchmarks import _get_benchmarks_dir

        return _get_benchmarks_dir() / "benchmarks-index.json"
    if feature == "news":
        from skillnir.news import _get_news_dir

        return _get_news_dir() / "news-index.json"
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
    """Invoke the matching Skillnir async entry point.

    All filter parameters are read from env vars at call time so the
    runner script itself stays generic — customization is done entirely
    from CI variables.
    """
    if feature == "research":
        from skillnir.researcher import research

        topics = _csv_env("AI_AGENT_RESEARCH_TOPICS")
        if topics:
            _log(f"research topics filter: {topics}")
        date_range = (
            os.environ.get("AI_AGENT_RESEARCH_DATE_RANGE") or ""
        ).strip() or None
        if date_range:
            _log(f"research date range: {date_range}")
        return await research(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            topics=topics,
            date_range=date_range,
        )

    if feature == "testing-research":
        from skillnir.testing_researcher import testing_research

        topics = _csv_env("AI_AGENT_TESTING_RESEARCH_TOPICS")
        if topics:
            _log(f"testing-research topics filter: {topics}")
        date_range = (
            os.environ.get("AI_AGENT_TESTING_RESEARCH_DATE_RANGE") or ""
        ).strip() or None
        if date_range:
            _log(f"testing-research date range: {date_range}")
        return await testing_research(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            topics=topics,
            date_range=date_range,
        )

    if feature == "events":
        from skillnir.events import search_events

        countries = _csv_env("AI_AGENT_EVENT_COUNTRIES")
        if countries:
            _log(f"events countries filter: {countries}")
        return await search_events(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            countries=countries,
        )

    if feature == "security":
        from skillnir.security import search_security

        categories = _csv_env("AI_AGENT_SECURITY_CATEGORIES")
        if categories:
            _log(f"security categories filter: {categories}")
        return await search_security(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            categories=categories,
        )

    if feature == "benchmarks":
        from skillnir.benchmarks import search_benchmarks

        top_n_str = (os.environ.get("AI_AGENT_BENCHMARK_TOP_N") or "10").strip()
        top_n = int(top_n_str) if top_n_str.isdigit() else 10
        _log(f"benchmarks model_count={top_n}")
        return await search_benchmarks(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            model_count=top_n,
        )

    if feature == "news":
        from skillnir.news import DEFAULT_RECENCY, NEWS_RECENCY, search_news

        categories = _csv_env("AI_AGENT_NEWS_CATEGORIES")
        if categories:
            _log(f"news categories filter: {categories}")
        recency = (
            os.environ.get("AI_AGENT_NEWS_RECENCY") or DEFAULT_RECENCY
        ).strip() or DEFAULT_RECENCY
        if recency not in NEWS_RECENCY:
            _log(f"unknown recency {recency!r}; falling back to {DEFAULT_RECENCY}")
            recency = DEFAULT_RECENCY
        _log(f"news recency: {recency}")
        return await search_news(
            on_progress=_emit_progress,
            backend_override=backend,
            model_override=model,
            categories=categories,
            recency=recency,
        )

    raise ValueError(f"unknown feature: {feature}")


def _run_with_fallback(feature: str, backend: AIBackend) -> tuple[Any, str, bool]:
    """Run the feature with the primary model; fall back on failure."""
    primary = (os.environ.get("AI_AGENT_MODEL") or "auto").strip() or "auto"
    fallback = (os.environ.get("AI_AGENT_MODEL_FALLBACK") or "").strip() or None

    _log(
        f"feature={feature} primary_model={primary} "
        f"fallback_model={fallback or '<none>'}"
    )

    try:
        result = asyncio.run(_run_feature(feature, primary, backend))
    except Exception as exc:  # noqa: BLE001
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
# Per-feature field extraction
# ---------------------------------------------------------------------------

_DESC_MAX = 150


def _extract_fields(
    feature: str, item: dict, desc_max: int = _DESC_MAX
) -> tuple[str, str, str]:
    """Map an index item dict to ``(title, description, reference_url)``."""
    title = str(item.get("title") or item.get("name") or "(no title)").strip()

    if feature in ("research", "testing-research"):
        topic = str(item.get("topic") or "").strip()
        pub_date = str(item.get("published_date") or "").strip()
        tag_parts = [p for p in [topic, pub_date] if p]
        tag = f"[{' - '.join(tag_parts)}] " if tag_parts else ""
        title = f"{tag}{title}"
        desc = str(item.get("summary") or "").strip()
        url = str(item.get("source_url") or "").strip()
    elif feature == "events":
        event_date = str(item.get("event_date") or "").strip()
        country = str(item.get("country") or "").strip().upper()
        topic = str(item.get("topic") or "").strip()
        is_free = item.get("is_free")
        price_label = "Free" if is_free else "Paid" if is_free is not None else ""
        tag_parts = [p for p in [event_date, country, topic, price_label] if p]
        tag = f"[{' - '.join(tag_parts)}] " if tag_parts else ""
        raw_desc = str(item.get("description") or "").strip()
        desc = f"{tag}{raw_desc}"
        url = (
            str(item.get("event_url") or "").strip()
            or str(item.get("registration_url") or "").strip()
        )
    elif feature == "security":
        severity = str(item.get("severity") or "").strip()
        cvss = item.get("cvss_score")
        raw_desc = str(item.get("description") or "").strip()
        if severity and cvss:
            desc = f"[{severity.upper()} - {cvss}] {raw_desc}"
        elif severity:
            desc = f"[{severity.upper()}] {raw_desc}"
        else:
            desc = raw_desc
        url = str(item.get("source_url") or "").strip()
    elif feature == "news":
        category = str(item.get("category") or "").strip()
        pub_date = str(item.get("published_date") or "").strip()
        tag_parts = [p for p in [category, pub_date] if p]
        tag = f"[{' - '.join(tag_parts)}] " if tag_parts else ""
        title = f"{tag}{title}"
        desc = str(item.get("summary") or "").strip()
        url = str(item.get("source_url") or "").strip()
    elif feature == "benchmarks":
        provider = str(item.get("provider") or "").strip()
        scores = item.get("category_scores") or {}
        coding = scores.get("coding")
        parts = ["[CODING]"]
        if provider:
            parts.append(f"by {provider}")
        if coding is not None:
            parts.append(f"score: {coding}")
        input_price = item.get("input_price")
        output_price = item.get("output_price")
        if input_price is not None and output_price is not None:
            parts.append(f"${input_price}/${output_price} per 1M tokens")
        ctx = item.get("context_window")
        if ctx:
            parts.append(
                f"{ctx // 1000}K ctx"
                if isinstance(ctx, int) and ctx >= 1000
                else f"{ctx} ctx"
            )
        desc = " | ".join(parts)
        url = ""  # no per-item URL — all models share the same leaderboard sources
    else:
        desc = ""
        url = ""

    if len(desc) > desc_max:
        desc = desc[: desc_max - 3].rstrip() + "..."

    return title, desc, url


# ---------------------------------------------------------------------------
# Consolidated notification (one message for all new items)
# ---------------------------------------------------------------------------


_DEFAULT_CHUNK_SIZE = 15


def _notify_new_items(
    feature: str,
    new_items: list[dict],
    notify_limit: int,
) -> bool:
    """Send Google Chat cards for new items, chunked to avoid size limits.

    Items are split into chunks of 15 and sent as separate messages with
    a 2-second delay between them. Returns True if all chunks succeeded.
    """
    webhook = (os.environ.get("AI_AGENT_WEBHOOK_URL") or "").strip()
    if not webhook:
        _log("AI_AGENT_WEBHOOK_URL not set; skipping notifications")
        return True

    if not new_items:
        _log("no new items to notify about")
        return True

    to_send = new_items[:notify_limit]
    overflow = max(0, len(new_items) - notify_limit)

    chunk_size_str = (os.environ.get("AI_AGENT_NOTIFY_CHUNK_SIZE") or "").strip()
    chunk_size = (
        int(chunk_size_str)
        if chunk_size_str.isdigit() and int(chunk_size_str) > 0
        else _DEFAULT_CHUNK_SIZE
    )

    desc_max_str = (os.environ.get("AI_AGENT_NOTIFY_DESC_MAX") or "").strip()
    desc_max = (
        int(desc_max_str)
        if desc_max_str.isdigit() and int(desc_max_str) > 0
        else _DESC_MAX
    )

    button_text = (
        os.environ.get("AI_AGENT_NOTIFY_BUTTON_TEXT") or ""
    ).strip() or "View source"
    subtitle_template = (
        os.environ.get("AI_AGENT_NOTIFY_SUBTITLE") or ""
    ).strip() or "{feature} — {count} new item(s)"
    overflow_text = (
        os.environ.get("AI_AGENT_NOTIFY_OVERFLOW_TEXT") or ""
    ).strip() or "+{count} more — see workflow artifact"

    items_for_card: list[tuple[str, str, str]] = []
    for item in to_send:
        title, desc, url = _extract_fields(feature, item, desc_max=desc_max)
        items_for_card.append((title, desc, url))

    chunk_count = (len(items_for_card) + chunk_size - 1) // chunk_size
    _log(
        f"sending {len(items_for_card)} item(s) in {chunk_count} "
        f"chunk(s) of {chunk_size}"
    )

    # Enrich feature label for the card subtitle
    feature_label = feature
    footer_urls: list[tuple[str, str]] = []
    if feature == "benchmarks":
        feature_label = "benchmarks sorted by coding"
        footer_urls = [
            ("Chatbot Arena", "https://arena.ai/leaderboard/code"),
            (
                "Artificial Analysis",
                "https://artificialanalysis.ai/leaderboards/models",
            ),
            ("SWE-bench", "https://www.swebench.com/"),
        ]

    ok, err = send_gchat_intel_report(
        webhook,
        feature=feature_label,
        items=items_for_card,
        overflow_count=overflow,
        chunk_size=chunk_size,
        button_text=button_text,
        subtitle_template=subtitle_template,
        overflow_text=overflow_text,
        footer_urls=footer_urls,
    )
    if ok:
        _log(f"all {chunk_count} chunk(s) sent successfully")
    else:
        _err(f"notification failed: {err}")
    return ok


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Non-interactive Skillnir intel runner (for CI)."
    )
    parser.add_argument(
        "feature",
        choices=[
            "research",
            "testing-research",
            "events",
            "security",
            "benchmarks",
            "news",
        ],
        help="Which intel pipeline to run.",
    )
    parser.add_argument(
        "--notify-limit",
        type=int,
        default=100,
        help="Max items to include in the notification card (default: 100).",
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

    notified = _notify_new_items(args.feature, new_items, args.notify_limit)

    summary = {
        "feature": args.feature,
        "tool_used": backend.value,
        "pre_run_count": len(before_ids),
        "post_run_count": len(after_ids),
        "new_count": len(new_items),
        "notified": notified,
        "model_used": model_used,
        "fallback_used": fallback_used,
        "result_success": bool(getattr(result, "success", False)),
    }
    print("SUMMARY " + json.dumps(summary), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
