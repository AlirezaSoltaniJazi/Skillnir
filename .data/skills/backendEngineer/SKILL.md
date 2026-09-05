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
sub-agents:
  - name: code-reviewer
    file: agents/code-reviewer.md
  - name: test-writer
    file: agents/test-writer.md
  - name: dependency-auditor
    file: agents/dependency-auditor.md
---

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: backendEngineer skill" at the very start of your response before doing any work.

## When to Use

1. Any Python file under `src/skillnir/` — modules, dataclasses, CLI commands, backend integrations
2. Fixing bugs, refactoring, performance; async/streaming/subprocess/file I/O
3. pytest tests under `tests/`; dependencies via `uv` or `pyproject.toml`

## Do NOT Use

- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)
- **NiceGUI UI components/pages** (Tailwind, Quasar, HTML) — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **CI/CD, Docker, pre-commit hooks, workflows** — use [devopsEngineer](../devopsEngineer/SKILL.md)

## Architecture

Package `src/skillnir/` — entry point `skillnir.cli:main` (`pyproject.toml`). `cli.py` (argparse + questionary, 28 commands) is orchestration only; each command dispatches to a dedicated core module (`skills`, `tools`, `injector`, `syncer`, `generator`, `skill_generator`, research/intel pipelines) that owns the business logic.

**Data flow**: CLI input → `main()`'s `choices=[...]` handler → core module → filesystem/subprocess/SDK → result dataclass → CLI/UI report. `.data/skills/` is the source of truth; tool dotdirs hold only relative symlinks. Full module map: [architecture guide](references/architecture-guide.md).

## Key Patterns

| Pattern             | Rule + WHY                                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------------------ |
| Result objects      | `@dataclass` with `success`/`error`; return, never raise — callers handle expected failures inline     |
| Registry pattern    | Module-level `dict`/`tuple` (`BACKENDS`, `TOOLS`) — single lookup point, no scattered conditionals      |
| Callback progress   | `on_progress: Callable[[T], None] \| None` — decouples core logic from CLI vs UI rendering              |
| Frozen dataclasses  | `@dataclass(frozen=True)` for `AITool`/`ModelInfo`/`BackendInfo` — shared configs must not mutate       |
| Async streaming     | `async for message in query(...)`; `asyncio.run()` at CLI entry — SDK is async, only the boundary syncs |
| Subprocess backends | `subprocess.Popen` + threaded stderr, parse line-by-line — streaming output must not block             |
| Filesystem storage  | `Path` + symlinks; no ORM — `.data/` is the database, source of truth                                   |

See [references/patterns.md](references/patterns.md) for full code examples.

## Code Style

Anti-Patterns (below) is the authoritative list of prohibitions (`os.path`, `Optional`, relative imports, double quotes). Positive conventions:

