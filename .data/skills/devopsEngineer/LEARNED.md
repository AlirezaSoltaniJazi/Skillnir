# devopsEngineer — Learned Knowledge

> Auto-updated by AI. Entries accumulate across sessions. Format: `- YYYY-MM-DD: rule description`

## Corrections

## Preferences

## Discovered Conventions

- 2026-08-02: `.pre-commit-config.yaml` has 12 hooks (trailing-whitespace, end-of-file-fixer, check-yaml, check-added-large-files, check-ast, check-merge-conflict, uv-safety, bandit, autoflake, pylint, black, prettier). The dependency-CVE hook is a local hook named `uv-safety` (exports `uv.lock` and pipes into `safety check --stdin`), not the upstream `python-safety-dependencies-check` hook.
- 2026-08-02: Release automation exists: `.github/workflows/pr-version-check.yml` fails a PR if `pyproject.toml`'s version goes backwards, and `.github/workflows/bump-version.yml` bumps the version + promotes the CHANGELOG `[Unreleased]` section + tags + creates a GitHub Release, triggered on a labeled PR merge (`release:patch|minor|major`) or manual `workflow_dispatch`.
