"""Tests for skillnir.article_cleanup + status-aware researcher behavior."""

# The store-behavior tests parametrize over the three researcher modules and
# call their private index helpers by attribute — intended white-box testing.
# pylint: disable=protected-access

import json
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir import researcher, software_researcher, testing_researcher
from skillnir.article_cleanup import (
    CONFIDENCE_THRESHOLD,
    REPORT_JSON,
    REPORT_MD,
    STORE_SPECS,
    CleanupResult,
    _parse_verdicts,
    _to_candidates,
    cleanup_articles,
    move_article_to_outdated,
    select_articles,
    write_cleanup_report,
)
from skillnir.article_status import (
    STATUS_OUTDATED,
    article_dir,
    is_outdated,
    split_by_status,
)


def _article(module, article_id="src-2025-01-01", topic=None, **kwargs):
    """Build an Article for any researcher module."""
    topic = topic or next(iter(module.TOPIC_LABELS))
    defaults = {
        "id": article_id,
        "title": f"Title {article_id}",
        "source_url": "https://example.com/a",
        "source_name": "Example",
        "published_date": "2025-01-01",
        "topic": topic,
        "key_insights": ["insight one"],
        "summary": "A summary.\n\nSecond paragraph.",
    }
    defaults.update(kwargs)
    return module.Article(**defaults)


# ── StoreSpec registry ───────────────────────────────────────


class TestStoreSpecs:
    def test_three_stores_registered(self):
        assert set(STORE_SPECS) == {
            "research",
            "software-research",
            "testing-research",
        }

    def test_index_filenames(self):
        assert STORE_SPECS["research"].index_filename == "research-index.json"
        assert (
            STORE_SPECS["software-research"].index_filename
            == "software-research-index.json"
        )
        assert (
            STORE_SPECS["testing-research"].index_filename
            == "testing-research-index.json"
        )

    def test_topic_labels_wired_to_modules(self):
        assert STORE_SPECS["research"].topic_labels is researcher.TOPIC_LABELS
        assert (
            STORE_SPECS["software-research"].topic_labels
            is software_researcher.TOPIC_LABELS
        )

    def test_only_research_store_has_migration(self):
        assert STORE_SPECS["research"].migrate is not None
        assert STORE_SPECS["software-research"].migrate is None
        assert STORE_SPECS["testing-research"].migrate is None


# ── select_articles ──────────────────────────────────────────


class TestSelectArticles:
    def _articles(self):
        a1 = _article(researcher, "a-2024-01-01", published_date="2024-01-01")
        a2 = _article(researcher, "b-2025-06-01", published_date="2025-06-01")
        a3 = _article(
            researcher,
            "c-2023-01-01",
            published_date="2023-01-01",
            status=STATUS_OUTDATED,
        )
        a4 = _article(
            researcher, "d-2025-01-01", published_date="2025-01-01", topic="mcp"
        )
        return {a.id: a for a in (a1, a2, a3, a4)}

    def test_excludes_outdated(self):
        selected = select_articles(self._articles())
        assert all(a.status != STATUS_OUTDATED for a in selected)

    def test_topic_filter(self):
        selected = select_articles(self._articles(), topics=["mcp"])
        assert [a.id for a in selected] == ["d-2025-01-01"]

    def test_older_than_boundary_is_exclusive(self):
        selected = select_articles(self._articles(), older_than="2025-01-01")
        assert "d-2025-01-01" not in {a.id for a in selected}
        assert "a-2024-01-01" in {a.id for a in selected}

    def test_oldest_first_and_capped(self):
        selected = select_articles(self._articles(), max_articles=2)
        assert [a.id for a in selected] == ["a-2024-01-01", "d-2025-01-01"]


# ── verdict parsing ──────────────────────────────────────────


