# Skillnir — AI Agent Context

## What This Is

CLI + Web UI tool that generates, manages, and injects domain-specific AI skills into 35+ AI coding tool directories (.claude/, .cursor/, .github/, .windsurf/, etc.). Skills are structured markdown directories symlinked from a central `.data/skills/` store into each tool's dotdir. Python 3.14+, built with NiceGUI, questionary, and claude-agent-sdk.

## Stack

| Component      | Technology                                                                                                        |
| -------------- | ----------------------------------------------------------------------------------------------------------------- |
| Language       | Python 3.14+                                                                                                      |
| Build          | hatchling + uv (package manager)                                                                                  |
| CLI            | argparse + questionary (interactive prompts)                                                                      |
| Web UI         | NiceGUI 2.0+                                                                                                      |
| AI Generation  | claude-agent-sdk + subprocess backends                                                                            |
| Config Parsing | PyYAML (SKILL.md frontmatter)                                                                                     |
| Testing        | pytest + pytest-asyncio                                                                                           |
| Linting        | Black (-S), Pylint, Autoflake, Bandit, Prettier                                                                   |
| Pre-commit     | 7 hooks (trailing-whitespace, EOF, YAML, AST, merge-conflict, safety, bandit, autoflake, pylint, black, prettier) |

## Project Structure

```
src/skillnir/              # Core package (all modules)
├── cli.py                 # CLI entry point — 15 commands, argparse + questionary
├── skill_generator.py     # Multi-backend skill generation (async SDK + subprocess)
├── researcher.py          # AI news research and summarization
├── backends.py            # Backend registry (Claude, Cursor, Gemini, Copilot)
├── generator.py           # AI docs (agents.md) generation
├── rule_generator.py      # Cursor rule (.mdc) generation
├── scaffold.py            # Skill scaffolding and templates
├── injector.py            # Symlink injection into tool dotdirs
├── syncer.py              # Version-aware skill synchronization
├── remover.py             # Skill and docs removal
├── tools.py               # AI tool registry (35+ tools, ratings)
├── hooks.py               # Claude Code sound notification hooks
├── skills.py              # Skill discovery and YAML frontmatter parsing
├── usage.py               # Usage statistics tracking
├── ui/                    # NiceGUI web interface
│   ├── layout.py          # Navigation structure (NAV_GROUPS)
│   ├── pages/             # 13+ page modules (one per feature)
│   └── components/        # 12 reusable UI components
└── resources/             # Static assets
.data/                     # Central skill storage (SOURCE OF TRUTH)
├── skills/                # Installed skills (symlinked into tool dotdirs)
│   └── <skillName>/       # camelCase directories
│       ├── SKILL.md       # Generated — NEVER edit manually
│       ├── INJECT.md      # Always-loaded summary (50-150 tokens)
│       ├── LEARNED.md     # AI-written session corrections
│       ├── references/    # Detailed docs and code samples
│       ├── scripts/       # Validation scripts
│       └── agents/        # Sub-agent definitions
├── promptsv1/             # 26+ skill generation prompt templates
└── research/articles/     # 100+ research articles on AI
tests/                     # 14 test files (pytest, class-based)
```

## How To Run

```bash
# Install dependencies
uv sync

# CLI (default command: install)
uv run skillnir --help
uv run skillnir generate-skill
uv run skillnir install

# Web UI
uv run skillnir ui

# Tests
uv run pytest
uv run pytest tests/test_injector.py    # single file

# Lint / format
uv run pre-commit run --all-files
```

## Development Conventions

### Code Style

- **Formatter**: Black with `-S` flag (no single quotes — double quotes only)
- **Line length**: 100 characters (enforced by .pylintrc)
- **Type hints**: Required on all function signatures. Use modern syntax: `str | None`, `tuple[str, ...]`, `list[X]`
- **Docstrings**: Triple-quoted, single-line for simple functions. No enforced style (Google/NumPy)
- **Imports**: Absolute only — never relative. Order: stdlib → third-party → `skillnir.*`
- **isort**: Disabled (commented out in pre-commit)

### Naming Conventions

| Context             | Convention | Example                       |
| ------------------- | ---------- | ----------------------------- |
| Functions/variables | snake_case | `inject_skill`, `skill_name`  |
| Classes             | PascalCase | `InjectionResult`, `AITool`   |
| Constants           | UPPER_CASE | `SOURCE_DOTDIR`, `TOOLS`      |
| Skill directories   | camelCase  | `backendEngineer`, `skillnir` |
| Module files        | snake_case | `skill_generator.py`          |

