# Branch Naming

> Generic branch-name grammar, repo-style detection, slug rules, the no-issue-key fallback, and the exact `git checkout -b` commands for the github skill — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

---

## Grammar

Two accepted forms. Pick the one the repo already uses — never mix them. `<KEY>-<n>` is the full issue id (project key plus number, e.g. `PROJ-123`); `<slug>` is the ticket summary or change, slugified.

```bash
# Typed form — a type prefix, then the issue id, then the slug:
<type>/<KEY>-<n>-<slug>       # type in {feature, feat, fix, refactor, ci}

# Bare form — issue id then slug, no type prefix:
<KEY>-<n>-<slug>
```

- `<type>` — one of `feature`, `feat`, `fix`, `refactor`, `ci` only. Infer from the work; ask when ambiguous.
- `<KEY>` — the issue-tracker project key for the repo. Auto-detect, never hardcode.
- `<n>` — the ticket number. `<KEY>-<n>` is the full id, e.g. `PROJ-123`.
- `<slug>` — the ticket summary or change, transformed (see Slug rules).

---

## Detect which form the repo uses

Read existing branch names (local plus remote), newest first, then classify.

```bash
# All recent branch names, newest first:
git for-each-ref --sort=-committerdate --format='%(refname:short)' refs/heads refs/remotes
```

Count how many branches match each form and let the majority decide.

```bash
# Typed form: <type>/<KEY>-<n>- ...
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes \
  | grep -oE '^(origin/)?(feature|feat|fix|refactor|ci)/[A-Z][A-Z0-9]+-[0-9]+-' \
  | wc -l

# Bare form: <KEY>-<n>- ... (no type prefix)
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes \
  | grep -oE '^(origin/)?[A-Z][A-Z0-9]+-[0-9]+-' \
  | wc -l
```

Whichever count is higher is the repo's form. If both are zero, or the counts tie, ask ONE question about the branch convention and record the answer to LEARNED.md.

Auto-detect the `<KEY>` from the same branch list (most-frequent prefix wins):

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes \
  | grep -oE '[A-Z][A-Z0-9]+-[0-9]+' \
  | sed -E 's/-[0-9]+$//' | sort | uniq -c | sort -rn
```

If branches are inconclusive, fall back to recent commits (`git log -50 --format=%s | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'`). If two keys compete, ask ONE question and persist the answer to LEARNED.md.

---

## Slug rules

Build `<slug>` from the ticket summary or the change being made:

- **Lowercase** every character.
- **ASCII only** — transliterate or strip accents and non-ASCII (drop emoji and symbols).
- **Hyphenate** — replace each run of spaces and punctuation with a single `-`.
- **Collapse** repeated hyphens to one.
- **Trim** leading and trailing hyphens.
- Keep it short and readable — a few meaningful words, not the whole sentence.

Optional helper (produces a slug from a summary string):

```bash
printf '%s' "Add retry logic to upload client" \
  | iconv -t ascii//TRANSLIT | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/-+/-/g; s/^-|-$//g'
# -> add-retry-logic-to-upload-client
```

---

## No-issue-key fallback

When no `<KEY>-<n>` can be detected (no tracker key in repo docs, branches, or commits), use a typed, key-less branch and ask which issue or tracker it belongs to. Record the answer to LEARNED.md so the next branch is fully qualified.

```bash
# <type>/<slug> — no issue id available yet:
git checkout -b fix/retry-logic-on-upload-client
```

---

## Create the branch

Placeholder issue id `PROJ-123`, example slug `add-retry-logic-to-upload-client`. Substitute the real detected `<KEY>-<n>`, `<type>`, and `<slug>`.

**Typed form:**

```bash
git checkout -b <type>/<KEY>-<n>-<slug>
```

```bash
git checkout -b feat/PROJ-123-add-retry-logic-to-upload-client
```

**Bare form** — no type prefix:

```bash
git checkout -b <KEY>-<n>-<slug>
```

```bash
git checkout -b PROJ-123-add-retry-logic-to-upload-client
```
