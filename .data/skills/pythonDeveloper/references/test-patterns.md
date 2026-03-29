# Testing Patterns

> pytest conventions, fixture patterns, test organization, and mocking strategies for the Skillnir project.

---

## Test Framework Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

- Framework: pytest with pytest-asyncio
- Test directory: `tests/` at project root
- Async mode: auto (no need for `@pytest.mark.asyncio`)

---

## Test File Structure

Each module gets a corresponding test file:

| Source Module | Test File |
|--------------|-----------|
| `src/skillnir/backends.py` | `tests/test_backends.py` |
| `src/skillnir/syncer.py` | `tests/test_syncer.py` |
| `src/skillnir/skills.py` | `tests/test_skills.py` |
| `src/skillnir/injector.py` | `tests/test_injector.py` |
| `src/skillnir/hooks.py` | `tests/test_hooks.py` |

---

## Test Organization — Class-Based

Group related tests in classes. Each class tests one function or one behavior:

```python
"""Tests for skillnir.syncer -- skill syncing with version comparison."""

from pathlib import Path

from skillnir.syncer import _get_skill_version, sync_skill, sync_skills


class TestGetSkillVersion:
    def test_extracts_version(self, tmp_path: Path):
        _make_skill(tmp_path, 's', SKILL_MD_V1)
        assert _get_skill_version(tmp_path / 's') == '1.0.0'

    def test_returns_unknown_when_no_skill_md(self, tmp_path: Path):
        (tmp_path / 'empty').mkdir()
        assert _get_skill_version(tmp_path / 'empty') == 'unknown'


class TestSyncSkill:
    def test_copies_when_target_missing(self, tmp_path: Path):
        source_dir = tmp_path / 'source'
        target_dir = tmp_path / 'target'
        _make_skill(source_dir, 'alpha', SKILL_MD_V1)

        result = sync_skill(source_dir, target_dir, 'alpha')
        assert result.action == 'copied'
        assert result.source_version == '1.0.0'
        assert (target_dir / 'alpha' / 'SKILL.md').exists()
```

**Naming rules:**
- Class: `TestFunctionName` or `TestBehaviorName`
- Method: `test_description_of_behavior`
- No `test_` prefix on classes (pytest discovers them by `Test` prefix)

---

## Shared Fixtures (conftest.py)

```python
"""Shared fixtures for skillnir tests."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.backends import AIBackend, AppConfig
from skillnir.skills import Skill
from skillnir.tools import AITool

SAMPLE_FRONTMATTER = """\
---
name: test-skill
description: A test skill
metadata:
  version: "1.0.0"
---
# Test Skill
Some content here.
"""


@pytest.fixture
def tmp_project(tmp_path: Path) -> Path:
    """Create a temp project directory with .data/skills/ and tool dotdirs."""
    skills_dir = tmp_path / '.data' / 'skills' / 'my-skill'
    skills_dir.mkdir(parents=True)
    (skills_dir / 'SKILL.md').write_text(SAMPLE_FRONTMATTER, encoding='utf-8')

    for dotdir in ('.cursor', '.claude'):
        (tmp_path / dotdir).mkdir()

    return tmp_path


@pytest.fixture
def sample_skill(tmp_project: Path) -> Skill:
    return Skill(
        name='my-skill',
        description='A test skill',
        version='1.0.0',
        path=tmp_project / '.data' / 'skills' / 'my-skill',
    )


@pytest.fixture
def sample_tool() -> AITool:
    return AITool(name='TestTool', dotdir='.testtool', company='TestCo')


@pytest.fixture
def mock_config():
    """Patch load_config to return a controllable AppConfig."""
    cfg = AppConfig(backend=AIBackend.CLAUDE, model='sonnet', prompt_version='v1')
    with patch('skillnir.backends.load_config', return_value=cfg):
        yield cfg
```

---

## Test Helpers — In-File, Not Fixtures

For test-specific setup, use module-level helper functions:

```python
SKILL_MD_V1 = """\
---
name: alpha
description: Alpha skill
metadata:
  version: "1.0.0"
---
# Alpha
"""


def _make_skill(parent: Path, name: str, content: str) -> Path:
    """Helper to create a skill directory with SKILL.md."""
    d = parent / name
    d.mkdir(parents=True, exist_ok=True)
    (d / 'SKILL.md').write_text(content, encoding='utf-8')
    return d
```

**Key pattern**: Helper functions start with `_` and stay in the test file. Shared helpers go to conftest.py.

---

## Mocking Strategy

### What to Mock

- External CLI tools (subprocess.Popen, shutil.which)
- Config loading (load_config)
- User input (questionary prompts)

### What NOT to Mock

- File system operations — use `tmp_path` fixture for real files
- Dataclass construction — test real instances
- Path operations — use real pathlib.Path with tmp_path

### Mocking Pattern

```python
from unittest.mock import patch, MagicMock


class TestConfigLoading:
    def test_falls_back_on_invalid_json(self, tmp_path: Path):
        config_file = tmp_path / 'config.json'
        config_file.write_text('invalid json', encoding='utf-8')

        with patch('skillnir.backends.CONFIG_FILE', config_file):
            config = load_config()
            assert config.backend == AIBackend.CLAUDE  # Default fallback
```

---

## Assertion Patterns

Assert on result dataclass fields directly:

```python
# GOOD — assert on result fields
result = sync_skill(source_dir, target_dir, 'alpha')
assert result.action == 'copied'
assert result.source_version == '1.0.0'
assert result.target_version is None

# GOOD — assert on file system state
assert (target_dir / 'alpha' / 'SKILL.md').exists()
content = (target_dir / 'alpha' / 'SKILL.md').read_text()
assert '2.0.0' in content

# BAD — asserting internal implementation
assert mock_copytree.called  # Don't test HOW, test WHAT
```

---

## Edge Case Testing

Always test these edge cases:

```python
class TestSamePathSafety:
    """Verify that syncing with source == target does not destroy data."""

    def test_sync_skill_skips_when_same_path(self, tmp_path: Path):
        shared_dir = tmp_path / 'skills'
        _make_skill(shared_dir, 'alpha', SKILL_MD_V1)

        result = sync_skill(shared_dir, shared_dir, 'alpha')
        assert result.action == 'skipped'
        assert (shared_dir / 'alpha' / 'SKILL.md').exists()
```

Standard edge cases to cover:
- Empty inputs (empty directories, empty strings)
- Missing files/directories
- Same source and target paths
- Malformed data (invalid YAML, invalid JSON)
- Non-existent paths

---

## Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_syncer.py

# Run specific test class
uv run pytest tests/test_syncer.py::TestSyncSkill

# Run specific test method
uv run pytest tests/test_syncer.py::TestSyncSkill::test_copies_when_target_missing

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=skillnir
```