class TestParseVerdicts:
    def test_bare_array(self):
        text = '[{"id": "x", "verdict": "valid", "confidence": 0.1}]'
        assert _parse_verdicts(text)[0]["id"] == "x"

    def test_fenced_block(self):
        text = 'Sure!\n```json\n[{"id": "x", "verdict": "outdated"}]\n```\nDone.'
        assert _parse_verdicts(text)[0]["verdict"] == "outdated"

    def test_prose_wrapped_array(self):
        text = 'Here are results: [{"id": "x", "verdict": "valid"}] hope it helps'
        assert _parse_verdicts(text)[0]["id"] == "x"

    def test_garbage_returns_empty(self):
        assert _parse_verdicts("no json here at all") == []

    def test_non_dict_items_dropped(self):
        assert _parse_verdicts('["just", "strings"]') == []

    def test_duplicated_array_parses(self):
        """Stream text + result_text can repeat the payload back-to-back."""
        array = '[{"id": "x", "verdict": "valid", "confidence": 0.1}]'
        assert _parse_verdicts(array + array)[0]["id"] == "x"


# ── candidate conversion / conservative threshold ───────────


class TestToCandidates:
    def _by_id(self):
        a = _article(researcher, "known-2025-01-01")
        return {a.id: a}

    def test_threshold_boundary(self):
        items = [
            {
                "id": "known-2025-01-01",
                "verdict": "outdated",
                "reason": "r",
                "confidence": 0.79,
            }
        ]
        c = _to_candidates(items, self._by_id())[0]
        assert c.confidence < CONFIDENCE_THRESHOLD  # lands in low_confidence

        items[0]["confidence"] = 0.8
        c = _to_candidates(items, self._by_id())[0]
        assert c.confidence >= CONFIDENCE_THRESHOLD

    def test_valid_verdict_kept_as_valid(self):
        items = [{"id": "known-2025-01-01", "verdict": "VALID", "confidence": 0.9}]
        assert _to_candidates(items, self._by_id())[0].verdict == "valid"

    def test_unknown_id_dropped(self):
        items = [{"id": "ghost", "verdict": "outdated", "confidence": 1.0}]
        assert _to_candidates(items, self._by_id()) == []

    def test_bad_confidence_clamped(self):
        by_id = self._by_id()
        for raw, expected in (("high", 0.0), (1.7, 1.0), (-1, 0.0)):
            items = [
                {"id": "known-2025-01-01", "verdict": "outdated", "confidence": raw}
            ]
            assert _to_candidates(items, by_id)[0].confidence == expected

    def test_duplicate_ids_deduped(self):
        items = [
            {"id": "known-2025-01-01", "verdict": "valid", "confidence": 0.0},
            {"id": "known-2025-01-01", "verdict": "outdated", "confidence": 0.9},
        ]
        result = _to_candidates(items, self._by_id())
        assert len(result) == 1
        assert result[0].verdict == "outdated"


# ── mover ────────────────────────────────────────────────────


class TestMoveArticleToOutdated:
    def _seed(self, tmp_path: Path) -> Path:
        articles_dir = tmp_path / "articles"
        topic_dir = articles_dir / "mcp"
        topic_dir.mkdir(parents=True)
        (topic_dir / "a-1.md").write_text("md")
        (topic_dir / "a-1.html").write_text("html")
        return articles_dir

    def test_moves_pair_into_outdated(self, tmp_path: Path):
        articles_dir = self._seed(tmp_path)
        moved, err = move_article_to_outdated("a-1", "mcp", articles_dir)
        assert err is None
        assert moved == 2
        assert (articles_dir / "mcp" / "outdated" / "a-1.md").is_file()
        assert (articles_dir / "mcp" / "outdated" / "a-1.html").is_file()
        assert not (articles_dir / "mcp" / "a-1.md").exists()

    def test_second_call_is_noop(self, tmp_path: Path):
        articles_dir = self._seed(tmp_path)
        move_article_to_outdated("a-1", "mcp", articles_dir)
        moved, err = move_article_to_outdated("a-1", "mcp", articles_dir)
        assert (moved, err) == (0, None)

    def test_missing_html_tolerated(self, tmp_path: Path):
        articles_dir = self._seed(tmp_path)
        (articles_dir / "mcp" / "a-1.html").unlink()
        moved, err = move_article_to_outdated("a-1", "mcp", articles_dir)
        assert err is None
        assert moved == 1

    def test_existing_destination_never_overwritten(self, tmp_path: Path):
        articles_dir = self._seed(tmp_path)
        outdated = articles_dir / "mcp" / "outdated"
        outdated.mkdir()
        (outdated / "a-1.md").write_text("already archived")
        move_article_to_outdated("a-1", "mcp", articles_dir)
        assert (outdated / "a-1.md").read_text() == "already archived"

    def test_oserror_returned_as_string(self, tmp_path: Path):
        articles_dir = self._seed(tmp_path)
        with patch.object(Path, "rename", side_effect=OSError("disk full")):
            moved, err = move_article_to_outdated("a-1", "mcp", articles_dir)
        assert "disk full" in err


