"""Back-compat shim for the pre-multi-provider notifier API.

The real implementation lives in :mod:`skillnir.notifications` (split into
``providers`` and ``senders``). This module re-exports the pre-existing
public surface so older call sites and tests keep working unchanged.

New code should import from :mod:`skillnir.notifications` directly.
"""

from __future__ import annotations

from skillnir.notifications.providers import (
    PROVIDERS,
    NotificationProvider,
    ProviderSpec,
    is_valid_cliq_webhook,
    is_valid_discord_webhook,
    is_valid_gchat_webhook,
    is_valid_slack_webhook,
    is_valid_teams_webhook,
    is_valid_telegram_chat_id,
    is_valid_telegram_token,
)
from skillnir.notifications.senders import (
    _build_gchat_card,
    send_gchat_item,
    send_gchat_notification,
)

__all__ = [
    "PROVIDERS",
    "NotificationProvider",
    "ProviderSpec",
    "_build_gchat_card",
    "is_valid_cliq_webhook",
    "is_valid_discord_webhook",
    "is_valid_gchat_webhook",
    "is_valid_slack_webhook",
    "is_valid_teams_webhook",
    "is_valid_telegram_chat_id",
    "is_valid_telegram_token",
    "send_gchat_item",
    "send_gchat_notification",
]
