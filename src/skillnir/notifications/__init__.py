"""Multi-provider outbound notification system.

Modules:
- ``providers``: registry, validators, and the ``NotificationProvider`` enum
- ``senders``: per-provider POST senders + shared ``_post_json`` helper

The top-level :mod:`skillnir.notifier` module re-exports the public surface
for backward compatibility with pre-multi-provider call sites.
"""

from skillnir.notifications.providers import (
    PROVIDERS,
    NotificationProvider,
    ProviderSpec,
    is_valid_gchat_webhook,
)
from skillnir.notifications.senders import (
    _build_gchat_card,
    send_gchat_intel_report,
    send_gchat_item,
    send_gchat_notification,
)

__all__ = [
    "PROVIDERS",
    "NotificationProvider",
    "ProviderSpec",
    "is_valid_gchat_webhook",
    "send_gchat_intel_report",
    "send_gchat_item",
    "send_gchat_notification",
    "_build_gchat_card",
]
