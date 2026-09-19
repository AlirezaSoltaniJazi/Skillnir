---
name: github
description: >-
  Reusable GitHub pull-request skill. Creates convention-correct branches, commits,
  and PRs through the authenticated gh CLI, auto-detecting each repo's branch, commit,
  and PR-template convention from git history and repo docs. Builds the PR body from
  the diff and the repo's PR template, applies existing labels/milestone, then updates
  the linked Jira ticket (adds the PR link and transitions it to the review state).
  Activates when the user asks to "raise/open/create a PR", "make a pull request",
  "push this branch", "commit and PR", or wants a branch named for a Jira ticket.
compatibility: "GitHub CLI (gh) authenticated; git 2.x; optional Jira link via acli"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: delivery
allowed-tools: Read Edit Write Bash(gh:*) Bash(git:*) Bash(acli:*) Glob Grep
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Command blocks go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It holds corrections, preferences, and per-repo conventions (branch style, base branch, PR-template path, label taxonomy, the linked Jira review status) discovered in previous sessions. Every rule there overrides defaults in this skill.

**Announce skill usage.** Say "Using: github skill" at the very start of your response before doing any work.

**Preflight**: run `gh auth status`. Note the token's scopes — if it lacks `project`, never pass `gh pr create -p` (adding a PR to a GitHub Project needs that scope).

## When to Use

1. Raising a pull request following the repo's convention
2. Creating a convention-named branch for a Jira ticket
3. Committing with the repo's ticket-prefixed subject format
4. Building a PR body from the diff + the repo's PR template
5. Applying labels / milestone and updating the linked Jira ticket

## Do NOT Use

