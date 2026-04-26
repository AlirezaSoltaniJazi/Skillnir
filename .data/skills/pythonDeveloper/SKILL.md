---
name: pythonDeveloper
description: >-
  Generic Python development skill for production codebases. Covers web APIs
  (FastAPI/Flask/Django), CLI tools (click/typer), data pipelines, libraries,
  async operations, dataclass patterns, module architecture, testing, type
  annotations, database operations, error handling, and package management.
  Activates when writing Python code, creating modules, fixing bugs, adding
  tests, refactoring, managing dependencies, working with any Python framework,
  or modifying any .py source file.
compatibility: "Python 3.12+, uv/pip/poetry, pytest, ruff/black, asyncio"
metadata:
  author: pythonDeveloper
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep Agent
---

<!-- SKILL.md target: <=300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: pythonDeveloper skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying any Python file (`*.py`) in the project
2. Creating new modules, dataclasses, API endpoints, CLI commands, or services
3. Fixing Python bugs, refactoring, or optimizing performance
4. Writing or updating pytest tests
5. Managing dependencies via `uv`/`pip`/`poetry` or modifying `pyproject.toml`
6. Working with async code, database operations, data validation, or file I/O

## Do NOT Use

- **Frontend JS/TS/CSS/HTML** — use a frontend-specific skill
- **Infrastructure (Docker, Terraform, CI/CD)** — use a devops-specific skill
- **Mobile (Swift/Kotlin)** — use a mobile-specific skill

## Architecture

```
YOUR_PROJECT/
├── pyproject.toml              # Project metadata, dependencies, tool config
├── src/YOUR_PROJECT/           # Source package (src layout)
│   ├── __init__.py             # Package init — version, public API
│   ├── main.py                 # Entry point (or cli.py, app.py, __main__.py)
│   ├── config.py               # Settings (pydantic-settings / environ / dotenv)
│   ├── models.py               # Data models (Pydantic / dataclasses / ORM)
│   ├── services.py             # Business logic layer
│   ├── routes.py               # API routes (FastAPI/Flask/Django views)
│   ├── db.py                   # Database session / connection management
│   ├── exceptions.py           # Custom exception hierarchy
│   └── utils.py                # Shared utilities
├── tests/
│   ├── conftest.py             # Shared fixtures
│   ├── test_models.py          # Unit tests per module
│   └── test_services.py
└── scripts/                    # Dev/ops scripts
```

**Data flow**: Input (HTTP / CLI / file) -> validation (Pydantic / dataclass) -> service logic -> data layer (ORM / raw SQL / file) -> response / output.

**Entry point**: Defined in `[project.scripts]` or `[project.gui-scripts]` in `pyproject.toml`.

## Key Patterns

| Pattern            | Approach                                          | Key Rule                                                |
| ------------------ | ------------------------------------------------- | ------------------------------------------------------- |
| Result objects     | `@dataclass` with `success`/`error` fields        | Return results from fallible ops, don't raise           |
| Data validation    | Pydantic `BaseModel` or `@dataclass` with types   | Validate at boundaries, trust internally                |
| Dependency inject  | Constructor/function params, not global state      | Pass deps explicitly, mock easily in tests              |
| Repository pattern | Separate data access from business logic           | Services call repos, repos call DB/filesystem           |
| Config from env    | pydantic-settings / `os.environ` / dotenv          | 12-factor: config from environment, never hardcoded     |
| Async streaming    | `async for` / `async with` with structured concur. | Use `asyncio.run()` at entry, async internals           |
| Error hierarchy    | Base `AppError` -> specific exceptions              | Catch specific, let unexpected propagate                |
| Factory fixtures   | pytest fixtures + factory functions for test data  | Reusable, composable, isolated                          |

See [references/patterns.md](references/patterns.md) for full code examples.

## Code Style

