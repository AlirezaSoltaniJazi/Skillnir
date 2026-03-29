# Skillnir — Quick Reference

- **Stack**: Python 3.14+ · NiceGUI · questionary · claude-agent-sdk · hatchling/uv
- **Entry points**: `src/skillnir/cli.py` (CLI) · `src/skillnir/ui/layout.py` (Web UI)
- **Key dirs**: `src/skillnir/` (core package) · `.data/skills/` (source of truth) · `tests/` (pytest) · `.data/promptsv1/` (generation templates)
- **Run**: `uv run skillnir --help` / `uv run pytest` / `uv run pre-commit run --all-files`
- **Patterns**: Result dataclasses with `error: str | None` · frozen dataclasses for configs · relative symlinks for injection · absolute imports only · `pathlib.Path` everywhere
- **Never**: Edit SKILL.md manually (generated) · use relative imports · use single quotes (Black -S) · hardcode absolute symlink paths · put NiceGUI imports at package top level
- **Full context**: See [agents.md](agents.md)
