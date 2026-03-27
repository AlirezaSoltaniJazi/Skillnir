---
name: create-skill
description: Guides users through creating effective Agent Skills for Cursor. Use when you want to create, write, or author a new skill, or asks about skill structure, best practices, or SKILL.md format.
---

# Creating Skills in Cursor

> **Disambiguation**: This is a **skill-authoring guide** — it teaches how to write effective skills manually. For generating project-wide system/meta skills automatically, see [`generate-skill-general-system.md`](generate-skill-general-system.md).

Skills are markdown files that teach the agent specific tasks: reviewing PRs, generating commits, querying schemas, or any specialized workflow.

## Before You Begin: Gather Requirements

Gather from the user (or infer from conversation context):

1. **Purpose and scope**: What task or workflow should this skill help with?
2. **Target location**: Personal (`~/.cursor/skills/`) or project (`.cursor/skills/`)?
3. **Trigger scenarios**: When should the agent apply this skill?
4. **Domain knowledge**: What does the agent need that it wouldn't already know?
5. **Output format**: Specific templates, formats, or styles required?
6. **Existing patterns**: Examples or conventions to follow?

If you can infer from prior context, skip redundant questions. Use AskQuestion tool when available for structured gathering.

**IMPORTANT**: Never create skills in `~/.cursor/skills-cursor/`. This directory is reserved for Cursor's built-in skills.

---

## Skill File Structure

### Directory Layout

```
skill-name/
├── SKILL.md              # Required — decision guide (≤300 lines / <3,500 tokens, no code blocks >5 lines)
├── INJECT.md             # Recommended — always-loaded summary (50-150 tokens)
├── reference.md          # Optional — detailed documentation
├── examples.md           # Optional — usage examples
└── scripts/              # Optional — utility scripts
    └── validate.py
```

### Storage Locations

| Type      | Path                           | Scope                                                                    |
| --------- | ------------------------------ | ------------------------------------------------------------------------ |
| Personal  | `~/.cursor/skills/skill-name/` | All your projects                                                        |
| Project   | `.cursor/skills/skill-name/`   | Shared via repository                                                    |
| Universal | `.agents/skills/skill-name/`   | Cross-tool (Cursor, Claude Code, Codex, Copilot, Aider, Windsurf, Cline) |

### SKILL.md Structure

```markdown
---
name: your-skill-name
description: Brief description of what this skill does and when to use it
---

# Your Skill Name

## Instructions

Clear, step-by-step guidance for the agent.

## Examples

Concrete examples of using this skill.
```

---

## Metadata Fields

### Required Fields

| Field         | Requirements                                    | Purpose                                 |
| ------------- | ----------------------------------------------- | --------------------------------------- |
| `name`        | Max 64 chars, lowercase letters/numbers/hyphens | Unique identifier                       |
| `description` | Max 1024 chars, non-empty                       | Agent uses this to decide when to apply |

### Extended Fields (for domain-specific skills)

| Field                 | Purpose                   | Example                                      |
| --------------------- | ------------------------- | -------------------------------------------- |
| `compatibility`       | Detected stack + versions | `'Python 3.12 + Django 5.0 + PostgreSQL 16'` |
| `metadata.author`     | Who generated it          | `skillnir`                                |
| `metadata.version`    | Semver                    | `'1.0.0'`                                    |
| `metadata.sdlc-phase` | SDLC stage                | `development`, `testing`, `deployment`       |
| `allowed-tools`       | Tools the skill may use   | `Read Edit Write Bash(python:*) Glob Grep`   |

---

## Writing Effective Descriptions

The description is **critical** — it determines when the agent applies your skill via semantic matching.

### Rules

1. **Third person** (injected into system prompt):
   - Good: "Processes Excel files and generates reports"
   - Bad: "I can help you process Excel files"

2. **Specific with trigger terms**:
   - Good: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
   - Bad: "Helps with documents"

3. **Include both WHAT and WHEN**:
   - WHAT: specific capabilities
   - WHEN: trigger scenarios

### Examples

```yaml
# Code Review
description: Review code for quality, security, and best practices following team standards. Use when reviewing pull requests, code changes, or when the user asks for a code review.

# Git Commit Helper
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

---

## Core Authoring Principles

### 1. Conciseness

The context window is shared with conversation, other skills, and requests. Every token competes.

**Default assumption**: The agent is already smart. Only add context it doesn't have.

Challenge each piece: "Does the agent really need this?" / "Does this justify its token cost?"

```markdown
<!-- GOOD: concise -->

