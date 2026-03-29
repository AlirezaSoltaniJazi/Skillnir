# Python Code Style Guide

> Import order, formatting, naming, transaction patterns, and structural conventions for the Skillnir project.

---

## Formatting Rules

| Rule | Value |
|------|-------|
| Formatter | Black 26.3.1 |
| Python target | 3.14 |
| String quotes | Single quotes (`-S` flag) |
| Line length | 100 characters (Black default) |
| Linter | Pylint (`.pylintrc`, fail-under=10) |
| Unused code | Autoflake (removes unused imports/variables) |
| Security | Bandit (`-lll -iii` threshold) |
| Markdown | Prettier 3.8.1 |

---

## Import Order

Standard library → Third-party → Local (absolute imports only):

```python
"""Module docstring — one line, ends with period."""

import functools
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Callable

import yaml
import questionary
from nicegui import ui

from skillnir.backends import AIBackend, AppConfig, load_config
from skillnir.skills import Skill, discover_skills
from skillnir.syncer import SyncResult, sync_skill
```

**Rules:**
- Always absolute imports (`from skillnir.X import Y`)
- Never relative imports (`from .X import Y`)
- Group: stdlib, then blank line, then third-party, then blank line, then local
- isort is commented out in pre-commit — manual ordering expected

---

## Naming Conventions

```python
# Constants — UPPER_SNAKE_CASE
BACKENDS: dict[AIBackend, BackendInfo] = {}
TOOLS: tuple[AITool, ...] = ()
SCOPE_LABELS: dict[str, str] = {}
CONFIG_DIR = Path.home() / '.skillnir'

# Classes — PascalCase
class AIBackend(Enum):
    CLAUDE = 'claude'

@dataclass
class SyncResult:
    skill_name: str

@dataclass(frozen=True)
class BackendInfo:
    id: AIBackend

# Functions — snake_case
def sync_skill(source_dir: Path, target_dir: Path, skill_name: str) -> SyncResult:
    """Sync a single skill from source to target."""

# Private functions — _leading_underscore
def _get_skill_version(skill_dir: Path) -> str:
    """Extract version from a skill's SKILL.md frontmatter."""

# Properties — snake_case
@property
def dir_name(self) -> str:
    """The actual directory name on disk."""
    return self.path.name
```

---

## Type Hints

Comprehensive type hints on ALL function signatures. Use modern Python 3.14 syntax:

```python
# Union types — use pipe operator
target_version: str | None = None
usage_command: tuple[str, ...] | None = None

# Generic collections — use built-in types
models: tuple[ModelInfo, ...]
results: list[SyncResult] = []
actions: dict[str, str] = {}

# Callable types
on_progress: Callable[[str], None] | None = None

# Dataclass fields with defaults
slash_commands: dict[str, str] = field(default_factory=dict)
mode_flags: dict[str, list[str]] = field(default_factory=dict)

# Never use Any unless absolutely unavoidable
# Never use Optional[X] — use X | None instead
# Never use List, Dict, Tuple from typing — use list, dict, tuple
```

---

## Docstring Format

One-liner docstrings with period. No param/return documentation (types are in signatures):

```python
def discover_skills(project_root: Path) -> list[Skill]:
    """Discover skills from a project's .data/skills/ directory."""

def sync_skill(source_dir: Path, target_dir: Path, skill_name: str) -> SyncResult:
    """Sync a single skill from source to target with version comparison."""

def _ask_target_project() -> Path:
    """Ask user for target project root, default cwd."""
```

Multi-line docstrings for complex functions:

```python
def sync_skills(source_dir: Path, target_dir: Path) -> list[SyncResult]:
    """Sync skills from source to target with version comparison.

    For each skill in source_dir:
    - Missing in target → copy entire directory
    - Same version → skip
    - Different version → remove old + copy new
    """
```

Module docstrings at top of every file:

```python
"""Multi-backend support for AI generation (Claude, Gemini, Copilot)."""
```

---

## Dataclass Patterns

### Frozen for Configuration (Immutable)

```python
@dataclass(frozen=True)
class BackendInfo:
    """Static metadata for a backend."""
    id: AIBackend
    name: str
    cli_command: str
    supports_stream_json: bool
    models: tuple[ModelInfo, ...]
    default_model: str
    icon: str
    slash_commands: dict[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class ModelInfo:
    """A model available in a backend."""
    id: str
    alias: str
    display_name: str
    is_default: bool = False
```

### Regular for Results (Mutable/Output)

```python
@dataclass
class SyncResult:
    skill_name: str
    action: str  # "copied" | "updated" | "skipped"
    source_version: str
    target_version: str | None = None

@dataclass
class GenerationResult:
    success: bool
    error: str | None = None
    backend_used: AIBackend | None = None
```

---

## Path Operations

Always use `pathlib.Path`, never `os.path`:

```python
from pathlib import Path

# Reading files — always specify encoding
text = skill_md.read_text(encoding='utf-8')
data = json.loads(config_file.read_text(encoding='utf-8'))

# Writing files — always specify encoding
config_file.write_text(json.dumps(data, indent=2), encoding='utf-8')

# Creating directories — parents=True, exist_ok=True
target_dir.mkdir(parents=True, exist_ok=True)

# Checking existence before operations
if not skill_md.exists():
    return 'unknown'
if not skills_dir.is_dir():
    return []

# Iterating directories — always sorted for deterministic output
for entry in sorted(skills_dir.iterdir()):
    if entry.is_dir() and (entry / 'SKILL.md').exists():
        ...

# Resolving paths for comparison
if source_dir.resolve() == target_dir.resolve():
    return []  # Same directory — skip to avoid data loss
```

---

## Enum Patterns

```python
from enum import Enum

class AIBackend(Enum):
    """Supported generation backends."""
    CLAUDE = 'claude'
    CURSOR = 'cursor'
    GEMINI = 'gemini'
    COPILOT = 'copilot'
```

- Enum values are lowercase strings
- Enum class has a docstring
- Used for fixed sets of choices, never plain strings

---

## Error Handling

Result dataclasses instead of exceptions for expected outcomes:

```python
# GOOD — result-based
def sync_skill(...) -> SyncResult:
    if not target_skill_dir.exists():
        shutil.copytree(source_skill_dir, target_skill_dir)
        return SyncResult(skill_name=skill_name, action='copied', source_version=source_version)

# BAD — exception-based
def sync_skill(...) -> None:
    if not target_skill_dir.exists():
        shutil.copytree(source_skill_dir, target_skill_dir)
    else:
        raise SkillAlreadyExistsError(skill_name)  # Don't do this
```

Try/except only for truly exceptional cases (I/O errors, subprocess failures):

```python
try:
    data = json.loads(config_file.read_text(encoding='utf-8'))
    return AppConfig.from_dict(data)
except (json.JSONDecodeError, KeyError):
    return AppConfig()  # Graceful fallback
```

---

## Pre-commit Configuration

All hooks exclude `.data/` directory:

```yaml
# .pre-commit-config.yaml patterns
exclude: ^\.data/  # Applied to autoflake, pylint, black
```

Running pre-commit manually:

```bash
pre-commit run --all-files    # Run all hooks
pre-commit run black          # Run specific hook
pre-commit run pylint         # Run specific hook
```
