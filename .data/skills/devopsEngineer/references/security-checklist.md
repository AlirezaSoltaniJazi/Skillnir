# Security Checklist — Infrastructure

## CI/CD Security

### Critical

- [ ] All GitHub Actions pinned to specific major versions (`@v4`, not `@main`)
- [ ] No secrets hardcoded in workflow files
- [ ] Workflow permissions scoped to minimum required per job
- [ ] No `pull_request_target` without explicit security review

### High

- [ ] Bandit security linter runs on every PR (`-lll -iii` threshold)
- [ ] Safety dependency CVE scanning via pre-commit
- [ ] CVE exemptions documented with reason and tracked version
- [ ] No `shell: bash` with user-controlled inputs in workflows

### Medium

- [ ] Pre-commit hooks cannot be bypassed without `--no-verify` (discouraged)
- [ ] PR template includes test plan checkbox
- [ ] Auto-assign workflow uses minimal `pull-requests: write` permission

### Low

- [ ] Composite actions use inputs with defaults (no required secrets)
- [ ] Workflow timeouts set on all jobs (prevents runaway costs)

## Dependency Security

### Critical

- [ ] No known high/critical CVEs in dependencies (Safety scan)
- [ ] All dependency versions pinned with minimum bounds (`>=X.Y.Z`)

### High

- [ ] CVE exemptions in `.pre-commit-config.yaml` include:
  - CVE number
  - Reason for exemption
  - Current version status
- [ ] `pyproject.toml` uses minimum version pinning, not exact pinning

### Medium

- [ ] Dev dependencies separated in `[project.optional-dependencies]`
- [ ] No unnecessary dependencies in production install

## Code Quality Security

### Critical

- [ ] Bandit scans all source code (`-r src/`)
- [ ] No `shell=True` with user input in subprocess calls
- [ ] No `eval()` or `exec()` with external input

### High

- [ ] Autoflake removes unused imports (reduces attack surface)
- [ ] Pylint catches suspicious patterns via `.pylintrc`
- [ ] Path validation before filesystem operations

### Medium

- [ ] `.gitignore` excludes sensitive files (`.env`, credentials, IDE configs)
- [ ] `.data/research/` excluded from git (may contain API responses)

## Pre-commit Security Hooks

Current security-relevant hooks in `.pre-commit-config.yaml`:

| Hook                               | Purpose                         | Severity |
| ---------------------------------- | ------------------------------- | -------- |
| `bandit`                           | Python security linter          | High     |
| `python-safety-dependencies-check` | CVE scanning for deps           | High     |
| `check-ast`                        | Validates Python syntax         | Medium   |
| `check-merge-conflict`             | Prevents merge conflict markers | Medium   |
| `check-added-large-files`          | Prevents accidental large files | Low      |

## Adding Security to New Infrastructure

1. **New workflow**: Scope permissions, pin actions, set timeouts
2. **New dependency**: Check Safety DB, pin minimum version
3. **New pre-commit hook**: Pin revision, document purpose
4. **New script**: Use `set -euo pipefail`, validate inputs, quote variables
