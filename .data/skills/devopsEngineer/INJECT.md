# devopsEngineer — Quick Reference

<!-- Always-loaded firewall: 50-150 tokens, bullets only. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) for prior corrections
- **Stack**: GitHub Actions CI, pre-commit (Black, pylint, autoflake, bandit, safety, prettier), Python 3.14+, uv, hatchling
- **CI**: `.github/workflows/` — run-tests, check-style, auto-assign-author (PR-triggered)
- **Gates**: Black → Autoflake → Pylint → Bandit (cheapest first)
- **Always**: pin actions (`@v4`), `timeout-minutes` on jobs, exclude `.data/` from hooks, document CVE exemptions
- **Never**: unpinned actions (`@main`), hardcoded secrets, `--no-verify`, Docker/K8s/Terraform (CLI tool, not a service)
- **Sub-agents**: security-scanner, pipeline-reviewer, hook-debugger
- **Full guide**: [SKILL.md](SKILL.md), [references/](references/)
