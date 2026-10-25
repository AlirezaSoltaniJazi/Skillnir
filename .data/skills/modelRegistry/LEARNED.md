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
- 2026-09-28: `cursor-agent --list-models` now returns the full catalog on this machine (239 IDs) — Cursor entries are verifiable again. Cursor IDs carry effort/thinking/fast suffixes (`claude-opus-5-5-medium`, `-max`, `-thinking-high`, `-fast`); pick the variant whose display name has no suffix as the family's plain entry. Fable variants are labeled "(NO ZDR)" — surface that in the display name.
- 2026-09-28: Copilot's model list is readable without login via `copilot help config` (also through `npx -y @github/copilot@latest help config` when not installed). Its IDs use dotted versions (`claude-opus-4.8`, `claude-sonnet-4.6`) — the earlier dashed entries (`claude-opus-4-8`, `claude-sonnet-4-5`) were never valid Copilot IDs. The CLI list can lag the GitHub docs page (CLI 1.0.88 lacked Opus 5.5 and GPT-6 Sol/Luna); the CLI list wins.
- 2026-09-28: Gemini CLI 0.61.0 still returns `IneligibleTierError` for the free individual tier. Gemini IDs were verified against Google's live model docs (`ai.google.dev/gemini-api/docs/models`) instead; shut-down models (`gemini-3-pro-preview`, `gemini-2.0-*`) were removed and the unversioned `pro` / `flash` / `flash-lite` aliases moved to the newest models, with `2.5-*` aliases for the Limited Access 2.5 models.
- 2026-09-28: Retired Claude models are removed rather than kept as legacy: once the deprecations page marks a model "Retired", requests fail. Removing an alias is safe for saved configs — `AppConfig.from_dict` falls back to the backend's `default_model` when the stored alias is gone.
- 2026-09-28: New Claude models can require a minimum Claude Code CLI version, and `claude-agent-sdk` runs its OWN bundled CLI (version in `claude_agent_sdk/_cli_version.py`), not the `claude` on PATH. Opus 5.5 needs CLI >= 2.1.280; SDK 0.2.87 bundled 2.1.150, so every SDK generation failed with a 400. When adding a Claude model: make one real SDK call with it, and if it fails, `uv lock --upgrade-package claude-agent-sdk` and raise the `claude-agent-sdk>=` floor in pyproject.toml (both entries).
