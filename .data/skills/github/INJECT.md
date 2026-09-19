# github — Quick Reference

- **FIRST**: read LEARNED.md; announce "Using: github skill"; `gh auth status`
- **Scopes**: no `project` scope → never `gh pr create -p`
- **Ticket**: reuse the active Jira ticket from context; else ask or hand off to jira (skip if no Jira)
- **Auto-detect** owner/repo, base branch, branch/commit style, PR template — never assume
- **PR**: body from template + `git diff <base>...HEAD`; apply only labels/milestones that exist
- **Update Jira**: comment PR link + transition to the review status; recipes: references/pr-recipes.md
