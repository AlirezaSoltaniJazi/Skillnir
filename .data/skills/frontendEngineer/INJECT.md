# frontendEngineer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: NiceGUI 2.0+, Quasar, Tailwind CSS, Material Design Icons, Python 3.14+
- **Source**: `src/skillnir/ui/` — components/ (13), pages/ (12), layout.py, __init__.py
- **Key rules**: `header()` on every page; `_COLOR_HEX` maps for colors; `.classes()` for Tailwind; `.props()` for Quasar; `t()` for i18n; absolute imports only; single quotes (Black -S)
- **Never**: Raw HTML over NiceGUI elements; hardcoded hex colors; skip `header()`; module-level nicegui imports in layout; relative imports; JavaScript frameworks; skip `t()` for user strings
- **Sub-agents**: component-auditor (read-only audit), style-enforcer (design system), test-writer (UI tests)
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
