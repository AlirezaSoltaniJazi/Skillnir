# python developer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: Python 3.14+ / hatchling / uv / NiceGUI / PyYAML / questionary / claude-agent-sdk
- **Entry points**: `src/skillnir/cli.py` (CLI), `src/skillnir/ui/__init__.py` (Web UI)
- **Key directories**: `src/skillnir/` (modules), `tests/` (pytest), `.data/skills/` (skill storage)
- **Patterns**: Result dataclasses (not exceptions), frozen dataclasses for config, pathlib.Path exclusively, single quotes (Black -S), comprehensive type hints (str | None)
- **Never**: Use os.path, raise exceptions for expected outcomes, use double quotes, use Any type, skip type hints, use yaml.load() (use yaml.safe_load)
- **Sub-agents**: code-reviewer, test-writer, security-scanner — see [agents/](agents/) for delegation rules
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first. On convention discovery → write to LEARNED.md.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
