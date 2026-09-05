---
name: gitlab
description: >-
  Reusable GitLab merge-request skill. Creates convention-correct branches, commits,
  and merge requests through the authenticated glab CLI, auto-detecting each repo's
  branch, commit, and MR-template convention from git history and repo docs. Builds
  the MR description from the diff and the repo's MR template, applies existing
  labels/milestone, then updates the linked Jira ticket (adds the MR link and
  transitions it to the review state). Activates when the user asks to "raise/open/create
  an MR", "make a merge request", "push this branch", "commit and MR", or wants a
  branch named for a Jira ticket on a GitLab project.
compatibility: "GitLab CLI (glab) authenticated; git 2.x; optional Jira link via acli"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: delivery
allowed-tools: Read Edit Write Bash(glab:*) Bash(git:*) Bash(acli:*) Glob Grep
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Command blocks go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It holds corrections, preferences, and per-repo conventions (branch style, target branch, MR-template path, label taxonomy, the linked Jira review status, and any glab flag differences confirmed on this machine). Every rule there overrides defaults in this skill.

**Announce skill usage.** Say "Using: gitlab skill" at the very start of your response before doing any work.

**Preflight**: run `glab auth status`. If `glab` is not installed, tell the user to install the GitLab CLI (`glab`) and run `glab auth login` — never guess credentials. **Confirm exact flags with `glab mr create --help` on first use** and record any differences to LEARNED.md (flag names can vary by glab version).

## When to Use

1. Raising a merge request following the repo's convention
2. Creating a convention-named branch for a Jira ticket
3. Committing with the repo's ticket-prefixed subject format
4. Building an MR description from the diff + the repo's MR template
5. Applying labels / milestone and updating the linked Jira ticket

## Do NOT Use

- **GitHub pull requests** — use [github](../github/SKILL.md) (wrong platform; `glab` targets GitLab MRs, not GitHub PRs).
- **Creating or transitioning Jira tickets as the primary task** — use [jira](../jira/SKILL.md). This skill only _updates_ the linked ticket at the end of the MR flow.
- **CI/CD pipeline files** (`.gitlab-ci.yml`) — use [devopsEngineer](../devopsEngineer/SKILL.md) (pipeline YAML is a different concern from raising an MR).
- **Never** add file paths / code to the Jira ticket — keep the ticket non-technical; technical detail goes in the MR description.

## Access & Convention Detection

| Fact          | Value                                                |
| ------------- | ---------------------------------------------------- |
| Tool          | `glab` CLI (authenticated) + `git`                   |
| Project       | Auto-resolved from the current repo — never hardcode |
| Target branch | **Detect, don't assume** (often `main` or `master`)  |
| Terminology   | GitLab uses **Merge Request (MR)**, not Pull Request |

**Detect the convention before acting** (never hardcode):

| What          | How                                                                                                                                             |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Target branch | `glab repo view` (shows the default branch), or strip `origin/` from `git symbolic-ref --short refs/remotes/origin/HEAD`                        |
| Branch style  | `git for-each-ref --format='%(refname:short)' refs/heads refs/remotes` → typed `^(feature\|feat\|fix\|refactor\|ci)/` vs bare `^[A-Z]+-[0-9]+-` |
| Commit style  | `git log -50 --format='%s'` → `[KEY-###] …` vs `KEY-###: …` vs Conventional Commits                                                             |
| MR template   | `Glob` `.gitlab/merge_request_templates/*.md` (project templates)                                                                               |
| Repo rules    | `Read` repo `CLAUDE.md`/`agents.md`/`CONTRIBUTING.md` for any branch/MR/label rules                                                             |

If no ticket-key pattern exists in history, fall back to `<type>/<slug>` branches + Conventional Commits and ask. Persist confirmed per-repo conventions to LEARNED.md. Details: [references/branch-naming.md](references/branch-naming.md), [references/commit-conventions.md](references/commit-conventions.md), [references/mr-templates.md](references/mr-templates.md).

## Raise-MR Flow (core protocol)

1. **Detect the convention** (above).
2. **Resolve the Jira ticket** — reuse the **active ticket held in conversation context** by the [jira](../jira/SKILL.md) skill. If none: ask for a key, or trigger the jira create flow (announce the handoff), then adopt the resulting key. Confirm the key before branching. (Ticket linking is optional — skip cleanly if the repo has no Jira.)
3. **Branch** (slug = ticket summary or change, lowercased, hyphenated):
   - Typed repos: `git checkout -b <type>/<KEY>-<n>-<slug>`.
   - Bare-key repos: `git checkout -b <KEY>-<n>-<slug>`.
