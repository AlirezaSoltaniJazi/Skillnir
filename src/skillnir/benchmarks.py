"""AI benchmarks pipeline: search and categorize top AI models by benchmark scores."""

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

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class AIModel:
    """A single AI model with benchmark scores."""

    id: str
    name: str
    provider: str
    category_scores: dict[str, float]  # e.g. {"coding": 92.1, "reasoning": 88.5}
    input_price: float  # $ per 1M tokens
    output_price: float  # $ per 1M tokens
    context_window: int  # tokens
    release_date: str  # YYYY-MM-DD or YYYY-MM
    source_urls: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class BenchmarksResult:
    """Result of a benchmarks search pipeline run."""

    success: bool
    models_found: int = 0
    models_new: int = 0
    models_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

BENCHMARK_CATEGORIES: dict[str, str] = {
    "coding": "Coding",
    "reasoning": "Reasoning",
    "math": "Math",
    "general": "General Knowledge",
    "instruction": "Instruction Following",
    "multimodal": "Multimodal",
    "agentic": "Agentic Tasks",
}

# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------

PROVIDER_LABELS: dict[str, str] = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "google": "Google",
    "meta": "Meta",
    "mistral": "Mistral AI",
    "alibaba": "Alibaba (Qwen)",
    "deepseek": "DeepSeek",
    "xai": "xAI",
    "cohere": "Cohere",
    "amazon": "Amazon",
    "other": "Other",
}

PROVIDER_COLORS: dict[str, str] = {
    "anthropic": "#d97706",
    "openai": "#10b981",
    "google": "#3b82f6",
    "meta": "#6366f1",
    "mistral": "#f97316",
    "alibaba": "#ef4444",
    "deepseek": "#06b6d4",
    "xai": "#8b5cf6",
    "cohere": "#ec4899",
    "amazon": "#f59e0b",
    "other": "#6b7280",
}

CATEGORY_COLORS: dict[str, str] = {
    "coding": "#3b82f6",
    "reasoning": "#8b5cf6",
    "math": "#10b981",
    "general": "#f59e0b",
    "instruction": "#ec4899",
    "multimodal": "#06b6d4",
    "agentic": "#ef4444",
}


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

_INDEX_FILE = "benchmarks-index.json"