| Rule               | Convention                                                        |
| ------------------ | ----------------------------------------------------------------- |
| Python version     | 3.12+ — use modern syntax (`X \| None`, `match`, type generics)   |
| Formatter          | ruff format / Black (consistent across project)                   |
| Linter             | ruff check / flake8 / pylint (pick one, enforce it)               |
| Import style       | Absolute only — never relative imports                            |
| Import order       | stdlib -> third-party -> local (groups separated by blank line)    |
| Type hints         | Modern syntax: `str \| None`, `dict[str, X]`, `list[X]`           |
| Naming — modules   | `snake_case.py`                                                   |
| Naming — classes   | `PascalCase` (e.g., `UserService`, `OrderResult`)                 |
| Naming — functions | `snake_case` with `_private` prefix for internal                  |
| Naming — constants | `SCREAMING_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)   |
| Paths              | Always `pathlib.Path` — never `os.path`                           |
| Data models        | `@dataclass` or Pydantic `BaseModel` (frozen for immutable)       |
| Docstrings         | Google-style — module one-liners, function descriptions           |
| Line length        | 88 characters (ruff/Black default) or project-configured          |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new API endpoint**: Define Pydantic request/response models -> add route handler -> add service function -> add tests -> update docs
2. **Add a CLI command**: Add command function with click/typer decorator -> add options/args -> call service layer -> format output -> add tests
3. **Add a database model**: Define ORM model -> create migration -> add repository functions -> add service layer -> add tests with fixtures
4. **Create a result dataclass**: Define `@dataclass` with descriptive fields -> include `error: str | None = None` -> return from function instead of raising
5. **Add async operation**: Use `async def` -> `async with`/`async for` for I/O -> wrap CLI entry with `asyncio.run()` -> test with `pytest-asyncio`
6. **Add a new module**: Create `src/YOUR_PROJECT/module_name.py` -> add module docstring -> use absolute imports -> export via `__init__.py` -> create `test_module_name.py`

## Testing Standards

| Rule              | Convention                                                  |
| ----------------- | ----------------------------------------------------------- |
| Framework         | pytest with appropriate plugins                             |
| Test file naming  | `test_{module}.py` in `tests/`                              |
| Fixture location  | `conftest.py` for shared, test file for local               |
| Temp filesystem   | `tmp_path` for all filesystem-dependent tests               |
| Mocking           | `unittest.mock.patch` / `pytest-mock` for boundaries        |
| Test organization | Class-based: `class TestFeatureName`                        |
| Async tests       | `async def test_*` with pytest-asyncio                      |
| What to mock      | Network calls, external APIs, databases, expensive I/O      |
| What NOT to mock  | Dataclass construction, pure functions, path operations      |
| Naming            | `test_{behavior}_when_{condition}`                          |

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance Rules

- Use generators for large sequences — avoid materializing full lists into memory
- Use `__slots__` on frequently instantiated dataclasses and classes
- Prefer bulk database operations over individual queries in loops
- Use `functools.lru_cache` / `functools.cache` for expensive pure computations
- Use connection pooling for database and HTTP connections
- Profile before optimizing — use `cProfile`, `line_profiler`, or `py-spy`
- Prefer `asyncio.gather()` / `TaskGroup` for concurrent I/O over sequential awaits
- Use `orjson` / `msgspec` for high-throughput JSON serialization

## Security

- Validate and sanitize all user input at API boundaries (Pydantic, etc.)
- Use parameterized queries — never string-format SQL
- Never embed secrets in source — use environment variables or secret managers
- Use `shlex.quote()` for any shell argument construction
- Never use `shell=True` in `subprocess` with user-provided input
- Pin dependencies and audit regularly (`pip-audit`, `safety`)
- Set `encoding='utf-8'` explicitly on all file read/write operations

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern                             | Why It's Wrong                                                    |
| ---------------------------------------- | ----------------------------------------------------------------- |
| Using `os.path` instead of `pathlib`     | `pathlib.Path` is more readable, composable, and modern           |
| Raising exceptions for expected failures | Use result objects — callers should handle expected errors cleanly |
| Using `Optional[X]` from typing          | Use `X \| None` — modern Python 3.10+ union syntax                |
| Using `Dict`, `List` from typing         | Use lowercase `dict`, `list` — deprecated uppercase generics      |
| Using relative imports                   | Absolute imports are clearer and avoid circular import confusion   |
| Bare `except:` clauses                   | Always catch specific exceptions — bare catches hide bugs         |
| Mutable default arguments                | Use `None` + internal creation or `field(default_factory=...)`    |
| Business logic in route handlers         | Handlers are thin — logic belongs in service/domain layer         |
| `print()` for logging                    | Use `logging` module with proper levels and configuration         |
| String-formatted SQL                     | Use parameterized queries — prevent SQL injection                 |

## Code Generation Rules

1. **Read before writing** — always read the target file and related modules before making changes
2. **Match existing style** — follow the project's formatter, linter, and import conventions exactly
3. **Return results** — new functions that can fail must return result objects, not raise
4. **Type everything** — use modern type hints on all function signatures and class fields
5. **Test alongside** — when creating a module, create its test file with fixtures and basic cases
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                 | Behavior                                                              |
| ---------- | ---------------------------------------------------------------- | --------------------------------------------------------------------- |
| Diagnostic | "ImportError", "TypeError", "test fails", "broken", stack trace  | Read error context, trace to root cause, fix with minimal changes     |
| Efficient  | "another endpoint like X", "add field to Y", "same pattern as Z" | Minimal explanation, replicate existing patterns, apply conventions   |
| Teaching   | "what does this do", "explain decorator", "how does async work"  | Explain with references to project examples, link to references/      |
| Review     | "review this", "check my code", "audit module"                   | Read-only analysis, check against conventions, report without changes |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections -> `## Corrections` section
- Preferences -> `## Preferences` section
- Discovered conventions -> `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent              | Role                                           | Spawn When                                       | Tools                          |
| ------------------ | ---------------------------------------------- | ------------------------------------------------ | ------------------------------ |
| code-reviewer      | Read-only Python code analysis, type audit     | PR review, refactoring assessment, type audit    | Read Glob Grep                 |
| test-writer        | Pytest test generation following project style | "write tests for X", new module, coverage gaps   | Read Edit Write Glob Grep Bash |
| dependency-auditor | Dependency analysis and security audit         | Dependency update, security audit, compatibility | Read Glob Grep Bash            |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                       | Examples                                                              |
| ----------------- | --------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| **MUST** follow   | Result objects, absolute imports, pathlib, type hints, parameterized SQL     | "MUST return result dataclass", "MUST use absolute imports"           |
| **SHOULD** follow | Google docstrings, frozen dataclasses for immutable, class-based tests      | "SHOULD add module docstring", "SHOULD freeze immutable data"         |
| **CAN** customize | Fixture organization, docstring detail level, test helper placement          | "CAN group fixtures by feature", "CAN use inline test helpers"        |

## References

| File                                                                     | Description                                                        |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions            |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)             |
| [references/patterns.md](references/patterns.md)                         | Result objects, API, CLI, async, repository patterns with examples |
| [references/code-style.md](references/code-style.md)                     | Import order, type hints, naming, formatting with full examples    |
| [references/test-patterns.md](references/test-patterns.md)               | Pytest fixtures, async tests, mocking patterns with examples       |
| [references/security-checklist.md](references/security-checklist.md)     | Input validation, SQL injection, secret management checklists      |
| [references/common-issues.md](references/common-issues.md)               | Troubleshooting Python pitfalls, import errors, async gotchas      |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols                   |
| [references/template.py](references/template.py)                         | Copy-paste module/class boilerplate                                |
| [assets/pyproject-example.toml](assets/pyproject-example.toml)           | pyproject.toml template with modern Python packaging               |
| [scripts/validate-python.sh](scripts/validate-python.sh)                 | Python naming + structure convention checker                       |
| [agents/code-reviewer.md](agents/code-reviewer.md)                       | Read-only Python code analysis agent                               |
| [agents/test-writer.md](agents/test-writer.md)                           | Pytest test generation agent                                       |
| [agents/dependency-auditor.md](agents/dependency-auditor.md)             | Dependency analysis and security agent                             |
