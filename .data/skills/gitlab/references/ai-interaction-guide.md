# AI Interaction Guide — GitLab Skill

> Interaction modes, the cross-skill Jira handoff, MR-vs-PR terminology, the non-technical-ticket rule, and common mistakes for the gitlab skill — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

---

## Interaction Modes

Detect the mode from the user's phrasing and match your behavior to it. Modes can shift within one session — re-detect on every request. Everything instance-specific (the `<target>` branch, the branch/commit style, the project, the label taxonomy, the `<site>`, the `<Review status>`, and any glab flag differences) is auto-detected at runtime or asked and recorded to LEARNED.md — never baked in.

### Raise MR

**Signals**: "raise/open/create an MR", "make a merge request", "commit and MR", "push this branch".
**Behavior**: run the full raise-MR flow. Detect the convention first (target branch, branch style, commit style, MR template), **resolve the Jira ticket** (see Cross-Skill Handoff), confirm the ticket + branch name, then branch → commit → push → create the MR → apply existing labels/milestone → update the linked ticket.

```bash
glab mr create --source-branch <branch> --target-branch <target> --title "…" --description "$(cat <body-file>)" --yes
```

Read the URL back before touching Jira:

```bash
glab mr view <id> --output json
```

### Branch only

**Signals**: "make a branch for <KEY>-<n>", "start work on …", "just create the branch".
**Behavior**: detect the branch style, create the convention branch, then **stop** — no commit, no push, no MR. Typed repos vs bare-key repos use different grammar:

```bash
git checkout -b <type>/<KEY>-<n>-<slug>
```

```bash
git checkout -b <KEY>-<n>-<slug>
```

The `<slug>` is the ticket summary or change, lowercased and hyphenated.

### Update MR

**Signals**: "add a label", "set the milestone", "edit the MR description", "request a reviewer".
**Behavior**: modify an existing MR — do not create a new one. Discover what the project actually defines first, then apply only existing values:

```bash
glab label list
```

```bash
glab milestone list
```

```bash
glab mr update <id> --label "…" --milestone "…"
```

To replace the body from an edited file, reuse inline substitution:

```bash
glab mr update <id> --description "$(cat <body-file>)"
```

### Teaching

**Signals**: "what's our branch convention", "how does the MR flow work", "explain the Jira handoff".
**Behavior**: explain with real commands, link to `references/`, and run **no** mutating command. Read-only detection is fine — show, for example, how the target branch is resolved:

```bash
git symbolic-ref refs/remotes/origin/HEAD | sed 's@.*/@@'
```

Answer the concept, then offer to run the real flow.

---

## Cross-Skill Handoff — the Jira ticket

The tracking ticket links the MR to its work item. It comes from the [jira](../../jira/SKILL.md) skill, which holds the **active ticket in conversation context** — there is no shared file. Resolve it in this order:

1. **Reuse the active ticket from context.** If the jira skill has set one this session, adopt it silently — do not re-ask which ticket. Restate it before branching so the user sees what the MR will link:

   ```text
   Using active ticket <KEY>-<n>
   ```

2. **No active ticket → ask or hand off.** Ask the user for a key, **or** trigger the jira create flow (announce the handoff first), then adopt the resulting key. Confirm the key before you branch.

3. **No Jira at all → skip cleanly.** Ticket linking is optional. If the repo has no Jira, run the branch/commit/MR steps without a key and omit the Jira-update step — do not fabricate one. Branch and commit fall back to `<type>/<slug>` + Conventional Commits.

When a ticket is linked, the branch, commit subject, and MR title all carry the key (e.g. branch `<type>/<KEY>-<n>-<slug>`, commit `[<KEY>-<n>] <Title>`), and the flow ends by syncing the ticket. The `<site>` for any browse URL comes from `acli jira auth status`, never a hardcoded domain:

```bash
acli jira auth status
```

```bash
acli jira workitem comment create --key <KEY>-<n> --body "MR: <url>"
```

```bash
acli jira workitem transition --key <KEY>-<n> --status "<Review status>" --yes
```

The `<Review status>` is instance-specific — `acli` cannot list valid transitions, so pull the name from LEARNED.md or ask, never assume a fixed string. On rejection, surface acli's exact error and record the real name to LEARNED.md. On GitHub, hand off to [github](../../github/SKILL.md) instead of running any of this against `{owner}/{repo}`.

---

## MR Terminology — Merge Request, not Pull Request

GitLab uses **Merge Request (MR)** everywhere; "Pull Request" / "PR" is GitHub's term. Say "MR", "raise an MR", "the merge request" in every message, title, description, and commit note. Calling it a pull request signals the wrong platform and the wrong skill — that work belongs to [github](../../github/SKILL.md). The CLI is `glab`, and its verbs are `mr`:

```bash
glab mr create --help
```

---

## Keeping the Jira Ticket Non-Technical

The ticket describes user-visible behavior; the **MR** carries the technical detail. Never push file paths, function or class names, stack traces, branch names, or internal identifiers into the ticket comment or description. The MR link and its own description hold that context — the Jira comment is just the pointer:

```bash
acli jira workitem comment create --key <KEY> --body "MR: <url>"
```

Replace `<KEY>` with the real issue key (for example `PROJ-123` or `ABC-42`). Keep the ticket readable by a non-engineer.

---

## Common Mistakes

- **Assuming glab flag names without checking.** Flags vary by glab version. Confirm with `glab mr create --help` (and each subcommand's `--help`) on first use and record any differences to LEARNED.md.
- **Hardcoding the target branch, branch style, commit style, or project.** They differ per repo — detect them (`git symbolic-ref …`, `git for-each-ref …`, `git log -50 --format='%s'`, `Glob .gitlab/merge_request_templates/*.md`). The project auto-resolves from the git remote; never paste a literal `{owner}/{repo}` you assumed.
- **Calling it a pull request.** GitLab uses Merge Requests — match the platform's terminology in every message, title, and commit. A PR is a GitHub artifact, not this skill's.
- **Skipping the Jira update when a ticket is linked.** Dropping the MR-link comment and the review transition removes a core purpose of the skill. Run both, then record the confirmed `<Review status>` to LEARNED.md.
- **Applying a label or milestone that doesn't exist.** `glab mr create --label` does not create labels, and it errors on unknown ones. Discover first (`glab label list`, `glab milestone list`), apply only what exists, and report the rest.
- **Putting ticket / skill / persona names in code comments.** Comments explain the code, not the process. Keys like `<KEY>-<n>`, "gitlab skill", and reviewer names belong in the branch, commit subject, MR, or ticket — never in source comments.

---

## Self-Learning

When a user correction or discovery reveals a durable convention, write it to [LEARNED.md](../LEARNED.md) under the matching heading:

- **Corrections** → `## Corrections` — the user overrode something you did.
- **Preferences** → `## Preferences` — a stated way the user wants MR work handled.
- **Discovered Conventions** → `## Discovered Conventions` — confirmed facts such as this repo's `<target>` branch, its branch/commit style, the MR-template path, the label taxonomy, the linked-Jira `<Review status>`, or a glab flag that differs from the recipes here.

Use the exact format, one rule per line:

```text
- YYYY-MM-DD: rule description
```

The active Jira ticket is the one thing that never goes to LEARNED.md — it is held in conversation context by the jira skill and is deliberately gone at session end.
