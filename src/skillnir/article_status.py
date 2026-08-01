"""Shared article-status helpers for the research stores.

Stdlib-only on purpose: the three researcher modules AND article_cleanup.py
import from here, so this module must never import from either side
(prevents circular imports).

Outdated articles keep their index entries (dedup skip-lists stay intact)
while their .md/.html files move to ``articles/<topic>/outdated/``.
"""

import html
from pathlib import Path

STATUS_ACTIVE = "active"
STATUS_OUTDATED = "outdated"

OUTDATED_DIR_NAME = "outdated"


def is_outdated(article) -> bool:
    """True when an Article's status marks it outdated."""
    return getattr(article, "status", STATUS_ACTIVE) == STATUS_OUTDATED


def split_by_status(articles: dict) -> tuple[list, list]:
    """Split an id->Article dict into (active, outdated), newest first."""
    ordered = sorted(articles.values(), key=lambda a: a.published_date, reverse=True)
    active = [a for a in ordered if not is_outdated(a)]
    outdated = [a for a in ordered if is_outdated(a)]
    return active, outdated


def article_dir(articles_dir: Path, topic: str, status: str) -> Path:
    """Directory an article's files belong in, given its status."""
    topic_dir = articles_dir / topic
    if status == STATUS_OUTDATED:
        return topic_dir / OUTDATED_DIR_NAME
    return topic_dir


def build_outdated_section_html(outdated: list, topic_labels: dict[str, str]) -> str:
    """Render the collapsible "Outdated" landing-page section.

    Rows use class ``outdated-row`` (never ``row``) and live in their own
    table, so the landing page's filter/sort JavaScript — which targets
    ``tr.row`` and the first ``tbody`` — ignores them entirely.
    """
    if not outdated:
        return ""

    rows = []
    for a in outdated:
        title_escaped = html.escape(a.title)
        topic_label = html.escape(topic_labels.get(a.topic, a.topic))
        reason = html.escape(getattr(a, "outdated_reason", ""))
        marked_at = html.escape(getattr(a, "outdated_at", ""))
        rows.append(f"""\
        <tr onclick="window.open('articles/{a.topic}/{OUTDATED_DIR_NAME}/{a.id}.html','_blank')" style="cursor:pointer;opacity:0.75;" class="outdated-row">
          <td style="padding:10px 16px;">
            <div style="font-weight:600;color:#94a3b8;">{title_escaped}</div>
            <div style="font-size:12px;color:#64748b;margin-top:4px;">{reason}</div>
          </td>
          <td style="padding:10px 16px;white-space:nowrap;">
            <span style="background:#475569;color:#cbd5e1;padding:2px 10px;border-radius:12px;font-size:12px;">{topic_label}</span>
          </td>
          <td style="padding:10px 16px;color:#64748b;font-family:monospace;font-size:13px;white-space:nowrap;">{a.published_date}</td>
          <td style="padding:10px 16px;color:#64748b;font-family:monospace;font-size:13px;white-space:nowrap;">{marked_at}</td>
        </tr>""")
    rows_html = "\n".join(rows)

    return f"""\
    <details class="outdated-section" style="margin-top:32px;">
      <summary style="cursor:pointer;color:#94a3b8;font-size:15px;font-weight:600;padding:8px 0;">
        Outdated articles ({len(outdated)}) — content superseded or invalidated; kept for reference
      </summary>
      <table style="width:100%;border-collapse:collapse;margin-top:12px;">
        <thead>
          <tr style="text-align:left;color:#64748b;font-size:12px;text-transform:uppercase;">
            <th style="padding:8px 16px;">Article / reason</th>
            <th style="padding:8px 16px;">Topic</th>
            <th style="padding:8px 16px;">Published</th>
            <th style="padding:8px 16px;">Marked outdated</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>
    </details>"""