| Rule        | Convention + WHY                                                                                                       |
| ----------- | -------------------------------------------------------------------------------------------------------------------- |
| Python      | 3.14+ — use latest syntax; older code triggers pylint deprecation warnings                                           |
| Format/lint | Black `-S` + pylint (`.pylintrc`) + autoflake — enforced by pre-commit, so non-conforming code is rejected           |
| Import order| stdlib → third-party → `skillnir.*`, blank-line separated — so diffs stay clean and cycles are visible               |
| Type hints  | `str \| None`, `dict[str, X]`, `list[X]` — required on every signature (pylint gate)                                 |
| Naming      | modules `snake_case.py`; classes `PascalCase`; functions `snake_case`/`_private`; constants `UPPER`; CLI `kebab-case` |
| Docstrings  | Google-style, selective — module one-liners + function descriptions                                                  |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **New CLI command**: add string to `choices=[...]` on `main()` in `cli.py` → `_command_name()` handler + questionary prompts → call core module → wire `elif args.command == ...` → report
2. **New AI tool**: add `AITool` to `TOOLS` tuple in `tools.py` (`detect_tools()` needs no change — it checks every entry's `dotdir`)
3. **New backend**: add `AIBackend` enum value → `BACKENDS` dict entry (CLI cmd, models, slash cmds) → stream parsing in `parse_stream_line()`
4. **Result dataclass**: `@dataclass` with fields + optional `error: str | None = None` → return instead of raising
5. **Async generation**: `async def` → `async for` with claude-agent-sdk → yield `GenerationProgress` via callback → `asyncio.run()` at entry
6. **New module**: `src/skillnir/module_name.py` → module docstring → absolute imports → export via `__init__.py` if public

## Testing Standards

- **Framework**: pytest with `asyncio_mode = "auto"`; `async def test_*` needs no decorator
- **Files**: `test_{module}.py` in `tests/`; class-based `class TestFeatureName`
- **Fixtures**: `tmp_path` (built-in) + `unittest.mock.patch` for subprocess/filesystem
- **Mock** subprocess calls, external APIs, expensive I/O; **never mock** dataclass construction, path ops, pure functions

See [references/test-patterns.md](references/test-patterns.md) for full test examples.

## Performance & Security

- Generators for large sequences; `subprocess.Popen` streaming (not `.run`) for long backends — avoids buffering the whole output
- `shutil.which()` + cache tool detection per session — filesystem probes are expensive
- Validate user paths before FS ops; `shlex.quote()` args, never `shell=True` with user input — command injection
- No secrets in source; Bandit (`-lll -iii`) + Safety CVE scan run every commit

See [references/security-checklist.md](references/security-checklist.md) for detailed checklists.

## Anti-Patterns

| Anti-Pattern (never)                      | Do instead                                                     |
| ----------------------------------------- | -------------------------------------------------------------- |
| `os.path`                                 | `pathlib.Path` — the codebase standard                         |
| Raising for expected failures             | Return a result dataclass                                      |
| `Optional[X]`, `Dict`, `List` from typing | `X \| None`, `dict`, `list` — modern generics                  |
| Relative imports                          | Absolute `skillnir.*` only                                     |
| `pip install`, `setup.py`, `requirements.txt` | `uv add` + `pyproject.toml` — single source of truth       |
| Double quotes for strings                 | Single quotes — Black `-S` enforces                            |
| Business logic in `cli.py`                | Dedicated core module — CLI is orchestration only              |
| `print()` for output                      | questionary/rich + progress callbacks                          |

## Communication Style

- **Lead with the answer** — no preamble, no "Let me explain", no "Great question"
- **Strip filler** — drop "basically", "essentially", "actually", "just", "simply"
- **No trailing summaries** — the user reads the diff; don't restate what you did
- **Bullets and tables over paragraphs**; show the fix, not a lecture about it
- **Max 2-3 sentences** per explanation unless asked "why" or in Teaching mode
- **No hedging, no apologies** — say "do X", and fix mistakes without "sorry"

## Session Protocols

| Mode       | Detection signals (observable)                                   | Behavior                          |
| ---------- | ---------------------------------------------------------------- | --------------------------------- |
| Teaching   | "what does this do", "explain decorator", first use of a pattern | Explain first, then generate      |
| Efficient  | "another one like X", Nth repetition of a known pattern          | Generate directly, minimal prose  |
| Diagnostic | traceback, "ImportError"/"TypeError", "test fails", "why broken" | Diagnose to root cause before edit |

Default to Teaching when uncertain; a developer override always wins. Deeper interaction guidance (Review mode, proficiency calibration, anti-dependency nudges) lives in [references/ai-interaction-guide.md](references/ai-interaction-guide.md).

**Self-Learning via LEARNED.md** (written, never merely suggested — so the next session inherits the fix):

- **Read LEARNED.md first**, before generating code.
- **On correction**: acknowledge, restate as a rule, apply for the session, write under `## Corrections`.
- **On an undocumented convention**: check LEARNED.md → project files → ask ONE question, write under `## Preferences`.
- **On discovering an implicit convention**: state it, then write under `## Discovered Conventions`.
- Entry format: `- YYYY-MM-DD: rule description`.

## Sub-Agent Delegation

| Agent                                        | Spawn when                                | Tools                    |
| -------------------------------------------- | ----------------------------------------- | ------------------------ |
| [code-reviewer](agents/code-reviewer.md)     | PR review, refactor/type audit (read-only)| Read Glob Grep           |
| [test-writer](agents/test-writer.md)         | "write tests for X", new module, coverage | Read Edit Write Bash Glob Grep |
| [dependency-auditor](agents/dependency-auditor.md) | dependency update, security audit    | Read Glob Grep Bash      |

Spawn when the task is self-contained and needs no follow-up context; never delegate architectural decisions. Pass all context explicitly — sub-agents don't see parent conversation and can't spawn their own (max depth 1). See [agents/](agents/).

## Freedom Levels

| Level             | Scope + WHY                                                                                                                                                                                                                                                                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | Return result dataclasses (a raise swallows the error path callers expect inline); absolute imports (relative break on module moves); `pathlib.Path` (raw strings desync the `Path`-only codebase); type hints on every signature (pylint gate); Black `-S` + uv (enforced toolchain — else pre-commit fails); LEARNED.md writes (unwritten corrections lost next session); explicit context to sub-agents (they never see parent conversation). |
| **SHOULD** follow | Google-style docstrings; `frozen=True` for immutable configs (catches accidental mutation of shared registries); class-based test grouping — vary only when a case genuinely differs.                                                                                                                                                                                |
| **CAN** customize | Fixture organization, docstring detail, test helper placement, sub-agent tool sets, `references/` depth — no downstream contract.                                                                                                                                                                                                                                    |

## References

- [LEARNED.md](LEARNED.md) — **auto-updated** corrections, preferences, conventions (read first)
- [architecture-guide](references/architecture-guide.md) — full module map + data flow
- [patterns.md](references/patterns.md) — result objects, registry, async, subprocess examples
- [code-style.md](references/code-style.md) — import order, type hints, naming, formatting
- [test-patterns.md](references/test-patterns.md) — pytest fixtures, async tests, mocking
- [security-checklist.md](references/security-checklist.md) — input validation, subprocess safety, secrets
- [common-issues.md](references/common-issues.md) — import errors, async gotchas, Python pitfalls
- [ai-interaction-guide.md](references/ai-interaction-guide.md) — Review mode, proficiency calibration, anti-dependency
- [template.py](references/template.py) · [pyproject-example.toml](assets/pyproject-example.toml) · [validate-backend.sh](scripts/validate-backend.sh) · [agents/](agents/)
