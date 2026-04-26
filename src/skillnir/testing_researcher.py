"""Testing-research pipeline: search the web for QA / testing news, deep-read articles, summarize, generate landing page.

Sibling of :mod:`skillnir.researcher` (AI-engineering domain). Same data
model, dedup, HTML / markdown writers, landing-page builder, and
subprocess flow — only the topic catalog, source allowlist, output
directory, and prompt focus differ. Designed so the two domains can
evolve independently; a future refactor can extract a shared engine
once a 3rd domain is needed.
"""

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
# Data models — same shape as researcher.Article, scoped to this module
# ---------------------------------------------------------------------------


@dataclass
class Article:
    """A single testing-research article with deep summary."""

    id: str  # sourcename-YYYY-MM-DD (dedup key)
    title: str
    source_url: str
    source_name: str
    published_date: str  # YYYY-MM-DD
    topic: str  # test-automation, manual-testing, ai-in-testing, etc.
    key_insights: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class TestingResearchResult:
    """Result of a testing-research pipeline run."""

    success: bool
    articles_found: int = 0
    articles_new: int = 0
    articles_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Topics — 16 testing / QA topic queries
# ---------------------------------------------------------------------------

RESEARCH_TOPICS: tuple[str, ...] = (
    "test automation frameworks Playwright Cypress WebDriverIO Selenium 2025 2026",
    "manual testing exploratory SBTM session-based heuristics ISTQB 2025 2026",
    "AI in software testing GenAI test generation autonomous QA self-healing 2026",
    "performance load testing k6 JMeter Gatling Locust observability 2025 2026",
    "API testing contract testing Postman REST Assured Pact Karate gRPC 2025 2026",
    "mobile testing Appium Detox Maestro real device cloud 2025 2026",
    "accessibility testing WCAG 2.2 axe-core NVDA JAWS VoiceOver ARIA 2025 2026",
    "security testing OWASP ZAP Burp SAST DAST dependency audit fuzz 2025 2026",
    "visual regression testing Percy Applitools Chromatic Playwright snapshots 2025 2026",
    "test data management synthetic data masking GDPR HIPAA factories 2025 2026",
    "chaos engineering resilience Chaos Mesh Litmus Gremlin fault injection 2025 2026",
    "testops CI CD test sharding parallelization flake detection quarantine 2025 2026",
    "BDD TDD Cucumber SpecFlow Karate Gherkin patterns ATDD 2025 2026",
    "quality engineering culture shift-left shift-right SDET DORA metrics 2025 2026",
    "test reporting tools Allure TestRail Xray Zephyr qTest 2025 2026",
    "QA conferences communities Ministry of Testing EuroSTAR TestBash Selenium Conf 2025 2026",
)

TOPIC_LABELS: dict[str, str] = {
    "test-automation": "Test Automation Frameworks",
    "manual-testing": "Manual & Exploratory Testing",
    "ai-in-testing": "AI in Testing",
    "performance-testing": "Performance & Load",
    "api-testing": "API & Contract Testing",
    "mobile-testing": "Mobile Testing",
    "accessibility-testing": "Accessibility Testing",
    "security-testing": "Security Testing",
    "visual-regression": "Visual Regression",
    "test-data-management": "Test Data Management",
    "chaos-engineering": "Chaos Engineering & Resilience",
    "testops-cicd": "TestOps & CI/CD",
    "bdd-tdd": "BDD / TDD",
    "quality-engineering": "Quality Engineering Culture",
    "test-reporting": "Test Reporting & Tools",
    "qa-conferences": "QA Conferences & Communities",
}


# ---------------------------------------------------------------------------
# Preferred sources — 35 high-quality testing / QA domains
# ---------------------------------------------------------------------------

PREFERRED_SOURCES: tuple[str, ...] = (
    "ministryoftesting.com",
    "developsense.com",
    "satisfice.com",
    "testrail.com",
    "saucelabs.com",
    "browserstack.com",
    "lambdatest.com",
    "bugbug.io",
    "katalon.com",
    "functionize.com",
    "selenium.dev",
    "playwright.dev",
    "cypress.io",
    "webdriver.io",
    "appium.io",
    "postman.com",
    "pact.io",
    "k6.io",
    "grafana.com",
    "testguild.com",
    "dzone.com",
    "qualitybits.substack.com",
    "stickyminds.com",
    "infoq.com",
    "smartbear.com",
    "tricentis.com",
    "applitools.com",
    "mabl.com",
    "testsigma.com",
    "kobiton.com",
    "perfecto.io",
    "testautomationu.applitools.com",
    "softwaretestinghelp.com",
    "guru99.com",
    "thenewstack.io",
)


