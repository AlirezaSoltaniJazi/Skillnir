# Commit Subject Conventions

> Commit-message reference for the gitlab skill, referenced from SKILL.md: how to detect the repo's commit-subject style from git history, the three common styles (`[KEY-####] Title` vs `KEY-###: Description` vs Conventional Commits), how to find the issue KEY, why the trailing `(#N)` merge number is never hand-authored, and the exact `git commit -m` command for each style.

The commit-subject format is a per-repo convention — **detect it, never hardcode it**. Everything below is auto-detected at runtime from git history and repo docs, or asked once and recorded to `LEARNED.md`. Placeholders: `<KEY>` is the project's issue-key prefix and `<n>` the number, so `<KEY>-<n>` is a full issue id (examples: `PROJ-123`, `ABC-42`).

---

## Detect the repo's commit style first

Read the last 50 subjects and match them against the three known shapes. Whichever pattern the majority of real (non-merge) commits follow is the style you adopt:

```bash
git log -50 --format=%s
```

Classify the output with a grep per style — the one that matches the most lines wins:

```bash
# Style A — bracketed key + Title Case:  [KEY-####] Title
git log -50 --format=%s | grep -cE '^\[[A-Z][A-Z0-9]+-[0-9]+\] '

# Style B — key + colon + description:   KEY-###: Description
git log -50 --format=%s | grep -cE '^[A-Z][A-Z0-9]+-[0-9]+: '

# Style C — Conventional Commits:        type: subject
git log -50 --format=%s | grep -cE '^(feat|fix|refactor|ci|docs|chore|test|build|perf|style)(\(.+\))?!?: '
```

If a repo `CLAUDE.md`, `agents.md`, `README`, or `CONTRIBUTING` states the commit convention explicitly, that overrides the git-history vote. Record the confirmed style to `LEARNED.md` so the next session skips the detection.

---

## Style A — bracketed key + Title Case

Grammar: `[<KEY>-<n>] <Title>` — the issue id in square brackets, then a Title-Cased summary. Used by repos that want the tracker id to read first and stand out.

```bash
git commit -m "[PROJ-123] Add rate limiting to the public API"
```

---

## Style B — key + colon + description

Grammar: `<KEY>-<n>: <Description>` — the issue id, a colon, then a lowercase-leading description. Same information as Style A, different punctuation.

```bash
git commit -m "PROJ-123: add rate limiting to the public API"
```

---

## Style C — Conventional Commits

Grammar: `<type>(<scope>)!: <subject>` — a semantic `type` (`feat`, `fix`, `refactor`, `ci`, `docs`, `chore`, `test`, `build`, `perf`, `style`), an optional `scope` in parentheses, an optional `!` for a breaking change, then a colon and a lowercase subject. The issue key is **not** in the subject here; put it in a trailer line instead so the tracker still links.

```bash
git commit -m "feat: add rate limiting to the public API"
```

With a scope, a breaking-change marker, and an issue trailer (second `-m` becomes the body):

```bash
git commit -m "feat(api)!: add rate limiting to the public API" -m "Refs: PROJ-123"
```

---

## When no issue-key pattern exists

If `git log -50 --format=%s` shows no `<KEY>-<n>` prefix anywhere and the repo has no linked tracker, default to **Conventional Commits** for subjects and `<type>/<slug>` for branches — and **ask** the user once whether that is right before committing. Record the answer to `LEARNED.md`.

```bash
git commit -m "fix: correct off-by-one in pagination cursor"
```

---

## Detect the issue KEY

The `<KEY>` prefix (the letters before the number) is discovered in priority order; the **most-frequent** prefix wins. If two prefixes tie, or none is found, ask **one** question and record the answer to `LEARNED.md` — never guess.

1. **Repo docs** — read `CLAUDE.md`, `agents.md`, `README`, or `CONTRIBUTING` for a stated project key.
2. **Recent branches** — extract keys from branch names:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

3. **Recent commits** — extract keys from subjects:

```bash
git log -50 --format=%s | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

Count the prefixes across whichever source yields matches, take the majority, and reuse it for the branch, commit subject, and MR title so all three carry the same id.

---

## The `(#N)` merge-number suffix — never author it

Some repos show subjects ending in a bracketed number, for example `[PROJ-123] Add rate limiting (#4217)`. That trailing `(#N)` is the **platform's MR/PR number**, appended automatically by GitLab (or GitHub) at squash-merge time — it is **not** part of the hand-written subject. Never type it into a `git commit -m` yourself: at commit time the merge does not exist yet, so any number you invent is wrong and will collide with the real one the platform assigns on merge. Author only the `[<KEY>-<n>] <Title>` part; let the platform add the `(#N)`.

---

## Keep the subject clean

- One subject line, imperative or descriptive per the detected style — no ticket, skill, or persona names beyond the issue key the style itself carries.
- Put file paths, symbols, and internal ids in the commit **body** (a second `-m`) or the MR description, never in the linked tracker ticket.
- Match the detected style exactly (brackets vs colon vs `type:`); do not mix styles within one repo. When in doubt, re-run the detection above and record the outcome to `LEARNED.md`.
