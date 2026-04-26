"""AI news pipeline: search the web for fresh AI news headlines, dedup, generate landing page.

Sibling of :mod:`skillnir.researcher` (long-form articles) and
:mod:`skillnir.events` (conferences). Where ``researcher`` produces
deeply-summarized articles and ``events`` lists upcoming conferences,
this module produces *short, fresh* news items (model releases, funding,
regulation, research breakthroughs, product launches) within a
user-selectable recency window (24h / 48h / 7d).

Same data-model / dedup / subprocess flow as researcher; only the
domain (categories, recency, prompt focus, output dir) differs.
"""

import asyncio
import html
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_subprocess_command,
    load_config,
    parse_stream_line,
)
from skillnir.generator import GenerationProgress, _emit

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class NewsItem:
    """A single AI news headline with a one-line summary."""

    id: str  # sourcename-YYYY-MM-DD-slug (dedup key)
    title: str
    source_url: str
    source_name: str
    published_date: str  # YYYY-MM-DD
    category: str  # key from NEWS_CATEGORIES
    summary: str = ""


@dataclass
class NewsResult:
    """Result of a news pipeline run."""

    success: bool
    items_found: int = 0
    items_new: int = 0
    items_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Categories — fixed taxonomy
# ---------------------------------------------------------------------------

NEWS_CATEGORIES: dict[str, str] = {
    "model-releases": "Model Releases",
    "funding": "Funding & Acquisitions",
    "regulation": "Regulation & Policy",
    "research": "Research Breakthroughs",
    "product": "Product Launches",
}

NEWS_CATEGORY_QUERIES: dict[str, str] = {
    "model-releases": (
        "new AI model release announcement Anthropic OpenAI Google Meta Mistral "
        "DeepSeek Qwen Llama"
    ),
    "funding": ("AI startup funding round Series A B C acquisition merger valuation"),
    "regulation": (
        "AI regulation policy law executive order EU AI Act White House FTC "
        "court ruling enforcement"
    ),
    "research": (
        "AI research paper breakthrough arXiv NeurIPS ICML ICLR benchmark "
        "state-of-the-art SOTA"
    ),
    "product": (
        "AI product launch feature release general availability GA enterprise "
        "developer tool integration"
    ),
}


# ---------------------------------------------------------------------------
# Recency windows — user-selectable
# ---------------------------------------------------------------------------

NEWS_RECENCY: dict[str, int] = {
    "24h": 1,
    "48h": 2,
    "7d": 7,
}

DEFAULT_RECENCY = "7d"


def _recency_hint(recency: str) -> str:
    """Render the recency key into a human-readable date hint for the prompt."""
    days = NEWS_RECENCY.get(recency, NEWS_RECENCY[DEFAULT_RECENCY])
    if days == 1:
        return "published in the last 24 hours — strictly exclude anything older"
    if days == 2:
        return "published in the last 48 hours — strictly exclude anything older"
    return f"published in the last {days} days — strictly exclude anything older"


# ---------------------------------------------------------------------------
# Preferred sources — high-signal AI-news outlets
# ---------------------------------------------------------------------------

