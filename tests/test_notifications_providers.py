"""Tests for skillnir.notifications.providers — validators + registry."""

from skillnir.notifications import PROVIDERS, NotificationProvider
from skillnir.notifications.providers import (
    is_valid_cliq_webhook,
    is_valid_discord_webhook,
    is_valid_slack_webhook,
    is_valid_teams_webhook,
    is_valid_telegram_chat_id,
    is_valid_telegram_token,
)


class TestRegistry:
    def test_all_six_providers_registered(self):
        assert set(PROVIDERS.keys()) == set(NotificationProvider)

    def test_each_provider_has_required_spec_fields(self):
        for provider_id, spec in PROVIDERS.items():
            assert spec.id == provider_id
            assert spec.display_name
            assert spec.icon
            assert spec.credential_fields
            assert callable(spec.validator)
            assert callable(spec.sender)
            assert spec.help_url.startswith("https://")

    def test_telegram_has_two_credential_fields(self):
        assert PROVIDERS[NotificationProvider.TELEGRAM].credential_fields == (
            "bot_token",
            "chat_id",
        )

    def test_single_url_providers_have_one_field(self):
        for pid in (
            NotificationProvider.GCHAT,
            NotificationProvider.SLACK,
            NotificationProvider.DISCORD,
            NotificationProvider.TEAMS,
            NotificationProvider.CLIQ,
        ):
            assert PROVIDERS[pid].credential_fields == ("url",)


class TestSlackValidator:
    def test_accepts_canonical(self):
        assert (
            is_valid_slack_webhook("https://hooks.slack.com/services/T123/B456/abcdef")
            is True
        )

    def test_rejects_http(self):
        assert is_valid_slack_webhook("http://hooks.slack.com/services/T/B/X") is False

    def test_rejects_foreign_host(self):
        assert is_valid_slack_webhook("https://attacker.com/services/T/B/X") is False

    def test_rejects_suffix_forgery(self):
        assert (
            is_valid_slack_webhook(
                "https://hooks.slack.com.attacker.com/services/T/B/X"
            )
            is False
        )

    def test_rejects_empty(self):
        assert is_valid_slack_webhook("") is False


class TestDiscordValidator:
    def test_accepts_discord_com(self):
        assert (
            is_valid_discord_webhook("https://discord.com/api/webhooks/123/abc") is True
        )

    def test_accepts_discordapp_com(self):
        assert (
            is_valid_discord_webhook("https://discordapp.com/api/webhooks/123/abc")
            is True
        )

    def test_rejects_http(self):
        assert (
            is_valid_discord_webhook("http://discord.com/api/webhooks/123/abc") is False
        )

    def test_rejects_foreign_host(self):
        assert (
            is_valid_discord_webhook("https://evildiscord.com/api/webhooks/123/abc")
            is False
        )

    def test_rejects_suffix_forgery(self):
        assert (
            is_valid_discord_webhook(
                "https://discord.com.attacker.com/api/webhooks/123/abc"
            )
            is False
        )


class TestTeamsValidator:
    def test_accepts_canonical_power_automate_url(self):
        assert (
            is_valid_teams_webhook(
                "https://prod-20.westus.logic.azure.com/workflows/abc/triggers/manual"
            )
            is True
        )

    def test_accepts_any_logic_azure_subdomain(self):
        assert (
            is_valid_teams_webhook("https://foo.bar.baz.logic.azure.com/workflows/x")
            is True
        )

    def test_rejects_http(self):
        assert (
            is_valid_teams_webhook(
                "http://prod-20.westus.logic.azure.com/workflows/abc"
            )
            is False
        )

    def test_rejects_suffix_forgery_evillogic(self):
        # "evillogic.azure.com" must NOT match ".logic.azure.com"
        assert (
            is_valid_teams_webhook("https://evillogic.azure.com/workflows/x") is False
        )

    def test_rejects_foreign_host(self):
        assert is_valid_teams_webhook("https://azure.com/workflows/x") is False

    def test_rejects_exact_suffix_only(self):
        # "logic.azure.com" without any prefix — needs a subdomain
        assert is_valid_teams_webhook("https://logic.azure.com/workflows/x") is False


