"""Tests for skillnir.notifications.senders — per-provider POST senders."""

import json
import urllib.error
from unittest.mock import MagicMock, patch

from skillnir.notifications.senders import (
    send_cliq_notification,
    send_discord_notification,
    send_slack_notification,
    send_teams_notification,
    send_telegram_notification,
)

# Canonical valid URLs for each provider
_GCHAT = "https://chat.googleapis.com/v1/spaces/X/messages?key=y&token=z"
_SLACK = "https://hooks.slack.com/services/T123/B456/abcdef"
_DISCORD = "https://discord.com/api/webhooks/123/token"
_TEAMS = "https://prod-20.westus.logic.azure.com/workflows/abc/triggers/manual"
_CLIQ = "https://cliq.zoho.com/api/v2/bots/skillnir/message?zapikey=abc"
_TG_TOKEN = "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl"
_TG_CHAT = "-100999"


def _mock_200_response() -> MagicMock:
    fake_resp = MagicMock()
    fake_resp.status = 200
    fake_resp.__enter__ = MagicMock(return_value=fake_resp)
    fake_resp.__exit__ = MagicMock(return_value=False)
    return fake_resp


# ── Slack ─────────────────────────────────────────────────────────────────


class TestSendSlack:
    def test_success_posts_text_payload(self):
        with patch("urllib.request.urlopen", return_value=_mock_200_response()) as m:
            ok, err = send_slack_notification(
                {"url": _SLACK}, "Task complete", "some detail", 10.0
            )
        assert ok is True
        assert err is None
        body = json.loads(m.call_args[0][0].data.decode())
        assert "Task complete" in body["text"]
        assert "some detail" in body["text"]

    def test_invalid_url_never_opens_socket(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_slack_notification(
                {"url": "https://attacker.com/x"}, "t", None, 10.0
            )
        assert ok is False
        assert "invalid" in (err or "").lower()
        assert not m.called

    def test_empty_url(self):
        ok, err = send_slack_notification({"url": ""}, "t", None, 10.0)
        assert ok is False
        assert "not set" in (err or "")

    def test_http_error(self):
        exc = urllib.error.HTTPError(_SLACK, 403, "Forbidden", hdrs=None, fp=None)
        with patch("urllib.request.urlopen", side_effect=exc):
            ok, err = send_slack_notification({"url": _SLACK}, "t", None, 10.0)
        assert ok is False
        assert "403" in (err or "")


# ── Discord ───────────────────────────────────────────────────────────────


class TestSendDiscord:
    def test_success_posts_embeds_payload(self):
        with patch("urllib.request.urlopen", return_value=_mock_200_response()) as m:
            ok, err = send_discord_notification(
                {"url": _DISCORD}, "Task done", "detail", 10.0
            )
        assert ok is True
        assert err is None
        body = json.loads(m.call_args[0][0].data.decode())
        assert body["embeds"][0]["title"] == "Task done"
        assert body["embeds"][0]["description"] == "detail"
        assert body["embeds"][0]["footer"]["text"] == "Skillnir"

    def test_invalid_host_never_opens_socket(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_discord_notification(
                {"url": "https://evildiscord.com/webhooks/x"}, "t", None, 10.0
            )
        assert ok is False
        assert not m.called

    def test_url_error(self):
        with patch(
            "urllib.request.urlopen",
            side_effect=urllib.error.URLError("no route"),
        ):
            ok, err = send_discord_notification({"url": _DISCORD}, "t", None, 10.0)
        assert ok is False
        assert "no route" in (err or "")


# ── Microsoft Teams ───────────────────────────────────────────────────────


class TestSendTeams:
    def test_success_posts_title_detail_source(self):
        with patch("urllib.request.urlopen", return_value=_mock_200_response()) as m:
            ok, err = send_teams_notification(
                {"url": _TEAMS}, "Build done", "all green", 10.0
            )
        assert ok is True
        assert err is None
        body = json.loads(m.call_args[0][0].data.decode())
        assert body == {
            "title": "Build done",
            "detail": "all green",
            "source": "Skillnir",
        }

    def test_rejects_suffix_forgery(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_teams_notification(
                {"url": "https://evillogic.azure.com/workflows/x"}, "t", None, 10.0
            )
        assert ok is False
        assert not m.called

    def test_timeout_error(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError("slow")):
            ok, err = send_teams_notification({"url": _TEAMS}, "t", None, 10.0)
        assert ok is False
        assert "slow" in (err or "")


# ── Zoho Cliq ─────────────────────────────────────────────────────────────


class TestSendCliq:
    def test_success_posts_text_payload(self):
        with patch("urllib.request.urlopen", return_value=_mock_200_response()) as m:
            ok, err = send_cliq_notification(
                {"url": _CLIQ}, "Task complete", None, 10.0
            )
        assert ok is True
        body = json.loads(m.call_args[0][0].data.decode())
        assert "Task complete" in body["text"]

    def test_rejects_missing_zapikey(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_cliq_notification(
                {"url": "https://cliq.zoho.com/api/v2/bots/skillnir/message"},
                "t",
                None,
                10.0,
            )
        assert ok is False
        assert not m.called

    def test_rejects_non_cliq_zoho_host(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_cliq_notification(
                {"url": "https://crm.zoho.com/api/x?zapikey=abc"}, "t", None, 10.0
            )
        assert ok is False
        assert not m.called


# ── Telegram ──────────────────────────────────────────────────────────────


class TestSendTelegram:
    def test_success_posts_chat_id_and_text(self):
        with patch("urllib.request.urlopen", return_value=_mock_200_response()) as m:
            ok, err = send_telegram_notification(
                {"bot_token": _TG_TOKEN, "chat_id": _TG_CHAT},
                "Task done",
                "great",
                10.0,
            )
        assert ok is True
        assert err is None
        req = m.call_args[0][0]
        # URL must be constructed correctly
        assert f"api.telegram.org/bot{_TG_TOKEN}/sendMessage" in req.full_url
        body = json.loads(req.data.decode())
        assert body["chat_id"] == _TG_CHAT
        assert "Task done" in body["text"]
        assert "great" in body["text"]
        assert "parse_mode" not in body  # plain text for v1

    def test_invalid_token_never_opens_socket(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_telegram_notification(
                {"bot_token": "bogus", "chat_id": _TG_CHAT}, "t", None, 10.0
            )
        assert ok is False
        assert "token" in (err or "").lower()
        assert not m.called

    def test_missing_chat_id_never_opens_socket(self):
        with patch("urllib.request.urlopen") as m:
            ok, err = send_telegram_notification(
                {"bot_token": _TG_TOKEN, "chat_id": ""}, "t", None, 10.0
            )
        assert ok is False
        assert "chat" in (err or "").lower()
        assert not m.called

    def test_error_redacts_bot_token(self):
        """CRITICAL: Telegram errors must NEVER echo the bot token back.

        The bot token IS the capability. A stack trace or UI toast that
        includes the full URL would leak credentials to logs.
        """
        # Simulate an HTTPError whose reason string embeds the full URL
        url = f"https://api.telegram.org/bot{_TG_TOKEN}/sendMessage"
        exc = urllib.error.HTTPError(url, 401, f"Unauthorized: {_TG_TOKEN}", None, None)
        with patch("urllib.request.urlopen", side_effect=exc):
            ok, err = send_telegram_notification(
                {"bot_token": _TG_TOKEN, "chat_id": _TG_CHAT},
                "t",
                None,
                10.0,
            )
        assert ok is False
        assert err is not None
        assert _TG_TOKEN not in err, f"bot token leaked in error: {err!r}"
        assert "<redacted>" in err
