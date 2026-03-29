# Base: Skill Generator Scaffold

> **This file is referenced by all domain-specific skill generators.**
> Domain prompts supply: ROLE, scan checklist, synthesis categories, best practices, body sections, and suggested files.
> This file supplies: directory structure, frontmatter schema, output rules, quality gates, execution order, sub-agent delegation, and cross-tool guidance.

---

## OUTPUT STRUCTURE

Generate a complete skill directory — not a single file:

```
{{skill-name}}/
├── SKILL.md            # Decision guide — tables, rules, checklists, links. No code blocks >5 lines
├── INJECT.md           # Always-loaded summary (50-150 tokens) — key imports, file map, pattern cheat-sheet
├── LEARNED.md          # Auto-updated by AI — corrections, preferences, conventions accumulate here
├── agents/             # Sub-agent definitions (skip if skill has no delegation needs)
│   └── {{agent-name}}.md
├── references/         # Detailed guides, full code templates, troubleshooting
│   ├── architecture-guide.md
│   ├── {{pattern}}-patterns.md
│   ├── common-issues.md
│   └── {{name}}-template.{{ext}}
├── assets/             # Copy-as-is config files and boilerplate (skip if nothing qualifies)
│   └── {{config}}-example.{{ext}}
└── scripts/            # Validation and automation (skip only if no checkable conventions)
    └── validate-{{scope}}.sh
```

### Placement Rules

| Artifact    | Rule                                                                                                                                                                                                      |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SKILL.md    | **≤300 lines / <3,500 tokens.** Tables, rules, checklists, links only. **No code blocks >5 lines** — move them to references/. Must instruct AI to read LEARNED.md first.                                 |
| INJECT.md   | 50-150 tokens. Always loaded by AI tools. Key imports, directory map, 5-7 bullet pattern summary                                                                                                          |
| LEARNED.md  | Auto-updated by AI. Starts with header template. Sections: Corrections, Preferences, Discovered Conventions. Entries use `- YYYY-MM-DD: rule` format.                                                     |
| agents/     | One `.md` file per sub-agent. Each contains: role, tools, spawn conditions, context template, result format, weaknesses. **Skip this directory entirely if the skill has no sub-agent delegation needs.** |
| references/ | **ALL code blocks >5 lines.** Detailed guides, full templates, troubleshooting. Loaded on demand when referenced                                                                                          |
| assets/     | Config/boilerplate users copy verbatim                                                                                                                                                                    |
| scripts/    | At least one `validate-*.sh` checking naming/structure conventions                                                                                                                                        |

SKILL.md links to references/ with relative paths: `[architecture guide](references/architecture-guide.md)`

---

## FRONTMATTER SCHEMA

```yaml
---
name: { { provided-by-user } }
description: >-
  {{domain-prompt supplies this — must trigger for ANY task in this domain}}
compatibility: "{{detected stack + versions}}"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: { { development|testing|deployment } }
allowed-tools:
  {
    {
      domain-prompt supplies — e.g.,
      Read Edit Write Bash(python:*) Glob Grep Agent,
    },
  }
# sub-agents:                    # Optional — only when delegation is warranted
#   - name: {{agent-name}}
#     file: agents/{{agent-name}}.md
---
```

| Field                 | Required | Notes                                                                                                                          |
| --------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `name`                | Yes      | Max 64 chars, lowercase, hyphens only                                                                                          |
| `description`         | Yes      | Max 1024 chars. Third person. Include WHAT + WHEN + trigger terms                                                              |
| `compatibility`       | Yes      | Detected language, framework, key library versions                                                                             |
| `metadata.author`     | Yes      | Always `skillnir`                                                                                                              |
| `metadata.version`    | Yes      | Semver string                                                                                                                  |
| `metadata.sdlc-phase` | Yes      | Which SDLC phase this skill covers                                                                                             |
| `allowed-tools`       | Yes      | Space-separated tool list. Use platform-specific scoping where possible. **Include `Agent` only when `sub-agents` is defined** |
| `sub-agents`          | No       | List of sub-agent definitions. When present, `Agent` MUST be in `allowed-tools`                                                |

---

## INJECT.md PATTERN

Generate an INJECT.md companion alongside SKILL.md. This file is always loaded into context (costs 50-150 tokens) and serves as a hallucination firewall.

Template:

```markdown
# {{Skill Name}} — Quick Reference

- **Stack**: {{language}} + {{framework}} + {{key libs}}
- **Entry points**: {{main files}}
- **Key directories**: {{annotated 3-5 dirs}}
- **Patterns**: {{3-5 bullet pattern summary}}
- **Never**: {{2-3 critical anti-patterns}}
- **Sub-agents**: {{agent names or "none"}} — see [agents/](agents/) for delegation rules
- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Self-learning**: On correction -> write to LEARNED.md. On ambiguity -> check LEARNED.md first. On convention discovery -> write to LEARNED.md.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
```

