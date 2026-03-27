"""Tests for skillnir.usage -- session token usage tracking."""

from skillnir.usage import SessionUsageTracker, TokenUsage


class TestTokenUsage:
    def test_defaults(self):
        u = TokenUsage()
        assert u.input_tokens == 0
        assert u.output_tokens == 0
        assert u.total_tokens == 0
        assert u.num_requests == 0
        assert u.total_cost_usd == 0.0

    def test_add_usage(self):
        u = TokenUsage()
        u.add({'input_tokens': 100, 'output_tokens': 50}, cost=0.01)
        assert u.input_tokens == 100
        assert u.output_tokens == 50
        assert u.total_tokens == 150
        assert u.num_requests == 1
        assert u.total_cost_usd == 0.01

    def test_add_multiple(self):
        u = TokenUsage()
        u.add({'input_tokens': 100, 'output_tokens': 50})
        u.add(
            {
                'input_tokens': 200,
                'output_tokens': 100,
                'cache_creation_input_tokens': 30,
            }
        )
        assert u.input_tokens == 300
        assert u.output_tokens == 150
        assert u.cache_creation_input_tokens == 30
        assert u.num_requests == 2

    def test_add_with_missing_keys(self):
        u = TokenUsage()
        u.add({})
        assert u.input_tokens == 0
        assert u.num_requests == 1

    def test_to_dict(self):
        u = TokenUsage(input_tokens=10, output_tokens=5, num_requests=1)
        d = u.to_dict()
        assert d['total_tokens'] == 15
        assert d['input_tokens'] == 10
        assert d['num_requests'] == 1


class TestSessionUsageTracker:
    def test_record_and_get(self):
        tracker = SessionUsageTracker()
        tracker.record('claude', {'input_tokens': 100, 'output_tokens': 50})
        usage = tracker.get_usage('claude')
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50

    def test_get_unknown_backend(self):
        tracker = SessionUsageTracker()
        usage = tracker.get_usage('unknown')
        assert usage.total_tokens == 0

    def test_multiple_backends(self):
        tracker = SessionUsageTracker()
        tracker.record('claude', {'input_tokens': 100, 'output_tokens': 50})
        tracker.record('gemini', {'input_tokens': 200, 'output_tokens': 100})
        all_usage = tracker.get_all()
        assert len(all_usage) == 2
        assert all_usage['claude'].input_tokens == 100
        assert all_usage['gemini'].input_tokens == 200

    def test_get_total(self):
        tracker = SessionUsageTracker()
        tracker.record('claude', {'input_tokens': 100, 'output_tokens': 50}, cost=0.01)
        tracker.record('gemini', {'input_tokens': 200, 'output_tokens': 100}, cost=0.02)
        total = tracker.get_total()
        assert total.input_tokens == 300
        assert total.output_tokens == 150
        assert total.total_tokens == 450
        assert total.total_cost_usd == 0.03
        assert total.num_requests == 2

    def test_accumulate_same_backend(self):
        tracker = SessionUsageTracker()
        tracker.record('claude', {'input_tokens': 100, 'output_tokens': 50})
        tracker.record('claude', {'input_tokens': 200, 'output_tokens': 100})
        usage = tracker.get_usage('claude')
        assert usage.input_tokens == 300
        assert usage.num_requests == 2

    def test_reset(self):
        tracker = SessionUsageTracker()
        tracker.record('claude', {'input_tokens': 100, 'output_tokens': 50})
        tracker.reset()
        assert tracker.get_total().total_tokens == 0
        assert len(tracker.get_all()) == 0