PREFERRED_SOURCES: tuple[str, ...] = (
    "anthropic.com",
    "openai.com",
    "ai.googleblog.com",
    "deepmind.google",
    "ai.meta.com",
    "research.microsoft.com",
    "huggingface.co",
    "techcrunch.com",
    "theverge.com",
    "venturebeat.com",
    "thenewstack.io",
    "wired.com",
    "technologyreview.com",
    "spectrum.ieee.org",
    "reuters.com",
    "bloomberg.com",
    "ft.com",
    "wsj.com",
    "axios.com",
    "theinformation.com",
    "semianalysis.com",
    "stratechery.com",
    "simonwillison.net",
    "arxiv.org",
    "github.blog",
    "blog.langchain.dev",
    "www.llamaindex.ai",
    "newsletter.theaiedge.io",
    "read.deeplearning.ai",
)


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_NEWS_PROMPT = """\
You are a fresh AI news scout. Your task is to search the web for SHORT, RECENT \
news items — not long-form articles. Headlines + a one-line summary, nothing more.

## Instructions

For the category below, find 5-8 recent news items ({date_hint}). For EACH item:

1. **Search** for the freshest news matching the category — model releases, funding \
rounds, regulatory moves, research breakthroughs, or product launches
2. **Confirm** the item falls within the recency window — discard anything older
3. **Extract** the title, source, URL, and publication date
4. **Write** a one-sentence summary (under 200 characters) — what happened, no fluff

## Output Format

Return EXACTLY this JSON array (no markdown, no explanation, ONLY the JSON):

```json
[
  {{
    "id": "sourcename-YYYY-MM-DD-slug",
    "title": "Headline",
    "source_url": "https://...",
    "source_name": "Source Name",
    "published_date": "YYYY-MM-DD",
    "category": "CATEGORY_KEY",
    "summary": "One-sentence summary under 200 characters."
  }}
]
```

## Rules
- `id` format: lowercase source name (no spaces, hyphens) + date + short slug, \
e.g., `anthropic-2026-04-25-claude-opus-47`
- `published_date`: YYYY-MM-DD; must be within the recency window
- `category`: use the CATEGORY_KEY provided below
- `summary`: ONE sentence, under 200 characters, factual — no hype words
- Skip opinion pieces, listicles, and re-publications of older items
- Prefer official announcements (vendor blogs, press releases) and reputable wires \
(Reuters, Bloomberg, The Information) over aggregators

## Preferred Sources

Prioritize these high-signal outlets when content exists. You are NOT limited to \
these — include excellent items from other sources — but check these first:

{sources_list}

## Category to Search

CATEGORY_KEY: {category_key}
SEARCH_QUERY: {search_query}

## Existing News IDs (skip these — already in our knowledge base)

{existing_ids}
"""


# ---------------------------------------------------------------------------
# Index persistence
# ---------------------------------------------------------------------------


def _get_news_dir() -> Path:
    """Find skillnir's own .data/news/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / "news"
        if candidate.parent.is_dir():
            candidate.mkdir(parents=True, exist_ok=True)
            (candidate / "items").mkdir(exist_ok=True)
            return candidate
        current = current.parent
    fallback = Path.cwd() / ".data" / "news"
    fallback.mkdir(parents=True, exist_ok=True)
    (fallback / "items").mkdir(exist_ok=True)
    return fallback


def _load_index(news_dir: Path) -> dict[str, NewsItem]:
    """Load existing news-index.json for dedup."""
    index_file = news_dir / "news-index.json"
    if not index_file.exists():
        return {}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        return {item["id"]: NewsItem(**item) for item in data}
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(news_dir: Path, items: dict[str, NewsItem]) -> None:
    """Persist news registry."""
    index_file = news_dir / "news-index.json"
    data = [
        asdict(n)
        for n in sorted(items.values(), key=lambda n: n.published_date, reverse=True)
    ]
    index_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# News markdown writer
# ---------------------------------------------------------------------------


def _write_news_md(item: NewsItem, items_dir: Path) -> Path:
    """Write a single news item as markdown."""
    cat_dir = items_dir / item.category
    cat_dir.mkdir(exist_ok=True)
    md_path = cat_dir / f"{item.id}.md"
    content = f"""\
---
id: {item.id}
title: "{item.title}"
source: {item.source_url}
source_name: {item.source_name}
published: {item.published_date}
category: {item.category}
---

# {item.title}

**Source**: [{item.source_name}]({item.source_url}) | **Published**: {item.published_date} | **Category**: {NEWS_CATEGORIES.get(item.category, item.category)}

## Summary

