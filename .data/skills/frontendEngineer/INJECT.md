# frontendEngineer — Quick Reference

- **FIRST**: Read [LEARNED.md](LEARNED.md) for prior corrections
- **Stack**: NiceGUI 3.10+, Quasar, Tailwind, Python 3.14+
- **Source**: `src/skillnir/ui/` — `components/`, `pages/`, `layout.py`, `__init__.py`
- **Always**: `header()` per page; `_COLOR_HEX` maps; `.classes()`/`.props()`; `t()` i18n; absolute imports
- **Never**: raw HTML; hardcoded hex; skip `header()`; module-level nicegui import in `layout.py`
- **Sub-agents**: component-auditor, style-enforcer, test-writer
- **Full guide**: [SKILL.md](SKILL.md), [references/](references/)
