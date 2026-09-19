# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries — they accumulate over time.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

## Preferences

## Discovered Conventions

- 2026-09-19: The unversioned alias tracks the family flagship. When Fable 5.1 shipped, `fable` was repointed from `claude-fable-5` to `claude-fable-5-1` and the older model kept a `fable-5` alias — same pattern previously applied to `opus` (→ Opus 5) and `sonnet` (→ Sonnet 5).
- 2026-09-19: Claude model IDs from the 4.6 generation onward are dateless AND already pinned snapshots — never append a date suffix. Only Haiku 4.5 has a dated form (`claude-haiku-4-5-20251001`) alongside its `claude-haiku-4-5` alias.
- 2026-09-19: Claude Mythos is Project Glasswing / invitation-only, so it is deliberately omitted from the picker — listing a model most accounts cannot call produces confusing runtime failures.
- 2026-09-19: `cursor-agent --list-models` returned "No models available for this account" on this machine — the CLI is installed and authenticated-capable, but without account model access the Cursor list cannot be verified. Do not guess Cursor IDs in that state.
- 2026-09-19: The Gemini CLI (`@google/gemini-cli` 0.36.0) fails with `IneligibleTierError` for individual free-tier accounts — Google redirects those users to the "Antigravity" suite. Treat the Gemini install hint as unverifiable for free-tier users until that changes.
- 2026-09-19: `copilot` was not installed on this machine (not on PATH, not npm-global, not a `gh` extension), so its model list could not be verified.
