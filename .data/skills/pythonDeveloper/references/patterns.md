# Python Patterns — Generic Reference

> Full code examples for key patterns used in production Python projects. Referenced from SKILL.md Key Patterns table.

---

## Result Object Pattern

All operations that can fail return result dataclasses instead of raising exceptions:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OperationResult:
    success: bool
    message: str
    data: dict | None = None
    error: str | None = None


def process_file(source: Path, target: Path) -> OperationResult:
    """Process a file from source to target location.

    Args:
        source: Path to the input file.
        target: Path to write the output.

    Returns:
        OperationResult with success status.
    """
    if not source.exists():
        return OperationResult(
            success=False,
            message='Source not found',
            error=f'Path does not exist: {source}',
        )

    try:
        content = source.read_text(encoding='utf-8')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return OperationResult(
            success=True,
            message=f'Processed {source.name}',
        )
    except OSError as exc:
        return OperationResult(
            success=False,
            message='Processing failed',
            error=str(exc),
        )
```

---

## Data Validation Pattern (Pydantic)

Validate at API boundaries using Pydantic models:

```python
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

    @field_validator('name')
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name must not be blank')
        return v.strip()


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    model_config = {'from_attributes': True}
```

---

## Data Validation Pattern (Dataclasses)

For projects not using Pydantic, use dataclasses with manual validation:

```python
from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    """Immutable application configuration."""

    host: str
    port: int
    debug: bool = False
    allowed_origins: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self):
        if not 1 <= self.port <= 65535:
            raise ValueError(f'Port must be 1-65535, got {self.port}')


@dataclass
class TaskResult:
    """Mutable result object for task operations."""

    task_id: str
    status: str
    output: str | None = None
    error: str | None = None
```

---

## Repository Pattern

Separate data access from business logic:

```python
from dataclasses import dataclass
from pathlib import Path


@dataclass
class User:
    id: int
    name: str
    email: str


class UserRepository:
    """Data access layer for users."""

    def __init__(self, db_session) -> None:
        self._session = db_session

    def get_by_id(self, user_id: int) -> User | None:
        row = self._session.execute(
            'SELECT id, name, email FROM users WHERE id = :id',
            {'id': user_id},
        ).fetchone()
        if row is None:
            return None
        return User(id=row.id, name=row.name, email=row.email)

    def create(self, name: str, email: str) -> User:
        result = self._session.execute(
            'INSERT INTO users (name, email) VALUES (:name, :email) RETURNING id',
            {'name': name, 'email': email},
        )
        self._session.commit()
        return User(id=result.fetchone().id, name=name, email=email)


class UserService:
    """Business logic for user operations."""

    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def get_user(self, user_id: int) -> OperationResult:
        user = self._repo.get_by_id(user_id)
        if user is None:
            return OperationResult(
                success=False,
                message='User not found',
                error=f'No user with id={user_id}',
            )
        return OperationResult(
            success=True,
            message='User found',
            data={'id': user.id, 'name': user.name, 'email': user.email},
        )
```

---

## FastAPI Route Pattern

Thin route handlers that delegate to services:

```python
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Create a new user."""
    result = await service.create_user(request.name, request.email)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )
    return UserResponse(**result.data)


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: int,
    service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Get a user by ID."""
    result = await service.get_user(user_id)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.error,
        )
    return UserResponse(**result.data)
```

---

## CLI Command Pattern (click/typer)

```python
import click

from your_project.services import process_data


@click.group()
def cli():
    """YOUR_PROJECT command-line interface."""


@cli.command()
@click.argument('input_path', type=click.Path(exists=True, path_type=Path))
@click.option('--output', '-o', type=click.Path(path_type=Path), default=None)
@click.option('--verbose', '-v', is_flag=True, default=False)
def process(input_path: Path, output: Path | None, verbose: bool) -> None:
    """Process input data and write results."""
    if output is None:
        output = input_path.with_suffix('.out')

    result = process_data(input_path, output)
    if not result.success:
        click.echo(f'Error: {result.error}', err=True)
        raise SystemExit(1)

    if verbose:
        click.echo(f'Processed: {result.message}')
    click.echo(f'Output written to {output}')
```

---

## Async Streaming Pattern

```python
import asyncio
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass


@dataclass
class StreamProgress:
    kind: str          # 'data', 'status', 'error', 'complete'
    content: str
    metadata: dict | None = None


async def stream_process(
    source: str,
    on_progress: Callable[[StreamProgress], None] | None = None,
) -> list[str]:
    """Process data with streaming progress updates."""
    results: list[str] = []

    async for chunk in _fetch_chunks(source):
        results.append(chunk)
        if on_progress:
            on_progress(StreamProgress(
                kind='data',
                content=chunk,
            ))

    if on_progress:
        on_progress(StreamProgress(
            kind='complete',
            content=f'Processed {len(results)} chunks',
        ))

    return results


async def _fetch_chunks(source: str) -> AsyncIterator[str]:
    """Fetch data chunks from source."""
    # Implementation depends on source type
    yield 'chunk_1'
    yield 'chunk_2'
```

---

## Configuration Pattern

```python
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    """Application settings loaded from environment."""

    database_url: str
    secret_key: str
    debug: bool = False
    host: str = '0.0.0.0'
    port: int = 8000
    allowed_origins: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_env(cls) -> 'AppSettings':
        origins = os.environ.get('ALLOWED_ORIGINS', '')
        return cls(
            database_url=os.environ['DATABASE_URL'],
            secret_key=os.environ['SECRET_KEY'],
            debug=os.environ.get('DEBUG', '').lower() == 'true',
            host=os.environ.get('HOST', '0.0.0.0'),
            port=int(os.environ.get('PORT', '8000')),
            allowed_origins=tuple(o.strip() for o in origins.split(',') if o.strip()),
        )
```

---

## Error Hierarchy Pattern

```python
class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        super().__init__(message)
        self.code = code


class NotFoundError(AppError):
    """Resource was not found."""

    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(f'{resource} not found: {identifier}', code='NOT_FOUND')
        self.resource = resource
        self.identifier = identifier


class ValidationError(AppError):
    """Input validation failed."""

    def __init__(self, field: str, reason: str) -> None:
        super().__init__(f'Validation failed for {field}: {reason}', code='VALIDATION')
        self.field = field
        self.reason = reason


class AuthorizationError(AppError):
    """User is not authorized for this action."""

    def __init__(self, action: str) -> None:
        super().__init__(f'Not authorized: {action}', code='UNAUTHORIZED')
        self.action = action
```
