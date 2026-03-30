"""Session-level token usage tracking + API-based usage fetching."""

import json
import platform
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock


@dataclass
class TokenUsage:
    """Accumulated token counts for a single backend interaction."""

    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    total_cost_usd: float = 0.0
    num_requests: int = 0

    @property
    def total_tokens(self) -> int:
        """Return sum of input and output tokens."""
        return self.input_tokens + self.output_tokens

    def add(self, usage_dict: dict, cost: float | None = None) -> None:
        """Accumulate token counts from a usage dictionary."""
        self.input_tokens += usage_dict.get('input_tokens', 0)
        self.output_tokens += usage_dict.get('output_tokens', 0)
        self.cache_creation_input_tokens += usage_dict.get(
            'cache_creation_input_tokens', 0
        )
        self.cache_read_input_tokens += usage_dict.get('cache_read_input_tokens', 0)
        if cost:
            self.total_cost_usd += cost
        self.num_requests += 1

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'input_tokens': self.input_tokens,
            'output_tokens': self.output_tokens,
            'cache_creation_input_tokens': self.cache_creation_input_tokens,
            'cache_read_input_tokens': self.cache_read_input_tokens,
            'total_cost_usd': self.total_cost_usd,
            'total_tokens': self.total_tokens,
            'num_requests': self.num_requests,
        }


@dataclass
class SessionUsageTracker:
    """Thread-safe session-level usage accumulator."""

    _usage_by_backend: dict[str, TokenUsage] = field(default_factory=dict)
    _lock: Lock = field(default_factory=Lock)

    def record(
        self,
        backend_name: str,
        usage_dict: dict,
        cost: float | None = None,
    ) -> None:
        """Record token usage for a backend."""
        with self._lock:
            if backend_name not in self._usage_by_backend:
                self._usage_by_backend[backend_name] = TokenUsage()
            self._usage_by_backend[backend_name].add(usage_dict, cost)

    def get_usage(self, backend_name: str) -> TokenUsage:
        """Get usage for a specific backend."""
        with self._lock:
            return self._usage_by_backend.get(backend_name, TokenUsage())

    def get_all(self) -> dict[str, TokenUsage]:
        """Get all backend usage data."""
        with self._lock:
            return dict(self._usage_by_backend)

    def get_total(self) -> TokenUsage:
        """Get aggregated usage across all backends."""
        with self._lock:
            total = TokenUsage()
            for u in self._usage_by_backend.values():
                total.input_tokens += u.input_tokens
                total.output_tokens += u.output_tokens
                total.cache_creation_input_tokens += u.cache_creation_input_tokens
                total.cache_read_input_tokens += u.cache_read_input_tokens
                total.total_cost_usd += u.total_cost_usd
                total.num_requests += u.num_requests
            return total

    def reset(self) -> None:
        """Reset all tracked usage."""
        with self._lock:
            self._usage_by_backend.clear()


# Module-level singleton — lives for the process lifetime.
session_tracker = SessionUsageTracker()


# ---------------------------------------------------------------------------
# Claude API usage (OAuth-based, like claude-pulse)
# ---------------------------------------------------------------------------

USAGE_API_HOSTNAME = "api.anthropic.com"
USAGE_API_PATH = "/api/oauth/usage"
KEYCHAIN_SERVICE = "Claude Code-credentials"


@dataclass
class ClaudeApiUsage:
    """Usage data from Claude's OAuth API."""

    five_hour_utilization: float = 0.0
    five_hour_resets_at: str = ""
    seven_day_utilization: float = 0.0
    seven_day_resets_at: str = ""
    seven_day_sonnet_utilization: float = 0.0
    seven_day_opus_utilization: float = 0.0
    extra_usage_enabled: bool = False
    extra_usage_limit: float = 0.0
    extra_usage_used: float = 0.0


def _get_oauth_credentials() -> str | None:
    """Read Claude OAuth access token from keychain (macOS) or file."""
    if platform.system() == "Darwin":
        return _get_credentials_from_keychain()
    return _get_credentials_from_file()


def _get_credentials_from_keychain() -> str | None:
    """Read from macOS keychain."""
    try:
        result = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None

        import re

        match = re.search(r'"acct"<blob>="([^"]+)"', result.stdout)
        account = match.group(1) if match else ""
        if not account:
            import os

            account = os.getenv("USER", "")

        result2 = subprocess.run(
            [
                "/usr/bin/security",
                "find-generic-password",
                "-s",
                KEYCHAIN_SERVICE,
                "-a",
                account,
                "-w",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result2.returncode != 0:
            return None

        parsed = json.loads(result2.stdout.strip())
        oauth = parsed.get("claudeAiOauth", {})
        return oauth.get("accessToken")
    except subprocess.TimeoutExpired, json.JSONDecodeError, OSError:
        return None


def _get_credentials_from_file() -> str | None:
    """Read from ~/.claude/.credentials.json."""
    try:
        cred_path = Path.home() / ".claude" / ".credentials.json"
        parsed = json.loads(cred_path.read_text(encoding="utf-8"))
        oauth = parsed.get("claudeAiOauth", {})
        return oauth.get("accessToken")
    except FileNotFoundError, json.JSONDecodeError, OSError:
        return None


def fetch_claude_api_usage() -> ClaudeApiUsage | None:
    """Fetch usage data from Claude's OAuth API.

    Returns ClaudeApiUsage on success, None on failure.
    """
    import urllib.request

    token = _get_oauth_credentials()
    if not token:
        return None

    url = f"https://{USAGE_API_HOSTNAME}{USAGE_API_PATH}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "anthropic-beta": "oauth-2025-04-20",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError, json.JSONDecodeError, OSError:
        return None

    usage = ClaudeApiUsage()

    five_hour = data.get("five_hour") or {}
    usage.five_hour_utilization = five_hour.get("utilization", 0.0)
    usage.five_hour_resets_at = five_hour.get("resets_at", "")

    seven_day = data.get("seven_day") or {}
    usage.seven_day_utilization = seven_day.get("utilization", 0.0)
    usage.seven_day_resets_at = seven_day.get("resets_at", "")

    sonnet = data.get("seven_day_sonnet") or {}
    usage.seven_day_sonnet_utilization = sonnet.get("utilization", 0.0)

    opus = data.get("seven_day_opus") or {}
    usage.seven_day_opus_utilization = opus.get("utilization", 0.0)

    extra = data.get("extra_usage") or {}
    usage.extra_usage_enabled = extra.get("is_enabled", False)
    usage.extra_usage_limit = extra.get("monthly_limit", 0.0)
    usage.extra_usage_used = extra.get("used_credits", 0.0)

    return usage