def _get_benchmarks_dir() -> Path:
    """Get or create the benchmarks data directory."""
    d = Path(__file__).resolve().parent.parent.parent / ".data" / "benchmarks"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_index(benchmarks_dir: Path) -> dict[str, AIModel]:
    """Load existing models from index JSON."""
    idx_path = benchmarks_dir / _INDEX_FILE
    if not idx_path.exists():
        return {}
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        return {item["id"]: AIModel(**item) for item in data if isinstance(item, dict)}
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(benchmarks_dir: Path, models: dict[str, AIModel]) -> None:
    """Write models index sorted by best coding score descending."""
    sorted_models = sorted(
        models.values(),
        key=lambda m: m.category_scores.get("coding", 0),
        reverse=True,
    )
    data = [asdict(m) for m in sorted_models]
    idx_path = benchmarks_dir / _INDEX_FILE
    idx_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# HTML template loader
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load HTML template from resources directory."""
    tpl = Path(__file__).resolve().parent / "resources" / name
    return tpl.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Landing page generation
# ---------------------------------------------------------------------------


def _generate_landing_html(
    models: dict[str, AIModel],
    benchmarks_dir: Path,
    new_ids: set[str] | None = None,
) -> Path:
    """Generate index.html landing page with model comparison table."""
    sorted_models = sorted(
        models.values(),
        key=lambda m: m.category_scores.get("coding", 0),
        reverse=True,
    )
    new_ids = new_ids or set()

    rows = []
    for m in sorted_models:
        provider_color = PROVIDER_COLORS.get(m.provider, "#6b7280")
        provider_name = html.escape(PROVIDER_LABELS.get(m.provider, m.provider))
        name_escaped = html.escape(m.name)
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;border-radius:4px;'
            'font-size:11px;margin-left:8px;">NEW</span>'
            if m.id in new_ids
            else ""
        )

        # Build score cells for each category
        score_cells = ""
        for cat_key in BENCHMARK_CATEGORIES:
            score = m.category_scores.get(cat_key)
            if score is not None and score > 0:
                # Color based on score
                if score >= 85:
                    sc = "#22c55e"
                elif score >= 70:
                    sc = "#f59e0b"
                elif score >= 50:
                    sc = "#f97316"
                else:
                    sc = "#ef4444"
                score_cells += (
                    f'<td data-sort="{score}" style="padding:10px 12px;text-align:center;">'
                    f'<span style="color:{sc};font-weight:600;font-size:13px;">'
                    f'{score:.1f}</span></td>'
                )
            else:
                score_cells += (
                    '<td data-sort="0" style="padding:10px 12px;text-align:center;'
                    'color:#4b5563;">—</td>'
                )

        # Price formatting
        input_price = f"${m.input_price:.2f}" if m.input_price else "—"
        output_price = f"${m.output_price:.2f}" if m.output_price else "—"
        if m.context_window >= 1_000_000:
            ctx = (
                f"{m.context_window / 1_000_000:.0f}M"
                if m.context_window % 1_000_000 == 0
                else f"{m.context_window / 1_000_000:.1f}M"
            )
        elif m.context_window >= 1000:
            ctx = f"{m.context_window // 1000}K"
        else:
            ctx = str(m.context_window)

        rows.append(f"""\
        <tr class="row" data-provider="{m.provider}" style="cursor:default;">
          <td data-sort="{name_escaped.lower()}" style="padding:10px 12px;">
            <div style="font-weight:600;color:#e2e8f0;">{name_escaped}{badge}</div>
          </td>
          <td data-sort="{m.provider}" style="padding:10px 12px;white-space:nowrap;">
            <span style="background:{provider_color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{provider_name}</span>
          </td>
          {score_cells}
          <td data-sort="{m.input_price}" style="padding:10px 12px;text-align:center;font-family:monospace;font-size:12px;color:#94a3b8;">{input_price}</td>
          <td data-sort="{m.output_price}" style="padding:10px 12px;text-align:center;font-family:monospace;font-size:12px;color:#94a3b8;">{output_price}</td>
          <td data-sort="{m.context_window}" style="padding:10px 12px;text-align:center;font-family:monospace;font-size:12px;color:#94a3b8;">{ctx}</td>
        </tr>""")

    rows_html = "\n".join(rows)

    # Provider chips
    provider_counts: dict[str, int] = {}
    for m in sorted_models:
        provider_counts[m.provider] = provider_counts.get(m.provider, 0) + 1

    all_provider_chip = (
        f'<span class="chip provider-chip active" data-filter="all" '
        f'onclick="toggleProvider(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All Providers: {len(sorted_models)}</span>'
    )
    provider_chips = " ".join(
        f'<span class="chip provider-chip" data-filter="{p}" '
        f"onclick=\"toggleProvider('{p}')\" style=\"background:{PROVIDER_COLORS.get(p, '#6b7280')};"
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;'
        f'opacity:0.7;">{PROVIDER_LABELS.get(p, p)}: {c}</span>'
        for p, c in sorted(provider_counts.items(), key=lambda x: -x[1])
    )
    provider_chips_html = all_provider_chip + " " + provider_chips

    # Category header cells
    cat_headers = "".join(
        f'<th onclick="sortTable(this,\'num\')" style="text-align:center;min-width:80px;">'
        f'{label} <span class="sort-arrow"></span></th>'
        for label in BENCHMARK_CATEGORIES.values()
    )

    from datetime import datetime

    total = len(sorted_models)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = f"{total} models | Generated: {generated_at}"

    template = _load_template("benchmarks-landing.html")
    page_html = (
        template.replace("<!-- SUBTITLE -->", subtitle)
        .replace("<!-- PROVIDER_CHIPS -->", provider_chips_html)
        .replace("<!-- TABLE_ROWS -->", rows_html)
        .replace("<!-- TOTAL_MODELS -->", str(total))
        .replace("<!-- CATEGORY_HEADERS -->", cat_headers)
    )

    index_path = benchmarks_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


def regenerate_landing(benchmarks_dir: Path | None = None) -> tuple[int, Path | None]:
    """Regenerate the benchmarks landing page from existing index."""
    if benchmarks_dir is None:
        benchmarks_dir = _get_benchmarks_dir()
    models = _load_index(benchmarks_dir)
    if not models:
        return 0, None
    index_path = _generate_landing_html(models, benchmarks_dir)
    return len(models), index_path


# ---------------------------------------------------------------------------
# AI prompt
# ---------------------------------------------------------------------------

_BENCHMARKS_PROMPT = """\
You are an AI benchmarks researcher. Your task is to find and compile benchmark data \
for the top {model_count} AI language models from multiple authoritative sources.

## CRITICAL: Output Rules
- After your research is complete, your FINAL message MUST contain the JSON array as text output.
- Do NOT write files. Do NOT use the Write tool or Bash to save results.
- Do NOT create any files on disk.
- Simply output the JSON array as your final text response.
- The JSON must start with [ and end with ] — no markdown fences, no explanation before or after.

## Instructions

