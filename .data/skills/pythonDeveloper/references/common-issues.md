# Common Issues — Generic Python Reference

> Troubleshooting guide for common Python pitfalls in production projects.

---

## Import Errors

### `ModuleNotFoundError: No module named 'your_project'`

**Cause**: Package not installed in editable mode or virtual environment not activated.
**Fix**: Run `pip install -e .` or `uv pip install -e .` from project root. Verify venv is active.

### `ImportError: cannot import name 'X' from 'your_project.module'`

**Cause**: Circular import or name not exported.
**Fix**: Check import order. Move imports inside functions if circular. Verify the name exists in the target module.

### `ImportError` with relative imports

**Cause**: Running a module directly instead of as part of a package.
**Fix**: Use absolute imports. Run with `python -m your_project.module` instead of `python src/your_project/module.py`.

---

## Async Gotchas

### `RuntimeError: Event loop is already running`

**Cause**: Calling `asyncio.run()` inside an already-running event loop (e.g., inside Jupyter, web framework).
**Fix**: Use `await` directly in async context. Only use `asyncio.run()` at the top-level entry point.

### `RuntimeWarning: coroutine was never awaited`

**Cause**: Calling an async function without `await`.
**Fix**: Add `await` before the call. If in sync context, wrap with `asyncio.run()`.

### `pytest-asyncio: async def test not detected`

**Cause**: Missing `asyncio_mode = "auto"` in pyproject.toml or missing pytest-asyncio plugin.
**Fix**: Ensure `[tool.pytest.ini_options]` has `asyncio_mode = "auto"` and `pytest-asyncio` is installed.

### `CancelledError` in asyncio tasks

**Cause**: Task cancelled during `await` without proper cleanup.
**Fix**: Use `try/finally` blocks around async operations. Use `asyncio.TaskGroup` for structured concurrency (Python 3.11+).

---

## Type Hint Issues

### `TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'`

**Cause**: Using `X | None` syntax in Python < 3.10.
**Fix**: Use `from __future__ import annotations` at the top of the file, or use `Optional[X]` for Python < 3.10.

### mypy/pyright reports `Incompatible types in assignment`

**Cause**: Assigning `None` to a variable not typed as `X | None`.
**Fix**: Update the type annotation to include `None`: `value: str | None = None`.

---

## Dataclass Issues

### `TypeError: unhashable type` with frozen dataclass

**Cause**: Mutable default field (list, dict) in a frozen dataclass.
**Fix**: Use `field(default_factory=tuple)` instead of `field(default_factory=list)` for frozen dataclasses.

### `FrozenInstanceError` when modifying frozen dataclass

**Cause**: Attempting to modify a frozen dataclass field after construction.
**Fix**: Use `dataclasses.replace()` to create a modified copy.

### `TypeError: non-default argument follows default argument`

**Cause**: Dataclass field without default value after field with default value.
**Fix**: Reorder fields: required fields first, optional fields (with defaults) last.

---

## Database Issues

### `OperationalError: database is locked` (SQLite)

**Cause**: Multiple concurrent writes to SQLite database.
**Fix**: Use WAL mode (`PRAGMA journal_mode=WAL`), reduce write concurrency, or switch to PostgreSQL.

### `IntegrityError: UNIQUE constraint failed`

**Cause**: Attempting to insert a duplicate value in a unique column.
**Fix**: Check for existence before insert, or use `INSERT ... ON CONFLICT` (upsert).

### Connection pool exhaustion

**Cause**: Connections not returned to pool, or pool size too small.
**Fix**: Use context managers (`with session:`) for all database operations. Increase pool size if needed.

---

## Path Issues

### `FileNotFoundError` with relative paths

**Cause**: Relative path resolved against wrong working directory.
**Fix**: Always use `Path.resolve()` or construct absolute paths from known roots.

### `PermissionError` on file operations

**Cause**: Insufficient permissions or file locked by another process.
**Fix**: Check file permissions. Use `try/except PermissionError` and report clearly.

---

## Testing Issues

### Fixtures not found

**Cause**: conftest.py in wrong directory, or fixture name typo.
**Fix**: Ensure `conftest.py` is in `tests/` directory. Check fixture names match exactly.

### Tests pass individually but fail together

**Cause**: Shared mutable state between tests.
**Fix**: Use fresh fixtures for each test. Avoid module-level mutable state. Reset singletons in fixtures.

### `asyncio.run() cannot be called from a running event loop`

**Cause**: Mixing sync `asyncio.run()` calls in async test context.
**Fix**: Use `await` directly in async tests. Ensure `asyncio_mode = "auto"` in pytest config.

---

## Dependency Issues

### `pip install` / `uv add` fails with resolution error

**Cause**: Conflicting version constraints between packages.
**Fix**: Check version specifiers in `pyproject.toml`. Use `pip install --dry-run` to diagnose conflicts.

### `AttributeError: module has no attribute` after upgrade

**Cause**: Breaking API change in upgraded dependency.
**Fix**: Check the package's changelog. Pin to working version. Update code to match new API.

---

## Performance Pitfalls

### Slow startup time

**Cause**: Heavy imports at module level (large ML libraries, etc.).
**Fix**: Use lazy imports inside functions that need them. Use `importlib.import_module()` for optional deps.

### Memory spikes with large datasets

**Cause**: Loading entire dataset into memory.
**Fix**: Use generators/iterators. Process in chunks. Use `itertools.islice()` for pagination.

### N+1 query problem

**Cause**: Querying related records in a loop instead of joining.
**Fix**: Use eager loading (`joinedload`, `selectinload` in SQLAlchemy) or batch queries.
