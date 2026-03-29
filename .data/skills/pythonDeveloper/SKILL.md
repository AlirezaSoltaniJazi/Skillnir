---
name: pythonDeveloper
description: >-
  Backend Python development rules for the Skillnir project. Covers module design,
  dataclass patterns, CLI commands, subprocess spawning, file operations, YAML parsing,
  testing, type hints, error handling, and code style. Activates for any Python backend
  task including new modules, bug fixes, refactoring, testing, code review, performance,
  migrations, and deployment.
compatibility: "Python 3.14+, hatchling, uv, NiceGUI 2.0+, PyYAML 6.0+, pytest 9.0+"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Bash(uv:*) Bash(python:*) Bash(pytest:*) Glob Grep Agent
sub-agents:
  - name: code-reviewer
    file: agents/code-reviewer.md
  - name: test-writer
    file: agents/test-writer.md
  - name: security-scanner
    file: agents/security-scanner.md
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: python developer skill" at the very start of your response before doing any work.

## When to Use

1. Creating or modifying Python modules in `src/skillnir/`
2. Writing or updating pytest tests in `tests/`
3. Designing dataclasses, enums, result types, or data models
4. Subprocess spawning, stream parsing, or CLI command building
5. Bug fixing, refactoring, or code review of backend Python code
6. Performance optimization, dependency management, or deployment tasks

## Do NOT Use

- **UI components or page layouts** (NiceGUI templates, Tailwind) — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **CI/CD, Docker, pre-commit config** — use [devopsEngineer](../devopsEngineer/SKILL.md)
- **Skill file structure, LEARNED.md, INJECT.md** — use [skillnir](../skillnir/SKILL.md)

## Architecture

```
src/skillnir/                    # Main package — modular, feature-driven
├── cli.py                      # argparse CLI entry (17 commands)
├── backends.py                 # Multi-backend abstraction (4 backends)
├── skills.py                   # Skill discovery + YAML frontmatter parsing
├── syncer.py                   # Version-aware skill syncing
├── injector.py                 # Symlink creation for tool dotdirs
├── generator.py                # AI docs generation (SDK + subprocess)
├── skill_generator.py          # Skill generation (30+ scopes)
├── rule_generator.py           # Cursor rule generation
├── remover.py                  # Skill/docs deletion
├── scaffold.py                 # Template generation
├── hooks.py                    # Claude Code sound notifications
├── tools.py                    # AI tool registry (40+ tools)
├── researcher.py               # Web search + summarization pipeline
├── usage.py                    # Thread-safe token tracking
└── ui/                         # NiceGUI web interface
    ├── __init__.py             # App setup, CSS, page registration
    ├── layout.py               # Shared layout components
    ├── pages/                  # @ui.page route modules (11 pages)
    └── components/             # Reusable UI widgets (12 components)
tests/                          # pytest suite (13 test files + conftest.py)
```

**Data flow**: CLI/UI → module function → result dataclass → print/display. No database — file system only (pathlib.Path). Config persisted to `~/.skillnir/config.json`.

## Key Patterns

| Pattern | Approach | Key Rule |
|---------|----------|----------|
| Error handling | Result dataclasses (`SyncResult`, `GenerationResult`) | Return results, never raise for expected outcomes |
| Config objects | `@dataclass(frozen=True)` with `field(default_factory=...)` | Immutable after creation |
| Result objects | `@dataclass` (regular, mutable) | Include action/status + optional error field |
| File operations | `pathlib.Path` exclusively | Always `encoding='utf-8'`, check `.exists()` first |
| Enums | `class X(Enum)` with string values | Used for fixed sets, never plain strings |
| Type hints | Modern Python 3.14 syntax | `str \| None`, `list[X]`, `tuple[X, ...]`, no `Any` |
| Subprocess | `Popen` with threaded stderr drain | Never `shell=True`, always command as list |
| Directory iteration | `sorted(dir.iterdir())` | Deterministic output, filter with `.is_dir()` |
| Caching | `@functools.lru_cache` | For expensive discovery operations only |
| Multi-backend | `AIBackend` enum + `BACKENDS` registry dict | Add new backends via registry, not conditionals |

See [references/api-patterns.md](references/api-patterns.md) for full code examples.

## Code Style

