# Commit Subject Conventions

> Generic branch, commit-subject, and label conventions for the github skill — referenced from SKILL.md. Everything instance-specific is auto-detected from the repo at runtime or asked once and recorded to LEARNED.md; nothing here is hardcoded.

---

## Detect the repo's commit style first

Never assume a style. Read the last 50 subjects and let the dominant pattern decide.

```bash
git log -50 --format=%s
```

Match what you see against the three common styles below and pick the one the majority of recent subjects follow. If two compete, or if no issue-key pattern appears at all, ask ONE question and record the answer to LEARNED.md.

The three common styles:

- `[KEY-####] Title` — bracketed issue key, then a capitalized imperative title.
- `KEY-###: Description` — bare issue key, colon, then the description.
- Conventional Commits — `feat: ...`, `fix: ...`, `refactor: ...`, etc., optionally with a `(scope)`.

If the repo has no issue-key pattern anywhere, default to Conventional Commits for subjects and `<type>/<slug>` for branches, and ask whether an issue key should be tracked.

---

## The `(#N)` merge-number suffix — never author it

Some subjects show a trailing `(#N)`, for example:

```text
[PROJ-123] Add retry logic to the upload client (#142)
```

That `(#142)` is the platform's PR/MR number, appended automatically when a squash merge lands. It is NOT part of the commit message you write. Never type it by hand — author only the subject up to and including the title/description; the platform adds `(#N)` at merge.

---

## Style 1 — `[KEY-####] Title`

Bracketed key, single space, then a capitalized imperative title. No trailing period.

```bash
git commit -m "[PROJ-123] Add retry logic to the upload client"
```

---

## Style 2 — `KEY-###: Description`

Bare key, colon, single space, then the description.

```bash
git commit -m "PROJ-123: Add retry logic to the upload client"
```

---

## Style 3 — Conventional Commits

Type is one of `feat`, `fix`, `refactor`, `ci`, `docs`, `test`, `chore`, etc. No issue key in the subject.

```bash
git commit -m "feat: add retry logic to the upload client"
```

With an optional scope:

```bash
git commit -m "feat(upload): add retry logic to the upload client"
```

If the repo tracks an issue key alongside Conventional Commits, put it in the body or footer rather than the subject:

```bash
git commit -m "feat: add retry logic to the upload client" -m "Refs: PROJ-123"
```

---

## Branch naming grammar

Detect which form the repo uses from its history, then follow it. Both are auto-detected — never hardcode a choice.

```text
<type>/<KEY>-<n>-<slug>      # typed prefix
<KEY>-<n>-<slug>             # bare, no type prefix
```

- `<type>` is one of `feature`, `feat`, `fix`, `refactor`, `ci`.
- `<KEY>-<n>` is the full issue id, e.g. `PROJ-123`.
- `<slug>` is the ticket summary or change, lowercased, hyphenated, ASCII only, trimmed.

Inspect existing branch names to pick the form:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes
```

Example branches for each form:

```bash
git switch -c feature/PROJ-123-add-upload-retry-logic
git switch -c PROJ-123-add-upload-retry-logic
```

---

## Issue KEY detection order

Resolve the project key by walking these sources in order; the most-frequent prefix wins.

1. Repo docs — CLAUDE.md, agents.md, README.

1. Recent branch names:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

1. Recent commit subjects:

```bash
git log -50 --format=%s
```

If two keys compete for the top spot, or none is found, ask ONE question and record the resolved key to LEARNED.md.

---

## Labels and milestones — discover, never invent

Discover what the repo already defines, then apply only labels and milestones that already exist. Never create a taxonomy of your own. If a needed label or milestone does not exist, report it instead of creating it.

```bash
gh label list --repo {owner}/{repo}
gh api repos/{owner}/{repo}/milestones --jq '.[].title'
```

---

## Jira transition after the PR/MR is open

The review status the linked issue should transition to is instance-specific. Detect it from LEARNED.md or ask once, then record it — never assume a fixed string. Represent it as `<Review status>` until resolved.

The Jira site `<site>` comes from the CLI's auth status, never hardcoded:

```bash
jira me
```

Transition the issue to the recorded review status:

```bash
jira issue move PROJ-123 "<Review status>"
```

---

## Content boundaries

- Jira issue descriptions stay NON-TECHNICAL — no file paths, symbols, code, or internal ids. That detail belongs in the PR/MR body.
- Code comments must not name tickets, skills, or personas.