class TestCliqValidator:
    def test_accepts_com_with_zapikey(self):
        assert (
            is_valid_cliq_webhook(
                "https://cliq.zoho.com/api/v2/bots/skillnir/message?zapikey=abc"
            )
            is True
        )

    def test_accepts_eu_region(self):
        assert (
            is_valid_cliq_webhook(
                "https://cliq.zoho.eu/api/v2/bots/skillnir/message?zapikey=abc"
            )
            is True
        )

    def test_accepts_in_region(self):
        assert (
            is_valid_cliq_webhook(
                "https://cliq.zoho.in/api/v2/bots/skillnir/message?zapikey=abc"
            )
            is True
        )

    def test_rejects_without_zapikey(self):
        assert (
            is_valid_cliq_webhook("https://cliq.zoho.com/api/v2/bots/skillnir/message")
            is False
        )

    def test_rejects_http(self):
        assert (
            is_valid_cliq_webhook(
                "http://cliq.zoho.com/api/v2/bots/x/message?zapikey=abc"
            )
            is False
        )

    def test_rejects_foreign_zoho_host(self):
        assert (
            is_valid_cliq_webhook("https://crm.zoho.com/api/v2/bots/x?zapikey=abc")
            is False
        )


class TestTelegramValidators:
    def test_token_accepts_canonical(self):
        assert (
            is_valid_telegram_token("123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl")
            is True
        )

    def test_token_rejects_empty(self):
        assert is_valid_telegram_token("") is False

    def test_token_rejects_too_short(self):
        assert is_valid_telegram_token("123:abc") is False

    def test_token_rejects_missing_colon(self):
        assert (
            is_valid_telegram_token("123456789AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl")
            is False
        )

    def test_token_rejects_non_digit_prefix(self):
        assert (
            is_valid_telegram_token("abc:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl") is False
        )

    def test_chat_id_accepts_positive_int(self):
        assert is_valid_telegram_chat_id("12345") is True

    def test_chat_id_accepts_negative_supergroup(self):
        assert is_valid_telegram_chat_id("-1001234567890") is True

    def test_chat_id_accepts_username(self):
        assert is_valid_telegram_chat_id("@skillnir_test") is True

    def test_chat_id_rejects_short_username(self):
        # Username shorter than 5 chars after @
        assert is_valid_telegram_chat_id("@ab") is False

    def test_chat_id_rejects_plain_text(self):
        assert is_valid_telegram_chat_id("not a chat id") is False

    def test_chat_id_rejects_empty(self):
        assert is_valid_telegram_chat_id("") is False


class TestProviderSpecValidators:
    """The dict-based validator wrappers (ProviderSpec.validator) return
    ``(bool, error)`` tuples, not raw bools."""

    def test_gchat_empty_dict(self):
        ok, err = PROVIDERS[NotificationProvider.GCHAT].validator({})
        assert ok is False
        assert "not set" in (err or "")

    def test_gchat_valid(self):
        ok, err = PROVIDERS[NotificationProvider.GCHAT].validator(
            {"url": "https://chat.googleapis.com/v1/spaces/X"}
        )
        assert ok is True
        assert err is None

    def test_telegram_missing_chat_id(self):
        ok, err = PROVIDERS[NotificationProvider.TELEGRAM].validator(
            {"bot_token": "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl"}
        )
        assert ok is False
        assert "chat" in (err or "").lower()

    def test_telegram_invalid_token_format(self):
        ok, err = PROVIDERS[NotificationProvider.TELEGRAM].validator(
            {"bot_token": "totally wrong", "chat_id": "-100123"}
        )
        assert ok is False
        assert "token" in (err or "").lower()

    def test_telegram_valid(self):
        ok, err = PROVIDERS[NotificationProvider.TELEGRAM].validator(
            {
                "bot_token": "123456789:AAHtYjKlmNopQrStUvWxYzAbCdEfGhIjKl",
                "chat_id": "-100999",
            }
        )
        assert ok is True
        assert err is None
