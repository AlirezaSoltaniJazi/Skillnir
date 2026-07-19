# GitHub Skill — AI Interaction Guide

> Interaction modes, the jira cross-skill handoff, the non-technical-Jira rule, and the common mistakes for the github skill — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

---

## Interaction Modes

Detect the mode from the user's phrasing, then run only the steps that mode needs. Modes can shift within one session — re-detect on every request. Corrections and preferences persist via [LEARNED.md](../LEARNED.md).

### Raise PR

**Signals**: "raise/open/create a PR", "make a pull request", "commit and PR", "push this and open a PR".

**Behavior**: run the full raise-PR flow — detect the repo's convention, resolve the Jira ticket, branch, commit, push, build the PR body from the diff + template, create the PR, apply the labels/milestone/component the repo actually defines, then update the linked Jira ticket. Confirm the ticket key and branch name before branching.

```bash
gh pr create --base <default> --head <branch> --title "[<KEY>-<n>] <Short desc>" --body-file -
```

### Branch only

**Signals**: "make a branch for `<KEY>-<n>`", "start work on …", "just create the branch".

**Behavior**: detect the branch style, create the convention branch, and stop. No commit, no PR, no Jira update.

```bash
git checkout -b <type>/<KEY>-<n>-<slug>
```

### Update PR

**Signals**: "add a label", "set the milestone", "edit the PR body", "attach the component".

**Behavior**: edit an existing PR. Discover what already exists first, then apply. Apply only labels/milestones the repo defines; skip and report the rest.

```bash
gh pr edit <n> --add-label <label> --milestone <version>
```

### Teaching

**Signals**: "what's our branch convention", "how does the PR flow work", "why no `-p`".

**Behavior**: explain with real commands from this skill and link to the relevant `references/` file. Do not create branches, commits, or PRs.

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

---

## Cross-Skill Handoff (jira)

The github skill never owns the Jira ticket — it reuses one. There is no shared file; the active ticket lives only in conversation context.

1. **Reuse the active ticket.** If the [jira](../../jira/SKILL.md) skill has already resolved a ticket earlier in the conversation, adopt that key (e.g. `PROJ-123`, `ABC-42`). Confirm it before branching.
2. **If no ticket is active**, either ask the user for a key, or trigger the jira create flow and adopt the key it returns. Announce the handoff so the user sees the mode switch.
3. **If the repo has no Jira**, skip the ticket steps cleanly — branch, commit, push, and open the PR without a ticket key, and drop the final Jira update. Do not invent a key.
4. **Otherwise continue** the raise-PR flow with the adopted key threaded through the branch, commit subject, PR title, the PR-body Ticket URL, and the final Jira update.

```bash
acli jira workitem comment create --key <KEY>-<n> --body "PR: <url>"
```

```bash
acli jira workitem transition --key <KEY>-<n> --status "<Review status>" --yes
```

Both skills carry these acli recipes in their `references/`, so the Jira-update step still works when the jira skill is not loaded. `<Review status>` is instance-specific — detect it, ask, or read it from LEARNED.md; never assume a fixed string. If the transition status name is rejected, surface acli's exact message (it cannot list transitions) and record the real status name to LEARNED.md.

---

## The Jira Ticket Stays Non-Technical

Keep the two artifacts separated by audience:

- **Jira ticket** — the "what" and "why" for a non-engineering reader. Never add file paths, code, branch names, commit hashes, or diff detail to the ticket. Its only technical addition is the PR link.
- **PR body** — the "how" for reviewers. All technical detail lives here: the diff summary, the commit subjects, the repo template's checklists, and any CI / test-run links.

```bash
git diff <base>...HEAD --stat
```

The PR-body Ticket URL is `<site>/browse/<KEY>-<n>`. Read `<site>` from the CLI's auth status — never hardcode a Jira domain.

```bash
acli jira auth status
```

If the user asks to paste code or paths into the ticket, restate the rule and route that detail into the PR body instead.

---

## Common Mistakes

- **Using `-p` without the scope.** The token's scopes may not include `project` — then `gh pr create -p` fails. Check scopes first and never pass `-p` when the scope is absent.

  ```bash
  gh auth status
  ```

- **Hardcoding base / branch / commit style / owner.** They differ per repo — some repos have no type prefix and use `<KEY>-<n>: <Desc>` commits, others use `[<KEY>-<n>] <Title>` or Conventional Commits; the owner/repo is `{owner}/{repo}` resolved from the current repo. Detect the default branch and history; never assume a branch name or a fixed prefix.

  ```bash
  gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
  ```

  ```bash
  git log -50 --format='%s'
  ```

- **Skipping the Jira update.** When a ticket is linked, a PR with no acli comment + transition drops the Jira side of the flow. Always comment the PR link and transition to the repo's `<Review status>`. (Skip only when the repo has no Jira.)

  ```bash
  acli jira workitem transition --key <KEY>-<n> --status "<Review status>" --yes
  ```

- **Applying non-existent labels.** `gh pr edit --add-label` errors on a label the repo does not define. Discover first, then apply only what exists and report the gaps.

  ```bash
  gh label list --json name
  ```

- **Writing the `(#PR)` number by hand.** The `(#PR)` suffix is GitHub's squash-merge number, assigned at merge — never author it into the commit subject or PR title yourself.

- **Putting ticket / skill names in code comments.** Where a repo's contribution docs (`CLAUDE.md` / `CONTRIBUTING.md`) require it, comments explain code, not process — keep Jira keys, skill names, and persona names out of source comments.

---

## Self-Learning

Write learnings to [LEARNED.md](../LEARNED.md) as you discover them:

- **Corrections** → `## Corrections`
- **Preferences** → `## Preferences`
- **Discovered conventions** (per-repo base branch, branch/commit style, PR-template path, label taxonomy, the real `<Review status>`) → `## Discovered Conventions`

Format every entry as `- YYYY-MM-DD: rule`.

```text
- YYYY-MM-DD: This repo uses bare <KEY>-<n>-<slug> branches and <KEY>-<n>: <Desc> commits (no type prefix).
```
