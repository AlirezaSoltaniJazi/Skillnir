"""Security vulnerabilities research pipeline: search CVEs, advisories, and security news."""

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
class Vulnerability:
    """A single security vulnerability or advisory."""

    id: str  # e.g. "cve-2026-1234" or "source-slug-date"
    title: str
    source_url: str
    source_name: str
    published_date: str  # YYYY-MM-DD
    category: str  # key from SECURITY_CATEGORIES
    severity: str  # critical, high, medium, low
    cvss_score: float  # 0.0-10.0
    affected_systems: list[str] = field(default_factory=list)
    description: str = ""
    mitigation: str = ""


@dataclass
class SecurityResult:
    """Result of a security research pipeline run."""

    success: bool
    vulns_found: int = 0
    vulns_new: int = 0
    vulns_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

SECURITY_CATEGORIES: dict[str, str] = {
    "cve-critical": "Critical CVEs",
    "zero-day": "Zero-Day Exploits",
    "supply-chain": "Supply Chain Attacks",
    "web-security": "Web Security (OWASP)",
    "cloud-security": "Cloud & Infrastructure",
    "malware": "Malware & Ransomware",
    "ai-security": "AI & LLM Security",
    "data-breach": "Data Breaches",
    "auth-identity": "Authentication & Identity",
    "open-source": "Open Source Vulnerabilities",
}

CATEGORY_COLORS: dict[str, str] = {
    "cve-critical": "#ef4444",
    "zero-day": "#dc2626",
    "supply-chain": "#f97316",
    "web-security": "#8b5cf6",
    "cloud-security": "#3b82f6",
    "malware": "#b91c1c",
    "ai-security": "#06b6d4",
    "data-breach": "#ec4899",
    "auth-identity": "#f59e0b",
    "open-source": "#10b981",
}

# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

SECURITY_SOURCES: dict[str, str] = {
    "nist-nvd": "NIST NVD (nvd.nist.gov)",
    "cisa": "CISA Advisories (cisa.gov)",
    "github-advisories": "GitHub Security Advisories",
    "bleeping-computer": "Bleeping Computer",
    "krebs": "Krebs on Security",
    "hacker-news-sec": "Hacker News (security)",
    "the-record": "The Record (therecord.media)",
    "dark-reading": "Dark Reading",
}

SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "nist-nvd": ("nvd.nist.gov",),
    "cisa": ("cisa.gov",),
    "github-advisories": ("github.com/advisories",),
    "bleeping-computer": ("bleepingcomputer.com",),
    "krebs": ("krebsonsecurity.com",),
    "hacker-news-sec": ("news.ycombinator.com",),
    "the-record": ("therecord.media",),
    "dark-reading": ("darkreading.com",),
}

SEVERITY_COLORS: dict[str, str] = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#f59e0b",
    "low": "#3b82f6",
}

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

_INDEX_FILE = "security-index.json"


def _get_security_dir() -> Path:
    """Get or create the security data directory."""
    d = Path(__file__).resolve().parent.parent.parent / ".data" / "security"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _load_index(security_dir: Path) -> dict[str, Vulnerability]:
    """Load existing vulnerabilities from index JSON."""
    idx_path = security_dir / _INDEX_FILE
    if not idx_path.exists():
        return {}
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        return {
            item["id"]: Vulnerability(**item) for item in data if isinstance(item, dict)
        }
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(security_dir: Path, vulns: dict[str, Vulnerability]) -> None:
    """Write vulnerability index sorted by date descending."""
    sorted_vulns = sorted(vulns.values(), key=lambda v: v.published_date, reverse=True)
    data = [asdict(v) for v in sorted_vulns]
    idx_path = security_dir / _INDEX_FILE
    idx_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load HTML template from resources directory."""
    tpl = Path(__file__).resolve().parent / "resources" / name
    return tpl.read_text(encoding="utf-8")


def _generate_landing_html(
    vulns: dict[str, Vulnerability],
    security_dir: Path,
    new_ids: set[str] | None = None,
) -> Path:
    """Generate index.html landing page with vulnerability table."""
    sorted_vulns = sorted(vulns.values(), key=lambda v: v.published_date, reverse=True)
    new_ids = new_ids or set()

    rows = []
    for v in sorted_vulns:
        cat_color = CATEGORY_COLORS.get(v.category, "#6b7280")
        sev_color = SEVERITY_COLORS.get(v.severity, "#6b7280")
        title_escaped = html.escape(v.title)
        source_escaped = html.escape(v.source_name)
        cat_label = html.escape(SECURITY_CATEGORIES.get(v.category, v.category))
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;margin-left:8px;">NEW</span>'
            if v.id in new_ids
            else ""
        )
        cvss_display = f"{v.cvss_score:.1f}" if v.cvss_score else "—"
        cvss_color = (
            SEVERITY_COLORS.get("critical")
            if v.cvss_score >= 9.0
            else (
                SEVERITY_COLORS.get("high")
                if v.cvss_score >= 7.0
                else (
                    SEVERITY_COLORS.get("medium")
                    if v.cvss_score >= 4.0
                    else SEVERITY_COLORS.get("low") if v.cvss_score > 0 else "#6b7280"
                )
            )
        )

        rows.append(f"""\
        <tr class="row" data-category="{v.category}" data-source="{v.source_name}" \
