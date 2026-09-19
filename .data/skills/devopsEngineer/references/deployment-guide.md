# Deployment Guide — Skillnir

## Project Type

Skillnir is a **Python CLI tool** — not a web service, not a cloud application. There is no deployment pipeline, no server infrastructure, and no container orchestration.

## Distribution Model

- **Package format**: Python package built with hatchling
- **Package manager**: uv (local), pip (CI)
- **Entry point**: `skillnir = "skillnir.cli:main"` in `pyproject.toml`
- **Installation**: `uv sync` for development (CI uses `pip install -e ".[dev]"` in `run-tests.yml`)

## Environment Topology

```
┌─────────────────────────────────────────────┐
│                  Developer                   │
│                                              │
│  ┌──────────┐    ┌───────────┐    ┌───────┐ │
│  │ Pre-     │───▶│ Local     │───▶│ Git   │ │
│  │ commit   │    │ Testing   │    │ Push  │ │
│  │ Hooks    │    │ (pytest)  │    │       │ │
│  └──────────┘    └───────────┘    └───┬───┘ │
└───────────────────────────────────────┼─────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────┐
│              GitHub Actions CI               │
│                                              │
│  ┌──────────┐    ┌───────────┐    ┌───────┐ │
│  │ Style    │    │ Tests     │    │ Auto  │ │
│  │ Check    │    │ Runner    │    │ Assign│ │
│  │          │    │           │    │       │ │
│  └──────────┘    └───────────┘    └───────┘ │
│       │               │                      │
│       ▼               ▼                      │
│  ┌──────────────────────────┐                │
│  │    PR Merge Decision     │                │
│  └──────────────────────────┘                │
└─────────────────────────────────────────────┘
```

## Quality Gate Flow

```
Code Change
    │
    ├──▶ Pre-commit (local, automatic)
    │     ├── trailing-whitespace
    │     ├── end-of-file-fixer
    │     ├── check-yaml
    │     ├── check-added-large-files
    │     ├── check-ast
    │     ├── check-merge-conflict
    │     ├── uv-safety (CVE scan)
    │     ├── bandit (security)
    │     ├── autoflake (dead code)
    │     ├── pylint (linting)
    │     ├── black (formatting)
    │     └── prettier (markdown)
    │
    ├──▶ Git Push
    │
    └──▶ GitHub Actions CI (remote, on PR)
          ├── check-style (Black → Autoflake → Pylint → Bandit)
          ├── run-tests (pytest --tb=short -q)
          ├── auto-assign-author (on PR open)
          └── pr-version-check (fails PR if pyproject.toml version regresses)
```

## Local Development Setup

1. Clone repository
2. Install Python 3.14+
3. Install uv package manager
4. Run `uv sync`
5. Install pre-commit: `uv run pre-commit install`
6. Verify: `uv run pytest` and `uv run pre-commit run --all-files`

## Release Process

Automated via `.github/workflows/bump-version.yml`. Two trigger paths:

1. **PR merge** — merging a PR labeled `release:patch`, `release:minor`, or `release:major` into `main` bumps `pyproject.toml`'s `version`, promotes the CHANGELOG's `[Unreleased]` section to a dated release heading, re-seeds an empty `[Unreleased]` section, tags `vX.Y.Z`, and creates a GitHub Release from that CHANGELOG section.
2. **Manual dispatch** — running the workflow by hand with a chosen bump type (patch/minor/major) does the same, from `main`.

`.github/workflows/pr-version-check.yml` is a separate PR gate that fails if a PR's `pyproject.toml` version is lower than the base branch's — versions may only stay equal or move forward. The project uses semver in `pyproject.toml` (currently `version = "1.8.0"`).
