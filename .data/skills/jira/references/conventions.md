# Jira Conventions & Detection

> Generic Jira naming, linking, and detection rules for the jira skill — referenced from SKILL.md. Everything instance-specific is auto-detected at runtime or asked once and recorded to LEARNED.md; nothing is hardcoded.

---

## Site resolution

The Jira site is never hardcoded. Read it from the CLI's authenticated session every time you need it:

```bash
acli jira auth status
```

Use the site reported there as `<site>` for all URL construction. If the command shows no authenticated session, ask the user to authenticate rather than guessing a domain. Do not cache a domain across repos — different repos may target different sites.

---

## Issue URL pattern

Build issue links from the resolved site and the full issue id `<KEY>-<n>`:

```
<site>/browse/<KEY>-<n>
```

Example shape only (placeholder key): `<site>/browse/PROJ-123`. The `<KEY>-<n>` segment is the complete issue id — project key plus number, e.g. `PROJ-123` or `ABC-42`.

---

## Issue KEY auto-detection ladder

Never assume the project key. Walk this ladder in order and stop at the first confident answer:

1. Repo docs — check `CLAUDE.md`, `agents.md`, and `README` for a stated project key or ticket-link convention.

2. Recent branches — extract key candidates from local and remote branch names:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

3. Recent commits — extract key candidates from subjects:

```bash
git log -50 --format=%s
```

The most-frequent key prefix across these signals wins. If two prefixes compete, or none is found, ask ONE question to confirm the key and record the answer to LEARNED.md so later sessions skip the ladder.

---

## Branch naming

Auto-detect which of these two grammars the repo already uses from its branch history; do not impose one.

```
<type>/<KEY>-<n>-<slug>      # type-prefixed
<KEY>-<n>-<slug>             # bare, no type prefix
```

- `<type>` is one of `feature`, `feat`, `fix`, `refactor`, `ci`.
- `<KEY>-<n>` is the full issue id (e.g. `PROJ-123`).
- `<slug>` is the ticket summary or change, lowercased, hyphen-separated, ASCII-only, trimmed of leading/trailing hyphens.

Inspect existing branches to decide type-prefixed vs. bare:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes
```

If the history is ambiguous, ask ONE question and record the chosen grammar to LEARNED.md.

---

## Commit subjects

Detect the repo's commit style from its recent history — do not assume:

```bash
git log -50 --format=%s
```

Common styles to match against:

```
[KEY-####] Title          # bracketed key prefix
KEY-###: Description       # key-colon prefix
feat: ... / fix: ...       # Conventional Commits
```

Follow whichever style dominates the last 50 subjects. If no issue-key pattern exists at all, default to Conventional Commits for subjects and `<type>/<slug>` for branches, and ask the user once to confirm before committing.

The `(#N)` suffix that some repos show at the end of a merged subject is the platform's PR/MR number, added automatically at merge time. Never author it by hand.

---

## Labels & milestones

Discover what the repo and issue tracker already define, then apply only the ones that already exist. Never invent a taxonomy.

- Match the requested label/milestone against the existing set.
- Apply only exact matches.
- If a requested label or milestone does not exist, report that it is missing instead of creating it.

---

## Review status transition

The Jira status used to mark an issue as ready for review — written here as `<Review status>` — is instance-specific and is never assumed to be a fixed string.

1. Check LEARNED.md for a previously recorded `<Review status>`.
2. If absent, detect it from the issue's available transitions, or ask the user which status name to use.
3. Record the confirmed value to LEARNED.md so future transitions reuse it.

Do not hardcode a status name in the skill or in code.

---

## Descriptions stay NON-TECHNICAL

Jira ticket descriptions describe the change in product/behaviour terms for a non-technical reader. They must not contain file paths, code symbols, code snippets, internal ids, or tool/persona names — that level of detail belongs in the PR/MR, not the ticket. Code comments must likewise never name tickets, skills, or personas.

Good (PROJ-123 description):

```
Users can now reset their password from the sign-in screen. A reset link
is emailed and expires after one hour. Errors show a clear retry message.
```

Bad (PROJ-123 description):

```
Fixed null deref in auth/reset_handler.py::send_link(); token TTL now
3600s via RESET_TTL const. See jira skill / backendEngineer persona.
```

The bad example leaks file paths, a symbol, a constant, an internal ttl value, and skill/persona names — move all of that into the PR/MR body.

---

## Recording detections

Any value that had to be asked or resolved at runtime — project key, branch grammar, commit style, `<Review status>` — is written back to LEARNED.md with a dated rule line so subsequent sessions detect it from memory instead of re-asking.
