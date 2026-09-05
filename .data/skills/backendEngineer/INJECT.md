# backendEngineer — Quick Reference

- **FIRST**: read [LEARNED.md](LEARNED.md)
- **Stack**: Python 3.14+, uv, hatchling, pytest, Black `-S`, asyncio; `src/skillnir/`, entry `skillnir.cli:main`
- **cli.py** = orchestration only; logic in core modules → result dataclass
- **Always**: absolute imports, `pathlib.Path`, result dataclasses, `str | None`
- **Never**: relative imports, `os.path`, `Optional`/`Dict`/`List`, `pip install`, raise for expected failures
- **Sub-agents**: code-reviewer, test-writer, dependency-auditor
- **Full**: [SKILL.md](SKILL.md), [references/](references/)
