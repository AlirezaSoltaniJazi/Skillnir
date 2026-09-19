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

- 2026-08-02: Strings use double quotes in many newer files in this codebase, not single quotes uniformly. Black `-S` preserves existing quotes — it does not enforce single quotes. SKILL.md's "Strings: Single quotes (Black -S enforced)" row was stale; rewritten directly in SKILL.md on 2026-08-02 to say to match the file being edited (calling out which files are double-quoted and that `layout.py` itself is mixed), this entry kept for history.
- 2026-08-02: `pyproject.toml`'s dev floor is `pytest>=9.0.3`, not `9.0.2+` as SKILL.md's Testing Standards table previously said; fixed directly in SKILL.md on 2026-08-02, this entry kept for history.
- 2026-08-02: `src/skillnir/ui/layout.py` is now 833 lines (SKILL.md's Architecture tree previously said "670 lines"); fixed directly in SKILL.md on 2026-08-02, this entry kept for history.
- 2026-08-02: `src/skillnir/ui/pages/` has grown to 23 route modules (SKILL.md's Architecture tree previously listed only the original 12: `home.py`, `skill.py`, `delete_skill.py`, `generate_skill.py`, `ai_context.py`, `ai_extra.py`, `settings.py`, `supported.py`, `usage_page.py`, `research.py`, `events.py`, `templates.py`). Added since: `benchmarks.py`, `cleanup_articles.py`, `harness_research.py`, `ignore.py`, `news.py`, `optimize_docs.py`, `package_vulns_page.py`, `security_page.py`, `software_research.py`, `testing_research.py`, `wiki.py` — SKILL.md's Architecture tree now lists all 23, fixed directly on 2026-08-02, this entry kept for history.
