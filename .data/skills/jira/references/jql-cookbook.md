# JQL Cookbook

> Ready-to-run JQL snippets and full `acli jira workitem search` commands for the jira skill — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

Every snippet below is a `--jql` value for `acli jira workitem search`. Swap `<KEY>` for the real project key (e.g. `PROJ-123` lives in project `PROJ`) and `<KEY>-nnn` for a real work item key. Confirm auth first (read-only) — the site it reports is the target; never hardcode a domain:

```bash
acli jira auth status
# ✓ Authenticated / Site: <site>
```

---

## Output shape

CSV is the cleanest surface for parsing — the header row is exactly `Type,Key,Status,Summary`, and its column order is fixed by acli regardless of what you pass to `--fields`:

```bash
acli jira workitem search --jql "<JQL>" --limit 30 --fields "key,summary,issuetype,status" --csv
```

`--json` instead returns full REST issue objects; pull fields from `.[].key`, `.[].fields.summary`, `.[].fields.issuetype.name`, `.[].fields.status.name`.

---

## Open Epics/Stories to pick a parent

Everything not yet Done, most recently touched first — use this to choose a parent before `create --parent`:

```jql
project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC
```

---

## Refine by summary

Narrow the parent list by a search term (`~` is the JQL contains/text-match operator):

```jql
project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done AND summary ~ "term" ORDER BY updated DESC
```

---

## My open issues

Assigned to the authenticated user and still active:

```jql
assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC
```

Scope it to one project by prefixing `project = <KEY> AND`.

---

## Issues under a given parent

Direct children of a specific Epic or Story — substitute the real key you picked above:

```jql
parent = <KEY>-nnn ORDER BY created ASC
```

---

## Recently updated

Anything touched in the project within the last 7 days:

```jql
project = <KEY> AND updated >= -7d ORDER BY updated DESC
```

---

## By status

Filter by an exact status name (quote names that contain spaces). The review-status label is instance-specific — detect it from LEARNED.md or ask, then record it; never assume a fixed string:

```jql
project = <KEY> AND status = "<Review status>" ORDER BY updated DESC
```

By status category instead of a single named status:

```jql
project = <KEY> AND statusCategory = "In Progress" ORDER BY updated DESC
```

---

## Full search commands

Open Epics/Stories to pick a parent, CSV out (`Type,Key,Status,Summary`):

```bash
acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --csv
```

Same list refined by a summary term, CSV out:

```bash
acli jira workitem search --jql "project = <KEY> AND issuetype in (Epic, Story) AND statusCategory != Done AND summary ~ \"term\" ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --csv
```

My open issues, JSON out for scripted field extraction:

```bash
acli jira workitem search --jql "assignee = currentUser() AND statusCategory != Done ORDER BY updated DESC" --limit 30 --fields "key,summary,issuetype,status" --json
```

Children of a chosen parent, CSV out:

```bash
acli jira workitem search --jql "parent = <KEY>-nnn ORDER BY created ASC" --limit 30 --fields "key,summary,issuetype,status" --csv
```
