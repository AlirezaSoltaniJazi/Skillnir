"""AI research pipeline: search web, deep-read articles, summarize, generate landing page."""

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
class Article:
    """A single research article with deep summary."""

    id: str  # sourcename-YYYY-MM-DD (dedup key)
    title: str
    source_url: str
    source_name: str
    published_date: str  # YYYY-MM-DD
    topic: str  # prompt-engineering, mcp, rag, etc.
    key_insights: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class ResearchResult:
    """Result of a research pipeline run."""

    success: bool
    articles_found: int = 0
    articles_new: int = 0
    articles_skipped: int = 0
    index_path: Path | None = None
    error: str | None = None


# ---------------------------------------------------------------------------
# Topics
# ---------------------------------------------------------------------------

RESEARCH_TOPICS: tuple[str, ...] = (
    "prompt engineering AI coding best practices 2025 2026",
    "AI agent skills SKILL.md agentskills specification",
    "MCP model context protocol servers best practices",
    "RAG retrieval augmented generation context engineering 2025 2026",
    "AI coding rules cursorrules CLAUDE.md copilot-instructions",
    "multi-agent sub-agent orchestration Claude Agent SDK",
    "context engineering replacing prompt engineering",
    "AI developer productivity research METR study",
    "AI agent memory systems cross-session learning",
    "AI generated code security vulnerabilities OWASP",
    "LLM fine-tuning LoRA QLoRA instruction tuning 2025 2026",
    "AI agent frameworks tool-use function calling 2025 2026",
    "open source LLM models Llama Mistral Qwen 2025 2026",
    "multimodal AI vision language models GPT-4o Gemini 2025 2026",
    "AI infrastructure MLOps model serving deployment 2025 2026",
)

TOPIC_LABELS: dict[str, str] = {
    "prompt-engineering": "Prompt Engineering",
    "ai-skills": "AI Coding Skills",
    "mcp": "MCP (Model Context Protocol)",
    "rag-context": "RAG & Context Engineering",
    "ai-rules": "AI Coding Rules",
    "multi-agent": "Sub-Agents / Multi-Agent",
    "context-engineering": "Context Engineering",
    "ai-productivity": "AI Developer Productivity",
    "ai-memory": "AI Agent Memory",
    "ai-security": "AI Code Security",
    "fine-tuning": "Fine-Tuning & LoRA",
    "ai-agents-tools": "AI Agent Frameworks & Tools",
    "open-source-models": "Open Source Models",
    "multimodal-ai": "Multimodal AI (Vision, Audio)",
    "ai-infrastructure": "AI Infrastructure & MLOps",
}


# ---------------------------------------------------------------------------
# Preferred sources
# ---------------------------------------------------------------------------

PREFERRED_SOURCES: tuple[str, ...] = (
    "medium.com",
    "towardsdatascience.com",
    "arxiv.org",
    "news.ycombinator.com",
    "substack.com",
    "dev.to",
    "hashnode.com",
    "anthropic.com",
    "openai.com",
    "ai.googleblog.com",
    "research.microsoft.com",
    "ai.meta.com",
    "simonwillison.net",
    "huyenchip.com",
    "karpathy.ai",
    "a16z.com",
    "thegradient.pub",
    "lilianweng.github.io",
    "technologyreview.com",
    "spectrum.ieee.org",
    "github.blog",
    "huggingface.co",
    "deeplearning.ai",
    "blog.langchain.dev",
    "www.llamaindex.ai",
    "wandb.ai",
    "deepmind.google",
    "paperswithcode.com",
    "techcrunch.com",
    "theverge.com",
    "venturebeat.com",
    "thenewstack.io",
    "newsletter.theaiedge.io",
    "read.deeplearning.ai",
)


# ---------------------------------------------------------------------------
# Source filters
# ---------------------------------------------------------------------------

