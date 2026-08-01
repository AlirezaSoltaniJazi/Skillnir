# Create-Ticket Flow

> The full step-by-step "create a child under a selected Epic/Story" protocol for the jira skill — referenced from SKILL.md.

Build a new work item as a **child under a user-selected parent** (Epic or Story). The flow is read-only through step 6: nothing in Jira changes until the user confirms and you run `create` in step 7. The eight steps below mirror SKILL.md exactly.

---

## Step 1 — Detect the project KEY

Auto-detect from git context; never hardcode a key or a Jira domain. First hit wins; on ties the most-frequent prefix wins. If two keys compete or none is found, ask ONE question and record the answer to LEARNED.md.

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
git log -50 --format='%s' | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

Also run the read-only auth preflight once per session; it reports the authenticated **site** used to build every browse URL — never hardcode a domain:

```bash
acli jira auth status
```

---

## Step 2 — Ask the issue type

Ask which type unless it is obvious from the request: **Story / Task / Bug / Sub-task**. A "bug" report means `Bug`; a discrete unit of work means `Story` or `Task`; a `Sub-task` needs a Story parent, not an Epic.

---

## Step 3 — Search parents

Present candidate Epics and Stories the child can hang under. CSV is cleanest for scanning — the header is exactly `Type,Key,Status,Summary` (fixed by acli; parse by header name, not by the order passed to `--fields`):

```bash
acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --csv
```

Refine with `AND summary ~ "<term>"` when the user names the area. More JQL patterns: [jql-cookbook.md](jql-cookbook.md).

---

## Step 4 — User picks the parent

Show the results as a numbered list and wait for the user to choose. Hold the chosen parent key (e.g. `PROJ-123`) for the `--parent` flag.

```text
Which parent should this go under?
  1. PROJ-123  (Epic)   Reporting dashboard
  2. PROJ-118  (Story)  Bulk export
  3. PROJ-104  (Epic)   Notification preferences
```

---

## Step 5 — Gather summary + non-technical description

Collect a short **summary** and a **non-technical description**. Jira descriptions are read by PMs, QA, and other non-engineers: no file paths, function/class/method names, variable names, code snippets, or internal identifiers — that detail belongs in the PR/MR the ticket links to. Describe the user-visible problem, repro steps, and expected vs actual behaviour in plain language.

For short text use `--description`. For multi-line text write a file and use `--description-file <file>` (or `--editor`).

---

## Step 6 — CONFIRM all fields

Echo every field back and wait for an explicit yes. Never mutate Jira before this step. Example confirmation prompt (parent `PROJ-123`):

```text
About to create this Jira work item — confirm before I create it:

  Project:      PROJ
  Type:         Story
  Parent:       PROJ-123  (Epic — Reporting dashboard)
  Summary:      A long note cannot be saved
  Description:  When a user writes a long note, saving it silently fails and the
                text is lost. Steps: open an item, type a note longer than the
                visible area, press Save. Expected: the note is saved. Actual:
                the note disappears with no error.
  Assignee:     @me

Create it? (y/n)
```

If the user changes any field, re-echo the full block and confirm again.

---

## Step 7 — Create

On confirmation, run the exact create command with `--json` so you can read the new key back:

```bash
acli jira workitem create --project <KEY> --type Story --parent <PARENT> --summary "..." --description "non-technical text" --assignee @me --json
```

Filled in for the example above (parent `PROJ-123`):

```bash
acli jira workitem create --project PROJ --type Story --parent PROJ-123 --summary "A long note cannot be saved" --description "When a user writes a long note, saving it silently fails and the text is lost. Steps: open an item, type a long note, press Save. Expected: the note is saved. Actual: the note disappears with no error." --assignee @me --json
```

**Capture the new key** from the `key` field of the returned JSON — that value (e.g. `PROJ-457`) becomes the session active ticket:

```bash
acli jira workitem create --project PROJ --type Story --parent PROJ-123 --summary "..." --description "..." --assignee @me --json | jq -r '.key'
```

**If `--parent` is rejected** on a company-managed project, use the fallback ladder from [acli-recipes.md](acli-recipes.md): create WITHOUT `--parent`, then link the new child to the parent:

```bash
acli jira workitem link create --out <PARENT> --in <CHILD> --type "Parent of"
```

Record whichever approach worked to LEARNED.md under `## Discovered Conventions` so it is tried first next time.

---

## Step 8 — Report + record active ticket

Report the new key and its browse URL, building the URL from the `<site>` reported by `acli jira auth status` — never hardcode a domain:

```text
Created PROJ-457 — A long note cannot be saved
<site>/browse/PROJ-457
```

Then hold it as the session active ticket (below).

---

## Session active ticket (recap)

- **Context only** — the active ticket lives in your working conversation context. No file, no LEARNED.md entry; it is gone at session end, by design.
- **State and hold** after creating, viewing, or resolving a ticket: `Active ticket: PROJ-457 — <summary>`.
- **Reuse it** on later Jira or PR/MR requests in the same session — restate `Using active ticket PROJ-457` before any mutation instead of re-asking. The [github](../../github/SKILL.md) and [gitlab](../../gitlab/SKILL.md) skills read this same active ticket from context when raising a PR/MR.
- **Ask before creating a new one** while a ticket is active: `You have active ticket PROJ-457. Create a new one instead of using it? (y/n)`. Apply the same guard before replacing the active pointer.
