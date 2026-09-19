# gitlab — Quick Reference

- **FIRST**: read LEARNED.md; announce "Using: gitlab skill"; `glab auth status`
- **Terminology**: GitLab = MR, not PR; confirm `glab mr` flags on first use
- **Ticket**: reuse the active Jira ticket from context; else ask or hand off to jira (skip if no Jira)
- **Auto-detect** project, target branch, branch/commit style, MR template — never assume
- **MR**: desc from template + `git diff <target>...HEAD`; apply only labels/milestones that exist
- **Update Jira**: comment MR link + transition to the review status; recipes: references/glab-recipes.md