---

## QUALITY GATES

- Every code example must reference an actual file path from the project (CONFIRMED) or be explicitly marked INFERRED
- Concrete and project-specific — zero generic advice ("write clean code", "follow best practices")
- Opinionated — make clear decisions, don't hedge with "you could also..."
- Written as if from a senior engineer who works in this codebase daily
- Phase 3 best practices SHOULD be **numbered by priority** (1 = highest) — this communicates trade-off ordering to the consuming AI when resources or time are limited
- SKILL.md **≤300 lines and <3,500 tokens** — no code blocks >5 lines
- At least **5 reference files** generated (must include: code-style, security-checklist, patterns, common-issues)
- Generated SKILL.md MUST include an announcement rule in "Before You Start": **Always say "Using: {{Skill Name}} skill" at the very start of the response before doing any work.**
- Generated skill MUST include an "Adaptive Interaction Protocols" section with self-learning via LEARNED.md
- Generated skill MUST include a LEARNED.md template with Corrections, Preferences, and Discovered Conventions sections
- If `agents/` exists, each agent file MUST follow the agent definition template (Role, When to Spawn, Tools, Context Template, Result Format, Weaknesses)
- `Agent` is in `allowed-tools` if and only if `agents/` is non-empty
- Sub-agent count MUST NOT exceed 4
- Each agent definition MUST include a Weaknesses section (improves routing accuracy)

---

## PROGRESSIVE DISCLOSURE RULES

SKILL.md is a **decision guide** — it tells the AI WHAT to do and WHEN. References tell HOW with full code examples. This separation is critical: SKILL.md is loaded on activation (~3,500 tokens budget), references are loaded on demand (unlimited).

**What STAYS in SKILL.md** (activation phase):

- Tables (pattern summaries, style rules, anti-patterns, freedom levels)
- Numbered rule lists (code generation rules, debugging steps, recipes as step lists)
- Checklists (code review, security summary)
- One-liner code snippets only (≤5 lines)
- Links to references/ for everything else
- Sub-agent delegation table (name, role, spawn trigger — minimal)

