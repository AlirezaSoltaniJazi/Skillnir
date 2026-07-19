# PR Recipes — gh Command Cookbook

> The complete `gh` (and `acli`) command cookbook for raising a pull request and updating its linked Jira ticket — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean. Everything instance-specific (branch, base, keys, site, review status) is auto-detected at runtime or asked and recorded to LEARNED.md — never baked in.

---

## Auth preflight

Confirm `gh` is authenticated and inspect the token scopes before doing anything else. `gh` auto-resolves `{owner}/{repo}` from the current repo, so never hardcode an org.

```bash
gh auth status
```

Read the scope list from the output. **If `project` is not among the scopes, never pass `-p`/`--project` to any `gh` command** — it will fail on the missing scope. Skip all project-board wiring in that case.

Preflight `acli` too (read-only) — it reports the Jira site to use downstream:

```bash
acli jira auth status
```

Use whatever `Site` (`<site>`) and account it reports. Never hardcode a Jira domain.

---

## Detect the base branch

Ask the repo for its default branch rather than assuming `main` vs `master`.

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

Capture the result and reuse it as `<base>` in every command below.

---

## Build the PR body from the diff + template

Assemble the body from a short diff summary plus the commit subjects on the branch, computed against the detected base.

```bash
git diff <base>...HEAD --stat
git log <base>..HEAD --format='%s'
```

Use the `--stat` output as a "Changed files" block and the commit subjects as bullet points under a summary heading. Feed the assembled body to `gh pr create` on stdin via `--body-file -` and a heredoc — no temp file needed.

The branch and title follow this grammar (placeholders, not fixed strings): branch `<type>/<KEY>-<slug>`, title `[<KEY>] <short description>`, where `<KEY>` is the Jira project key + number (e.g. `PROJ-123` or `ABC-42`).

---

## Create the PR

Body supplied on stdin through a heredoc. `--body-file -` reads the heredoc; every flag below is verified present on `gh pr create`.

```bash
gh pr create \
  --base <base> \
  --head <type>/<KEY>-<slug> \
  --title "[PROJ-123] Short description" \
  --body-file - <<'EOF'
## Ticket
<site>/browse/PROJ-123
## Summary
- <generated from the diff>
EOF
```

No-template fallback — let `gh` fill the title and body from the branch commits:

```bash
gh pr create --base <base> --fill
```

Flag reference (all verified on `gh pr create`):

- `-t`/`--title`, `-b`/`--body`, `-F`/`--body-file` (`-` = stdin)
- `-B`/`--base`, `-H`/`--head`
- `-l`/`--label`, `-m`/`--milestone`, `-a`/`--assignee`, `-r`/`--reviewer`
- `-d`/`--draft`, `-T`/`--template <file>`
- `-f`/`--fill` (title + body from commits), `--fill-first`, `--fill-verbose`
- `--dry-run`, `-R`/`--repo`

Notes:

- `--title`/`--body` override `--fill` when both are present.
- **Never** use `-p`/`--project` — it needs the `project` scope, which the preflight showed is absent.

---

## Read back the URL

After creation, read the canonical URL (and number/title) back as JSON.

```bash
gh pr view <n> --json url,number,title
```

`<n>` may be the PR number or the branch; when run right after create on the same branch you can omit it.

---

## Labels

Discover what labels the repo actually defines, then apply only those that exist — do not invent label names.

```bash
gh label list --json name,description --limit 100
```

Apply at create time with repeated `--label`:

```bash
gh pr create --base <base> --fill --label "<label-a>" --label "<label-b>"
```

Or after the fact on an existing PR (repeatable):

```bash
gh pr edit <n> --add-label "<label-a>" --add-label "<label-b>"
```

`gh` errors on a label that doesn't exist, which fails the whole command — so cross-check every value against the discovery output first, and skip-and-report anything the repo lacks rather than inventing it.

---

## Milestones

There is no dedicated `gh` milestone command — go through `gh api`, whose `{owner}`/`{repo}` placeholders auto-resolve from the current repo. The milestone must **already exist**; `gh` will not create one.

List existing milestones:

```bash
gh api "repos/{owner}/{repo}/milestones" --jq '.[].title'
```

Attach an existing milestone to the PR:

```bash
gh pr edit <n> --milestone "<milestone>"
```

If the intended milestone is not in the list, skip and report it — a maintainer must create it in the GitHub UI first.

---

## Dry-run

Preview without opening the PR. `--dry-run` prints what would be created instead of creating it.

```bash
gh pr create --base <base> --fill --dry-run
```

Caveat: `--dry-run` may still push the current branch to the remote as part of its setup — it only guarantees that no PR is opened, not that nothing touches the remote.

---

## Update the linked Jira ticket

Once the PR is up, comment the PR URL onto the ticket and move it to the review state. The site (`<site>`) and account come from `acli jira auth status` — never hardcode them.

Comment the PR URL onto the ticket:

```bash
acli jira workitem comment create --key <KEY> --body "PR raised: <url>"
```

Transition the ticket to the review state. `acli` **cannot** list valid statuses, and the review-status name is instance-specific, so the exact string is not assumed here — detect it from LEARNED.md, or ask once and record it there. `--yes` skips the confirmation prompt:

```bash
acli jira workitem transition --key <KEY> --status "<Review status>" --yes
```

If the transition is rejected because the status name is wrong, ask for the correct review-status label for this instance, run the command with it, and write the confirmed value to LEARNED.md as `YYYY-MM-DD: review status for <site> is "<Review status>"` so future runs use it directly.
