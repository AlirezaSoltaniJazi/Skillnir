# jira — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: read LEARNED.md; announce "Using: jira skill"; `acli jira auth status`
- **Tool**: `acli jira workitem …`; site + account come from auth status — never hardcode a domain
- **Key**: auto-detect per repo from git branches/commits/docs (e.g. `ABC-123`) — never hardcode
- **Create = child under a parent**: search Epics/Stories → user picks → `create --parent <P>`; confirm first; keep descriptions non-technical
- **Active ticket lives in context only** — reuse it; ask before making a new one
- **Transition** to the team's review status (detect/ask, record to LEARNED.md); recipes: references/acli-recipes.md
