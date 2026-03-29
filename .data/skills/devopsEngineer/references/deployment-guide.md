# Deployment Guide

> CI/CD flow, environment topology, and quality gate pipeline for the Skillnir project.

---

## Environment Topology

Skillnir is a local-first CLI/UI tool with no cloud deployment. The "deployment" is package distribution:

```
Developer Machine (local)
├── uv sync              → Install from pyproject.toml
├── pre-commit install   → Hook into git workflow
├── uv run skillnir      → CLI entry point
└── uv run skillnir ui   → NiceGUI web interface (localhost)
```

---

## CI/CD Pipeline Flow

```
PR Opened
    ├── check-style.yml (parallel)
    │   ├── Black --check -S src/ tests/
    │   ├── Autoflake --check -r src/ tests/
    │   ├── Pylint --rcfile=.pylintrc src/skillnir/
    │   └── Bandit -lll -iii -r src/
    │
    ├── run-tests.yml (parallel)
    │   ├── actions/checkout@v4
    │   ├── .github/actions/setup-python (composite)
    │   ├── pip install -e ".[dev]"
    │   └── pytest --tb=short -q
    │
    └── auto-assign-author.yml (parallel)
        └── Assign PR author as assignee

All Pass → Review → Merge to main
```

---

## Quality Gate Order

The quality gates run in this specific order within `check-style.yml`:

1. **Black** (formatting) — fastest, catches style issues first
2. **Autoflake** (unused code) — removes dead imports/variables
3. **Pylint** (linting) — comprehensive code analysis with `.pylintrc`
4. **Bandit** (security) — catches security anti-patterns

This order is optimized for fast feedback — formatting issues are cheapest to fix.

---

## Composite Action: setup-python

Location: `.github/actions/setup-python/action.yml`

```yaml
name: Setup Python
inputs:
  python-version:
    description: Python version
    default: '3.14'
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
```

**Key rules:**
- Always `actions/checkout@v4` BEFORE using this composite action
- Default Python version is 3.14 — override via input if needed
- pip caching enabled for faster CI runs

---

## Pre-commit Local Flow

```
git commit
    └── pre-commit hooks (7 hooks in order)
        ├── trailing-whitespace
        ├── end-of-file-fixer
        ├── check-yaml (--allow-multiple-documents)
        ├── check-added-large-files
        ├── check-ast
        ├── check-merge-conflict
        ├── python-safety-dependencies-check (--ignore=CVE-2025-6176)
        ├── bandit (-lll -iii)
        ├── autoflake (--in-place, exclude .data/)
        ├── pylint (-rn, exclude .data/)
        ├── black (-S, exclude .data/)
        └── prettier (markdown only)
```

---

## Adding a New Quality Check

1. Add to `.pre-commit-config.yaml` (for local pre-commit)
2. Add to `.github/workflows/check-style.yml` (for CI)
3. Ensure both run the SAME command with SAME flags — avoid drift
4. Pin the version in both locations
5. Test locally: `pre-commit run --all-files`
6. Test CI: push to a feature branch and verify the workflow