## Extract PDF text

Use pdfplumber for text extraction:
\`\`\`python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
text = pdf.pages[0].extract_text()
\`\`\`

<!-- BAD: verbose -->

## Extract PDF text

PDF (Portable Document Format) files are a common file format...
To extract text from a PDF, you'll need to use a library...
```

### 2. Keep SKILL.md Under 300 Lines / <3,500 Tokens

Research shows instruction accuracy peaks at 800-2,000 tokens and degrades beyond 5,000. SKILL.md is a **decision guide** — tables, rules, checklists, links. **No code blocks >5 lines** — move them to references/.

### 3. Progressive Disclosure

SKILL.md tells WHAT and WHEN. References tell HOW with full code examples. The AI loads SKILL.md on activation (~3,500 tokens), then pulls reference files on demand.

```markdown
## Additional resources

- For complete API details, see [reference.md](reference.md)
- For usage examples, see [examples.md](examples.md)
```

**Keep references one level deep** — link directly from SKILL.md to reference files. Deeply nested references may result in partial reads.

### 4. Degrees of Freedom

Match specificity to task fragility:

| Freedom Level                     | When to Use                      | Example                |
| --------------------------------- | -------------------------------- | ---------------------- |
| **High** (text instructions)      | Multiple valid approaches        | Code review guidelines |
| **Medium** (pseudocode/templates) | Preferred pattern with variation | Report generation      |
| **Low** (specific scripts)        | Fragile, consistency critical    | Database migrations    |

---

## INJECT.md Companion Pattern

Generate an INJECT.md alongside SKILL.md. This file is **always loaded** into AI context (50-150 tokens) and acts as a hallucination firewall.

```markdown
# {{Skill Name}} — Quick Reference

- **Stack**: {{language + framework + key libs}}
- **Entry points**: {{main files}}
- **Key directories**: {{annotated 3-5 dirs}}
- **Patterns**: {{3-5 bullet summary}}
- **Never**: {{2-3 critical anti-patterns}}
- **Full guide**: See [SKILL.md](SKILL.md)
```

**When to update INJECT.md**: Whenever the AI hallucinates a pattern — add the correct one to INJECT.md so it's always in context.

---

## Common Patterns

### Template Pattern

Provide output format templates the agent follows:

```markdown
## Report structure

\`\`\`markdown

# [Analysis Title]

## Executive summary

[One-paragraph overview]

## Key findings

- Finding 1 with data

## Recommendations

1. Specific action
   \`\`\`
```

### Workflow Pattern

Break complex operations into trackable steps:

```markdown
## Form filling workflow

Task Progress:

- [ ] Step 1: Analyze the form
- [ ] Step 2: Create field mapping
- [ ] Step 3: Validate mapping
- [ ] Step 4: Fill the form
- [ ] Step 5: Verify output

**Step 1: Analyze the form**
Run: `python scripts/analyze_form.py input.pdf`
```

### Feedback Loop Pattern

For quality-critical tasks, implement validation:

```markdown
1. Make your edits
2. **Validate**: `python scripts/validate.py output/`
3. If validation fails → fix → revalidate
4. **Only proceed when validation passes**
```

---

## Utility Scripts

Pre-made scripts offer advantages over generated code:

- More reliable (tested, not hallucinated)
- Save tokens (no code in context)
- Ensure consistency across uses

Make clear whether the agent should **execute** or **read** the script.

---

## Anti-Patterns to Avoid

- **Windows-style paths**: Use `scripts/helper.py`, not `scripts\helper.py`
- **Too many options**: Provide a default with escape hatch, not a buffet
- **Time-sensitive info**: Use "Current method" / "Legacy (deprecated)" sections, not dates
- **Inconsistent terminology**: Pick one term per concept ("API endpoint" throughout, not mixing "URL", "route", "path")
- **Vague skill names**: Use `processing-pdfs`, not `helper` or `utils`

---

## Skill Creation Workflow

### Phase 1: Discovery

Gather purpose, storage location, trigger scenarios, constraints, existing patterns.

### Phase 2: Design

Draft name (lowercase, hyphens, ≤64 chars), write description, outline sections, identify supporting files needed.

