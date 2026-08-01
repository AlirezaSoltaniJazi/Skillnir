# AI Context Document Generator

Generate `agents.md`, `.claude/claude.md`, and companion files that make any project instantly productive for AI coding assistants (Claude Code, Cursor, Copilot, Gemini CLI, Codex, Windsurf, Cline, Aider).

---

## OUTPUT FILES

```
project-root/
├── agents.md              <- Source of truth (GitHub-rendered, universal AI-agent standard)
├── INJECT.md              <- Always-loaded summary (50-150 tokens, hallucination firewall)
├── .claude/
│   └── claude.md          <- Symlink -> ../agents.md (Claude Code auto-loads)
├── .github/
│   └── copilot-instructions.md  <- Symlink -> ../agents.md (Copilot auto-loads)
└── .data/
    └── skills/            <- Skill directory (referenced in agents.md if present)
```

**Symlink strategy**: `agents.md` is the single source of truth. Tool-specific entry points symlink to it. One file, zero drift.

---

## PHASE 1: PRE-FLIGHT — Read Before Writing

### 1a. Check for existing skills

```
Search in order:
1. .data/skills/               (project-local)
2. .data/skills/*/SKILL.md     (installed skills)
3. .cursor/skills/             (Cursor skills)
4. .agents/skills/             (universal skills)
5. .data/skills/*/agents/     (sub-agent definitions)
```

Extract: coding conventions, framework patterns, vocabulary, tool preferences.
**Use skill content to make generated docs MORE specific, not generic.**

### 1b. Check for existing AI context

```
Look for: CLAUDE.md, claude.md, agents.md, AGENTS.md, .cursorrules,
.cursor/rules/*.mdc, .github/copilot-instructions.md, GEMINI.md, AI_CONTEXT.md
```

If found: extract content as signal, then replace/update.

### 1c. Read standard project files

```
README.md, requirements.txt / pyproject.toml / package.json / Cargo.toml / go.mod,
Makefile / justfile, docker-compose.yml, .env.example, CONTRIBUTING.md,
openapi.yaml / swagger.json
```

---

## PHASE 2: PROJECT DEEP SCAN

Focus on **patterns**, not exhaustive listings.

### 2a. Architecture

- What is this project? (API server, CLI, library, monolith, microservice)
- Primary language + framework
- Entry points (main.py, manage.py, cmd/, src/main.rs)
- Key directories and what lives in each
- External services (DB, cache, queue, storage, auth)

### 2b. Code patterns (sample 3-5 representative files)

- Naming conventions (snake_case, camelCase, PascalCase — where)
- Import style (absolute vs relative, grouping)
- Error handling approach
- Test structure and execution
- Logging patterns + config/settings management

### 2c. Developer workflow

- Run locally (from Makefile, README, docker-compose)
- Run tests, lint/format
- Pre-commit hooks + branch/PR conventions

### 2d. AI-gotcha scan

- Custom abstractions overriding stdlib behavior
- Files that must be edited together (always update X and Y)
- Generated files — NEVER edit manually
- Unusual encoding or templating
- Monkeypatching/metaprogramming changing runtime behavior
- "Don't touch" zones

### 2e. LEARNED.md scan

If `.data/skills/*/LEARNED.md` files exist with non-empty content, extract corrections, preferences, and discovered conventions. These represent accumulated team knowledge from prior AI sessions and should inform the generated docs.

---

## PHASE 3: GENERATE DOCUMENTS

### OUTPUT 1: `agents.md`

**Tone**: Direct, specific, zero fluff. No "This project is..." intros.
**Length**: **≤150 lines target, 250 lines absolute max.** Empirical studies (ETH Zurich AGENTbench, 2026) show long LLM-generated context files REDUCE agent task success while raising cost 20%+ — the fastest way to improve a context file is to delete from it.
**Format**: GitHub-flavored Markdown.

**The one test every line must pass**: could a competent agent infer this by reading the code for 30 seconds? If yes, OMIT it. Context files earn their tokens with NON-INFERABLE knowledge only: exact commands, boundaries, cross-file coupling, don't-touch zones, and conventions no amount of code-reading reveals.

**Ordering is load-bearing**: models weight the start and end of context most (lost-in-the-middle). Commands, boundaries, and gotchas go FIRST; reference material goes last; nothing critical sits in the middle.

