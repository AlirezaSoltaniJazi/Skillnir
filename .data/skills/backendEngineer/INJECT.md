# backendEngineer — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) for prior corrections
- **Stack**: Python 3.14+, uv, hatchling, pytest, Black (-S), pylint, asyncio, argparse + questionary
- **Source**: `src/skillnir/` (CLI, backends, injector, syncer, generator, tools, UI); entry `skillnir.cli:main`
- **Always**: absolute imports; `pathlib.Path`; result dataclasses; `str | None`
- **Never**: relative imports, `os.path`, `Optional[X]`, `Dict/List` from typing, `pip install` (use `uv add`), raise for expected failures
- **Sub-agents**: code-reviewer, test-writer, dependency-auditor
- **Full guide**: [SKILL.md](SKILL.md), [references/](references/)
