---
name: skillnir
description: >-
  Cross-cutting skill system rules for the skillnir (skillnir) project. Defines
  how to interact with skill files (SKILL.md, LEARNED.md, INJECT.md, references/),
  file ownership, content placement, skill activation protocols, cross-skill
  coordination, and LEARNED.md self-learning. Activates when working with any
  skill file, adding learnings, resolving content placement ambiguity, creating
  or modifying skill directory structure, or coordinating between domain skills.
compatibility: "Python 3.14+, skillnir CLI, YAML frontmatter, Markdown skill files"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development
allowed-tools: Read Edit Write Glob Grep
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: skillnir skill" at the very start of your response before doing any work.

## When to Use

1. Working with ANY skill file (SKILL.md, LEARNED.md, INJECT.md, references/, scripts/)
2. Adding corrections, preferences, or discovered conventions to any skill's LEARNED.md
3. Creating or modifying skill directory structure under `.data/skills/`
4. Resolving ambiguity about where content belongs (SKILL.md vs LEARNED.md vs references/)
5. Cross-skill coordination — rules that affect multiple domain skills
6. Creating new skills, scaffolding skill directories, or reviewing skill structure

## Do NOT Use

- **Domain-specific code changes** (Python modules, UI components) — use [backendEngineer](../backendEngineer/SKILL.md) or [frontendEngineer](../frontendEngineer/SKILL.md)
- **Infrastructure/CI/CD tasks** (Docker, workflows, pre-commit) — use [devopsEngineer](../devopsEngineer/SKILL.md)
- **Application logic** (CLI commands, backend integrations, testing) — use the appropriate domain skill

## Architecture

