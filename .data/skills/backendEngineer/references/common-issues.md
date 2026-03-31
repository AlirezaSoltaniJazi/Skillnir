# Common Issues — Skillnir Backend

> Troubleshooting guide for common Python pitfalls encountered in the Skillnir project.

---

## Import Errors

### `ModuleNotFoundError: No module named 'skillnir'`

**Cause**: Package not installed in editable mode.
**Fix**: Run `uv pip install -e .` from project root.

### `ImportError: cannot import name 'X' from 'skillnir.module'`

**Cause**: Circular import or name not exported.
**Fix**: Check import order. Move imports inside functions if circular. Verify the name exists in the target module.

---

## Async Gotchas

### `RuntimeError: Event loop is already running`

**Cause**: Calling `asyncio.run()` inside an already-running event loop (e.g., inside NiceGUI).
**Fix**: Use `await` directly in async context. Only use `asyncio.run()` at the top-level CLI entry point.

### `RuntimeWarning: coroutine was never awaited`

**Cause**: Calling an async function without `await`.
**Fix**: Add `await` before the call. If in sync context, wrap with `asyncio.run()`.

### `pytest-asyncio: async def test not detected`

**Cause**: Missing `asyncio_mode = "auto"` in pyproject.toml.
**Fix**: Ensure `[tool.pytest.ini_options]` has `asyncio_mode = "auto"`.

---

## Dataclass Issues

### `TypeError: unhashable type` with frozen dataclass

**Cause**: Mutable default field (list, dict) in a frozen dataclass.
**Fix**: Use `field(default_factory=tuple)` instead of `field(default_factory=list)` for frozen dataclasses.

### `FrozenInstanceError` when modifying frozen dataclass

**Cause**: Attempting to modify a frozen dataclass field after construction.
**Fix**: Use `dataclasses.replace()` to create a modified copy.

---

## Path Issues

### `FileNotFoundError` with relative paths

**Cause**: Relative path resolved against wrong working directory.
**Fix**: Always use `Path.resolve()` or construct absolute paths from known roots.

### Symlink creation fails on Windows

**Cause**: Windows requires elevated privileges for symlinks.
**Fix**: The project targets macOS/Linux. Document Windows limitations.

---

## Subprocess Issues

### `subprocess.TimeoutExpired`

**Cause**: Backend CLI takes too long to respond.
**Fix**: Increase timeout. Add progress feedback so user knows it's working.

### Empty stdout from subprocess

**Cause**: Backend CLI writes to stderr instead of stdout, or buffering.
**Fix**: Check both stdout and stderr. Use `text=True` and line-buffered reading.

---

## YAML Frontmatter Issues

### `yaml.YAMLError` when parsing SKILL.md

**Cause**: Invalid YAML syntax in frontmatter block.
**Fix**: Validate YAML between `---` delimiters. Check for unquoted special characters.

### Version field parsed as float

**Cause**: YAML interprets `1.0` as float, not string `"1.0"`.
**Fix**: Always quote version strings in frontmatter: `version: "1.0.0"`.

---

## Pre-commit Hook Failures

### Black reformats code on commit

**Cause**: Code wasn't formatted before staging.
**Fix**: Run `black -S src/ tests/` before committing. Pre-commit will auto-fix but reject the commit.

### Pylint fails with import errors

**Cause**: pylint can't find project modules.
**Fix**: Ensure `.pylintrc` has correct `init-hook` or run via `uv run pylint`.

### Autoflake removes used imports

**Cause**: Import used only in type hints or conditional blocks.
**Fix**: Add `# noqa: F401` comment or configure autoflake exclusions.

---

## UV Package Manager Issues

### `uv add` fails with resolution error

**Cause**: Conflicting version constraints.
**Fix**: Check `pyproject.toml` version specifiers. Use `uv lock --upgrade` to refresh.

### `uv run` can't find command

**Cause**: Package not installed in virtual environment.
**Fix**: Run `uv sync` to install all dependencies including dev extras.
