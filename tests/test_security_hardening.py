"""Regression tests for the 2026-10-25 security audit fixes.

Generated pages and file names are built from AI output that was itself
built from arbitrary web pages, so every test feeds attacker-shaped values.
"""

# The tests parametrize over the pipeline modules and call their private
# parse/render helpers by attribute — intended white-box testing.
# pylint: disable=protected-access

import dataclasses
import html
import json
import re
import sys
from pathlib import Path

import pytest

from skillnir import (
    benchmarks,
    events,
    harness_researcher,
    news,
    package_vulns,
    researcher,
    security,
    software_researcher,
    testing_researcher,
)
from skillnir.backends import RESEARCH_CLAUDE_TOOLS
from skillnir.crypto import write_private_text
from skillnir.hooks import disable_sound_hooks, enable_sound_hooks, remove_all_hooks
from skillnir.html_safety import is_safe_id, onclick_open, safe_url

XSS = '<img src=x onerror="alert(1)">'
TRAVERSAL_ID = "../../../../.claude/agents/pwn"


def _onclick_targets(page: str) -> list[str]:
    """Return the decoded JS of every ``onclick`` attribute in *page*."""
    return [html.unescape(m) for m in re.findall(r'onclick="([^"]*)"', page)]


class TestHtmlSafetyHelpers:
    @pytest.mark.parametrize(
        "value",
        ["openai-2026-04-25-gpt-5.3", "cve-2026-1234", "A1_b-2.c"],
    )
    def test_accepts_slug_ids(self, value):
        assert is_safe_id(value)

    @pytest.mark.parametrize(
        "value",
        [TRAVERSAL_ID, "..", ".hidden", "a/b", "a\\b", "", "x" * 200, "a b"],
    )
    def test_rejects_path_like_ids(self, value):
        assert not is_safe_id(value)

    @pytest.mark.parametrize("url", ["https://e.com/a?b=1", "http://e.com"])
    def test_keeps_web_urls(self, url):
        assert safe_url(url) == url

    @pytest.mark.parametrize(
        "url",
        [
            "javascript:alert(1)",
            "JaVaScRiPt:alert(1)",
            " \x01javascript:alert(1)",
            "java\tscript:alert(1)",
            "data:text/html,<script>alert(1)</script>",
            "vbscript:x",
        ],
    )
    def test_blocks_script_urls(self, url):
        assert safe_url(url) == "#"

    def test_onclick_target_cannot_break_out_of_js_string(self):
        target = "https://e.com/x');alert(1);//\"<"
        decoded = html.unescape(onclick_open(target))
        assert decoded == f"window.open({json.dumps(target)},'_blank')"


@pytest.mark.parametrize(
    ("parse", "item"),
    [
        (
            lambda d: researcher._dict_to_article(d, "mcp"),
            {"title": "t", "source_url": "https://e.com"},
        ),
        (
            lambda d: harness_researcher._dict_to_article(d, "mcp"),
            {"title": "t", "source_url": "https://e.com"},
        ),
        (
            lambda d: testing_researcher._dict_to_article(d, "mcp"),
            {"title": "t", "source_url": "https://e.com"},
        ),
        (
            lambda d: software_researcher._dict_to_article(d, "mcp"),
            {"title": "t", "source_url": "https://e.com"},
        ),
        (
            lambda d: news._dict_to_news_item(d, "product"),
            {"title": "t", "source_url": "https://e.com"},
        ),
        (
            lambda d: events._dict_to_event(d, "de"),
            {"title": "t", "event_url": "https://e.com"},
        ),
    ],
)
class TestAiIdsCannotEscapeStore:
    def test_traversal_id_is_dropped(self, parse, item):
        assert parse({**item, "id": TRAVERSAL_ID}) is None

    def test_slug_id_is_kept(self, parse, item):
        assert parse({**item, "id": "src-2026-10-25-ok"}) is not None


