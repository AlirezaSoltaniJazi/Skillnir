"""AI events pipeline: search upcoming events per country, summarize, generate landing page."""

import asyncio
import html
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, field
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
from skillnir.researcher import TOPIC_LABELS

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """A single upcoming AI event or conference."""

    id: str
    title: str
    event_url: str
    registration_url: str
    organizer: str
    event_date: str  # YYYY-MM-DD
    end_date: str  # YYYY-MM-DD
    location: str
    country: str  # country code from EVENT_COUNTRIES
    topic: str  # key from TOPIC_LABELS
    is_free: bool
    description: str = ""
    key_highlights: list[str] = field(default_factory=list)


@dataclass
class EventsResult:
    """Result of an events search pipeline run."""

    success: bool
    events_found: int = 0
    events_new: int = 0
    events_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Countries
# ---------------------------------------------------------------------------

EVENT_COUNTRIES: dict[str, str] = {
    "uk": "United Kingdom",
    "us": "United States",
    "de": "Germany",
    "nl": "Netherlands",
    "pl": "Poland",
    "ir": "Iran",
    "ua": "Ukraine",
    "al": "Albania",
    "ca": "Canada",
    "au": "Australia",
    "at": "Austria",
    "ae": "UAE",
}

COUNTRY_COLORS: dict[str, str] = {
    "uk": "#3b82f6",
    "us": "#ef4444",
    "de": "#f59e0b",
    "nl": "#f97316",
    "pl": "#e11d48",
    "ir": "#10b981",
    "ua": "#06b6d4",
    "al": "#8b5cf6",
    "ca": "#ec4899",
    "au": "#14b8a6",
    "at": "#6366f1",
    "ae": "#a855f7",
}

_FLAGS_DIR = Path(__file__).parent / "assets" / "flags"

_flag_cache: dict[str, str] = {}


def _load_flag_img(country_code: str) -> str:
    """Load a country flag PNG and return inline HTML img tag (base64 data URI)."""
    import base64

    if country_code in _flag_cache:
        return _flag_cache[country_code]
    if country_code not in EVENT_COUNTRIES:
        _flag_cache[country_code] = ""
        return ""
    flag_path = _FLAGS_DIR / f"{country_code}.png"
    if not flag_path.exists():
        _flag_cache[country_code] = ""
        return ""
    png_data = flag_path.read_bytes()
    b64 = base64.b64encode(png_data).decode("ascii")
    img = (
        f'<img src="data:image/png;base64,{b64}" '
        f'alt="{EVENT_COUNTRIES.get(country_code, country_code)}" '
        f'style="width:22px;height:16px;vertical-align:middle;'
        f'border-radius:2px;margin-right:6px;object-fit:cover;">'
    )
    _flag_cache[country_code] = img
    return img


# ---------------------------------------------------------------------------
# Events prompt
# ---------------------------------------------------------------------------

_EVENTS_PROMPT = """\
You are an AI events research assistant. Your task is to search the internet for upcoming AI \
events, conferences, meetups, and workshops in a specific country, then extract structured \
information about each one.

## Instructions

Search for upcoming AI-related events in **{country_name}** (country code: {country_code}). \
Find 5-10 events that are scheduled in the near future (from today onwards). For EACH event:

1. **Search** for upcoming AI conferences, meetups, workshops, hackathons, and summits
2. **Deep-read** each event page to get accurate details
3. **Extract** key highlights and what attendees will learn
4. **Verify** dates, locations, and registration links are current and valid

## Output Format

Return EXACTLY this JSON array (no markdown, no explanation, ONLY the JSON):

```json
[
  {{{{
    "id": "eventname-YYYY-MM-DD",
    "title": "Event Title",
    "event_url": "https://...",
    "registration_url": "https://...",
    "organizer": "Organizer Name",
    "event_date": "YYYY-MM-DD",
    "end_date": "YYYY-MM-DD",
    "location": "City, Venue",
    "topic": "TOPIC_KEY",
    "is_free": false,
    "description": "2-3 paragraph description of the event...",
    "key_highlights": [
      "First highlight or key session",
      "Second highlight",
      "Third highlight"
    ]
  }}}}
]
```

## Rules
- `id` format: lowercase event name (no spaces, use hyphens) + start date, e.g., `ai-summit-london-2026-05-15`
- `event_date` and `end_date`: use YYYY-MM-DD format. For single-day events, both dates are the same
- `topic`: must be one of these keys: {topic_list}
- `is_free`: boolean — true if the event is free to attend, false if paid
- `key_highlights`: 3-5 bullets describing key sessions, speakers, or takeaways
- `description`: 2-3 paragraphs about the event, its focus, and why it matters
- Only include events with confirmed dates (no TBD)
- Skip events that have already passed (today is {today_date})

## Existing Event IDs (skip these — already in our knowledge base)

{existing_ids}
"""


