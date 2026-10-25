#!/usr/bin/env python3
"""
Mechanical checks for translation catalogs, in any repo.

Compares every translated string with its source-language string and, with --base, with
its previous value. Formats: JSON (flat or nested; ngx-translate, i18next, vue-i18n, ARB),
gettext .po, Android strings.xml, iOS .strings.

Usage (run from the repo root):
    check_catalogs.py --base origin/main --head HEAD          # files changed between refs
    check_catalogs.py --base origin/main --head pr-123 --all  # also unchanged strings (OLD)
    check_catalogs.py path/to/de.json path/to/fr.json         # working tree, no diff info
    check_catalogs.py ... --source-lang en --keep brandix --keep "FlowKit X" --json

Severity: ERROR (breaks at runtime or shows garbage), WARN (likely wrong), INFO (context).
Tag: NEW (value changed between --base and --head) or OLD (already on base).
Exit code 1 when there is at least one NEW ERROR.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

# ---------------------------------------------------------------- placeholders
PLACEHOLDER = re.compile(
    r"\{\{\s*[^{}]+?\s*\}\}"  # {{ name }}         angular / ngx-translate / handlebars / i18next
    r"|%\([^)]+\)[#0\- +]*\d*(?:\.\d+)?[sdifrxXeEgGc]"  # %(name)s  python
    r"|%\d+\$[#0\- +]*\d*(?:\.\d+)?[sdif@]"  # %1$s         android / printf positional
    r"|%[#0\- +]*\d*(?:\.\d+)?(?:l{0,2}|h)[sdifuxXeEgGc@]"  # %s %d %.2f %@ %lld
    r"|%\{\w+\}"  # %{name}           ruby / custom
    r"|\$\{[^}]+\}"  # ${name}          js template / ICU-like
    r"|\{\s*\w[\w.]*\s*\}"  # {name} {0}      python format / ICU simple arg / .NET
    r"|\{\s*\w+\s*,\s*(?:number|date|time)[^{}]*\}"  # {n, number}  ICU formatted arg
    r"|</?[a-zA-Z][\w-]*(?:\s[^<>]*)?/?>"  # <b> <a href> <br/>  markup (compared by tag name)
)
ICU_COMPLEX = re.compile(r"\{\s*(\w+)\s*,\s*(plural|select|selectordinal)\s*,")
PERCENT_FORMAT = re.compile(r"%\(|%[sdif]")
STRAY_PERCENT = re.compile(r"%(?!%|\([^)]+\)[#0\- +]*\d*(?:\.\d+)?[sdifrxXeEgGc]|\d+\$|[#0\- +]*\d*(?:\.\d+)?(?:l{0,2}|h)[sdifuxXeEgGc@]|\{\w+\})")
NUMBER = re.compile(r"(?<![\d.,])\d{1,3}(?:[.,\u00a0\u202f ’']\d{3})+(?:[.,]\d+)?(?!\d)|(?<![\d.,])\d+(?:[.,]\d+)?(?!\d)")


def _num(n: str) -> str:
    """Normalize '2,500' / '2.500' / '2 500' / '1’234.5' to one canonical value."""
    n = re.sub(r"[\u00a0\u202f ’']", "", n)
    if re.fullmatch(r"\d{1,3}([.,]\d{3})+", n):
        return re.sub(r"[.,]", "", n)  # pure thousands grouping
    m = re.fullmatch(r"(\d{1,3}(?:[.,]\d{3})+)([.,])(\d+)", n)
    if m:
        return re.sub(r"[.,]", "", m.group(1)) + "." + m.group(3)
    return n.replace(",", ".")
URL = re.compile(r"https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+")
WORD = re.compile(r"[^\W\d_]{3,}")

# Languages whose decimal separator is a comma (CLDR); a dot-decimal number there is suspect.
COMMA_DECIMAL = {"de", "it", "nl", "fr", "pt", "es", "fi", "cs", "nb", "no", "nn", "sv", "da", "el", "pl", "ru", "uk", "tr", "ro", "hu", "sk", "sl", "hr", "bg", "lt", "lv", "et", "id", "vi"}
# Sentence-final question mark per language (others use '?').
QUESTION_MARK = {"el": ";", "ar": "؟", "fa": "؟", "ur": "؟"}
# Scripts where letter case does not exist.
NO_CASE = {"ar", "fa", "he", "ur", "zh", "ja", "ko", "th", "hi"}
SOURCE_NAMES = ("en", "en_GB", "en-GB", "en_US", "en-US", "base", "Base", "source")


@dataclass
class Finding:
    severity: str
    check: str
    tag: str
    file: str
    lang: str
    key: str
    source: str
    target: str
    detail: str = ""


# ---------------------------------------------------------------- git helpers
def git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def read(ref: str | None, path: str) -> str | None:
    if ref is None:
        p = Path(path)
        return p.read_text(encoding="utf-8") if p.is_file() else None
    r = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", "replace") if r.returncode == 0 else None


def exists(ref: str | None, path: str) -> bool:
    if ref is None:
        return Path(path).is_file()
    return subprocess.run(["git", "cat-file", "-e", f"{ref}:{path}"], capture_output=True).returncode == 0


# ---------------------------------------------------------------- parsers
def _flatten(d: dict, prefix: str = "") -> dict[str, str]:
    out: dict[str, str] = {}
    for k, v in d.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(_flatten(v, key))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                out[f"{key}[{i}]"] = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
        elif isinstance(v, str):
            out[key] = v
    return out


def parse_json(text: str) -> tuple[dict[str, str], list[str]]:
    problems: list[str] = []

    def hook(pairs):
        seen = Counter(k for k, _ in pairs)
        problems.extend(f"duplicate key '{k}' (last value wins)" for k, c in seen.items() if c > 1)
        return dict(pairs)

    try:
        data = json.loads(text, object_pairs_hook=hook)
    except json.JSONDecodeError as e:
        return {}, [f"invalid JSON: {e}"]
    if not text.endswith("\n"):
        problems.append("no newline at end of file")
    flat = _flatten(data) if isinstance(data, dict) else {}
    flat = {k: v for k, v in flat.items() if not k.startswith("@")}  # ARB metadata
    return flat, problems


def _po_unescape(s: str) -> str:
    return s.replace('\\"', '"').replace("\\n", "\n").replace("\\t", "\t").replace("\\\\", "\\")


def parse_po(text: str) -> tuple[dict[str, str], list[str]]:
    """Return {msgctxt|msgid: msgstr} with plural forms as 'msgid[n]'. Skips the header."""
    entries: dict[str, str] = {}
    problems: list[str] = []
    m = re.search(r"nplurals\s*=\s*(\d+)", text)
    nplurals = int(m.group(1)) if m else None
    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        fields: dict[str, str] = {}
        cur = None
        fuzzy = False
        for line in block.splitlines():
            line = line.strip()
            if line.startswith("#,") and "fuzzy" in line:
                fuzzy = True
            if line.startswith("#~"):
                cur = None
                break
            if not line or line.startswith("#"):
                continue
            mm = re.match(r'(msgctxt|msgid_plural|msgid|msgstr(?:\[\d+\])?)\s+"(.*)"$', line)
            if mm:
                cur = mm.group(1)
                fields[cur] = _po_unescape(mm.group(2))
            elif line.startswith('"') and cur:
                fields[cur] += _po_unescape(line[1:-1])
        mid = fields.get("msgid")
        if not mid:
            continue
        key = f"{fields['msgctxt']}\x04{mid}" if "msgctxt" in fields else mid
        if fuzzy:
            problems.append(f"fuzzy entry (ignored by gettext at runtime): {mid[:60]}")
        if "msgid_plural" in fields:
            forms = sorted(k for k in fields if k.startswith("msgstr["))
            if nplurals is not None and len(forms) != nplurals:
                problems.append(f"plural '{mid[:60]}' has {len(forms)} msgstr forms, header says nplurals={nplurals}")
            for f in forms:
                entries[f"{key}{f[6:]}"] = fields[f]
        else:
            entries[key] = fields.get("msgstr", "")
    return entries, problems


def parse_android(text: str) -> tuple[dict[str, str], list[str]]:
    out: dict[str, str] = {}
    problems: list[str] = []
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    for m in re.finditer(r'<string\s+name="([^"]+)"([^>]*?)(?:/>|>(.*?)</string>)', text, re.S):
        if 'translatable="false"' in m.group(2):
            continue
        value = m.group(3) or ""
        if "<string" in value:
            problems.append(f"malformed XML: <string> nested inside '{m.group(1)}'")
        out[m.group(1)] = _android_unescape(value)
    for m in re.finditer(r'<plurals\s+name="([^"]+)"[^>]*>(.*?)</plurals>', text, re.S):
        for q in re.finditer(r'<item\s+quantity="(\w+)"[^>]*?(?:/>|>(.*?)</item>)', m.group(2), re.S):
            out[f"{m.group(1)}[{q.group(1)}]"] = _android_unescape(q.group(2) or "")
    return out, problems


def _android_unescape(v: str) -> str:
    v = re.sub(r"^\s*<!\[CDATA\[(.*)\]\]>\s*$", r"\1", v, flags=re.S)
    v = v.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n").replace("\\@", "@").replace("\\?", "?")
    return v.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&").strip('"')


def parse_strings(text: str) -> tuple[dict[str, str], list[str]]:
    out: dict[str, str] = {}
    for m in re.finditer(r'"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', text):
        out[m.group(1)] = m.group(2).replace('\\"', '"').replace("\\n", "\n")
    return out, []


def parse(path: str, text: str) -> tuple[dict[str, str], list[str]]:
    if path.endswith((".json", ".arb")):
        return parse_json(text)
    if path.endswith(".po"):
        return parse_po(text)
    if path.endswith(".xml"):
        return parse_android(text)
    if path.endswith(".strings"):
        return parse_strings(text)
    return {}, []


# ---------------------------------------------------------------- source discovery
def lang_of(path: str) -> str | None:
    p = Path(path)
    for part in reversed(p.parts):
        m = re.fullmatch(r"values-([a-z]{2,3})(?:-r?[A-Z]{2})?", part)
        if m:
            return m.group(1)
        m = re.fullmatch(r"([a-zA-Z]{2,3})(?:[_-][A-Za-z]{2,4})?\.lproj", part)
        if m:
            return m.group(1).lower()
    if "LC_MESSAGES" in p.parts:
        return p.parts[p.parts.index("LC_MESSAGES") - 1].split("_")[0].split("-")[0]
    m = re.search(r"(?:^|[_.-])([a-z]{2,3})(?:[_-][A-Za-z]{2,4})?$", p.stem)
    return m.group(1) if m else None


def source_candidates(path: str, src: str) -> list[str]:
    p = Path(path)
    if "LC_MESSAGES" in p.parts:
        i = p.parts.index("LC_MESSAGES") - 1
        return [str(Path(*p.parts[:i], s, *p.parts[i + 1:])) for s in (src, f"{src}_GB", f"{src}_US")]
    for i, part in enumerate(p.parts):
        if re.fullmatch(r"values-[a-z]{2,3}(?:-r?[A-Z]{2})?", part):
            return [str(Path(*p.parts[:i], "values", *p.parts[i + 1:]))]
        if part.endswith(".lproj"):
            return [str(Path(*p.parts[:i], f"{n}.lproj", *p.parts[i + 1:])) for n in (src, "Base")]
    stem = re.sub(r"([_.-])?[a-z]{2,3}(?:[_-][A-Za-z]{2,4})?$", "", p.stem)
    sep = p.stem[len(stem)] if len(p.stem) > len(stem) and p.stem[len(stem)] in "_.-" else ""
    names = [f"{stem}{sep}{n}{p.suffix}" if stem else f"{n}{p.suffix}" for n in (src, f"{src}_GB", f"{src}-GB", f"{src}_US", f"{src}-US")]
    return [str(p.with_name(n)) for n in names]


def is_catalog(path: str) -> bool:
    if path.endswith(".po"):
        return "LC_MESSAGES" in path
    if path.endswith(".strings"):
        return ".lproj" in path
    if path.endswith(".xml"):
        return bool(re.search(r"/values(-[a-z]{2,3}(-r?[A-Z]{2})?)?/[^/]*strings[^/]*\.xml$", path))
    if path.endswith((".json", ".arb")):
        return bool(re.search(r"(i18n|locales?|lang|translations?|l10n|localization)", path, re.I)) and lang_of(path) is not None
    return False


# ---------------------------------------------------------------- checks
def ph(text: str) -> Counter:
    found = []
    for p in PLACEHOLDER.findall(text.replace("%%", "")):
        if p.startswith("<"):
            p = re.sub(r"^<\s*(/?[a-zA-Z][\w-]*).*", r"<\1>", p, flags=re.S).lower()
        else:
            p = re.sub(r"\s+", "", p)
        found.append(p)
    return Counter(found)


def icu_ok(text: str) -> str:
    depth = 0
    for ch in text:
        depth += ch == "{"
        depth -= ch == "}"
        if depth < 0:
            return "unbalanced braces"
    if depth:
        return "unbalanced braces"
    for m in ICU_COMPLEX.finditer(text):
        tail = text[m.end():]
        if not re.search(r"\bother\s*\{", tail):
            return f"ICU {m.group(2)} '{m.group(1)}' has no 'other' branch"
    return ""


def check_string(lang: str, key: str, src: str | None, tgt: str, keep: list[str], po_python: bool) -> list[tuple[str, str, str]]:
    """Return [(severity, check, detail)]."""
    out: list[tuple[str, str, str]] = []
    if tgt.strip() == "":
        if src and src.strip():
            out.append(("INFO", "empty", "falls back to source language (if the loader falls back at all)"))
        return out
    if src is None:
        out.append(("INFO", "not-in-source", "key has no source string (dead, renamed, or source missing)"))
        return out
    sp, tp = ph(src), ph(tgt)
    if sp != tp:
        miss = list((sp - tp).elements())
        extra = list((tp - sp).elements())
        sev = "ERROR"
        bits = []
        if miss:
            bits.append(f"missing {miss}")
        if extra:
            bits.append(f"unexpected {extra}")
        if all(x.startswith("<") for x in miss + extra):
            sev = "WARN"
        out.append((sev, "placeholder", "; ".join(bits)))
    if ICU_COMPLEX.search(src) or "{" in tgt:
        err = icu_ok(tgt)
        if err and not icu_ok(src):
            out.append(("ERROR", "icu-syntax", err))
    if po_python and (PERCENT_FORMAT.search(src) or PERCENT_FORMAT.search(tgt)) and STRAY_PERCENT.search(tgt.replace("%%", "")):
        out.append(("ERROR", "stray-percent", "lone % in a %-formatted string raises ValueError; use %%"))
    if len(src) > 3 and tgt == src and not any(k.lower() == src.lower() for k in keep) and WORD.search(src):
        out.append(("INFO", "untranslated", "identical to source (fine for brands, units, cognates)"))
    for term in keep:
        if term not in src:
            continue
        stem = term[:-1] if len(term) > 4 else term  # tolerate inflection: brandix -> brandixissa (fi)
        if term in tgt or stem in tgt:
            continue
        if stem.lower() in tgt.lower():
            out.append(("WARN", "do-not-translate", f"'{term}' has different casing in translation"))
        else:
            out.append(("WARN", "do-not-translate", f"'{term}' translated or missing"))
    if set(URL.findall(src)) - set(URL.findall(tgt)) and not URL.findall(tgt):
        out.append(("WARN", "url", "URL/e-mail from source is gone"))
    s_nums = {_num(n) for n in NUMBER.findall(src)}
    t_nums = {_num(n) for n in NUMBER.findall(tgt)}
    if s_nums - t_nums and not ph(src):
        if t_nums - s_nums:
            out.append(("WARN", "number", f"numbers differ: source {sorted(s_nums)}, translation {sorted(t_nums)}"))
        else:
            out.append(("INFO", "number-dropped", f"source numbers {sorted(s_nums - t_nums)} spelled out or dropped"))
    if t_nums - s_nums and sp and not s_nums:
        out.append(("WARN", "number", f"translation hard-codes {sorted(t_nums - s_nums)} where source uses placeholders"))
    if lang in COMMA_DECIMAL and re.search(r"(?<![\w.,])\d+\.\d{1,2}(?![\w.\d])", tgt) and not re.search(r"\d+\.\d", src):
        out.append(("WARN", "decimal", "dot decimal in a comma-decimal locale"))
    if src[:1].isupper() and tgt[:1].islower() and lang not in NO_CASE and not ph(tgt[:12]):
        out.append(("WARN", "case", "source starts uppercase, translation lowercase"))
    if src != src.strip() or tgt != tgt.strip():
        if (src[:1].isspace(), src[-1:].isspace()) != (tgt[:1].isspace(), tgt[-1:].isspace()):
            out.append(("WARN", "whitespace", "leading/trailing whitespace differs from source"))
    if "  " in tgt and "  " not in src:
        out.append(("WARN", "whitespace", "double space"))
    if src.count("\n") != tgt.count("\n"):
        out.append(("WARN", "newlines", f"source has {src.count(chr(10))} line breaks, translation {tgt.count(chr(10))}"))
    s_end, t_end = src.rstrip()[-1:], tgt.rstrip()[-1:]
    want_q = QUESTION_MARK.get(lang, "?")
    if s_end == "?" and t_end not in (want_q, "?", ";"):
        out.append(("WARN", "punctuation", f"source is a question, translation ends with {t_end!r}"))
    if t_end == ":" and s_end != ":":
        out.append(("WARN", "truncation", "translation ends with ':' but source does not (truncated?)"))
    if lang in QUESTION_MARK and t_end == "?":
        out.append(("WARN", "punctuation", f"question mark in '{lang}' is {QUESTION_MARK[lang]!r}, not '?'"))
    if len(src) >= 25 and len(tgt) < 0.4 * len(src):
        out.append(("WARN", "length", f"translation is {len(tgt)} chars vs source {len(src)} (truncated?)"))
    return out


# ---------------------------------------------------------------- driver
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="catalog files (default: catalogs changed between --base and --head)")
    ap.add_argument("--base", help="git ref to diff against (enables NEW/OLD tags)")
    ap.add_argument("--head", default=None, help="git ref to check (default: working tree)")
    ap.add_argument("--all", action="store_true", help="also report OLD findings for unchanged strings")
    ap.add_argument("--source-lang", default="en")
    ap.add_argument("--keep", action="append", default=[], help="term that must stay unchanged (brand, unit); repeatable")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--no-terms", action="store_true", help="skip the term-shift summary")
    a = ap.parse_args()

    base = git("merge-base", a.base, a.head or "HEAD").strip() if a.base else None
    if a.base and not base:
        sys.exit(f"cannot resolve merge-base of {a.base} and {a.head or 'HEAD'}")
    paths = a.paths or [p for p in git("diff", "--name-only", base, *( [a.head] if a.head else [] )).split() if is_catalog(p)]
    paths = [p for p in paths if is_catalog(p) and lang_of(p) not in (a.source_lang, None)]
    findings: list[Finding] = []
    terms: dict[str, tuple[Counter, Counter]] = defaultdict(lambda: (Counter(), Counter()))
    file_stats = []

    for path in sorted(set(paths)):
        lang = lang_of(path) or "?"
        head_text = read(a.head, path)
        if head_text is None:
            continue
        tgt, problems = parse(path, head_text)
        for p in problems:
            findings.append(Finding("ERROR" if "invalid" in p or "duplicate" in p or "nplurals" in p else "WARN", "catalog", "NEW", path, lang, "", "", "", p))
        src_map: dict[str, str] = {}
        src_path = next((c for c in source_candidates(path, a.source_lang) if exists(a.head, c)), None)
        if src_path:
            src_map, _ = parse(src_path, read(a.head, src_path) or "")
        keys_are_text = path.endswith(".po") and not src_map
        base_map: dict[str, str] = {}
        if base:
            bt = read(base, path)
            base_map = parse(path, bt)[0] if bt else {}
        po_python = path.endswith(".po")  # gettext catalogs are %-formatted by Python/C callers
        changed = 0
        for key, value in tgt.items():
            src_key = re.sub(r"\[\w+\]$", "", key)
            src = src_map.get(key) or src_map.get(src_key)
            if src is None and keys_are_text:
                src = src_key.split("\x04")[-1]
            if src is None and path.endswith(".po") and re.search(r"\[\d+\]$", key):
                src = src_map.get(src_key + "[0]") or src_map.get(src_key + "[1]")
            was = base_map.get(key) if base else None
            is_new = not base or was != value
            changed += is_new
            if base and was and value == "":
                findings.append(Finding("ERROR", "emptied", "NEW", path, lang, key, src or "", value, f"was: {was[:80]}"))
            if base and was and value and was[:1].isupper() and value[:1].islower() and lang not in NO_CASE:
                findings.append(Finding("WARN", "case-regression", "NEW", path, lang, key, src or "", value, f"was: {was[:80]}"))
            if not is_new and not a.all:
                continue
            for sev, check, detail in check_string(lang, key, src, value, a.keep, po_python):
                findings.append(Finding(sev, check, "NEW" if is_new and base else ("OLD" if base else "-"), path, lang, key, src or "", value, detail))
            if base and was and value and was != value and not a.no_terms:
                bw, hw = Counter(w.lower() for w in WORD.findall(was)), Counter(w.lower() for w in WORD.findall(value))
                terms[lang][0].update(bw - hw)
                terms[lang][1].update(hw - bw)
        for key in set(base_map) - set(tgt):
            if base_map[key]:
                findings.append(Finding("WARN", "removed", "NEW", path, lang, key, src_map.get(key, ""), "", f"was: {base_map[key][:80]}"))
        missing = [k for k, v in src_map.items() if v and k not in tgt]
        # a plural is missing only if the language has none of its forms (categories differ per language)
        tgt_bases = {re.sub(r"\[\w+\]$", "", k) for k in tgt if re.search(r"\[\w+\]$", k)}
        plural_missing = sorted({re.sub(r"\[\w+\]$", "", k) for k in missing if re.search(r"\[\w+\]$", k)} - tgt_bases)
        for k in plural_missing:
            findings.append(Finding("WARN", "plural-missing", "NEW" if base else "-", path, lang, k, src_map.get(k + "[0]") or src_map.get(k + "[other]", ""), "", "plural in source, absent here: renders source language"))
        if [k for k in missing if not re.search(r"\[\w+\]$", k)]:
            findings.append(Finding("INFO", "missing-keys", "-", path, lang, "", "", "", f"{len(missing)} source keys absent (fallback or raw key, depending on loader)"))
        if path.endswith(".po"):
            mo = path[:-3] + ".mo"
            if not exists(a.head, mo):
                findings.append(Finding("WARN", "catalog", "NEW", path, lang, "", "", "", ".mo missing next to .po"))
            elif base and git("diff", "--name-only", base, *([a.head] if a.head else []), "--", path) and not git("diff", "--name-only", base, *([a.head] if a.head else []), "--", mo):
                findings.append(Finding("ERROR", "catalog", "NEW", path, lang, "", "", "", ".po changed but .mo did not (recompile)"))
        file_stats.append((path, lang, len(tgt), changed, src_path))

    if a.json:
        print(json.dumps({"files": file_stats, "findings": [asdict(f) for f in findings]}, ensure_ascii=False, indent=1))
    else:
        print(f"files={len(file_stats)} base={base or '-'} head={a.head or 'worktree'}")
        missing_src = [p for p, *_, s in file_stats if not s]
        if missing_src:
            print(f"\n[INFO] no source-language file found for {len(missing_src)} file(s), e.g. {missing_src[:3]}")
        for sev in ("ERROR", "WARN", "INFO"):
            group = [f for f in findings if f.severity == sev]
            if not group:
                continue
            print(f"\n===== {sev} ({len(group)}) =====")
            by_check = defaultdict(list)
            for f in group:
                by_check[f.check].append(f)
            for check, items in sorted(by_check.items()):
                print(f"\n--- {check} ({len(items)})")
                shown = items if sev != "INFO" else items[:8]
                for f in shown:
                    print(f"  [{f.tag}] {f.lang} {f.file}\n      {f.key.replace(chr(4), ' | ')}")
                    if f.source:
                        print(f"      SRC: {f.source[:160]}")
                    if f.target:
                        print(f"      TR:  {f.target[:160]}")
                    if f.detail:
                        print(f"      >> {f.detail}")
                if len(items) > len(shown):
                    print(f"  ... {len(items) - len(shown)} more")
        shifts = []
        for lang, (rem, add) in sorted(terms.items()):
            r = [w for w, c in rem.most_common(6) if c >= 3]
            ad = [w for w, c in add.most_common(6) if c >= 3]
            if r or ad:
                shifts.append(f"  {lang}: -{r}  +{ad}")
        if shifts:
            print("\n===== TERM SHIFTS (words removed -> added in rewritten strings; bulk replaces show up here) =====")
            print("\n".join(shifts))
    return 1 if any(f.severity == "ERROR" and f.tag in ("NEW", "-") for f in findings) else 0


if __name__ == "__main__":
    import signal

    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped into head/less
    sys.exit(main())