**What MOVES to references/** (on-demand phase):

- Code blocks >5 lines (ViewSet examples, serializer examples, model templates)
- Import order examples, transaction pattern examples
- Detailed security verification checklists (per-component)
- Research citations and detailed anti-pattern explanations
- Full test examples with setup/teardown
- **Priority-based decision tables** — when multiple approaches exist, rank them in a numbered fallback hierarchy (e.g., locator strategies, caching strategies, error handling approaches) rather than flat unordered lists

**What MOVES to agents/** (on-delegation phase):

- Full sub-agent definitions (role, tools, context template, result format, weaknesses)
- Loaded only when the AI decides to delegate a task

**Required reference files** (every generated skill MUST include at minimum):

- `references/{{domain}}-patterns.md` — full code examples for key patterns
- `references/code-style.md` — imports, formatting, naming with code examples
- `references/security-checklist.md` — per-component verification checklists, classified by **severity** (Critical/High/Medium/Low) and referencing relevant **OWASP category** where applicable
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/common-issues.md` — troubleshooting with code fixes
- `references/{{name}}-template.{{ext}}` — copy-paste boilerplate in project language

---

## FREEDOM LEVELS

In the generated SKILL.md, include a section declaring:

| Level             | Scope                                                                                                                                                                                      | Examples                                                                                                                      |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------- |
| **MUST** follow   | File structure, naming conventions, error patterns, imports, adaptive interaction protocols (all 7 subsections), correction accumulation, sub-agent delegation rules (when agents/ exists) | "Models MUST extend BaseModel", "MUST include Correction Accumulation protocol", "MUST pass context explicitly to sub-agents" |
| **SHOULD** follow | Preferred patterns with acceptable variation, domain-specific detection signals for interaction modes, sub-agent spawn triggers                                                            | "SHOULD use repository pattern", "SHOULD delegate security scans to security-scanner sub-agent"                               |
| **CAN** customize | Implementation details, library choices, adaptive protocol thresholds, proficiency calibration sensitivity, sub-agent tool sets                                                            | "CAN choose caching strategy", "CAN adjust anti-dependency threshold (default: 3)", "CAN add domain-specific sub-agents"      |

---

## ADAPTIVE INTERACTION PROTOCOLS

The generated SKILL.md MUST include an "Adaptive Interaction Protocols" section. This section teaches the AI consuming the skill how to adapt its behavior during a session. All tracking operates within the context window — no persistent state required.

Include ALL of the following subsections:

### 1. Interaction Modes (required)

Generate a table with three modes: **Teaching**, **Efficient**, **Diagnostic**. Each mode MUST have:

- **Concrete detection signals** — not vague triggers like "select based on context". Use observable signals: "what is...", "how does..." for Teaching; "another one like X", Nth instance for Efficient; tracebacks, error messages for Diagnostic.
- **Specific behavior** — explain first vs. generate directly vs. diagnose first.
- Default to Teaching when uncertain. Allow explicit developer override.

### 2. Correction Accumulation (required)

Instruct the AI to follow this protocol when the developer corrects generated output:

1. Acknowledge the specific mistake
2. Restate the correction as a rule (e.g., "Understood: always use X not Y in this project")
3. Apply the correction to ALL subsequent outputs in the session
4. **Write the correction to LEARNED.md** under `## Corrections` with today's date (format: `- YYYY-MM-DD: rule`)

### 3. Preference Elicitation (required)

When encountering an undocumented convention for the first time:

1. Check LEARNED.md first, then project files (`CLAUDE.md`, `agents.md`, existing code)
2. Ask ONE targeted question — not a list of options
3. Apply the answer consistently for the session remainder
4. **Write the preference to LEARNED.md** under `## Preferences` with today's date

### 4. Proficiency Calibration (required)

Generate a two-row table with signal types **Senior** and **Learning**:

- **Senior indicators**: modifies generated code, asks architectural questions, references framework internals, questions trade-offs → Reduce boilerplate explanations, lead with code, rationale on non-obvious only
- **Learning indicators**: asks "what is...", copies code unchanged, pastes errors without analysis → Use Teaching mode more often, add context for why not just how, link to docs

Never announce the calibration or be condescending. Adjust silently.

### 5. Anti-Dependency Guardrails (required)

Prevent over-reliance on generation:

- After 3+ similar generations in a session, suggest creating a project template or snippet
- In Teaching mode, offer "try writing it yourself first — I'll review" before generating
- Reference official documentation for deeper learning when explaining patterns

### 6. Convention Surfacing (required)

When discovering an implicit project convention through code analysis:

1. State the convention explicitly before using it
2. If uncertain, ask for confirmation before applying
3. **Write confirmed conventions to LEARNED.md** under `## Discovered Conventions` with today's date

### 7. Self-Learning via LEARNED.md (required)

All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections -> `## Corrections` section
- Preferences -> `## Preferences` section
- Discovered conventions -> `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`
- The SKILL.md must instruct: "Read LEARNED.md first before generating code"
- LEARNED.md starts with a header template and empty sections — the AI fills them over time

---

## SUB-AGENT DELEGATION

When the project warrants it, the generated skill can define sub-agents that the consuming AI spawns via the `Agent` tool. Sub-agents provide context isolation, security boundaries, and parallel execution for complex workflows.

### When to Delegate (decision table)

| Delegate to Sub-Agent                                          | Stay Inline                                           |
| -------------------------------------------------------------- | ----------------------------------------------------- |
| Task has 2+ distinct phases with different tool needs          | Task is simple, single-focus                          |
| Security isolation needed (read-only analysis vs write access) | Entire conversation history is critical for decisions |
| Main context window approaching limits                         | Task has deep interdependencies between steps         |
| Parallel work streams with no dependencies                     | Frequent back-and-forth with parent needed            |
| Specialized domain knowledge benefits from focused context     | Sub-agent would need to spawn its own sub-agents      |

**If none of the "Delegate" conditions apply, skip the agents/ directory entirely.**

### Agent Definition Template

Each sub-agent definition file (`agents/{{name}}.md`) MUST follow this template:

```markdown
# {{Agent Name}}

## Role

{{one-line role description — what this agent does}}

## When to Spawn

{{2-3 specific trigger conditions — observable signals, not vague criteria}}

## Tools

{{space-separated tool list — restrict to MINIMUM needed}}

- Analysis agents: Read Glob Grep (read-only — analysis agents MUST NOT have Edit/Write access)
- Modification agents: Read Edit Write Bash Glob Grep
- Test agents: Read Edit Write Bash Glob Grep

## Context Template

{{what the parent MUST pass in the Agent tool prompt — sub-agents do NOT receive parent conversation history}}
Include:

- Task description (what to do)
- Relevant file paths (where to look)
- Constraints and conventions from SKILL.md (how to do it)
- Output format expectations (what to return)

## Result Format

{{structured format the agent returns in its final message}}

## Weaknesses

{{what this agent should NOT be used for — including weaknesses improves routing accuracy}}
```

### Delegation Rules

1. **Cap at 3-4 sub-agents** per skill — more causes decision overhead and degrades routing accuracy
2. **Use tool restriction strategically** — analysis agents get `Read Glob Grep` (read-only, never Edit/Write), modification agents get `Read Edit Write Bash Glob Grep` (full write). This is the primary security value of sub-agents. Test-writer agents SHOULD include flakiness prevention guidance in their context template (deterministic tests, no shared state, explicit waits over sleeps)
3. **Pass ALL context explicitly** — sub-agents receive their own prompt + project CLAUDE.md files, but do NOT receive parent conversation history, parent skills, or parent system prompt
4. **Only the final message returns** — intermediate tool calls and results stay inside the sub-agent. Design result format accordingly
5. **No recursive sub-agents** — sub-agents CANNOT spawn their own sub-agents (max depth = 1). Design workflows accordingly
6. **Include weaknesses** — stating what an agent should NOT do improves routing accuracy by preventing inappropriate task assignments

### Context Passing Template

When the consuming AI spawns a sub-agent, it should construct the prompt like this:

```
You are the {{agent-name}} sub-agent for the {{skill-name}} skill.

## Your Task
{{specific task description}}

## Context
- Project: {{project path}}
- Files to examine: {{relevant file list}}
- Conventions: {{key rules extracted from SKILL.md — not the entire file}}

## Constraints
{{from SKILL.md freedom levels — MUST/SHOULD rules relevant to this task}}

## Output Format
{{from agent definition result format — be specific about structure}}
```

Keep context prompts **concise** — extract only the relevant SKILL.md rules, not the entire file.

### Result Handling

1. Parse sub-agent result per the defined result format
2. Validate result against quality gates (if applicable)
3. If result is incomplete or unclear, retry with clarified context (max 1 retry)
4. Integrate result into parent workflow

### Sub-Agent Section in SKILL.md

When agents/ exists, the generated SKILL.md MUST include a "Sub-Agent Delegation" section with:

```markdown
## Sub-Agent Delegation

| Agent                          | Role              | Spawn When  | Tools         |
| ------------------------------ | ----------------- | ----------- | ------------- |
| [{{name}}](agents/{{name}}.md) | {{one-line role}} | {{trigger}} | {{tool list}} |

### Delegation Rules

1. Delegate when task has distinct phases or needs security isolation
2. Stay inline for simple, single-focus tasks
3. Cap at 3-4 sub-agents per workflow
4. Pass ALL context explicitly — sub-agents don't see parent conversation
5. Sub-agents CANNOT spawn their own sub-agents (max depth = 1)
```

---

## CROSS-TOOL OUTPUT

When the user prompt specifies cross-tool compatibility, also generate:

- `.agents/skills/{{skill-name}}/SKILL.md` — universal format (Cursor, Claude Code, Codex, Copilot, Aider, Windsurf, Cline)
- Cursor-native: `.cursor/skills/{{skill-name}}/SKILL.md`

Default to Cursor-native unless instructed otherwise.

---

## EXECUTION ORDER

```
[ ] 1. Read reference skill (if provided) for format context
[ ] 2. Create /tmp/skill_analysis_{{domain}}.md (scratchpad — update aggressively, never lose context)
[ ] 3. Deep-scan project — {{domain}} code only (Phase 1)
[ ] 4. Create /tmp/skill_synthesis_{{domain}}.md (Phase 2)
[ ] 5. Integrate best practices for detected stack (Phase 3)
[ ] 6. mkdir -p {{output_dir}}
[ ] 7. Generate references/ files first (architecture guide, patterns, templates)
[ ] 8. Generate assets/ files (if applicable)
[ ] 9. Generate scripts/ files (if applicable)
[ ] 10. Generate agents/ files (if skill warrants sub-agent delegation — evaluate using decision table)
[ ] 11. Generate LEARNED.md template (empty sections: Corrections, Preferences, Discovered Conventions)
[ ] 12. Generate INJECT.md (must reference LEARNED.md and sub-agents if present)
[ ] 13. Generate SKILL.md with links to references/ and agents/ (must instruct "Read LEARNED.md first")
[ ] 14. Quality check: all gates pass? Links valid? SKILL.md ≤300 lines and <3,500 tokens? No code blocks >5 lines? LEARNED.md template included? At least 5 reference files? Sub-agent definitions valid (if present)?
[ ] 15. Write all files to output location
```

Do NOT skip phases. Do NOT generate until analysis is complete. Every line must reflect this specific project.