# ---------------------------------------------------------------------------
# Index persistence
# ---------------------------------------------------------------------------


def _get_events_dir() -> Path:
    """Find skillnir's own .data/events/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / "events"
        if candidate.parent.is_dir():
            candidate.mkdir(parents=True, exist_ok=True)
            (candidate / "events").mkdir(exist_ok=True)
            return candidate
        current = current.parent
    fallback = Path.cwd() / ".data" / "events"
    fallback.mkdir(parents=True, exist_ok=True)
    (fallback / "events").mkdir(exist_ok=True)
    return fallback


def _load_index(events_dir: Path) -> dict[str, Event]:
    """Load existing events-index.json for dedup."""
    index_file = events_dir / "events-index.json"
    if not index_file.exists():
        return {}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        return {item["id"]: Event(**item) for item in data}
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(events_dir: Path, events: dict[str, Event]) -> None:
    """Persist events registry."""
    index_file = events_dir / "events-index.json"
    data = [asdict(e) for e in sorted(events.values(), key=lambda e: e.event_date)]
    index_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Migration: flat events → topic subdirectories
# ---------------------------------------------------------------------------


def _migrate_events_to_topic_dirs(events_dir: Path) -> int:
    """Move events from flat events/ into events/{topic}/ subdirectories.

    Handles both indexed events and orphan files (by reading frontmatter).
    Returns the number of files moved.
    """
    events_subdir = events_dir / "events"
    if not events_subdir.is_dir():
        return 0

    # Build id→topic map from index
    events = _load_index(events_dir)
    id_to_topic: dict[str, str] = {e.id: e.topic for e in events.values()}

    # Collect flat .md files to discover orphan topics via frontmatter
    valid_topics = set(TOPIC_LABELS.keys())
    for md_file in events_subdir.glob("*.md"):
        stem = md_file.stem
        if stem in id_to_topic:
            continue
        try:
            text = md_file.read_text(encoding="utf-8")[:500]
            match = re.search(r"^topic:\s*(.+)$", text, re.MULTILINE)
            if match:
                topic = match.group(1).strip()
                if topic in valid_topics:
                    id_to_topic[stem] = topic
        except OSError:
            continue

    moved = 0
    for event_id, topic in id_to_topic.items():
        topic_dir = events_subdir / topic
        for ext in (".md", ".html"):
            old_path = events_subdir / f"{event_id}{ext}"
            new_path = topic_dir / f"{event_id}{ext}"
            if old_path.exists() and not new_path.exists():
                topic_dir.mkdir(exist_ok=True)
                old_path.rename(new_path)
                moved += 1
    return moved


# ---------------------------------------------------------------------------
# Event MD writer
# ---------------------------------------------------------------------------


def _write_event_md(event: Event, events_subdir: Path) -> Path:
    """Write individual event summary as markdown."""
    topic_dir = events_subdir / event.topic
    topic_dir.mkdir(exist_ok=True)
    md_path = topic_dir / f"{event.id}.md"
    highlights = "\n".join(f"{i + 1}. {h}" for i, h in enumerate(event.key_highlights))
    free_label = "Free" if event.is_free else "Paid"

    content = f"""\
