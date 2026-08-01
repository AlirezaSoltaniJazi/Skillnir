"""Package-vulnerability research pipeline.

Searches package-registry advisory databases (GitHub Advisory DB, OSV, Snyk,
…) for known vulnerabilities in published packages across the top language
ecosystems, and records — per advisory — which package is affected, which
version ranges are vulnerable, and which version resolves the issue.

Mirrors the security.py / benchmarks.py intel pattern: AI web-search →
JSON parse → dedup'd index → self-contained landing page. Distinct from
security.py, which is CVE/advisory-general and has no package/version schema.
"""

import asyncio
import html
import json
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass, fields
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
class PackageVulnerability:
    """A single package advisory: what's vulnerable, which versions, the fix."""

    id: str  # lowercased GHSA/CVE id, else "ecosystem-package-YYYY-MM-DD"
    package_name: str  # e.g. "axios"
    ecosystem: str  # key from ECOSYSTEMS (npm, pypi, maven, ...)
    title: str
    severity: str  # critical | high | medium | low
    cvss_score: float  # 0.0-10.0
    affected_versions: str  # human range, e.g. ">=1.0.0, <1.6.0"
    fixed_version: str  # version that resolves it, e.g. "1.6.0" (or "")
    cve_id: str = ""  # CVE id when distinct from id
    published_date: str = ""  # YYYY-MM-DD
    advisory_url: str = ""  # GHSA / OSV / CVE link
    source_name: str = ""  # "GitHub Advisory DB" / "OSV" / "Snyk" ...
    summary: str = ""  # 2-3 sentence what/impact
    recommendation: str = ""  # "Upgrade to >= 1.6.0" / mitigation


@dataclass
class PackageVulnsResult:
    """Result of a package-vulnerability pipeline run."""

    success: bool
    vulns_found: int = 0
    vulns_new: int = 0
    vulns_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Ecosystems (top 10 package registries)
# ---------------------------------------------------------------------------

ECOSYSTEMS: dict[str, str] = {
    "npm": "npm (JS/TS)",
    "pypi": "PyPI (Python)",
    "maven": "Maven (Java/Kotlin)",
    "go": "Go modules",
    "crates": "crates.io (Rust)",
    "rubygems": "RubyGems (Ruby)",
    "packagist": "Packagist (PHP)",
    "nuget": "NuGet (C#/.NET)",
    "pub": "Pub (Dart/Flutter)",
    "hex": "Hex (Elixir/Erlang)",
}

DEFAULT_ECOSYSTEM = "npm"

# Common aliases the AI might emit → canonical ecosystem key.
_ECOSYSTEM_ALIASES: dict[str, str] = {
    "yarn": "npm",
    "pnpm": "npm",
    "node": "npm",
    "javascript": "npm",
    "typescript": "npm",
    "pip": "pypi",
    "python": "pypi",
    "pipenv": "pypi",
    "poetry": "pypi",
    "gradle": "maven",
    "java": "maven",
    "kotlin": "maven",
    "golang": "go",
    "gomod": "go",
    "cargo": "crates",
    "crates.io": "crates",
    "rust": "crates",
    "gem": "rubygems",
    "ruby": "rubygems",
    "composer": "packagist",
    "php": "packagist",
    "dotnet": "nuget",
    ".net": "nuget",
    "csharp": "nuget",
    "dart": "pub",
    "flutter": "pub",
    "elixir": "hex",
    "erlang": "hex",
}

ECOSYSTEM_COLORS: dict[str, str] = {
    "npm": "#cb3837",
    "pypi": "#3b82f6",
    "maven": "#f97316",
    "go": "#06b6d4",
    "crates": "#a855f7",
    "rubygems": "#dc2626",
    "packagist": "#8b5cf6",
    "nuget": "#6366f1",
    "pub": "#0ea5e9",
    "hex": "#8b5cf6",
}

SEVERITY_COLORS: dict[str, str] = {
    "critical": "#ef4444",
    "high": "#f97316",
    "medium": "#f59e0b",
    "low": "#3b82f6",
}

