# devopsEngineer — Quick Reference

- **FIRST**: Read [LEARNED.md](LEARNED.md)
- **Stack**: GitHub Actions + pre-commit + uv/hatchling, Python 3.14+
- **Gates**: Black → Autoflake → Pylint → Bandit (cheapest first)
- **Always**: pin actions/hooks, `timeout-minutes` per job, exclude `.data/`, CI ↔ pre-commit parity
- **Never**: `@main`/`@latest`, hardcoded secrets, `--no-verify`, Docker/K8s (CLI tool)
- **Map**: `.github/workflows/`, `.pre-commit-config.yaml`, `.pylintrc`, `pyproject.toml`
- **Sub-agents**: security-scanner, pipeline-reviewer, hook-debugger — see [SKILL.md](SKILL.md)