---
id: {event.id}
title: "{event.title}"
event_url: {event.event_url}
registration_url: {event.registration_url}
organizer: {event.organizer}
event_date: {event.event_date}
end_date: {event.end_date}
location: {event.location}
country: {event.country}
topic: {event.topic}
is_free: {str(event.is_free).lower()}
---

# {event.title}

**Organizer**: {event.organizer} | **Date**: {event.event_date} — {event.end_date} | **Location**: {event.location} | **Country**: {EVENT_COUNTRIES.get(event.country, event.country)} | **Topic**: {TOPIC_LABELS.get(event.topic, event.topic)} | **Price**: {free_label}

**Event Page**: [{event.title}]({event.event_url}) | **Register**: [Registration]({event.registration_url})

## Key Highlights

{highlights}

## Description

{event.description}
"""
    md_path.write_text(content, encoding="utf-8")
    _write_event_html(event, events_subdir)
    return md_path


# ---------------------------------------------------------------------------
# Event HTML page generator
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load an HTML template from the resources directory."""
    template_path = Path(__file__).parent / "resources" / name
    return template_path.read_text(encoding="utf-8")


def _generate_event_html(event: Event) -> str:
    """Generate a self-contained styled HTML page for a single event."""
    title = html.escape(event.title)
    event_url = html.escape(event.event_url, quote=True)
    registration_url = html.escape(event.registration_url, quote=True)
    organizer = html.escape(event.organizer)
    event_date = event.event_date
    if event.end_date and event.end_date != event.event_date:
        event_date = f"{event.event_date} — {event.end_date}"
    location = html.escape(event.location)
    country = html.escape(EVENT_COUNTRIES.get(event.country, event.country))
    topic_label = html.escape(TOPIC_LABELS.get(event.topic, event.topic))
    free_badge = "free" if event.is_free else "paid"

    highlights_html = "\n".join(
        f"        <li>{html.escape(h)}</li>" for h in event.key_highlights
    )

    description_html = "\n".join(
        f"      <p>{html.escape(p.strip())}</p>"
        for p in event.description.split("\n\n")
        if p.strip()
    )

    template = _load_template("event.html")
    return (
        template.replace("<!-- TITLE -->", title)
        .replace("<!-- EVENT_URL -->", event_url)
        .replace("<!-- REGISTRATION_URL -->", registration_url)
        .replace("<!-- ORGANIZER -->", organizer)
        .replace("<!-- EVENT_DATE -->", event_date)
        .replace("<!-- LOCATION -->", location)
        .replace("<!-- COUNTRY_FLAG -->", _load_flag_img(event.country))
        .replace("<!-- COUNTRY -->", country)
        .replace("<!-- TOPIC_LABEL -->", topic_label)
        .replace("<!-- FREE_BADGE -->", free_badge)
        .replace("<!-- HIGHLIGHTS_HTML -->", highlights_html)
        .replace("<!-- DESCRIPTION_HTML -->", description_html)
    )


def _write_event_html(event: Event, events_subdir: Path) -> Path:
    """Write individual event as styled HTML page."""
    topic_dir = events_subdir / event.topic
    topic_dir.mkdir(exist_ok=True)
    html_path = topic_dir / f"{event.id}.html"
    html_path.write_text(_generate_event_html(event), encoding="utf-8")
    return html_path


# ---------------------------------------------------------------------------
# Landing page HTML generator
# ---------------------------------------------------------------------------


