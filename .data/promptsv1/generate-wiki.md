# Project Wiki Generator

Generate a token-efficient project wiki for any codebase: a single `llms.txt`
index at the project root plus a focused `docs/` folder. The wiki is consumed
by AI assistants (Claude Code, Cursor, Copilot, Gemini CLI, Codex, Windsurf,
Cline, Aider) and by humans browsing the repo on GitHub.

The goal: an AI agent opening this project should be able to load `llms.txt`
(2k–10k tokens) and a single relevant `docs/*.md` page (<5k tokens) instead of
crawling source files. This saves 5k–50k tokens per session and lets the agent
land on the right module on the first try.

---

## OUTPUT FILES

```
project-root/
├── llms.txt                  <- Curated AI index (llmstxt.org spec)
└── docs/
    ├── architecture.md       <- Mermaid diagram + key abstractions
    ├── modules.md            <- Table of every module with purpose + entry point
    ├── dataflow.md           <- Main user-facing pipeline(s) traced end-to-end
    ├── extending.md          <- "How do I add X" recipes
    ├── getting-started.md    <- Install, run, test commands
    └── troubleshooting.md    <- Known gotchas, common errors
```

---

## PHASE 1: PRE-FLIGHT — Detect the Stack

Before writing anything, identify the project so generated content matches
reality (no Python-only assumptions on a Rust project).

### 1a. Detect language and framework

Look at (in order, stop when found):

```
pyproject.toml / setup.py        -> Python
package.json                     -> JavaScript/TypeScript (check "dependencies" for framework)
Cargo.toml                       -> Rust
go.mod                           -> Go
pom.xml / build.gradle           -> Java/Kotlin
Gemfile                          -> Ruby
composer.json                    -> PHP
*.csproj / *.sln                 -> C#/.NET
mix.exs                          -> Elixir
```

### 1b. Read existing AI context (do not duplicate it)

```
README.md, agents.md, AGENTS.md, CLAUDE.md, INJECT.md,
.claude/CLAUDE.md, .cursorrules, .cursor/rules/*.mdc,
.github/copilot-instructions.md, .data/skills/*/SKILL.md
```

If found: extract content and refer to it from the wiki rather than
re-stating it. The wiki COMPLEMENTS these; it does not replace them.

### 1c. Standard project files

```
README.md, CHANGELOG.md, CONTRIBUTING.md, LICENSE,
Makefile / justfile / Taskfile.yml, docker-compose.yml, .env.example,
.pre-commit-config.yaml, .github/workflows/*.yml
```

---

## PHASE 2: PROJECT DEEP SCAN

Sample (do not exhaustively read) the codebase to identify:

### 2a. Top-level architecture

- What is this? (CLI, web app, library, service, mobile app, etc.)
- Entry points (main file(s), bin/, cmd/, src/main.\*, package.json "main")
- Top-level source directories and one-line purpose for each
- External dependencies (DB, cache, queue, third-party APIs)
- Key abstractions (3–7 most important — classes, interfaces, protocols)

### 2b. Module map

For every source module/package (cap at ~30 — group by parent if more):

- Path (from project root)
- One-line purpose
- Public entry point (function/class name to start reading from)
- 1–3 key dependencies (other modules it calls)

### 2c. Data flow

Identify the 1–3 main user-facing pipelines. Trace each end-to-end:
who calls what, in what order, with what data shape. Use Mermaid
sequence diagrams where helpful.

### 2d. Extension points

How does someone add a new X to this project? (Where X = whatever the
project lets users extend: route, command, plugin, provider, model, etc.)

### 2e. Gotchas (AI-trap scan)

- Files that must change together
- Generated files (never edit manually)
- Custom abstractions overriding stdlib behavior
- Non-obvious naming conventions
- Anything called out in existing CLAUDE.md / AGENTS.md / INJECT.md

---

## PHASE 3: WRITE THE WIKI

Tone: **direct, specific, grounded in real file paths**. Zero filler.
No "this project is...". No "best practices". Cite paths from your scan.

### OUTPUT 1: `llms.txt` (project root)

