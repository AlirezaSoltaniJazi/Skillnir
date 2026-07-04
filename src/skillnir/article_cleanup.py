"""AI-driven cleanup of research article stores — conservative, never deletes.

Classifies articles from index metadata alone (no file reads, batched AI
calls), and in apply mode soft-deletes the invalidated ones: their .md/.html
pair moves to ``articles/<topic>/outdated/``, their index entry stays (with
``status="outdated"``) so fetch dedup keeps skipping them, and the landing
page regenerates with an "Outdated" section.

Two modes, mirroring ``docs_optimizer``:

- **report** — classify and write ``cleanup-report.md``/``.json`` only.
- **apply**  — classify, move files, update the index, regenerate landing.
"""

import asyncio
import json
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

from skillnir.article_status import STATUS_OUTDATED, article_dir
from skillnir.backends import (
    BACKENDS,
    AIBackend,
    build_subprocess_command,
    load_config,
    run_streaming_command,
)
from skillnir.generator import GenerationProgress, _emit
from skillnir.researcher import (
    TOPIC_LABELS as RESEARCH_TOPIC_LABELS,
    _get_research_dir,
    _load_index as research_load_index,
    _migrate_articles_to_topic_dirs,
    _save_index as research_save_index,
    regenerate_landing as research_regenerate_landing,
)
from skillnir.software_researcher import (
    TOPIC_LABELS as SOFTWARE_TOPIC_LABELS,
    _get_software_research_dir,
    _load_index as software_load_index,
    _save_index as software_save_index,
    regenerate_landing as software_regenerate_landing,
)
from skillnir.testing_researcher import (
    TOPIC_LABELS as TESTING_TOPIC_LABELS,
    _get_testing_research_dir,
    _load_index as testing_load_index,
    _save_index as testing_save_index,
    regenerate_landing as testing_regenerate_landing,
)

CLEANUP_BATCH_SIZE = 25
CONFIDENCE_THRESHOLD = 0.8
DEFAULT_MAX_ARTICLES = 100
SUMMARY_EXCERPT_CHARS = 500
REPORT_MD = "cleanup-report.md"
REPORT_JSON = "cleanup-report.json"


# ---------------------------------------------------------------------------
# Store registry
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class StoreSpec:
    """Everything the cleanup needs to operate on one research store."""

    key: str
    label: str
    get_dir: Callable[[], Path]
    index_filename: str
    topic_labels: dict[str, str]
    load_index: Callable[[Path], dict]
    save_index: Callable[[Path, dict], None]
    regenerate_landing: Callable[..., tuple[int, Path | None]]
    migrate: Callable[[Path], int] | None = None


STORE_SPECS: dict[str, StoreSpec] = {
    "research": StoreSpec(
        key="research",
        label="AI Engineering Research",
        get_dir=_get_research_dir,
        index_filename="research-index.json",
        topic_labels=RESEARCH_TOPIC_LABELS,
        load_index=research_load_index,
        save_index=research_save_index,
        regenerate_landing=research_regenerate_landing,
        migrate=_migrate_articles_to_topic_dirs,
    ),
    "software-research": StoreSpec(
        key="software-research",
        label="Software Engineering Research",
        get_dir=_get_software_research_dir,
        index_filename="software-research-index.json",
        topic_labels=SOFTWARE_TOPIC_LABELS,
        load_index=software_load_index,
        save_index=software_save_index,
        regenerate_landing=software_regenerate_landing,
    ),
    "testing-research": StoreSpec(
        key="testing-research",
        label="Testing & QA Research",
        get_dir=_get_testing_research_dir,
        index_filename="testing-research-index.json",
        topic_labels=TESTING_TOPIC_LABELS,
        load_index=testing_load_index,
        save_index=testing_save_index,
        regenerate_landing=testing_regenerate_landing,
    ),
}


# ---------------------------------------------------------------------------
# Result models
# ---------------------------------------------------------------------------


@dataclass
class CleanupCandidate:
    """One article the AI judged outdated."""

    id: str
    topic: str
    title: str
    published_date: str
    verdict: str  # "outdated" | "valid"
    reason: str
    confidence: float