def _generate_landing_html(
    events: dict[str, Event], events_dir: Path, new_ids: set[str] | None = None
) -> Path:
    """Generate index.html landing page sorted by event_date ascending."""
    sorted_events = sorted(events.values(), key=lambda e: e.event_date)
    new_ids = new_ids or set()

    topic_colors = {
        "prompt-engineering": "#3b82f6",
        "ai-skills": "#8b5cf6",
        "mcp": "#06b6d4",
        "rag-context": "#10b981",
        "ai-rules": "#f59e0b",
        "multi-agent": "#ef4444",
        "context-engineering": "#ec4899",
        "ai-productivity": "#6366f1",
        "ai-memory": "#14b8a6",
        "ai-security": "#f97316",
    }

    from datetime import date as date_cls

    today = date_cls.today()

    rows = []
    for e in sorted_events:
        color = topic_colors.get(e.topic, "#6b7280")
        country_color = COUNTRY_COLORS.get(e.country, "#6b7280")
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;border-radius:4px;'
            'font-size:11px;margin-left:8px;">NEW</span>'
            if e.id in new_ids
            else ""
        )
        title_escaped = html.escape(e.title)
        country_name = html.escape(EVENT_COUNTRIES.get(e.country, e.country))
        location_escaped = html.escape(e.location)
        free_label = "Free" if e.is_free else "Paid"
        free_color = "#22c55e" if e.is_free else "#ef4444"
        free_val = "free" if e.is_free else "paid"

        # Date color-coding and remaining time
        try:
            evt_date = date_cls.fromisoformat(e.event_date)
            days_remaining = (evt_date - today).days
        except ValueError:
            evt_date = None
            days_remaining = None

        if days_remaining is not None and days_remaining < 0:
            date_color = "#ef4444"
            remaining_label = "Passed"
            remaining_color = "#ef4444"
        elif days_remaining == 0:
            date_color = "#f59e0b"
            remaining_label = "Today"
            remaining_color = "#f59e0b"
        elif days_remaining == 1:
            date_color = "#94a3b8"
            remaining_label = "Tomorrow"
            remaining_color = "#94a3b8"
        elif days_remaining is not None:
            date_color = "#94a3b8"
            remaining_label = f"{days_remaining} days"
            remaining_color = "#94a3b8"
        else:
            date_color = "#94a3b8"
            remaining_label = "—"
            remaining_color = "#94a3b8"

        rows.append(f"""\
        <tr onclick="window.open('events/{e.topic}/{e.id}.html','_blank')" style="cursor:pointer;" class="row" data-topic="{e.topic}" data-country="{e.country}" data-free="{free_val}" data-date="{e.event_date}">
          <td style="padding:12px 16px;">
            <div style="font-weight:600;color:#e2e8f0;">{title_escaped}{badge}</div>
            <div style="font-size:13px;color:#94a3b8;margin-top:4px;">{html.escape(e.organizer)}</div>
          </td>
          <td style="padding:12px 16px;color:{date_color};font-family:monospace;font-size:13px;white-space:nowrap;">{e.event_date}</td>
          <td style="padding:12px 16px;color:{remaining_color};font-size:13px;white-space:nowrap;font-weight:600;">{remaining_label}</td>
          <td style="padding:12px 16px;color:#94a3b8;">{location_escaped}</td>
          <td style="padding:12px 16px;white-space:nowrap;">
            <span style="background:{country_color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;display:inline-flex;align-items:center;">{_load_flag_img(e.country)}{country_name}</span>
          </td>
          <td style="padding:12px 16px;white-space:nowrap;">
            <span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{TOPIC_LABELS.get(e.topic, e.topic)}</span>
          </td>
          <td style="padding:12px 16px;white-space:nowrap;">
            <span style="background:{free_color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{free_label}</span>
          </td>
        </tr>""")

    rows_html = "\n".join(rows)
    topic_counts: dict[str, int] = {}
    country_counts: dict[str, int] = {}
    free_counts: dict[str, int] = {"free": 0, "paid": 0}
    for e in sorted_events:
        topic_counts[e.topic] = topic_counts.get(e.topic, 0) + 1
        country_counts[e.country] = country_counts.get(e.country, 0) + 1
        if e.is_free:
            free_counts["free"] += 1
        else:
            free_counts["paid"] += 1

    # Topic chips
    all_topic_chip = (
        f'<span class="chip topic-chip active" data-filter="all" '
        f'onclick="toggleTopic(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All Topics: {len(sorted_events)}</span>'
    )
    topic_chips = " ".join(
        f'<span class="chip topic-chip" data-filter="{t}" '
        f'onclick="toggleTopic(\'{t}\')" style="background:{topic_colors.get(t, "#6b7280")};'
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;">{TOPIC_LABELS.get(t, t)}: {c}</span>'
        for t, c in sorted(topic_counts.items(), key=lambda x: -x[1])
    )
    stats_chips = all_topic_chip + " " + topic_chips

    # Country chips
    all_country_chip = (
        f'<span class="chip country-chip active" data-filter="all" '
        f'onclick="toggleCountry(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All Countries: {len(sorted_events)}</span>'
    )
    country_chips = " ".join(
        f'<span class="chip country-chip" data-filter="{cc}" '
        f"onclick=\"toggleCountry('{cc}')\" style=\"background:{COUNTRY_COLORS.get(cc, '#6b7280')};"
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;display:inline-flex;align-items:center;">'
        f'{_load_flag_img(cc)}{EVENT_COUNTRIES.get(cc, cc)}: {c}</span>'
        for cc, c in sorted(country_counts.items(), key=lambda x: -x[1])
    )
    country_chips_html = all_country_chip + " " + country_chips

    # Free/paid chips
    all_free_chip = (
        f'<span class="chip free-chip active" data-filter="all" '
        f'onclick="toggleFree(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All: {len(sorted_events)}</span>'
    )
    free_chip = (
        f'<span class="chip free-chip" data-filter="free" '
        f'onclick="toggleFree(\'free\')" style="background:#22c55e;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;">Free: {free_counts["free"]}</span>'
    )
    paid_chip = (
        f'<span class="chip free-chip" data-filter="paid" '
        f'onclick="toggleFree(\'paid\')" style="background:#ef4444;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;">Paid: {free_counts["paid"]}</span>'
    )
    free_chips_html = all_free_chip + " " + free_chip + " " + paid_chip

    from datetime import datetime

    total = len(sorted_events)
    today_iso = today.isoformat()
    upcoming = [e for e in sorted_events if e.event_date >= today_iso]
    next_event = upcoming[0].event_date if upcoming else "N/A"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = (
        f"{total} events | Next event: {next_event}" f" | Generated: {generated_at}"
    )

    template = _load_template("events-landing.html")
    page_html = (
        template.replace("<!-- SUBTITLE -->", subtitle)
        .replace("<!-- TOPIC_CHIPS -->", stats_chips)
        .replace("<!-- COUNTRY_CHIPS -->", country_chips_html)
        .replace("<!-- FREE_CHIPS -->", free_chips_html)
        .replace("<!-- TABLE_ROWS -->", rows_html)
        .replace("<!-- TOTAL_EVENTS -->", str(total))
    )

    index_path = events_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


