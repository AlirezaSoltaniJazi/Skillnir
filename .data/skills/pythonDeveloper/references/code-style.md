# Python Code Style — Generic Reference

> Import order, type hints, naming conventions, and formatting rules with full examples.

---

## Import Order

Three groups, separated by blank lines. Within each group, `import` statements first, then `from` statements, alphabetically sorted:

```python
import json
import logging
import subprocess
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from your_project.config import settings
from your_project.models import User, UserCreate
from your_project.services import UserService
```

**Rules**:

- stdlib imports first
- Third-party imports second
- Local (`your_project.*`) imports third
- Never use relative imports (`from .module import X` is forbidden)
- Never use wildcard imports (`from module import *`)
- Import specific names, not entire modules when only a few names are needed

---

## Type Hints

Use modern Python 3.10+ syntax exclusively:

```python
# Correct — modern union syntax
def process(name: str, count: int | None = None) -> list[str]:
    ...

# Wrong — deprecated typing imports
from typing import Optional, List, Dict
def process(name: str, count: Optional[int] = None) -> List[str]:
    ...
```

### Common Type Patterns

```python
from collections.abc import Callable, Iterator, AsyncIterator
from pathlib import Path

# Union types
value: str | None = None
result: int | float = 0

# Generic builtins (lowercase)
names: list[str] = []
config: dict[str, str] = {}
coordinates: tuple[float, float] = (0.0, 0.0)
unique_ids: set[int] = set()

# Callable with optional parameter
on_progress: Callable[[str], None] | None = None

# Path parameters
def read_file(path: Path) -> str:
    ...

# Self type (Python 3.11+)
from typing import Self

class Builder:
    def set_name(self, name: str) -> Self:
        self.name = name
        return self

# TypeVar for generics
from typing import TypeVar

T = TypeVar('T')

def first(items: list[T]) -> T | None:
    return items[0] if items else None

# Protocol for structural typing
from typing import Protocol

class Readable(Protocol):
    def read(self) -> str: ...
```

---

## Naming Conventions

| Category         | Style                  | Examples                                        |
| ---------------- | ---------------------- | ----------------------------------------------- |
| Modules          | `snake_case`           | `user_service.py`, `data_processor.py`          |
| Classes          | `PascalCase`           | `UserService`, `OrderResult`, `AppConfig`       |
| Functions        | `snake_case`           | `create_user`, `process_data`, `validate_input` |
| Private funcs    | `_snake_case`          | `_build_query`, `_format_output`                |
| Constants        | `SCREAMING_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_TIMEOUT`, `API_VERSION` |
| Variables        | `snake_case`           | `user_name`, `file_path`, `retry_count`         |
| Dataclass fields | `snake_case`           | `created_at`, `is_active`, `error_message`      |
| Enum values      | `SCREAMING_SNAKE_CASE` | `Status.ACTIVE`, `Role.ADMIN`                   |
| Type aliases     | `PascalCase`           | `UserId = int`, `JsonDict = dict[str, Any]`     |

---

## Docstrings

Google-style, selective use. Module docstrings are one-liners. Function docstrings include brief description and optionally Args/Returns:

```python
"""Core user management — CRUD operations and validation."""


def create_user(name: str, email: str, role: str = 'user') -> UserResult:
    """Create a new user with the given details.

    Args:
        name: Display name for the user.
        email: Unique email address.
        role: User role, defaults to 'user'.

    Returns:
        UserResult with created user data or error details.

    Raises:
        AuthorizationError: If current user lacks admin role.
    """
```

**Rules**:

- Every module gets a one-line docstring
- Public functions get at minimum a one-line description
- Private functions (`_func`) may omit docstrings if self-explanatory
- Args/Returns sections are optional but encouraged for complex functions
- Use type hints in signatures, not in docstrings
- Document raised exceptions only for unexpected/propagated exceptions

---

## String Style

Choose one convention and enforce via formatter:

```python
# Single quotes (Black -S / ruff)
name = 'your_project'
message = f'Processing {count} items'

# OR double quotes (Black default / ruff default)
name = "your_project"
message = f"Processing {count} items"

# Multiline — implicit concatenation
multiline = (
    'This is a long string that spans '
    'multiple lines using implicit concatenation'
)

# Exception: Docstrings always use triple double quotes
"""This is a docstring."""
```

---

## Dataclass Style

```python
from dataclasses import dataclass, field


# Immutable data — use frozen=True
@dataclass(frozen=True)
class AppConfig:
    name: str
    version: str
    tags: tuple[str, ...] = field(default_factory=tuple)


# Mutable result — regular dataclass
@dataclass
class ProcessResult:
    status: str
    output: str | None = None
    error: str | None = None
    items_processed: int = 0
```

---

## Error Handling Style

```python
# Correct — specific exceptions, result objects
try:
    content = path.read_text(encoding='utf-8')
except FileNotFoundError:
    return ProcessResult(status='failed', error='File not found')
except OSError as exc:
    return ProcessResult(status='failed', error=str(exc))

# Wrong — bare except, generic exception
try:
    content = path.read_text()
except:
    raise Exception('Something went wrong')
```

---

## File Organization

Each module follows this structure:

```python
"""One-line module description — what this module does."""

# stdlib imports
import json
import logging
from pathlib import Path

# third-party imports
from pydantic import BaseModel

# local imports
from your_project.models import User

# module-level constants
logger = logging.getLogger(__name__)
DEFAULT_TIMEOUT = 30
SUPPORTED_FORMATS = ('json', 'yaml', 'toml')


# dataclasses / models
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

---

## Logging Style

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug('Processing file: %s', file_path)
logger.info('User created: user_id=%d', user.id)
logger.warning('Retry attempt %d/%d for %s', attempt, max_retries, url)
logger.error('Failed to process: %s', exc, exc_info=True)

# Never use f-strings in log calls (lazy formatting for performance)
# Wrong:
logger.info(f'Processing {file_path}')
# Correct:
logger.info('Processing %s', file_path)
```
