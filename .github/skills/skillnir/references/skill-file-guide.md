# Skill File System — Complete Guide

> Reference for the skillnir skill system. Explains every file in a skill directory, its purpose, constraints, and ownership.

---

## Directory Layout

```
{{skill-name}}/
├── SKILL.md            # Decision guide (≤300 lines / <3,500 tokens)
├── INJECT.md           # Always-loaded quick reference (50-150 tokens)
├── LEARNED.md          # AI-written corrections, preferences, conventions
├── agents/             # Sub-agent definitions (optional)
│   └── {{name}}.md     # One file per sub-agent
├── references/         # Detailed docs, code examples, templates
│   ├── code-style.md
│   ├── security-checklist.md
│   ├── common-issues.md
│   └── {{pattern}}.md
├── assets/             # Copy-as-is config boilerplate (optional)
│   └── {{config}}.ext
└── scripts/            # Convention validation (at least one)
    └── validate-{{scope}}.sh
```

---

## File Details

### SKILL.md — Decision Guide

**Purpose**: The primary skill definition loaded when a skill activates. Contains tables, rules, checklists, and links — never code blocks longer than 5 lines.

**Constraints**:

- **≤300 lines** total
- **<3,500 tokens** total
- No code blocks >5 lines — move them to `references/`
- Must instruct AI to read LEARNED.md first
- Must include announcement rule: `"Using: {{Skill Name}} skill"`
- Must include Adaptive Interaction Protocols section

**Sections** (standard order):

1. Frontmatter (YAML `---` block)
2. Before You Start (read LEARNED.md, announce skill)
3. When to Use (activation triggers)
4. Do NOT Use (delegation to other skills)
5. Architecture (directory map, data flow)
6. Key Patterns (table: pattern → approach → key rule)
7. Code Style / Conventions (table: rule → convention)
8. Common Recipes (numbered steps)
9. Testing Standards (if applicable)
10. Performance Rules (if applicable)
11. Security (if applicable)
12. Anti-Patterns (table: anti-pattern → why it's wrong)
13. Code Generation Rules (numbered list)
14. Adaptive Interaction Protocols (modes, corrections, preferences, calibration)
15. Sub-Agent Delegation (table, only if agents/ exists)
16. References (table: file → description)

**Who edits**: Skill generator only. Manual edits may be overwritten on regeneration.

---

### INJECT.md — Hallucination Firewall

**Purpose**: Always loaded into the AI's context window (even before SKILL.md). Contains the most critical facts the AI must know at all times to avoid hallucinations.

**Constraints**:

- **50-150 tokens** (strict)
- Bullet-point format only
- Must reference LEARNED.md
- Must reference SKILL.md for full guide

**Standard bullets**:

- FIRST: Read LEARNED.md
- Stack / technology summary
- Entry points / key files
- Key directories
- Critical patterns (3-5 bullets)
- Critical anti-patterns (2-3 bullets)
- Sub-agents (if any)
- Self-learning protocol
- Link to SKILL.md

**Who edits**: AI updates when it discovers a hallucination pattern (e.g., consistently getting an import wrong). Keep updates rare — this file has a tight token budget.

---

### LEARNED.md — Session Memory

**Purpose**: Accumulates corrections, preferences, and discovered conventions across sessions. The AI reads this first and writes to it during sessions. This is the primary mechanism for cross-session learning.

**Constraints**:

- Entries use `- YYYY-MM-DD: rule description` format
- One discrete rule per entry (not paragraphs)
- Never delete entries — they accumulate over time
- Three sections: Corrections, Preferences, Discovered Conventions

**Template**:

```markdown
# Learned Conventions

> This file is auto-updated by the AI when user corrections reveal conventions.
> Each entry has a date and the rule learned. Do NOT delete entries.
> Format: `- YYYY-MM-DD: rule description`

## Corrections

<!-- AI writes here when user corrects generated code -->

## Preferences

<!-- AI writes here when user states a preference -->

## Discovered Conventions

<!-- AI writes here when it discovers implicit project conventions -->
```

**Good entries**:

```
- 2026-03-21: Always use single quotes in Python strings (Black -S flag)
- 2026-03-21: Pre-commit hooks must exclude .data/ directory
- 2026-03-21: Use `uv add` not `pip install` for all dependencies
```

**Bad entries** (too vague, too long, or multiple rules):

```
- 2026-03-21: The project uses single quotes and pathlib and dataclasses and lazy imports
  and also the tests use pytest with asyncio mode auto and there's a pre-commit config
```

**Who edits**: AI writes during sessions. Never edited by the skill generator.

---

### agents/ — Sub-Agent Definitions

**Purpose**: Define specialized sub-agents the AI can spawn via the `Agent` tool. Each agent gets its own file with role, spawn triggers, tools, context template, result format, and weaknesses.

**Constraints**:

- One `.md` file per sub-agent
- Maximum 3-4 sub-agents per skill
- `Agent` must be in `allowed-tools` if this directory exists
- Sub-agents cannot spawn their own sub-agents (max depth = 1)
- Each definition must include a Weaknesses section

**When to skip**: If the skill has no delegation needs, omit this directory entirely.

**Who edits**: Skill generator creates; AI may suggest additions but generator writes.

---

### references/ — Detailed Documentation

**Purpose**: All detailed content that won't fit in SKILL.md's token budget. Code examples, full templates, detailed checklists, troubleshooting guides. Loaded on demand when the AI encounters a relevant task.

**Constraints**:

- All code blocks >5 lines go here (not in SKILL.md)
- Minimum 5 reference files per skill
- Use descriptive filenames: `code-style.md`, `api-patterns.md`, `common-issues.md`
- SKILL.md links to these with relative paths: `[guide](references/code-style.md)`

**Required files** (every skill must have):

1. `code-style.md` — imports, formatting, naming with examples
2. `security-checklist.md` — per-component verification
3. `common-issues.md` — troubleshooting with fixes
4. `{{domain}}-patterns.md` — full code examples for key patterns
5. `ai-interaction-guide.md` — anti-dependency strategies

**Who edits**: Skill generator creates; AI may extend with new reference files.

---

### assets/ — Boilerplate Templates

**Purpose**: Config files, Dockerfiles, env examples, and other files users copy verbatim. Not documentation — actual runnable/usable files.

**Constraints**:

- Use descriptive names: `env-example`, `config-example.py`
- Keep files minimal and well-commented
- Only include if the skill has copy-worthy boilerplate

**When to skip**: If no boilerplate templates are relevant, omit this directory.

**Who edits**: Skill generator or DevOps.

---

### scripts/ — Validation Scripts

**Purpose**: Bash scripts that verify convention compliance. Run manually or as CI checks.

**Constraints**:

- Naming: `validate-{{scope}}.sh`
- Must use `set -euo pipefail`
- Use colored output for pass/fail
- Exit with non-zero on any failure
- At least one validation script per skill

**Who edits**: Skill generator creates; DevOps may extend.

---

## Token Budgets

| File             | Budget                      | Loaded When                   |
| ---------------- | --------------------------- | ----------------------------- |
| INJECT.md        | 50-150 tokens               | Always (every response)       |
| SKILL.md         | ≤300 lines / <3,500 tokens  | On skill activation           |
| LEARNED.md       | Unlimited (grows over time) | Before SKILL.md on activation |
| references/\*.md | Unlimited                   | On demand (when task matches) |
| agents/\*.md     | Unlimited                   | On delegation decision        |