SOURCE_FILTERS: dict[str, str] = {
    "medium": "Medium (medium.com, towardsdatascience.com)",
    "arxiv": "arXiv (arxiv.org)",
    "hackernews": "Hacker News (news.ycombinator.com)",
    "substack": "Substack (substack.com)",
    "vendor-blogs": "Vendor Blogs (Anthropic, OpenAI, Google, Meta, Microsoft)",
    "research-labs": "Research Labs (DeepMind, Hugging Face, Papers with Code)",
    "ai-frameworks": "AI Frameworks (LangChain, LlamaIndex, Weights & Biases)",
    "dev-community": "Dev Community (dev.to, hashnode.com)",
    "tech-news": "Tech News (TechCrunch, The Verge, VentureBeat)",
    "newsletters": "AI Newsletters (The Batch, TLDR AI, The AI Edge)",
}

SOURCE_DOMAINS: dict[str, tuple[str, ...]] = {
    "medium": ("medium.com", "towardsdatascience.com"),
    "arxiv": ("arxiv.org",),
    "hackernews": ("news.ycombinator.com",),
    "substack": ("substack.com",),
    "vendor-blogs": (
        "anthropic.com",
        "openai.com",
        "ai.googleblog.com",
        "ai.meta.com",
        "research.microsoft.com",
    ),
    "research-labs": (
        "deepmind.google",
        "huggingface.co",
        "paperswithcode.com",
        "deeplearning.ai",
    ),
    "ai-frameworks": (
        "blog.langchain.dev",
        "www.llamaindex.ai",
        "wandb.ai",
    ),
    "dev-community": (
        "dev.to",
        "hashnode.com",
    ),
    "tech-news": (
        "techcrunch.com",
        "theverge.com",
        "venturebeat.com",
        "thenewstack.io",
    ),
    "newsletters": (
        "newsletter.theaiedge.io",
        "read.deeplearning.ai",
    ),
}


# ---------------------------------------------------------------------------
# Research prompt (skill-based with inline fallback)
# ---------------------------------------------------------------------------


def _load_research_skill() -> str | None:
    """Load the deepResearcher skill's SKILL.md as the research prompt.

    Returns the skill content (minus YAML frontmatter) or None if not found.
    """
    current = Path(__file__).resolve().parent
    for _ in range(5):
        skill_path = current / ".data" / "skills" / "deepResearcher" / "SKILL.md"
        if skill_path.exists():
            text = skill_path.read_text(encoding="utf-8")
            # Strip YAML frontmatter (between --- markers)
            if text.startswith("---"):
                end = text.find("---", 3)
                if end != -1:
                    text = text[end + 3 :].strip()
            return text
        current = current.parent
    return None


_RESEARCH_PROMPT = """\
You are a deep research assistant. Your task is to search the internet for the latest articles, \
news, and research papers on AI engineering topics, then deeply read each one and extract the most \
important, actionable insights.

## Instructions

For the topic below, find 5-8 recent articles ({date_hint}). For EACH article:

1. **Search** for recent, high-quality articles (blog posts, research papers, official docs, conference talks)
2. **Deep-read** each article — do not just summarize the title
3. **Extract** 3-5 KEY INSIGHTS that are actionable and specific (not generic advice)
4. **Write** a comprehensive summary focusing on what's most useful for AI tool builders and developers

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
      "First key insight with specific data or technique",
      "Second key insight",
      "Third key insight"
    ],
    "summary": "Detailed 3-5 paragraph summary focusing on actionable content..."
  }}
]
```

## Rules
- `id` format: lowercase source name (no spaces, use hyphens) + date, e.g., `metr-2025-07-10`
- `published_date`: use YYYY-MM-DD format. If unsure, use the year and month with day 01
- `topic`: use the TOPIC_KEY provided below
- `key_insights`: 3-5 bullets, each a specific actionable insight (not vague summaries)
- `summary`: 3-5 paragraphs, deeply covering the most important and useful parts
- Prefer articles with data, benchmarks, case studies, or concrete techniques
- Skip listicles and surface-level blog posts

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


def _get_research_dir() -> Path:
    """Find skillnir's own .data/research/ directory."""
    current = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = current / ".data" / "research"
        if candidate.parent.is_dir():
            candidate.mkdir(parents=True, exist_ok=True)
            (candidate / "articles").mkdir(exist_ok=True)
            return candidate
        current = current.parent
    fallback = Path.cwd() / ".data" / "research"
    fallback.mkdir(parents=True, exist_ok=True)
    (fallback / "articles").mkdir(exist_ok=True)
    return fallback


