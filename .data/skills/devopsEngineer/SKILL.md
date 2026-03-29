---
name: devopsEngineer
description: >-
  Infrastructure and DevOps rules for the Skillnir project. Covers GitHub Actions
  CI/CD pipelines, pre-commit hooks, code quality tooling, build system configuration,
  composite actions, PR templates, and development workflow automation. Activates for
  any infrastructure task including Docker/container config, CI/CD pipelines, pre-commit
  hooks, build system changes, deployment scripts, GitHub Actions workflows, code quality
  tooling, secret management, and DevOps automation.
compatibility: "GitHub Actions, pre-commit 4.5+, hatchling, uv, Black 26.3+, Pylint 4.0+, Bandit 1.9+, Safety 1.4+"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: infrastructure
allowed-tools: Read Edit Write Bash(git:*) Bash(uv:*) Bash(pre-commit:*) Bash(gh:*) Glob Grep Agent
sub-agents:
  - name: security-scanner
    file: agents/security-scanner.md
  - name: drift-detector
    file: agents/drift-detector.md
  - name: cost-reviewer
    file: agents/cost-reviewer.md
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: devops engineer skill" at the very start of your response before doing any work.

## When to Use

1. Creating or modifying GitHub Actions workflows in `.github/workflows/`
2. Updating pre-commit hooks or `.pre-commit-config.yaml`
3. Changing build system configuration in `pyproject.toml`
4. Creating or updating composite actions in `.github/actions/`
5. Modifying code quality tooling (Black, Pylint, Bandit, Autoflake, Safety)
6. Updating PR templates, OWNERS, `.gitignore`, or dev workflow automation

## Do NOT Use

- **Python modules, dataclasses, CLI logic** — use [pythonDeveloper](../pythonDeveloper/SKILL.md)
- **UI components or page layouts** — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **Skill file structure, LEARNED.md, INJECT.md** — use [skillnir](../skillnir/SKILL.md)

## Architecture

```
.github/
├── workflows/
│   ├── check-style.yml         # Lint + format (Black, Autoflake, Pylint, Bandit)
│   ├── run-tests.yml           # pytest suite on PR
│   └── auto-assign-author.yml  # Auto-assign PR author
├── actions/
│   └── setup-python/
│       └── action.yml          # Composite: Python 3.14 + pip cache
└── pull_request_template.md    # PR template (Summary, Changes, Test plan)

.pre-commit-config.yaml         # 7 hooks: trailing-ws, eof, yaml, ast, black, pylint, bandit
.pylintrc                       # Line 100, fail-under=10, snake_case
pyproject.toml                  # hatchling build, uv deps, pytest config
OWNERS                          # Code ownership (@AlirezaSoltaniJazi)
.gitignore                      # Python, IDE, env, credentials exclusions
.claude/settings.json           # Claude Code security whitelist
```

**CI/CD Flow**: PR opened → `check-style` + `run-tests` + `auto-assign-author` (parallel) → All checks pass → Review → Merge to main

**Quality Gate Pipeline**: Black format check → Autoflake unused imports → Pylint score ≥10 → Bandit security scan → pytest suite

## Key Patterns

| Pattern | Approach | Key Rule |
|---------|----------|----------|
| CI/CD platform | GitHub Actions on `pull_request` trigger | All checks run in parallel on PR |
| Composite actions | `.github/actions/setup-python/` | Extract shared steps, reuse across workflows |
| Pre-commit hooks | 7 hooks in `.pre-commit-config.yaml` | Exclude `.data/` from code quality hooks |
| Code formatting | Black 26.3.1 with `-S` flag | Single quotes enforced, Python 3.14 target |
| Linting | Pylint with `.pylintrc` (fail-under=10) | Serial execution, 100-char line length |
| Security scanning | Bandit `-lll -iii` + Safety check | Low false-positive threshold, document CVE exceptions |
| Build system | hatchling via `pyproject.toml` | Entry point: `skillnir = "skillnir.cli:main"` |
| Package manager | uv exclusively | Never pip, poetry, or pipenv |
| Python version | 3.14+ pinned | `actions/setup-python@v5` with pip caching |
| PR workflow | Template + auto-assign + parallel checks | Always checkout before local composite actions |

See [references/pipeline-patterns.md](references/pipeline-patterns.md) for full workflow examples.

## Conventions

