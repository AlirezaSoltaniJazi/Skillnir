# Code Style — Infrastructure Conventions

> Naming, configuration, and file organization conventions for Skillnir infrastructure files.

---

## Workflow Naming

| Convention | Example |
|-----------|---------|
| Workflow files | `kebab-case.yml` (`check-style.yml`, `run-tests.yml`) |
| Job names | `snake_case` or short lowercase (`test`, `style`, `assign-author`) |
| Step names | Sentence case with action verb (`Install dependencies`, `Run tests`) |
| Composite actions | Nested under `.github/actions/{name}/action.yml` |

---

## Workflow Structure Template

```yaml
name: Descriptive Name
on: pull_request

jobs:
  job-name:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    permissions:
      # Only what's needed
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python  # Local composite
      - name: Step description
        run: command here
```

**Key rules:**
- Always set `timeout-minutes: 10`
- Always pin action versions (`@v4`, not `@latest`)
- Always `checkout` before local composite actions
- Minimal `permissions` block

---

## Pre-commit Hook Entry

```yaml
- repo: https://github.com/org/repo
  rev: vX.Y.Z          # Always pinned
  hooks:
    - id: hook-name
      args: [--flag1, --flag2]
      exclude: '\.data/'  # For code quality hooks
```

**Key rules:**
- Pin `rev:` to exact version tag
- Add `exclude: '\.data/'` for Black, Pylint, Autoflake
- Use `additional_dependencies:` for local hooks that need packages
- Safety exceptions: `--ignore=CVE-YYYY-NNNN` with inline comment

---

## pyproject.toml Conventions

```toml
[project]
requires-python = ">=3.14"

[project.scripts]
skillnir = "skillnir.cli:main"

[project.optional-dependencies]
dev = ["pytest>=8.0", "pytest-asyncio>=0.24"]

[dependency-groups]
dev = ["pre-commit>=4.5.1", "pylint>=4.0.5"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
```

**Key rules:**
- Use `>=` version bounds (not `==` pinning) in `pyproject.toml`
- Exact pinning lives in `uv.lock` (auto-generated)
- Entry points under `[project.scripts]`
- Dev tools in `[dependency-groups]`, test tools in `[project.optional-dependencies]`

---

## .gitignore Organization

Group exclusions by category with comments:

```
# Python
__pycache__/
*.pyc

# Environment
.env
.envrc

# Credentials
.pypirc

# IDE
.idea/

# Build
build/
dist/

# Project-specific
/.data/research/
```

---

## GitHub PR Template

```markdown
## Summary
<!-- What and why -->

## Changes
- Change 1
- Change 2

## Test plan
- [ ] Tests pass (`uv run pytest`)
- [ ] Manual verification
```

---

## Version Pinning Strategy

| Location | Strategy | Example |
|----------|---------|---------|
| `pyproject.toml` | Minimum bound | `pyyaml>=6.0` |
| `uv.lock` | Exact lock (auto) | `pyyaml==6.0.2` |
| `.pre-commit-config.yaml` | Exact tag | `rev: 26.3.1` |
| GitHub Actions | Major version | `uses: actions/checkout@v4` |
| Composite action inputs | Default value | `default: '3.14'` |