### Phase 3: Implementation

Create directory, write SKILL.md with frontmatter, create INJECT.md, create references and scripts.

### Phase 4: Verification

- [ ] Description is specific, third person, includes WHAT + WHEN
- [ ] SKILL.md under 500 lines
- [ ] INJECT.md under 150 tokens
- [ ] Consistent terminology throughout
- [ ] File references one level deep
- [ ] Examples are concrete, not abstract
- [ ] Workflows have clear steps
- [ ] No time-sensitive information
- [ ] Scripts solve problems (not punt them)
- [ ] Required packages documented
- [ ] Adaptive Interaction Protocols section present with all 7 subsections
- [ ] Interaction mode detection signals are domain-specific and concrete

---

## Writing Adaptive Interaction Protocols

When creating skills for any domain, include adaptive behavior protocols. These teach the AI to adjust its interaction style within a session. All tracking operates within the context window — no persistent state.

### Key Principles

1. **Detection signals must be concrete** — "what is..." and "how does..." are Teaching signals; "another one like X" is Efficient; tracebacks and error messages are Diagnostic. Never use vague triggers like "select based on context."
2. **Correction accumulation is mandatory** — every user correction becomes a session rule, applied to all subsequent outputs.
3. **Preference elicitation is lazy** — check existing project files before asking. Ask ONE question, not a list of options.
4. **Proficiency calibration is silent** — never announce level adjustments or be condescending. Adjust explanation depth based on observable behavior.
5. **Anti-dependency guardrails prevent over-reliance** — suggest templates after repetitive generation. Offer "try yourself first" in learning scenarios.
6. **Convention surfacing makes implicit knowledge explicit** — state discovered conventions before using them. Confirm if uncertain.
7. **Memory bridge connects sessions** — suggest persisting important corrections and conventions to project config files.

### Template

Include this section structure in generated SKILL.md files:

```markdown
### Adaptive Interaction Protocols

#### Interaction Modes

| Mode       | Detection Signals                                | Behavior                           |
| ---------- | ------------------------------------------------ | ---------------------------------- |
| Teaching   | {{domain-specific signals for first encounters}} | Explain first, then generate       |
| Efficient  | {{domain-specific signals for routine tasks}}    | Generate directly, brief reference |
| Diagnostic | {{domain-specific signals for errors}}           | Diagnose first, explain fix        |

#### On Correction

1. Acknowledge → 2. Restate as rule → 3. Apply to session → 4. **Write to LEARNED.md**

#### On Ambiguity

Check LEARNED.md first → Ask ONE question → Apply consistently → **Write to LEARNED.md**

#### Proficiency Calibration

| Signal   | Indicators                           | Adjustment                               |
| -------- | ------------------------------------ | ---------------------------------------- |
| Senior   | {{domain-specific senior signals}}   | Lead with code, rationale on non-obvious |
| Learning | {{domain-specific learning signals}} | More Teaching mode, add context          |

#### Anti-Dependency

- Suggest templates after 3+ similar generations
- Offer "try yourself first" in Teaching mode

#### Convention Surfacing

State discovered conventions → Confirm if uncertain → **Write to LEARNED.md**

#### Self-Learning via LEARNED.md

All learnings written to LEARNED.md (not suggested — written):

- Corrections → `## Corrections`
- Preferences → `## Preferences`
- Conventions → `## Discovered Conventions`
- Format: `- YYYY-MM-DD: rule description`
```

---

## SUB-AGENT AUTHORING GUIDANCE

When creating skills that include sub-agent definitions, follow these guidelines:

1. **Evaluate necessity first** — use the decision table in the base scaffold to determine if sub-agents add value. Not every skill needs them.
2. **Define agents in `agents/` directory** — one `.md` file per sub-agent following the agent definition template (Role, When to Spawn, Tools, Context Template, Result Format, Weaknesses).
3. **Add `Agent` to `allowed-tools`** — required when `sub-agents` is defined in frontmatter.
4. **Cap at 3-4 sub-agents** — more causes decision overhead.
5. **Use tool restriction** — analysis agents: `Read Glob Grep`, modification agents: `Read Edit Write Bash Glob Grep`.
6. **Include weaknesses** — each agent definition must state what it should NOT be used for.
7. **Add delegation table to SKILL.md** — minimal table with agent name, role, spawn trigger, and tools.