| Rule | Convention |
|------|-----------|
| Workflow triggers | `on: pull_request` for checks, never `on: push` to main for CI |
| Job timeout | 10 minutes max for all CI jobs |
| Runner | `ubuntu-latest` for all workflows |
| Permissions | Minimal — only `pull-requests: write` for auto-assign |
| Composite actions | Stored in `.github/actions/{name}/action.yml` |
| Pre-commit excludes | `.data/` excluded from Black, Pylint, Autoflake |
| Hook versions | Pinned with `rev:` — update via `pre-commit autoupdate` |
| Safety exceptions | Document CVE ID + reason in `args:` with `--ignore` |
| Dependency management | `uv add <pkg>` (runtime), `uv add --group dev <pkg>` (dev) |
| Branch strategy | Feature branches from main: `feat/`, `fix/`, `docs/` prefixes |

See [references/code-style.md](references/code-style.md) for naming and configuration conventions.

## Common Recipes

1. **Add a new CI workflow**: Create `.github/workflows/{name}.yml` → set `on: pull_request` trigger → add `actions/checkout@v4` step → use `./.github/actions/setup-python` composite → add job steps → set `timeout-minutes: 10`
2. **Add a pre-commit hook**: Add repo entry to `.pre-commit-config.yaml` → pin `rev:` version → add `exclude: '\.data/'` if code quality hook → test with `pre-commit run --all-files`
3. **Add a new composite action**: Create `.github/actions/{name}/action.yml` → define inputs with defaults → add steps → reference with `uses: ./.github/actions/{name}`
4. **Update a dependency**: `uv add {package}>=version` → verify `uv.lock` updated → run `uv run pytest` → run `pre-commit run --all-files`
5. **Add a Safety CVE exception**: Add `--ignore=CVE-YYYY-NNNN` to safety hook args → add comment with reason and affected package
6. **Update pre-commit hooks**: Run `pre-commit autoupdate` → verify all hooks pass → commit updated `.pre-commit-config.yaml`

## Monitoring & Alerting

- GitHub Actions status checks enforce quality gates on every PR
- Pre-commit hooks catch issues before commit reaches CI
- Bandit scans catch security issues at `-lll -iii` threshold
- Safety checks catch known CVEs in dependencies (with documented exceptions)
- Pylint fail-under=10 prevents code quality regression
- PR template checklist ensures manual verification steps

## Security

| Area | Rule | Severity |
|------|------|----------|
| Secrets in CI | Never hardcode — use GitHub Secrets or environment variables | Critical |
| Bandit threshold | `-lll -iii` — low false-positive, catches real issues | High |
| Safety exceptions | Document every ignored CVE with ID, package, and reason | High |
| Pre-commit | `check-ast` validates Python syntax before commit | Medium |
| `.gitignore` | Excludes `.env`, `.pypirc`, credentials files | Critical |
| Claude settings | Whitelist specific bash commands in `.claude/settings.json` | High |
| PR permissions | Minimal scope — only `pull-requests: write` for auto-assign | Medium |

See [references/security-checklist.md](references/security-checklist.md) for full verification checklists.

## Disaster Recovery

- **Broken pre-commit**: Run `pre-commit clean && pre-commit install` to reset
- **Failed CI workflow**: Check workflow logs → fix locally → push fix commit (never force-push main)
- **Corrupted uv.lock**: Delete `uv.lock` → run `uv sync` to regenerate
- **Python version mismatch**: Update `setup-python` composite action input → update `pyproject.toml` requires-python
- **Broken dependency**: Pin to known-good version in `pyproject.toml` → add Safety exception if CVE

## Anti-Patterns

| Anti-Pattern | Why It's Wrong |
|-------------|----------------|
| Using `pip install` instead of `uv` | Project uses uv exclusively — mixing creates dependency conflicts |
| Running hooks with `--no-verify` | Bypasses quality gates — fix the hook failure instead |
| Using `on: push` to main for CI checks | Checks should run on PR to catch issues before merge |
| Hardcoding Python version in workflows | Use composite action input — single source of truth |
| Adding secrets to `.env` files in repo | Use GitHub Secrets — `.env` is gitignored for a reason |
| Skipping `actions/checkout` before local actions | Composite actions need repo code — checkout first |
| Using `pip` in CI instead of `pip install -e` | Dev dependencies need editable install for pytest |
| Ignoring Safety CVEs without documentation | Every exception needs CVE ID, package, and justification |
| Using `shell: bash` with user input in CI | Injection risk — use `actions/github-script` for dynamic content |
| Setting `fail-under` below 10 in Pylint | Allows code quality regression — maintain the bar |

