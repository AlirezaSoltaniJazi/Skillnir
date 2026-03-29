# Pipeline Patterns

> GitHub Actions workflow patterns with full examples for the Skillnir project.

---

## Pattern 1: Code Quality Check Workflow

The `check-style.yml` workflow runs formatting and linting checks:

```yaml
name: Check Style
on: pull_request

jobs:
  style:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Check formatting
        run: black --check -S src/ tests/
      - name: Check unused imports
        run: autoflake --check --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports -r src/ tests/
      - name: Lint
        run: pylint -rn --rcfile=.pylintrc src/skillnir/
      - name: Security scan
        run: bandit -lll -iii -r src/
```

**Key rules:**

- Steps run sequentially — fail fast on formatting before expensive linting
- Same flags as pre-commit hooks — no drift between local and CI
- `--check` mode only — CI should never modify code

---

## Pattern 2: Test Runner Workflow

The `run-tests.yml` workflow runs the pytest suite:

```yaml
name: Run Tests
on: pull_request

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run tests
        run: pytest --tb=short -q
```

**Key rules:**

- `--tb=short` for readable CI output
- `-q` for quiet mode (less noise in logs)
- Editable install (`-e`) ensures imports work correctly

---

## Pattern 3: Auto-Assignment Workflow

The `auto-assign-author.yml` workflow assigns the PR author:

```yaml
name: Auto Assign Author
on:
  pull_request:
    types: [opened]

jobs:
  assign-author:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.addAssignees({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              assignees: [context.payload.pull_request.user.login]
            })
```

**Key rules:**

- Only triggers on `opened` (not every PR update)
- Minimal permission: `pull-requests: write`
- Uses `actions/github-script` for safe GitHub API interaction (no shell injection)

---

## Pattern 4: Composite Action

The `setup-python` composite action:

```yaml
name: Setup Python
description: Setup Python with caching
inputs:
  python-version:
    description: Python version to install
    required: false
    default: "3.14"
runs:
  using: composite
  steps:
    - uses: actions/setup-python@v5
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
```

**Key rules:**

- Inputs have sensible defaults (Python 3.14)
- `cache: pip` for faster subsequent runs
- `using: composite` (not Docker or Node.js)
- Stored at `.github/actions/setup-python/action.yml`

---

## Pattern 5: Adding a New Workflow

Template for any new workflow:

```yaml
name: <Descriptive Name>
on: pull_request

jobs:
  <job-name>:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    # permissions:
    #   Only if needed, add minimal permissions
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-python
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: <Step description>
        run: <command>
```

**Checklist for new workflows:**

1. Set `timeout-minutes: 10`
2. Pin all action versions
3. Use composite action for Python setup
4. Add minimal permissions (only if needed)
5. Match local pre-commit flags exactly

---

## Pre-commit to CI Alignment

Ensure pre-commit hooks and CI workflows run identical commands:

| Tool      | Pre-commit Args                                                                                                       | CI Args                                                                                                            |
| --------- | --------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Black     | `-S` (in-place)                                                                                                       | `--check -S` (check mode)                                                                                          |
| Autoflake | `--in-place --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports` | `--check --remove-all-unused-imports --remove-unused-variables --expand-star-imports --ignore-init-module-imports` |
| Pylint    | `-rn --rcfile=.pylintrc`                                                                                              | `-rn --rcfile=.pylintrc`                                                                                           |
| Bandit    | `-lll -iii`                                                                                                           | `-lll -iii -r src/`                                                                                                |

**Key difference:** Pre-commit runs `--in-place` (fixes), CI runs `--check` (validates).