{item.summary}
"""
    md_path.write_text(content, encoding="utf-8")
    return md_path


# ---------------------------------------------------------------------------
# Landing page HTML generator
# ---------------------------------------------------------------------------


def _generate_landing_html(
    items: dict[str, NewsItem],
    news_dir: Path,
    new_ids: set[str] | None = None,
) -> Path:
    """Generate index.html landing page sorted by date."""
    sorted_items = sorted(items.values(), key=lambda n: n.published_date, reverse=True)
    new_ids = new_ids or set()

    category_colors = {
        "model-releases": "#6366f1",
        "funding": "#10b981",
        "regulation": "#f59e0b",
        "research": "#06b6d4",
        "product": "#ec4899",
    }

    rows = []
    for n in sorted_items:
        color = category_colors.get(n.category, "#6b7280")
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;margin-left:8px;">NEW</span>'
            if n.id in new_ids
            else ""
        )
        title_escaped = html.escape(n.title)
        source_escaped = html.escape(n.source_name)
        source_url = html.escape(n.source_url, quote=True)
        summary_escaped = html.escape(n.summary)
        cat_label = NEWS_CATEGORIES.get(n.category, n.category)
        rows.append(f"""\
        <tr onclick="window.open('{source_url}','_blank')" style="cursor:pointer;" class="row" data-topic="{n.category}" data-source="{html.escape(n.source_name, quote=True)}">
          <td style="padding:12px 16px;">
            <div style="font-weight:600;color:#e2e8f0;">{title_escaped}{badge}</div>
            <div style="font-size:13px;color:#94a3b8;margin-top:4px;">{summary_escaped}</div>
          </td>
          <td style="padding:12px 16px;color:#94a3b8;white-space:nowrap;">{source_escaped}</td>
          <td style="padding:12px 16px;white-space:nowrap;">
            <span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{cat_label}</span>
          </td>
          <td style="padding:12px 16px;color:#94a3b8;font-family:monospace;font-size:13px;white-space:nowrap;">{n.published_date}</td>
        </tr>""")

    rows_html = "\n".join(rows)

    cat_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    for n in sorted_items:
        cat_counts[n.category] = cat_counts.get(n.category, 0) + 1
        source_counts[n.source_name] = source_counts.get(n.source_name, 0) + 1

    all_chip = (
        '<span class="chip topic-chip active" data-filter="all" '
        'onclick="toggleTopic(\'all\')" '
        'style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;'
        f'font-size:12px;cursor:pointer;">All Categories: {len(sorted_items)}</span>'
    )
    cat_chips = " ".join(
        f'<span class="chip topic-chip" data-filter="{c}" '
        f'onclick="toggleTopic(\'{c}\')" '
        f'style="background:{category_colors.get(c, "#6b7280")};color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;">{NEWS_CATEGORIES.get(c, c)}: {count}</span>'
        for c, count in sorted(cat_counts.items(), key=lambda x: -x[1])
    )
    stats_chips = all_chip + " " + cat_chips

    all_source_chip = (
        '<span class="chip source-chip active" data-filter="all" '
        'onclick="toggleSource(\'all\')" '
        'style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;'
        f'font-size:12px;cursor:pointer;">All Sources: {len(sorted_items)}</span>'
    )
    source_chips = " ".join(
        f'<span class="chip source-chip" '
        f'data-filter="{html.escape(s, quote=True)}" '
        f'onclick="toggleSource(this.dataset.filter)" '
        f'style="background:#64748b;color:#fff;padding:4px 12px;'
        f'border-radius:16px;font-size:12px;cursor:pointer;opacity:0.7;">'
        f'{html.escape(s)}: {count}</span>'
        for s, count in sorted(source_counts.items(), key=lambda x: -x[1])
    )
    source_chips_html = all_source_chip + " " + source_chips

    total = len(sorted_items)
    last_updated = sorted_items[0].published_date if sorted_items else "N/A"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = (
        f"{total} news items | Last updated: {last_updated}"
        f" | Generated: {generated_at}"
    )

    template = _load_template("landing.html")
    page_html = (
        template.replace("<!-- SUBTITLE -->", subtitle)
        .replace("<!-- TOPIC_CHIPS -->", stats_chips)
        .replace("<!-- SOURCE_CHIPS -->", source_chips_html)
        .replace("<!-- TABLE_ROWS -->", rows_html)
        .replace("<!-- TOTAL_ARTICLES -->", str(total))
    )

    index_path = news_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


def _load_template(name: str) -> str:
    """Load an HTML template from the resources directory."""
    template_path = Path(__file__).parent / "resources" / name
    return template_path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# AI response parser
# ---------------------------------------------------------------------------


def _parse_news_json(text: str, category_key: str) -> list[NewsItem]:
    """Parse a JSON array of news items from AI response text."""
    items: list[NewsItem] = []

    code_blocks = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    for block in code_blocks:
        items.extend(_try_parse_json_array(block, category_key))
        if items:
            return items

    all_arrays = re.findall(
        r"\[\s*\{[^[\]]*\"id\"[^[\]]*\"title\"[\s\S]*?\}\s*\]", text
    )
    for arr in reversed(all_arrays):
        items.extend(_try_parse_json_array(arr, category_key))
        if items:
            return items

    obj_pattern = r'\{\s*"id"\s*:\s*"[^"]+"\s*,\s*"title"\s*:\s*"[^"]+"[\s\S]*?\}'
    for obj_match in re.finditer(obj_pattern, text):
        try:
            item = json.loads(obj_match.group())
            news_item = _dict_to_news_item(item, category_key)
            if news_item:
                items.append(news_item)
        except json.JSONDecodeError:
            continue

    return items


def _try_parse_json_array(text: str, category_key: str) -> list[NewsItem]:
    """Try to parse a JSON array string into news items."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    items = []
    for item in data:
        news_item = _dict_to_news_item(item, category_key)
        if news_item:
            items.append(news_item)
    return items


