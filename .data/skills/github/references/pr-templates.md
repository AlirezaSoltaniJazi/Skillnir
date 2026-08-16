# Finding & Filling a GitHub PR Template

> How the github skill locates a repository's pull-request template, fills it (ticket URL + a Summary generated from the diff, checklists preserved), and falls back to `--fill` when none exists — referenced from SKILL.md. Full detail lives here so SKILL.md stays lean.

Everything instance-specific below is **auto-detected at runtime or asked once and recorded to LEARNED.md** — never hardcode a key, host, org, branch style, or status string.

---

## Preflight — auth + token scopes

Confirm `gh` is authenticated and read the token scopes before anything else. The Jira `<site>` shown in later commands comes from the CLI's own auth status, never from a baked-in value.

```bash
gh auth status
```

If the listed scopes do **not** include `project`, never pass `-p`/`--project` to any `gh` command — it fails on the missing scope. Skip all project-board wiring in that case.

---

## Resolve the base branch

Ask the repo for its default branch instead of assuming `main` vs `master`. Capture it as `<default>` (also used as `<base>` in diff commands).

```bash
gh repo view --json defaultBranchRef --jq .defaultBranchRef.name
```

`{owner}/{repo}` in later commands also auto-resolves from the current repo — never hardcode an org.

---

## Find the PR template

GitHub accepts the template in the repo root, `docs/`, or `.github/` (`.github/` is by far the most common in practice), and **the casing varies** by repo. Glob all of them and take the first match:

```text
.github/pull_request_template.md
.github/PULL_REQUEST_TEMPLATE.md
.github/PULL_REQUEST_TEMPLATE/*.md
pull_request_template.md
docs/pull_request_template.md
PULL_REQUEST_TEMPLATE/*.md
docs/PULL_REQUEST_TEMPLATE/*.md
```

Locate it from the shell:

```bash
ls .github/pull_request_template.md \
   .github/PULL_REQUEST_TEMPLATE.md \
   .github/PULL_REQUEST_TEMPLATE/*.md \
   pull_request_template.md \
   docs/pull_request_template.md \
   PULL_REQUEST_TEMPLATE/*.md \
   docs/PULL_REQUEST_TEMPLATE/*.md 2>/dev/null
```

Notes:

