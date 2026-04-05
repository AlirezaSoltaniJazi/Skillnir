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


def _split_by_zones(
    text: str, zones: list[tuple[int, int]]
) -> list[tuple[str, bool]]:
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


def _compress_words(text: str) -> str:
    """Remove articles, auxiliaries, intensifiers, and fillers."""

    def _replace(m: re.Match) -> str:
        word = m.group(0)
        lower = word.lower()
        if lower in _KEEP_WORDS:
            return word
        if lower in _REMOVABLE:
            return ""
        return word

    # Match whole words only.
    result = re.sub(r"\b[A-Za-z]+\b", _replace, text)
    return result


def _collapse_whitespace(text: str) -> str:
    """Normalize excess whitespace while preserving structure."""
    # Collapse multiple spaces (but not newlines) into one.
    text = re.sub(r"[^\S\n]+", " ", text)
    # Collapse 3+ consecutive newlines into 2.
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove trailing whitespace on each line.
    text = re.sub(r" +$", "", text, flags=re.MULTILINE)
    # Remove leading whitespace on each line (but keep bullet indentation).
    text = re.sub(r"^[ \t]+(?=[^\s*\-\d])", "", text, flags=re.MULTILINE)
    return text.strip()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compress_prompt(text: str) -> CompressionResult:
    """Compress a prompt using rule-based caveman compression.

    Applies, in order:
    1. Detect protected zones (code, JSON templates, URLs, paths, headers)
    2. Replace verbose phrases with concise equivalents
    3. Remove articles, auxiliaries, intensifiers, fillers
    4. Collapse excess whitespace

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

    compressed_parts: list[str] = []
    for segment, is_protected in parts:
        if is_protected:
            compressed_parts.append(segment)
        else:
            segment = _compress_phrases(segment)
            segment = _compress_words(segment)
            compressed_parts.append(segment)

    compressed = "".join(compressed_parts)
    compressed = _collapse_whitespace(compressed)

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