# ---------------------------------------------------------------------------
# Source filters — UI-facing groups, mapped to domain tuples
# ---------------------------------------------------------------------------

SOURCE_FILTERS: dict[str, str] = {
    "thought-leaders": "Thought Leaders (Bach, Bolton, Ministry of Testing)",
    "vendor-blogs": "Vendor Blogs (BrowserStack, Sauce Labs, LambdaTest, Tricentis, SmartBear)",
    "framework-docs": "Framework Docs (Playwright, Cypress, WebdriverIO, Selenium, Appium)",
    "ai-testing-tools": "AI Testing Tools (Mabl, Applitools, Functionize, Testsigma)",
    "performance-tools": "Performance Tools (k6, Grafana, Postman)",
    "test-management": "Test Management (TestRail, Katalon)",
    "communities": "Communities (Ministry of Testing, TestGuild, StickyMinds, InfoQ)",
    "tutorials": "Tutorials (Guru99, Software Testing Help, Test Automation University)",
    "tech-news": "Tech News (DZone, The New Stack)",
    "newsletters": "Newsletters (Quality Bits)",
}

SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "thought-leaders": (
        "ministryoftesting.com",
        "developsense.com",
        "satisfice.com",
    ),
    "vendor-blogs": (
        "browserstack.com",
        "saucelabs.com",
        "lambdatest.com",
        "tricentis.com",
        "smartbear.com",
        "perfecto.io",
        "kobiton.com",
    ),
    "framework-docs": (
        "playwright.dev",
        "cypress.io",
        "webdriver.io",
        "selenium.dev",
        "appium.io",
    ),
    "ai-testing-tools": (
        "mabl.com",
        "applitools.com",
        "functionize.com",
        "testsigma.com",
        "bugbug.io",
    ),
    "performance-tools": (
        "k6.io",
        "grafana.com",
        "postman.com",
    ),
    "test-management": (
        "testrail.com",
        "katalon.com",
    ),
    "communities": (
        "ministryoftesting.com",
        "testguild.com",
        "stickyminds.com",
        "infoq.com",
    ),
    "tutorials": (
        "guru99.com",
        "softwaretestinghelp.com",
        "testautomationu.applitools.com",
    ),
    "tech-news": (
        "dzone.com",
        "thenewstack.io",
    ),
    "newsletters": ("qualitybits.substack.com",),
}


# ---------------------------------------------------------------------------
# Topic colors for the landing page chips (kept distinct from AI-research)
# ---------------------------------------------------------------------------

_TOPIC_COLORS: dict[str, str] = {
    "test-automation": "#2563eb",
    "manual-testing": "#7c3aed",
    "ai-in-testing": "#0891b2",
    "performance-testing": "#059669",
    "api-testing": "#d97706",
    "mobile-testing": "#dc2626",
    "accessibility-testing": "#db2777",
    "security-testing": "#4f46e5",
    "visual-regression": "#0d9488",
    "test-data-management": "#ea580c",
    "chaos-engineering": "#9333ea",
    "testops-cicd": "#0284c7",
    "bdd-tdd": "#65a30d",
    "quality-engineering": "#be123c",
    "test-reporting": "#475569",
    "qa-conferences": "#a16207",
}


# ---------------------------------------------------------------------------
# Research prompt
# ---------------------------------------------------------------------------