@dataclass
class CleanupResult:
    """Aggregate result of a cleanup run."""

    success: bool
    store: str = ""
    mode: str = "report"
    scanned: int = 0
    batches: int = 0
    candidates: list[CleanupCandidate] = field(default_factory=list)
    low_confidence: list[CleanupCandidate] = field(default_factory=list)
    moved: int = 0
    report_md_path: Path | None = None
    report_json_path: Path | None = None
    landing_path: Path | None = None
    error: str | None = None
    backend_used: AIBackend | None = None


# ---------------------------------------------------------------------------
# Selection
# ---------------------------------------------------------------------------


def select_articles(
    articles: dict,
    topics: list[str] | None = None,
    older_than: str | None = None,
    max_articles: int = DEFAULT_MAX_ARTICLES,
) -> list:
    """Pick active articles to classify: filtered, oldest first, capped."""
    selected = [
        a
        for a in articles.values()
        if getattr(a, "status", "active") != STATUS_OUTDATED
        and (not topics or a.topic in topics)
        and (older_than is None or a.published_date < older_than)
    ]
    selected.sort(key=lambda a: a.published_date)
    return selected[:max_articles]


# ---------------------------------------------------------------------------
# AI classification
# ---------------------------------------------------------------------------

_CLEANUP_PROMPT = """\
You are a conservative research librarian curating the "{store_label}" \
article archive. Today's date: {today}.

Judge each article below using ONLY the metadata given. An article is \
"outdated" ONLY when its content is clearly invalidated today:
- the spec/version/API it describes has been superseded in a way that makes \
its guidance actively wrong, or
- the product/tool/model it covers is discontinued or replaced, or
- its central claims are now demonstrably false.

Age alone is NEVER a reason. Foundational concepts, empirical studies, and \
still-accurate guidance stay "valid" regardless of date. When in doubt, \
answer "valid".

Do not use any tools. Respond with ONLY a JSON array — no markdown fences, \
no commentary:
[{{"id": "...", "verdict": "outdated" | "valid", "reason": "one concrete \
sentence naming WHAT invalidated it", "confidence": 0.0-1.0}}]
Include every input id exactly once. "confidence" is your certainty that \
the content is invalidated (use it only for "outdated" verdicts).

## Articles

{articles_json}
"""


def _build_batch_payload(batch: list) -> str:
    """JSON payload for one classification batch — index metadata only."""
    items = [
        {
            "id": a.id,
            "title": a.title,
            "published_date": a.published_date,
            "topic": a.topic,
            "key_insights": a.key_insights,
            "summary": a.summary[:SUMMARY_EXCERPT_CHARS],
        }
        for a in batch
    ]
    return json.dumps(items, ensure_ascii=False, indent=1)


def _parse_verdicts(text: str) -> list[dict]:
    """Extract the verdict JSON array from AI response text.

    The stream can repeat the payload (assistant text + final result event),
    so the bare-array fallback uses ``raw_decode`` from the first ``[`` —
    it parses one complete array and ignores any duplicate that follows.
    """
    candidates_text: list[str] = []
    fenced = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    candidates_text.extend(reversed(fenced))
    start = text.find("[")
    if start != -1:
        candidates_text.append(text[start:])

    decoder = json.JSONDecoder()
    for blob in candidates_text:
        try:
            data, _ = decoder.raw_decode(blob)
        except json.JSONDecodeError:
            continue
        if isinstance(data, list):
            return [item for item in data if isinstance(item, dict)]
    return []


def _clamp_confidence(value) -> float:
    try:
        return min(1.0, max(0.0, float(value)))
    except TypeError, ValueError:
        return 0.0


def _to_candidates(items: list[dict], by_id: dict) -> list[CleanupCandidate]:
    """Convert raw verdict dicts to candidates; unknown ids dropped."""
    seen: dict[str, CleanupCandidate] = {}
    for item in items:
        article = by_id.get(str(item.get("id", "")))
        if article is None:
            continue
        verdict = str(item.get("verdict", "")).strip().lower()
        seen[article.id] = CleanupCandidate(
            id=article.id,
            topic=article.topic,
            title=article.title,
            published_date=article.published_date,
            verdict="outdated" if verdict == "outdated" else "valid",
            reason=str(item.get("reason", "")).strip(),
            confidence=_clamp_confidence(item.get("confidence")),
        )
    return list(seen.values())