## Code Generation Rules

1. **Read before writing** — always read the target config file and 1-2 similar configs before generating
2. **Match existing patterns** — check how similar workflows/hooks are structured in the codebase
3. **Minimal permissions** — CI jobs get only the permissions they need
4. **Pin versions** — all actions, hooks, and tools use pinned versions
5. **On correction** — acknowledge, restate as rule, apply to all subsequent output, **write to [LEARNED.md](LEARNED.md)** under `## Corrections`
6. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then existing configs, ask ONE question, **write to [LEARNED.md](LEARNED.md)** under `## Preferences`

## Sub-Agent Delegation

| Agent | Role | Spawn When | Tools |
|-------|------|------------|-------|
| [security-scanner](agents/security-scanner.md) | CI/CD security audit and secret detection | Workflow review, secret detection, permission audit | Read Glob Grep |
| [drift-detector](agents/drift-detector.md) | Config drift between CI and local tooling | Pre-commit vs CI mismatch, version drift, config validation | Read Glob Grep |
| [cost-reviewer](agents/cost-reviewer.md) | CI optimization and resource analysis | Workflow optimization, action caching review, job parallelization | Read Glob Grep |

### Delegation Rules

1. Delegate when task has distinct phases or needs security isolation (read-only analysis)
2. Stay inline for simple, single-focus tasks
3. Cap at 3 sub-agents per workflow
4. Pass ALL context explicitly — sub-agents don't see parent conversation
5. Sub-agents CANNOT spawn their own sub-agents (max depth = 1)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode | Detection Signal | Behavior |
|------|-----------------|----------|
| Diagnostic | "CI failed", "hook error", "workflow broken", error logs | Read workflow/config, check syntax/versions, diagnose root cause first |
| Efficient | "Same as check-style", "Add another workflow like X", Nth similar task | Minimal explanation, match existing patterns, generate directly |
| Teaching | "What is a composite action", "why pre-commit", "explain this workflow" | Explain rationale, reference pipeline-patterns.md, show existing examples |
| Review | "Check this workflow", "audit CI config", "review pipeline" | Read-only analysis, delegate to security-scanner agent, report findings |

**Proficiency Calibration:**

| Signal Type | Indicators | Behavior |
|-------------|-----------|----------|
| Senior | Modifies generated config, asks about trade-offs, references CI internals | Lead with config, rationale on non-obvious only |
| Learning | Asks "what is...", copies unchanged, pastes errors without analysis | Teaching mode, explain why not just how, link to docs |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Freedom Levels

| Level | Scope | Examples |
|-------|-------|---------|
| **MUST** follow | uv only, pin versions, minimal permissions, exclude .data/, timeout on jobs, checkout before local actions | "MUST use uv, never pip" |
| **SHOULD** follow | 10-min timeout, ubuntu-latest runner, composite actions for shared steps, `-lll -iii` Bandit threshold | "SHOULD extract shared steps into composite actions" |
| **CAN** customize | Workflow naming, job concurrency, specific hook ordering, Pylint disable rules | "CAN choose between `on: [push, pull_request]` triggers" |

## References

| File | Description |
|------|-------------|
| [LEARNED.md](LEARNED.md) | **Auto-updated.** Corrections, preferences, conventions across sessions |
| [INJECT.md](INJECT.md) | Always-loaded quick reference (hallucination firewall) |
| [references/deployment-guide.md](references/deployment-guide.md) | CI/CD flow, environment topology, quality gate pipeline |
| [references/code-style.md](references/code-style.md) | Naming, tagging, configuration conventions with examples |
| [references/security-checklist.md](references/security-checklist.md) | CI/CD security, secrets, permissions, dependency verification |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols |
| [references/pipeline-patterns.md](references/pipeline-patterns.md) | GitHub Actions workflow patterns with full examples |
| [references/common-issues.md](references/common-issues.md) | Troubleshooting common CI/CD and pre-commit pitfalls |
| [assets/workflow-template.yml](assets/workflow-template.yml) | Copy-paste GitHub Actions workflow template |
| [assets/pre-commit-hook-template.yaml](assets/pre-commit-hook-template.yaml) | Pre-commit hook entry template |
| [scripts/validate-infra.sh](scripts/validate-infra.sh) | Infrastructure convention and naming validator |
