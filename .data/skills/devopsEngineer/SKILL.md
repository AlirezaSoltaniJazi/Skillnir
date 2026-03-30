---
name: devopsEngineer
description: >-
  Infrastructure and DevOps skill for the Skillnir project. Covers GitHub Actions
  CI/CD pipelines, pre-commit hook configuration, code quality gates (Black, pylint,
  autoflake, bandit, safety), composite actions, workflow automation, validation scripts,
  and Python packaging infrastructure. Activates when modifying workflows, pre-commit
  hooks, CI configuration, quality gate setup, bash validation scripts, or any
  .github/, .pre-commit-config.yaml, .pylintrc, or pyproject.toml build config.
compatibility: "GitHub Actions, pre-commit 4.5+, Black 26.3+, pylint 4.0+, bandit 1.9+, Python 3.14+"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: deployment
allowed-tools: Read Edit Write Bash(pre-commit:*) Bash(gh:*) Bash(git:*) Bash(uv:*) Glob Grep Agent
sub-agents:
  - name: security-scanner
    file: agents/security-scanner.md
  - name: pipeline-reviewer
    file: agents/pipeline-reviewer.md
  - name: hook-debugger
    file: agents/hook-debugger.md
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: devopsEngineer skill" at the very start of your response before doing any work.

## When to Use

1. Creating or modifying GitHub Actions workflows under `.github/workflows/`
2. Configuring pre-commit hooks in `.pre-commit-config.yaml`
3. Updating linter/formatter configuration (`.pylintrc`, Black flags, autoflake args)
4. Writing or modifying bash validation scripts under `.data/skills/*/scripts/`
5. Modifying CI-related sections of `pyproject.toml` (build system, dev dependencies)
6. Creating composite actions under `.github/actions/`

## Do NOT Use

- **Python source code** (modules, dataclasses, CLI logic) — use [backendEngineer](../backendEngineer/SKILL.md)
- **NiceGUI UI components/pages** (Tailwind, Quasar) — use [frontendEngineer](../frontendEngineer/SKILL.md)
- **Skill system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md)

## Architecture

```
.github/
├── actions/setup-python/action.yml  # Composite: Python 3.14 + pip cache
├── workflows/
│   ├── run-tests.yml                # pytest --tb=short -q
│   ├── check-style.yml              # Black → Autoflake → Pylint → Bandit
│   └── auto-assign-author.yml       # PR author assignment
└── pull_request_template.md         # Summary + Changes + Test plan

.pre-commit-config.yaml              # 11 hooks mirroring CI checks
.pylintrc                            # 500+ line comprehensive config
pyproject.toml                       # hatchling build, uv, dev deps
```

**Flow**: Code change → pre-commit hooks (local) → git push → GitHub Actions CI (remote) → PR merge decision.

## Key Patterns

| Pattern               | Approach                                       | Key Rule                                           |
| --------------------- | ---------------------------------------------- | -------------------------------------------------- |
| Composite actions     | Shared setup in `.github/actions/`             | Reuse via `uses: ./.github/actions/setup-python`   |
| Quality gate ordering | Sequential: cheapest/fastest first             | Black → Autoflake → Pylint → Bandit               |
| CI ↔ pre-commit parity| Same tools in both, same flags                 | Changes to one MUST be evaluated for the other     |
| Action pinning        | Major version only                             | `@v4`, `@v5`, `@v7` — never `@main`/`@latest`     |
| CVE exemptions        | Documented inline with reason                  | `--ignore={CVE}` with comment explaining why       |
| `.data/` exclusion    | Excluded from all code quality hooks           | `exclude: ^\.data/` on Black, pylint, autoflake    |
| Timeout enforcement   | Every job gets `timeout-minutes`               | 10 min for test/style, 5 min for automation        |
| Permission scoping    | Minimum required per job                       | Default read-only, explicit when write needed      |

See [references/pipeline-patterns.md](references/pipeline-patterns.md) for full workflow examples.