# ── report ───────────────────────────────────────────────────


class TestWriteCleanupReport:
    def test_writes_md_and_json(self, tmp_path: Path):
        spec = STORE_SPECS["research"]
        result = CleanupResult(success=True, store="research", mode="report")
        md, js = write_cleanup_report(tmp_path, spec, result)
        assert md == tmp_path / REPORT_MD and md.is_file()
        assert js == tmp_path / REPORT_JSON and js.is_file()
        payload = json.loads(js.read_text())
        assert payload["store"] == "research"
        assert payload["confidence_threshold"] == CONFIDENCE_THRESHOLD


# ── orchestrator (classification mocked) ─────────────────────


def _temp_spec(tmp_path: Path):
    """A research StoreSpec pointing at a temp dir."""
    spec = STORE_SPECS["research"]
    return replace(spec, get_dir=lambda: tmp_path, migrate=None)


def _seed_store(tmp_path: Path, articles: dict) -> None:
    researcher._save_index(tmp_path, articles)
    for a in articles.values():
        topic_dir = article_dir(tmp_path / "articles", a.topic, a.status)
        topic_dir.mkdir(parents=True, exist_ok=True)
        (topic_dir / f"{a.id}.md").write_text("md")
        (topic_dir / f"{a.id}.html").write_text("html")


