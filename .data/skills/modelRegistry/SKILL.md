---
name: modelRegistry
description: >-
  Keeps Skillnir's AI model selection list and backend CLI install hints current.
  Checks authoritative live sources for newly released models (Claude, Cursor,
  Gemini, Copilot), updates the model registry in backends.py using the project's
  alias/tier/default conventions, and refreshes the per-backend install / login /
  verify hints shown in the web UI. Activates when the user asks to "check for new
  models", "update the model list", "is the model picker up to date", "add <model>
  to the picker", says a new Claude/Opus/Sonnet/Fable/Haiku model is out, or wants
  to review or fix the CLI install instructions.
compatibility: "Skillnir repo; WebFetch for live model docs; backend CLIs optional"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: maintenance
allowed-tools: Read Edit Write WebFetch Bash(uv:*) Bash(cursor-agent:*) Bash(gemini:*) Bash(claude:*) Glob Grep
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Commands go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It records which sources were reachable, account/tier limits found on this machine, and past corrections. Entries there override defaults here.

**Announce skill usage.** Say "Using: modelRegistry skill" at the very start of your response before doing any work.

**Never answer model questions from memory.** Model IDs are exact strings and the lineup changes often; a remembered ID is how a broken model reaches the picker. Always check a live source first — see [model-sources.md](references/model-sources.md).

## When to Use

1. Checking whether the model selection list is still current
2. Adding a newly released model, or retiring one
3. Fixing a wrong/missing model ID, alias, tier, or default
4. Reviewing or updating the CLI install / login / verify hints
5. Auditing that the picker, CLI, and tests all agree

## Do NOT Use

- **Changing which model a run uses right now** — that's the Settings page or the Switch Model dialog, not a code change.
- **Adding a new skill scope or prompt template** — use [skillnir](../skillnir/SKILL.md) (different registry, different file).
- **Backend behavior (effort, thinking, subprocess flags)** — use [backendEngineer](../backendEngineer/SKILL.md); this skill owns the catalog data, not the execution path.

## What This Skill Owns

| Concern                                  | File                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------- |
| Model selection list (all 4 backends)    | `src/skillnir/backends.py` → `BACKENDS[...].models`                        |
| Default model + alias resolution         | `src/skillnir/backends.py` → `default_model`, `resolve_model_id()`          |
| CLI install / login / verify hints       | `src/skillnir/ui/components/welcome_dialog.py` → `_CLI_SETUP_INFO`          |
| Alias + catalog invariants (tests)       | `tests/test_backends.py`                                                    |

The web UI picker and the CLI config menu both build from `BACKENDS`, so a registry-only edit surfaces everywhere. Details: [backends-registry-guide.md](references/backends-registry-guide.md).

## Authoritative Sources

| Backend | Source                                                      | How                                                   |
| ------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| Claude  | Anthropic models overview (live)                            | WebFetch the models-overview doc — the canonical table |
| Claude  | Model deprecations page                                     | WebFetch, for retirement dates                        |
| Cursor  | The CLI itself                                              | `cursor-agent --list-models`                          |
| Gemini  | Google AI model docs                                        | No list command; check docs                           |
| Copilot | The TUI                                                     | `copilot`, then `/model`                              |

Exact URLs and commands: [model-sources.md](references/model-sources.md).

## Rules

Every rule states its WHY — that's what lets you generalize to cases not listed here.

| Rule                                                                                       | Why                                                                                                     |
| ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| **MUST** verify each model ID against a live source before editing                         | IDs are exact strings; a guessed ID 404s at runtime and the picker silently offers a broken model        |
| **MUST** keep the unversioned alias (`fable`/`opus`/`sonnet`/`haiku`) on the family's newest | Saved configs store the alias, so users track the latest without editing `config.json`                   |
| **MUST** give the superseded model its own versioned alias (`opus-4.8`, `fable-5`)          | Without it the older model is unreachable for anyone who needs to pin a known-good version               |
| **MUST** keep exactly one `is_default=True` per backend, and `default_model` an alias that resolves | The picker and every new config read it; two defaults or a dangling alias breaks model resolution |
| **MUST** update the alias assertions in `tests/test_backends.py` in the same edit           | They pin the flagship; a stale assertion keeps passing while pointing at the wrong model                 |
| **MUST** add a `## [Unreleased]` CHANGELOG entry                                            | Model list changes are user-facing — the picker and the default both change under the user               |
| **Never** list invitation-only or restricted models (e.g. Mythos / Project Glasswing)       | Offering a model most accounts cannot call turns into a confusing runtime failure, not a useful choice   |
| **Never** edit UI files to add a model                                                      | `backend_picker` builds from the registry; a UI edit drifts from the source of truth                     |
| **Never** guess third-party (Cursor/Gemini/Copilot) IDs when the CLI can't list them        | An unverifiable ID is worse than an omission — it breaks the picker for everyone on that backend         |

