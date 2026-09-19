# modelRegistry — Quick Reference

- **FIRST**: read LEARNED.md; announce "Using: modelRegistry skill"
- **Never from memory** — verify IDs against the provider's live doc/CLI
- **Registry**: `backends.py` → `BACKENDS[...].models` (`ModelInfo`: id, alias, display, tier)
- **Alias**: unversioned (`opus`/`sonnet`/`fable`/`haiku`) = family's newest; demoted gets `opus-4.8`-style
- **One** `is_default=True` per backend; `default_model` must resolve
- **Install hints**: `welcome_dialog.py` → `_CLI_SETUP_INFO`
- **Same edit**: `tests/test_backends.py` aliases + CHANGELOG `[Unreleased]`