def _load_index(research_dir: Path) -> dict[str, Article]:
    """Load existing research-index.json for dedup."""
    index_file = research_dir / "research-index.json"
    if not index_file.exists():
        return {}
    try:
        data = json.loads(index_file.read_text(encoding="utf-8"))
        return {item["id"]: Article(**item) for item in data}
    except json.JSONDecodeError, KeyError, TypeError:
        return {}


def _save_index(research_dir: Path, articles: dict[str, Article]) -> None:
    """Persist article registry."""
    index_file = research_dir / "research-index.json"
    data = [
        asdict(a)
        for a in sorted(articles.values(), key=lambda a: a.published_date, reverse=True)
    ]
    index_file.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Migration: flat articles → topic subdirectories
# ---------------------------------------------------------------------------


def _migrate_articles_to_topic_dirs(research_dir: Path) -> int:
    """Move articles from flat articles/ into articles/{topic}/ subdirectories.

    Handles both indexed articles and orphan files (by reading frontmatter).
    Returns the number of files moved.
    """
    articles_dir = research_dir / "articles"
    if not articles_dir.is_dir():
        return 0

    # Build id→topic map from index
    articles = _load_index(research_dir)
    id_to_topic: dict[str, str] = {a.id: a.topic for a in articles.values()}

    # Collect flat .md files to discover orphan topics via frontmatter
    valid_topics = set(TOPIC_LABELS.keys())
    for md_file in articles_dir.glob("*.md"):
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
    for article_id, topic in id_to_topic.items():
        topic_dir = articles_dir / topic
        for ext in (".md", ".html"):
            old_path = articles_dir / f"{article_id}{ext}"
            new_path = topic_dir / f"{article_id}{ext}"
            if old_path.exists() and not new_path.exists():
                topic_dir.mkdir(exist_ok=True)
                old_path.rename(new_path)
                moved += 1
    return moved


# ---------------------------------------------------------------------------
# Article MD writer
# ---------------------------------------------------------------------------


def _write_article_md(article: Article, articles_dir: Path) -> Path:
    """Write individual article summary as markdown."""
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


# ---------------------------------------------------------------------------
# Article HTML page generator
# ---------------------------------------------------------------------------


def _load_template(name: str) -> str:
    """Load an HTML template from the resources directory."""
    template_path = Path(__file__).parent / 'resources' / name
    return template_path.read_text(encoding='utf-8')


def _generate_article_html(article: Article) -> str:
    """Generate a self-contained styled HTML page for a single article."""
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

    template = _load_template('article.html')
    return (
        template.replace('<!-- TITLE -->', title)
        .replace('<!-- SOURCE_URL -->', source_url)
        .replace('<!-- SOURCE_NAME -->', source_name)
        .replace('<!-- PUBLISHED_DATE -->', article.published_date)
        .replace('<!-- TOPIC_LABEL -->', topic_label)
        .replace('<!-- INSIGHTS_HTML -->', insights_html)
        .replace('<!-- SUMMARY_HTML -->', summary_html)
    )


def _write_article_html(article: Article, articles_dir: Path) -> Path:
    """Write individual article as styled HTML page."""
    topic_dir = articles_dir / article.topic
    topic_dir.mkdir(exist_ok=True)
    html_path = topic_dir / f"{article.id}.html"
    html_path.write_text(_generate_article_html(article), encoding="utf-8")
    return html_path


# ---------------------------------------------------------------------------
# Landing page HTML generator
# ---------------------------------------------------------------------------


