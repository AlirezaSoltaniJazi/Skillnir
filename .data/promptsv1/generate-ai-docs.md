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

---

## PHASE 3: GENERATE DOCUMENTS

### OUTPUT 1: `agents.md`

**Tone**: Direct, specific, zero fluff. No "This project is..." intros.
**Length**: 150-400 lines. Useful enough for productivity, short enough for context windows.
**Format**: GitHub-flavored Markdown.

```markdown
# {{Project Name}} — AI Agent Context

## What This Is

{{1-3 direct sentences: what it does, who uses it, core technology. No preamble.}}

## Stack

{{Concise table or list: language, framework, DB, cache, queue, key libraries}}

## Project Structure

{{Only directories/files that matter — annotated}}
src/
├── api/ # Route handlers — one file per resource
├── models/ # ORM models
├── services/ # Business logic — keep fat, views thin
├── tasks/ # Async tasks
└── core/ # Shared utilities, base classes, constants

## How To Run

{{Exact commands. No ambiguity.}}

# Install

make install

# Dev server

make dev

# Tests

make test

# Lint

make lint

## Development Conventions

### Code Style

{{Exact rules: type hints required? docstring format? line length? formatter?}}

### Naming Conventions

{{Specific: models = PascalCase, services = snake_case, etc.}}

### Import Order

{{If non-standard or enforced}}

### Error Handling

{{How errors propagate: custom exceptions? middleware? result types?}}

## Architecture Rules

{{3-7 most important architectural decisions an AI must respect}}

- "Never put business logic in views. Services layer only."
- "All DB queries through repository pattern."
- "Celery tasks must be idempotent."

## Files To Know

| File               | Purpose                       |
| ------------------ | ----------------------------- |
| config/settings.py | All env-driven config         |
| src/api/router.py  | Register new endpoints here   |
| src/models/base.py | Base model all others inherit |

## Files To Never Touch

- migrations/ — auto-generated, never edit manually
- src/generated/ — codegen output

## Common Patterns

{{2-5 recurring patterns with minimal copy-paste examples}}

### Adding a new API endpoint

{{code snippet using project's actual conventions}}

### Adding a new model

{{code snippet}}

## Environment Variables

{{Key vars from .env.example with descriptions}}

## External Services

{{What the app connects to, local mock/stub strategy}}

## Testing

{{Organization, what to run, factories/fixtures}}

## Known Gotchas

{{AI-trap list from Phase 2d — non-obvious things causing mistakes}}

- "X.py and Y.py must always be updated together"
- "Never import from internal/ — use public API in **init**.py"
- "User model is in auth service — don't add fields here"

## Freedom Levels

| MUST follow                | SHOULD follow          | CAN customize                 |
| -------------------------- | ---------------------- | ----------------------------- |
| {{file structure, naming}} | {{preferred patterns}} | {{impl details, lib choices}} |

## AI Interaction Guidelines

{{If the project has skills with adaptive protocols, summarize the key interaction patterns here}}

- **Interaction modes**: Teaching (conceptual questions, first encounters) · Efficient (repeated patterns, "just generate") · Diagnostic (errors, failures, tracebacks)
- **On correction**: AI restates as rule, applies consistently for the session, suggests persisting to CLAUDE.md
- **On ambiguity**: Check project files first, ask ONE question, apply consistently
- **Adaptive**: Proficiency calibration (silent depth adjustment) · Convention surfacing · Memory bridge (persist learnings)

## Skills Reference

{{If .data/skills/ or .cursor/skills/ exist}}

> Project-specific conventions live in `.data/skills/`. Check before making architectural decisions.
> Skills available: {{list skill names}}

## Sub-Agent Capabilities

{{If any installed skills define sub-agents in agents/ directories}}

> Some skills support sub-agent delegation for complex workflows.
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

- [ ] `agents.md` is 150-400 lines (not a wall, not a stub)
- [ ] Every code snippet is correct for this project's language/framework
- [ ] "Known Gotchas" has at least 3 real project-specific items
- [ ] Common Patterns section has working, copy-pasteable examples
- [ ] `INJECT.md` is under 150 tokens
- [ ] Symlinks created and verified (`cat .claude/claude.md`)
- [ ] No generic filler ("follows best practices") — everything is specific
- [ ] Skills directory referenced if it exists
- [ ] Freedom levels section populated
- [ ] `.github/copilot-instructions.md` symlink created
- [ ] AI Interaction Guidelines section present (if project has adaptive skills)
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