data-severity="{v.severity}" style="cursor:pointer;" \
onclick="window.open('{html.escape(v.source_url)}','_blank')">
          <td data-sort="{title_escaped.lower()}" style="padding:10px 12px;">
            <div style="font-weight:600;color:#e2e8f0;">{title_escaped}{badge}</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:2px;">\
{html.escape(v.id)}</div>
          </td>
          <td data-sort="{source_escaped.lower()}" \
style="padding:10px 12px;color:#94a3b8;font-size:13px;">{source_escaped}</td>
          <td data-sort="{v.published_date}" \
style="padding:10px 12px;color:#94a3b8;font-family:monospace;font-size:13px;\
white-space:nowrap;">{v.published_date}</td>
          <td style="padding:10px 12px;white-space:nowrap;">
            <span style="background:{cat_color};color:#fff;padding:2px 10px;\
border-radius:12px;font-size:12px;">{cat_label}</span>
          </td>
          <td data-sort="{v.severity}" style="padding:10px 12px;white-space:nowrap;">
            <span style="background:{sev_color};color:#fff;padding:2px 10px;\
border-radius:12px;font-size:12px;text-transform:uppercase;">\
{v.severity}</span>
          </td>
          <td data-sort="{v.cvss_score}" style="padding:10px 12px;text-align:center;">
            <span style="color:{cvss_color};font-weight:700;font-size:14px;">\
{cvss_display}</span>
          </td>
        </tr>""")

    rows_html = "\n".join(rows)

    # Category chips
    cat_counts: dict[str, int] = {}
    sev_counts: dict[str, int] = {}
    for v in sorted_vulns:
        cat_counts[v.category] = cat_counts.get(v.category, 0) + 1
        sev_counts[v.severity] = sev_counts.get(v.severity, 0) + 1

    all_cat_chip = (
        f'<span class="chip cat-chip active" data-filter="all" '
        f'onclick="toggleCategory(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All: {len(sorted_vulns)}</span>'
    )
    cat_chips = " ".join(
        f'<span class="chip cat-chip" data-filter="{c}" '
        f"onclick=\"toggleCategory('{c}')\" "
        f'style="background:{CATEGORY_COLORS.get(c, "#6b7280")};'
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;'
        f'cursor:pointer;opacity:0.7;">'
        f'{SECURITY_CATEGORIES.get(c, c)}: {n}</span>'
        for c, n in sorted(cat_counts.items(), key=lambda x: -x[1])
    )
    cat_chips_html = all_cat_chip + " " + cat_chips

    # Severity chips
    all_sev_chip = (
        f'<span class="chip sev-chip active" data-filter="all" '
        f'onclick="toggleSeverity(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All: {len(sorted_vulns)}</span>'
    )
    sev_order = ["critical", "high", "medium", "low"]
    sev_chips = " ".join(
        f'<span class="chip sev-chip" data-filter="{s}" '
        f"onclick=\"toggleSeverity('{s}')\" "
        f'style="background:{SEVERITY_COLORS.get(s, "#6b7280")};'
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;'
        f'cursor:pointer;opacity:0.7;text-transform:uppercase;">'
        f'{s}: {sev_counts.get(s, 0)}</span>'
        for s in sev_order
        if sev_counts.get(s, 0) > 0
    )
    sev_chips_html = all_sev_chip + " " + sev_chips

    from datetime import datetime

    total = len(sorted_vulns)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = f"{total} vulnerabilities | Generated: {generated_at}"

    template = _load_template("security-landing.html")
    page_html = (
        template.replace("<!-- SUBTITLE -->", subtitle)
        .replace("<!-- CATEGORY_CHIPS -->", cat_chips_html)
        .replace("<!-- SEVERITY_CHIPS -->", sev_chips_html)
        .replace("<!-- TABLE_ROWS -->", rows_html)
        .replace("<!-- TOTAL_VULNS -->", str(total))
    )

    index_path = security_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


def regenerate_landing(
    security_dir: Path | None = None,
) -> tuple[int, Path | None]:
    """Regenerate the security landing page from existing index."""
    if security_dir is None:
        security_dir = _get_security_dir()
    vulns = _load_index(security_dir)
    if not vulns:
        return 0, None
    index_path = _generate_landing_html(vulns, security_dir)
    return len(vulns), index_path


# ---------------------------------------------------------------------------
# AI prompt
# ---------------------------------------------------------------------------

_SECURITY_PROMPT = """\
You are a cybersecurity researcher. Your task is to find the most critical and \
important security vulnerabilities, CVEs, and advisories from the past 90 days.

