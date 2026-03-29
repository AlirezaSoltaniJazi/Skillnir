# Security Checklist — Infrastructure

> CI/CD security, secret management, permissions, and dependency verification for the Skillnir project.

---

## Severity Classification

| Severity     | Description                                     | Examples                                        |
| ------------ | ----------------------------------------------- | ----------------------------------------------- |
| **Critical** | Secret exposure, code injection                 | Secrets in workflow logs, shell injection in CI |
| **High**     | Permission escalation, dependency vulnerability | Overly broad permissions, unpatched CVEs        |
| **Medium**   | Configuration weakness                          | Missing timeouts, unpinned versions             |
| **Low**      | Best practice deviation                         | Verbose logging, non-minimal runners            |

---

## GitHub Actions Security (OWASP A03: Injection)

### Critical

- [ ] Never use `${{ github.event.pull_request.title }}` directly in `run:` — use environment variables
- [ ] Never hardcode secrets in workflow files — use `${{ secrets.NAME }}`
- [ ] Never use `pull_request_target` without careful review — exposes secrets to forks
- [ ] Never log secret values — use `::add-mask::` for dynamic secrets

### High

- [ ] Set minimal `permissions:` on every job — never use default (read-all)
- [ ] Pin all actions to specific versions (`@v4`, not `@main` or `@latest`)
- [ ] Use `actions/github-script` for dynamic content instead of `shell: bash` with interpolation
- [ ] Review third-party actions before adoption — check maintenance, stars, verified publisher

### Medium

- [ ] Set `timeout-minutes` on every job (prevent runaway workflows)
- [ ] Use `concurrency` groups to prevent duplicate workflow runs
- [ ] Limit `GITHUB_TOKEN` permissions via `permissions:` block

---

## Secret Management

### Critical

- [ ] `.env` files are in `.gitignore` — never committed
- [ ] `.pypirc` is in `.gitignore` — never committed
- [ ] No API keys or tokens in source code or config files
- [ ] Claude Code settings whitelist specific commands only (`.claude/settings.json`)

### High

- [ ] Use GitHub Secrets for CI environment variables
- [ ] Rotate secrets on suspected exposure
- [ ] Document all secret dependencies in README or CONTRIBUTING.md

### Medium

- [ ] Use `.env.example` (without real values) for documentation
- [ ] Backend-specific auth handled by each tool (Claude, Cursor, etc.)

---

## Dependency Security

### High

- [ ] Safety check runs in pre-commit pipeline
- [ ] Every CVE exception has documented justification with `--ignore=CVE-YYYY-NNNN`
- [ ] Current exception: CVE-2025-6176 (brotli v1.1.0 — no fix available)
- [ ] Bandit security scanning at `-lll -iii` threshold

### Medium

- [ ] Pin minimum dependency versions in `pyproject.toml`
- [ ] Review `uv.lock` changes in PRs for unexpected transitive dependencies
- [ ] Run `pre-commit autoupdate` periodically to get security patches in hooks

---

## Pre-commit Security

### High

- [ ] `check-ast` hook validates Python syntax (catches injection in .py files)
- [ ] `check-merge-conflict` prevents accidental conflict marker commits
- [ ] `check-added-large-files` prevents accidental binary/secret file commits

### Medium

- [ ] `check-yaml` with `--allow-multiple-documents` validates YAML syntax
- [ ] `trailing-whitespace` and `end-of-file-fixer` for consistent formatting

---

## Claude Code Security (`.claude/settings.json`)

### High

- [ ] Bash commands are whitelisted — only specific grep and git commands allowed
- [ ] No write permissions to system directories
- [ ] No network access commands in whitelist

---

## Pre-Merge Security Checklist

1. [ ] All pre-commit hooks pass (`pre-commit run --all-files`)
2. [ ] No Bandit findings at `-lll -iii` threshold
3. [ ] No Safety CVE alerts (except documented exceptions)
4. [ ] GitHub Actions permissions are minimal
5. [ ] No secrets in diff (`git diff` review)
6. [ ] All action versions pinned
7. [ ] No `shell=True` or unquoted variables in workflow `run:` steps
