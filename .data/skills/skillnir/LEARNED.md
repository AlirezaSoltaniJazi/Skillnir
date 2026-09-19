# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries — they accumulate over time.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

<!-- AI writes here when user corrects skill system actions -->

## Preferences

<!-- AI writes here when user states a preference about skill system conventions -->

## Discovered Conventions

<!-- AI writes here when it discovers implicit skill system conventions through analysis -->

- 2026-08-02: This skill's own `SKILL.md` frontmatter says `compatibility: "Python 3.13+..."`; `pyproject.toml` requires `>=3.14`. Treat this skill as Python 3.14+ until `SKILL.md` is regenerated.
- 2026-08-02: `.data/skills/` now has 9 directories, not the 4 shown in `SKILL.md`'s Architecture diagram: `github`, `gitlab`, and `jira` were added in commit `4c980f2` (2026-08-01) alongside the existing `backendEngineer`, `devopsEngineer`, `frontendEngineer`, `promptCompressor`, `securityEngineer`, `skillnir`. Treat all 9 as the current skill roster until `SKILL.md` is regenerated.
- 2026-09-19: Do NOT hardcode the skill roster in `SKILL.md` — it has gone stale twice (4→9→10) and each name costs budget in a file capped at 3,500 tokens. `SKILL.md` now points at `ls .data/skills/` instead. `modelRegistry` was the 10th skill added.