### Error Handling

Result dataclasses with optional error fields — preferred over raising exceptions:

```python
@dataclass
class InjectionResult:
    tool: AITool
    symlink_path: Path
    created: bool
    error: str | None = None
```

OS/file errors caught with specific exceptions (`OSError`, `FileNotFoundError`, `json.JSONDecodeError`), logged to result objects. No custom exception hierarchy.

### Data Modeling

- **Immutable configs**: `@dataclass(frozen=True)` — `ModelInfo`, `BackendInfo`, `AITool`
- **Mutable results**: `@dataclass` — `InjectionResult`, `SyncResult`, `SkillGenerationResult`
- **No ORM** — all filesystem-based persistence

## Architecture Rules

- **`.data/skills/` is the single source of truth.** Tool dotdirs (`.claude/skills/`, `.cursor/skills/`) contain only symlinks pointing back to `.data/skills/`.
- **Symlinks are always relative**: `../../.data/skills/<skillName>` — never absolute paths.
- **SKILL.md is generated — never edit manually.** It gets overwritten on regeneration.
- **LEARNED.md is AI-written.** Session corrections and discovered conventions go here.
- **INJECT.md is a hallucination firewall.** Max 50-150 tokens, bullet-point only.
- **Dual execution paths**: Skill generation supports both async SDK (Claude) and subprocess CLI (Cursor/Gemini/Copilot). Both must be maintained.
- **No relative imports.** Always `from skillnir.X import Y`.
- **All filesystem paths use `pathlib.Path`** — never raw strings.

## Files To Know

| File                        | Purpose                                                                         |
| --------------------------- | ------------------------------------------------------------------------------- |
| `src/skillnir/cli.py`       | CLI entry point — `main()` at bottom, 15 commands                               |
| `src/skillnir/tools.py`     | AI tool registry — `TOOLS` tuple, `AITool` dataclass, `SOURCE_DOTDIR` constant  |
| `src/skillnir/backends.py`  | Backend configs — `BACKENDS` dict, `BackendInfo`, model lists                   |
| `src/skillnir/skills.py`    | Skill discovery — `Skill` dataclass, `parse_frontmatter()`, `discover_skills()` |
| `src/skillnir/injector.py`  | Symlink creation — `inject_skill()`                                             |
| `src/skillnir/scaffold.py`  | Skill template scaffolding                                                      |
| `src/skillnir/ui/layout.py` | Web UI navigation structure                                                     |
| `pyproject.toml`            | Build config, deps, entry point                                                 |
| `.pylintrc`                 | Linting rules (100 char, snake_case)                                            |
| `.pre-commit-config.yaml`   | 7 pre-commit hooks                                                              |

## Files To Never Touch

- `.data/promptsv*/` — Generation prompt templates, input to AI (edit only intentionally)
- `.data/research/` — Archived research articles
- `.data/skills/*/SKILL.md` — Generated files, overwritten on regeneration
- `uv.lock` — Auto-generated dependency lock (use `uv sync` to update)
- `.github/skills/` — Symlinks to `.data/skills/` (auto-created by injector)
- `.nicegui/` — NiceGUI persistence storage

## Common Patterns

### Adding a new AI tool to the registry

```python
# In src/skillnir/tools.py — append to TOOLS tuple
AITool(
    "ToolName",
    ".tooldir",
    "CompanyName",
    popularity=5,
    performance=5,
    price=5,
    icon_url="https://github.com/org.png?size=32",
)
```

### Adding a new CLI command

```python
# In src/skillnir/cli.py
# 1. Add subparser in build_parser()
sub = subparsers.add_parser("my-command", help="Does something")
sub.add_argument("--flag", help="A flag")

# 2. Add handler function
def cmd_my_command(args):
    """Handle my-command."""
    # Implementation using questionary for interactive prompts
    pass

# 3. Wire in main() dispatch
elif args.command == "my-command":
    cmd_my_command(args)
```

### Creating a result dataclass

```python
@dataclass
class MyResult:
    name: str
    success: bool
    error: str | None = None
```

### Discovering and injecting a skill

