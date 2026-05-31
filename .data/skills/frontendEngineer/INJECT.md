# frontendEngineer — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) for prior corrections
- **Stack**: NiceGUI 2.0+, Quasar, Tailwind CSS, Material Design Icons, Python 3.14+
- **Source**: `src/skillnir/ui/` — `components/`, `pages/`, `layout.py`, `__init__.py`
- **Always**: `header()` on every page; `_COLOR_HEX` maps; `.classes()` (Tailwind); `.props()` (Quasar); `t()` for i18n; absolute imports
- **Never**: raw HTML over NiceGUI elements; hardcoded hex colors; skip `header()`; module-level nicegui imports in layout; skip `t()` for user strings
- **Sub-agents**: component-auditor, style-enforcer, test-writer
- **Full guide**: [SKILL.md](SKILL.md), [references/](references/)
