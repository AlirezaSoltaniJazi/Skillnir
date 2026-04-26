# pythonDeveloper — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: Python 3.12+, modern packaging (pyproject.toml), pytest, ruff/Black, asyncio
- **Source**: `src/YOUR_PROJECT/` — src layout with pyproject.toml entry points
- **Key rules**: Absolute imports only; `pathlib.Path` not `os.path`; result dataclasses not exceptions; `str | None` not `Optional`; parameterized SQL not string formatting
- **Never**: Relative imports, `os.path`, `Optional[X]`, `Dict/List` from typing, bare `except:`, mutable default args, `print()` for logging, `shell=True` with user input
- **Sub-agents**: code-reviewer (read-only audit), test-writer (pytest generation), dependency-auditor (security)
- **Self-learning**: On correction -> write to LEARNED.md. On ambiguity -> check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
