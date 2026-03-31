---
name: backendEngineer
description: >-
  Python backend development skill for the Skillnir project. Covers CLI logic,
  async operations, dataclass patterns, module architecture, testing, type annotations,
  database/filesystem operations, error handling, and package management. Activates
  when writing Python code, creating modules, fixing bugs, adding tests, refactoring,
  managing dependencies, or working with argparse/questionary CLI, NiceGUI UI,
  claude-agent-sdk integrations, or any src/skillnir/ source file.
compatibility: "Python 3.14+, uv, hatchling, pytest, Black, pylint, asyncio"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(python:*) Bash(uv:*) Bash(pip:*) Bash(pytest:*) Glob Grep Agent
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: backendEngineer skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying any Python file under `src/skillnir/`
2. Creating new modules, dataclasses, CLI commands, or backend integrations
3. Fixing Python bugs, refactoring, or optimizing performance
4. Writing or updating pytest tests under `tests/`
5. Managing dependencies via `uv` or modifying `pyproject.toml`
6. Working with async code, streaming, subprocess execution, or file I/O

## Do NOT Use

- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)
- **NiceGUI UI components/pages** (Tailwind, Quasar, HTML) — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **CI/CD, Docker, pre-commit hooks, workflows** — use [devopsEngineer](../devopsEngineer/SKILL.md)

## Architecture

```
src/skillnir/
├── cli.py                  # Entry point — argparse + questionary (1,287 lines)
├── backends.py             # Multi-backend registry (Claude, Cursor, Gemini, Copilot)
├── skills.py               # Skill dataclass + discovery
├── tools.py                # AITool registry (32+ tools with scoring)
├── injector.py             # Symlink injection logic
├── syncer.py               # Version-aware skill syncing
├── remover.py              # Skill removal logic
├── generator.py            # AI doc generation (async SDK + subprocess)
├── skill_generator.py      # SKILL.md generation with templates
├── rule_generator.py       # Cursor rule file generation
├── researcher.py           # AI news research + summarization
├── events.py               # AI events/conferences search
├── hooks.py                # Sound notification hooks (macOS/Linux)
├── i18n.py                 # Internationalization (9 languages, RTL)
├── scaffold.py             # Project scaffolding
├── locales/                # Language JSON files
├── ui/                     # NiceGUI web interface
│   ├── __init__.py         # App setup, static routes, theme
│   ├── components/         # Reusable UI components
│   └── pages/              # Route pages
├── assets/                 # Static assets (sounds)
└── resources/              # HTML templates
```

**Data flow**: CLI input → argparse subparser → core module → filesystem/subprocess → result dataclass → CLI/UI report.

**Entry point**: `skillnir = "skillnir.cli:main"` in `pyproject.toml`.

## Key Patterns

| Pattern             | Approach                                         | Key Rule                                            |
| ------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Result objects      | `@dataclass` with `success`/`error` fields       | Return results from operations, never raise          |
| Registry pattern    | Module-level `dict`/`tuple` constants             | `BACKENDS`, `TOOLS`, `SKILL_SCOPES` as registries   |
| Callback progress   | `on_progress: Callable[[T], None] \| None`       | Stream updates to CLI/UI via callbacks               |
| Frozen dataclasses  | `@dataclass(frozen=True)` for immutable data     | `AITool`, `ModelInfo`, `BackendInfo` are frozen      |
| Async streaming     | `async for message in query(...)` with SDK       | Use `asyncio.run()` at CLI entry, async internals    |
| Subprocess backends | `subprocess.Popen` with threading for stderr     | Parse streaming output line-by-line                  |
| Filesystem storage  | `Path` objects, symlinks, structured directories  | No ORM — `.data/` is the database                   |
| Multi-backend       | `AIBackend` enum + `BACKENDS` registry dict      | Backend-agnostic via enum dispatch                   |

See [references/patterns.md](references/patterns.md) for full code examples.

## Code Style