```python
from skillnir.skills import discover_skills
from skillnir.injector import inject_skill
from skillnir.tools import TOOLS

skills = discover_skills(project_root)
for skill in skills:
    results = inject_skill(project_root, skill, list(TOOLS))
```

## Environment Variables

No `.env` file used. Configuration stored in `~/.skillnir/config.json`:

```json
{ "backend": "claude", "model": "claude-opus-4-6", "prompt_version": "v1" }
```

AI backends expect their CLIs in PATH: `claude`, `agent` (Cursor), `gemini`, `copilot`.

## External Services

- **Claude API** — via claude-agent-sdk (async, streaming)
- **Cursor/Gemini/Copilot CLIs** — subprocess calls to locally installed tools
- **No DB, cache, queue, or cloud storage** — all local filesystem

## Testing

```bash
uv run pytest                            # all tests
uv run pytest tests/test_injector.py     # single file
uv run pytest -k "test_creates_symlink"  # single test
```

- **Framework**: pytest + pytest-asyncio (asyncio_mode = "auto")
- **Organization**: Class-based (`TestInjectSkill`, `TestLoadSkillPrompt`)
- **Fixtures**: `tmp_path` (built-in) for temporary directories
- **Mocking**: `unittest.mock.patch` for function-level overrides
- **CI**: GitHub Actions runs `pytest --tb=short -q` on PRs

## Security

- **Bandit** scans all source code (`-lll -iii` — low noise)
- **Safety** checks dependencies for known CVEs
- **Pre-commit hooks** enforce both on every commit
- **No secrets in code** — backends use CLI tools already authenticated locally
- **Symlinks only** — injector never copies or modifies skill content

## Known Gotchas

- **Skill directories are camelCase** (`backendEngineer`), not snake_case — enforced by `to_camel_case()` in scaffold.py
- **Symlinks are relative** (`../../.data/skills/name`) — moving `.data/` breaks all injected skills
- **Dual execution paths** in `skill_generator.py`: async SDK (Claude only) vs subprocess CLI (all backends). Changes must work for both.
- **`SKILL.md` frontmatter is YAML** between `---` markers — `parse_frontmatter()` depends on this exact format
- **Prompt versions** auto-discovered from `.data/promptsv{N}/` directory names — cached with `@functools.lru_cache`
- **NiceGUI imports** only inside UI modules — never at package top level
- **Thread-safe usage tracker** uses `threading.Lock()` — don't bypass the `SessionUsageTracker` interface
- **Black `-S` flag** means NO single quotes — formatter enforces double quotes throughout
- **`.data/` excluded from autoflake and pylint** — prompt templates contain Python-like syntax that triggers false positives

## Freedom Levels

| MUST follow                           | SHOULD follow                   | CAN customize                        |
| ------------------------------------- | ------------------------------- | ------------------------------------ |
| Absolute imports only                 | Result dataclass error pattern  | UI page layout and components        |
| `pathlib.Path` for all filesystem ops | Class-based test organization   | Prompt template content              |
| camelCase skill directory names       | questionary for CLI interaction | Backend model lists                  |
| Relative symlinks for injection       | `frozen=True` for config models | Tool ratings (popularity/perf/price) |
| Type hints on all function signatures | Single-line docstrings          | Research article organization        |
| Black -S formatting (double quotes)   | `tmp_path` fixture in tests     | CLI argument names                   |
| `.data/skills/` as source of truth    | Streaming via callback pattern  | UI component styling                 |

## AI Interaction Guidelines

- **Interaction modes**: Teaching (conceptual questions, first encounters) · Efficient (repeated patterns, "just generate") · Diagnostic (errors, failures, tracebacks)
- **On correction**: AI restates as rule, applies consistently for the session, writes to LEARNED.md
- **On ambiguity**: Check LEARNED.md first, then SKILL.md, then ask ONE question
- **Self-learning**: On convention discovery → write to LEARNED.md with `YYYY-MM-DD: rule description` format
- **Skill activation**: Announce "Using: skillnir skill" when working with skill system files

## Skills Reference

> Project-specific conventions live in `.data/skills/`. Check before making architectural decisions.
> Skills available: backendEngineer, frontendEngineer, devopsEngineer, skillnir

## Sub-Agent Capabilities

> Some skills support sub-agent delegation for complex workflows.
> Skills with sub-agents: skillnir (has `agents/` subdirectory)
> Ensure `Agent` is in allowed-tools when using these skills.