- The multi-template directory (`PULL_REQUEST_TEMPLATE/*.md`) holds **multiple** named templates and is valid under `.github/`, the repo root, or `docs/` (GitHub's own docs: "store multiple pull request templates in a `PULL_REQUEST_TEMPLATE` subdirectory within the root or `docs/` directories") — pick the one matching the change (e.g. `bugfix.md`, `feature.md`) or ask ONE question if ambiguous.
- Read the matched file's content; you will fill it yourself and pipe the result via `--body-file -`.
- If nothing matches, jump to **No template? Use `--fill`**.

---

## Auto-detect the ticket KEY, branch & commit style

Detect the project **KEY** (e.g. `PROJ`, `ABC`) — most-frequent prefix wins. Precedence: repo docs (CLAUDE.md / agents.md / README) → recent branches → recent commits.

```bash
git for-each-ref --format='%(refname:short)' refs/heads refs/remotes | grep -oE '[A-Z][A-Z0-9]+-[0-9]+'
```

```bash
git log -50 --format=%s
```

The full issue id is `<KEY>-<n>` (e.g. `PROJ-123`, `ABC-42`). Branch grammar is one of — detect which the repo uses from the branch history above:

```text
<type>/<KEY>-<n>-<slug>      # type ∈ feature | feat | fix | refactor | ci
<KEY>-<n>-<slug>             # bare, no type prefix
```

`<slug>` = the ticket summary, lowercased, ascii-only, hyphenated, collapsed, trimmed.

Detect the **commit subject** style from `git log -50 --format=%s` and mirror it in the PR `--title`. Common styles:

```text
[KEY-####] Title
KEY-###: Description
feat: … / fix: …          # Conventional Commits
```

If no issue-key pattern exists anywhere, use Conventional Commits with `<type>/<slug>` branches and ask ONE question. If two keys compete or none is found, ask ONE question and record the answer to LEARNED.md.

The `(#N)` suffix some merged titles show is the platform's PR number, appended by GitHub **at merge** — never author it by hand.

---

## Generate the Summary from the diff

Build the Summary block from a file-level stat plus the branch's commit subjects, computed against `<default>`.

```bash
git diff <default>...HEAD --stat
```

```bash
git log <default>..HEAD --format='%s'
```

Turn the `--stat` output into a short "Changed files" note and the commit subjects into Summary bullets. No temp file — feed the assembled body to `gh pr create` on stdin.

---

## Fill the template

When a template was found, fill it — do not discard its structure:

- **Prepend a Ticket section** with the issue URL: `<site>/browse/<KEY>-<n>`.
- **Add a Summary** generated from the diff (bullets from the commit subjects + stat).
- **Keep every checklist** (`- [ ]`) intact; leave a box unticked unless the work genuinely satisfies it.
- Replace `<!-- placeholder -->` / `<placeholder>` comments with real content; drop lines that don't apply rather than leaving stubs.

---

## Create the PR — filled body via heredoc

Pipe the filled body on stdin with `--body-file -`. Keep `--title` in the detected commit style; `--title`/`--body` override `--fill` when combined.

```bash
gh pr create \
  --base <default> \
  --head <branch> \
  --title "[PROJ-123] Short desc" \
  --body-file - <<'EOF'
## Ticket

<site>/browse/PROJ-123

## Summary

- <generated from the diff — one bullet per meaningful change>
- <second change>

## Changed files

<paste of `git diff <default>...HEAD --stat`>

## Checklist

- [ ] Tests added or updated
- [ ] Docs updated
- [ ] CI is green
EOF
```

To point `gh` at one specific file from the `PULL_REQUEST_TEMPLATE/` directory instead of piping your own body, use `-T`/`--template <file>` (interactive/web flow):

```bash
gh pr create --base <default> --template feature.md
```

---

## No template? Use `--fill`

When the Glob finds nothing, let `gh` populate the title and body from the branch commits:

```bash
gh pr create --base <default> --fill
```

Related fill variants: `--fill-first` (use only the first commit), `--fill-verbose` (include full commit bodies).

---

## `gh pr create` flag reference

All verified present on `gh pr create`:

- `-t`/`--title`, `-b`/`--body`, `-F`/`--body-file` (`-` = stdin)
- `-B`/`--base`, `-H`/`--head`
- `-l`/`--label`, `-m`/`--milestone`, `-a`/`--assignee`, `-r`/`--reviewer`
- `-d`/`--draft`, `-T`/`--template <file>`
- `-f`/`--fill`, `--fill-first`, `--fill-verbose`
- `--dry-run`, `-R`/`--repo`

Caveats:

- `--title`/`--body` override `--fill`.
- `--dry-run` prints what would be created — but may still **push the current branch** to the remote as part of setup.
- **Never** `-p`/`--project` unless the token carries the `project` scope (see Preflight).

---

## Read back the PR

After creation, read the canonical URL, number, and title as JSON.

```bash
gh pr view <n> --json url,number,title
```

`<n>` may be the PR number or the branch; right after create on the same branch you can omit it.

---

## Labels

Discover what the repo already defines, then apply only matching names — never invent a taxonomy. Report a wanted label that doesn't exist instead of creating it.

```bash
gh label list --json name,description --limit 100
```

Apply on an existing PR (`--add-label` is repeatable):

```bash
gh pr edit <n> --add-label "enhancement" --add-label "documentation"
```

---

## Milestones

There is no dedicated `gh` milestone command — go through `gh api`. The milestone must already exist; `gh` will not create one.

```bash
gh api "repos/{owner}/{repo}/milestones" --jq '.[].title'
```

Attach an existing milestone (`{owner}/{repo}` and `<m>` auto-resolve):

```bash
gh pr edit <n> --milestone "<m>"
```

---

## Linked ticket & review status

Comment the PR URL onto the ticket, then transition it to the review state. The transition status is **instance-specific** — resolve `"<Review status>"` from LEARNED.md or ask ONE question, then record it. Do not assume a fixed string.

- Ticket description / Summary stays **non-technical**: no file paths, symbols, code, or internal ids — that detail belongs in the PR body, not the ticket.
- **Code comments must not name tickets, skills, or personas.**
