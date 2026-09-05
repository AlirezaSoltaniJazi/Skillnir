# Architecture Guide — DevOps Infrastructure

Full structure map of Skillnir's CI/CD and quality-gate infrastructure. SKILL.md
keeps only the flow summary; the annotated tree lives here.

## Directory Map

```
.github/
├── actions/setup-python/action.yml  # Composite action: installs Python 3.14 + pip cache, reused by all workflows
├── workflows/
│   ├── run-tests.yml                # pytest --tb=short -q on PR
│   ├── check-style.yml              # Sequential gate: Black → Autoflake → Pylint → Bandit
│   ├── auto-assign-author.yml       # Assigns the PR author on open
│   ├── pr-version-check.yml         # Fails PR if pyproject.toml version regresses below base
│   └── bump-version.yml             # Bumps version + promotes CHANGELOG + tags + GitHub Release
└── pull_request_template.md         # Summary + Changes + Test plan

.pre-commit-config.yaml              # 12 hooks mirroring CI checks (see hook list below)
.pylintrc                            # Comprehensive lint config (100-char lines, snake_case)
pyproject.toml                       # hatchling build, uv, dev deps — single source of truth for packaging
```

## Pre-commit Hooks (12)

From `pre-commit/pre-commit-hooks@v6.0.0`: trailing-whitespace, end-of-file-fixer,
check-yaml, check-added-large-files, check-ast, check-merge-conflict.
Then: uv-safety (local, CVE scan), bandit@1.9.2, autoflake@v2.3.1, pylint (local),
black@26.3.1, prettier@v3.8.1. (isort is commented out.)

## Flow

Code change → pre-commit hooks (local) → git push → GitHub Actions CI (remote) → PR merge decision.

See [deployment-guide.md](deployment-guide.md) for environment topology, the quality-gate
flow diagram, and the release process.