1. First, WebFetch the **Chatbot Arena Code leaderboard** at https://arena.ai/leaderboard/code \
and extract the top {model_count} models listed there. Use the **EXACT model names** as shown \
on the leaderboard (e.g., "GPT-5.3-Codex", "Claude Opus 4.6", "Gemini 3.1 Pro"). \
Do NOT rename, abbreviate, or modify model names in any way.

2. Then WebFetch **Artificial Analysis** at https://artificialanalysis.ai/leaderboards/models \
to get pricing (input/output per 1M tokens), context window, and intelligence index for each model.

3. Then WebFetch **SWE-bench** at https://www.swebench.com/ to get coding/agentic scores.

For each model, gather:
- Benchmark scores across categories (coding, reasoning, math, general, instruction, multimodal, agentic)
- Pricing (input and output per 1M tokens in USD)
- Context window size
- Release date

## CRITICAL: Model Naming
- Use the EXACT model name as it appears on arena.ai/leaderboard/code
- Do NOT invent names, merge models, or use generic names
- If arena.ai says "GPT-5.3-Codex", use exactly "GPT-5.3-Codex" — not "GPT-5" or "GPT-5.3"
- The `name` field must match the leaderboard exactly

## Output Format

Your final message must be ONLY this JSON array (no other text, no markdown, no explanation):

[
  {{{{
    "id": "provider-modelname",
    "name": "Model Display Name",
    "provider": "PROVIDER_KEY",
    "category_scores": {{{{
      "coding": 92.1,
      "reasoning": 88.5,
      "math": 85.0,
      "general": 90.2,
      "instruction": 87.3,
      "multimodal": 0,
      "agentic": 75.0
    }}}},
    "input_price": 3.00,
    "output_price": 15.00,
    "context_window": 200000,
    "release_date": "2025-06",
    "source_urls": ["https://..."],
    "notes": "Brief note about the model"
  }}}}
]

## Rules
- `name`: EXACT name from arena.ai leaderboard — do NOT modify
- `id`: lowercase version of the name with hyphens, e.g., "GPT-5.3-Codex" becomes `openai-gpt-5-3-codex`
- `provider`: must be one of: {provider_list}
- `category_scores`: 0-100 scale. Use 0 if the model doesn't support that category. Normalize scores to 0-100 if needed.
- `input_price` / `output_price`: USD per 1 million tokens. Use 0 for free/open-source models.
- `context_window`: in tokens (e.g., 200000 for 200K)
- `release_date`: YYYY-MM format
- `source_urls`: 1-3 URLs where you found the benchmark data
- Include both proprietary AND open-source models
- REMEMBER: Output ONLY the JSON array as text. Do NOT write any files.

## Existing Model IDs (update these with latest data rather than skipping)
{existing_ids}
"""


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------


def _search_benchmarks_subprocess(
    model_count: int,
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[AIModel]:
    """Search benchmarks using subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"
    provider_list = ", ".join(PROVIDER_LABELS.keys())

    prompt = _BENCHMARKS_PROMPT.format(
        model_count=model_count,
        provider_list=provider_list,
        existing_ids=existing_ids_str,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=30)

    # Enable web tools for research
    if backend == AIBackend.CLAUDE:
        try:
            idx = cmd.index("--allowedTools")
            cmd[idx + 1] = "WebFetch,WebSearch"
        except ValueError:
            pass

    collected_text: list[str] = []
    raw_lines: list[str] = []

    cmd_display = " ".join(cmd[:8]) + " ..."
    _emit(on_progress, "status", f"    [CMD] {cmd_display}")
    _emit(on_progress, "status", f"    [CMD] prompt length: {len(prompt)} chars")

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        _emit(on_progress, "status", f"    [PID] subprocess started: pid={proc.pid}")

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
                    f"    [STDOUT line {line_count}] {line[:120].strip()}",
                )
            parse_stream_line(backend, line, collect_progress)

        proc.wait(timeout=600)
        stderr_thread.join(timeout=5)
        stderr_output = "".join(stderr_chunks)

        _emit(
            on_progress,
            "status",
            f"    [DONE] exit={proc.returncode}, stdout_lines={line_count}, "
            f"collected_chunks={len(collected_text)}, stderr_len={len(stderr_output)}",
        )

        if stderr_output:
            _emit(on_progress, "status", f"    [STDERR] {stderr_output[:300]}")

        if proc.returncode != 0:
            _emit(
                on_progress, "error", f"{info.name} exited with code {proc.returncode}"
            )
            # Still try to parse — the model may have output JSON before erroring

    except subprocess.TimeoutExpired:
        proc.kill()
        _emit(on_progress, "error", f"{info.name} timed out")
        return []
    except FileNotFoundError:
        _emit(on_progress, "error", f"{info.cli_command} CLI not found in PATH")
        return []
    except Exception as e:
        _emit(on_progress, "error", f"    [EXCEPTION] {type(e).__name__}: {e}")
        return []

    full_text = "".join(collected_text)
    _emit(
        on_progress,
        "status",
        f"    [PARSE] collected_text={len(full_text)} chars, raw_lines={len(raw_lines)}",
    )

    if full_text:
        _emit(on_progress, "status", f"    [SAMPLE] {full_text[:300]}")

    models = _parse_models_json(full_text, on_progress)

    # Fallback: search raw stdout lines for JSON if collected_text failed
    if not models and raw_lines:
        fallback = _extract_models_from_stream(raw_lines, on_progress)
        if fallback:
            return fallback

    return models