class TestGeneratedPagesEscapeAiFields:
    def test_research_landing_escapes_published_date(self, tmp_path: Path):
        a = researcher.Article(
            id="src-2026-10-25-x",
            title="t",
            source_url="https://e.com",
            source_name="s",
            published_date=XSS,
            topic="mcp",
        )
        page = researcher._generate_landing_html({a.id: a}, tmp_path).read_text(
            encoding="utf-8"
        )
        assert XSS not in page
        assert html.escape(XSS) in page

    def test_research_article_page_blocks_script_source_link(self):
        a = researcher.Article(
            id="src-2026-10-25-x",
            title="t",
            source_url="javascript:alert(1)",
            source_name="s",
            published_date=XSS,
            topic="mcp",
        )
        page = researcher._generate_article_html(a)
        assert "javascript:" not in page
        assert XSS not in page

    def test_news_row_link_cannot_inject_script(self, tmp_path: Path):
        breakout = news.NewsItem(
            id="src-2026-10-25-a",
            title="t",
            source_url="https://e.com/');alert(1);//",
            source_name="s",
            published_date=XSS,
            category="product",
        )
        scheme = news.NewsItem(
            id="src-2026-10-25-b",
            title="t",
            source_url="javascript:alert(1)",
            source_name="s",
            published_date="2026-10-25",
            category="product",
        )
        page = news._generate_landing_html(
            {breakout.id: breakout, scheme.id: scheme}, tmp_path
        ).read_text(encoding="utf-8")
        assert XSS not in page
        row_targets = [t for t in _onclick_targets(page) if t.startswith("window.open")]
        assert f"window.open({json.dumps(breakout.source_url)},'_blank')" in row_targets
        assert "window.open(\"#\",'_blank')" in row_targets
        assert not any("javascript:" in t for t in row_targets)

    def test_security_row_escapes_source_name_and_link(self, tmp_path: Path):
        v = security.Vulnerability(
            id="cve-2026-1",
            title="t",
            source_url="javascript:alert(1)",
            source_name=f'x" onmouseover="alert(1)',
            published_date=XSS,
            category="cve-critical",
            severity="high",
            cvss_score=9.8,
        )
        page = security._generate_landing_html({v.id: v}, tmp_path).read_text(
            encoding="utf-8"
        )
        assert XSS not in page
        assert 'onmouseover="alert(1)' not in page
        assert not any("javascript:" in t for t in _onclick_targets(page))


class TestResearchToolGrant:
    def test_research_pipelines_get_no_shell_or_file_tools(self):
        granted = set(RESEARCH_CLAUDE_TOOLS.split(","))
        assert granted == {"WebFetch", "WebSearch"}


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX permission bits")
class TestPrivateFiles:
    def test_file_and_parent_are_owner_only(self, tmp_path: Path):
        target = tmp_path / "store" / "config.json"
        write_private_text(target, "{}\n")
        assert target.read_text(encoding="utf-8") == "{}\n"
        assert target.stat().st_mode & 0o777 == 0o600
        assert target.parent.stat().st_mode & 0o777 == 0o700

    def test_tightens_existing_parent_and_leaves_no_temp_files(self, tmp_path: Path):
        store = tmp_path / "store"
        store.mkdir(mode=0o755)
        store.chmod(0o755)
        write_private_text(store / "client_id", "abc\n")
        write_private_text(store / "client_id", "def\n")
        assert store.stat().st_mode & 0o777 == 0o700
        assert [p.name for p in store.iterdir()] == ["client_id"]
        assert (store / "client_id").read_text(encoding="utf-8") == "def\n"


class TestBrokenClaudeSettingsAreNotOverwritten:
    BROKEN = '{"permissions": {"deny": ["Bash(rm:*)"]},'  # truncated JSON

    @pytest.mark.parametrize(
        "action", [enable_sound_hooks, disable_sound_hooks, remove_all_hooks]
    )
    def test_refuses_and_keeps_file(self, tmp_path: Path, action):
        settings = tmp_path / "settings.json"
        settings.write_text(self.BROKEN, encoding="utf-8")
        error = action(settings)
        assert error and "not valid JSON" in error
        assert settings.read_text(encoding="utf-8") == self.BROKEN

    def test_non_object_json_is_refused(self, tmp_path: Path):
        settings = tmp_path / "settings.json"
        settings.write_text("[]", encoding="utf-8")
        assert enable_sound_hooks(settings)
        assert settings.read_text(encoding="utf-8") == "[]"

    def test_valid_settings_keep_other_keys(self, tmp_path: Path):
        settings = tmp_path / "settings.json"
        settings.write_text(json.dumps({"permissions": {"deny": ["x"]}}), "utf-8")
        assert enable_sound_hooks(settings) is None
        data = json.loads(settings.read_text(encoding="utf-8"))
        assert data["permissions"] == {"deny": ["x"]}
        assert "hooks" in data