| Rule | Convention |
|------|-----------|
| Formatter | Black 26.3.1, Python 3.14 target, `-S` flag (single quotes) |
| Line length | 100 characters |
| Linter | Pylint (`.pylintrc`, fail-under=10) |
| Imports | Absolute only: `from skillnir.X import Y` |
| Import order | stdlib → third-party → local (blank lines between) |
| Naming | `snake_case` functions, `UPPER_CASE` constants, `PascalCase` classes |
| Docstrings | One-liner with period, no param/return docs (types in signatures) |
| Module docstrings | Required on every `.py` file |
| Type hints | Required on all function signatures |
| Path operations | `pathlib.Path` only, never `os.path` |
| String quotes | Single quotes (enforced by Black -S) |
| Unused code | Autoflake removes unused imports/variables |
| Pre-commit exclude | `.data/` excluded from all code quality hooks |

See [references/code-style.md](references/code-style.md) for import order examples and full formatting rules.

## Common Recipes

1. **Add a new module**: Create `src/skillnir/{name}.py` with module docstring → define result dataclass → implement core functions with type hints → create `tests/test_{name}.py` with class-based tests → use `tmp_path` fixture for file operations
2. **Add a new backend**: Add variant to `AIBackend` enum → create `BackendInfo` entry in `BACKENDS` dict → define model list as `tuple[ModelInfo, ...]` → implement stream parsing in `parse_stream_line` → add CLI flags in `build_subprocess_command`
3. **Add a CLI command**: Add subparser in `cli.py:main()` → create `_handle_{command}` function → use questionary for user prompts → return result via print
4. **Add a dataclass**: Choose frozen (config) vs regular (result) → add type hints on all fields → use `field(default_factory=...)` for mutable defaults → add `str | None` for optional fields
5. **Fix a bug**: Read the module → check result dataclass for missing error paths → verify Path guards (`.exists()`, `.is_dir()`) → check `encoding='utf-8'` → add test for the edge case
6. **Run quality checks**: `uv run pytest` → `pre-commit run --all-files` → verify Black, Pylint, Autoflake, Bandit all pass

## Testing Standards

- Framework: pytest with pytest-asyncio (`asyncio_mode = "auto"`)
- Organization: class-based (`TestFunctionName`) with `test_description` methods
- File operations: use `tmp_path` fixture (real files, not mocks)
- Mock only: external dependencies (subprocess, config loading, user input)
- Assertions: on result dataclass fields directly, not on mock calls
- Edge cases: empty inputs, missing files, same source/target paths, malformed YAML/JSON
- Helpers: module-level `_make_*` functions for test setup, shared fixtures in `conftest.py`
- Run: `uv run pytest` (all), `uv run pytest tests/test_{module}.py` (specific)

See [references/test-patterns.md](references/test-patterns.md) for full examples and fixture patterns.

## Performance Rules

- Use `@functools.lru_cache` for expensive discovery operations (prompt versions, tool lists)
- Use `sorted()` on directory iteration for deterministic output
- Drain subprocess stderr in a separate daemon thread to prevent deadlocks
- Use `Path.resolve()` for path comparison (not string comparison)
- Set timeout on `proc.wait()` to prevent hanging processes
- Use `shutil.copytree` / `shutil.rmtree` for directory operations (not recursive manual copy)
- Use `tuple[...]` for immutable sequences in frozen dataclasses (not `list`)

## Security

- Always `yaml.safe_load()`, never `yaml.load()` (arbitrary code execution — Critical)
- Never `shell=True` in subprocess (injection — Critical)
- Validate paths with `.resolve()` before `shutil.rmtree` (path traversal — Critical)
- Always `encoding='utf-8'` on file I/O (data integrity — Medium)
- Handle `JSONDecodeError` gracefully with safe defaults (misconfiguration — Medium)
- Never store API keys in config.json or source (disclosure — High)

See [references/security-checklist.md](references/security-checklist.md) for per-module verification checklists.

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|-------------|----------------|
| Using `os.path` for file operations | Project uses `pathlib.Path` exclusively — mixing creates inconsistency |
| Raising exceptions for expected outcomes | Use result dataclasses (SyncResult, etc.) — exceptions are for truly exceptional cases |
| Using `Optional[X]` from typing | Use `X \| None` — modern Python 3.14 syntax |
| Using `List`, `Dict`, `Tuple` from typing | Use built-in `list`, `dict`, `tuple` — typing generics are deprecated |
| Using `Any` type hint | Find the correct type — `Any` defeats the purpose of type checking |
| Mutable defaults in dataclass fields | Use `field(default_factory=dict)` — mutable defaults are shared across instances |
| Using `yaml.load()` | Security risk — always `yaml.safe_load()` |
| Missing `encoding='utf-8'` on file I/O | Causes encoding bugs on different platforms |
| String comparison for paths | Use `Path.resolve()` — handles symlinks and relative paths correctly |
| Mocking file operations in tests | Use `tmp_path` fixture for real file system tests |

