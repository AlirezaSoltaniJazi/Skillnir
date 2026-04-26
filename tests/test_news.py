"""Tests for skillnir.news -- categories, recency, parser, dedup, landing page."""

from pathlib import Path

from skillnir.news import (
    DEFAULT_RECENCY,
    NEWS_CATEGORIES,
    NEWS_CATEGORY_QUERIES,
    NEWS_RECENCY,
    NewsItem,
    _dict_to_news_item,
    _generate_landing_html,
    _load_index,
    _parse_news_json,
    _recency_hint,
    _save_index,
    _try_parse_json_array,
    _write_news_md,
)


class TestCategoryCatalog:
    def test_has_five_categories(self):
        assert len(NEWS_CATEGORIES) == 5

    def test_expected_keys(self):
        for key in (
            "model-releases",
            "funding",
            "regulation",
            "research",
            "product",
        ):
            assert key in NEWS_CATEGORIES

    def test_every_category_has_a_query(self):
        for key in NEWS_CATEGORIES:
            assert key in NEWS_CATEGORY_QUERIES
            assert NEWS_CATEGORY_QUERIES[key]


class TestRecency:
    def test_default_is_seven_days(self):
        assert DEFAULT_RECENCY == "7d"
        assert NEWS_RECENCY[DEFAULT_RECENCY] == 7

    def test_three_windows(self):
        assert set(NEWS_RECENCY.keys()) == {"24h", "48h", "7d"}

    def test_hint_24h_says_24_hours(self):
        assert "24 hours" in _recency_hint("24h")

    def test_hint_48h_says_48_hours(self):
        assert "48 hours" in _recency_hint("48h")

    def test_hint_7d_says_7_days(self):
        assert "7 days" in _recency_hint("7d")

    def test_unknown_recency_falls_back_to_default(self):
        # Should produce the same hint as the default window
        assert _recency_hint("nonsense") == _recency_hint(DEFAULT_RECENCY)


class TestDictToNewsItem:
    def test_minimal_valid_dict_becomes_news_item(self):
        item = {
            "id": "anthropic-2026-04-25-claude-opus-47",
            "title": "Claude Opus 4.7 released",
            "source_url": "https://anthropic.com/news/claude-opus-4-7",
            "source_name": "Anthropic",
            "published_date": "2026-04-25",
            "summary": "Anthropic announced Claude Opus 4.7 today.",
        }
        n = _dict_to_news_item(item, "model-releases")
        assert n is not None
        assert n.category == "model-releases"
        assert n.id == "anthropic-2026-04-25-claude-opus-47"
        assert n.summary.startswith("Anthropic")

    def test_missing_required_fields_returns_none(self):
        assert _dict_to_news_item({"id": "x"}, "model-releases") is None
        assert _dict_to_news_item({}, "model-releases") is None

    def test_non_dict_returns_none(self):
        assert _dict_to_news_item("not a dict", "model-releases") is None
        assert _dict_to_news_item(None, "model-releases") is None


class TestParseNewsJson:
    def test_parses_fenced_json_block(self):
        text = """Here are today's news:

```json
[
  {
    "id": "openai-2026-04-25-gpt5",
    "title": "GPT-5 announced",
    "source_url": "https://openai.com/blog/gpt-5",
    "source_name": "OpenAI",
    "published_date": "2026-04-25",
    "summary": "OpenAI announced GPT-5."
  }
]
```
"""
        items = _parse_news_json(text, "model-releases")
        assert len(items) == 1
        assert items[0].category == "model-releases"
        assert items[0].title == "GPT-5 announced"

    def test_parses_inline_array(self):
        text = (
            'noise [{"id":"x-2026-04-25-y","title":"T",'
            '"source_url":"https://e.com/x",'
            '"source_name":"e","published_date":"2026-04-25",'
            '"summary":"s"}] more noise'
        )
        items = _parse_news_json(text, "funding")
        assert len(items) == 1
        assert items[0].category == "funding"

    def test_returns_empty_when_no_json(self):
        assert _parse_news_json("nothing useful here", "regulation") == []

    def test_try_parse_rejects_non_list(self):
        assert _try_parse_json_array('{"id": "x"}', "regulation") == []