class TestCleanupArticlesOrchestration:
    def test_unknown_store_is_error_result(self):
        import asyncio

        result = asyncio.run(cleanup_articles("nope"))
        assert result.success is False
        assert "Unknown store" in result.error

    def test_unknown_mode_is_error_result(self):
        import asyncio

        result = asyncio.run(cleanup_articles("research", mode="destroy"))
        assert result.success is False
        assert "Unknown mode" in result.error

    @pytest.mark.asyncio
    async def test_report_mode_moves_nothing(self, tmp_path: Path):
        a = _article(researcher, "old-2024-01-01", topic="mcp")
        _seed_store(tmp_path, {a.id: a})
        index_before = (tmp_path / "research-index.json").read_bytes()

        verdicts = [
            {
                "id": a.id,
                "verdict": "outdated",
                "reason": "superseded",
                "confidence": 0.95,
            }
        ]
        with (
            patch.dict(STORE_SPECS, {"research": _temp_spec(tmp_path)}),
            patch(
                "skillnir.article_cleanup._classify_batch_subprocess",
                return_value=(verdicts, None),
            ),
            patch("skillnir.article_cleanup.shutil.which", return_value="/bin/x"),
        ):
            result = await cleanup_articles("research", mode="report")

        assert result.success is True
        assert len(result.candidates) == 1
        assert result.moved == 0
        assert (tmp_path / "articles" / "mcp" / f"{a.id}.md").exists()
        assert (tmp_path / "research-index.json").read_bytes() == index_before
        assert result.report_md_path.is_file()

    @pytest.mark.asyncio
    async def test_apply_mode_moves_and_updates_index(self, tmp_path: Path):
        a = _article(researcher, "old-2024-01-01", topic="mcp")
        keep = _article(researcher, "new-2026-01-01", published_date="2026-01-01")
        _seed_store(tmp_path, {a.id: a, keep.id: keep})

        verdicts = [
            {
                "id": a.id,
                "verdict": "outdated",
                "reason": "superseded by v2 spec",
                "confidence": 0.9,
            },
            {"id": keep.id, "verdict": "valid", "confidence": 0.0},
        ]
        with (
            patch.dict(STORE_SPECS, {"research": _temp_spec(tmp_path)}),
            patch(
                "skillnir.article_cleanup._classify_batch_subprocess",
                return_value=(verdicts, None),
            ),
            patch("skillnir.article_cleanup.shutil.which", return_value="/bin/x"),
        ):
            result = await cleanup_articles("research", mode="apply")

        assert result.success is True
        assert result.moved == 2
        assert (tmp_path / "articles" / "mcp" / "outdated" / f"{a.id}.md").is_file()

        reloaded = researcher._load_index(tmp_path)
        assert reloaded[a.id].status == STATUS_OUTDATED
        assert reloaded[a.id].outdated_reason == "superseded by v2 spec"
        assert reloaded[a.id].outdated_at
        assert reloaded[keep.id].status == "active"
        # Dedup skip-list still contains the outdated id
        assert a.id in set(reloaded.keys())
        # Landing regenerated with outdated section
        landing = (tmp_path / "index.html").read_text()
        assert "outdated-section" in landing

    @pytest.mark.asyncio
    async def test_low_confidence_never_moved(self, tmp_path: Path):
        a = _article(researcher, "old-2024-01-01", topic="mcp")
        _seed_store(tmp_path, {a.id: a})
        verdicts = [
            {"id": a.id, "verdict": "outdated", "reason": "meh", "confidence": 0.5}
        ]
        with (
            patch.dict(STORE_SPECS, {"research": _temp_spec(tmp_path)}),
            patch(
                "skillnir.article_cleanup._classify_batch_subprocess",
                return_value=(verdicts, None),
            ),
            patch("skillnir.article_cleanup.shutil.which", return_value="/bin/x"),
        ):
            result = await cleanup_articles("research", mode="apply")

        assert result.success is True
        assert result.candidates == []
        assert len(result.low_confidence) == 1
        assert result.moved == 0
        assert (tmp_path / "articles" / "mcp" / f"{a.id}.md").exists()

    @pytest.mark.asyncio
    async def test_batching_math(self, tmp_path: Path):
        articles = {}
        for i in range(60):
            a = _article(
                researcher,
                f"a{i:03d}-2024-01-01",
                published_date=f"2024-01-{(i % 28) + 1:02d}",
            )
            articles[a.id] = a
        _seed_store(tmp_path, articles)

        calls = []

        def fake_classify(payload, *args, **kwargs):
            calls.append(len(json.loads(payload)))
            return [], None

        with (
            patch.dict(STORE_SPECS, {"research": _temp_spec(tmp_path)}),
            patch(
                "skillnir.article_cleanup._classify_batch_subprocess",
                side_effect=fake_classify,
            ),
            patch("skillnir.article_cleanup.shutil.which", return_value="/bin/x"),
        ):
            result = await cleanup_articles("research", max_articles=60)

        assert result.batches == 3
        assert calls == [25, 25, 10]

    @pytest.mark.asyncio
    async def test_all_batches_failing_is_failure(self, tmp_path: Path):
        a = _article(researcher, "old-2024-01-01")
        _seed_store(tmp_path, {a.id: a})
        with (
            patch.dict(STORE_SPECS, {"research": _temp_spec(tmp_path)}),
            patch(
                "skillnir.article_cleanup._classify_batch_subprocess",
                return_value=([], "boom"),
            ),
            patch("skillnir.article_cleanup.shutil.which", return_value="/bin/x"),
        ):
            result = await cleanup_articles("research")
        assert result.success is False


# ── status-aware store behavior (parametrized over modules) ──


@pytest.fixture(params=[researcher, software_researcher, testing_researcher])
def store_module(request):
    return request.param


class TestIndexStatusRoundTrip:
    def test_new_fields_survive_save_load(self, store_module, tmp_path: Path):
        a = _article(
            store_module,
            status=STATUS_OUTDATED,
            outdated_reason="superseded",
            outdated_at="2026-07-04",
        )
        store_module._save_index(tmp_path, {a.id: a})
        reloaded = store_module._load_index(tmp_path)
        assert reloaded[a.id].status == STATUS_OUTDATED
        assert reloaded[a.id].outdated_reason == "superseded"
        assert reloaded[a.id].outdated_at == "2026-07-04"


