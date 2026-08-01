"""Rule-based prompt compression for reducing token count without losing meaning."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionResult:
    """Result of a prompt compression operation."""

    original: str
    compressed: str
    original_chars: int
    compressed_chars: int
    reduction_pct: float  # 0.0 to 100.0


# ---------------------------------------------------------------------------
# Word sets (frozenset for O(1) lookup)
# ---------------------------------------------------------------------------

_ARTICLES: frozenset[str] = frozenset({"a", "an", "the"})

_AUXILIARIES: frozenset[str] = frozenset(
    {
        "is",
        "are",
        "was",
        "were",
        "am",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
    }
)

_INTENSIFIERS: frozenset[str] = frozenset(
    {
        "very",
        "quite",
        "rather",
        "somewhat",
        "really",
        "extremely",
        "essentially",
        "particularly",
        "especially",
    }
)

_FILLERS: frozenset[str] = frozenset(
    {
        "currently",
        "basically",
        "actually",
        "simply",
        "just",
        "certainly",
        "definitely",
        "obviously",
        "clearly",
        "literally",
    }
)

_REMOVABLE: frozenset[str] = _ARTICLES | _AUXILIARIES | _INTENSIFIERS | _FILLERS

# Words that must NEVER be removed even if they appear in a removal set.
_KEEP_WORDS: frozenset[str] = frozenset(
    {
        "not",
        "no",
        "never",
        "without",
        "nor",
        "neither",
        "may",
        "might",
        "could",
        "seems",
        "appears",
        "from",
        "with",
        "must",
    }
)

# ---------------------------------------------------------------------------
# Phrase replacements (applied before word removal)
# ---------------------------------------------------------------------------

_PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("in order to", "to"),
    ("as well as", "and"),
    ("due to the fact that", "because"),
    ("in the case of", "for"),
    ("at this point in time", "now"),
    ("on the other hand", "however"),
    ("in addition to", "besides"),
    ("a large number of", "many"),
    ("a small number of", "few"),
    ("is able to", "can"),
    ("are able to", "can"),
    ("was able to", "could"),
    ("make sure that", "ensure"),
    ("make sure to", "ensure"),
    ("in the event that", "if"),
    ("with respect to", "regarding"),
    ("take into account", "consider"),
    ("it is important to note that", "note:"),
    ("it should be noted that", "note:"),
    ("for the purpose of", "to"),
    ("in the process of", "while"),
    ("on a regular basis", "regularly"),
    ("at the present time", "now"),
    ("for the most part", "mostly"),
    ("in the near future", "soon"),
    ("in the context of", "in"),
    ("with regard to", "regarding"),
    ("in terms of", "in"),
    ("as a result of", "from"),
    ("prior to", "before"),
)


# ---------------------------------------------------------------------------
# Protected zone detection
# ---------------------------------------------------------------------------

_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_JSON_TEMPLATE_RE = re.compile(r"\{{2,}[\s\S]*?\}{2,}")
_URL_RE = re.compile(r"https?://\S+")
_FILE_PATH_RE = re.compile(r"(?<!\w)[/~][\w./-]+(?:\.\w+)")
_MD_HEADER_RE = re.compile(r"^#+\s.*$", re.MULTILINE)
# YAML frontmatter at document start — skill descriptions drive activation
# matching, so a single dropped word there breaks skill triggering. Tolerate
# a UTF-8 BOM (Windows-edited files) and leading blank lines before ---.
_FRONTMATTER_RE = re.compile(
    r"\A﻿?(?:[ \t]*\n)*---[ \t]*\n[\s\S]*?\n---[ \t]*(?=\n|\Z)"
)
# Any line containing a pipe — markdown table rows lose column alignment
# (and cell content) under word removal.
_TABLE_ROW_RE = re.compile(r"^[^\n]*\|[^\n]*$", re.MULTILINE)
# Indented code blocks (4-space / tab) — as structural as fenced ones.
_INDENTED_CODE_RE = re.compile(r"(?:^(?:[ ]{4}|\t)[^\n]*\n?)+", re.MULTILINE)


def _find_protected_zones(text: str) -> list[tuple[int, int]]:
    """Find character ranges that must not be modified."""
    zones: list[tuple[int, int]] = []
    for pattern in (
        _CODE_BLOCK_RE,
        _INLINE_CODE_RE,
        _JSON_TEMPLATE_RE,
        _URL_RE,
        _FILE_PATH_RE,
        _MD_HEADER_RE,
        _FRONTMATTER_RE,
        _TABLE_ROW_RE,
        _INDENTED_CODE_RE,
    ):
        for m in pattern.finditer(text):
            zones.append((m.start(), m.end()))
    # Sort and merge overlapping zones.
    zones.sort()
    merged: list[tuple[int, int]] = []
    for start, end in zones:
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _split_by_zones(text: str, zones: list[tuple[int, int]]) -> list[tuple[str, bool]]:
    """Split text into (segment, is_protected) pairs."""
    parts: list[tuple[str, bool]] = []
    pos = 0
    for start, end in zones:
        if pos < start:
            parts.append((text[pos:start], False))
        parts.append((text[start:end], True))
        pos = end
    if pos < len(text):
        parts.append((text[pos:], False))
    return parts


# ---------------------------------------------------------------------------
# Compression transforms
# ---------------------------------------------------------------------------


def _compress_phrases(text: str) -> str:
    """Replace verbose multi-word phrases with concise equivalents."""
    for old, new in _PHRASE_REPLACEMENTS:
        text = re.sub(re.escape(old), new, text, flags=re.IGNORECASE)
    return text


# Word removal keeps words glued to these characters ("A/B", "the-flag",
# "a.out") — dropping half of a compound identifier changes its meaning.
_GLUE_CHARS = "/-_."


def _compress_words(text: str) -> str:
    """Remove articles, auxiliaries, intensifiers, and fillers."""

    def _replace(m: re.Match) -> str:
        word = m.group(1)
        lower = word.lower()
        if lower in _KEEP_WORDS or lower not in _REMOVABLE:
            return m.group(0)
        source = m.string
        before = source[m.start() - 1] if m.start() > 0 else ""
        after = source[m.end(1)] if m.end(1) < len(source) else ""
        if (before and before in _GLUE_CHARS) or (after and after in _GLUE_CHARS):
            return m.group(0)
        # "have/has/had to" expresses necessity — removal inverts intent.
        if lower in ("have", "has", "had") and re.match(
            r"\s*to\b", source[m.end(1) :], re.IGNORECASE
        ):
            return m.group(0)
        return ""

    # Match whole words plus one trailing space so removals don't leave gaps.
    result = re.sub(r"\b([A-Za-z]+)\b ?", _replace, text)
    return result


def _collapse_whitespace(text: str, strip_final: bool = True) -> str:
    """Normalize excess whitespace while preserving line structure.

    Leading indentation is never touched — it is structural in markdown
    (nested lists) and in code. Only interior runs, trailing whitespace,
    and blank-line stacks are collapsed.

    ``strip_final=False`` keeps whitespace at the very end of the text.
    Segments feeding ``compress_prompt`` need it: a segment's final space
    is usually the separator before an inline protected zone (URL, `code`,
    path), and stripping it glues the preceding word onto the zone.
    """
    # Collapse interior runs of spaces/tabs (never leading indentation).
    text = re.sub(r"(?<=\S)[^\S\n]+(?=\S)", " ", text)
    # Remove trailing whitespace before each newline. Anchoring on the
    # newline instead of `$` matters: under MULTILINE, `$` also matches
    # end-of-string, which is a segment boundary — not a line end.
    text = re.sub(r"[^\S\n]+(?=\n)", "", text)
    if strip_final:
        text = re.sub(r"[^\S\n]+\Z", "", text)
    # Collapse 3+ consecutive newlines into 2.
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compress_prompt(text: str) -> CompressionResult:
    """Compress a prompt using rule-based caveman compression.

    Applies, in order:
    1. Detect protected zones (code, JSON templates, URLs, paths, headers,
       YAML frontmatter, table rows, indented code)
    2. Replace verbose phrases with concise equivalents
    3. Remove articles, auxiliaries, intensifiers, fillers
    4. Collapse excess whitespace (per unprotected segment only)

    Returns a CompressionResult with the original and compressed text plus metrics.
    """
    if not text or not text.strip():
        return CompressionResult(
            original=text,
            compressed=text,
            original_chars=len(text),
            compressed_chars=len(text),
            reduction_pct=0.0,
        )

    zones = _find_protected_zones(text)
    parts = _split_by_zones(text, zones)

    # Every transform — including whitespace collapse — runs per unprotected
    # segment. Running any pass over the joined text would strip indentation
    # inside protected code blocks and flatten nested lists. Segment-final
    # whitespace is stripped only on the document's last segment: elsewhere
    # it is the separator before an inline protected zone.
    compressed_parts: list[str] = []
    for index, (segment, is_protected) in enumerate(parts):
        if is_protected:
            compressed_parts.append(segment)
        else:
            segment = _compress_phrases(segment)
            segment = _compress_words(segment)
            segment = _collapse_whitespace(segment, strip_final=index == len(parts) - 1)
            compressed_parts.append(segment)

    compressed = "".join(compressed_parts)

    original_chars = len(text)
    compressed_chars = len(compressed)
    reduction = (
        ((original_chars - compressed_chars) / original_chars * 100)
        if original_chars > 0
        else 0.0
    )

    return CompressionResult(
        original=text,
        compressed=compressed,
        original_chars=original_chars,
        compressed_chars=compressed_chars,
        reduction_pct=round(reduction, 1),
    )