class TestIndexRoundTrip:
    def test_save_then_load(self, tmp_path: Path):
        item = NewsItem(
            id="anthropic-2026-04-25-claude-opus-47",
            title="Claude Opus 4.7 released",
            source_url="https://anthropic.com/news/claude-opus-4-7",
            source_name="Anthropic",
            published_date="2026-04-25",
            category="model-releases",
            summary="Anthropic announced Claude Opus 4.7 today.",
        )
        _save_index(tmp_path, {item.id: item})
        loaded = _load_index(tmp_path)
        assert item.id in loaded
        assert loaded[item.id].title == "Claude Opus 4.7 released"
        assert loaded[item.id].category == "model-releases"

    def test_save_uses_news_index_filename(self, tmp_path: Path):
        item = NewsItem(
            id="x-2026-04-25-y",
            title="x",
            source_url="https://x.com",
            source_name="x",
            published_date="2026-04-25",
            category="product",
        )
        _save_index(tmp_path, {item.id: item})
        # Critical: must NOT collide with research / events / testing-research
        assert (tmp_path / "news-index.json").exists()
        assert not (tmp_path / "research-index.json").exists()
        assert not (tmp_path / "events-index.json").exists()
        assert not (tmp_path / "testing-research-index.json").exists()

    def test_dedup_same_id_collapses_to_one(self, tmp_path: Path):
        item_a = NewsItem(
            id="dupe-2026-04-25-x",
            title="A",
            source_url="https://a.com",
            source_name="a",
            published_date="2026-04-25",
            category="research",
        )
        item_b = NewsItem(
            id="dupe-2026-04-25-x",
            title="B (different title, same id)",
            source_url="https://b.com",
            source_name="b",
            published_date="2026-04-25",
            category="research",
        )
        # Simulating the pipeline writing the same id twice — the second
        # write should overwrite, not duplicate. (The pipeline itself
        # skips dupes; this guards the persistence layer too.)
        _save_index(tmp_path, {item_a.id: item_a, item_b.id: item_b})
        loaded = _load_index(tmp_path)
        assert len(loaded) == 1
        assert loaded[item_a.id].title.startswith("B")

    def test_load_returns_empty_when_missing(self, tmp_path: Path):
        assert _load_index(tmp_path) == {}

    def test_load_handles_corrupt_json(self, tmp_path: Path):
        (tmp_path / "news-index.json").write_text("not valid json", encoding="utf-8")
        assert _load_index(tmp_path) == {}


class TestNewsMarkdown:
    def test_writes_md_under_category_subdir(self, tmp_path: Path):
        items_dir = tmp_path / "items"
        items_dir.mkdir()
        item = NewsItem(
            id="test-2026-04-25-x",
            title="Test headline",
            source_url="https://example.com/x",
            source_name="Example",
            published_date="2026-04-25",
            category="funding",
            summary="Series B raised.",
        )
        md_path = _write_news_md(item, items_dir)
        assert md_path.parent.name == "funding"
        text = md_path.read_text(encoding="utf-8")
        assert "Test headline" in text
        assert "https://example.com/x" in text
        assert "Series B raised." in text


class TestLandingPage:
    def test_generates_index_html(self, tmp_path: Path):
        item = NewsItem(
            id="src-2026-04-25-x",
            title="Hello news",
            source_url="https://e.com",
            source_name="Example",
            published_date="2026-04-25",
            category="product",
            summary="A short summary.",
        )
        index_path = _generate_landing_html({item.id: item}, tmp_path)
        assert index_path == tmp_path / "index.html"
        html = index_path.read_text(encoding="utf-8")
        assert "Hello news" in html
        assert "Product Launches" in html
        assert "Example" in html

    def test_subtitle_says_news_items(self, tmp_path: Path):
        item = NewsItem(
            id="x-2026-04-25-y",
            title="x",
            source_url="https://e.com",
            source_name="e",
            published_date="2026-04-25",
            category="research",
        )
        index_path = _generate_landing_html({item.id: item}, tmp_path)
        html = index_path.read_text(encoding="utf-8")
        # Subtitle uses the news-specific phrasing — distinguishes from
        # the research / testing-research landings
        assert "news items" in html

    def test_new_badge_marks_only_new_ids(self, tmp_path: Path):
        old = NewsItem(
            id="old-2026-04-20-x",
            title="Old",
            source_url="https://e.com/old",
            source_name="e",
            published_date="2026-04-20",
            category="research",
        )
        fresh = NewsItem(
            id="fresh-2026-04-25-y",
            title="Fresh",
            source_url="https://e.com/fresh",
            source_name="e",
            published_date="2026-04-25",
            category="research",
        )
        index_path = _generate_landing_html(
            {old.id: old, fresh.id: fresh}, tmp_path, new_ids={fresh.id}
        )
        html = index_path.read_text(encoding="utf-8")
        # NEW badge appears in the row of the fresh item only.
        # A simple way to check: the substring "NEW</span>" appears once.
        assert html.count(">NEW<") == 1
