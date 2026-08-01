"""Tests for skillnir.package_vulns — package-vulnerability intel pipeline."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.package_vulns import (
    ECOSYSTEMS,
    PackageVulnerability,
    PackageVulnsResult,
    _dict_to_pkgvuln,
    _generate_landing_html,
    _load_index,
    _normalize_ecosystem,
    _save_index,
    _try_parse_json_array,
    regenerate_landing,
    search_package_vulns,
)


def _item(**overrides) -> dict:
    base = {
        "id": "GHSA-abcd-1234-xyzq",
        "package_name": "axios",
        "ecosystem": "npm",
        "title": "SSRF in axios",
        "severity": "critical",
        "cvss_score": 9.1,
        "affected_versions": ">=1.0.0, <1.6.0",
        "fixed_version": "1.6.0",
        "cve_id": "CVE-2026-0001",
        "published_date": "2026-06-01",
        "advisory_url": "https://github.com/advisories/GHSA-abcd-1234-xyzq",
        "source_name": "GitHub Advisory DB",
        "summary": "Server-side request forgery.",
        "recommendation": "Upgrade to >= 1.6.0.",
    }
    base.update(overrides)
    return base


# ── JSON array extraction ─────────────────────────────────────


class TestTryParseJsonArray:
    def test_bare_array(self):
        assert _try_parse_json_array('[{"id": "x"}]')[0]["id"] == "x"

    def test_fenced_block(self):
        text = 'Here:\n```json\n[{"id": "x"}]\n```\n'
        assert _try_parse_json_array(text)[0]["id"] == "x"

    def test_prose_wrapped(self):
        text = 'Results: [{"id": "x"}] done'
        assert _try_parse_json_array(text)[0]["id"] == "x"

    def test_garbage_returns_empty(self):
        assert _try_parse_json_array("nothing here") == []

    def test_object_not_list_returns_empty(self):
        assert _try_parse_json_array('{"id": "x"}') == []


# ── dict → PackageVulnerability coercion ──────────────────────


class TestDictToPkgVuln:
    def test_full_item(self):
        v = _dict_to_pkgvuln(_item())
        assert v is not None
        assert v.package_name == "axios"
        assert v.fixed_version == "1.6.0"
        assert v.id == "ghsa-abcd-1234-xyzq"  # lowercased

    def test_missing_id_dropped(self):
        assert _dict_to_pkgvuln(_item(id="")) is None

    def test_missing_package_name_dropped(self):
        assert _dict_to_pkgvuln(_item(package_name="")) is None

    def test_unknown_ecosystem_defaults(self):
        assert _dict_to_pkgvuln(_item(ecosystem="cobol-registry")).ecosystem == "npm"

    def test_ecosystem_alias_mapped(self):
        assert _dict_to_pkgvuln(_item(ecosystem="pip")).ecosystem == "pypi"
        assert _dict_to_pkgvuln(_item(ecosystem="cargo")).ecosystem == "crates"

    def test_unknown_severity_defaults_medium(self):
        assert _dict_to_pkgvuln(_item(severity="apocalyptic")).severity == "medium"

    def test_non_numeric_cvss_zeroed(self):
        assert _dict_to_pkgvuln(_item(cvss_score="high")).cvss_score == 0.0

    def test_cvss_rounded(self):
        assert _dict_to_pkgvuln(_item(cvss_score=9.15)).cvss_score == 9.2

    def test_title_falls_back_to_package(self):
        assert _dict_to_pkgvuln(_item(title="")).title == "axios"


class TestNormalizeEcosystem:
    def test_canonical_passthrough(self):
        assert _normalize_ecosystem("npm") == "npm"

    def test_case_insensitive(self):
        assert _normalize_ecosystem("PyPI") == "pypi"

    def test_alias(self):
        assert _normalize_ecosystem("golang") == "go"

    def test_unknown_default(self):
        assert _normalize_ecosystem("zzz") == "npm"


# ── index round-trip ──────────────────────────────────────────


class TestIndexRoundTrip:
    def test_save_load_preserves_all_fields(self, tmp_path: Path):
        v = _dict_to_pkgvuln(_item())
        _save_index(tmp_path, {v.id: v})
        reloaded = _load_index(tmp_path)
        assert reloaded[v.id] == v

    def test_load_missing_returns_empty(self, tmp_path: Path):
        assert _load_index(tmp_path) == {}

    def test_load_tolerates_extra_keys(self, tmp_path: Path):
        entry = _item()
        entry["id"] = entry["id"].lower()
        entry["future_field"] = 123
        (tmp_path / "package-vulns-index.json").write_text(json.dumps([entry]))
        reloaded = _load_index(tmp_path)
        assert reloaded[entry["id"]].package_name == "axios"

    def test_load_skips_entries_without_id(self, tmp_path: Path):
        (tmp_path / "package-vulns-index.json").write_text(
            json.dumps([{"package_name": "x"}])
        )
        assert _load_index(tmp_path) == {}

    def test_save_sorts_critical_first(self, tmp_path: Path):
        crit = _dict_to_pkgvuln(_item(id="a", severity="critical"))
        low = _dict_to_pkgvuln(_item(id="b", severity="low"))
        _save_index(tmp_path, {crit.id: crit, low.id: low})
        data = json.loads((tmp_path / "package-vulns-index.json").read_text())
        assert data[0]["severity"] == "critical"


# ── landing page ──────────────────────────────────────────────


class TestLandingHtml:
    def test_rows_and_chips_rendered(self, tmp_path: Path):
        npm_v = _dict_to_pkgvuln(_item(id="a", ecosystem="npm"))
        py_v = _dict_to_pkgvuln(
            _item(id="b", ecosystem="pypi", package_name="requests")
        )
        vulns = {npm_v.id: npm_v, py_v.id: py_v}
        index_path = _generate_landing_html(vulns, tmp_path, {npm_v.id})
        page = index_path.read_text()

        assert page.count('class="row"') == 2
        assert "toggleEcosystem" in page
        assert 'data-ecosystem="npm"' in page
        assert 'data-ecosystem="pypi"' in page
        assert "1.6.0" in page  # fixed_version cell
        assert "&gt;=1.0.0, &lt;1.6.0" in page  # affected range, HTML-escaped
        assert "const TOTAL_VULNS = 2;" in page
        assert "NEW" in page  # new badge for npm_v

    def test_escapes_package_name(self, tmp_path: Path):
        v = _dict_to_pkgvuln(_item(package_name="pkg<script>"))
        page = _generate_landing_html({v.id: v}, tmp_path).read_text()
        # The injected package name must appear only in escaped form.
        assert "pkg&lt;script&gt;" in page
        assert "pkg<script>" not in page

    def test_regenerate_landing_empty_index(self, tmp_path: Path):
        count, path = regenerate_landing(tmp_path)
        assert count == 0 and path is None

    def test_regenerate_landing_with_data(self, tmp_path: Path):
        v = _dict_to_pkgvuln(_item())
        _save_index(tmp_path, {v.id: v})
        count, path = regenerate_landing(tmp_path)
        assert count == 1
        assert path is not None and path.exists()


# ── orchestrator (subprocess mocked) ──────────────────────────


class TestSearchPackageVulns:
    def test_missing_cli_returns_failure(self, tmp_path: Path):
        import asyncio

        with (
            patch("skillnir.package_vulns.shutil.which", return_value=None),
            patch(
                "skillnir.package_vulns._get_package_vulns_dir", return_value=tmp_path
            ),
        ):
            result = asyncio.run(search_package_vulns())
        assert isinstance(result, PackageVulnsResult)
        assert result.success is False
        assert "not found" in result.error

    @pytest.mark.asyncio
    async def test_new_and_updated_counts(self, tmp_path: Path):
        existing = _dict_to_pkgvuln(_item(id="ghsa-old", package_name="lodash"))
        _save_index(tmp_path, {existing.id: existing})

        fresh = _dict_to_pkgvuln(_item(id="ghsa-new", package_name="axios"))
        updated = _dict_to_pkgvuln(
            _item(id="ghsa-old", package_name="lodash", fixed_version="4.17.22")
        )

        with (
            patch("skillnir.package_vulns.shutil.which", return_value="/bin/claude"),
            patch(
                "skillnir.package_vulns._get_package_vulns_dir", return_value=tmp_path
            ),
            patch(
                "skillnir.package_vulns._search_package_vulns_subprocess",
                return_value=[fresh, updated],
            ),
        ):
            result = await search_package_vulns()

        assert result.success is True
        assert result.vulns_found == 2
        assert result.vulns_new == 1
        assert result.vulns_skipped == 1
        assert result.index_path is not None and result.index_path.exists()

        reloaded = _load_index(tmp_path)
        assert reloaded["ghsa-new"].package_name == "axios"
        assert reloaded["ghsa-old"].fixed_version == "4.17.22"  # updated in place


# ── constants sanity ──────────────────────────────────────────


class TestConstants:
    def test_ten_ecosystems(self):
        assert len(ECOSYSTEMS) == 10
        assert "npm" in ECOSYSTEMS and "pypi" in ECOSYSTEMS and "maven" in ECOSYSTEMS

    def test_dataclass_has_package_fields(self):
        names = {f for f in PackageVulnerability.__dataclass_fields__}
        assert {
            "package_name",
            "ecosystem",
            "affected_versions",
            "fixed_version",
        } <= names
