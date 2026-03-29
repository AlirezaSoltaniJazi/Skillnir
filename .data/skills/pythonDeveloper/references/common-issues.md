# Common Issues & Troubleshooting

> Frequently encountered problems and their solutions for backend Python development in the Skillnir project.

---

## 1. Import Errors

### Problem: `ModuleNotFoundError: No module named 'skillnir'`

**Cause**: Package not installed in development mode.

**Fix**:

```bash
uv pip install -e .
# or
uv sync
```

### Problem: Circular imports between modules

**Cause**: Two modules importing each other at the top level.

**Fix**: Use string annotations for type hints that would cause circular imports:

```python
# In syncer.py — reference AITool as string to avoid importing tools.py
def inject_skill(tool: 'AITool', skill: Skill) -> InjectionResult:
    ...
```

---

## 2. Path-Related Issues

### Problem: `shutil.rmtree` deletes source when source == target

**Cause**: Not checking if source and target resolve to the same directory.

**Fix** (already implemented in syncer.py):

```python
if source_dir.resolve() == target_dir.resolve():
    return []  # Skip — same directory
```

### Problem: `FileNotFoundError` on Path.read_text()

**Cause**: Missing `.exists()` guard before reading.

**Fix**:

```python
if not skill_md.exists():
    return 'unknown'
text = skill_md.read_text(encoding='utf-8')
```

### Problem: Encoding errors on non-UTF-8 files

**Cause**: Missing `encoding='utf-8'` parameter.

**Fix**: Always specify encoding:

```python
# GOOD
text = path.read_text(encoding='utf-8')
path.write_text(content, encoding='utf-8')

# BAD — uses system default encoding
text = path.read_text()
```

---

## 3. Subprocess Issues

### Problem: Subprocess hangs indefinitely

**Cause**: Stderr buffer fills up, blocking the process.

**Fix**: Drain stderr in a separate thread:

```python
stderr_lines: list[str] = []
stderr_thread = threading.Thread(
    target=lambda: stderr_lines.extend(proc.stderr.readlines()),
    daemon=True,
)
stderr_thread.start()
```

### Problem: `FileNotFoundError` when spawning CLI tool

**Cause**: External CLI tool not installed or not on PATH.

**Fix**: Check availability before spawning:

```python
if not shutil.which(backend_info.cli_command):
    return GenerationResult(success=False, error=f'{backend_info.cli_command} not found on PATH')
```

### Problem: JSON decode error on stream output

**Cause**: Non-JSON lines mixed into stream output (progress bars, warnings).

**Fix**: Handle gracefully with try/except:

```python
try:
    return json.loads(stripped)
except json.JSONDecodeError:
    return None  # Skip non-JSON lines
```

---

## 4. YAML Frontmatter Issues

### Problem: `yaml.safe_load` returns None

**Cause**: Empty frontmatter block (`---\n---`).

**Fix**: Always use `or {}`:

```python
return yaml.safe_load(text[3:end]) or {}
```

### Problem: Missing nested metadata fields

**Cause**: Accessing `meta['metadata']['version']` when metadata key doesn't exist.

**Fix**: Use `.get()` with defaults:

```python
metadata = meta.get('metadata', {}) or {}
version = metadata.get('version', 'unknown')
```

---

## 5. Dataclass Issues

### Problem: `TypeError: unhashable type: 'dict'` on frozen dataclass

**Cause**: Using mutable default (dict/list) directly in frozen dataclass field.

**Fix**: Use `field(default_factory=...)`:

```python
# GOOD
@dataclass(frozen=True)
class BackendInfo:
    slash_commands: dict[str, str] = field(default_factory=dict)

# BAD — TypeError at class definition
@dataclass(frozen=True)
class BackendInfo:
    slash_commands: dict[str, str] = {}
```

### Problem: Frozen dataclass field cannot be modified

**Cause**: Trying to mutate a frozen dataclass after creation.

**Fix**: Create a new instance instead:

```python
# Use dataclasses.replace() for modified copies
from dataclasses import replace
new_config = replace(old_config, model='opus')
```

---

## 6. Testing Issues

### Problem: Tests fail with `FileNotFoundError` for config

**Cause**: Tests reading real `~/.skillnir/config.json` instead of test config.

**Fix**: Mock the config loader:

```python
@pytest.fixture
def mock_config():
    cfg = AppConfig(backend=AIBackend.CLAUDE, model='sonnet', prompt_version='v1')
    with patch('skillnir.backends.load_config', return_value=cfg):
        yield cfg
```

### Problem: Symlink tests fail on Windows

**Cause**: Symlink creation requires admin privileges on Windows.

**Fix**: Skip or mark tests:

```python
import os
import pytest

@pytest.mark.skipif(os.name == 'nt', reason='Symlinks require admin on Windows')
def test_symlink_creation(tmp_path: Path):
    ...
```

### Problem: Async tests not running

**Cause**: Missing `asyncio_mode = "auto"` in pyproject.toml.

**Fix**: Ensure pytest config includes:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

---

## 7. Pre-commit Issues

### Problem: Black reformats .data/ skill files

**Cause**: Missing `exclude: ^\.data/` in Black hook config.

**Fix**: Ensure all code quality hooks exclude `.data/`:

```yaml
- id: black
  exclude: ^\.data/
  args: ["-S"]
```

### Problem: Pylint fails with import errors

**Cause**: Pylint cannot find skillnir package.

**Fix**: Ensure package is installed in dev environment:

```bash
uv sync
uv pip install -e .
```

---

## 8. NiceGUI Issues

### Problem: UI not updating after async operation

**Cause**: NiceGUI requires explicit UI refresh for async state changes.

**Fix**: Use `ui.notify()` or bind reactive state variables.

### Problem: Storage not persisting across restarts

**Cause**: Missing `storage_secret` in `ui.run()`.

**Fix**: Already implemented — ensure `storage_secret='skillnir-local'` is set.