## Code Generation Rules

1. **Read before writing** — always read the target module and 1-2 similar modules before generating code
2. **Match existing patterns** — check how similar functionality is implemented in the codebase
3. **Result dataclasses** — every new operation returns a result dataclass with action/status + optional error
4. **Type hints everywhere** — all function signatures, all dataclass fields, all variables where non-obvious
5. **On correction** — acknowledge, restate as rule, apply to all subsequent output, **write to [LEARNED.md](LEARNED.md)** under `## Corrections`
6. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then existing code, ask ONE question, **write to [LEARNED.md](LEARNED.md)** under `## Preferences`

## Sub-Agent Delegation

| Agent | Role | Spawn When | Tools |
|-------|------|------------|-------|
| [code-reviewer](agents/code-reviewer.md) | Read-only convention compliance check | PR review, code audit, architecture check | Read Glob Grep |
| [test-writer](agents/test-writer.md) | pytest test generation | "Write tests for X", new module, coverage gaps | Read Edit Write Bash Glob Grep |
| [security-scanner](agents/security-scanner.md) | OWASP security audit | Security review, pre-deploy check, dependency audit | Read Glob Grep |

### Delegation Rules

1. Delegate when task has distinct phases or needs security isolation (read-only analysis)
2. Stay inline for simple, single-focus tasks
3. Cap at 3 sub-agents per workflow
4. Pass ALL context explicitly — sub-agents don't see parent conversation
5. Sub-agents CANNOT spawn their own sub-agents (max depth = 1)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode | Detection Signal | Behavior |
|------|-----------------|----------|
| Diagnostic | Traceback, "doesn't work", "wrong result", error output | Read module, check types/paths/error handling, diagnose root cause first |
| Efficient | "Another module like X", "Add Y to Z", Nth similar task | Minimal explanation, match existing patterns, generate directly |
| Teaching | "What is a result dataclass", "why pathlib", "explain this pattern" | Explain rationale, reference code-style.md, show existing examples |
| Review | "Check this code", "audit module X", "review my changes" | Read-only analysis, delegate to code-reviewer agent, report findings |

**Proficiency Calibration:**

| Signal Type | Indicators | Behavior |
|-------------|-----------|----------|
| Senior | Modifies generated code, asks about trade-offs, references internals | Lead with code, rationale on non-obvious only |
| Learning | Asks "what is...", copies unchanged, pastes errors without analysis | Teaching mode, explain why not just how, link to docs |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Freedom Levels

| Level | Scope | Examples |
|-------|-------|---------|
| **MUST** follow | pathlib.Path, result dataclasses, type hints, single quotes, encoding='utf-8', yaml.safe_load, no shell=True | "MUST return result dataclass", "MUST use pathlib.Path" |
| **SHOULD** follow | Class-based test organization, module docstrings, frozen for config, lru_cache for discovery | "SHOULD use frozen=True for config dataclasses" |
| **CAN** customize | Test helper naming, docstring detail level, specific lru_cache maxsize | "CAN choose between one-liner and multi-line docstrings" |

## References

| File | Description |
|------|-------------|
| [LEARNED.md](LEARNED.md) | **Auto-updated.** Corrections, preferences, conventions across sessions |
| [INJECT.md](INJECT.md) | Always-loaded quick reference (hallucination firewall) |
| [references/api-patterns.md](references/api-patterns.md) | CLI patterns, subprocess spawning, stream parsing, config persistence |
| [references/code-style.md](references/code-style.md) | Import order, naming, type hints, dataclass patterns, formatting |
| [references/security-checklist.md](references/security-checklist.md) | Per-module OWASP security verification checklists |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols |
| [references/test-patterns.md](references/test-patterns.md) | pytest conventions, fixtures, mocking, assertion patterns |
| [references/common-issues.md](references/common-issues.md) | Troubleshooting common backend Python pitfalls |
| [references/model-template.py](references/model-template.py) | Copy-paste module template with dataclasses and patterns |
| [assets/env-example](assets/env-example) | Environment variable template |
| [scripts/validate-backend.sh](scripts/validate-backend.sh) | Backend convention and naming validator |
