# devops engineer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **CI/CD**: GitHub Actions on `pull_request` — 3 workflows: check-style, run-tests, auto-assign-author
- **Quality gate**: Black -S → Autoflake → Pylint (fail-under=10) → Bandit (-lll -iii) → pytest
- **Pre-commit**: 7 hooks, exclude `.data/` from code quality hooks, pin all `rev:` versions
- **Build**: hatchling + uv exclusively (never pip/poetry), Python 3.14+, entry point `skillnir.cli:main`
- **Never**: Use pip, skip pre-commit (--no-verify), hardcode secrets, set fail-under below 10, force-push main
- **Composite actions**: `.github/actions/setup-python/` — always checkout before referencing local actions
- **Sub-agents**: security-scanner, drift-detector, cost-reviewer — see [agents/](agents/) for delegation rules
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