_TESTING_RESEARCH_PROMPT = """\
You are a deep research assistant focused on **software testing and quality engineering**. \
Your task is to search the internet for the latest articles, news, framework releases, \
and research papers on testing topics, then deeply read each one and extract the most \
important, actionable insights for QA engineers, SDETs, manual testers, and test architects.

## Instructions

For the topic below, find 5-8 recent articles ({date_hint}). For EACH article:

1. **Search** for recent, high-quality articles (blog posts, framework changelogs, conference talks, research papers, vendor announcements, ISTQB syllabi)
2. **Deep-read** each article — do not just paraphrase the title
3. **Extract** 3-5 KEY INSIGHTS that are actionable and specific (e.g., new feature, benchmark number, technique, tool comparison) — never generic ("write good tests")
4. **Write** a comprehensive summary focusing on what's most useful for testing practitioners

## Output Format

Return EXACTLY this JSON array (no markdown, no explanation, ONLY the JSON):

```json
[
  {{
    "id": "sourcename-YYYY-MM-DD",
    "title": "Article Title",
    "source_url": "https://...",
    "source_name": "Source Name",
    "published_date": "YYYY-MM-DD",
    "topic": "TOPIC_KEY",
    "key_insights": [
      "First key insight with specific data, technique, or tool name",
      "Second key insight",
      "Third key insight"
    ],
    "summary": "Detailed 3-5 paragraph summary focusing on actionable content..."
  }}
]
```

## Rules
- `id` format: lowercase source name (no spaces, use hyphens) + date, e.g., `playwright-2026-03-15`
- `published_date`: use YYYY-MM-DD format. If unsure, use the year and month with day 01
- `topic`: use the TOPIC_KEY provided below
- `key_insights`: 3-5 bullets, each a specific actionable insight (cite versions, tool names, percentages, ISTQB chapter numbers)
- `summary`: 3-5 paragraphs, deeply covering the most important and useful parts
- Prefer articles with: tool benchmarks, framework comparisons, real bug stories, ISTQB updates, vendor changelogs, conference talks, case studies
- Skip listicles ("10 best testing tools") and surface-level marketing posts
- Prioritize technical depth over breadth

{source_instruction}

## Topic to Research

TOPIC_KEY: {topic_key}
SEARCH_QUERY: {search_query}

## Existing Article IDs (skip these — already in our knowledge base)

{existing_ids}
"""


# ---------------------------------------------------------------------------
# Index persistence
# ---------------------------------------------------------------------------


def _get_testing_research_dir() -> Path:
    """Find skillnir's own .data/testing-research/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / "testing-research"
        if candidate.parent.is_dir():
            candidate.mkdir(parents=True, exist_ok=True)
            (candidate / "articles").mkdir(exist_ok=True)
            return candidate
        current = current.parent
    fallback = Path.cwd() / ".data" / "testing-research"
    fallback.mkdir(parents=True, exist_ok=True)
    (fallback / "articles").mkdir(exist_ok=True)
    return fallback


def _load_index(research_dir: Path) -> dict[str, Article]:
    """Load existing testing-research-index.json for dedup."""
    index_file = research_dir / "testing-research-index.json"
    if not index_file.exists():
        return {}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        return {item["id"]: Article(**item) for item in data}
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(research_dir: Path, articles: dict[str, Article]) -> None:
    """Persist article registry."""
    index_file = research_dir / "testing-research-index.json"
    data = [
        asdict(a)
        for a in sorted(articles.values(), key=lambda a: a.published_date, reverse=True)
    ]
    index_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Article writers (markdown + HTML)
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load an HTML template from the resources directory."""
    template_path = Path(__file__).parent / "resources" / name
    return template_path.read_text(encoding="utf-8")


def _write_article_md(article: Article, articles_dir: Path) -> Path:
    """Write individual article summary as markdown + HTML sibling."""
    topic_dir = articles_dir / article.topic
    topic_dir.mkdir(exist_ok=True)
    md_path = topic_dir / f"{article.id}.md"
    insights = "\n".join(
        f"{i + 1}. {ins}" for i, ins in enumerate(article.key_insights)
    )

    content = f"""\
---
id: {article.id}
title: "{article.title}"
source: {article.source_url}
source_name: {article.source_name}
published: {article.published_date}
topic: {article.topic}
---

# {article.title}

**Source**: [{article.source_name}]({article.source_url}) | **Published**: {article.published_date} | **Topic**: {TOPIC_LABELS.get(article.topic, article.topic)}

## Key Insights

{insights}

## Summary

{article.summary}
"""
    md_path.write_text(content, encoding="utf-8")
    _write_article_html(article, articles_dir)
    return md_path


