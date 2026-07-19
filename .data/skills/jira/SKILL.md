---
name: jira
description: >-
  Reusable Jira work-item skill. Creates, searches, views, transitions, and comments
  on Jira issues through the authenticated Atlassian CLI (acli) against whatever Jira
  site the CLI is logged into, auto-detecting the project key from git context. The
  create flow builds a ticket as a child under a user-selected Epic or Story. Activates
  when the user mentions a Jira ticket, issue, story, epic, task, or bug; asks to
  "create a ticket", "raise a Jira", "log a task", "move it to review/done", update,
  transition, or comment on an issue; or references an issue key like ABC-123.
compatibility: "Atlassian CLI (acli) authenticated to a Jira Cloud site; git 2.x"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: planning
allowed-tools: Read Grep Glob Bash(acli:*) Bash(git:*)
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Command blocks go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It holds corrections, preferences, and per-repo conventions (the confirmed project key, the team's review status name) discovered in previous sessions. Every rule there overrides defaults in this skill.

**Announce skill usage.** Say "Using: jira skill" at the very start of your response before doing any work.

**Preflight once per session**: run `acli jira auth status`. It reports the authenticated **site** and account — use that site for every issue URL; never hardcode a domain. If not authenticated, stop and tell the user to run `acli jira auth login` — never guess credentials.

## When to Use

1. Creating a Jira ticket as a child under an Epic or Story
2. Searching / listing issues (find a parent, "my open issues", by summary)
3. Viewing an issue's fields
4. Transitioning status (e.g. to the team's review or done state)
5. Commenting on an issue (e.g. attaching a PR/MR link)
6. Editing summary / assignee / labels on an existing issue

## Do NOT Use

- **Raising PRs / MRs, creating branches, or commits** — use [github](../github/SKILL.md) (GitHub) or [gitlab](../gitlab/SKILL.md) (GitLab). This skill never touches git branches.
- **Putting file paths, code, function/class names, or internal identifiers into a Jira description** — those belong in the PR/MR. Keep Jira text non-technical.
- **Skill-system meta-rules** (SKILL.md structure, LEARNED.md format) — use [skillnir](../skillnir/SKILL.md).

## Access & Conventions

| Fact          | Value                                                                                               |
| ------------- | --------------------------------------------------------------------------------------------------- |
| Tool          | `acli jira workitem …` (Atlassian CLI)                                                              |
| Site          | Whatever `acli jira auth status` reports — never hardcode                                           |
| Issue URL     | `<site>/browse/<KEY>-<n>`                                                                           |
| Project key   | **Auto-detect per repo — never hardcode** (see below)                                               |
| Review status | Instance-specific (e.g. "In Review", "In Code Review") — detect from LEARNED.md or ask, then record |
| Descriptions  | Non-technical: user-visible problem, repro, expected vs actual, plain-language cause/fix            |

**Detect the project key** (first hit wins, most-frequent prefix): repo docs (`CLAUDE.md`/`agents.md`/`README`) → recent branches (`git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'`) → recent commits (`git log -50 --format='%s'`). If two keys compete or none is found, ask ONE question and record the answer to LEARNED.md. Full recipe: [references/conventions.md](references/conventions.md).

## Create-Ticket Flow (core protocol)

Build a **child under a user-selected parent** (Epic or Story). Never mutate Jira before the confirm step.

1. **Detect the project key** (above).
2. **Ask the issue type** — Story / Task / Bug / Sub-task — unless it's clear from the request.
3. **Search for the parent** and present a numbered list; the user picks the Epic/Story:
   `acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --csv`
   Refine with `AND summary ~ "<term>"` when the user names the area.
4. **Gather** the summary and a **non-technical** description.
5. **Confirm** every field back to the user: project, type, parent, summary, description, assignee.
6. **Create**:
   `acli jira workitem create --project <KEY> --type <Type> --parent <PARENT> --summary "…" --description "…" --assignee @me --json`
   Parse `key` from the JSON. If `--parent` is rejected, use the fallback ladder in [references/acli-recipes.md](references/acli-recipes.md).
7. **Report** the new `KEY-nnn` and its browse URL (built from the site in `auth status`).
8. **Record it as the session active ticket** (below).

Step-by-step script: [references/create-ticket-flow.md](references/create-ticket-flow.md). JQL patterns: [references/jql-cookbook.md](references/jql-cookbook.md).

## Session Active Ticket (conversation context only)

The active ticket lives **only in your working context** — no file, no LEARNED.md entry. It is gone at session end. This is deliberate.

- After creating, viewing, or resolving a specific ticket, state and hold: **`Active ticket: KEY-nnn — <summary>`**.
- On later Jira or PR/MR requests in the same session, **reuse the active ticket** — restate `Using active ticket KEY-nnn` before any mutation, don't re-ask.
- **Before creating a NEW ticket while one is active**, ask: `You have active ticket KEY-nnn. Create a new one instead of using it? (y/n)`. Same guard before replacing the active pointer.
- The [github](../github/SKILL.md) and [gitlab](../gitlab/SKILL.md) skills read this same active ticket from context when raising a PR/MR.

## Common Recipes

| Task           | Command                                                                                                                   |
| -------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Auth preflight | `acli jira auth status`                                                                                                   |
| Search parents | `acli jira workitem search --jql "…" --fields "key,summary,issuetype,status" --csv`                                       |
| Create child   | `acli jira workitem create --project <KEY> --type <T> --parent <P> --summary "…" --description "…" --assignee @me --json` |
| View           | `acli jira workitem view <KEY> --fields "key,summary,status,assignee,description" --json`                                 |
| Transition     | `acli jira workitem transition --key <KEY> --status "<Review status>" --yes`                                              |
| Comment        | `acli jira workitem comment create --key <KEY> --body "…"`                                                                |
| Edit           | `acli jira workitem edit --key <KEY> --summary "…" --assignee "…"`                                                        |

Full flags, JSON/CSV parsing, and fallbacks: [references/acli-recipes.md](references/acli-recipes.md).

## Anti-Patterns

| Anti-Pattern                                             | Why It's Wrong                                                                                 |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Hardcoding a project key or Jira domain                  | Both differ per repo/instance — detect the key from git, the site from `acli jira auth status` |
| Technical Jira descriptions (paths, symbols, code)       | Read by PMs/QA/non-engineers; implementation detail belongs in the PR/MR                       |
| Mutating before the confirm step                         | Search/view are read-only; create/transition/comment/edit change state — confirm first         |
| Creating a new ticket while one is active without asking | Silently loses the user's working context                                                      |
| Guessing a transition status name                        | acli can't list transitions; surface its error and record the real name to LEARNED.md          |

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                         | Behavior                                                                        |
| ---------- | -------------------------------------------------------- | ------------------------------------------------------------------------------- |
| Create     | "create/raise/log a ticket", "new story/task/bug"        | Run the create-ticket flow; confirm before creating                             |
| Update     | "assign", "rename", "add label", "edit KEY-###"          | `workitem edit`; confirm the change                                             |
| Transition | "move to", "in review", "done", "in progress"            | `workitem transition`; on error surface acli's message + record the real status |
| Search     | "find", "which epic", "my open issues", "list stories"   | Read-only `workitem search`; present a numbered list                            |
| Teaching   | "how does acli", "what's the parent", "explain the flow" | Explain with real commands, link to references/                                 |

**Self-Learning**: write learnings to LEARNED.md — Corrections → `## Corrections`, Preferences → `## Preferences`, discovered facts (confirmed project key, real review-status name, `--parent` behaviour on this instance) → `## Discovered Conventions`. Format: `- YYYY-MM-DD: rule description`.

## Freedom Levels

| Level             | Scope                                                                                                                                                                           |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | Detect key + site (never hardcode); confirm before any mutation; non-technical descriptions; child created under a user-selected parent; hold the active ticket in context only |
| **SHOULD** follow | Announce skill usage; preflight `acli jira auth status`; present searches as numbered lists; record confirmed conventions to LEARNED.md                                         |
| **CAN** customize | JQL filters, field selections, `--csv` vs `--json` parsing, default issue type per repo                                                                                         |

## References

| File                                                                     | Description                                                                             |
| ------------------------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, confirmed conventions                       |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)                                  |
| [references/acli-recipes.md](references/acli-recipes.md)                 | Every verified `acli jira` command, flags, JSON/CSV parsing, `--parent` fallback ladder |
| [references/conventions.md](references/conventions.md)                   | Key-detection recipe, site-from-auth rule, review-status handling, non-technical rule   |
| [references/create-ticket-flow.md](references/create-ticket-flow.md)     | Full child-under-parent protocol + confirmation script                                  |
| [references/jql-cookbook.md](references/jql-cookbook.md)                 | Parent search, my-open-issues, summary search, status filters                           |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Modes, active-ticket memory rules, common mistakes                                      |
| [scripts/validate-jira.sh](scripts/validate-jira.sh)                     | Read-only preflight: `acli` on PATH + auth status                                       |
