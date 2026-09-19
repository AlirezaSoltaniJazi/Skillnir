---
name: devopsEngineer
description: >-
  Infrastructure and DevOps skill for the Skillnir project. Covers GitHub Actions
  CI/CD pipelines, pre-commit hook configuration, code quality gates (Black, pylint,
  autoflake, bandit, safety), composite actions, workflow automation, validation scripts,
  and Python packaging infrastructure. Activates when modifying workflows, pre-commit
  hooks, CI configuration, quality gate setup, bash validation scripts, or any
  .github/, .pre-commit-config.yaml, .pylintrc, or pyproject.toml build config.
compatibility: "GitHub Actions, pre-commit 4.6+, Black 26.3+, pylint 4.0+, bandit 1.9+, Python 3.14+"
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

Entry points: `.github/workflows/` (5 CI workflows), `.github/actions/setup-python/` (composite), `.pre-commit-config.yaml` (12 hooks), `.pylintrc`, `pyproject.toml`.

**Flow**: Code change → pre-commit hooks (local) → git push → GitHub Actions CI (remote) → PR merge decision.

See [references/architecture-guide.md](references/architecture-guide.md) for the annotated structure map and hook list.

## Key Patterns

| Pattern                | Approach                             | Key Rule                                         |
| ---------------------- | ------------------------------------ | ------------------------------------------------ |
| Composite actions      | Shared setup in `.github/actions/`   | Reuse via `uses: ./.github/actions/setup-python` |
| Quality gate ordering  | Sequential: cheapest/fastest first   | Black → Autoflake → Pylint → Bandit              |
| CI ↔ pre-commit parity | Same tools in both, same flags       | Changes to one MUST be evaluated for the other   |
| Action pinning         | Major version only                   | `@v4`, `@v5`, `@v7` — never `@main`/`@latest`    |
| CVE exemptions         | Documented inline with reason        | `--ignore={CVE}` with comment explaining why     |
| `.data/` exclusion     | Excluded from all code quality hooks | `exclude: ^\.data/` on Black, pylint, autoflake  |
| Timeout enforcement    | Every job gets `timeout-minutes`     | 10 min for test/style, 5 min for automation      |
| Permission scoping     | Minimum required per job             | Default read-only, explicit when write needed    |

See [references/pipeline-patterns.md](references/pipeline-patterns.md) for full workflow examples.

## Conventions

| Rule                 | Convention                                               |
| -------------------- | -------------------------------------------------------- |
| Workflow naming      | File: `kebab-case.yml`, Name: `PR - {Description}`       |
| Job naming           | Descriptive, title case (e.g., `Lint & Format Check`)    |
| Step naming          | Imperative, title case (e.g., `Checkout repository`)     |
| Pre-commit revisions | Pinned: `rev: vX.Y.Z` — never `main`/`latest`            |
| Script shebang       | `#!/usr/bin/env bash` + `set -euo pipefail`              |
| Script output        | Emoji prefixes: ✅ pass, ❌ fail, ⚠️ warning             |
| CI Python version    | 3.14 (set in composite action default)                   |
| Trigger events       | `pull_request` for all quality gates                     |

See [references/code-style.md](references/code-style.md) for full formatting examples.

## Common Recipes

1. **New CI workflow**: create `.github/workflows/{trigger}-{action}.yml` → set `timeout-minutes` → reuse the setup-python composite → pin actions → scope permissions
2. **New pre-commit hook**: add repo entry → pin `rev` → `exclude: ^\.data/` for code hooks → add matching CI step if merge-blocking → `pre-commit run --all-files`
3. **New composite action**: `.github/actions/{name}/action.yml` → inputs with defaults → `runs: using: composite` → reference via `uses: ./.github/actions/{name}`
4. **Update a quality gate**: change `.pre-commit-config.yaml` AND `check-style.yml` together → verify flag parity → `pre-commit run {hook-id} --all-files`
5. **Exempt a CVE**: `--ignore={CVE}` on safety args → comment with CVE number, reason, version status
6. **New validation script**: `.data/skills/{name}/scripts/validate-{scope}.sh` → `set -euo pipefail` → compute `PROJECT_ROOT` → pass/fail/warn helpers → exit 1 on failure

## Monitoring & Alerting

GitHub Actions run notifications + PR status checks gate merges; pre-commit gives immediate local feedback; validation scripts check conventions on demand. No external monitoring (Prometheus/Datadog) — a CLI tool doesn't need it.

## Security

Bandit runs on every PR (`-lll -iii`); Safety scans CVEs with documented exemptions; pre-commit blocks issues before CI. Project has no deployment secrets. (Action pinning + permission scoping — see Key Patterns / Anti-Patterns.)

See [references/security-checklist.md](references/security-checklist.md) for severity-classified checklists.

## Disaster Recovery

- **Broken CI**: check Actions status → verify composite action exists → check Python version
- **Pre-commit corruption**: `pre-commit clean && pre-commit install` → `pre-commit run --all-files`
- **Rollback**: `git revert` the workflow commit — workflows are versioned in git
- **Broken gate**: `SKIP={hook-id} git commit` to unblock — fix immediately after

## Anti-Patterns