def _classify_batch_subprocess(
    payload_json: str,
    store_label: str,
    today: str,
    backend: AIBackend,
    model: str,
    cwd: Path,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> tuple[list[dict], str | None]:
    """Run one classification batch via the backend CLI. Returns (verdicts, error)."""
    prompt = _CLEANUP_PROMPT.format(
        store_label=store_label, today=today, articles_json=payload_json
    )
    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=4)
    if backend == AIBackend.CLAUDE:
        # Pure classification — no tools needed or wanted.
        try:
            idx = cmd.index("--allowedTools")
            cmd[idx + 1] = ""
        except ValueError:
            pass

    # "result_text" is the backend's authoritative final message; streamed
    # "text" chunks repeat the same content, so collect them separately and
    # prefer the result to avoid a duplicated (unparseable) payload.
    text_chunks: list[str] = []
    result_chunks: list[str] = []

    def _collector(p: GenerationProgress) -> None:
        if p.kind == "text":
            text_chunks.append(p.content)
        elif p.kind == "result_text":
            result_chunks.append(p.content)
        if on_progress:
            on_progress(p)

    try:
        run = run_streaming_command(cmd, backend, cwd, _collector, timeout=300)
    except FileNotFoundError:
        return [], f"{BACKENDS[backend].cli_command} CLI not found in PATH."

    if run.timed_out:
        return [], "Classification batch timed out after 5 minutes."
    if run.returncode != 0:
        return [], f"Backend exited with code {run.returncode}: {run.stderr}"

    final_text = "".join(result_chunks) or "".join(text_chunks)
    verdicts = _parse_verdicts(final_text)
    if not verdicts:
        return [], "No verdict JSON found in AI response."
    return verdicts, None


# ---------------------------------------------------------------------------
# Mover
# ---------------------------------------------------------------------------


