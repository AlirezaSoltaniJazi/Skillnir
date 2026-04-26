# Test Patterns — Generic Python Reference

> Pytest fixtures, async tests, mocking patterns, and test organization examples.

---

## Test File Structure

```python
"""Tests for your_project.services module."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from your_project.models import User, UserCreate
from your_project.services import UserService


class TestCreateUser:
    """Tests for UserService.create_user method."""

    def test_creates_user_with_valid_data(self, user_service, sample_user_data):
        result = user_service.create_user(**sample_user_data)
        assert result.success is True
        assert result.data['name'] == sample_user_data['name']
        assert result.error is None

    def test_returns_error_for_duplicate_email(self, user_service, existing_user):
        result = user_service.create_user(
            name='Another User',
            email=existing_user.email,
        )
        assert result.success is False
        assert 'duplicate' in result.error.lower()

    def test_returns_error_for_empty_name(self, user_service):
        result = user_service.create_user(name='', email='test@example.com')
        assert result.success is False
        assert result.error is not None
```

---

## Conftest Fixtures

Located in `tests/conftest.py`:

```python
"""Shared test fixtures for the test suite."""

import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from your_project.config import AppSettings
from your_project.models import User


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory with standard structure."""
    src_dir = tmp_path / 'src'
    src_dir.mkdir()
    tests_dir = tmp_path / 'tests'
    tests_dir.mkdir()
    return tmp_path


@pytest.fixture
def sample_user_data() -> dict:
    """Provide sample user creation data."""
    return {
        'name': 'Test User',
        'email': 'test@example.com',
        'role': 'user',
    }


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    session = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    return session


@pytest.fixture
def user_service(mock_db_session):
    """Create a UserService with mocked database."""
    from your_project.repositories import UserRepository
    repo = UserRepository(mock_db_session)
    return UserService(repo)


@pytest.fixture
def test_settings(tmp_path: Path) -> AppSettings:
    """Create test application settings."""
    return AppSettings(
        database_url='sqlite:///test.db',
        secret_key='test-secret-key-not-for-production',
        debug=True,
        host='127.0.0.1',
        port=8000,
    )
```

---

## Async Test Patterns

With `asyncio_mode = "auto"` in `pyproject.toml`, async tests are detected automatically:

```python
"""Tests for async service functions."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from your_project.services import fetch_data, process_stream


class TestFetchData:
    """Tests for async fetch_data function."""

    async def test_returns_data_on_success(self):
        with patch('your_project.services.httpx.AsyncClient') as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'key': 'value'}
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(get=AsyncMock(return_value=mock_response))
            )

            result = await fetch_data('https://api.example.com/data')

        assert result.success is True
        assert result.data == {'key': 'value'}

    async def test_handles_network_error(self):
        with patch('your_project.services.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__ = AsyncMock(
                return_value=MagicMock(
                    get=AsyncMock(side_effect=ConnectionError('timeout'))
                )
            )

            result = await fetch_data('https://api.example.com/data')

        assert result.success is False
        assert 'timeout' in result.error


class TestProcessStream:
    """Tests for async streaming function."""

    async def test_streams_progress_callbacks(self):
        progress_calls: list = []

        def on_progress(p) -> None:
            progress_calls.append(p)

        await process_stream('source', on_progress=on_progress)

        assert len(progress_calls) > 0
        assert progress_calls[-1].kind == 'complete'
```

---

## Mocking Patterns

### External API Mocking

```python
from unittest.mock import patch, MagicMock


def test_api_call_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'id': 1, 'name': 'Test'}

    with patch('your_project.client.httpx.get', return_value=mock_response):
        result = fetch_resource(1)

    assert result.success is True
    assert result.data['name'] == 'Test'
```

### Database Mocking

```python
def test_user_not_found(mock_db_session):
    mock_db_session.execute.return_value.fetchone.return_value = None
    repo = UserRepository(mock_db_session)

    user = repo.get_by_id(999)

    assert user is None
```

### Filesystem (Real with tmp_path)

```python
def test_reads_config_from_file(tmp_path: Path):
    config_file = tmp_path / 'config.json'
    config_file.write_text('{"key": "value"}', encoding='utf-8')

    result = load_config(config_file)

    assert result == {'key': 'value'}


def test_handles_missing_config(tmp_path: Path):
    config_path = tmp_path / 'config.json'
    # Don't create the file — test missing file handling
    result = load_config(config_path)
    assert result is None
```

### Subprocess Mocking

```python
from unittest.mock import MagicMock, patch


def test_subprocess_execution():
    mock_proc = MagicMock()
    mock_proc.stdout = iter(['line 1\n', 'line 2\n'])
    mock_proc.stderr = iter([])
    mock_proc.returncode = 0
    mock_proc.wait.return_value = 0

    with patch('subprocess.Popen', return_value=mock_proc):
        result = run_external_tool('arg1', 'arg2')

    assert result.success is True
```

### Environment Variable Mocking

```python
def test_settings_from_env(monkeypatch):
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///test.db')
    monkeypatch.setenv('SECRET_KEY', 'test-key')
    monkeypatch.setenv('DEBUG', 'true')

    settings = AppSettings.from_env()

    assert settings.database_url == 'sqlite:///test.db'
    assert settings.debug is True
```

---

## Pytest Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks integration tests",
]
```

---

## Test Organization Rules

1. One test file per source module: `test_services.py` tests `services.py`
2. Class-based grouping: `class TestFunctionName` groups related tests
3. Test method naming: `test_{behavior}_when_{condition}`
4. Fixtures for setup: never use `setUp`/`tearDown` — use pytest fixtures
5. `tmp_path` for filesystem: always use pytest's built-in temp directory fixture
6. Minimal mocking: only mock external boundaries (network, database, expensive I/O)
7. Assert one thing: each test method should verify one behavior
8. Use `monkeypatch` for environment variables, not `os.environ` manipulation
9. Mark slow/integration tests with `@pytest.mark.slow` / `@pytest.mark.integration`
10. Use `parametrize` for testing multiple inputs against the same logic