`.data/skills/` is the single source of truth — run `ls .data/skills/` for the live roster
(10 at last count; don't hardcode the list here, it goes stale). `skillnir install` symlinks each
into every tool dotdir (`.claude/skills/`, `.cursor/skills/`, ...). AI tools read
SKILL.md on activation; LEARNED.md is read first for overrides; INJECT.md is
always loaded as a firewall. Full directory tree and data flow:
[references/architecture-guide.md](references/architecture-guide.md).

## Rules

Authoritative rule set — each stated once here. The Anti-Patterns table below
mirrors these as "what not to do".

| Rule                     | Value / How                                                              | Why                                                                        |
| ------------------------ | ------------------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Read before edit         | Read a skill's SKILL.md before modifying any file in its directory       | Miss ownership rules and content-placement instructions otherwise          |
| LEARNED.md for learnings  | Corrections, preferences, conventions go to LEARNED.md — never SKILL.md   | SKILL.md is regenerated; learnings written elsewhere are lost              |
| SKILL.md is generated    | Never hand-edit SKILL.md; regenerate via the generator                   | Regeneration overwrites manual edits silently                             |
| Code in references only  | Code blocks >5 lines live in `references/`, never SKILL.md                | Keeps SKILL.md within the ≤300-line / <3,500-token activation budget       |
| One rule per LEARNED entry | Each LEARNED.md entry is one atomic, date-stamped rule                  | Atomic entries stay scannable and selectively applicable                   |
| Date format in LEARNED   | Use `- YYYY-MM-DD: rule` — not `Mar 21` or `03/21/2026`                   | Sortable, unambiguous across locales                                       |
| Check LEARNED.md first   | On ambiguity, read LEARNED.md before asking the user                     | A prior session may already have answered — avoids repeat questions        |
| Announce activation      | Say "Using: skillnir skill" at the start of any response using a skill    | Signals which rule set is active to the user                              |
| Skill dir naming         | `camelCase` matching existing skills (e.g. `backendEngineer`)            | Injector and discovery assume camelCase; snake_case breaks lookups         |
| Reference file naming    | Lowercase-hyphen: `code-style.md`, `api-patterns.md`                     | Consistent, predictable links from SKILL.md                                |
| Script naming            | `validate-{{scope}}.sh` with `set -euo pipefail`                         | Uniform validators; strict mode surfaces failures instead of masking them  |
| Minimum references       | At least 5 reference files per skill                                      | Quality gate — forces progressive disclosure out of SKILL.md               |
| Symlink pattern          | Relative: `../../.data/skills/{{name}}` from dotdirs                      | Absolute paths break when the repo moves; source of truth stays single     |
| Agent ↔ agents/ sync     | `Agent` in `allowed-tools` iff an `agents/` directory exists             | Advertising a tool with no definitions (or vice versa) misroutes tasks     |

See [references/code-style.md](references/code-style.md) for full formatting
conventions and [references/cross-skill-rules.md](references/cross-skill-rules.md)
for routing between domain skills.

## File Ownership

| File                   | Purpose                                                | Who Edits                            |
| ---------------------- | ------------------------------------------------------ | ------------------------------------ |
| SKILL.md               | Generated skill definition — decision guide            | Skill generator only                 |
| LEARNED.md             | Session-accumulated corrections and preferences        | AI writes during sessions            |
| INJECT.md              | Always-loaded quick reference (hallucination firewall) | AI updates when hallucinations recur |
| references/\*.md       | Detailed documentation, code examples                  | Skill generator or AI when extending |
| scripts/validate-\*.sh | Convention validation scripts                          | Skill generator or DevOps            |
| agents/\*.md           | Sub-agent definitions (role, triggers, tools)          | Skill generator creates              |
| assets/\*              | Copy-as-is config boilerplate                          | Skill generator or DevOps            |

See [references/skill-file-guide.md](references/skill-file-guide.md) for complete file system documentation with token budgets.

## Common Recipes

1. **Add a LEARNED.md entry**: pick the skill → its LEARNED.md → right section (Corrections/Preferences/Discovered Conventions) → `- YYYY-MM-DD: single rule`
2. **Create a new skill**: `mkdir -p .data/skills/{{name}}/{references,scripts}` → SKILL.md + frontmatter → INJECT.md (≤150 tok) → LEARNED.md template → ≥5 references → `validate-{{scope}}.sh` → `skillnir install`
3. **Route content**: learning → LEARNED.md; quick fact → INJECT.md; code → references/; decision rule → SKILL.md (via generator only)
4. **Resolve ambiguity**: route by file pattern ([references/cross-skill-rules.md](references/cross-skill-rules.md)) → still unclear, ask ONE question → record decision in LEARNED.md
5. **Update INJECT.md**: replace stale facts → verify ≤150 tokens → keep the LEARNED.md reference
6. **Add a reference file**: hyphenated name in `references/` → link it in the References table → code gets language tags

## Anti-Patterns

| Anti-Pattern                                        | Why It's Wrong                                                         |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| Writing preferences to / hand-editing SKILL.md      | SKILL.md is generated; regeneration overwrites edits — use LEARNED.md   |
| Editing skill files without reading SKILL.md first  | Miss content-placement and file-ownership rules                        |
| Putting code >5 lines in SKILL.md                   | Blows the ≤300-line / <3,500-token budget — code goes in references/   |
| Skipping LEARNED.md check on ambiguity              | May repeat a question a prior session already answered                 |
| Mixing multiple rules in one LEARNED.md entry       | Makes entries hard to scan and apply selectively                       |
| Wrong date format in LEARNED.md                     | Use `YYYY-MM-DD`, not `Mar 21` or `03/21/2026`                         |
| Adding `Agent` to allowed-tools without agents/     | `Agent` in allowed-tools ↔ agents/ directory must be in sync           |
| INJECT.md exceeding 150 tokens                      | Consumes context budget every response — keep minimal                  |
| Recording domain conventions in skillnir LEARNED.md | Domain learnings belong in the domain skill's LEARNED.md               |

## Communication Style

- **Lead with the answer** — no preamble, no "Let me explain", no "Great question"
- **Strip filler words** — drop "basically", "essentially", "actually", "just", "simply"
- **No trailing summaries** — the user can read the diff; don't restate what you did
- **Bullet points over paragraphs** — lists, tables, one-liners
- **Show the fix, not a lecture** about the fix
- **Max 2-3 sentences** per explanation unless the user asks "why" or is in Teaching mode
- **No hedging, no apologies** — say "do X", fix mistakes silently

## Session Protocols

| Mode       | Detection signal                                                   | Behavior                          |
| ---------- | ------------------------------------------------------------------ | --------------------------------- |
| Teaching   | "where does this go", "what is LEARNED.md for", first encounter    | Explain first, then act           |
| Efficient  | "add to LEARNED.md", "new skill like X", Nth repeat of a pattern   | Apply conventions directly, write |
| Diagnostic | "wrong file", "lost my changes", "overwritten", "broken skill"     | Diagnose which file/why first     |

Default to Teaching when uncertain; a developer override always wins.

**Self-learning (non-negotiable, always written — never merely suggested):**

- **On correction**: acknowledge, restate as a rule, apply for the session, write under `## Corrections`.
- **On undocumented convention**: check LEARNED.md → project files → ask ONE question, write under `## Preferences`.
- **On discovered implicit convention**: state it, write under `## Discovered Conventions`.
- Entry format: `- YYYY-MM-DD: rule`. Deeper guidance: [references/ai-interaction-guide.md](references/ai-interaction-guide.md).

## Freedom Levels

| Level             | Scope                                                                                       | Examples                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **MUST** follow   | File ownership, LEARNED.md format, read-before-edit, announcement rule, SKILL.md ≤300 lines | "MUST write preferences to LEARNED.md", "MUST announce skill activation" |
| **SHOULD** follow | Minimum 5 references, validation scripts, cross-skill routing table                         | "SHOULD have a validate-\*.sh script", "SHOULD route by file pattern"    |
| **CAN** customize | Reference file organization, INJECT.md exact wording, LEARNED.md entry phrasing             | "CAN organize references by topic or alphabetically"                     |

## References

| File                                                                     | Description                                                                  |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions across sessions      |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)                       |
| [references/skill-file-guide.md](references/skill-file-guide.md)         | Complete skill file system documentation with token budgets and examples     |
| [references/cross-skill-rules.md](references/cross-skill-rules.md)       | Skill interaction, priority, delegation, and routing rules                   |
| [references/code-style.md](references/code-style.md)                     | Formatting conventions for all skill files (SKILL.md, LEARNED.md, INJECT.md) |
| [references/security-checklist.md](references/security-checklist.md)     | Skill system security verification checklists                                |
| [references/common-issues.md](references/common-issues.md)               | Troubleshooting common skill system problems                                 |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols                             |
| [scripts/validate-skill-system.sh](scripts/validate-skill-system.sh)     | Skill directory structure and convention validator                           |