# ---------------------------------------------------------------------------
# AI response parser
# ---------------------------------------------------------------------------


def _parse_events_json(text: str, country_code: str) -> list[Event]:
    """Parse JSON array of events from AI response text."""
    events: list[Event] = []

    # Strategy 1: Find JSON inside ```json ... ``` code blocks
    code_blocks = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    for block in code_blocks:
        events.extend(_try_parse_json_array(block, country_code))
        if events:
            return events

    # Strategy 2: Find standalone JSON arrays (greedy last match — the final output)
    all_arrays = re.findall(
        r"\[\s*\{[^[\]]*\"id\"[^[\]]*\"title\"[\s\S]*?\}\s*\]", text
    )
    for arr in reversed(
        all_arrays
    ):  # Try last match first (most likely the final output)
        events.extend(_try_parse_json_array(arr, country_code))
        if events:
            return events

    # Strategy 3: Find individual JSON objects with event fields
    obj_pattern = r'\{\s*"id"\s*:\s*"[^"]+"\s*,\s*"title"\s*:\s*"[^"]+"[\s\S]*?\}'
    for obj_match in re.finditer(obj_pattern, text):
        try:
            item = json.loads(obj_match.group())
            event = _dict_to_event(item, country_code)
            if event:
                events.append(event)
        except json.JSONDecodeError:
            continue

    return events