def _generate_article_html(article: Article) -> str:
    """Render a single-article HTML page using the shared template."""
    title = html.escape(article.title)
    source_name = html.escape(article.source_name)
    source_url = html.escape(article.source_url, quote=True)
    topic_label = html.escape(TOPIC_LABELS.get(article.topic, article.topic))

    insights_html = "\n".join(
        f"        <li>{html.escape(ins)}</li>" for ins in article.key_insights
    )
    summary_html = "\n".join(
        f"      <p>{html.escape(p.strip())}</p>"
        for p in article.summary.split("\n\n")
        if p.strip()
    )

    template = _load_template("article.html")
    return (
        template.replace("<!-- TITLE -->", title)
        .replace("<!-- SOURCE_URL -->", source_url)
        .replace("<!-- SOURCE_NAME -->", source_name)
        .replace("<!-- PUBLISHED_DATE -->", article.published_date)
        .replace("<!-- TOPIC_LABEL -->", topic_label)
        .replace("<!-- INSIGHTS_HTML -->", insights_html)
        .replace("<!-- SUMMARY_HTML -->", summary_html)
    )


def _write_article_html(article: Article, articles_dir: Path) -> Path:
    """Write individual article as styled HTML page."""
    topic_dir = articles_dir / article.topic
    topic_dir.mkdir(exist_ok=True)
    html_path = topic_dir / f"{article.id}.html"
    html_path.write_text(_generate_article_html(article), encoding="utf-8")
    return html_path


# ---------------------------------------------------------------------------
# Landing page builder
# ---------------------------------------------------------------------------


