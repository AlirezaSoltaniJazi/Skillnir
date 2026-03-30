# backendEngineer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: Python 3.14+, uv, hatchling, pytest, Black (-S), pylint, asyncio, argparse + questionary
- **Entry point**: `skillnir = "skillnir.cli:main"` in `pyproject.toml`
- **Source**: `src/skillnir/` — CLI, backends, injector, syncer, generator, tools, UI
- **Key rules**: Absolute imports only; `pathlib.Path` not `os.path`; result dataclasses not exceptions; `str | None` not `Optional`; single quotes (Black -S)
- **Never**: Relative imports, `os.path`, `Optional[X]`, `Dict/List` from typing, `pip install` (use `uv add`), raise for expected failures, `setup.py`/`requirements.txt`
- **Sub-agents**: code-reviewer (read-only audit), test-writer (pytest generation), dependency-auditor (security)
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
