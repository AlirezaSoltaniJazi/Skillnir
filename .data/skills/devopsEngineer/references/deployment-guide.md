# Deployment Guide — Skillnir

## Project Type

Skillnir is a **Python CLI tool** — not a web service, not a cloud application. There is no deployment pipeline, no server infrastructure, and no container orchestration.

## Distribution Model

- **Package format**: Python package built with hatchling
- **Package manager**: uv (local), pip (CI)
- **Entry point**: `skillnir = "skillnir.cli:main"` in `pyproject.toml`
- **Installation**: `pip install -e ".[dev]"` for development

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
    │     ├── safety (CVE scan)
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
          └── auto-assign-author (on PR open)
```

## Local Development Setup

1. Clone repository
2. Install Python 3.14+
3. Install uv package manager
4. Run `uv pip install -e ".[dev]"`
5. Install pre-commit: `pre-commit install`
6. Verify: `pre-commit run --all-files`

## Release Process

Currently manual — no automated release pipeline. The project uses semver in `pyproject.toml` (`version = "1.0.1"`).