def move_article_to_outdated(
    article_id: str, topic: str, articles_dir: Path
) -> tuple[int, str | None]:
    """Move an article's .md/.html pair into articles/<topic>/outdated/.

    Idempotent and non-destructive: existing destinations are never
    overwritten, missing sources are tolerated (a later backfill can
    regenerate the .html). Returns (files_moved, error).
    """
    src_dir = articles_dir / topic
    dst_dir = article_dir(articles_dir, topic, STATUS_OUTDATED)
    moved = 0
    for ext in (".md", ".html"):
        src = src_dir / f"{article_id}{ext}"
        dst = dst_dir / f"{article_id}{ext}"
        if dst.exists() or not src.exists():
            continue
        try:
            dst_dir.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
            moved += 1
        except OSError as exc:
            return moved, str(exc)
    return moved, None


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_cleanup_report(
    store_dir: Path, spec: StoreSpec, result: CleanupResult
) -> tuple[Path, Path]:
    """Write cleanup-report.md + .json into the store directory."""
    generated_at = date.today().isoformat()

    json_payload = {
        "store": result.store,
        "mode": result.mode,
        "generated_at": generated_at,
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "scanned": result.scanned,
        "batches": result.batches,
        "moved": result.moved,
        "candidates": [asdict(c) for c in result.candidates],
        "low_confidence": [asdict(c) for c in result.low_confidence],
    }
    json_path = store_dir / REPORT_JSON
    json_path.write_text(
        json.dumps(json_payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    def _table(rows: list[CleanupCandidate]) -> str:
        if not rows:
            return "- (none)\n"
        lines = [
            "| Article | Topic | Published | Confidence | Reason |",
            "| --- | --- | --- | --- | --- |",
        ]
        for c in rows:
            title = c.title.replace("|", "\\|")
            reason = c.reason.replace("|", "\\|")
            lines.append(
                f"| {title} (`{c.id}`) | {c.topic} | {c.published_date} "
                f"| {c.confidence:.2f} | {reason} |"
            )
        return "\n".join(lines) + "\n"

    md_path = store_dir / REPORT_MD
    md_path.write_text(
        f"""\
# Article Cleanup Report — {spec.label}

Generated: {generated_at}
Mode: {result.mode}
Scanned: {result.scanned} articles in {result.batches} batches
Confidence threshold: {CONFIDENCE_THRESHOLD}
Moved to outdated/: {result.moved} files

## Outdated (confidence >= {CONFIDENCE_THRESHOLD})

{_table(result.candidates)}
## Low confidence (flagged but NOT moved — review manually)

{_table(result.low_confidence)}
""",
        encoding="utf-8",
    )
    return md_path, json_path


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def cleanup_articles(
    store: str,
    mode: str = "report",
    topics: list[str] | None = None,
    older_than: str | None = None,
    max_articles: int = DEFAULT_MAX_ARTICLES,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
) -> CleanupResult:
    """Main entry point. ``mode`` is ``"report"`` (default) or ``"apply"``."""
    spec = STORE_SPECS.get(store)
    if spec is None:
        return CleanupResult(
            success=False,
            store=store,
            mode=mode,
            error=f"Unknown store: {store!r}. One of: {sorted(STORE_SPECS)}",
        )
    if mode not in ("report", "apply"):
        return CleanupResult(
            success=False, store=store, mode=mode, error=f"Unknown mode: {mode!r}"
        )

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]
    if not shutil.which(info.cli_command):
        return CleanupResult(
            success=False,
            store=store,
            mode=mode,
            error=f"{info.name} CLI ({info.cli_command}) not found in PATH.",
            backend_used=backend,
        )

    result = CleanupResult(success=True, store=store, mode=mode, backend_used=backend)

    _emit(on_progress, "phase", f"Loading {spec.label} index...")
    store_dir = spec.get_dir()
    if spec.migrate is not None:
        spec.migrate(store_dir)
    articles = spec.load_index(store_dir)

    selected = select_articles(articles, topics, older_than, max_articles)
    result.scanned = len(selected)
    if not selected:
        _emit(on_progress, "status", "No active articles match the filters.")
        result.report_md_path, result.report_json_path = write_cleanup_report(
            store_dir, spec, result
        )
        return result

    today = date.today().isoformat()
    batches = [
        selected[i : i + CLEANUP_BATCH_SIZE]
        for i in range(0, len(selected), CLEANUP_BATCH_SIZE)
    ]
    result.batches = len(batches)

    loop = asyncio.get_event_loop()
    all_candidates: list[CleanupCandidate] = []
    failed_batches = 0
    for i, batch in enumerate(batches):
        _emit(
            on_progress,
            "phase",
            f"Classifying batch {i + 1}/{len(batches)} ({len(batch)} articles)...",
        )
        by_id = {a.id: a for a in batch}
        verdicts, err = await loop.run_in_executor(
            None,
            _classify_batch_subprocess,
            _build_batch_payload(batch),
            spec.label,
            today,
            backend,
            model,
            store_dir,
            on_progress,
        )
        if err:
            failed_batches += 1
            _emit(on_progress, "error", f"Batch {i + 1} failed: {err}")
            continue
        all_candidates.extend(_to_candidates(verdicts, by_id))

    if failed_batches == len(batches):
        result.success = False
        result.error = "All classification batches failed."
        return result

    outdated_verdicts = [c for c in all_candidates if c.verdict == "outdated"]
    result.candidates = [
        c for c in outdated_verdicts if c.confidence >= CONFIDENCE_THRESHOLD
    ]
    result.low_confidence = [
        c for c in outdated_verdicts if c.confidence < CONFIDENCE_THRESHOLD
    ]
    _emit(
        on_progress,
        "status",
        f"{len(result.candidates)} outdated (>= {CONFIDENCE_THRESHOLD} confidence), "
        f"{len(result.low_confidence)} low-confidence flags.",
    )

    if mode == "apply" and result.candidates:
        _emit(on_progress, "phase", "Moving outdated articles...")
        articles_dir = store_dir / "articles"
        for c in result.candidates:
            files_moved, err = move_article_to_outdated(c.id, c.topic, articles_dir)
            if err:
                _emit(on_progress, "error", f"Move failed for {c.id}: {err}")
                continue
            result.moved += files_moved
            entry = articles.get(c.id)
            if entry is not None:
                entry.status = STATUS_OUTDATED
                entry.outdated_reason = c.reason
                entry.outdated_at = today
        spec.save_index(store_dir, articles)
        _emit(on_progress, "phase", "Regenerating landing page...")
        _, result.landing_path = spec.regenerate_landing(store_dir)

    result.report_md_path, result.report_json_path = write_cleanup_report(
        store_dir, spec, result
    )
    return result