## CRITICAL: Output Rules
- Your FINAL message MUST contain the JSON array as text output.
- Do NOT write files. Do NOT use the Write tool or Bash.
- Output ONLY the JSON array — no markdown fences, no explanation.

## Instructions

Use WebSearch and WebFetch to search these sources for recent security vulnerabilities:

1. **NIST NVD** (https://nvd.nist.gov/) — CVE database with CVSS scores
2. **CISA** (https://www.cisa.gov/known-exploited-vulnerabilities-catalog) — known exploited vulnerabilities
3. **GitHub Security Advisories** (https://github.com/advisories) — open source vulnerabilities
4. **Bleeping Computer** (https://www.bleepingcomputer.com/) — security news and advisories
5. **The Record** (https://therecord.media/) — cybersecurity news

Focus on the {vuln_count} most critical and impactful vulnerabilities. Prioritize:
- Actively exploited vulnerabilities (zero-days)
- Critical CVSS 9.0+ CVEs
- Supply chain attacks affecting major packages
- Vulnerabilities in widely-used software (Linux, Windows, browsers, cloud services)
- AI/LLM security issues

{category_instruction}

## Output Format

Your final message must be ONLY this JSON array:

[
  {{{{
    "id": "cve-2026-XXXXX",
    "title": "Vulnerability Title",
    "source_url": "https://...",
    "source_name": "Source Name",
    "published_date": "YYYY-MM-DD",
    "category": "CATEGORY_KEY",
    "severity": "critical",
    "cvss_score": 9.8,
    "affected_systems": ["System 1", "System 2"],
    "description": "2-3 sentence description of the vulnerability and its impact.",
    "mitigation": "Brief mitigation steps or patches available."
  }}}}
]

## Rules
- `id`: Use EXACT CVE ID if available (e.g., "cve-2026-12345"). For non-CVE items use "source-slug-YYYY-MM-DD"
- `category`: must be one of: {category_list}
- `severity`: must be one of: critical, high, medium, low
- `cvss_score`: 0.0-10.0 scale. Use the official CVSS v3.1 score if available, otherwise estimate
- `affected_systems`: list of affected software, libraries, or platforms
- `published_date`: YYYY-MM-DD format
- Do NOT invent CVE IDs — use only real, verified CVE numbers
- Include both actively exploited AND recently disclosed vulnerabilities
- REMEMBER: Output ONLY the JSON array as text. Do NOT write any files.

## Existing vulnerability IDs (skip these — already in our knowledge base)
{existing_ids}
"""


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------


def _search_security_subprocess(
    vuln_count: int,
    categories: list[str],
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[Vulnerability]:
    """Search security vulnerabilities using subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"
    category_list = ", ".join(SECURITY_CATEGORIES.keys())

    if categories and len(categories) < len(SECURITY_CATEGORIES):
        cat_names = [SECURITY_CATEGORIES.get(c, c) for c in categories]
        category_instruction = f"Focus ONLY on these categories: {', '.join(cat_names)}"
    else:
        category_instruction = "Cover all security categories broadly."

    prompt = _SECURITY_PROMPT.format(
        vuln_count=vuln_count,
        category_list=category_list,
        category_instruction=category_instruction,
        existing_ids=existing_ids_str,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=20)

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
            f"collected_chunks={len(collected_text)}, "
            f"stderr_len={len(stderr_output)}",
        )

        if stderr_output:
            _emit(on_progress, "status", f"    [STDERR] {stderr_output[:300]}")

        if proc.returncode != 0:
            _emit(
                on_progress,
                "error",
                f"{info.name} exited with code {proc.returncode}",
            )

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
        f"    [PARSE] collected_text={len(full_text)} chars, "
        f"raw_lines={len(raw_lines)}",
    )

    if full_text:
        _emit(on_progress, "status", f"    [SAMPLE] {full_text[:300]}")

    vulns = _parse_vulns_json(full_text, on_progress)

    if not vulns and raw_lines:
        fallback = _extract_vulns_from_stream(raw_lines, on_progress)
        if fallback:
            return fallback

    return vulns


def _extract_vulns_from_stream(
    raw_lines: list[str],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[Vulnerability]:
    """Extract vulnerability JSON from raw stream lines as fallback."""
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
            vulns = _parse_vulns_json(txt, on_progress)
            if vulns:
                _emit(
                    on_progress,
                    "status",
                    f"    [FALLBACK] Found {len(vulns)} vulns in raw stream",
                )
                return vulns
    return []


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _try_parse_json_array(text: str) -> list[dict]:
    """Try to parse a JSON array from text."""
    text = text.strip()
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group(1))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

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


def _dict_to_vuln(item: dict) -> Vulnerability | None:
    """Convert a dict to a Vulnerability, returning None on failure."""
    try:
        vuln_id = str(item.get("id", "")).strip()
        title = str(item.get("title", "")).strip()
        if not vuln_id or not title:
            return None

        category = str(item.get("category", "")).strip().lower()
        if category not in SECURITY_CATEGORIES:
            category = "cve-critical"

        severity = str(item.get("severity", "medium")).strip().lower()
        if severity not in SEVERITY_COLORS:
            severity = "medium"

        try:
            cvss = round(float(item.get("cvss_score", 0) or 0), 1)
        except ValueError, TypeError:
            cvss = 0.0

        return Vulnerability(
            id=vuln_id,
            title=title,
            source_url=str(item.get("source_url", "")),
            source_name=str(item.get("source_name", "")),
            published_date=str(item.get("published_date", "")),
            category=category,
            severity=severity,
            cvss_score=cvss,
            affected_systems=item.get("affected_systems", []) or [],
            description=str(item.get("description", "")),
            mitigation=str(item.get("mitigation", "")),
        )
    except Exception:
        return None


def _parse_vulns_json(
    text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[Vulnerability]:
    """Parse vulnerability data from collected text."""
    items = _try_parse_json_array(text)
    vulns = []
    for item in items:
        v = _dict_to_vuln(item)
        if v:
            vulns.append(v)
    _emit(on_progress, "status", f"    [RESULT] Parsed {len(vulns)} vulnerabilities")
    return vulns


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


async def search_security(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    categories: list[str] | None = None,
    vuln_count: int = 30,
) -> SecurityResult:
    """Main entry: search security vulnerabilities, generate landing page."""
    _emit(on_progress, "phase", "Initializing security research pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    if not shutil.which(info.cli_command):
        return SecurityResult(
            success=False,
            error=(
                f"{info.cli_command} CLI not found in PATH. "
                "Install it or switch AI tools."
            ),
        )

    security_dir = _get_security_dir()

    existing = _load_index(security_dir)
    existing_ids = set(existing.keys())
    _emit(
        on_progress,
        "status",
        f"  Loaded {len(existing)} existing vulnerabilities",
    )

    selected_cats = list(SECURITY_CATEGORIES.keys())
    if categories:
        selected_cats = [c for c in selected_cats if c in categories]

    _emit(
        on_progress,
        "phase",
        f"Searching for top {vuln_count} security vulnerabilities...",
    )

    loop = asyncio.get_event_loop()
    found_vulns = await loop.run_in_executor(
        None,
        _search_security_subprocess,
        vuln_count,
        selected_cats,
        existing_ids,
        backend,
        model,
        on_progress,
    )

    total_found = len(found_vulns)
    total_new = 0
    new_ids: set[str] = set()

    for v in found_vulns:
        if v.id in existing_ids:
            existing[v.id] = v
            _emit(on_progress, "status", f"  Updated: {v.title}")
        else:
            existing[v.id] = v
            new_ids.add(v.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {v.title}")
        existing_ids.add(v.id)

    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(security_dir, existing)

    index_path = _generate_landing_html(existing, security_dir, new_ids)

    _emit(on_progress, "phase", "Security research complete.")

    return SecurityResult(
        success=True,
        vulns_found=total_found,
        vulns_new=total_new,
        vulns_skipped=total_found - total_new,
        index_path=index_path,
    )
