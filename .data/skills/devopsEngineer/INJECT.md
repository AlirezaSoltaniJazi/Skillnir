# devopsEngineer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: GitHub Actions CI, pre-commit hooks (Black, pylint, autoflake, bandit, safety, prettier), Python 3.14+, uv, hatchling
- **CI pipelines**: `.github/workflows/` — run-tests, check-style, auto-assign-author (all PR-triggered)
- **Quality gates**: Black → Autoflake → Pylint → Bandit (sequential, cheapest first)
- **Key rules**: Pin action versions (`@v4`), set `timeout-minutes` on all jobs, exclude `.data/` from hooks, document CVE exemptions
- **Never**: Unpinned actions (`@main`), hardcoded secrets, skip pre-commit (`--no-verify`), Docker/K8s/Terraform (CLI tool, not a service), `requirements.txt`
- **Sub-agents**: security-scanner (audit), pipeline-reviewer (review), hook-debugger (fix)
- **Self-learning**: On correction → write to LEARNED.md. On ambiguity → check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