def _generate_landing_html(
    articles: dict[str, Article],
    research_dir: Path,
    new_ids: set[str] | None = None,
) -> Path:
    """Generate index.html landing page sorted by date."""
    sorted_articles = sorted(
        articles.values(), key=lambda a: a.published_date, reverse=True
    )
    new_ids = new_ids or set()

    rows = []
    for a in sorted_articles:
        color = _TOPIC_COLORS.get(a.topic, "#6b7280")
        badge = (
            '<span style="background:#22c55e;color:#fff;padding:2px 8px;border-radius:4px;font-size:11px;margin-left:8px;">NEW</span>'
            if a.id in new_ids
            else ""
        )
        title_escaped = html.escape(a.title)
        source_escaped = html.escape(a.source_name)
        source_attr = html.escape(a.source_name, quote=True)
        insights_preview = html.escape(a.key_insights[0]) if a.key_insights else ""
        rows.append(f"""\
        <tr onclick="window.open('articles/{a.topic}/{a.id}.html','_blank')" style="cursor:pointer;" class="row" data-topic="{a.topic}" data-source="{source_attr}">
          <td style="padding:12px 16px;">
            <div style="font-weight:600;color:#e2e8f0;">{title_escaped}{badge}</div>
            <div style="font-size:13px;color:#94a3b8;margin-top:4px;">{insights_preview}</div>
          </td>
          <td style="padding:12px 16px;color:#94a3b8;white-space:nowrap;">{source_escaped}</td>
          <td style="padding:12px 16px;white-space:nowrap;">
            <span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;">{TOPIC_LABELS.get(a.topic, a.topic)}</span>
          </td>
          <td style="padding:12px 16px;color:#94a3b8;font-family:monospace;font-size:13px;white-space:nowrap;">{a.published_date}</td>
        </tr>""")

    rows_html = "\n".join(rows)
    topic_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    for a in sorted_articles:
        topic_counts[a.topic] = topic_counts.get(a.topic, 0) + 1
        source_counts[a.source_name] = source_counts.get(a.source_name, 0) + 1

    all_chip = (
        f'<span class="chip topic-chip active" data-filter="all" '
        f"onclick=\"toggleTopic('all')\" "
        f'style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f"All Topics: {len(sorted_articles)}</span>"
    )
    topic_chips = " ".join(
        f'<span class="chip topic-chip" data-filter="{t}" '
        f"onclick=\"toggleTopic('{t}')\" "
        f'style="background:{_TOPIC_COLORS.get(t, "#6b7280")};color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;opacity:0.7;">'
        f"{TOPIC_LABELS.get(t, t)}: {c}</span>"
        for t, c in sorted(topic_counts.items(), key=lambda x: -x[1])
    )
    stats_chips = all_chip + " " + topic_chips

    all_source_chip = (
        f'<span class="chip source-chip active" data-filter="all" '
        f"onclick=\"toggleSource('all')\" "
        f'style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">'
        f"All Sources: {len(sorted_articles)}</span>"
    )
    source_chips = " ".join(
        f'<span class="chip source-chip" data-filter="{html.escape(s, quote=True)}" '
        f'onclick="toggleSource(this.dataset.filter)" '
        f'style="background:#64748b;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;opacity:0.7;">'
        f"{html.escape(s)}: {c}</span>"
        for s, c in sorted(source_counts.items(), key=lambda x: -x[1])
    )
    source_chips_html = all_source_chip + " " + source_chips

    from datetime import datetime

    total = len(sorted_articles)
    last_updated = sorted_articles[0].published_date if sorted_articles else "N/A"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = (
        f"{total} testing articles | Last updated: {last_updated}"
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

    index_path = research_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


# ---------------------------------------------------------------------------
# AI response parser (same as researcher.py — duplicated for module isolation)
# ---------------------------------------------------------------------------


def _parse_articles_json(text: str, topic_key: str) -> list[Article]:
    """Parse JSON array of articles from AI response text."""
    articles: list[Article] = []

    code_blocks = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    for block in code_blocks:
        articles.extend(_try_parse_json_array(block, topic_key))
        if articles:
            return articles

    all_arrays = re.findall(
        r"\[\s*\{[^[\]]*\"id\"[^[\]]*\"title\"[\s\S]*?\}\s*\]", text
    )
    for arr in reversed(all_arrays):
        articles.extend(_try_parse_json_array(arr, topic_key))
        if articles:
            return articles

    obj_pattern = r'\{\s*"id"\s*:\s*"[^"]+"\s*,\s*"title"\s*:\s*"[^"]+"[\s\S]*?\}'
    for obj_match in re.finditer(obj_pattern, text):
        try:
            item = json.loads(obj_match.group())
            article = _dict_to_article(item, topic_key)
            if article:
                articles.append(article)
        except json.JSONDecodeError:
            continue

    return articles


def _try_parse_json_array(text: str, topic_key: str) -> list[Article]:
    """Try to parse a JSON array string into articles."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    articles = []
    for item in data:
        article = _dict_to_article(item, topic_key)
        if article:
            articles.append(article)
    return articles


def _dict_to_article(item: dict, topic_key: str) -> Article | None:
    """Convert a dict to an Article, returning None if invalid."""
    if not isinstance(item, dict):
        return None
    try:
        article = Article(
            id=str(item.get("id", "")).strip(),
            title=str(item.get("title", "")).strip(),
            source_url=str(item.get("source_url", "")).strip(),
            source_name=str(item.get("source_name", "")).strip(),
            published_date=str(item.get("published_date", "")).strip(),
            topic=topic_key,
            key_insights=[str(i) for i in item.get("key_insights", [])],
            summary=str(item.get("summary", "")).strip(),
        )
        if article.id and article.title and article.source_url:
            return article
    except KeyError, TypeError, ValueError:
        pass
    return None


# ---------------------------------------------------------------------------
# Subprocess search (per-topic)
# ---------------------------------------------------------------------------


def _research_topic_subprocess(
    topic_key: str,
    search_query: str,
    existing_ids: set[str],
    backend: AIBackend,
    model: str,
    sources: list[str] | None = None,
    on_progress: Callable[[GenerationProgress], None] | None = None,
    date_range: str | None = None,
) -> list[Article]:
    """Search and summarize articles for a single testing topic via subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"

    if sources:
        focused_domains: list[str] = []
        for key in sources:
            focused_domains.extend(SOURCE_DOMAINS.get(key, ()))
        sources_list = "\n".join(f"- {d}" for d in focused_domains)
        source_instruction = (
            "## Source Filter (search these sources)\n\n"
            "**IMPORTANT**: Focus your search on articles from these specific sources. "
            "Most or all of your articles should come from these domains:\n\n"
            f"{sources_list}"
        )
    else:
        sources_list = "\n".join(f"- {s}" for s in PREFERRED_SOURCES)
        source_instruction = (
            "## Preferred Sources (prioritize these)\n\n"
            "When searching, prioritize articles from these high-quality testing / QA sources. "
            "You are NOT limited to these — still include excellent articles from other sources — "
            "but actively check these first:\n\n"
            f"{sources_list}\n\n"
            "At least 2-3 of your articles should come from these preferred sources when relevant content exists."
        )

    if date_range:
        date_hint = f"{date_range} — strictly exclude older articles"
    else:
        date_hint = "2025-2026 preferred"

    prompt = _TESTING_RESEARCH_PROMPT.format(
        topic_key=topic_key,
        search_query=search_query,
        existing_ids=existing_ids_str,
        source_instruction=source_instruction,
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
        _emit(on_progress, "error", f"{info.name} timed out for topic {topic_key}")
        return []
    except FileNotFoundError:
        _emit(on_progress, "error", f"{info.cli_command} CLI not found in PATH")
        return []
    except Exception as exc:
        _emit(on_progress, "error", f"  [EXCEPTION] {type(exc).__name__}: {exc}")
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

    articles = _parse_articles_json(full_text, topic_key)
    if not articles:
        _emit(
            on_progress,
            "status",
            f"  [RESULT] No parseable articles in {len(full_text)} chars for {topic_key}",
        )
        research_dir = _get_testing_research_dir()
        debug_file = research_dir / f"_debug_{topic_key}.txt"
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
            f"  [RESULT] Parsed {len(articles)} articles for {topic_key}",
        )
    return articles


# ---------------------------------------------------------------------------
# HTML backfill + landing regeneration
# ---------------------------------------------------------------------------


def backfill_article_html(research_dir: Path | None = None) -> int:
    """Generate HTML pages for articles that only have .md files."""
    if research_dir is None:
        research_dir = _get_testing_research_dir()
    articles = _load_index(research_dir)
    articles_dir = research_dir / "articles"
    count = 0
    for article in articles.values():
        topic_dir = articles_dir / article.topic
        html_path = topic_dir / f"{article.id}.html"
        md_path = topic_dir / f"{article.id}.md"
        if md_path.exists() and not html_path.exists():
            _write_article_html(article, articles_dir)
            count += 1
    return count


def regenerate_landing(
    research_dir: Path | None = None,
) -> tuple[int, Path | None]:
    """Backfill HTML + regenerate the landing page."""
    if research_dir is None:
        research_dir = _get_testing_research_dir()
    articles = _load_index(research_dir)
    if not articles:
        return 0, None
    count = backfill_article_html(research_dir)
    index_path = _generate_landing_html(articles, research_dir)
    return count, index_path


# ---------------------------------------------------------------------------
# Main pipeline entry point
# ---------------------------------------------------------------------------


async def testing_research(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    topics: list[str] | None = None,
    sources: list[str] | None = None,
    date_range: str | None = None,
) -> TestingResearchResult:
    """Search the web for each testing topic, summarize with AI, generate landing page."""
    _emit(on_progress, "phase", "Initializing testing-research pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    if not shutil.which(info.cli_command):
        return TestingResearchResult(
            success=False,
            error=(
                f"{info.cli_command} CLI not found in PATH. Install it or switch AI tools."
            ),
        )

    research_dir = _get_testing_research_dir()
    articles_dir = research_dir / "articles"
    articles_dir.mkdir(exist_ok=True)

    existing = _load_index(research_dir)
    existing_ids = set(existing.keys())
    _emit(
        on_progress,
        "status",
        f"Loaded {len(existing)} existing testing articles for dedup",
    )

    topic_keys = list(TOPIC_LABELS.keys())
    search_queries = list(RESEARCH_TOPICS)

    if topics:
        filtered_keys = []
        filtered_queries = []
        for i, key in enumerate(topic_keys):
            if key in topics:
                filtered_keys.append(key)
                filtered_queries.append(search_queries[i])
        topic_keys = filtered_keys
        search_queries = filtered_queries

    total_new = 0
    total_found = 0
    new_ids: set[str] = set()

    for i, (topic_key, search_query) in enumerate(zip(topic_keys, search_queries)):
        label = TOPIC_LABELS.get(topic_key, topic_key)
        _emit(
            on_progress,
            "phase",
            f"[{i + 1}/{len(topic_keys)}] Researching: {label}",
        )

        loop = asyncio.get_event_loop()
        articles = await loop.run_in_executor(
            None,
            _research_topic_subprocess,
            topic_key,
            search_query,
            existing_ids,
            backend,
            model,
            sources,
            on_progress,
            date_range,
        )

        for article in articles:
            total_found += 1
            if article.id in existing_ids:
                _emit(on_progress, "status", f"  Skipped (duplicate): {article.id}")
                continue

            _write_article_md(article, articles_dir)
            existing[article.id] = article
            existing_ids.add(article.id)
            new_ids.add(article.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {article.title}")

    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(research_dir, existing)
    backfill_article_html(research_dir)
    index_path = _generate_landing_html(existing, research_dir, new_ids)

    _emit(on_progress, "phase", "Testing-research complete.")

    return TestingResearchResult(
        success=True,
        articles_found=total_found,
        articles_new=total_new,
        articles_skipped=total_found - total_new,
        index_path=index_path,
    )
