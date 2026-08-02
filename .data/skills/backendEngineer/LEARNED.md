# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries — they accumulate over time.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

<!-- AI writes here when user corrects generated code -->

## Preferences

<!-- AI writes here when user states a preference -->

## Discovered Conventions

<!-- AI writes here when it discovers implicit project conventions through analysis -->

- 2026-07-01: Strings use double quotes in this codebase (~1,370 double-quoted vs ~50 single-quoted literals in `src/skillnir/`). Black `-S` preserves existing quotes — it does not enforce single quotes. SKILL.md's "single quotes preferred" rows are stale; follow the surrounding file's double-quote style until SKILL.md is regenerated.
- 2026-07-01: `cli.py` has no argparse subparsers and no `build_parser()` — all 25 commands are entries in the `choices=[...]` list of the single positional `command` argument in `main()`, handled by zero-arg, underscore-prefixed functions (`_my_command()`) dispatched via `elif`. Ignore SKILL.md's "argparse subparser" wording.
- 2026-08-02: `cli.py`'s `choices=[...]` list now has 28 commands (grew from 25): added `harness-research`, `software-research`, `cleanup-articles`, `package-vulns`, `news`.
- 2026-08-02: `pyproject.toml`'s dev floor is `pytest>=9.0.3`, not `9.0.2+` as SKILL.md's Testing Standards table says.
- 2026-08-02: `cli.py` is now 2,224 lines (SKILL.md's Architecture tree still says "1,287 lines"); `TOOLS` in `tools.py` has 37 entries (SKILL.md's Architecture tree still says "32+ tools").
- 2026-08-02: SKILL.md's Architecture tree lists ~19 of the 37 modules now in `src/skillnir/`; it predates `benchmarks.py`, `compressor.py`, `crypto.py`, `docs_compressor.py`, `docs_optimizer.py`, `notifications/`, `notifier.py`, `security.py`, `harness_researcher.py`, `software_researcher.py`, `testing_researcher.py`, `news.py`, `package_vulns.py`, `skill_validator.py`, `article_cleanup.py`, `article_status.py`, and `wiki_generator.py` — all present today.