## Conventions

| Rule                    | Convention                                                     |
| ----------------------- | -------------------------------------------------------------- |
| Workflow naming         | File: `kebab-case.yml`, Name: `PR - {Description}`            |
| Job naming              | Descriptive, title case (e.g., `Lint & Format Check`)         |
| Step naming             | Imperative, title case (e.g., `Checkout repository`)          |
| Action pinning          | Major version: `actions/checkout@v4` — never branch refs      |
| Pre-commit revisions    | Pinned: `rev: vX.Y.Z` — never `main`/`latest`                |
| Script shebang          | `#!/usr/bin/env bash` + `set -euo pipefail`                   |
| Script output           | Emoji prefixes: ✅ pass, ❌ fail, ⚠️ warning                  |
| CI Python version       | 3.14 (set in composite action default)                        |
| Trigger events          | `pull_request` for all quality gates                           |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **Add a new CI workflow**: Create `.github/workflows/{trigger}-{action}.yml` → set `timeout-minutes` → use composite action for Python setup → pin all action versions → scope permissions
2. **Add a pre-commit hook**: Add repo entry to `.pre-commit-config.yaml` → pin `rev` → add `exclude: ^\.data/` for code hooks → add corresponding CI step if merge-blocking → run `pre-commit run --all-files` to verify
3. **Add a composite action**: Create `.github/actions/{name}/action.yml` → define inputs with defaults → use `runs: using: composite` → reference via `uses: ./.github/actions/{name}`
4. **Update a quality gate**: Update both `.pre-commit-config.yaml` AND `.github/workflows/check-style.yml` → verify flag parity → test locally with `pre-commit run {hook-id} --all-files`
5. **Exempt a CVE**: Add `--ignore={CVE}` to safety args in `.pre-commit-config.yaml` → add comment with CVE number, reason, and version status
6. **Add a validation script**: Create `.data/skills/{name}/scripts/validate-{scope}.sh` → use `set -euo pipefail` → calculate `PROJECT_ROOT` → use pass/fail/warn helpers → exit 1 on any failure

## Monitoring & Alerting

- GitHub Actions provides built-in workflow run notifications
- PR status checks gate merge — failed checks block merging
- Pre-commit failures provide immediate local feedback
- No external monitoring (Prometheus, Datadog) — not applicable for CLI tool
- Validation scripts provide on-demand convention checks

## Security

- All actions pinned to major versions (no branch refs)
- Workflow permissions scoped to minimum per job
- Bandit scans on every PR (`-lll -iii` threshold)
- Safety CVE scanning with documented exemptions
- No secrets in workflows — project has no deployment secrets
- Pre-commit hooks enforce security before code reaches CI

See [references/security-checklist.md](references/security-checklist.md) for severity-classified checklists.

## Disaster Recovery

- **Broken CI**: Check GitHub Actions status page → verify composite action exists → check Python version compatibility
- **Pre-commit corruption**: `pre-commit clean && pre-commit install` → `pre-commit run --all-files`
- **Rollback workflow change**: `git revert` the workflow commit — workflows are versioned in git
- **Broken quality gate**: Temporarily skip in pre-commit with `SKIP={hook-id} git commit` — fix immediately after

## Anti-Patterns

| Anti-Pattern                           | Why It's Wrong                                              |
| -------------------------------------- | ----------------------------------------------------------- |
| Using `@main`/`@latest` for actions   | Supply chain risk — action updates can break or compromise  |
| Hardcoding secrets in workflows        | Exposed in repo history — use GitHub Secrets if ever needed |
| Skipping pre-commit (`--no-verify`)    | Bypasses quality gates — fix the issue instead              |
| No `timeout-minutes` on jobs           | Runaway jobs waste CI minutes and block PRs                 |
| Docker/K8s/Terraform for this project  | Skillnir is a CLI tool — no containerization needed         |
| Adding `requirements.txt`              | `pyproject.toml` is single source of truth                  |
| Breaking CI ↔ pre-commit parity       | Developers get surprised by CI failures after local pass    |
| Overly permissive workflow permissions | Principle of least privilege — scope per job                |
| Running pylint without `.pylintrc`     | Inconsistent results between local and CI                   |

