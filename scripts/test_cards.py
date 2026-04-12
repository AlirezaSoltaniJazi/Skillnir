#!/usr/bin/env python3
"""Send sample Google Chat cards locally to test card layout.

Reads existing local index data and posts one (or more) items per feature
to the webhook in AI_AGENT_WEBHOOK_URL. No AI calls, no Cursor needed —
just reads the index files and sends.

Usage:
    python scripts/test_cards.py          # 1 item per feature
    python scripts/test_cards.py 3        # 3 items per feature
    python scripts/test_cards.py 5 research  # 5 items, research only
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from run_intel import _extract_fields
from skillnir.notifications.senders import send_gchat_intel_report

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

_FEATURE_INDEX = {
    "research": "research/research-index.json",
    "events": "events/events-index.json",
    "security": "security/security-index.json",
    "benchmarks": "benchmarks/benchmarks-index.json",
}

_FOOTER_URLS: dict[str, list[tuple[str, str]]] = {
    "benchmarks": [
        ("Chatbot Arena", "https://arena.ai/leaderboard/code"),
        ("Artificial Analysis", "https://artificialanalysis.ai/leaderboards/models"),
        ("SWE-bench", "https://www.swebench.com/"),
    ],
}

_FEATURE_LABELS: dict[str, str] = {
    "benchmarks": "benchmarks sorted by coding",
}


def _find_data_dir() -> Path:
    """Locate the .data directory."""
    for candidate in [_PROJECT_ROOT / ".data", Path.cwd() / ".data"]:
        if candidate.is_dir():
            return candidate
    print("ERROR: .data/ directory not found", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    webhook = os.environ.get("AI_AGENT_WEBHOOK_URL", "").strip()
    if not webhook:
        print("ERROR: AI_AGENT_WEBHOOK_URL not set in env", file=sys.stderr)
        return 1

    count = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 1
    only_feature = sys.argv[2] if len(sys.argv) > 2 else None

    if only_feature and only_feature not in _FEATURE_INDEX:
        print(
            f"ERROR: unknown feature '{only_feature}'. "
            f"Choose from: {', '.join(_FEATURE_INDEX)}",
            file=sys.stderr,
        )
        return 1

    data_dir = _find_data_dir()
    features = {only_feature: _FEATURE_INDEX[only_feature]} if only_feature else _FEATURE_INDEX

    for feature, rel_path in features.items():
        index_path = data_dir / rel_path
        if not index_path.exists():
            print(f"[skip] {feature}: no index at {index_path}")
            continue

        items = json.loads(index_path.read_text(encoding="utf-8"))
        if not items:
            print(f"[skip] {feature}: index is empty")
            continue

        sample = items[:count]
        print(f"\n[{feature}] sending {len(sample)} item(s)...")

        cards = []
        for item in sample:
            title, desc, url = _extract_fields(feature, item)
            cards.append((title, desc, url))
            print(f"  title: {title[:80]}")
            print(f"  desc:  {desc[:80]}")
            if url:
                print(f"  url:   {url[:80]}")

        feature_label = _FEATURE_LABELS.get(feature, feature)
        footer = _FOOTER_URLS.get(feature)

        ok, err = send_gchat_intel_report(
            webhook,
            feature=feature_label,
            items=cards,
            footer_urls=footer,
        )
        if ok:
            print("  -> sent OK")
        else:
            print(f"  -> FAILED: {err}")

        time.sleep(2)

    print("\nDone. Check your Google Chat channel.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
