# github — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: read LEARNED.md; announce "Using: github skill"; `gh auth status`
- **Scopes**: if the token lacks `project`, never `gh pr create -p`
- **Ticket**: reuse the active Jira ticket from context; else ask or hand off to jira skill (skip cleanly if no Jira)
- **Auto-detect** owner/repo + base branch + branch/commit style + PR template; branch `<type>/<KEY>-<n>-<slug>` or bare, commit `[<KEY>-<n>] Title`
- **PR body** from template + `git diff <base>...HEAD`; then labels/milestone (only what exists)
- **Update linked Jira**: comment PR link + `transition --status "<Review status>" --yes`; recipes: references/pr-recipes.md