def _try_parse_json_array(text: str, country_code: str) -> list[Event]:
    """Try to parse a JSON array string into events."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    events = []
    for item in data:
        event = _dict_to_event(item, country_code)
        if event:
            events.append(event)
    return events


def _dict_to_event(item: dict, country_code: str) -> Event | None:
    """Convert a dict to an Event, returning None if invalid."""
    if not isinstance(item, dict):
        return None
    try:
        # Handle is_free as str or bool
        is_free_raw = item.get("is_free", False)
        if isinstance(is_free_raw, str):
            is_free = is_free_raw.lower() in ("true", "yes", "1")
        else:
            is_free = bool(is_free_raw)

        # Validate topic — must be in TOPIC_LABELS, fallback to ai-productivity
        topic = str(item.get("topic", "ai-productivity")).strip()
        if topic not in TOPIC_LABELS:
            topic = "ai-productivity"

        event = Event(
            id=str(item.get("id", "")).strip(),
            title=str(item.get("title", "")).strip(),
            event_url=str(item.get("event_url", "")).strip(),
            registration_url=str(item.get("registration_url", "")).strip(),
            organizer=str(item.get("organizer", "")).strip(),
            event_date=str(item.get("event_date", "")).strip(),
            end_date=str(item.get("end_date", "")).strip(),
            location=str(item.get("location", "")).strip(),
            country=country_code,
            topic=topic,
            is_free=is_free,
            description=str(item.get("description", "")).strip(),
            key_highlights=[str(h) for h in item.get("key_highlights", [])],
        )
        if event.id and event.title and event.event_url:
            return event
    except json.JSONDecodeError, KeyError, TypeError:
        pass
    return None


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def _search_events_subprocess(
    country_code: str,
    country_name: str,
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[Event]:
    """Search upcoming events for a single country using subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"
    topic_list = ", ".join(TOPIC_LABELS.keys())

    from datetime import date

    today_date = date.today().isoformat()

    prompt = _EVENTS_PROMPT.format(
        country_name=country_name,
        country_code=country_code,
        topic_list=topic_list,
        existing_ids=existing_ids_str,
        today_date=today_date,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=10)

    # Override allowed tools to include WebFetch and WebSearch for research
    if backend == AIBackend.CLAUDE:
        try:
            idx = cmd.index("--allowedTools")
            cmd[idx + 1] = "Read,Glob,Grep,Bash,Write,WebFetch,WebSearch"
        except ValueError:
            pass

    collected_text: list[str] = []
    raw_lines: list[str] = []

    # Log the full command for debugging
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
            f"  [DONE] exit={proc.returncode}, stdout_lines={line_count}, "
            f"collected_chunks={len(collected_text)}, stderr_len={len(stderr_output)}",
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
        _emit(on_progress, "error", f"{info.name} timed out for country {country_code}")
        return []
    except FileNotFoundError:
        _emit(on_progress, "error", f"{info.cli_command} CLI not found in PATH")
        return []
    except Exception as e:
        _emit(on_progress, "error", f"  [EXCEPTION] {type(e).__name__}: {e}")
        return []

    full_text = "".join(collected_text)
    _emit(
        on_progress,
        "status",
        f"  [PARSE] collected_text={len(full_text)} chars, raw_lines={len(raw_lines)}",
    )

    # If no text was collected from parsed events, try raw stdout
    if not full_text.strip():
        _emit(
            on_progress,
            "status",
            f"  [PARSE] No parsed text. Falling back to raw stdout...",
        )
        full_text = "".join(raw_lines)

    # Log a sample of the text for debugging
    if full_text:
        sample = full_text[:300].replace("\n", "\\n")
        _emit(on_progress, "status", f"  [SAMPLE] {sample}")
    else:
        _emit(on_progress, "status", "  [SAMPLE] (empty — no output from AI)")

    events = _parse_events_json(full_text, country_code)
    if not events:
        _emit(
            on_progress,
            "status",
            f"  [RESULT] No parseable events in {len(full_text)} chars for {country_code}",
        )
        # Save raw output for debugging
        ev_dir = _get_events_dir()
        debug_file = ev_dir / f"_debug_{country_code}.txt"
        debug_content = (
            f"=== CMD ===\n{' '.join(cmd)}\n\n"
            f"=== COLLECTED TEXT ({len(collected_text)} chunks, {len(full_text)} chars) ===\n"
            f"{''.join(collected_text)}\n\n"
            f"=== RAW LINES ({len(raw_lines)} lines) ===\n"
            f"{''.join(raw_lines)}\n\n"
            f"=== STDERR ===\n{stderr_output if 'stderr_output' in dir() else '(not captured)'}\n"
        )
        debug_file.write_text(debug_content, encoding="utf-8")
        _emit(on_progress, "status", f"  [DEBUG] saved to {debug_file}")
    else:
        _emit(
            on_progress,
            "status",
            f"  [RESULT] Parsed {len(events)} events for {country_code}",
        )
    return events


