"""Core internationalization module for Skillnir."""

import functools
import json
from pathlib import Path

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "de": "Deutsch",
    "nl": "Nederlands",
    "pl": "Polski",
    "fa": "\u0641\u0627\u0631\u0633\u06cc",
    "uk": "\u0423\u043a\u0440\u0430\u0457\u043d\u0441\u044c\u043a\u0430",
    "sq": "Shqip",
    "fr": "Fran\u00e7ais",
    "ar": "\u0627\u0644\u0639\u0631\u0628\u064a\u0629",
}

RTL_LANGUAGES: set[str] = {"ar", "fa"}

LOCALES_DIR = Path(__file__).parent / "locales"
CONFIG_PATH = Path.home() / ".skillnir" / "config.json"


@functools.lru_cache
def load_locale(lang: str) -> dict:
    """Load JSON locale file for the given language. Returns empty dict if not found."""
    locale_file = LOCALES_DIR / f"{lang}.json"
    try:
        return json.loads(locale_file.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _resolve(data: dict, key: str) -> str | None:
    """Resolve a dot-notation key by traversing nested dicts."""
    parts = key.split(".")
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current if isinstance(current, str) else None


def get_current_language() -> str:
    """Read language from config file. Default: 'en'."""
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        return config.get("language", "en")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return "en"


def set_language(lang: str) -> None:
    """Save language to config file."""
    config: dict = {}
    try:
        config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    config["language"] = lang
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def t(key: str, lang: str | None = None, **kwargs: str) -> str:
    """Main translation function with fallback chain: lang -> en -> key."""
    if lang is None:
        lang = get_current_language()
    result = _resolve(load_locale(lang), key)
    if result is None and lang != "en":
        result = _resolve(load_locale("en"), key)
    if result is None:
        result = key
    if kwargs:
        result = result.format_map(kwargs)
    return result


def is_rtl(lang: str | None = None) -> bool:
    """Return True if the language is right-to-left."""
    if lang is None:
        lang = get_current_language()
    return lang in RTL_LANGUAGES