class TestLoadIndexBackCompat:
    def test_legacy_entries_default_to_active(self, store_module, tmp_path: Path):
        legacy = {
            "id": "old-2024-01-01",
            "title": "t",
            "source_url": "u",
            "source_name": "s",
            "published_date": "2024-01-01",
            "topic": next(iter(store_module.TOPIC_LABELS)),
            "key_insights": [],
            "summary": "",
        }
        index_file = tmp_path / STORE_SPECS_BY_MODULE[store_module.__name__]
        index_file.write_text(json.dumps([legacy]))
        reloaded = store_module._load_index(tmp_path)
        assert reloaded["old-2024-01-01"].status == "active"

    def test_unknown_extra_key_tolerated(self, store_module, tmp_path: Path):
        entry = {
            "id": "x-2024-01-01",
            "title": "t",
            "source_url": "u",
            "source_name": "s",
            "published_date": "2024-01-01",
            "topic": next(iter(store_module.TOPIC_LABELS)),
            "key_insights": [],
            "summary": "",
            "some_future_field": 42,
        }
        index_file = tmp_path / STORE_SPECS_BY_MODULE[store_module.__name__]
        index_file.write_text(json.dumps([entry]))
        reloaded = store_module._load_index(tmp_path)
        assert "x-2024-01-01" in reloaded


STORE_SPECS_BY_MODULE = {
    "skillnir.researcher": "research-index.json",
    "skillnir.software_researcher": "software-research-index.json",
    "skillnir.testing_researcher": "testing-research-index.json",
}


class TestLandingExcludesOutdated:
    def test_active_table_and_outdated_section(self, store_module, tmp_path: Path):
        topic = next(iter(store_module.TOPIC_LABELS))
        active1 = _article(store_module, "act-1-2025-01-01", topic=topic)
        active2 = _article(
            store_module, "act-2-2025-02-01", topic=topic, published_date="2025-02-01"
        )
        old = _article(
            store_module,
            "old-1-2024-01-01",
            topic=topic,
            published_date="2024-01-01",
            status=STATUS_OUTDATED,
            outdated_reason="tool <discontinued>",
            outdated_at="2026-07-04",
        )
        articles = {a.id: a for a in (active1, active2, old)}
        index_path = store_module._generate_landing_html(articles, tmp_path)
        page = index_path.read_text()

        assert page.count('class="row"') == 2
        assert "outdated-section" in page
        assert f"articles/{topic}/outdated/old-1-2024-01-01.html" in page
        assert "tool &lt;discontinued&gt;" in page  # reason escaped
        assert "const TOTAL_ARTICLES = 2;" in page

    def test_no_outdated_no_section(self, store_module, tmp_path: Path):
        a = _article(store_module)
        index_path = store_module._generate_landing_html({a.id: a}, tmp_path)
        assert "outdated-section" not in index_path.read_text()


class TestBackfillOutdatedDir:
    def test_html_healed_inside_outdated(self, store_module, tmp_path: Path):
        topic = next(iter(store_module.TOPIC_LABELS))
        a = _article(store_module, topic=topic, status=STATUS_OUTDATED)
        store_module._save_index(tmp_path, {a.id: a})
        outdated_dir = tmp_path / "articles" / topic / "outdated"
        outdated_dir.mkdir(parents=True)
        (outdated_dir / f"{a.id}.md").write_text("md only")

        created = store_module.backfill_article_html(tmp_path)
        assert created == 1
        assert (outdated_dir / f"{a.id}.html").is_file()
        assert not (tmp_path / "articles" / topic / f"{a.id}.html").exists()


class TestMigrationRespectsStatus:
    def test_flat_outdated_file_lands_in_outdated_dir(self, tmp_path: Path):
        a = _article(researcher, "flat-2024-01-01", topic="mcp", status=STATUS_OUTDATED)
        researcher._save_index(tmp_path, {a.id: a})
        articles_dir = tmp_path / "articles"
        articles_dir.mkdir()
        (articles_dir / f"{a.id}.md").write_text("flat file")

        moved = researcher._migrate_articles_to_topic_dirs(tmp_path)
        assert moved == 1
        assert (articles_dir / "mcp" / "outdated" / f"{a.id}.md").is_file()


class TestSplitByStatus:
    def test_split_and_order(self):
        a = _article(researcher, "a-2025-01-01")
        b = _article(
            researcher,
            "b-2026-01-01",
            published_date="2026-01-01",
            status=STATUS_OUTDATED,
        )
        active, outdated = split_by_status({a.id: a, b.id: b})
        assert [x.id for x in active] == ["a-2025-01-01"]
        assert [x.id for x in outdated] == ["b-2026-01-01"]

    def test_is_outdated_default(self):
        a = _article(researcher)
        assert is_outdated(a) is False