_SEVERITY_RANK: dict[str, int] = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# Advisory sources the AI is told to consult (for the prompt only).
ECOSYSTEM_SOURCES: dict[str, str] = {
    "github-advisories": "GitHub Advisory Database (github.com/advisories)",
    "osv": "OSV.dev (osv.dev)",
    "snyk": "Snyk Vulnerability DB (security.snyk.io)",
    "npm-advisories": "npm advisories (npmjs.com/advisories)",
    "pypa": "PyPA Advisory Database / Safety DB",
    "rustsec": "RustSec Advisory DB (rustsec.org)",
}


# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------

_INDEX_FILE = "package-vulns-index.json"

_PKGVULN_FIELDS = frozenset(f.name for f in fields(PackageVulnerability))


def _get_package_vulns_dir() -> Path:
    """Get or create the package-vulns data directory."""
    d = Path(__file__).resolve().parent.parent.parent / ".data" / "package-vulns"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sort_key(v: PackageVulnerability) -> tuple[int, str]:
    """Sort by severity rank (critical first), then newest date."""
    return (_SEVERITY_RANK.get(v.severity, 9), _neg_date(v.published_date))


def _neg_date(date_str: str) -> str:
    """Invert a YYYY-MM-DD string so ascending sort yields newest-first."""
    # Map each digit d -> (9 - d) so lexicographic asc == chronological desc.
    return "".join(str(9 - int(c)) if c.isdigit() else c for c in date_str)


def _load_index(pkg_dir: Path) -> dict[str, PackageVulnerability]:
    """Load existing package vulnerabilities from index JSON.

    Field-filtered so a legacy/forward index (missing or extra keys) still
    loads instead of blanking the whole store.
    """
    idx_path = pkg_dir / _INDEX_FILE
    if not idx_path.exists():
        return {}
    try:
        data = json.loads(idx_path.read_text(encoding="utf-8"))
        return {
            item["id"]: PackageVulnerability(
                **{k: v for k, v in item.items() if k in _PKGVULN_FIELDS}
            )
            for item in data
            if isinstance(item, dict) and item.get("id")
        }
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(pkg_dir: Path, vulns: dict[str, PackageVulnerability]) -> None:
    """Write index sorted by severity then date descending."""
    sorted_vulns = sorted(vulns.values(), key=_sort_key)
    data = [asdict(v) for v in sorted_vulns]
    idx_path = pkg_dir / _INDEX_FILE
    idx_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# HTML template + landing page
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load HTML template from resources directory."""
    tpl = Path(__file__).resolve().parent / "resources" / name
    return tpl.read_text(encoding="utf-8")


def _cvss_color(score: float) -> str:
    """Color a CVSS score by severity band."""
    if score >= 9.0:
        return SEVERITY_COLORS["critical"]
    if score >= 7.0:
        return SEVERITY_COLORS["high"]
    if score >= 4.0:
        return SEVERITY_COLORS["medium"]
    if score > 0:
        return SEVERITY_COLORS["low"]
    return "#6b7280"


def _generate_landing_html(
    vulns: dict[str, PackageVulnerability],
    pkg_dir: Path,
    new_ids: set[str] | None = None,
) -> Path:
    """Generate index.html landing page with the package-vulnerability table."""
    sorted_vulns = sorted(vulns.values(), key=_sort_key)
    new_ids = new_ids or set()

    rows = []
    for v in sorted_vulns:
        eco_color = ECOSYSTEM_COLORS.get(v.ecosystem, "#6b7280")
        sev_color = SEVERITY_COLORS.get(v.severity, "#6b7280")
        pkg_escaped = html.escape(v.package_name)
        eco_label = html.escape(ECOSYSTEMS.get(v.ecosystem, v.ecosystem))
        affected = html.escape(v.affected_versions or "—")
        fixed = html.escape(v.fixed_version or "—")
        id_escaped = html.escape(v.id)
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;'
            'border-radius:4px;font-size:11px;margin-left:8px;">NEW</span>'
            if v.id in new_ids
            else ""
        )
        cvss_display = f"{v.cvss_score:.1f}" if v.cvss_score else "—"
        cvss_color = _cvss_color(v.cvss_score)
        link = html.escape(v.advisory_url) if v.advisory_url else ""
        onclick = f"window.open('{link}','_blank')" if link else ""

        rows.append(f"""\
        <tr class="row" data-ecosystem="{v.ecosystem}" data-severity="{v.severity}" \
