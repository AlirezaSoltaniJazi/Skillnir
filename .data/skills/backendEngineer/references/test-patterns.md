# Test Patterns — Skillnir Backend

> Pytest fixtures, async tests, mocking patterns, and test organization examples.

---

## Test File Structure

```python
"""Tests for skillnir.injector module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.injector import InjectionResult, inject_skill
from skillnir.skills import Skill
from skillnir.tools import AITool


class TestInjectSkill:
    """Tests for inject_skill function."""

    def test_creates_symlink_when_none_exists(self, tmp_project, sample_skill):
        result = inject_skill(sample_skill.path, tmp_project / '.claude')
        assert result.created is True
        assert result.error is None
        assert result.symlink_path.is_symlink()

    def test_skips_when_symlink_already_exists(self, tmp_project, sample_skill):
        # First injection
        inject_skill(sample_skill.path, tmp_project / '.claude')
        # Second injection — should skip
        result = inject_skill(sample_skill.path, tmp_project / '.claude')
        assert result.created is False
        assert result.error is None

    def test_handles_permission_error(self, tmp_project, sample_skill):
        with patch('pathlib.Path.symlink_to', side_effect=OSError('Permission denied')):
            result = inject_skill(sample_skill.path, tmp_project / '.claude')
        assert result.created is False
        assert 'Permission denied' in result.error
```

---

## Conftest Fixtures

Located in `tests/conftest.py`:

```python
"""Shared test fixtures for skillnir test suite."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from skillnir.skills import Skill
from skillnir.tools import AITool


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temporary project with .data/skills/ and tool dotdirs."""
    skills_dir = tmp_path / '.data' / 'skills'
    skills_dir.mkdir(parents=True)

    # Create tool dotdirs
    for dotdir in ('.claude', '.cursor', '.github'):
        (tmp_path / dotdir).mkdir()

    return tmp_path


@pytest.fixture
def sample_skill(tmp_project: Path) -> Skill:
    """Create a sample skill in the temporary project."""
    skill_dir = tmp_project / '.data' / 'skills' / 'testSkill'
    skill_dir.mkdir(parents=True)

    skill_md = skill_dir / 'SKILL.md'
    skill_md.write_text(
        '---\n'
        'name: testSkill\n'
        'description: A test skill\n'
        'compatibility: "Python 3.14+"\n'
        'metadata:\n'
        '  version: "1.0.0"\n'
        'allowed-tools: Read Edit\n'
        '---\n'
        '\n'
        '## Test Skill Content\n',
        encoding='utf-8',
    )

    return Skill(name='testSkill', description='A test skill', version='1.0.0', path=skill_dir)


@pytest.fixture
def sample_tool() -> AITool:
    """Create a sample AITool for testing."""
    return AITool(
        name='Test Tool',
        dotdir='.test-tool',
        company='Test Co',
        popularity=5,
        performance=5,
        price=5,
    )


@pytest.fixture
def mock_config():
    """Mock AppConfig for testing."""
    config = MagicMock()
    config.backend = 'claude'
    config.model = 'sonnet'
    return config
```

---

## Async Test Patterns

With `asyncio_mode = "auto"` in `pyproject.toml`, async tests are detected automatically:

```python
"""Tests for async generation functions."""

from unittest.mock import AsyncMock, patch

import pytest

from skillnir.generator import GenerationProgress, generate_docs_sdk


class TestGenerateDocsSdk:
    """Tests for generate_docs_sdk async function."""

    async def test_streams_text_content(self):
        progress_calls: list[GenerationProgress] = []

        def on_progress(p: GenerationProgress) -> None:
            progress_calls.append(p)

        with patch('skillnir.generator.query') as mock_query:
            mock_query.return_value = AsyncMock()
            mock_query.return_value.__aiter__ = AsyncMock(
                return_value=iter([
                    MagicMock(type='text', content='Hello '),
                    MagicMock(type='text', content='World'),
                ])
            )

            result = await generate_docs_sdk('test prompt', 'sonnet', on_progress)

        assert result == 'Hello World'
        assert len(progress_calls) == 2
        assert progress_calls[0].kind == 'text'

    async def test_handles_empty_response(self):
        with patch('skillnir.generator.query') as mock_query:
            mock_query.return_value = AsyncMock()
            mock_query.return_value.__aiter__ = AsyncMock(return_value=iter([]))

            result = await generate_docs_sdk('test prompt', 'sonnet')

        assert result == ''
```

---

## Mocking Patterns

### Subprocess Mocking

```python
from unittest.mock import MagicMock, patch


def test_subprocess_generation(tmp_project):
    mock_proc = MagicMock()
    mock_proc.stdout = iter(['line 1\n', 'line 2\n'])
    mock_proc.stderr = iter([])
    mock_proc.returncode = 0
    mock_proc.wait.return_value = 0

    with patch('subprocess.Popen', return_value=mock_proc):
        result = generate_docs_subprocess('prompt', 'claude', tmp_project)

    assert result.success is True
```

### Filesystem Mocking

```python
def test_handles_missing_config(tmp_path):
    config_path = tmp_path / 'config.json'
    # Don't create the file — test missing file handling
    result = load_config(config_path)
    assert result is None
```

### Tool Detection Mocking

```python
from unittest.mock import patch


def test_detect_installed_tools(tmp_project):
    (tmp_project / '.claude').mkdir(exist_ok=True)
    (tmp_project / '.cursor').mkdir(exist_ok=True)

    with patch('shutil.which', return_value='/usr/bin/claude'):
        tools = detect_tools(tmp_project)

    assert any(t.dotdir == '.claude' for t in tools)
```

---

## Pytest Configuration

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

---

## Test Organization Rules

1. One test file per source module: `test_injector.py` tests `injector.py`
2. Class-based grouping: `class TestFunctionName` groups related tests
3. Test method naming: `test_{{behavior}}_when_{{condition}}`
4. Fixtures for setup: never use `setUp`/`tearDown` — use pytest fixtures
5. `tmp_path` for filesystem: always use pytest's built-in temp directory fixture
6. Minimal mocking: only mock external boundaries (subprocess, network, expensive I/O)
7. Assert one thing: each test method should verify one behavior
