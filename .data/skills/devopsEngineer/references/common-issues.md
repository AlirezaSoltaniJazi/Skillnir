# Common Issues — Infrastructure

> Troubleshooting common CI/CD, pre-commit, and build system pitfalls in the Skillnir project.

---

## Pre-commit Issues

### Hook fails with "command not found"

**Cause**: Local hook expects system-installed tool (e.g., pylint) but it's not in PATH.

**Fix**: Ensure dev dependencies are installed: `uv sync` then `uv run pre-commit run --all-files`

### Black reformats files but CI still fails

**Cause**: Pre-commit runs Black in `--in-place` mode, CI runs `--check` mode. Files were auto-fixed locally but not committed.

**Fix**: After pre-commit fixes files, stage and commit the changes: `git add -u && git commit`

### Safety check fails with unknown CVE

**Cause**: New vulnerability discovered in a dependency.

**Fix**: Either update the dependency (`uv add package>=fixed_version`) or add exception (`--ignore=CVE-YYYY-NNNN`) with documented justification in `.pre-commit-config.yaml`

### Pre-commit hooks not running

**Cause**: Hooks not installed in local git repo.

**Fix**: `uv run pre-commit install`

### "Hook id X not found" after update

**Cause**: Hook ID changed in upstream repo after version update.

**Fix**: Check the hook repo's changelog, update the `id:` field in `.pre-commit-config.yaml`

---

## GitHub Actions Issues

### Workflow fails with "not found" for composite action

**Cause**: Missing `actions/checkout@v4` before referencing local composite action.

**Fix**: Always add checkout step before `uses: ./.github/actions/setup-python`

### Tests pass locally but fail in CI

**Cause**: Python version mismatch between local (3.14) and CI.

**Fix**: Check the `setup-python` composite action default version matches local Python.

### CI is slow

**Cause**: No caching configured.

**Fix**: The composite action uses `cache: pip`. Verify it's being used correctly.

### Workflow doesn't trigger

**Cause**: Incorrect trigger event or branch filter.

**Fix**: Check `on:` block — use `pull_request` (not `pull_request_target` unless needed).

---

## Build System Issues

### `uv sync` fails with resolution error

**Cause**: Conflicting version bounds in `pyproject.toml`.

**Fix**: Check `requires-python` and dependency versions. Use `uv pip compile` to debug resolution.

### Import errors after dependency change

**Cause**: Not using editable install.

**Fix**: `pip install -e ".[dev]"` for development, or `uv sync` for uv-managed installs.

### `uv.lock` conflicts in PR

**Cause**: Multiple PRs modifying dependencies simultaneously.

**Fix**: Rebase on main, run `uv sync` to regenerate lock, commit the updated `uv.lock`.

---

## Pylint Issues

### Pylint score drops below 10

**Cause**: New code introduced without following conventions.

**Fix**: Run `pylint -rn --rcfile=.pylintrc src/skillnir/` locally, fix all issues before pushing.

### Pylint false positive

**Cause**: Pylint doesn't understand a pattern.

**Fix**: Add specific `# pylint: disable=rule-name` inline (not in `.pylintrc` globally) with comment explaining why.

---

## Version Drift Issues

### Pre-commit and CI run different tool versions

**Cause**: Version pinned differently in `.pre-commit-config.yaml` vs CI `pip install`.

**Fix**: Audit both locations — ensure same tool versions. Consider using pre-commit in CI: `pre-commit run --all-files`.
