#!/usr/bin/env python3
"""
Dump changed strings side by side (source + every language) for a human or sub-agent content read.

Usage (repo root):
    dump_side_by_side.py --base origin/main --head pr-123 > /tmp/side_by_side.txt
    dump_side_by_side.py --base origin/main --head pr-123 --langs de,fr,pl --rewritten-only
    dump_side_by_side.py --base origin/main --head pr-123 --grep 'clinic|centre'

Groups catalogs that share a source file (e.g. i18n/en.json + i18n/*.json, or every
locale/<lang>/LC_MESSAGES/django.po of one app) and prints, per changed key:
    == key
      en: source text
      de: translation            (was: previous value, when rewritten)
Reuses the parsers in check_catalogs.py (same folder).
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_catalogs import exists, git, is_catalog, lang_of, parse, read, source_candidates  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", default=None)
    ap.add_argument("--source-lang", default="en")
    ap.add_argument("--langs", help="comma-separated language codes to include (default: all)")
    ap.add_argument("--rewritten-only", action="store_true", help="only keys whose previous value was non-empty")
    ap.add_argument("--grep", help="regex; keep keys whose source or any translation matches")
    a = ap.parse_args()

    base = git("merge-base", a.base, a.head or "HEAD").strip()
    changed = [p for p in git("diff", "--name-only", base, *([a.head] if a.head else [])).split() if is_catalog(p)]
    want = set(a.langs.split(",")) if a.langs else None
    groups: dict[str, list[str]] = defaultdict(list)
    for p in changed:
        lang = lang_of(p)
        if lang in (None, a.source_lang) or (want and lang not in want):
            continue
        src = next((c for c in source_candidates(p, a.source_lang) if exists(a.head, c)), None)
        groups[src or f"(no source) {p}"].append(p)

    pat = re.compile(a.grep, re.I) if a.grep else None
    for src_path, files in sorted(groups.items()):
        src_map = parse(src_path, read(a.head, src_path) or "")[0] if not src_path.startswith("(") else {}
        rows: dict[str, dict[str, tuple[str, str | None]]] = defaultdict(dict)
        for f in sorted(files, key=lambda x: lang_of(x) or ""):
            head = parse(f, read(a.head, f) or "")[0]
            old_text = read(base, f)
            old = parse(f, old_text)[0] if old_text else {}
            for k, v in head.items():
                was = old.get(k)
                if v == was or not v:
                    continue
                if a.rewritten_only and not was:
                    continue
                rows[k][lang_of(f)] = (v, was)
        if not rows:
            continue
        print(f"\n######## {src_path}  ({len(rows)} changed keys, {len(files)} languages)")
        for k in sorted(rows):
            src = src_map.get(k) or src_map.get(re.sub(r"\[\w+\]$", "", k)) or ""
            texts = [src] + [v for v, _ in rows[k].values()]
            if pat and not any(pat.search(t or "") for t in texts + [k]):
                continue
            print(f"\n== {k.replace(chr(4), ' | ')}\n  {a.source_lang}: {src}")
            for lang, (v, was) in sorted(rows[k].items()):
                print(f"  {lang}: {v}" + (f"\n      (was: {was})" if was else ""))


if __name__ == "__main__":
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head/less
    main()
