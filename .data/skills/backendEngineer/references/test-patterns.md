# Test Patterns — Skillnir Backend

> Pytest fixtures, async tests, mocking patterns, and test organization examples.

---

## Test File Structure

`inject_skill(project_root, skill, tools)` injects one skill into every tool in the
`tools` list in a single call, returning one `InjectionResult` per tool:

```python
"""Tests for skillnir.injector module."""

from pathlib import Path
from unittest.mock import patch

import pytest

from skillnir.injector import inject_skill
from skillnir.skills import Skill
from skillnir.tools import AITool


class TestInjectSkill:
    """Tests for inject_skill function."""

    def test_creates_symlink_when_none_exists(self, tmp_project, sample_skill, sample_tool):
        results = inject_skill(tmp_project, sample_skill, [sample_tool])
        assert results[0].created is True
        assert results[0].error is None
        assert results[0].symlink_path.is_symlink()

    def test_skips_when_symlink_already_exists(self, tmp_project, sample_skill, sample_tool):
        # First injection
        inject_skill(tmp_project, sample_skill, [sample_tool])
        # Second injection — should skip
        results = inject_skill(tmp_project, sample_skill, [sample_tool])
        assert results[0].created is False
        assert results[0].error is None

    def test_handles_permission_error(self, tmp_project, sample_skill, sample_tool):
        with patch('pathlib.Path.symlink_to', side_effect=OSError('Permission denied')):
            results = inject_skill(tmp_project, sample_skill, [sample_tool])
        assert results[0].created is False
        assert 'Permission denied' in results[0].error
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

With `asyncio_mode = "auto"` in `pyproject.toml`, async tests are detected automatically.
`generate_docs_sdk(target_project, prompt_text, on_progress=None) -> GenerationResult`
takes no `model` argument (Claude-only) and streams typed messages from
`claude_agent_sdk.query()` — fake it with `monkeypatch.setattr` on an async-generator
function rather than mocking `.type`/`.content` attributes off a `MagicMock`:

```python
"""Tests for async generation functions."""

from pathlib import Path

import pytest

from skillnir.generator import GenerationProgress, generate_docs_sdk


class TestGenerateDocsSdk:
    """Tests for generate_docs_sdk async function."""

    async def test_streams_text_content(self, tmp_path: Path, monkeypatch):
        from claude_agent_sdk import AssistantMessage, TextBlock

        progress_calls: list[GenerationProgress] = []

        def on_progress(p: GenerationProgress) -> None:
            progress_calls.append(p)

        async def fake_query(*, prompt, options):  # noqa: ARG001
            (tmp_path / 'agents.md').write_text('# Hello World\n', encoding='utf-8')
            yield AssistantMessage(content=[TextBlock(text='Hello World')], model='test')

        monkeypatch.setattr('claude_agent_sdk.query', fake_query)
        result = await generate_docs_sdk(tmp_path, 'SYSTEM PROMPT', on_progress)

        assert result.success is True
        assert any(p.kind == 'text' and p.content == 'Hello World' for p in progress_calls)

    async def test_handles_empty_response(self, tmp_path: Path, monkeypatch):
        async def fake_query(*, prompt, options):  # noqa: ARG001
            return
            yield  # pragma: no cover — makes this an async generator

        monkeypatch.setattr('claude_agent_sdk.query', fake_query)
        result = await generate_docs_sdk(tmp_path, 'SYSTEM PROMPT')

        assert result.success is False
```

---

## Mocking Patterns

### Subprocess Mocking

`generate_docs_subprocess(target_project, prompt_text, backend, model, on_progress=None)`
delegates the actual `Popen` + streaming to `run_streaming_command()` in `backends.py`,
so mock at that boundary rather than patching `subprocess.Popen` directly:

```python
from unittest.mock import patch

from skillnir.backends import AIBackend, StreamedRunResult


def test_subprocess_generation(tmp_project):
    with patch(
        'skillnir.generator.run_streaming_command',
        return_value=StreamedRunResult(returncode=0, stderr=''),
    ):
        (tmp_project / 'agents.md').write_text('# Done\n', encoding='utf-8')
        result = generate_docs_subprocess(tmp_project, 'prompt', AIBackend.CLAUDE, 'sonnet')

    assert result.success is True
```

### Filesystem Mocking

`load_config()` takes no path argument — it always reads `~/.skillnir/config.json` via
the module-level `CONFIG_FILE` constant, so point that constant at a temp path instead
of passing one in. Also note it never returns `None`; a missing file yields a default
`AppConfig`:

```python
def test_handles_missing_config(tmp_path, monkeypatch):
    monkeypatch.setattr('skillnir.backends.CONFIG_FILE', tmp_path / 'config.json')
    # Don't create the file — test missing-file handling
    result = load_config()
    assert result.backend == AIBackend.CLAUDE  # default
```

### Tool Detection Mocking

`detect_tools()` is a plain `(target_root / tool.dotdir).is_dir()` check over every
`TOOLS` entry — no `shutil.which()`, no mocking needed, just create the dotdir:

```python
def test_detect_installed_tools(tmp_project):
    (tmp_project / '.claude').mkdir(exist_ok=True)
    (tmp_project / '.cursor').mkdir(exist_ok=True)

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
