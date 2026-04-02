# Test Patterns — Skillnir Frontend

> UI component testing strategies, mock patterns, and test organization examples.

---

## What to Test

| Category          | Test Strategy                            | Example                                  |
| ----------------- | ---------------------------------------- | ---------------------------------------- |
| Color maps        | Unit test `_COLOR_HEX` dict completeness | All semantic colors have hex values      |
| Component logic   | Test conditional rendering paths         | `stat_card(clickable=True)` adds classes |
| State transitions | Test handler side effects                | `on_dark_toggle` updates storage         |
| Validation        | Test path/input validation logic         | Invalid path shows error notification    |
| i18n              | Test `t()` returns correct translations  | Missing keys fallback to English         |
| Navigation        | Test `NAV_GROUPS` structure completeness | All routes have icons and labels         |

## What NOT to Test

- NiceGUI rendering internals (Quasar/Vue output)
- CSS class application (visual testing territory)
- Browser storage persistence (NiceGUI responsibility)
- Tailwind utility class correctness

---

## Test File Structure

```python
"""Tests for skillnir.ui.components.stat_card module."""

from unittest.mock import MagicMock, patch

import pytest

from skillnir.ui.components.stat_card import _COLOR_HEX, stat_card


class TestColorHex:
    """Tests for the _COLOR_HEX color map."""

    def test_contains_all_semantic_colors(self):
        expected = {'primary', 'secondary', 'accent', 'positive', 'negative', 'warning', 'info', 'grey'}
        assert expected.issubset(set(_COLOR_HEX.keys()))

    def test_all_values_are_hex(self):
        for name, hex_val in _COLOR_HEX.items():
            assert hex_val.startswith('#'), f'{name} value is not hex: {hex_val}'
            assert len(hex_val) == 7, f'{name} hex length wrong: {hex_val}'
```

---

## Mocking NiceGUI Elements

```python
"""Tests for page routing and layout."""

from unittest.mock import MagicMock, patch


class TestPageSettings:
    """Tests for settings page logic."""

    @patch('skillnir.ui.pages.settings.header')
    @patch('skillnir.ui.pages.settings.ui')
    def test_dark_mode_toggle_updates_storage(self, mock_ui, mock_header):
        mock_app = MagicMock()
        mock_app.storage.user = {'dark_mode': True}

        # Simulate toggle event
        event = MagicMock()
        event.value = False

        # Call the handler directly
        from skillnir.ui.pages.settings import page_settings
        # Test handler logic in isolation
```

---

## Testing Navigation Structure

```python
"""Tests for layout navigation structure."""

from skillnir.ui.layout import NAV_GROUPS, get_nav_groups


class TestNavGroups:
    """Tests for navigation group definitions."""

    def test_all_groups_have_items(self):
        for group_title, items in NAV_GROUPS:
            assert len(items) > 0, f'Group "{group_title}" has no items'

    def test_all_items_have_required_fields(self):
        for group_title, items in NAV_GROUPS:
            for item in items:
                assert len(item) == 3, f'Item in "{group_title}" missing fields: {item}'
                icon, label, route = item
                assert icon, f'Missing icon in "{group_title}"'
                assert label, f'Missing label in "{group_title}"'
                assert route.startswith('/'), f'Route must start with /: {route}'

    def test_translated_groups_match_count(self):
        translated = get_nav_groups('en')
        assert len(translated) == len(NAV_GROUPS)
```

---

## Testing i18n

```python
"""Tests for i18n integration in UI."""

from skillnir.i18n import t, is_rtl, SUPPORTED_LANGUAGES


class TestI18n:
    """Tests for internationalization."""

    def test_fallback_to_english(self):
        result = t('nav.items.install', 'nonexistent_lang')
        assert result  # Should fallback, not return empty

    def test_rtl_languages(self):
        assert is_rtl('ar') is True
        assert is_rtl('fa') is True
        assert is_rtl('en') is False

    def test_all_languages_have_locale_files(self):
        from pathlib import Path
        locales_dir = Path(__file__).parent.parent / 'src' / 'skillnir' / 'locales'
        for code in SUPPORTED_LANGUAGES:
            assert (locales_dir / f'{code}.json').exists(), f'Missing locale: {code}'
```

---

## Testing Async Progress

```python
"""Tests for progress panel component logic."""

from skillnir.ui.components.progress_panel import format_duration


class TestFormatDuration:
    """Tests for duration formatting."""

    def test_seconds_only(self):
        assert format_duration(45) == '45s'

    def test_minutes_and_seconds(self):
        assert format_duration(125) == '2m 5s'

    def test_zero(self):
        assert format_duration(0) == '0s'
```