def backfill_event_html(events_dir: Path | None = None) -> int:
    """Generate HTML pages for events that only have .md files.

    Returns the number of HTML files created.
    """
    if events_dir is None:
        events_dir = _get_events_dir()
    events = _load_index(events_dir)
    events_subdir = events_dir / "events"
    count = 0
    for event in events.values():
        topic_dir = events_subdir / event.topic
        html_path = topic_dir / f"{event.id}.html"
        md_path = topic_dir / f"{event.id}.md"
        if md_path.exists() and not html_path.exists():
            _write_event_html(event, events_subdir)
            count += 1
    return count


def regenerate_landing(events_dir: Path | None = None) -> tuple[int, Path | None]:
    """Backfill HTML event pages and regenerate the landing page.

    Returns (html_files_created, index_path).
    """
    if events_dir is None:
        events_dir = _get_events_dir()
    _migrate_events_to_topic_dirs(events_dir)
    events = _load_index(events_dir)
    if not events:
        return 0, None
    count = backfill_event_html(events_dir)
    index_path = _generate_landing_html(events, events_dir)
    return count, index_path


async def search_events(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    countries: list[str] | None = None,
) -> EventsResult:
    """Main entry: search events for each country, summarize with AI, generate landing page."""
    _emit(on_progress, "phase", "Initializing events search pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    # Check CLI availability
    if not shutil.which(info.cli_command):
        return EventsResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH. Install it or switch AI tools.",
        )

    events_dir = _get_events_dir()
    events_subdir = events_dir / "events"
    events_subdir.mkdir(exist_ok=True)

    # Migrate flat events into topic subdirectories
    _migrate_events_to_topic_dirs(events_dir)

    # Load existing index for dedup
    existing = _load_index(events_dir)
    existing_ids = set(existing.keys())
    _emit(on_progress, "status", f"Loaded {len(existing)} existing events for dedup")

    # Determine which countries to search
    country_codes = list(EVENT_COUNTRIES.keys())

    if countries:
        country_codes = [cc for cc in country_codes if cc in countries]

    total_new = 0
    total_found = 0
    new_ids: set[str] = set()

    for i, country_code in enumerate(country_codes):
        country_name = EVENT_COUNTRIES[country_code]
        _emit(
            on_progress,
            "phase",
            f"[{i + 1}/{len(country_codes)}] Searching events: {country_name}",
        )

        loop = asyncio.get_event_loop()
        found_events = await loop.run_in_executor(
            None,
            _search_events_subprocess,
            country_code,
            country_name,
            existing_ids,
            backend,
            model,
            on_progress,
        )

        for event in found_events:
            total_found += 1
            if event.id in existing_ids:
                _emit(on_progress, "status", f"  Skipped (duplicate): {event.id}")
                continue

            # Write MD file
            _write_event_md(event, events_subdir)
            existing[event.id] = event
            existing_ids.add(event.id)
            new_ids.add(event.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {event.title}")

    # Save updated index
    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(events_dir, existing)

    # Backfill HTML pages for any events that only have .md
    backfill_event_html(events_dir)

    # Generate landing page
    index_path = _generate_landing_html(existing, events_dir, new_ids)

    _emit(on_progress, "phase", "Events search complete.")

    return EventsResult(
        success=True,
        events_found=total_found,
        events_new=total_new,
        events_skipped=total_found - total_new,
        index_path=index_path,
    )
