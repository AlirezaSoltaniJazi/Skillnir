# acli Command Cookbook

> Complete `acli jira` recipe reference for the jira skill — auth, search, create, view, transition, comment, edit, link, and the parent-child capability + fallback ladder. Referenced from SKILL.md. Every site/status/key value is auto-detected at runtime or asked and recorded to LEARNED.md — nothing instance-specific is baked in.

The verified command tree:

```
acli jira {auth,board,dashboard,field,filter,project,sprint,workitem}
acli jira workitem {archive,assign,attachment,clone,comment,create,create-bulk,delete,edit,link,list-watchers,search,transition,unarchive,view,watcher}
```

---

## Auth preflight (read-only)

Always run this first. The SITE comes from here — NEVER hardcode a domain. Do not attempt any write operation until it reports an authenticated site.

```bash
acli jira auth status
```

It reports the active Site (`<site>`) and the authenticated account. Use the reported `<site>` for all subsequent work; treat it as the source of truth, not an assumption. If it does not show an authenticated site — or shows a different site than the work target — stop and surface the problem before any search, create, or transition.

---

## Search for a parent

Find the Epic or Story to hang new work under. Two output formats: CSV is the cleanest for scanning, JSON when you need to parse specific fields. `<KEY>` is the project key (e.g. `PROJ` — so keys look like `PROJ-123` or `ABC-42`).

### CSV (cleanest)

```bash
acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --csv
```

The CSV header is exactly:

```
Type,Key,Status,Summary
```

Note the column order (`Type,Key,Status,Summary`) is fixed by acli and does not follow the order passed to `--fields`. Parse by header name, not by position guessed from the flag.

### JSON

`--json` returns full REST issue objects. The jq-style paths into each element:

```
.[].key                    # the work item key, e.g. "PROJ-123"
.[].fields.summary         # summary text
.[].fields.issuetype.name  # "Epic" / "Story" / "Task" / "Sub-task"
.[].fields.status.name     # e.g. "In Progress"
```

```bash
acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --json
```

---

## Create a child under a parent

Create flags: `-p/--project`, `-t/--type`, `-s/--summary`, `-d/--description`, `--description-file`, `-a/--assignee` (`@me`), `-l/--label`, `--parent <parent key>`, `--json`, `--from-json`, `--generate-json`.

```bash
acli jira workitem create --project <KEY> --type Story --parent <PARENT> --summary "..." --description "non-technical text" --assignee @me --json
```

Capture `"key"` from the returned JSON and record it as the session's active ticket — every later `view`, `transition`, `comment`, `edit`, and `link` command targets that key.

`--description` takes plain text and is fine for short non-technical summaries. For anything multi-line, see [Multi-line descriptions](#multi-line-descriptions) below.

---

## View

```bash
acli jira workitem view <KEY> --fields "key,summary,status,assignee,description" --json
```

`<KEY>` is any issue key (e.g. `PROJ-123`).

---

## Transition

There is **no way to list valid transition statuses in acli** — the review-status name is instance-specific and is written here only as `"<Review status>"`, never assumed to be a fixed string. Detect it from LEARNED.md; if absent, ask once, then record it. Pass the detected name directly.

```bash
acli jira workitem transition --key <KEY> --status "<Review status>" --yes
```

`--yes` skips the interactive confirmation. If the status name is rejected, the project uses a different label — that is a workflow-naming mismatch, not a syntax error. Discover the correct name once, then record it in LEARNED.md so it is used first next time.

---

## Comment

```bash
acli jira workitem comment create --key <KEY> --body "..."
```

---

## Edit

```bash
acli jira workitem edit --key <KEY> --summary "..." --assignee "..." --labels "..."
```

---

## Link

Create a typed link between two existing work items. This is also the fallback path for establishing a parent relationship (see the ladder below).

```bash
acli jira workitem link create --out <PARENT> --in <CHILD> --type "Parent of"
```

`--out` is the source (parent) key, `--in` is the target (child) key. List the available link types on the site with:

```bash
acli jira workitem link type
```

---

## Parent-child: capability + fallback ladder

**The `--parent` caveat.** `--parent` on `create` works for Epic → Story/Task and Story → Sub-task. Do not be misled by `--generate-json`: it labels the `parentIssueId` field as "only if sub-task", which reflects legacy company-managed epic-link semantics. The CLI `--parent` flag is more general than that JSON hint suggests and is the right first choice for setting a parent.

**Fallback ladder** — use in order if `--parent` is rejected on a company-managed project:

1. Try `create` with `--parent` (the normal path):

   ```bash
   acli jira workitem create --project <KEY> --type Story --parent <PARENT> --summary "..." --assignee @me --json
   ```

2. If `--parent` is rejected, create **without** `--parent`, then attach the parent with a link. There is no universal "parent" link type — the default Jira Cloud set is `Relates`/`Duplicate`/`Blocks`/`Cloners`, and instances add their own on top (verified: this site's set has no parent/child-style type at all). List what actually exists before picking one:

   ```bash
   acli jira workitem create --project <KEY> --type Story --summary "..." --assignee @me --json
   acli jira workitem link type
   acli jira workitem link create --out <PARENT> --in <CHILD> --type "<a real type from the list above, e.g. Relates>"
   ```

   Note this rung is a traceability substitute only — a plain issue link does **not** set the real hierarchy `parent` field, so the child still won't satisfy `parent = <KEY>` JQL or show nested under the parent on boards/backlogs. If the site has no suitable link type either, treat `--parent` support as unavailable here and go straight to rung 3.

3. If that also fails, use `--from-json` with a full ADF body describing the parent relationship:

   ```bash
   acli jira workitem create --from-json <file.json>
   ```

Record whichever rung worked for the project in LEARNED.md so it is tried first next time and the ladder is skipped. Also record the detected `"<Review status>"` and `<site>` there once known.

---

## Multi-line descriptions

`--description` accepts plain text and is best for short, non-technical text. For multi-line content, pass a file or open the editor instead of trying to cram newlines into `--description`:

```bash
acli jira workitem create --project <KEY> --type Story --parent <PARENT> --summary "..." --description-file <file> --assignee @me --json
```

```bash
acli jira workitem create --project <KEY> --type Story --parent <PARENT> --summary "..." --editor --assignee @me --json
```

- `--description-file <file>` — read the description body from a file.
- `--editor` — open an editor to compose the description interactively.
