# gitlab — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: read LEARNED.md; announce "Using: gitlab skill"; `glab auth status` (install glab if missing)
- **Terminology**: GitLab = **Merge Request (MR)**, not PR; confirm `glab mr create --help` flags on first use
- **Ticket**: reuse the active Jira ticket from context; else ask or hand off to jira skill (skip cleanly if no Jira)
- **Auto-detect** project + target branch + branch/commit style + MR template; branch `<type>/<KEY>-<n>-<slug>` or bare, commit `[<KEY>-<n>] Title`
- **MR desc** from template + `git diff <target>...HEAD`; then labels/milestone (only what exists)
- **Update linked Jira**: comment MR link + `transition --status "<Review status>" --yes`; recipes: references/glab-recipes.md
