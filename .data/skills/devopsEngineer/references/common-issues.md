# Common Issues — Infrastructure Troubleshooting

## CI Pipeline Issues

### Black check fails but pre-commit passes

**Cause**: Pre-commit runs Black with `--in-place` but CI runs `--check`. Local files were auto-formatted but not committed.
**Fix**: Run `git add -u && git commit --amend` after pre-commit auto-fixes, or stage and create new commit.

### Pylint fails in CI but passes locally

**Cause**: CI installs different dependencies than local. CI uses `pip install` while local may use `uv`.
**Fix**: Ensure CI installs all dependencies needed for pylint (pyyaml, questionary, nicegui). Check that `.pylintrc` is the same.

### Autoflake reports unused imports in `__init__.py`

**Cause**: `__init__.py` re-exports are detected as unused.
**Fix**: Use `--ignore-init-module-imports` flag (already configured in both pre-commit and CI).

### Safety check fails on new dependency

**Cause**: Dependency has known CVE in Safety DB.
**Fix**:

1. Check if a patched version exists → upgrade
2. If no fix available, add `--ignore={CVE}` with documented comment in `.pre-commit-config.yaml`
3. Track the CVE for future resolution

### GitHub Actions timeout

**Cause**: Job exceeds `timeout-minutes` (10 min for test/style, 5 min for auto-assign).
**Fix**: Investigate slow step. Common causes: pip cache miss, large test suite, network issues.

## Pre-commit Issues

### Pre-commit hook fails on `.data/` files

**Cause**: Hook not configured to exclude `.data/` directory.
**Fix**: Add `exclude: ^\.data/` to the hook configuration.

### Pre-commit runs but CI still fails

**Cause**: Not all CI checks are mirrored in pre-commit (or vice versa). Safety and Prettier are pre-commit only.
**Fix**: This is by design. Some checks are local-only. Ensure the failing CI check has a pre-commit equivalent if needed.

### Pre-commit cache corruption

**Cause**: Python version change or hook version update.
**Fix**: `pre-commit clean && pre-commit install`

## Workflow Issues

### Composite action not found

**Cause**: `uses: ./.github/actions/setup-python` requires the action to exist in the checked-out repo.
**Fix**: Ensure `actions/checkout@v4` runs before the composite action step.

### Auto-assign fails with permission error

**Cause**: Workflow needs `pull-requests: write` permission.
**Fix**: Ensure `permissions: pull-requests: write` is set on the job.

### New workflow not triggering

**Cause**: Workflow file not on the default branch, or trigger event doesn't match.
**Fix**: For `pull_request` triggers, the workflow file must exist on the target branch. Push workflow to main first.

## Python Packaging Issues

### `pip install -e ".[dev]"` fails in CI

**Cause**: Missing build dependencies or Python version mismatch.
**Fix**: Ensure composite action sets correct Python version (3.14). Check `pyproject.toml` `requires-python`.

### uv vs pip discrepancy

**Cause**: Local uses `uv` but CI uses `pip`. Dependency resolution may differ.
**Fix**: This is current project design. CI uses pip for simplicity. Ensure `pyproject.toml` dependencies are compatible with both.

## Script Issues

### Validation script fails with "command not found"

**Cause**: Script uses tools not available in the environment (grep flags, etc.).
**Fix**: Use POSIX-compatible commands or check for tool availability.

### Script produces wrong PROJECT_ROOT

**Cause**: Symlinks or unexpected directory structure.
**Fix**: Use `$(cd "$(dirname "$0")/../../.." && pwd)` pattern with appropriate depth.
