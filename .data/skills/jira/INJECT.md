# jira — Quick Reference

- **FIRST**: read LEARNED.md; announce "Using: jira skill"; `acli jira auth status`
- **Tool**: `acli jira workitem …`; site + account from auth status — never hardcode a domain
- **Key**: auto-detect per repo from branches/commits/docs (e.g. `ABC-123`) — never hardcode
- **Create = child**: search parent Epic/Story → pick → `create --parent <P>`; confirm first
- **Active ticket lives in context only** — reuse it; ask before creating a new one
- **Transition** to the review status (detect/ask → LEARNED.md); recipes: references/acli-recipes.md
