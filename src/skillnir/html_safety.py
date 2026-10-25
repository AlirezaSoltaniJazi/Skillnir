"""Escaping helpers for the static HTML the research pipelines generate.

Every value in those pages comes from AI output that was itself built from
arbitrary web content, so it must be treated as attacker-controlled. The
pages are served on the same origin as the unauthenticated UI, which makes
script injection there able to read the Settings page.

Stdlib-only so any pipeline module can import it without circular imports.
"""

import html
import json
import re
from urllib.parse import urlsplit

# Record IDs become file names (``<topic>/<id>.md``); anything outside this
# set — notably "/" , "\" and a leading "." — could escape the store.
_SAFE_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,159}")

# Browsers drop leading C0 controls and spaces before parsing the scheme.
_URL_LEADING_JUNK = "".join(chr(c) for c in range(0x21))

_SAFE_URL_SCHEMES = frozenset({"http", "https"})


def is_safe_id(value: str) -> bool:
    """Return True if *value* is usable as a single path component."""
    return bool(_SAFE_ID_RE.fullmatch(value))


def safe_url(url: str) -> str:
    """Return *url* if it is http(s), else ``"#"`` (blocks ``javascript:``)."""
    url = url.lstrip(_URL_LEADING_JUNK)
    try:
        scheme = urlsplit(url).scheme.lower()
    except ValueError:
        return "#"
    return url if scheme in _SAFE_URL_SCHEMES else "#"


def attr(value: object) -> str:
    """Escape *value* for an HTML attribute or text node."""
    return html.escape(str(value), quote=True)


def href(url: str) -> str:
    """Escape an external link for an ``href`` attribute."""
    return attr(safe_url(url))


def onclick_open(target: str) -> str:
    """Build an escaped ``onclick`` value that opens *target* in a new tab.

    ``html.escape`` alone is not enough inside inline JS: the browser decodes
    ``&#x27;`` back to ``'`` before the script runs. JSON-encoding first makes
    the target a valid JS string literal whatever it contains.
    """
    return attr(f"window.open({json.dumps(target)},'_blank')")
