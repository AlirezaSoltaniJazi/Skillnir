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

- 2026-08-02: Strings use double quotes in this codebase, not single quotes. Black `-S` preserves existing quotes — it does not enforce single quotes. SKILL.md's "Strings: Single quotes (Black -S enforced)" row is stale; follow the surrounding file's double-quote style until SKILL.md is regenerated.
- 2026-08-02: `pyproject.toml`'s dev floor is `pytest>=9.0.3`, not `9.0.2+` as SKILL.md's Testing Standards table says.
- 2026-08-02: `src/skillnir/ui/layout.py` is now 833 lines (SKILL.md's Architecture tree still says "670 lines").
- 2026-08-02: `src/skillnir/ui/pages/` has grown to 23 route modules (SKILL.md's Architecture tree still lists only the original 12: `home.py`, `skill.py`, `delete_skill.py`, `generate_skill.py`, `ai_context.py`, `ai_extra.py`, `settings.py`, `supported.py`, `usage_page.py`, `research.py`, `events.py`, `templates.py`). Added since: `benchmarks.py`, `cleanup_articles.py`, `harness_research.py`, `ignore.py`, `news.py`, `optimize_docs.py`, `package_vulns_page.py`, `security_page.py`, `software_research.py`, `testing_research.py`, `wiki.py`.
