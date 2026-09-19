# Finding & Filling a GitLab MR Template

> How the gitlab skill locates a project's Merge Request template, fills it from the branch diff and the linked ticket, and falls back to `glab mr create --fill` when no template exists — referenced from SKILL.md. GitLab uses **Merge Request (MR)**, never "Pull Request".

> [!IMPORTANT]
> `glab` was **NOT** available to verify live in this environment. Every flag below is the _typical_ surface. On first use in any repository run `glab mr create --help` and confirm the exact flag names and behavior, then record any differences to `LEARNED.md`.

---

## Find the template

GitLab stores project MR templates as individual `.md` files under `.gitlab/merge_request_templates/` — unlike GitHub, there is no single template file at the repository root. Each filename (minus `.md`) is a selectable template name. Glob for them:

```bash
ls -1 .gitlab/merge_request_templates/*.md 2>/dev/null
```

A repo can also set a project-level default description template in **Settings > Merge requests** (GitLab Premium/Ultimate). That default isn't a file you can `ls` — if the Glob above finds a `Default.md`, GitLab prefers it unless a project-settings default overrides it; either way, ask if you can't tell which the project expects.

Notes on which one to use:

- **Multiple templates found** — pick `Default.md` if present (case-insensitive); otherwise choose the one whose name matches the change (for example a `Bugfix` template for a fix branch), or ask which to use and record the answer to `LEARNED.md`.
- **One template found** — use it.
- **None found** — skip to the `--fill` fallback at the bottom.

Record the resolved MR-template path to `LEARNED.md` so the next session skips the search.

---

## Resolve the target branch and gather the diff

The template's Summary is built from what the branch actually changes. First resolve the target (default) branch — detect it, never assume `main` vs `master`:

```bash
git symbolic-ref refs/remotes/origin/HEAD | sed 's@.*/@@'
```

Then summarize the branch against that resolved `<target>`:

```bash
git diff <target>...HEAD --stat
git log <target>..HEAD --format='%s'
```

Use the `--stat` output as a "Changes" block and the commit subjects as Summary bullets.

---

## Fill the template

Copy the resolved template to a working body file, then edit that copy — never edit the template itself:

```bash
cp .gitlab/merge_request_templates/Default.md body.md
```

Fill `body.md` following three rules:

- **Prepend the ticket URL.** Put a link to the linked work item at the top. The Jira site `<site>` comes from `acli jira auth status` — never hardcode a domain. The issue key `<KEY>` is the full id (for example `PROJ-123` or `ABC-42`). URL form: `https://<site>/browse/<KEY>`.
- **Add a Summary from the diff.** Turn the commit subjects into short Summary bullets and drop the `--stat` output into a Changes block. Describe _what changed and why_ — do not paste code.
- **Keep the template's checklists verbatim.** Preserve every checklist item and heading the template ships with. Leave a box unchecked (`- [ ]`) unless that item is genuinely done; only then tick it (`- [x]`). Do not delete, reword, or reorder the template's sections.

---

## Filled example

A concrete `body.md` after filling a template — placeholder key `PROJ-123`, placeholder Jira site `<site>`:

```markdown
Related: https://<site>/browse/PROJ-123

## Summary

- Extract the retry logic into a reusable helper
- Cap retries at the configured ceiling instead of looping unbounded
- Add coverage for the exhausted-retries path

## Changes

src/client/retry.py | 42 ++++++++++++++++-----
src/client/**init**.py | 3 +-
tests/test_retry.py | 58 +++++++++++++++++++++++++++++
3 files changed, 92 insertions(+), 11 deletions(-)

## Checklist

- [x] Tests added / updated
- [x] Self-reviewed the diff
- [ ] Docs updated
- [ ] Breaking change noted in the changelog
```

The Summary and Changes come from the diff commands above; the `## Checklist` section is the template's own — kept as-is, boxes ticked only where true.

---

## Create the MR with the filled body

`glab` has **no `--body-file`** flag — pass the filled file inline with command substitution. The `--title` mirrors the repo's detected commit-subject style (auto-detected, never hardcoded; e.g. `[PROJ-123] <short desc>` or `PROJ-123: <short desc>`):

```bash
glab mr create \
  --title "<title>" \
  --description "$(cat body.md)" \
  --source-branch "<source>" \
  --target-branch "<target>"
```

---

## No template — the `--fill` fallback

When the Glob finds no template, let `glab` derive the title and description from the branch's commit messages instead of hand-writing a body. Confirm the flag with `glab mr create --help` before relying on it, and record any difference to `LEARNED.md`:

```bash
glab mr create --fill --source-branch "<source>" --target-branch "<target>"
```

`-f/--fill` populates title + description from the commit subjects on the branch. Prefer this only when there is no template _and_ the commit history already reads well; otherwise write a `body.md` and use `--description "$(cat body.md)"` as above.