def _generate_landing_html(
    articles: dict[str, Article], research_dir: Path, new_ids: set[str] | None = None
) -> Path:
    """Generate index.html landing page sorted by date."""
    sorted_articles = sorted(
        articles.values(), key=lambda a: a.published_date, reverse=True
    )
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
        "fine-tuning": "#a855f7",
        "ai-agents-tools": "#0ea5e9",
        "open-source-models": "#84cc16",
        "multimodal-ai": "#e11d48",
        "ai-infrastructure": "#64748b",
    }

    rows = []
    for a in sorted_articles:
        color = topic_colors.get(a.topic, "#6b7280")
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

    # Topic chips
    all_chip = f'<span class="chip topic-chip active" data-filter="all" onclick="toggleTopic(\'all\')" style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">All Topics: {len(sorted_articles)}</span>'
    topic_chips = " ".join(
        f'<span class="chip topic-chip" data-filter="{t}" onclick="toggleTopic(\'{t}\')" style="background:{topic_colors.get(t, "#6b7280")};color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;opacity:0.7;">{TOPIC_LABELS.get(t, t)}: {c}</span>'
        for t, c in sorted(topic_counts.items(), key=lambda x: -x[1])
    )
    stats_chips = all_chip + " " + topic_chips

    # Source chips
    all_source_chip = f'<span class="chip source-chip active" data-filter="all" onclick="toggleSource(\'all\')" style="background:#475569;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;">All Sources: {len(sorted_articles)}</span>'
    source_chips = " ".join(
        f'<span class="chip source-chip" data-filter="{html.escape(s, quote=True)}" onclick="toggleSource(this.dataset.filter)" style="background:#64748b;color:#fff;padding:4px 12px;border-radius:16px;font-size:12px;cursor:pointer;opacity:0.7;">{html.escape(s)}: {c}</span>'
        for s, c in sorted(source_counts.items(), key=lambda x: -x[1])
    )
    source_chips_html = all_source_chip + " " + source_chips

    from datetime import datetime

    total = len(sorted_articles)
    last_updated = sorted_articles[0].published_date if sorted_articles else "N/A"
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    subtitle = (
        f"{total} articles | Last updated: {last_updated}"
        f" | Generated: {generated_at}"
    )

    template = _load_template('landing.html')
    page_html = (
        template.replace('<!-- SUBTITLE -->', subtitle)
        .replace('<!-- TOPIC_CHIPS -->', stats_chips)
        .replace('<!-- SOURCE_CHIPS -->', source_chips_html)
        .replace('<!-- TABLE_ROWS -->', rows_html)
        .replace('<!-- TOTAL_ARTICLES -->', str(total))
    )

    index_path = research_dir / "index.html"
    index_path.write_text(page_html, encoding="utf-8")
    return index_path


# ---------------------------------------------------------------------------
# AI response parser
# ---------------------------------------------------------------------------


