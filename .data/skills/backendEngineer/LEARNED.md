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
