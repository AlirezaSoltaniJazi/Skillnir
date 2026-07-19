# Labels and Milestones

> Generic discover-then-apply rules for attaching labels and milestones to a pull request with the GitHub CLI — referenced from SKILL.md.

The core rule: **discover what the repo already defines, then apply only the entries that already exist.** Never invent a taxonomy, never create a missing label or milestone, and never open a GitHub Project. Anything that does not already exist is skipped and reported so a human can decide whether to create it.

`{owner}/{repo}` auto-resolves from the current repository — never hardcode an org or repo. Preflight `gh auth status` and read the token scopes: if there is **no `project` scope**, never pass `-p`/`--project` anywhere.

```bash
gh auth status
```

---

## Discover

Run both discovery commands before touching the PR. Treat their output as the only allowed set of values.

List every label the repo defines (name + description, so you can match by meaning, not by guessing). Raise `--limit` if the repo has many:

```bash
gh label list --json name,description --limit 100
```

List every milestone title the repo defines (there is no dedicated `gh` milestone command — go through the API; placeholders auto-resolve):

```bash
gh api "repos/{owner}/{repo}/milestones" --jq '.[].title'
```

---

## Match generically

Map the change to existing entries by category, using whatever the repo happens to define — do **not** assume any particular set of names. Common categories:

- **Type** — the nature of the change (a bug/fix category, a feature/enhancement category, a docs category, a chore/refactor category). Pick the existing label whose description matches the change.
- **Component / area** — the part of the codebase touched (a module, a subsystem, a surface). Pick an existing area label only if one clearly fits the diff. Label form varies per repo — a bare name or a prefixed one (`area: <x>`). Apply the discovered form verbatim; do not invent a prefix.
- **Version / release** — the milestone that groups the work. Pick an existing milestone title; if none applies, attach none.
- **Any other repo-defined axis** — status, priority, size, etc. Apply only when an existing label unambiguously fits.

If the repo defines nothing in a category, that category simply gets no label. When in doubt, skip and report rather than force a near-match. Never apply two competing type labels.

---

## Apply — labels

Attach only labels returned by `gh label list`. `--add-label` is repeatable; pass each existing label separately.

On create (each label repeated, milestone once — every value must already appear in the discovery output):

```bash
gh pr create \
  --base <default> \
  --head <branch> \
  --title "[<KEY>-<n>] Short desc" \
  --body-file - \
  --label "<existing-type-label>" \
  --label "<existing-component-label>" \
  --milestone "<existing-milestone-title>" <<'EOF'
## Ticket
<site>/browse/<KEY>-<n>
## Summary
- <generated from the diff>
EOF
```

After create, on an existing PR (`<n>` = PR number):

```bash
gh pr edit <n> \
  --add-label "<existing-type-label>" \
  --add-label "<existing-component-label>"
```

---

## Apply — milestones

There is no `gh milestone` create/attach command; use `gh pr edit`. The milestone **must pre-exist** in the discovery output:

```bash
gh pr edit <n> --milestone "<existing-milestone-title>"
```

---

## Skip and report

For every intended label or milestone that is **not** in the discovery output, do not create it. `gh` errors on a label or milestone that does not exist, so a missing one must never be part of an apply command. Collect the misses and report them verbatim, for example:

```text
Applied labels:      <type-label>, <component-label>
Applied milestone:   <milestone-title>
Not applied (absent in repo — create manually if wanted):
  - label:     "<requested-but-missing-label>"
  - milestone: "<requested-but-missing-milestone>"
```

Reasons an entry is skipped: it is missing from `gh label list` / the milestones API, or applying it would require the `project` scope the token lacks (no GitHub Projects without it).

---

## Read back

Confirm what actually landed on the PR:

```bash
gh pr view <n> --json url,number,title,labels,milestone
```