## Code Generation Rules

1. **Check parity first** — before modifying CI or pre-commit, read both to understand current state
2. **Pin everything** — action versions, hook revisions, Python version
3. **Set timeouts** — every workflow job gets `timeout-minutes`
4. **Exclude `.data/`** — from all code quality hooks and CI lint steps
5. **Document exemptions** — CVE ignores, permission escalations, disabled hooks
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then project files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                       | Behavior                                                              |
| ---------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Diagnostic | "CI fails", "hook error", "workflow broken", error logs                | Read error context, check parity, trace root cause, minimal fix       |
| Efficient  | "same as check-style", "another hook like X", "add step to workflow"  | Minimal explanation, replicate existing patterns, apply conventions    |
| Teaching   | "what is composite action", "how does pre-commit work", "explain CI"  | Explain with project examples, link to references/, reference docs    |
| Review     | "review workflow", "check hooks", "audit CI"                          | Read-only analysis, check conventions, delegate to sub-agents          |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent                                            | Role                              | Spawn When                            | Tools                          |
| ------------------------------------------------ | --------------------------------- | ------------------------------------- | ------------------------------ |
| [security-scanner](agents/security-scanner.md)   | CI/CD security audit              | Workflow review, secret detection     | Read Glob Grep                 |
| [pipeline-reviewer](agents/pipeline-reviewer.md) | Pipeline correctness review       | Workflow changes, parity checks       | Read Glob Grep                 |
| [hook-debugger](agents/hook-debugger.md)         | Pre-commit/CI failure diagnosis   | Hook failures, CI errors, config fix  | Read Edit Write Bash Glob Grep |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring cross-skill decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                                  | Examples                                                          |
| ----------------- | -------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| **MUST** follow   | Action pinning, timeout-minutes, CI ↔ pre-commit parity, `.data/` exclusion, LEARNED.md | "MUST pin actions to major versions", "MUST set timeout"         |
| **SHOULD** follow | Quality gate ordering, composite action reuse, naming conventions                       | "SHOULD run cheapest checks first", "SHOULD use composite action"|
| **CAN** customize | Bandit threshold, pylint rules, hook selection, timeout values                          | "CAN adjust bandit severity", "CAN add new hooks"                |

## References

| File                                                                     | Description                                                      |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions          |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)           |
| [references/pipeline-patterns.md](references/pipeline-patterns.md)       | Full workflow examples, CI gate ordering, hook configuration     |
| [references/code-style.md](references/code-style.md)                     | Workflow naming, YAML structure, script conventions              |
| [references/security-checklist.md](references/security-checklist.md)     | Severity-classified CI/CD and dependency security checklists     |
| [references/deployment-guide.md](references/deployment-guide.md)         | Environment topology, quality gate flow, distribution model      |
| [references/common-issues.md](references/common-issues.md)               | Troubleshooting CI failures, hook errors, parity issues          |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, common AI mistakes for infra         |
| [assets/workflow-example.yml](assets/workflow-example.yml)               | Copy-paste GitHub Actions workflow template                      |
| [assets/pre-commit-hook-example.yaml](assets/pre-commit-hook-example.yaml) | Copy-paste pre-commit hook entry template                     |
| [scripts/validate-infra.sh](scripts/validate-infra.sh)                   | Infrastructure convention checker                                |
| [agents/security-scanner.md](agents/security-scanner.md)                 | CI/CD security audit agent                                       |
| [agents/pipeline-reviewer.md](agents/pipeline-reviewer.md)               | Pipeline correctness review agent                                |
| [agents/hook-debugger.md](agents/hook-debugger.md)                       | Pre-commit/CI failure diagnosis agent                            |
