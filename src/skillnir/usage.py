"""Session-level token usage tracking."""

from dataclasses import dataclass, field
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