style="cursor:{'pointer' if onclick else 'default'};" onclick="{onclick}">
          <td data-sort="{pkg_escaped.lower()}" style="padding:10px 12px;">
            <div style="font-weight:600;color:#e2e8f0;">{pkg_escaped}{badge}</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:2px;">{id_escaped}</div>
          </td>
          <td data-sort="{v.ecosystem}" style="padding:10px 12px;white-space:nowrap;">
            <span style="background:{eco_color};color:#fff;padding:2px 10px;\
border-radius:12px;font-size:12px;">{eco_label}</span>
          </td>
          <td style="padding:10px 12px;color:#cbd5e1;font-family:monospace;\
font-size:13px;">{affected}</td>
          <td style="padding:10px 12px;color:#34d399;font-family:monospace;\
font-size:13px;font-weight:600;">{fixed}</td>
          <td data-sort="{v.severity}" style="padding:10px 12px;white-space:nowrap;">
            <span style="background:{sev_color};color:#fff;padding:2px 10px;\
border-radius:12px;font-size:12px;text-transform:uppercase;">{v.severity}</span>
          </td>
          <td data-sort="{v.cvss_score}" style="padding:10px 12px;text-align:center;">
            <span style="color:{cvss_color};font-weight:700;font-size:14px;">\
{cvss_display}</span>
          </td>
          <td data-sort="{v.published_date}" \
style="padding:10px 12px;color:#94a3b8;font-family:monospace;font-size:13px;\
white-space:nowrap;">{v.published_date or '—'}</td>
        </tr>""")

    rows_html = "\n".join(rows)

    eco_counts: dict[str, int] = {}
    sev_counts: dict[str, int] = {}
    for v in sorted_vulns:
        eco_counts[v.ecosystem] = eco_counts.get(v.ecosystem, 0) + 1
        sev_counts[v.severity] = sev_counts.get(v.severity, 0) + 1

    all_eco_chip = (
        f'<span class="chip eco-chip active" data-filter="all" '
        f'onclick="toggleEcosystem(\'all\')" style="background:#475569;color:#fff;'
        f'padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f'All: {len(sorted_vulns)}</span>'
    )
    eco_chips = " ".join(
        f'<span class="chip eco-chip" data-filter="{e}" '
        f"onclick=\"toggleEcosystem('{e}')\" "
        f'style="background:{ECOSYSTEM_COLORS.get(e, "#6b7280")};'
        f'color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;'
        f'cursor:pointer;opacity:0.7;">'
        f'{ECOSYSTEMS.get(e, e)}: {n}</span>'
        for e, n in sorted(eco_counts.items(), key=lambda x: -x[1])
    )
    eco_chips_html = all_eco_chip + " " + eco_chips

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
    subtitle = f"{total} package advisories | Generated: {generated_at}"

    template = _load_template("package-vulns-landing.html")
    page_html = (
        template.replace("<!-- SUBTITLE -->", subtitle)
        .replace("<!-- ECOSYSTEM_CHIPS -->", eco_chips_html)
        .replace("<!-- SEVERITY_CHIPS -->", sev_chips_html)
        .replace("<!-- TABLE_ROWS -->", rows_html)
        .replace("<!-- TOTAL_VULNS -->", str(total))
    )

    index_path = pkg_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


def regenerate_landing(pkg_dir: Path | None = None) -> tuple[int, Path | None]:
    """Regenerate the package-vulns landing page from the existing index."""
    if pkg_dir is None:
        pkg_dir = _get_package_vulns_dir()
    vulns = _load_index(pkg_dir)
    if not vulns:
        return 0, None
    index_path = _generate_landing_html(vulns, pkg_dir)
    return len(vulns), index_path


# ---------------------------------------------------------------------------
# AI prompt
# ---------------------------------------------------------------------------

_PACKAGE_VULNS_PROMPT = """\
You are a package-security researcher. Find the most important KNOWN \
vulnerabilities in PUBLISHED software packages (libraries/dependencies) across \
language ecosystems, disclosed in the past 120 days.