- **GitLab merge requests** — use [gitlab](../gitlab/SKILL.md) (wrong platform; `gh` can't open MRs).
- **Creating or transitioning Jira tickets as the primary task** — use [jira](../jira/SKILL.md). This skill only _updates_ the linked ticket at the end of the PR flow.
- **CI/CD workflow files** (`.github/workflows/`), pre-commit, quality gates — use [devopsEngineer](../devopsEngineer/SKILL.md) (workflow/pipeline YAML is a different concern from raising a PR).
- **Never** add file paths / code to the Jira ticket — keep the ticket non-technical; technical detail goes in the PR body.

## Access & Convention Detection

| Fact           | Value                                                          |
| -------------- | -------------------------------------------------------------- |
| Tool           | `gh` CLI (authenticated) + `git`                               |
| Owner / repo   | Auto-resolved from the current repo — never hardcode           |
| Default branch | **Detect, don't assume**                                       |
| Token scopes   | From `gh auth status` — no `project` ⇒ never `gh pr create -p` |

**Detect the convention before acting** (never hardcode):

| What         | How                                                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Base branch  | `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`                                                                                              |
| Branch style | `git for-each-ref --format='%(refname:short)' refs/heads refs/remotes` → typed `^(feature\|feat\|fix\|refactor\|ci)/` vs bare `^[A-Z]+-[0-9]+-`                 |
| Commit style | `git log -50 --format='%s'` → `[KEY-###] …` vs `KEY-###: …` vs Conventional Commits                                                                             |
| PR template  | `Glob` `pull_request_template.md` \| `PULL_REQUEST_TEMPLATE.md` \| `PULL_REQUEST_TEMPLATE/*` — each valid under `.github/`, repo root, or `docs/` (case varies) |
| Repo rules   | `Read` repo `CLAUDE.md`/`agents.md`/`CONTRIBUTING.md` for any branch/PR/label rules                                                                             |

If no ticket-key pattern exists in history, fall back to `<type>/<slug>` branches + Conventional Commits and ask. Persist confirmed per-repo conventions to LEARNED.md. Details: [references/branch-naming.md](references/branch-naming.md), [references/commit-conventions.md](references/commit-conventions.md), [references/pr-templates.md](references/pr-templates.md).

## Raise-PR Flow (core protocol)

1. **Detect the convention** (above).
2. **Resolve the Jira ticket** — reuse the **active ticket held in conversation context** by the [jira](../jira/SKILL.md) skill. If none: ask for a key, or trigger the jira create flow (announce the handoff), then adopt the resulting key. Confirm the key before branching. (Ticket linking is optional — skip cleanly if the repo has no Jira.)
3. **Branch** (slug = ticket summary or change, lowercased, hyphenated):
   - Typed repos: `git checkout -b <type>/<KEY>-<n>-<slug>` (type ∈ feature/feat/fix/refactor/ci — infer or ask).
   - Bare-key repos: `git checkout -b <KEY>-<n>-<slug>` (no type prefix).
4. **Stage + commit** per the detected style:
   - `git add -A && git commit -m "[<KEY>-<n>] <Title>"` (or `<KEY>-<n>: <Desc>` where that's the style).
     The `(#PR)` suffix some repos show is GitHub's squash-merge number — added at merge, not authored here.
5. **Push**: `git push -u origin <branch>`.
6. **PR title**: match the commit style, e.g. `[<KEY>-<n>] <Short desc>`.
7. **PR body** — "description updated based on the PR": load the repo's template (if any) and fill the ticket URL + a Summary generated from `git diff <base>...HEAD --stat` + commit subjects; keep the template's checklists. No template → `gh pr create --fill`.
8. **Create the PR**:
   `gh pr create --base <default> --head <branch> --title "…" --body-file -` (heredoc), then capture the URL (`gh pr view <n> --json url,number`).
9. **Labels / milestone**: discover with `gh label list --json name` and `gh api repos/{owner}/{repo}/milestones`; apply the ones the repo actually defines (type, component, version, etc.) via `gh pr edit <n> --add-label … --milestone <m>`. **Apply only what already exists; skip and report the rest.**
10. **Update Jira** (optional, if a ticket is linked — via acli, the same recipes the jira skill documents):
    `acli jira workitem comment create --key <KEY>-<n> --body "PR: <url>"`
    then `acli jira workitem transition --key <KEY>-<n> --status "<Review status>" --yes`.
    On transition error, surface acli's message and record the real status name to LEARNED.md.

Full commands: [references/pr-recipes.md](references/pr-recipes.md). Label handling: [references/labels-and-milestones.md](references/labels-and-milestones.md).

## Cooperation with the jira / gitlab skills

- `github` reads the **active Jira ticket from conversation context** (set by [jira](../jira/SKILL.md)); there is no shared file.
- Both carry the acli recipes in `references/`, so the Jira-update step works even if the jira skill isn't loaded.
- If no ticket is active, ask for a key or hand off to the jira create flow, then continue. On GitLab, use [gitlab](../gitlab/SKILL.md) instead.

## Anti-Patterns

| Anti-Pattern                                        | Why It's Wrong                                                          |
| --------------------------------------------------- | ----------------------------------------------------------------------- |
| `gh pr create -p` without the `project` scope       | The call fails — check scopes in `gh auth status` first                 |
| Hardcoding base branch / branch style / owner       | They differ per repo — detect them                                      |
| Skipping the Jira update when a ticket is linked    | Drops the ticket link + review transition — a core purpose of the skill |
| Applying a label/milestone that doesn't exist       | `gh` errors; discover first, apply only what exists, report the rest    |
| Ticket / skill / persona names in code comments     | Comments explain code, not process                                      |
| Writing the `(#PR)` number into the commit yourself | It's assigned by GitHub at squash-merge                                 |

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode        | Detection Signal                                            | Behavior                                                           |
| ----------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Raise PR    | "raise/open a PR", "pull request", "commit and PR"          | Run the full raise-PR flow; confirm the ticket + branch name first |
| Branch only | "make a branch for KEY-###", "start work on …"              | Detect style, create the convention branch, stop                   |
| Update PR   | "add label", "set milestone", "edit the PR body"            | `gh pr edit`; discover existing labels/milestones first            |
| Teaching    | "what's our branch convention", "how does the PR flow work" | Explain with real commands, link to references/                    |

**Self-Learning**: write learnings to LEARNED.md — Corrections → `## Corrections`, Preferences → `## Preferences`, discovered facts (per-repo base branch, branch/commit style, template path, label taxonomy, linked-Jira review status) → `## Discovered Conventions`. Format: `- YYYY-MM-DD: rule description`.

## Freedom Levels

| Level             | Scope                                                                                                                                                                                                                                           |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | Detect convention (never hardcode base/branch/commit style/owner); branch + commit + title carry the ticket key when one is linked; build the PR body from the diff + template; update the linked Jira ticket; never use `-p` without the scope |
| **SHOULD** follow | Announce skill usage; preflight `gh auth status`; reuse the active ticket from context; apply only existing labels/milestones and report gaps; record conventions to LEARNED.md                                                                 |
| **CAN** customize | Branch `type` choice, slug wording, the diff-summary format, label/component selection                                                                                                                                                          |

## References

| File                                                                       | Description                                                                                                        |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [LEARNED.md](LEARNED.md)                                                   | **Auto-updated.** Corrections, preferences, confirmed conventions                                                  |
| [INJECT.md](INJECT.md)                                                     | Always-loaded quick reference (hallucination firewall)                                                             |
| [references/pr-recipes.md](references/pr-recipes.md)                       | Verified `gh` commands, body-via-stdin, label/milestone discovery + apply, `--dry-run`, the acli Jira-update calls |
| [references/branch-naming.md](references/branch-naming.md)                 | Branch grammar (typed vs bare-key), slug rules, detection                                                          |
| [references/commit-conventions.md](references/commit-conventions.md)       | `[KEY-###]` vs `KEY-###:` vs Conventional Commits, the `(#PR)` note                                                |
| [references/pr-templates.md](references/pr-templates.md)                   | Finding + filling the repo's PR template; `--fill` fallback                                                        |
| [references/labels-and-milestones.md](references/labels-and-milestones.md) | Discover-then-apply rule for labels/milestones                                                                     |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md)   | Modes, cross-skill handoff, non-technical-Jira rule, common mistakes                                               |
| [scripts/validate-github.sh](scripts/validate-github.sh)                   | Read-only preflight: `gh` on PATH + auth status                                                                    |
