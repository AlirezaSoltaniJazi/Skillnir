# glab Command Cookbook — Merge Requests

> The GitLab CLI (`glab`) recipe reference for the gitlab skill, referenced from SKILL.md: how to preflight auth, detect the target branch, build and create a Merge Request, read it back, apply labels and milestones, update it, and sync the linked Jira ticket.

> [!IMPORTANT]
> `glab` was **NOT** available to verify live in this environment. Every flag below is the _typical_ surface, not a confirmed one. On first use in any repository you MUST run `glab mr create --help` (and the `--help` of each subcommand you touch) and confirm the exact flag names and behavior. Record any differences — renamed flags, missing options, different JSON field names — to `LEARNED.md` so the next session does not repeat the guesswork. GitLab uses **Merge Request (MR)**, never "Pull Request" — keep that terminology everywhere.

All standard `glab` commands **auto-resolve the project** from the current repository's git remote. You only need `-R/--repo {owner}/{repo}` when operating outside a checked-out clone.

---

## Auth preflight

Confirm you are authenticated before doing anything else. If `glab` is not installed, install the GitLab CLI first, then log in.

```bash
glab auth status
```

If the binary is missing (`command not found: glab`), install the GitLab CLI for your platform, then authenticate:

```bash
glab auth login
```

`glab auth login` walks through host selection (gitlab.com or a self-managed instance) and token entry. Re-run `glab auth status` afterward to confirm the account and host resolved. Confirm the real login flags with `glab auth login --help` and record anything that differs to `LEARNED.md`.

---

## Detect the target branch

The MR's target is the repository's default branch. Resolve it from the git remote HEAD:

```bash
git symbolic-ref refs/remotes/origin/HEAD | sed 's@.*/@@'
```

If `origin/HEAD` is not set locally (fresh clone, detached remote), fall back to the CLI:

```bash
glab repo view
```

Read the default branch from that output. Whatever value you resolve is `<target>` for the diff summary and the `--target-branch` flag below. Do not assume a fixed name — detect it.

---

## Build the MR description from the diff + template

`glab` has **no `--body-file`** flag. Compose the description text in a file, then pass it inline with command substitution, or let `--fill` derive it from your commits.

First, gather a concrete summary of what the branch changes against the resolved `<target>`:

```bash
git diff <target>...HEAD --stat
git log <target>..HEAD --format='%s'
```

Fold the `--stat` output and the commit-subject list into your MR description body file (`<body-file>`), following whatever MR template the project uses. Then supply it to `glab` one of two ways:

```bash
# Option A — full control: render a body file and inline it
glab mr create --title "<title>" --description "$(cat <body-file>)" --source-branch "<source>" --target-branch "<target>"
```

```bash
# Option B — let glab derive title + description from commits
glab mr create --fill --source-branch "<source>" --target-branch "<target>"
```

Use Option A when you want a templated, reviewed description; use Option B (`-f/--fill`) for quick MRs where the commit history already reads well.

---

## Create the MR

Full create with the typical flag surface. Confirm each flag with `glab mr create --help` before relying on it.

```bash
glab mr create \
  --title "<title>" \
  --description "$(cat <body-file>)" \
  --source-branch "<source>" \
  --target-branch "<target>" \
  --label "<label>" \
  --milestone "<milestone>" \
  --assignee "<assignee>" \
  --reviewer "<reviewer>" \
  --yes
```

Typical flags (short / long) and their meaning:

- `-t, --title` — MR title.
- `-d, --description` — MR description text (use `"$(cat <body-file>)"` since there is no `--body-file`).
- `-s, --source-branch` — the branch you are merging _from_.
- `-b, --target-branch` — the branch you are merging _into_ (the `<target>` you detected).
- `-l, --label` — apply a label (repeat for multiple; must already exist — see Labels).
- `-m, --milestone` — assign a milestone.
- `-a, --assignee` — assign the MR.
- `--reviewer` — request a reviewer.
- `--draft` — open the MR as a draft.
- `-f, --fill` — populate title + description from commit messages.
- `-y, --yes` — skip the interactive confirmation prompt.
- `-R, --repo` — target a different `{owner}/{repo}` than the current clone.
- `--remove-source-branch` — delete the source branch after merge.
- `--squash-before-merge` — squash commits on merge.
- `--web` — open the created MR in a browser.

---

## Read back the URL

After creating, fetch the MR as JSON to capture its web URL and IID for follow-up commands and for linking back to the Jira ticket:

```bash
glab mr view <id> --output json
```

Read the `url`, `iid`, and `title` fields from the JSON. `<id>` is the MR IID (or omit it while on the source branch to resolve the current branch's MR — confirm this shortcut with `glab mr view --help`). Persist the `url` — you will paste it into the Jira comment below.

---

## Labels — discover, then apply only existing

MR labels must already exist in the project; `glab mr create --label` does not create them. List first, then apply only labels that appear in that list.

```bash
glab label list
```

Match your intended labels against the output. Apply the ones that exist at create time (`--label`) or afterward via update:

```bash
glab mr update <id> --label "<existing-label>"
```

If a label you want is absent, do **not** invent it silently — either pick an existing one or ask, and record the project's label taxonomy to `LEARNED.md`.

---

## Milestones

`glab` has no dedicated `milestone list` subcommand in the typical surface — query the API directly. `:id` auto-resolves to the current project:

```bash
glab api "projects/:id/milestones"
```

Read the milestone `title` (or `id`) from the JSON array, then attach it at create time (`--milestone`) or on update:

```bash
glab mr update <id> --milestone "<milestone-title>"
```

---

## Update the MR

Change title, description, labels, milestone, assignee, reviewer, or draft state after creation:

```bash
glab mr update <id> --label "<label>" --milestone "<milestone>"
```

`glab mr update` accepts the same descriptive flags as create (confirm with `glab mr update --help`). To replace the description from an edited body file, reuse inline substitution:

```bash
glab mr update <id> --description "$(cat <body-file>)"
```

---

## Update the linked Jira ticket

Once the MR exists and you have its URL, sync the tracking ticket via the Atlassian CLI (`acli`). The Jira **site** is whatever `acli jira auth status` reports — never hardcode a domain. The review-status name is **instance-specific**: detect it from `LEARNED.md`, or ask, then record it; never assume a fixed string.

Auth preflight (read-only — reports the site `<site>` and account):

```bash
acli jira auth status
```

Comment the MR link onto the work item. Replace `<KEY>` with the real issue key (for example `PROJ-123` or `ABC-42`) and paste the MR `url` you read back above:

```bash
acli jira workitem comment create --key <KEY> --body "Merge Request opened: <mr-url>"
```

Transition the ticket into the review column. `acli` **cannot** list valid statuses, so `"<Review status>"` is a placeholder for the instance's actual review-column name — pull it from `LEARNED.md` or ask, then record what worked:

```bash
acli jira workitem transition --key <KEY> --status "<Review status>" --yes
```

If the transition is rejected because the status name is wrong, view the ticket to reason about its workflow, fix the status name, retry, and write the confirmed name to `LEARNED.md`:

```bash
acli jira workitem view <KEY> --fields "key,summary,status,assignee,description" --json
```