def _extract_models_from_stream(
    raw_lines: list[str],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[AIModel]:
    """Extract model JSON from raw stream lines when normal collection fails."""
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError, ValueError:
            continue
        msg = obj.get("message", obj.get("result", {}))
        if not isinstance(msg, dict):
            continue
        for block in msg.get("content", []):
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            txt = block.get("text", "")
            if "[" not in txt or "]" not in txt:
                continue
            models = _parse_models_json(txt, on_progress)
            if models:
                _emit(
                    on_progress,
                    "status",
                    f"    [FALLBACK] Found {len(models)} models in raw stream",
                )
                return models
    return []


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _try_parse_json_array(text: str) -> list[dict]:
    """Try to parse a JSON array from text, extracting from markdown if needed."""
    # Try direct parse
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # Try finding array brackets
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        try:
            data = json.loads(text[start : end + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    return []


def _dict_to_model(item: dict) -> AIModel | None:
    """Convert a dict to an AIModel, returning None on failure."""
    try:
        model_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        provider = str(item.get("provider", "other")).strip().lower()
        if not model_id or not name:
            return None

        if provider not in PROVIDER_LABELS:
            provider = "other"

        scores_raw = item.get("category_scores", {})
        category_scores = {}
        for cat in BENCHMARK_CATEGORIES:
            val = scores_raw.get(cat)
            if val is not None:
                try:
                    category_scores[cat] = round(float(val), 1)
                except ValueError, TypeError:
                    category_scores[cat] = 0.0
            else:
                category_scores[cat] = 0.0

        return AIModel(
            id=model_id,
            name=name,
            provider=provider,
            category_scores=category_scores,
            input_price=float(item.get("input_price", 0) or 0),
            output_price=float(item.get("output_price", 0) or 0),
            context_window=int(item.get("context_window", 0) or 0),
            release_date=str(item.get("release_date", "")),
            source_urls=item.get("source_urls", []) or [],
            notes=str(item.get("notes", "")),
        )
    except Exception:
        return None


def _parse_models_json(
    text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[AIModel]:
    """Parse AI model data from collected text."""
    items = _try_parse_json_array(text)
    models = []
    for item in items:
        m = _dict_to_model(item)
        if m:
            models.append(m)
    _emit(on_progress, "status", f"    [RESULT] Parsed {len(models)} models")
    return models


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


async def search_benchmarks(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    model_count: int = 30,
) -> BenchmarksResult:
    """Main entry: search benchmarks, categorize models, generate landing page."""
    _emit(on_progress, "phase", "Initializing AI benchmarks pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    # Check CLI availability
    if not shutil.which(info.cli_command):
        return BenchmarksResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH. Install it or switch AI tools.",
        )

    benchmarks_dir = _get_benchmarks_dir()

    # Load existing index
    existing = _load_index(benchmarks_dir)
    existing_ids = set(existing.keys())
    _emit(on_progress, "status", f"  Loaded {len(existing)} existing models")

    _emit(
        on_progress,
        "phase",
        f"Searching benchmarks for top {model_count} AI models...",
    )

    loop = asyncio.get_event_loop()
    found_models = await loop.run_in_executor(
        None,
        _search_benchmarks_subprocess,
        model_count,
        existing_ids,
        backend,
        model,
        on_progress,
    )

    total_found = len(found_models)
    total_new = 0
    new_ids: set[str] = set()

    for m in found_models:
        if m.id in existing_ids:
            # Update existing model with latest data
            existing[m.id] = m
            _emit(on_progress, "status", f"  Updated: {m.name}")
        else:
            existing[m.id] = m
            new_ids.add(m.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {m.name}")
        existing_ids.add(m.id)

    # Save updated index
    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(benchmarks_dir, existing)

    # Generate landing page
    index_path = _generate_landing_html(existing, benchmarks_dir, new_ids)

    _emit(on_progress, "phase", "Benchmarks search complete.")

    return BenchmarksResult(
        success=True,
        models_found=total_found,
        models_new=total_new,
        models_skipped=total_found - total_new,
        index_path=index_path,
    )
