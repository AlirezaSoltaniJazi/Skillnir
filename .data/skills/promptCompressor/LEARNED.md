# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries -- they accumulate over time.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

## Preferences

## Discovered Conventions

- 2026-08-02: SKILL.md's "Integration point: Single function `build_subprocess_command()`" undersells it — `maybe_compress_prompt()` (also in `backends.py`) is the integration point for the async-SDK path and is called from `generator.py`, `docs_compressor.py`, `docs_optimizer.py`, `rule_generator.py`, `wiki_generator.py`, and `skill_generator.py` in addition to `build_subprocess_command()`.