| Rule                  | Convention                                                        |
| --------------------- | ----------------------------------------------------------------- |
| Python version        | 3.14+ — use latest syntax features                                |
| Formatter             | Black with `-S` flag (single quotes, no string normalization)     |
| Linter                | pylint with custom `.pylintrc`, autoflake for unused imports      |
| Import style          | Absolute only — never relative imports                            |
| Import order          | stdlib → third-party → local (groups separated by blank line)     |
| Type hints            | Modern syntax: `str \| None`, `dict[str, X]`, `list[X]`          |
| Naming — modules      | `snake_case.py`                                                   |
| Naming — classes      | `PascalCase` (e.g., `AITool`, `GenerationProgress`)              |
| Naming — functions    | `snake_case` with `_private` prefix for internal                  |
| Naming — constants    | `SCREAMING_SNAKE_CASE` (e.g., `SKILL_SCOPES`, `RTL_LANGUAGES`)   |
| Naming — CLI commands | `kebab-case` (e.g., `generate-docs`, `delete-skill`)             |
| Paths                 | Always `pathlib.Path` — never `os.path`                           |
| Data models           | `@dataclass` (frozen for immutable, regular for mutable)          |
| Strings               | Single quotes preferred (enforced by Black `-S`)                  |
| Docstrings            | Google-style, selective — module one-liners, function descriptions |
| Line length           | Black default (88 characters)                                     |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new CLI command**: Add subparser in `cli.py` → create handler function `_command_name()` → add questionary prompts → call core module → report results
2. **Add a new AI tool**: Add `AITool` entry to `TOOLS` tuple in `tools.py` → set `dotdir`, `popularity`, `performance`, `price` → add detection pattern in `detect_tools()`
3. **Add a new backend**: Add enum value to `AIBackend` → add entry in `BACKENDS` dict with CLI command, models, slash commands → implement stream parsing in `parse_stream_line()`
4. **Create a result dataclass**: Define `@dataclass` with descriptive fields → include optional `error: str | None = None` → return from core function instead of raising
5. **Add async generation**: Use `async def` → `async for` with claude-agent-sdk → yield `GenerationProgress` via callback → wrap entry point with `asyncio.run()`
6. **Add a new module**: Create `src/skillnir/module_name.py` → add module docstring → use absolute imports → export via `__init__.py` if public API

## Testing Standards

| Rule                     | Convention                                                   |
| ------------------------ | ------------------------------------------------------------ |
| Framework                | pytest 9.0.2+ with `asyncio_mode = "auto"`                  |
| Test file naming         | `test_{{module}}.py` in `tests/`                             |
| Fixture location         | `conftest.py` for shared, test file for local                |
| Key fixtures             | `tmp_project`, `sample_skill`, `sample_tool`, `mock_config`  |
| Temp filesystem          | `tmp_path` + structured directories for integration tests    |
| Mocking                  | `unittest.mock.patch` for subprocess, file operations        |
| Test organization        | Class-based: `class TestFeatureName`                         |
| Async tests              | `async def test_*` — auto mode handles event loop            |
| What to mock             | Subprocess calls, external APIs, filesystem when expensive   |
| What NOT to mock         | Dataclass construction, path operations, pure functions       |

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance Rules

- Use generators for large sequences — avoid materializing full lists
- Use `__slots__` on frequently instantiated dataclasses
- Prefer `pathlib` bulk operations over individual file checks
- Use `shutil.which()` for CLI detection (cached per session)
- Avoid repeated YAML/JSON parsing — parse once, pass data structures
- Use `subprocess.Popen` with streaming for long-running backends (not `subprocess.run`)
- Cache expensive tool detection results within a session

## Security