def _dict_to_news_item(item: dict, category_key: str) -> NewsItem | None:
    """Convert a dict to a NewsItem, returning None if invalid."""
    if not isinstance(item, dict):
        return None
    try:
        news_item = NewsItem(
            id=str(item.get("id", "")).strip(),
            title=str(item.get("title", "")).strip(),
            source_url=str(item.get("source_url", "")).strip(),
            source_name=str(item.get("source_name", "")).strip(),
            published_date=str(item.get("published_date", "")).strip(),
            category=category_key,
            summary=str(item.get("summary", "")).strip(),
        )
        if news_item.id and news_item.title and news_item.source_url:
            return news_item
    except KeyError, TypeError, ValueError:
        pass
    return None


# ---------------------------------------------------------------------------
# Subprocess pipeline
# ---------------------------------------------------------------------------


def _search_category_subprocess(
    category_key: str,
    search_query: str,
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    recency: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[NewsItem]:
    """Search and summarize news items for a single category using subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"
    sources_list = "\n".join(f"- {s}" for s in PREFERRED_SOURCES)
    date_hint = _recency_hint(recency)

    prompt = _NEWS_PROMPT.format(
        category_key=category_key,
        search_query=search_query,
        existing_ids=existing_ids_str,
        sources_list=sources_list,
        date_hint=date_hint,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=10)

    if backend == AIBackend.CLAUDE:
        try:
            idx = cmd.index("--allowedTools")
            cmd[idx + 1] = "Read,Glob,Grep,Bash,Write,WebFetch,WebSearch"
        except ValueError:
            pass

    collected_text: list[str] = []
    raw_lines: list[str] = []

    cmd_display = " ".join(cmd[:8]) + " ..."
    _emit(on_progress, "status", f"  [CMD] {cmd_display}")
    _emit(on_progress, "status", f"  [CMD] prompt length: {len(prompt)} chars")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _emit(on_progress, "status", f"  [PID] subprocess started: pid={proc.pid}")

        import threading

        stderr_chunks: list[str] = []

        def _drain_stderr() -> None:
            for err_line in proc.stderr:
                stderr_chunks.append(err_line)

        stderr_thread = threading.Thread(target=_drain_stderr, daemon=True)
        stderr_thread.start()

        def collect_progress(p: GenerationProgress) -> None:
            if p.kind == "text":
                collected_text.append(p.content)
            if on_progress:
                on_progress(p)

        line_count = 0
        for line in proc.stdout:
            raw_lines.append(line)
            line_count += 1
            if line_count <= 3 or line_count % 50 == 0:
                _emit(
                    on_progress,
                    "status",
                    f"  [STDOUT line {line_count}] {line[:120].strip()}",
                )
            parse_stream_line(backend, line, collect_progress)

        proc.wait(timeout=600)
        stderr_thread.join(timeout=5)
        stderr_output = "".join(stderr_chunks)

        _emit(
            on_progress,
            "status",
            (
                f"  [DONE] exit={proc.returncode}, stdout_lines={line_count}, "
                f"collected_chunks={len(collected_text)}, "
                f"stderr_len={len(stderr_output)}"
            ),
        )

        if stderr_output:
            _emit(on_progress, "status", f"  [STDERR] {stderr_output[:300]}")

        if proc.returncode != 0:
            _emit(
                on_progress, "error", f"{info.name} exited with code {proc.returncode}"
            )
            if stderr_output:
                _emit(on_progress, "error", f"  stderr: {stderr_output[:500]}")
            return []

    except subprocess.TimeoutExpired:
        proc.kill()
        _emit(
            on_progress, "error", f"{info.name} timed out for category {category_key}"
        )
        return []
    except FileNotFoundError:
        _emit(on_progress, "error", f"{info.cli_command} CLI not found in PATH")
        return []
    except Exception as e:  # noqa: BLE001
        _emit(on_progress, "error", f"  [EXCEPTION] {type(e).__name__}: {e}")
        return []

    full_text = "".join(collected_text)
    _emit(
        on_progress,
        "status",
        f"  [PARSE] collected_text={len(full_text)} chars, raw_lines={len(raw_lines)}",
    )

    if not full_text.strip():
        _emit(
            on_progress,
            "status",
            "  [PARSE] No parsed text. Falling back to raw stdout...",
        )
        full_text = "".join(raw_lines)

    if full_text:
        sample = full_text[:300].replace("\n", "\\n")
        _emit(on_progress, "status", f"  [SAMPLE] {sample}")
    else:
        _emit(on_progress, "status", "  [SAMPLE] (empty — no output from AI)")

    items = _parse_news_json(full_text, category_key)
    if not items:
        _emit(
            on_progress,
            "status",
            (
                f"  [RESULT] No parseable news in {len(full_text)} chars "
                f"for {category_key}"
            ),
        )
        news_dir = _get_news_dir()
        debug_file = news_dir / f"_debug_{category_key}.txt"
        debug_content = (
            f"=== CMD ===\n{' '.join(cmd)}\n\n"
            f"=== COLLECTED TEXT ({len(collected_text)} chunks, "
            f"{len(full_text)} chars) ===\n"
            f"{''.join(collected_text)}\n\n"
            f"=== RAW LINES ({len(raw_lines)} lines) ===\n"
            f"{''.join(raw_lines)}\n\n"
            f"=== STDERR ===\n"
            f"{stderr_output if 'stderr_output' in dir() else '(not captured)'}\n"
        )
        debug_file.write_text(debug_content, encoding="utf-8")
        _emit(on_progress, "status", f"  [DEBUG] saved to {debug_file}")
    else:
        _emit(
            on_progress,
            "status",
            f"  [RESULT] Parsed {len(items)} news items for {category_key}",
        )
    return items


# ---------------------------------------------------------------------------
# Backfill / regenerate helpers
# ---------------------------------------------------------------------------


def regenerate_landing(news_dir: Path | None = None) -> tuple[int, Path | None]:
    """Regenerate the landing page from the existing index.

    Returns (md_files_created, index_path) — md_files_created counts any
    markdown files that were missing and got rewritten from the index.
    """
    if news_dir is None:
        news_dir = _get_news_dir()
    items = _load_index(news_dir)
    if not items:
        return 0, None

    items_dir = news_dir / "items"
    items_dir.mkdir(exist_ok=True)
    count = 0
    for item in items.values():
        cat_dir = items_dir / item.category
        md_path = cat_dir / f"{item.id}.md"
        if not md_path.exists():
            _write_news_md(item, items_dir)
            count += 1

    index_path = _generate_landing_html(items, news_dir)
    return count, index_path


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


async def search_news(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    categories: list[str] | None = None,
    recency: str = DEFAULT_RECENCY,
) -> NewsResult:
    """Search the web for fresh AI news in each selected category.

    Args:
        on_progress: Streaming progress callback (phases / status / errors).
        backend_override: Force a specific AI backend (else config default).
        model_override: Force a specific model (else config default).
        categories: Restrict to a subset of NEWS_CATEGORIES keys.
                     None = all five categories.
        recency: One of NEWS_RECENCY keys (24h / 48h / 7d).
                  Falls back to DEFAULT_RECENCY if unknown.
    """
    _emit(on_progress, "phase", "Initializing news pipeline...")

    if recency not in NEWS_RECENCY:
        _emit(
            on_progress,
            "status",
            f"Unknown recency {recency!r}; falling back to {DEFAULT_RECENCY}",
        )
        recency = DEFAULT_RECENCY

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    if not shutil.which(info.cli_command):
        return NewsResult(
            success=False,
            error=(
                f"{info.cli_command} CLI not found in PATH. "
                "Install it or switch AI tools."
            ),
        )

    news_dir = _get_news_dir()
    items_dir = news_dir / "items"
    items_dir.mkdir(exist_ok=True)

    existing = _load_index(news_dir)
    existing_ids = set(existing.keys())
    _emit(
        on_progress,
        "status",
        f"Loaded {len(existing)} existing news items for dedup",
    )

    cat_keys = list(NEWS_CATEGORIES.keys())
    if categories:
        cat_keys = [c for c in cat_keys if c in categories]

    if not cat_keys:
        return NewsResult(
            success=False,
            error="No valid categories selected.",
        )

    total_new = 0
    total_found = 0
    new_ids: set[str] = set()

    for i, category_key in enumerate(cat_keys):
        label = NEWS_CATEGORIES.get(category_key, category_key)
        _emit(
            on_progress,
            "phase",
            f"[{i + 1}/{len(cat_keys)}] News: {label} ({recency})",
        )

        search_query = NEWS_CATEGORY_QUERIES.get(category_key, label)

        loop = asyncio.get_event_loop()
        items = await loop.run_in_executor(
            None,
            _search_category_subprocess,
            category_key,
            search_query,
            existing_ids,
            backend,
            model,
            recency,
            on_progress,
        )

        for item in items:
            total_found += 1
            if item.id in existing_ids:
                _emit(on_progress, "status", f"  Skipped (duplicate): {item.id}")
                continue
            _write_news_md(item, items_dir)
            existing[item.id] = item
            existing_ids.add(item.id)
            new_ids.add(item.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {item.title}")

    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(news_dir, existing)
    index_path = _generate_landing_html(existing, news_dir, new_ids)

    _emit(on_progress, "phase", "News pipeline complete.")

    return NewsResult(
        success=True,
        items_found=total_found,
        items_new=total_new,
        items_skipped=total_found - total_new,
        index_path=index_path,
    )