Per the [llmstxt.org spec](https://llmstxt.org/). Target: under 10k tokens.

```markdown
# {{Project Name}}

> {{One-paragraph description of what this project does, the stack, and who
> uses it. 2-4 sentences. Token-efficient.}}

## Quick start

- Install: `{{install command}}`
- Run: `{{run command}}`
- Test: `{{test command}}`

## Wiki

- [Architecture](docs/architecture.md) — high-level diagram + key abstractions
- [Modules](docs/modules.md) — table of every module with purpose
- [Data flow](docs/dataflow.md) — main pipelines traced end-to-end
- [Extending](docs/extending.md) — how to add a {{thing-this-project-lets-you-add}}
- [Getting started](docs/getting-started.md) — install, run, test in detail
- [Troubleshooting](docs/troubleshooting.md) — known gotchas

## Modules

{{For every top-level module/package (cap ~30):}}

- [`{{module/path}}`](docs/modules.md#{{anchor}}) — one-line purpose

## Conventions

{{3-7 bullets — language, formatter, line length, naming, testing framework}}

## See also

{{Cross-references to existing AI context if present:}}

- [agents.md](agents.md) — full project context (if exists)
- [INJECT.md](INJECT.md) — quick reference (if exists)
- [CONTRIBUTING.md](CONTRIBUTING.md) — contribution workflow (if exists)
```

### OUTPUT 2: `docs/architecture.md`

```markdown
# Architecture

## Overview

{{1-2 paragraphs: what this is, the dominant pattern (CLI / web app /
service / library), the central abstraction.}}

## High-level diagram

\`\`\`mermaid
{{Mermaid diagram — flowchart or sequence — showing the main components and
how they relate. Keep nodes to 5-10. Label edges with what flows between them.}}
\`\`\`

## Key abstractions

### {{Abstraction 1}}

{{What it is, where it lives (file path), why it exists.}}

### {{Abstraction 2}}

{{...}}

## Key directories

| Directory   | Purpose      |
| ----------- | ------------ |
| `{{path/}}` | {{one-line}} |

## External dependencies

{{What this project talks to: DB, cache, APIs, file system, etc.
For each: protocol, where the integration lives.}}
```

### OUTPUT 3: `docs/modules.md`

```markdown
# Modules

Source-map of every module in the project. Use this to find the right file
to read first for any given concern.

## {{Top-level group 1, e.g. "Core"}}

### `{{module/path}}`

- **Purpose**: {{one line}}
- **Entry point**: `{{function or class name}}`
- **Calls**: {{1-3 dependencies}}
- **Called by**: {{1-3 callers}}

### `{{next module}}`

{{...}}

## {{Top-level group 2, e.g. "UI"}}

{{...}}
```

### OUTPUT 4: `docs/dataflow.md`

```markdown
# Data Flow

The main user-facing pipelines, traced end-to-end.

## Pipeline 1: {{name, e.g. "User signs in"}}

\`\`\`mermaid
sequenceDiagram
{{participants}}
{{messages with file:function references}}
\`\`\`

1. **Entry**: `{{file}}::{{function}}` — what happens, what data
2. **Step 2**: `{{file}}::{{function}}` — ...
3. **...**

## Pipeline 2: {{name}}

{{...}}
```

### OUTPUT 5: `docs/extending.md`

```markdown
# Extending {{Project Name}}

Recipes for the most common ways users extend the project. Each recipe lists
exact files to touch, in order, with minimal code examples drawn from
existing patterns.

## Add a new {{X}}

1. Create `{{file pattern}}` matching the convention from `{{example file}}`
2. Register it in `{{registry file}}` by adding `{{snippet}}`
3. Add a test in `{{tests path}}` mirroring `{{example test}}`
4. Run `{{test command}}` to verify

## Add a new {{Y}}

{{...}}
```

### OUTPUT 6: `docs/getting-started.md`

```markdown
# Getting Started

## Prerequisites

- {{Language version, e.g. Python 3.12+}}
- {{Package manager, e.g. uv, npm, cargo}}
- {{Optional: Docker, system libs, etc.}}

## Install

\`\`\`bash
{{exact install commands}}
\`\`\`

## Run

\`\`\`bash
{{exact run commands}}
\`\`\`

## Test

\`\`\`bash
{{exact test commands}}
\`\`\`

## Lint / format

\`\`\`bash
{{exact lint commands if pre-commit / formatter is configured}}
\`\`\`

## Project layout

{{Tree view — only directories that matter. Annotate each.}}
```

### OUTPUT 7: `docs/troubleshooting.md`

```markdown
# Troubleshooting

## Known gotchas

{{From Phase 2e — non-obvious things that have caused bugs or AI mistakes.
Each entry: one-line symptom, then resolution. Cite file paths.}}

### {{Symptom 1}}

**Cause**: {{...}}
**Fix**: {{...}}

### {{Symptom 2}}

{{...}}

## Files that must change together

{{Pairs/triples of files that must stay in sync. Cite paths.}}

## Generated files (never edit manually)

{{From Phase 2e.}}

## See also

- [Architecture](architecture.md)
- [Modules](modules.md)
- [Extending](extending.md)
```

---

## PHASE 4: QUALITY CHECKS

- [ ] `llms.txt` exists at project root, valid markdown, under 10k tokens
- [ ] `docs/` folder contains all 6 pages
- [ ] Each page is under 5k tokens
- [ ] Every code/path reference cites a real file (no fabrication)
- [ ] Mermaid diagrams parse (no syntax errors)
- [ ] No generic filler ("uses best practices", "modular and clean")
- [ ] Language/framework matches what was detected in Phase 1
- [ ] If existing `agents.md` / `INJECT.md` / `CLAUDE.md` was found, the wiki
      cross-links to them rather than duplicating content
- [ ] `llms.txt` lists every module that has a `docs/modules.md` entry

---

## EXECUTION ORDER

```
[ ] 1. Detect stack (Phase 1a) — adjust all subsequent output to match
[ ] 2. Read existing AI context (Phase 1b) — do not duplicate
[ ] 3. Read standard project files (Phase 1c)
[ ] 4. Scan top-level architecture (Phase 2a)
[ ] 5. Build module map (Phase 2b)
[ ] 6. Trace 1-3 main pipelines (Phase 2c)
[ ] 7. Identify extension points (Phase 2d)
[ ] 8. Note gotchas (Phase 2e)
[ ] 9. Write llms.txt to project root
[ ] 10. mkdir -p docs/
[ ] 11. Write docs/architecture.md
[ ] 12. Write docs/modules.md
[ ] 13. Write docs/dataflow.md
[ ] 14. Write docs/extending.md
[ ] 15. Write docs/getting-started.md
[ ] 16. Write docs/troubleshooting.md
[ ] 17. Quality check all items above
```