- Validate all user-provided paths before filesystem operations
- Use `shlex.quote()` for shell argument construction
- Never embed secrets in source — use environment variables
- Bandit scans on every commit (`-lll -iii` threshold)
- Safety CVE scanning via pre-commit (exemptions documented)
- Sanitize subprocess arguments — no shell=True with user input

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern                             | Why It's Wrong                                                    |
| ---------------------------------------- | ----------------------------------------------------------------- |
| Using `os.path` instead of `pathlib`     | Project standardized on `Path` — consistency and readability      |
| Raising exceptions for expected failures | Use result dataclasses — callers should handle expected errors     |
| Using `Optional[X]` from typing          | Use `X \| None` — modern Python 3.10+ union syntax               |
| Using `Dict`, `List` from typing         | Use lowercase `dict`, `list` — deprecated uppercase generics      |
| Using relative imports                   | Project uses absolute imports exclusively                         |
| Using `pip install`                      | Use `uv add` — project standardized on uv package manager        |
| Using `setup.py` or `requirements.txt`   | Use `pyproject.toml` — single source of truth                     |
| Using double quotes for strings          | Black `-S` enforces single quotes — follow formatter              |
| Putting business logic in `cli.py`       | CLI is orchestration only — logic belongs in dedicated modules    |
| Using `print()` for user output          | Use questionary/rich for formatted output, callbacks for progress |

## Code Generation Rules

1. **Read before writing** — always read the target file and related modules before making changes
2. **Match existing style** — follow Black `-S`, pylint, and import conventions exactly
3. **Return results** — new functions that can fail must return result dataclasses, not raise
4. **Type everything** — use modern type hints on all function signatures and class fields
5. **Test alongside** — when creating a module, create its test file with fixtures and basic cases
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                  | Behavior                                                                 |
| ---------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Diagnostic | "ImportError", "TypeError", "test fails", "broken", stack trace   | Read error context, trace to root cause, fix with minimal changes        |
| Efficient  | "another endpoint like X", "add field to Y", "same pattern as Z" | Minimal explanation, replicate existing patterns, apply conventions       |
| Teaching   | "what does this do", "explain decorator", "how does async work"  | Explain with references to project examples, link to references/          |
| Review     | "review this", "check my code", "audit module"                   | Read-only analysis, check against conventions, report without changes    |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent              | Role                                           | Spawn When                                       | Tools                          |
| ------------------ | ---------------------------------------------- | ------------------------------------------------ | ------------------------------ |
| code-reviewer      | Read-only Python code analysis, type audit     | PR review, refactoring assessment, type audit     | Read Glob Grep                 |
| test-writer        | Pytest test generation following project style | "write tests for X", new module, coverage gaps   | Read Edit Write Glob Grep Bash |
| dependency-auditor | Dependency analysis and security audit         | Dependency update, security audit, compatibility | Read Glob Grep Bash            |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                          | Examples                                                        |
| ----------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| **MUST** follow   | Result objects, absolute imports, pathlib, type hints, Black -S, uv            | "MUST return result dataclass", "MUST use absolute imports"     |
| **SHOULD** follow | Google docstrings, frozen dataclasses for immutable, class-based test grouping | "SHOULD add module docstring", "SHOULD freeze immutable data"   |
| **CAN** customize | Fixture organization, docstring detail level, test helper placement            | "CAN group fixtures by feature", "CAN use inline test helpers" |

## References

| File                                                                     | Description                                                          |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions              |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)               |
| [references/patterns.md](references/patterns.md)                         | Result objects, registry, async, subprocess patterns with examples   |
| [references/code-style.md](references/code-style.md)                     | Import order, type hints, naming, formatting with full examples      |
| [references/test-patterns.md](references/test-patterns.md)               | Pytest fixtures, async tests, mocking patterns with examples         |
| [references/security-checklist.md](references/security-checklist.md)     | Input validation, subprocess safety, secret management checklists    |
| [references/common-issues.md](references/common-issues.md)               | Troubleshooting Python pitfalls, import errors, async gotchas        |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols                     |
| [references/template.py](references/template.py)                         | Copy-paste module/class boilerplate                                  |
| [assets/pyproject-example.toml](assets/pyproject-example.toml)           | pyproject.toml template with uv + hatchling                          |
| [scripts/validate-backend.sh](scripts/validate-backend.sh)               | Python naming + structure convention checker                         |
| [agents/code-reviewer.md](agents/code-reviewer.md)                       | Read-only Python code analysis agent                                 |
| [agents/test-writer.md](agents/test-writer.md)                           | Pytest test generation agent                                         |
| [agents/dependency-auditor.md](agents/dependency-auditor.md)             | Dependency analysis and security agent                               |
