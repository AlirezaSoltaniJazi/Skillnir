"""Tests for skillnir.notifier -- webhook POST helper."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

from skillnir.notifier import _build_gchat_card, send_gchat_notification


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


class TestSendGchatNotification:
    def test_empty_url_returns_false(self):
        ok, err = send_gchat_notification("", "title")
        assert ok is False
        assert err == "webhook URL not set"

    def test_success_path(self):
        fake_resp = MagicMock()
        fake_resp.status = 200
        fake_resp.__enter__ = MagicMock(return_value=fake_resp)
        fake_resp.__exit__ = MagicMock(return_value=False)

        with patch("urllib.request.urlopen", return_value=fake_resp) as mock:
            ok, err = send_gchat_notification(
                "https://chat.googleapis.com/v1/spaces/X",
                "title",
                "detail",
            )
        assert ok is True
        assert err is None
        assert mock.called
        sent_req = mock.call_args[0][0]
        body = json.loads(sent_req.data.decode())
        assert body["cardsV2"][0]["card"]["header"]["subtitle"] == "title"

    def test_http_error_returns_false(self):
        err = urllib.error.HTTPError(
            "https://example.com", 403, "Forbidden", hdrs=None, fp=None
        )
        with patch("urllib.request.urlopen", side_effect=err):
            ok, msg = send_gchat_notification("https://example.com", "t")
        assert ok is False
        assert "403" in (msg or "")

    def test_url_error_returns_false(self):
        err = urllib.error.URLError("no route")
        with patch("urllib.request.urlopen", side_effect=err):
            ok, msg = send_gchat_notification("https://example.com", "t")
        assert ok is False
        assert "no route" in (msg or "")

    def test_timeout_returns_false(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("slow")):
            ok, msg = send_gchat_notification("https://example.com", "t")
        assert ok is False
        assert "slow" in (msg or "")
