# Contributing to Skillnir

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- Git

## Setup

```bash
git clone git@github.com:AlirezaSoltaniJazi/Skillnir.git
cd skillnir

# Install all dependencies
uv sync

# Install pre-commit hooks
uv run pre-commit install

# Verify everything works
uv run pytest
```

## Development Workflow

1. Create a branch from `main`

   ```bash
   git checkout -b feat/your-feature
   ```

2. Make your changes

3. Run tests

   ```bash
   uv run pytest
   ```

4. Commit -- pre-commit hooks will run automatically (Black, Pylint, Autoflake, Bandit, Safety)

5. Push and open a PR against `main`

## Code Style

| Tool      | Purpose                         | Config                                             |
| --------- | ------------------------------- | -------------------------------------------------- |
| Black     | Formatting (PEP 8)              | `-S` flag (skip string normalization), Python 3.13 |
| Pylint    | Linting                         | `.pylintrc` (line-length=100, fail-under=10)       |
| Autoflake | Remove unused imports/variables | Excludes `.data/`                                  |
| Bandit    | Security scanning               | `-lll -iii` (low false-positive threshold)         |
| Safety    | Dependency vulnerability check  | Runs on `requirements*` files                      |
| Prettier  | Markdown formatting             | Default config                                     |

All tools run automatically via pre-commit hooks on every commit. To run manually:

```bash
uv run pre-commit run --all-files
```

## Testing

Tests live in `tests/` and use pytest with pytest-asyncio.

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run a specific test file
uv run pytest tests/test_injector.py

# Run a specific test
uv run pytest tests/test_injector.py::TestInjectSkill::test_creates_symlink
```

## CI Pipelines

Every PR triggers:

- **Check Style** -- Black, Autoflake, Pylint, Bandit
- **Run Tests** -- full pytest suite
- **Auto Assign** -- PR author is automatically assigned

All checks must pass before merging.

## Project Conventions

- **Package manager**: uv exclusively (no pip, poetry, pipenv)
- **Build system**: hatchling via `pyproject.toml`
- **Imports**: absolute imports only (`from skillnir.skills import ...`)
- **Paths**: `pathlib.Path` exclusively (no `os.path`)
- **Config**: frozen dataclasses
- **Results**: result dataclasses (not tuples or dicts)
- **Line length**: 100 characters max
- **Quotes**: single quotes (Black `-S`)

## Adding Dependencies

```bash
# Runtime dependency
uv add <package>

# Dev dependency
uv add --group dev <package>
```

Never edit `uv.lock` manually.

## Creating Skills

Generate a skill through the UI or CLI:

```bash
# Via CLI
uv run skillnir generate-skill

# Via web UI
uv run skillnir ui
# Navigate to "Generate Skill"
```

Available scopes: backend, frontend, android, ios, infra, testing, js, python, test-design, general-system.

## GitHub Actions

When creating workflows, check existing workflows for shared steps first. Extract common steps into reusable composite actions under `.github/actions/`. Always add `actions/checkout` before referencing local composite actions.