## Tier Map

| Tier | Picker group       | Use for                          |
| ---- | ------------------ | -------------------------------- |
| 1    | Powerful           | Flagship / most capable          |
| 2    | Balanced           | Mid-tier default workhorse       |
| 3    | Fast & Affordable  | Small, fast, cheap               |

Tier drives the grouping in the Switch Model dialog — a wrong tier misfiles the model in the UI.

## Common Recipes

**Add a newly released model**

1. WebFetch the models-overview doc; copy the exact API ID and display name.
2. Add a `ModelInfo(id, alias, display_name, tier=N)` entry to that backend's `models` tuple.
3. If it supersedes the family flagship: move the unversioned alias to it, and give the old one a versioned alias.
4. If it becomes the default: move `is_default=True`, and confirm `default_model` still resolves.
5. Update the alias assertions in `tests/test_backends.py`; add one for the demoted alias.
6. Run the verification checklist below, then add the CHANGELOG entry.

**Retire / mark a model legacy** — keep it listed with a versioned alias unless the provider has actually removed it; only delete once the ID 404s, because pinned configs still reference it.

**Refresh install hints** — see [install-hints-guide.md](references/install-hints-guide.md).

## Verification

1. `uv run pytest tests/test_backends.py -q` — alias + catalog invariants
2. Resolve each alias and confirm it maps to the intended ID
3. `uv run black -S --check` and `uv run pylint` on changed files
4. `scripts/validate-model-registry.sh` — unique aliases, single default, resolvable `default_model`

## Anti-Patterns

| Anti-pattern                                     | Why it's wrong                                                                 |
| ------------------------------------------------ | ------------------------------------------------------------------------------ |
| Copying an ID from a blog post or changelog      | Marketing names ≠ API IDs; only the provider's model doc/CLI is authoritative   |
| Appending a date suffix to a dateless ID         | Current Claude IDs are already pinned snapshots; a suffixed variant 404s        |
| Leaving two `is_default=True` entries            | Resolution picks arbitrarily — the "default" badge and new configs disagree     |
| Reusing an alias already taken                   | `resolve_model_id` returns the first match, so one model becomes unreachable    |
| Editing the picker to reorder models             | Order comes from the registry tuple; UI edits get overwritten by the next pass  |

## Session Protocols

| Mode       | Trigger                                        | Behavior                                                       |
| ---------- | ---------------------------------------------- | -------------------------------------------------------------- |
| Teaching   | "how do aliases work", first time in registry  | Explain the alias/tier/default contract, cite `backends.py`     |
| Efficient  | "add model X", "refresh the list"              | Verify source → edit → tests → CHANGELOG, minimal prose         |
| Diagnostic | "picker shows wrong model", resolution failure | Resolve every alias first, then compare against the live source |

- **FIRST**: read [LEARNED.md](LEARNED.md) before editing.
- On correction: restate as a rule and append to LEARNED.md (`- YYYY-MM-DD: rule`).
- Record source reachability and account/tier limits in LEARNED.md — they change per machine.
- Deeper guidance: [ai-interaction-guide.md](references/ai-interaction-guide.md).

## Communication Style

Concise and factual. Report the model list as a table (ID → alias → tier), state explicitly which IDs were verified live and which could not be verified, and never present an unverified ID as confirmed.

## References

| File                                                                     | Description                                        |
| ------------------------------------------------------------------------ | -------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | Corrections, preferences, discovered conventions   |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference                      |
| [model-sources.md](references/model-sources.md)                          | Authoritative URLs + per-backend check commands    |
| [backends-registry-guide.md](references/backends-registry-guide.md)      | `ModelInfo`/`BackendInfo` structure + edit recipe  |
| [alias-conventions.md](references/alias-conventions.md)                  | Alias, tier, and default rules with worked examples |
| [install-hints-guide.md](references/install-hints-guide.md)              | `_CLI_SETUP_INFO` structure + how to verify hints  |
| [common-issues.md](references/common-issues.md)                          | Troubleshooting unreachable sources and CLIs       |
| [ai-interaction-guide.md](references/ai-interaction-guide.md)            | Interaction depth, proficiency calibration         |
