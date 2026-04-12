"""Tests for skillnir.notifier -- webhook POST helper."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

from skillnir.notifier import (
    _build_gchat_card,
    is_valid_gchat_webhook,
    send_gchat_notification,
)

_OK_URL = "https://chat.googleapis.com/v1/spaces/AAAA/messages?key=x&token=y"


class TestBuildGchatCard:
    def test_header_always_present(self):
        payload = _build_gchat_card("Task complete", None)
        card = payload["cardsV2"][0]["card"]
        assert card["header"]["title"] == "Skillnir"
        assert card["header"]["subtitle"] == "Task complete"
        assert "sections" not in card  # no detail -> no sections

    def test_detail_renders_text_paragraph(self):
        payload = _build_gchat_card("Skill generated", "backendEngineer v2")
        widgets = payload["cardsV2"][0]["card"]["sections"][0]["widgets"]
        assert widgets == [{"textParagraph": {"text": "backendEngineer v2"}}]


class TestIsValidGchatWebhook:
    def test_accepts_canonical_url(self):
        assert is_valid_gchat_webhook(_OK_URL) is True

    def test_accepts_bare_host_https(self):
        assert is_valid_gchat_webhook("https://chat.googleapis.com/anything") is True

    def test_host_is_case_insensitive(self):
        assert is_valid_gchat_webhook("https://Chat.GoogleAPIs.COM/v1/spaces/X") is True

    def test_rejects_empty_string(self):
        assert is_valid_gchat_webhook("") is False

    def test_rejects_http_scheme(self):
        # plaintext would leak the capability token
        assert is_valid_gchat_webhook("http://chat.googleapis.com/v1/spaces/X") is False

    def test_rejects_file_scheme(self):
        # file:// via urllib would read local files (SSRF-adjacent)
        assert is_valid_gchat_webhook("file:///etc/passwd") is False

    def test_rejects_ftp_scheme(self):
        assert is_valid_gchat_webhook("ftp://chat.googleapis.com/x") is False

    def test_rejects_foreign_host(self):
        assert is_valid_gchat_webhook("https://attacker.example.com/spaces/X") is False

    def test_rejects_localhost(self):
        assert is_valid_gchat_webhook("https://127.0.0.1/spaces/X") is False

    def test_rejects_host_suffix_trick(self):
        # "chat.googleapis.com.attacker.com" must not match
        assert (
            is_valid_gchat_webhook(
                "https://chat.googleapis.com.attacker.com/v1/spaces/X"
            )
            is False
        )

    def test_rejects_userinfo_masquerade(self):
        # userinfo@host — the real host is "attacker.com"
        assert (
            is_valid_gchat_webhook("https://chat.googleapis.com@attacker.com/spaces/X")
            is False
        )

    def test_rejects_garbage(self):
        assert is_valid_gchat_webhook("not a url") is False


class TestSendGchatNotification:
    def test_empty_url_returns_false(self):
        ok, err = send_gchat_notification("", "title")
        assert ok is False
        assert err == "webhook URL not set"

    def test_invalid_url_never_opens_socket(self):
        with patch("urllib.request.urlopen") as mock:
            ok, err = send_gchat_notification("http://chat.googleapis.com/x", "t")
        assert ok is False
        assert err == "invalid webhook URL"
        assert not mock.called

    def test_file_url_never_opens_socket(self):
        with patch("urllib.request.urlopen") as mock:
            ok, err = send_gchat_notification("file:///etc/passwd", "t")
        assert ok is False
        assert err == "invalid webhook URL"
        assert not mock.called

    def test_foreign_host_never_opens_socket(self):
        with patch("urllib.request.urlopen") as mock:
            ok, err = send_gchat_notification("https://attacker.example.com/x", "t")
        assert ok is False
        assert err == "invalid webhook URL"
        assert not mock.called

    def test_success_path(self):
        fake_resp = MagicMock()
        fake_resp.status = 200
        fake_resp.__enter__ = MagicMock(return_value=fake_resp)
        fake_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_resp) as mock:
            ok, err = send_gchat_notification(_OK_URL, "title", "detail")
        assert ok is True
        assert err is None
        assert mock.called
        sent_req = mock.call_args[0][0]
        body = json.loads(sent_req.data.decode())
        assert body["cardsV2"][0]["card"]["header"]["subtitle"] == "title"

    def test_http_error_returns_false(self):
        err = urllib.error.HTTPError(_OK_URL, 403, "Forbidden", hdrs=None, fp=None)
        with patch("urllib.request.urlopen", side_effect=err):
            ok, msg = send_gchat_notification(_OK_URL, "t")
        assert ok is False
        assert "403" in (msg or "")

    def test_url_error_returns_false(self):
        err = urllib.error.URLError("no route")
        with patch("urllib.request.urlopen", side_effect=err):
            ok, msg = send_gchat_notification(_OK_URL, "t")
        assert ok is False
        assert "no route" in (msg or "")

    def test_timeout_returns_false(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("slow")):
            ok, msg = send_gchat_notification(_OK_URL, "t")
        assert ok is False
        assert "slow" in (msg or "")
