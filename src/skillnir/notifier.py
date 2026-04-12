"""Outbound webhook notifications.

Currently supports Google Chat incoming webhooks only. Stdlib-only HTTP
(urllib.request) — mirrors the POST idiom in skillnir.usage.

All functions are fire-and-forget: failures never raise, they return
``(success, error_message)`` tuples so callers can optionally surface
errors via ``ui.notify`` or logs.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

_GCHAT_WEBHOOK_HOST = "chat.googleapis.com"


def is_valid_gchat_webhook(url: str) -> bool:
    """Return True if ``url`` is a well-formed Google Chat webhook URL.

    Accepts only ``https://chat.googleapis.com/...``. Any other scheme
    (``http``, ``file``, ``ftp``, ...) or host is rejected. This blocks
    typos that would leak the capability token over plaintext and
    SSRF-style probes against internal addresses via ``file://`` or
    ``http://127.0.0.1``.
    """
    if not url:
        return False
    try:
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return False
    if parts.scheme != "https":
        return False
    # ``netloc`` includes any ``userinfo@`` and ``:port`` — strip both.
    host = parts.hostname or ""
    return host.lower() == _GCHAT_WEBHOOK_HOST


def _build_gchat_card(title: str, detail: str | None) -> dict:
    """Build a Google Chat cards-v2 payload with a header + optional detail."""
    widgets: list[dict] = []
    if detail:
        widgets.append({"textParagraph": {"text": detail}})

    sections: list[dict] = []
    if widgets:
        sections.append({"widgets": widgets})

    card: dict = {
        "header": {
            "title": "Skillnir",
            "subtitle": title,
        },
    }
    if sections:
        card["sections"] = sections

    return {
        "cardsV2": [
            {
                "cardId": "skillnir-notification",
                "card": card,
            }
        ]
    }


def send_gchat_notification(
    webhook_url: str,
    title: str,
    detail: str | None = None,
    *,
    timeout: float = 10.0,
) -> tuple[bool, str | None]:
    """POST a Google Chat cards-v2 message to ``webhook_url``.

    Returns ``(True, None)`` on HTTP 2xx, ``(False, error_message)`` otherwise.
    Never raises.
    """
    if not webhook_url or not is_valid_gchat_webhook(webhook_url):
        return False, (
            "webhook URL not set" if not webhook_url else "invalid webhook URL"
        )

    payload = _build_gchat_card(title, detail)
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=data,
        headers={"Content-Type": "application/json; charset=UTF-8"},
        method="POST",
    )

    # B310 (urllib scheme check) is handled above by is_valid_gchat_webhook,
    # which enforces https://chat.googleapis.com and rejects file://, http://,
    # and arbitrary hosts before we ever open a socket.
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
            status = getattr(resp, "status", 200)
            if 200 <= status < 300:
                return True, None
            return False, f"HTTP {status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}: {exc.reason}"
    except urllib.error.URLError as exc:
        return False, f"network error: {exc.reason}"
    except (TimeoutError, OSError) as exc:
        return False, f"connection error: {exc}"