# Fields each pipeline's parser forces onto an allow-list, so real records
# only ever carry these known keys there.
_ALLOW_LISTED = {
    "topic": lambda mod: next(
        iter(getattr(mod, "TOPIC_LABELS", researcher.TOPIC_LABELS))
    ),
    "category": lambda mod: next(
        iter(getattr(mod, "NEWS_CATEGORIES", None) or security.SECURITY_CATEGORIES)
    ),
    "severity": lambda mod: "high",
    "ecosystem": lambda mod: next(iter(package_vulns.ECOSYSTEMS)),
    "provider": lambda mod: next(iter(benchmarks.PROVIDER_LABELS)),
    "country": lambda mod: next(iter(events.EVENT_COUNTRIES)),
    "status": lambda mod: "active",
}
# Combines a scheme attack, a JS-string breakout and a tag injection.
_URL_PAYLOAD = f"javascript:alert(1)//');alert(2);//{XSS}"


def _hostile_record(mod, cls, record_id: str):
    """Build *cls* with every free-text field set to an injection payload."""
    values = {}
    for f in dataclasses.fields(cls):
        if f.name == "id":
            values[f.name] = record_id
        elif f.name in _ALLOW_LISTED:
            values[f.name] = _ALLOW_LISTED[f.name](mod)
        elif f.type is str:
            values[f.name] = _URL_PAYLOAD if "url" in f.name else XSS
        elif f.type == list[str]:
            values[f.name] = [_URL_PAYLOAD if "url" in f.name else XSS]
        elif f.type is bool:
            values[f.name] = False
        elif f.type in (int, float):
            values[f.name] = 7
        else:
            values[f.name] = {}
    return cls(**values)


_PAGE_BUILDERS = [
    (researcher, researcher.Article),
    (harness_researcher, harness_researcher.Article),
    (testing_researcher, testing_researcher.Article),
    (software_researcher, software_researcher.Article),
    (news, news.NewsItem),
    (events, events.Event),
    (security, security.Vulnerability),
    (package_vulns, package_vulns.PackageVulnerability),
    (benchmarks, benchmarks.AIModel),
]


def _assert_inert(page: str) -> None:
    assert XSS not in page
    for js in _onclick_targets(page):
        assert "javascript:" not in js
        assert "alert(2)" not in js.replace(json.dumps(_URL_PAYLOAD), "")
    for link in re.findall(r'href="([^"]*)"', page):
        assert not html.unescape(link).lower().startswith("javascript:")


@pytest.mark.parametrize(
    ("mod", "cls"), _PAGE_BUILDERS, ids=[m.__name__ for m, _ in _PAGE_BUILDERS]
)
class TestEveryPageEscapesEveryField:
    def test_landing_page(self, tmp_path: Path, mod, cls):
        records = {"rec-1": _hostile_record(mod, cls, "rec-1")}
        if cls in (
            researcher.Article,
            harness_researcher.Article,
            testing_researcher.Article,
            software_researcher.Article,
        ):
            outdated = _hostile_record(mod, cls, "rec-2")
            outdated.status = "outdated"
            records["rec-2"] = outdated
        page = mod._generate_landing_html(records, tmp_path).read_text(encoding="utf-8")
        _assert_inert(page)

    def test_detail_page(self, mod, cls):
        builder = getattr(mod, "_generate_article_html", None) or getattr(
            mod, "_generate_event_html", None
        )
        if builder is None:
            pytest.skip("pipeline has no per-record page")
        _assert_inert(builder(_hostile_record(mod, cls, "rec-1")))