```markdown
# {{Project Name}} — AI Agent Context

## What This Is

{{1-2 direct sentences: what it does, core technology. No preamble.}}

## How To Run

{{Exact commands with flags — install, dev server, tests, single-test, lint.
No ambiguity, no alternatives. This is the #1 thing agents get wrong without help.}}

## Boundaries

| Always do                               | Ask first                            | Never do                        |
| --------------------------------------- | ------------------------------------ | ------------------------------- |
| {{e.g. run make lint before finishing}} | {{e.g. schema migrations, new deps}} | {{e.g. edit migrations/, push}} |

## Known Gotchas

{{The AI-trap list from Phase 2d — the highest-value section in this file.
At least 3 real, project-specific traps with file paths. Each one is something
that WILL cause a wrong edit if unknown:}}

- "X.py and Y.py must always be updated together"
- "Never import from internal/ — use the public API in **init**.py"
- "SKILL.md files are generated — never edit manually"

## Stack

{{One line or a compact table: language + framework + DB + the 2-3 libraries
whose choice isn't obvious from the manifest.}}

## Project Structure

{{ONLY directories an agent would misjudge — annotated with the non-obvious
purpose. Skip anything a directory listing already explains.}}

## Development Conventions

{{ONLY enforced or non-obvious rules: formatter + exact flags, import style if
policed, naming where it deviates from language defaults, error-handling
pattern if the codebase has a strong one. State the WHY in one clause when a
rule would surprise ("Black -S — respect existing quote style, don't mass-convert").
Skip anything the linter config already encodes unless agents keep violating it.}}

## Architecture Rules

{{3-5 decisions an agent must respect, each with its one-clause WHY:}}

- "Never put business logic in views — services layer only (views are tested shallowly)."
- "All DB access through the repository pattern (raw queries break the audit hooks)."

## Files To Know

| File               | Purpose                     |
| ------------------ | --------------------------- |
| config/settings.py | All env-driven config       |
| src/api/router.py  | Register new endpoints here |

## Files To Never Touch

- migrations/ — auto-generated, never edit manually
- src/generated/ — codegen output

## Common Patterns

{{1-2 recurring patterns MAX, minimal copy-paste examples, ONLY where the
project's idiom differs from the framework default. Generic framework usage
does not belong here.}}

## Environment & External Services

{{Key env vars from .env.example with one-line descriptions; what the app
connects to and the local mock/stub strategy. Compact — merge into one section.}}

## Testing

{{Organization, how to run one test, factories/fixtures location. Commands only
if they differ from How To Run.}}

## Security

{{ONLY project-specific rules: secrets management approach, input-validation
choke points, auth pattern. No generic OWASP advice.}}

## Freedom Levels

| MUST follow                | SHOULD follow          | CAN customize                 |
| -------------------------- | ---------------------- | ----------------------------- |
| {{file structure, naming}} | {{preferred patterns}} | {{impl details, lib choices}} |

## AI Interaction Guidelines

{{Only if the project has skills with Session Protocols — 3 compact bullets:}}

- **Modes**: Teaching (conceptual, first encounters) · Efficient (repeated patterns) · Diagnostic (errors, tracebacks)
- **On correction**: restate as a rule, apply for the session, write to the skill's LEARNED.md
- **On ambiguity**: check LEARNED.md, then project files, then ask ONE question

## Skills Reference

{{If .data/skills/ or .cursor/skills/ exist}}

> Project-specific conventions live in `.data/skills/`. Check before making architectural decisions.
> Skills available: {{list skill names}}

## Sub-Agent Capabilities

{{If any installed skills define sub-agents in agents/ directories}}

> Skills with sub-agents: {{list skill names that have agents/ subdirectories}}
> Ensure `Agent` is in allowed-tools when using these skills.
```

---

### OUTPUT 2: `INJECT.md`

Always-loaded summary (50-150 tokens). Acts as hallucination firewall.

```markdown
# {{Project Name}} — Quick Reference

- **Stack**: {{language + framework + DB + key libs}}
- **Entry points**: {{main files}}
- **Key dirs**: {{annotated 3-5 directories}}
- **Run**: `make dev` / `make test` / `make lint`
- **Patterns**: {{3-5 bullet pattern summary}}
- **Never**: {{2-3 critical anti-patterns or gotchas}}
- **Full context**: See [agents.md](agents.md)
```

---

### OUTPUT 3: Symlinks

```bash
# Claude Code
mkdir -p .claude
ln -sf ../agents.md .claude/claude.md

# GitHub Copilot
mkdir -p .github
ln -sf ../agents.md .github/copilot-instructions.md
```

If symlinks unsupported (Windows, certain CI), create copies with header:

```markdown
<!-- Mirrors agents.md. Prefer symlink: ln -sf ../agents.md .claude/claude.md -->
```

---

## PHASE 4: QUALITY CHECKS

- [ ] `agents.md` is ≤150 lines (250 absolute max) — if over, DELETE inferable content before anything else
- [ ] How To Run, Boundaries, and Known Gotchas are the first three content sections — nothing critical buried mid-file
- [ ] "Known Gotchas" has at least 3 real project-specific traps with file paths
- [ ] Zero lines an agent could infer by reading the code — no restated directory listings, no generic conventions, no framework tutorials
- [ ] Every surprising MUST/Never rule carries its one-clause WHY
- [ ] Every code snippet is correct for this project's language/framework
- [ ] `INJECT.md` is under 150 tokens
- [ ] Symlinks created and verified (`cat .claude/claude.md`)
- [ ] No generic filler ("follows best practices") — everything is specific
- [ ] Skills directory referenced if it exists
- [ ] Freedom levels section populated
- [ ] `.github/copilot-instructions.md` symlink created
- [ ] AI Interaction Guidelines section present (if project has skills with Session Protocols)
- [ ] Sub-Agent Capabilities section present if any skills have `agents/` subdirectories

---

## EXECUTION ORDER

```
[ ] 1. Read .data/skills/ + .cursor/skills/ — extract conventions
[ ] 2. Check for existing AI context files (CLAUDE.md, agents.md, .cursorrules, etc.)
[ ] 3. Read README, dependency files, Makefile
[ ] 4. Scan project structure (architecture)
[ ] 5. Sample 3-5 core files (patterns)
[ ] 6. Identify AI gotchas (non-obvious traps)
[ ] 7. Write agents.md to project root
[ ] 8. Write INJECT.md to project root
[ ] 9. Create .claude/ symlink
[ ] 10. Create .github/copilot-instructions.md symlink
[ ] 11. Verify symlinks: cat .claude/claude.md && cat .github/copilot-instructions.md
[ ] 12. Quality check all items above
```