def _parse_articles_json(text: str, topic_key: str) -> list[Article]:
    """Parse JSON array of articles from AI response text."""
    articles: list[Article] = []

    # Strategy 1: Find JSON inside ```json ... ``` code blocks
    code_blocks = re.findall(r"```(?:json)?\s*(\[[\s\S]*?\])\s*```", text)
    for block in code_blocks:
        articles.extend(_try_parse_json_array(block, topic_key))
        if articles:
            return articles

    # Strategy 2: Find standalone JSON arrays (greedy last match — the final output)
    # Look for arrays that contain "id" and "title" keys
    all_arrays = re.findall(
        r"\[\s*\{[^[\]]*\"id\"[^[\]]*\"title\"[\s\S]*?\}\s*\]", text
    )
    for arr in reversed(
        all_arrays
    ):  # Try last match first (most likely the final output)
        articles.extend(_try_parse_json_array(arr, topic_key))
        if articles:
            return articles

    # Strategy 3: Find individual JSON objects with article fields
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
# Main pipeline
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
    """Search and summarize articles for a single topic using subprocess."""
    info = BACKENDS[backend]

    existing_ids_str = ", ".join(sorted(existing_ids)) if existing_ids else "(none)"

    # Build source instruction: hard filter when sources selected, soft prioritization otherwise
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
            "When searching, prioritize articles from these high-quality sources. You are NOT limited to "
            "these — still include excellent articles from other sources — but actively check these first:\n\n"
            f"{sources_list}\n\n"
            "At least 2-3 of your articles should come from these preferred sources when relevant content exists."
        )

    # Build date hint for the prompt
    if date_range:
        date_hint = f"{date_range} — strictly exclude older articles"
    else:
        date_hint = "2025-2026 preferred"

    # Try skill-based prompt first, fall back to inline prompt
    skill_prompt = _load_research_skill()
    base_prompt = skill_prompt if skill_prompt else _RESEARCH_PROMPT
    prompt = base_prompt.format(
        topic_key=topic_key,
        search_query=search_query,
        existing_ids=existing_ids_str,
        source_instruction=source_instruction,
        date_hint=date_hint,
    )

    cmd = build_subprocess_command(backend, prompt, model=model, max_turns=10)

    # Override allowed tools to include WebFetch and WebSearch for research
    if backend == AIBackend.CLAUDE:
        try:
            idx = cmd.index("--allowedTools")
            cmd[idx + 1] = "Read,Glob,Grep,Bash,Write,WebFetch,WebSearch"
        except ValueError:
            pass

    # Disable Cursor sandbox so the agent can make outbound web requests
    if backend == AIBackend.CURSOR:
        try:
            sep = cmd.index("--")
            cmd.insert(sep, "disabled")
            cmd.insert(sep, "--sandbox")
        except ValueError:
            cmd.extend(["--sandbox", "disabled"])

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
        stderr_output = ''.join(stderr_chunks)

        _emit(
            on_progress,
            "status",
            f"  [DONE] exit={proc.returncode}, stdout_lines={line_count}, collected_chunks={len(collected_text)}, stderr_len={len(stderr_output)}",
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

    articles = _parse_articles_json(full_text, topic_key)
    if not articles:
        _emit(
            on_progress,
            "status",
            f"  [RESULT] No parseable articles in {len(full_text)} chars for {topic_key}",
        )
        # Save raw output for debugging
        research_dir = _get_research_dir()
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


def backfill_article_html(research_dir: Path | None = None) -> int:
    """Generate HTML pages for articles that only have .md files.

    Returns the number of HTML files created.
    """
    if research_dir is None:
        research_dir = _get_research_dir()
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


def regenerate_landing(research_dir: Path | None = None) -> tuple[int, Path | None]:
    """Backfill HTML article pages and regenerate the landing page.

    Returns (html_files_created, index_path).
    """
    if research_dir is None:
        research_dir = _get_research_dir()
    _migrate_articles_to_topic_dirs(research_dir)
    articles = _load_index(research_dir)
    if not articles:
        return 0, None
    count = backfill_article_html(research_dir)
    index_path = _generate_landing_html(articles, research_dir)
    return count, index_path


async def research(
    on_progress: Callable[[GenerationProgress], None] | None = None,
    backend_override: AIBackend | None = None,
    model_override: str | None = None,
    topics: list[str] | None = None,
    sources: list[str] | None = None,
    date_range: str | None = None,
) -> ResearchResult:
    """Main entry: search web for each topic, summarize with AI, generate landing page."""
    _emit(on_progress, "phase", "Initializing research pipeline...")

    config = load_config()
    backend = backend_override or config.backend
    model = model_override or config.model
    info = BACKENDS[backend]

    # Check CLI availability
    if not shutil.which(info.cli_command):
        return ResearchResult(
            success=False,
            error=f"{info.cli_command} CLI not found in PATH. Install it or switch AI tools.",
        )

    research_dir = _get_research_dir()
    articles_dir = research_dir / "articles"
    articles_dir.mkdir(exist_ok=True)

    # Migrate flat articles into topic subdirectories
    _migrate_articles_to_topic_dirs(research_dir)

    # Load existing index for dedup
    existing = _load_index(research_dir)
    existing_ids = set(existing.keys())
    _emit(on_progress, "status", f"Loaded {len(existing)} existing articles for dedup")

    # Determine which topics to search
    topic_keys = list(TOPIC_LABELS.keys())
    search_queries = list(RESEARCH_TOPICS)

    if topics:
        # Filter to requested topics
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
        _emit(on_progress, "phase", f"[{i + 1}/{len(topic_keys)}] Researching: {label}")

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

            # Write MD file
            _write_article_md(article, articles_dir)
            existing[article.id] = article
            existing_ids.add(article.id)
            new_ids.add(article.id)
            total_new += 1
            _emit(on_progress, "status", f"  New: {article.title}")

    # Save updated index
    _emit(on_progress, "phase", "Saving index and generating landing page...")
    _save_index(research_dir, existing)

    # Backfill HTML pages for any articles that only have .md
    backfill_article_html(research_dir)

    # Generate landing page
    index_path = _generate_landing_html(existing, research_dir, new_ids)

    _emit(on_progress, "phase", "Research complete.")

    return ResearchResult(
        success=True,
        articles_found=total_found,
        articles_new=total_new,
        articles_skipped=total_found - total_new,
        index_path=index_path,
    )