| Anti-Pattern                           | Why It's Wrong                                              |
| -------------------------------------- | ----------------------------------------------------------- |
| Using `@main`/`@latest` for actions    | Supply chain risk — action updates can break or compromise  |
| Hardcoding secrets in workflows        | Exposed in repo history — use GitHub Secrets if ever needed |
| Skipping pre-commit (`--no-verify`)    | Bypasses quality gates — fix the issue instead              |
| No `timeout-minutes` on jobs           | Runaway jobs waste CI minutes and block PRs                 |
| Docker/K8s/Terraform for this project  | Skillnir is a CLI tool — no containerization needed         |
| Adding `requirements.txt`              | `pyproject.toml` is single source of truth                  |
| Breaking CI ↔ pre-commit parity        | Developers get surprised by CI failures after local pass    |
| Overly permissive workflow permissions | Principle of least privilege — scope per job                |
| Running pylint without `.pylintrc`     | Inconsistent results between local and CI                   |

## Communication Style

- **Lead with the answer** — no preamble, no "Let me explain", no "Great question"
- **Strip filler words** — remove "basically", "essentially", "actually", "just", "simply"
- **No trailing summaries** — the user reads the diff/output, don't restate what you did
- **Bullet points over paragraphs** — lists, tables, one-liners
- **Show the config, not a lecture about it** — paste the YAML fix, not a walkthrough
- **Maximum 2-3 sentences** per explanation unless asked "why" or in Teaching mode
- **No hedging, no apologies** — say "do X", not "you might consider X"; fix mistakes silently

## Session Protocols

| Mode       | Detection Signal                                          | Behavior                            |
| ---------- | --------------------------------------------------------- | ----------------------------------- |
| Teaching   | "what is a composite action", "how does pre-commit work"  | Explain first, then generate        |
| Efficient  | "another hook like X", "same gate as check-style"         | Generate directly, minimal prose    |
| Diagnostic | "CI red", "hook failing", "workflow broken", error logs   | Diagnose before touching config     |

Default to Teaching when uncertain; developer override wins. **Self-learning** — write, never merely suggest:

- **Read [LEARNED.md](LEARNED.md) first**, before any change.
- **On correction**: acknowledge, restate as a rule, apply for the session, WRITE under `## Corrections`.
- **On undocumented convention**: check LEARNED.md → project files → ask ONE question, WRITE under `## Preferences`.
- **On discovered convention**: state it, WRITE under `## Discovered Conventions`. Format: `- YYYY-MM-DD: rule`.

## Sub-Agent Delegation

| Agent                                            | Role                            | Spawn When                           | Tools                          |
| ------------------------------------------------ | ------------------------------- | ------------------------------------ | ------------------------------ |
| [security-scanner](agents/security-scanner.md)   | CI/CD security audit            | Workflow review, secret detection    | Read Glob Grep                 |
| [pipeline-reviewer](agents/pipeline-reviewer.md) | Pipeline correctness review     | Workflow changes, parity checks      | Read Glob Grep                 |
| [hook-debugger](agents/hook-debugger.md)         | Pre-commit/CI failure diagnosis | Hook failures, CI errors, config fix | Read Edit Write Bash Glob Grep |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring cross-skill decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Rule (with WHY)                                                                                                             |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | Pin actions/hooks to a major version — `@main` is a supply-chain risk: an upstream compromise runs in CI                   |
| **MUST** follow   | Set `timeout-minutes` on every job — a runaway job blocks every PR and burns CI minutes                                    |
| **MUST** follow   | Keep CI ↔ pre-commit parity — mismatched flags surprise devs with CI failures after a clean local run                     |
| **MUST** follow   | Exclude `.data/` from code-quality hooks — prompt templates hold Python-like syntax that triggers false positives         |
| **MUST** follow   | Write corrections to LEARNED.md — otherwise the fix is lost next session                                                   |
| **SHOULD** follow | Quality-gate ordering (cheapest first), composite-action reuse, naming conventions — fail fast, less duplication           |
| **CAN** customize | Bandit threshold, pylint rules, hook selection, timeout values                                                            |

## References

| File | Description |
| --- | --- |
| [LEARNED.md](LEARNED.md) | **Auto-updated.** Corrections, preferences, conventions |
| [INJECT.md](INJECT.md) | Always-loaded quick reference (hallucination firewall) |
| [references/architecture-guide.md](references/architecture-guide.md) | Annotated `.github/` structure map + pre-commit hook list |
| [references/pipeline-patterns.md](references/pipeline-patterns.md) | Full workflow examples, gate ordering, hook config |
| [references/code-style.md](references/code-style.md) | Workflow naming, YAML structure, script conventions |
| [references/security-checklist.md](references/security-checklist.md) | Severity-classified CI/CD + dependency checklists |
| [references/deployment-guide.md](references/deployment-guide.md) | Environment topology, gate flow, distribution |
| [references/common-issues.md](references/common-issues.md) | Troubleshooting CI/hook/parity failures |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, common AI infra mistakes |
| [assets/workflow-example.yml](assets/workflow-example.yml) | Copy-paste workflow template |
| [assets/pre-commit-hook-example.yaml](assets/pre-commit-hook-example.yaml) | Copy-paste pre-commit hook entry |
| [scripts/validate-infra.sh](scripts/validate-infra.sh) | Infrastructure convention checker |

Sub-agent definitions live in [agents/](agents/) — see the Sub-Agent Delegation table above.