4. **Stage + commit** per the detected style:
   - `git add -A && git commit -m "[<KEY>-<n>] <Title>"` (or `<KEY>-<n>: <Desc>` where that's the style).
5. **Push**: `git push -u origin <branch>`.
6. **MR title**: match the commit style, e.g. `[<KEY>-<n>] <Short desc>`.
7. **MR description** — "description updated based on the MR": load the repo's MR template (if any) and fill the ticket URL + a Summary generated from `git diff <target>...HEAD --stat` + commit subjects; keep the template's checklists. No template → `glab mr create --fill`.
8. **Create the MR**:
   `glab mr create --source-branch <branch> --target-branch <target> --title "…" --description "$(cat <body-file>)" --yes`, then capture the URL (`glab mr view <id> --output json`).
9. **Labels / milestone**: discover with `glab label list` and `glab milestone list` (fall back to `glab api "projects/:id/milestones"` on older `glab`); apply the ones the repo actually defines via `glab mr update <id> --label "…" --milestone "…"` (or set them on `glab mr create`). **Apply only what already exists; skip and report the rest.**
10. **Update Jira** (optional, if a ticket is linked — via acli, the same recipes the jira skill documents):
    `acli jira workitem comment create --key <KEY>-<n> --body "MR: <url>"`
    then `acli jira workitem transition --key <KEY>-<n> --status "<Review status>" --yes`.
    On transition error, surface acli's message and record the real status name to LEARNED.md.

Full commands: [references/glab-recipes.md](references/glab-recipes.md). Label handling: [references/labels-and-milestones.md](references/labels-and-milestones.md).

## Cooperation with the jira / github skills

- `gitlab` reads the **active Jira ticket from conversation context** (set by [jira](../jira/SKILL.md)); there is no shared file.
- Both carry the acli recipes in `references/`, so the Jira-update step works even if the jira skill isn't loaded.
- If no ticket is active, ask for a key or hand off to the jira create flow, then continue. On GitHub, use [github](../github/SKILL.md) instead.

## Anti-Patterns

| Anti-Pattern                                      | Why It's Wrong                                                                     |
| ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Assuming glab flag names without checking         | Flags vary by version — confirm with `glab mr create --help`, record to LEARNED.md |
| Hardcoding target branch / branch style / project | They differ per repo — detect them                                                 |
| Calling it a "pull request"                       | GitLab uses Merge Requests; match the platform's terminology                       |
| Skipping the Jira update when a ticket is linked  | Drops the ticket link + review transition — a core purpose of the skill            |
| Applying a label/milestone that doesn't exist     | `glab` errors; discover first, apply only what exists, report the rest             |
| Ticket / skill / persona names in code comments   | Comments explain code, not process                                                 |

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode        | Detection Signal                                            | Behavior                                                           |
| ----------- | ----------------------------------------------------------- | ------------------------------------------------------------------ |
| Raise MR    | "raise/open an MR", "merge request", "commit and MR"        | Run the full raise-MR flow; confirm the ticket + branch name first |
| Branch only | "make a branch for KEY-###", "start work on …"              | Detect style, create the convention branch, stop                   |
| Update MR   | "add label", "set milestone", "edit the MR description"     | `glab mr update`; discover existing labels/milestones first        |
| Teaching    | "what's our branch convention", "how does the MR flow work" | Explain with real commands, link to references/                    |

**Self-Learning**: write learnings to LEARNED.md — Corrections → `## Corrections`, Preferences → `## Preferences`, discovered facts (per-repo target branch, branch/commit style, MR-template path, label taxonomy, linked-Jira review status, confirmed glab flags) → `## Discovered Conventions`. Format: `- YYYY-MM-DD: rule description`.

## Freedom Levels

| Level             | Scope                                                                                                                                                                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | Detect convention (never hardcode target/branch/commit style/project); branch + commit + title carry the ticket key when one is linked; build the MR description from the diff + template; update the linked Jira ticket; confirm glab flags before relying on them |
| **SHOULD** follow | Announce skill usage; preflight `glab auth status`; reuse the active ticket from context; apply only existing labels/milestones and report gaps; record conventions to LEARNED.md                                                                                   |
| **CAN** customize | Branch `type` choice, slug wording, the diff-summary format, label/milestone selection                                                                                                                                                                              |

## References

| File                                                                       | Description                                                                                    |
| -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                   | **Auto-updated.** Corrections, preferences, confirmed conventions + glab flags                 |
| [INJECT.md](INJECT.md)                                                     | Always-loaded quick reference (hallucination firewall)                                         |
| [references/glab-recipes.md](references/glab-recipes.md)                   | `glab` commands for MRs, labels, milestones, description-from-file, the acli Jira-update calls |
| [references/branch-naming.md](references/branch-naming.md)                 | Branch grammar (typed vs bare-key), slug rules, detection                                      |
| [references/commit-conventions.md](references/commit-conventions.md)       | `[KEY-###]` vs `KEY-###:` vs Conventional Commits, detection                                   |
| [references/mr-templates.md](references/mr-templates.md)                   | Finding + filling `.gitlab/merge_request_templates/`; `--fill` fallback                        |
| [references/labels-and-milestones.md](references/labels-and-milestones.md) | Discover-then-apply rule for labels/milestones                                                 |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md)   | Modes, cross-skill handoff, non-technical-Jira rule, common mistakes                           |
| [scripts/validate-gitlab.sh](scripts/validate-gitlab.sh)                   | Read-only preflight: `glab` on PATH + auth status                                              |
