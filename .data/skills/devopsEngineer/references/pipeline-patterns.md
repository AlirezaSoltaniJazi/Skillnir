# Pipeline Patterns — Skillnir CI/CD

## GitHub Actions Workflow Structure

All workflows live in `.github/workflows/` and trigger on `pull_request`.

### Composite Action: setup-python

Reusable setup shared across workflows:

```yaml
# .github/actions/setup-python/action.yml
name: Setup Python
description: Set up Python with pip cache (requires checkout first)

inputs:
    python-version:
        description: Python version to use
        required: false
        default: "3.14"

runs:
    using: composite
    steps:
        - name: Set up Python ${{ inputs.python-version }}
          uses: actions/setup-python@v5
          with:
              python-version: ${{ inputs.python-version }}
              cache: pip
```

### Workflow: run-tests.yml

```yaml
name: PR - Run Tests
on: [pull_request]
jobs:
    test:
        name: Run Tests
        runs-on: ubuntu-latest
        timeout-minutes: 10
        steps:
            - name: Checkout repository
              uses: actions/checkout@v4
            - name: Setup Python
              uses: ./.github/actions/setup-python
            - name: Install dependencies
              run: pip install -e ".[dev]"
            - name: Run tests
              run: pytest --tb=short -q
```

### Workflow: check-style.yml

Sequential quality gates — each step must pass before the next:

```yaml
name: PR - Check Style
on: [pull_request]
jobs:
    style:
        name: Lint & Format Check
        runs-on: ubuntu-latest
        timeout-minutes: 10
        steps:
            - name: Checkout repository
              uses: actions/checkout@v4
            - name: Setup Python
              uses: ./.github/actions/setup-python
            - name: Install dependencies
              run: pip install black autoflake pylint bandit pyyaml questionary nicegui
            - name: Check formatting with Black
              run: black --check -S src/ tests/
            - name: Check unused imports with Autoflake
              run: |
                  autoflake --check --remove-all-unused-imports \
                    --remove-unused-variables --expand-star-imports \
                    --ignore-init-module-imports -r src/ tests/
            - name: Lint with Pylint
              run: pylint -rn --rcfile=.pylintrc src/skillnir/
            - name: Security check with Bandit
              run: bandit -lll -iii -r src/
```

### Workflow: auto-assign-author.yml

```yaml
name: PR - Auto Assign Author
on:
    pull_request:
        types: [opened]
jobs:
    assign-author:
        name: Assign PR Author
        runs-on: ubuntu-latest
        timeout-minutes: 5
        permissions:
            pull-requests: write
        steps:
            - name: Assign author to PR
              uses: actions/github-script@v7
              with:
                  script: |
                      await github.rest.issues.addAssignees({
                        owner: context.repo.owner,
                        repo: context.repo.repo,
                        issue_number: context.payload.pull_request.number,
                        assignees: [context.payload.pull_request.user.login]
                      });
```

## CI Quality Gate Order

The style check enforces this sequential pipeline:

1. **Black** — formatting (fast, catches style issues)
2. **Autoflake** — unused imports/variables (fast, catches dead code)
3. **Pylint** — deep linting with `.pylintrc` (slower, catches logic issues)
4. **Bandit** — security scanning (catches vulnerabilities)

This order is intentional: cheapest/fastest checks first, most expensive last.

## Pre-commit ↔ CI Parity

Pre-commit hooks mirror CI checks to catch issues before push:

| Pre-commit Hook                   | CI Equivalent                      |
| --------------------------------- | ---------------------------------- |
| `black` with `-S`                 | `black --check -S src/ tests/`     |
| `autoflake` with in-place         | `autoflake --check ... src/ tests/`|
| `pylint` with `--rcfile=.pylintrc`| `pylint -rn --rcfile=.pylintrc`    |
| `bandit` with `-lll -iii`         | `bandit -lll -iii -r src/`         |
| `safety` (dependencies)           | Not in CI (pre-commit only)        |
| `prettier` (markdown)             | Not in CI (pre-commit only)        |

## Adding a New Workflow

1. Create `.github/workflows/{trigger}-{action}.yml`
2. Use naming convention: `PR - {Description}` for PR-triggered workflows
3. Always set `timeout-minutes` on every job
4. Use composite action `uses: ./.github/actions/setup-python` for Python setup
5. Pin all action versions to specific major versions (`@v4`, `@v5`, `@v7`)
6. Scope `permissions` to minimum required

## Adding a New Pre-commit Hook

1. Add repo entry to `.pre-commit-config.yaml`
2. Pin to specific revision (`rev: vX.Y.Z`)
3. Add corresponding CI step if the check should block PRs
4. Exclude `.data/` directory if the hook processes Python/code files
5. Document any CVE exemptions with `--ignore` args and comments
