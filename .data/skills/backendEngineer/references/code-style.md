# Python Code Style — Skillnir Backend

> Import order, type hints, naming conventions, and formatting rules with full examples.

---

## Import Order

Three groups, separated by blank lines. Within each group, `import` statements first, then `from` statements, alphabetically sorted:

```python
import json
import shutil
import subprocess
import threading
from dataclasses import dataclass, field
from pathlib import Path

import questionary
import yaml
from nicegui import ui

from skillnir.backends import AIBackend, BACKENDS, load_config
from skillnir.skills import Skill, discover_skills
from skillnir.tools import AITool, TOOLS, detect_tools
```

**Rules**:
- stdlib imports first
- Third-party imports second
- Local (`skillnir.*`) imports third
- Never use relative imports (`from .module import X` is forbidden)
- Never use wildcard imports (`from module import *`)

---

## Type Hints

Use modern Python 3.10+ syntax exclusively:

```python
# ✅ Correct — modern union syntax
def process(name: str, count: int | None = None) -> list[str]:
    ...

# ❌ Wrong — deprecated typing imports
from typing import Optional, List, Dict
def process(name: str, count: Optional[int] = None) -> List[str]:
    ...
```

### Common Type Patterns

```python
from collections.abc import Callable
from pathlib import Path

# Union types
value: str | None = None
result: int | float = 0

# Generic builtins (lowercase)
names: list[str] = []
config: dict[str, str] = {}
coordinates: tuple[float, float] = (0.0, 0.0)

# Callable with optional parameter
on_progress: Callable[[str], None] | None = None

# Path parameters
def read_file(path: Path) -> str:
    ...

# Dataclass fields
from dataclasses import dataclass, field

@dataclass
class Config:
    name: str
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)
```

---

## Naming Conventions

| Category         | Style                  | Examples                                          |
| ---------------- | ---------------------- | ------------------------------------------------- |
| Modules          | `snake_case`           | `skill_generator.py`, `rule_generator.py`         |
| Classes          | `PascalCase`           | `AITool`, `GenerationProgress`, `BackendInfo`     |
| Functions        | `snake_case`           | `inject_skill`, `sync_skills`, `detect_tools`     |
| Private funcs    | `_snake_case`          | `_ask_target_project`, `_print_sync_report`       |
| Constants        | `SCREAMING_SNAKE_CASE` | `SKILL_SCOPES`, `BACKENDS`, `RTL_LANGUAGES`       |
| CLI commands     | `kebab-case`           | `generate-docs`, `delete-skill`, `check-skill`    |
| Variables        | `snake_case`           | `skill_name`, `project_root`, `backend_info`      |
| Dataclass fields | `snake_case`           | `symlink_path`, `is_default`, `display_name`      |
| Enum values      | `SCREAMING_SNAKE_CASE` | `AIBackend.CLAUDE`, `AIBackend.CURSOR`            |

---

## Docstrings

Google-style, selective use. Module docstrings are one-liners. Function docstrings include brief description and optionally Args/Returns:

```python
"""Core injection logic: create symlinks from tool dotdirs to central skills."""


def inject_skill(skill_path: Path, tool_dir: Path) -> InjectionResult:
    """Create symlink from tool directory to central skill storage.

    Args:
        skill_path: Absolute path to the skill in .data/skills/.
        tool_dir: Path to the AI tool's dotdir (e.g., .claude/).

    Returns:
        InjectionResult with created=True if symlink was new.
    """
```

**Rules**:
- Every module gets a one-line docstring
- Public functions get at minimum a one-line description
- Private functions (`_func`) may omit docstrings if self-explanatory
- Args/Returns sections are optional but encouraged for complex functions
- Use type hints in signatures, not in docstrings

---

## String Style

Single quotes enforced by Black `-S` flag:

```python
# ✅ Correct
name = 'skillnir'
message = f'Processing {count} skills'
multiline = (
    'This is a long string that spans '
    'multiple lines using implicit concatenation'
)

# ❌ Wrong
name = "skillnir"
message = f"Processing {count} skills"
```

**Exception**: Docstrings always use triple double quotes (`"""..."""`).

---

## Dataclass Style

```python
from dataclasses import dataclass, field


# Immutable data — use frozen=True
@dataclass(frozen=True)
class AITool:
    name: str
    dotdir: str
    company: str
    popularity: int
    performance: int
    price: int
    icon_url: str = ''


# Mutable result — regular dataclass
@dataclass
class SyncResult:
    skill_name: str
    action: str
    source_version: str | None = None
    target_version: str | None = None
    error: str | None = None
```

---

## Error Handling Style

```python
# ✅ Correct — specific exceptions, result objects
try:
    content = path.read_text(encoding='utf-8')
except FileNotFoundError:
    return SyncResult(skill_name=name, action='skipped', error='File not found')
except OSError as exc:
    return SyncResult(skill_name=name, action='skipped', error=str(exc))

# ❌ Wrong — bare except, generic exception
try:
    content = path.read_text()
except:
    raise Exception('Something went wrong')
```

---

## File Organization

Each module follows this structure:

```python
"""One-line module description."""

# stdlib imports
import json
from pathlib import Path

# third-party imports
import yaml

# local imports
from skillnir.skills import Skill

# module-level constants
DEFAULT_TIMEOUT = 30
SUPPORTED_FORMATS = ('yaml', 'json')


# dataclasses / named tuples
@dataclass
class ModuleResult:
    ...


# public functions
def public_function() -> ModuleResult:
    ...


# private functions
def _helper_function() -> str:
    ...
```
