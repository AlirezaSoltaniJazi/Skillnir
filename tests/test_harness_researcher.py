"""Tests for skillnir.harness_researcher -- topic catalog, dedup, parser."""

from pathlib import Path

from skillnir.harness_researcher import (
    Article,
    PREFERRED_SOURCES,
    RESEARCH_TOPICS,
    SOURCE_DOMAINS,
    SOURCE_FILTERS,
    TOPIC_LABELS,
    _dict_to_article,
    _generate_landing_html,
    _load_index,
    _parse_articles_json,
    _save_index,
    _try_parse_json_array,
    _write_article_md,
)


class TestTopicCatalog:
    def test_topic_keys_match_search_query_count(self):
        assert len(TOPIC_LABELS) == len(RESEARCH_TOPICS)

    def test_has_14_topics(self):
        assert len(TOPIC_LABELS) == 14

    def test_known_topics_present(self):
        for key in (
            "agent-loops",
            "tool-use",
            "context-engineering",
            "multi-agent",
            "evals",
        ):
            assert key in TOPIC_LABELS

    def test_topic_labels_are_human_readable(self):
        for value in TOPIC_LABELS.values():
            assert value
            assert value[0].isupper()


class TestSourceCatalog:
    def test_preferred_sources_nonempty(self):
        assert len(PREFERRED_SOURCES) >= 25

    def test_source_filters_have_domain_mappings(self):
        for key in SOURCE_FILTERS:
            assert key in SOURCE_DOMAINS, f"filter {key!r} has no domain mapping"

    def test_filter_domains_are_subset_of_preferred(self):
        for key, domains in SOURCE_DOMAINS.items():
            for domain in domains:
                assert (
                    domain in PREFERRED_SOURCES
                ), f"{key}->{domain} not in PREFERRED_SOURCES"


class TestDictToArticle:
    def test_minimal_valid_dict_becomes_article(self):
        item = {
            "id": "anthropic-2026-04-19",
            "title": "Building effective agents",
            "source_url": "https://anthropic.com/x",
            "source_name": "Anthropic",
            "published_date": "2026-04-19",
            "key_insights": ["use simple loops"],
            "summary": "words",
        }
        article = _dict_to_article(item, "agent-loops")
        assert article is not None
        assert article.topic == "agent-loops"
        assert article.title == "Building effective agents"

    def test_missing_required_fields_returns_none(self):
        assert _dict_to_article({"title": "no id or url"}, "evals") is None

    def test_non_dict_returns_none(self):
        assert _dict_to_article("not a dict", "evals") is None


class TestParseArticlesJson:
    def test_parses_fenced_json_block(self):
        text = """Here you go:
```json
[
  {
    "id": "openai-2026-01-02",
    "title": "Function calling deep dive",
    "source_url": "https://openai.com/x",
    "source_name": "OpenAI",
    "published_date": "2026-01-02",
    "key_insights": ["parallel tool calls"],
    "summary": "summary text"
  }
]
```
"""
        articles = _parse_articles_json(text, "tool-use")
        assert len(articles) == 1
        assert articles[0].id == "openai-2026-01-02"
        assert articles[0].topic == "tool-use"

    def test_parses_inline_array(self):
        text = (
            '[{"id":"x-2026-01-01","title":"T","source_url":"https://e.com",'
            '"source_name":"E","published_date":"2026-01-01",'
            '"key_insights":["k"],"summary":"s"}]'
        )
        articles = _parse_articles_json(text, "memory-rag")
        assert len(articles) == 1
        assert articles[0].topic == "memory-rag"

    def test_returns_empty_when_no_json(self):
        assert _parse_articles_json("no json here", "evals") == []

    def test_try_parse_rejects_non_list(self):
        assert _try_parse_json_array('{"id": "x"}', "evals") == []


class TestIndexRoundTrip:
    def test_save_then_load(self, tmp_path: Path):
        article = Article(
            id="test-2026-04-19",
            title="Test article",
            source_url="https://example.com",
            source_name="Example",
            published_date="2026-04-19",
            topic="agent-loops",
            key_insights=["insight 1"],
            summary="summary",
        )
        _save_index(tmp_path, {article.id: article})
        loaded = _load_index(tmp_path)
        assert article.id in loaded
        assert loaded[article.id].title == "Test article"
        assert loaded[article.id].topic == "agent-loops"

    def test_save_uses_harness_research_index_filename(self, tmp_path: Path):
        article = Article(
            id="x-2026-04-19",
            title="x",
            source_url="https://x.com",
            source_name="x",
            published_date="2026-04-19",
            topic="agent-loops",
        )
        _save_index(tmp_path, {article.id: article})
        # Critical: must NOT collide with sibling index filenames
        assert (tmp_path / "harness-research-index.json").exists()
        assert not (tmp_path / "research-index.json").exists()
        assert not (tmp_path / "software-research-index.json").exists()
        assert not (tmp_path / "testing-research-index.json").exists()

    def test_load_returns_empty_when_missing(self, tmp_path: Path):
        assert _load_index(tmp_path) == {}

    def test_load_handles_corrupt_json(self, tmp_path: Path):
        (tmp_path / "harness-research-index.json").write_text(
            "not valid json", encoding="utf-8"
        )
        assert _load_index(tmp_path) == {}


class TestArticleMD:
    def test_writes_md_under_topic_subdir(self, tmp_path: Path):
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        article = Article(
            id="test-2026-04-19",
            title="Test",
            source_url="https://example.com",
            source_name="Example",
            published_date="2026-04-19",
            topic="context-engineering",
            key_insights=["a", "b"],
            summary="paragraph 1\n\nparagraph 2",
        )
        md_path = _write_article_md(article, articles_dir)
        assert md_path.parent.name == "context-engineering"
        text = md_path.read_text(encoding="utf-8")
        assert "Test" in text
        assert "https://example.com" in text


class TestLandingPage:
    def test_generates_index_html(self, tmp_path: Path):
        article = Article(
            id="src-2026-04-19",
            title="Hello",
            source_url="https://e.com",
            source_name="Example",
            published_date="2026-04-19",
            topic="multi-agent",
            key_insights=["something specific"],
            summary="words",
        )
        index_path = _generate_landing_html({article.id: article}, tmp_path)
        assert index_path == tmp_path / "index.html"
        html = index_path.read_text(encoding="utf-8")
        assert "Hello" in html
        assert "multi-agent" in html

    def test_subtitle_says_harness_engineering_articles(self, tmp_path: Path):
        article = Article(
            id="x-2026-04-19",
            title="x",
            source_url="https://e.com",
            source_name="e",
            published_date="2026-04-19",
            topic="agent-loops",
        )
        index_path = _generate_landing_html({article.id: article}, tmp_path)
        html = index_path.read_text(encoding="utf-8")
        # Verify the subtitle distinguishes this from sibling landings
        assert "harness-engineering articles" in html