## CRITICAL: Output Rules
- Your FINAL message MUST contain the JSON array as text output.
- Do NOT write files. Do NOT use the Write tool or Bash.
- Output ONLY the JSON array — no markdown fences, no explanation.

## Instructions

Use WebSearch and WebFetch on package advisory databases:
1. GitHub Advisory Database (https://github.com/advisories)
2. OSV.dev (https://osv.dev/)
3. Snyk Vulnerability DB (https://security.snyk.io/)
4. npm advisories, PyPA/Safety DB, RustSec, and registry-native advisories

Focus on the {vuln_count} highest-impact package advisories. Prioritize:
- Critical / high severity in widely-depended-on packages (e.g. axios, lodash, requests, log4j)
- Supply-chain compromises and malicious/hijacked package releases
- Advisories that already have a fixed version available

{ecosystem_instruction}

## Output Format

Your final message must be ONLY this JSON array:

[
  {{
    "id": "ghsa-xxxx-xxxx-xxxx",
    "package_name": "axios",
    "ecosystem": "npm",
    "title": "Short advisory title",
    "severity": "critical",
    "cvss_score": 9.1,
    "affected_versions": ">=1.0.0, <1.6.0",
    "fixed_version": "1.6.0",
    "cve_id": "CVE-2026-XXXXX",
    "published_date": "YYYY-MM-DD",
    "advisory_url": "https://github.com/advisories/GHSA-xxxx-xxxx-xxxx",
    "source_name": "GitHub Advisory DB",
    "summary": "2-3 sentence description of the flaw and its impact.",
    "recommendation": "Upgrade to >= 1.6.0."
  }}
]

## Rules
- `id`: prefer the real GHSA id (lowercased), else the real CVE id (lowercased), else "ecosystem-package-YYYY-MM-DD". NEVER invent IDs.
- `package_name`: the exact registry package name (required).
- `ecosystem`: MUST be one of: {ecosystem_list}
- `severity`: one of critical, high, medium, low
- `cvss_score`: 0.0-10.0 (official CVSS v3.1 if available, else best estimate)
- `affected_versions`: the vulnerable version range in registry syntax
- `fixed_version`: the FIRST version that resolves it (empty string if no fix yet)
- `published_date`: YYYY-MM-DD
- Use ONLY real, verifiable advisories from the sources above.
- REMEMBER: Output ONLY the JSON array as text. Do NOT write any files.

## Existing advisory IDs (skip these — already in our knowledge base)
{existing_ids}
"""


# ---------------------------------------------------------------------------
# Subprocess execution
# ---------------------------------------------------------------------------


def _search_package_vulns_subprocess(
    vuln_count: int,
    ecosystems: list[str],
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[PackageVulnerability]:
    """Search package vulnerabilities using the backend CLI subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"
    ecosystem_list = ", ".join(ECOSYSTEMS.keys())

    if ecosystems and len(ecosystems) < len(ECOSYSTEMS):
        eco_names = [ECOSYSTEMS.get(e, e) for e in ecosystems]
        ecosystem_instruction = (
            f"Focus ONLY on these ecosystems: {', '.join(eco_names)}"
        )
    else:
        ecosystem_instruction = "Cover all listed ecosystems broadly."

    prompt = _PACKAGE_VULNS_PROMPT.format(
        vuln_count=vuln_count,
        ecosystem_list=ecosystem_list,
        ecosystem_instruction=ecosystem_instruction,
        existing_ids=existing_ids_str,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=25)

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

    vulns = _parse_pkgvulns_json(full_text, on_progress)

    if not vulns and raw_lines:
        fallback = _extract_pkgvulns_from_stream(raw_lines, on_progress)
        if fallback:
            return fallback

    return vulns


def _extract_pkgvulns_from_stream(
    raw_lines: list[str],
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[PackageVulnerability]:
    """Extract advisory JSON from raw stream lines as a fallback."""
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
            vulns = _parse_pkgvulns_json(txt, on_progress)
            if vulns:
                _emit(
                    on_progress,
                    "status",
                    f"    [FALLBACK] Found {len(vulns)} advisories in raw stream",
                )
                return vulns
    return []


# ---------------------------------------------------------------------------
# JSON parsing
# ---------------------------------------------------------------------------


def _try_parse_json_array(text: str) -> list[dict]:
    """Try to parse a JSON array from text (three strategies)."""
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


def _normalize_ecosystem(raw: str) -> str:
    """Map a raw ecosystem string to a canonical ECOSYSTEMS key."""
    eco = raw.strip().lower()
    if eco in ECOSYSTEMS:
        return eco
    return _ECOSYSTEM_ALIASES.get(eco, DEFAULT_ECOSYSTEM)


def _dict_to_pkgvuln(item: dict) -> PackageVulnerability | None:
    """Convert a dict to a PackageVulnerability, returning None on failure."""
    try:
        vuln_id = str(item.get("id", "")).strip().lower()
        package_name = str(item.get("package_name", "")).strip()
        if not vuln_id or not package_name:
            return None

        ecosystem = _normalize_ecosystem(str(item.get("ecosystem", "")))

        severity = str(item.get("severity", "medium")).strip().lower()
        if severity not in SEVERITY_COLORS:
            severity = "medium"

        try:
            cvss = round(float(item.get("cvss_score", 0) or 0), 1)
        except ValueError, TypeError:
            cvss = 0.0

        return PackageVulnerability(
            id=vuln_id,
            package_name=package_name,
            ecosystem=ecosystem,
            title=str(item.get("title", "")).strip() or package_name,
            severity=severity,
            cvss_score=cvss,
            affected_versions=str(item.get("affected_versions", "")).strip(),
            fixed_version=str(item.get("fixed_version", "")).strip(),
            cve_id=str(item.get("cve_id", "")).strip(),
            published_date=str(item.get("published_date", "")).strip(),
            advisory_url=str(item.get("advisory_url", "")).strip(),
            source_name=str(item.get("source_name", "")).strip(),
            summary=str(item.get("summary", "")).strip(),
            recommendation=str(item.get("recommendation", "")).strip(),
        )
    except Exception:
        return None


def _parse_pkgvulns_json(
    text: str,
    on_progress: Callable[[GenerationProgress], None] | None = None,
) -> list[PackageVulnerability]:
    """Parse advisory data from collected text."""
    items = _try_parse_json_array(text)
    vulns = []
    for item in items:
        if not isinstance(item, dict):
            continue
        v = _dict_to_pkgvuln(item)
        if v:
            vulns.append(v)
    _emit(on_progress, "status", f"    [RESULT] Parsed {len(vulns)} advisories")
    return vulns


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


async def search_package_vulns(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    ecosystems: list[str] | None = None,
    vuln_count: int = 30,
) -> PackageVulnsResult:
    """Main entry: search package advisories, update index, regenerate landing."""
    _emit(on_progress, "phase", "Initializing package-vulnerability pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    if not shutil.which(info.cli_command):
        return PackageVulnsResult(
            success=False,
            error=(
                f"{info.cli_command} CLI not found in PATH. "
                "Install it or switch AI tools."
            ),
        )

    pkg_dir = _get_package_vulns_dir()

    existing = _load_index(pkg_dir)
    existing_ids = set(existing.keys())
    _emit(on_progress, "status", f"  Loaded {len(existing)} existing advisories")

    selected_ecos = list(ECOSYSTEMS.keys())
    if ecosystems:
        selected_ecos = [e for e in selected_ecos if e in ecosystems]

    _emit(
        on_progress,
        "phase",
        f"Searching for top {vuln_count} package advisories...",
    )

    loop = asyncio.get_event_loop()
    found_vulns = await loop.run_in_executor(
        None,
        _search_package_vulns_subprocess,
        vuln_count,
        selected_ecos,
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
            _emit(on_progress, "status", f"  Updated: {v.package_name} ({v.id})")
        else:
            existing[v.id] = v
            new_ids.add(v.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {v.package_name} ({v.id})")
        existing_ids.add(v.id)

    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(pkg_dir, existing)

    index_path = _generate_landing_html(existing, pkg_dir, new_ids)

    _emit(on_progress, "phase", "Package-vulnerability search complete.")

    return PackageVulnsResult(
        success=True,
        vulns_found=total_found,
        vulns_new=total_new,
        vulns_skipped=total_found - total_new,
        index_path=index_path,
    )
