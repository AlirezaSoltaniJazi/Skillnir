# Labels & Milestones — Discover, Then Apply Only What Exists

> The label and milestone handling reference for the gitlab skill, referenced from SKILL.md: how to discover the labels and milestones a repository already defines, apply only the matching ones to a Merge Request, and skip-and-report anything that does not exist — without ever inventing a taxonomy.

> [!IMPORTANT]
> `glab` was **NOT** available to verify live in this environment. The flag names below (`-l/--label`, `-m/--milestone`, and the `label list` / `milestone list` / `api` subcommands) are the _typical_ surface, not a confirmed one. On first use in any repository you MUST run `glab mr create --help`, `glab mr update --help`, `glab label list --help`, and `glab milestone list --help` and confirm the exact flag names and behavior. Record any differences — renamed flags, missing options, different JSON field names — to `LEARNED.md` so the next session does not repeat the guesswork.

**Core rule.** Labels and milestones must **already exist** in the project. `glab mr create` / `glab mr update` do **not** create them — they error on an unknown label or milestone. So the flow is always **discover first, then apply only the matches, then report the rest.** Never define a label taxonomy or a milestone scheme; only ever use what the repository has already set up.

All commands below **auto-resolve the project** from the current repository's git remote. You only need `-R/--repo {owner}/{repo}` when operating outside a checked-out clone.

---

## Discover the labels the project defines

List every label that exists in the project, then match your intended labels against that output. Only labels present in the list are eligible to apply.

```bash
glab label list
```

For a machine-readable list you can grep or diff against, request JSON (confirm the flag with `glab label list --help`):

```bash
glab label list --output json
```

Read the label `name` values from the output. An intended label that does **not** appear in this list is not applied — it is skipped and reported (see below). Do not create it, do not guess a near-match.

---

## Discover the milestones the project defines

Use the dedicated `glab milestone list` subcommand — it lists the current project's milestones by default:

```bash
glab milestone list --output json
```

If `milestone list` is missing on an older `glab` (confirm with `glab milestone --help`), fall back to the API directly — `:id` auto-resolves to the current project:

```bash
glab api "projects/:id/milestones"
```

Either way the response is a JSON array (or list); read each milestone's `title` (and `id` / `state` if you need to prefer active over closed milestones). Only a milestone whose `title` appears in this output is eligible to apply.

---

## Apply only existing labels / milestones — at create time

Attach the discovered, matching labels and milestone when you open the MR. Repeat `--label` for multiple labels. Every value here must have appeared in the discovery step above.

```bash
glab mr create \
  --source-branch "<source>" \
  --target-branch "<target>" \
  --title "<title>" \
  --description "$(cat <body-file>)" \
  --label "<existing-label>" \
  --milestone "<existing-milestone-title>" \
  --yes
```

Flags used here (confirm with `glab mr create --help`):

- `-l, --label` — apply a label that already exists; repeat for multiple.
- `-m, --milestone` — assign a milestone by its existing title.

If none of your intended labels/milestones exist, create the MR **without** those flags — an MR with no labels is fine; a failed create because of an unknown label is not.

---

## Apply only existing labels / milestones — after creation

To add or change labels and the milestone on an MR that already exists, update it. `<id>` is the MR IID (or omit while on the source branch to resolve the current branch's MR — confirm with `glab mr update --help`).

```bash
glab mr update <id> --label "<existing-label>" --milestone "<existing-milestone-title>"
```

Labels and milestone can be updated independently — pass only the flag you need:

```bash
glab mr update <id> --label "<existing-label>"
```

```bash
glab mr update <id> --milestone "<existing-milestone-title>"
```

`glab mr update` accepts the same descriptive flags as create; verify the exact set with `glab mr update --help` and record any differences to `LEARNED.md`.

---

## Skip and report anything that does not exist

When an intended label or milestone is absent from the discovery lists, do **not** invent it and do **not** silently drop it. Apply the subset that exists, then tell the user plainly which ones were skipped and why. A useful report names both what was applied and what was not:

```text
Applied labels: <existing-label-a>, <existing-label-b>
Skipped (not defined in this project): <missing-label-c>, <missing-milestone-x>
Milestone applied: <existing-milestone-title>
```

Then either pick an existing alternative, or ask the user **one** question (use it, don't create it, or create it deliberately outside this skill), and record the outcome to `LEARNED.md` so the next session knows this repo's available labels/milestones. Persisting the discovered set under `## Discovered Conventions` (format: `- YYYY-MM-DD: rule description`) lets a later run match against it without re-listing.

---

## Why discover-first, never a taxonomy

- **Unknown values error the command.** `glab mr create --label` / `--milestone` reject a value the project has not defined — the whole create can fail on one bad label.
- **Every repo's set is different.** Labels and milestones are project-specific; a taxonomy baked into this skill would be wrong somewhere. Detect the repo's actual set at runtime.
- **Creating labels is a deliberate act, not a side effect.** Inventing a label to make a command succeed pollutes the project's label list. Skip-and-report keeps the project's taxonomy owned by the project, not by this skill.
