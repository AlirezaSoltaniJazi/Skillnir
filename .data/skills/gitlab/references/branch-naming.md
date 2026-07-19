# Branch Naming Grammar

> The branch-name grammar for the gitlab skill — typed vs bare form, slug rules, style + issue-KEY detection, the no-issue-key fallback, and the exact `git checkout -b` commands — referenced from SKILL.md. Everything instance-specific is auto-detected at runtime or asked and recorded to `LEARNED.md`; nothing is hardcoded.

---

## Grammar

Two shapes exist. A repository uses **one** of them consistently — detect which before branching (see Detect the style).

**Typed** — a `<type>/` prefix in front of the issue id:

```text
<type>/<KEY>-<n>-<slug>
```

**Bare** — no type prefix:

```text
<KEY>-<n>-<slug>
```

- `<type>` ∈ `feature` | `feat` | `fix` | `refactor` | `ci` — infer from the work; ask when ambiguous.
- `<KEY>` — the issue-tracker project key for the repo (**auto-detect, never hardcode** — see Detect the issue KEY).
- `<n>` — the ticket number. `<KEY>-<n>` is the full issue id, e.g. `PROJ-123`.
- `<slug>` — the ticket summary / change, transformed (see Slug rules).

---

## Slug rules

Build `<slug>` from the ticket **summary** (or a short phrase describing the change):

- **Lowercase** every character.
- **ASCII only** — transliterate or strip accents and non-ascii, drop emoji and symbols.
- **Hyphenate** — replace each run of spaces and punctuation with a single `-`.
- **Collapse** repeated hyphens to one.
- **Trim** leading and trailing hyphens.
- Keep it short and readable — a few meaningful words, not the whole sentence.

Example: summary `"Add CSV export to the user list"` → slug `add-csv-export`.

Optional helper (produces a slug from a summary string):

```bash
printf '%s' "Add CSV export to the user list" \
  | iconv -t ascii//TRANSLIT | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/-+/-/g; s/^-|-$//g'
```

---

## Detect the style

List existing local + remote branches, then classify:

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes
```

- **Typed** if names match `^(feature|feat|fix|refactor|ci)/` → use `<type>/<KEY>-<n>-<slug>`.
- **Bare** if names match `^[A-Z][A-Z0-9]+-[0-9]+-` with no type prefix → use `<KEY>-<n>-<slug>`.

If the history is empty or inconclusive, ask ONE question (typed vs bare) and record the answer to `LEARNED.md`.

---

## Detect the issue KEY

Never hardcode the key. Resolve it in this order and let the **most-frequent** prefix win:

1. **Repo docs** — check `CLAUDE.md`, `agents.md`, `README` for a stated project key.
2. **Recent branches:**

   ```bash
   git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
   ```

3. **Recent commits:**

   ```bash
   git log -50 --format=%s
   ```

   Read the commit subjects to spot the key pattern (common styles: `[KEY-####] Title`, `KEY-###: Description`, or Conventional Commits). A trailing `(#N)` on some subjects is the platform's MR/PR number added **at merge** — it is not part of the key and you never author it by hand.

If two keys compete, or none is found, ask ONE question and persist the answer to `LEARNED.md`.

---

## No issue key — fallback

If the repo has no issue-key pattern at all (no `<KEY>-<n>` in docs, branches, or commits), do not fabricate one. Use a **Conventional Commits** style with a typed, keyless branch:

```text
<type>/<slug>
```

```bash
git checkout -b feat/add-csv-export
```

Then ask whether an issue tracker/key applies, and record whatever is confirmed to `LEARNED.md`.

---

## Create the branch

**Typed repos:**

```bash
git checkout -b <type>/<KEY>-<n>-<slug>
```

```bash
git checkout -b feature/PROJ-123-add-csv-export
```

**Bare repos** — no type prefix:

```bash
git checkout -b <KEY>-<n>-<slug>
```

```bash
git checkout -b PROJ-123-add-csv-export
```
