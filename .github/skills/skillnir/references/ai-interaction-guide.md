# AI Interaction Guide — Skill System

> Anti-dependency strategies, correction protocols, and interaction patterns for the skillnir skill system meta-skill.

---

## Anti-Dependency Strategies

### Prevent Over-Reliance on Skill Generation

- After generating 3+ similar skill structures, suggest creating a project-level scaffold template
- Point to `skillnir scaffold` command for automated skill creation
- Reference `.data/promptsv1/` prompt templates for consistent generation

### Promote Self-Sufficiency

- In teaching mode, explain WHY content goes in LEARNED.md vs SKILL.md before writing
- After correcting a file placement error, ask: "Do you want me to explain the full file ownership model?"
- Reference [skill-file-guide.md](skill-file-guide.md) for complete documentation

### Avoid Circular Dependencies

- The skillnir skill defines meta-rules for ALL skills
- Domain skills should NOT redefine meta-rules (e.g., LEARNED.md format)
- If a domain skill needs a meta-rule exception, record it in the skillnir LEARNED.md

---

## Correction Protocol

When the user corrects a skill-system-related action:

1. **Acknowledge** the specific mistake:
   - "I wrote that preference to SKILL.md instead of LEARNED.md — that's wrong."

2. **Restate as a rule**:
   - "Understood: all session learnings go to LEARNED.md, never SKILL.md."

3. **Apply immediately** to all subsequent actions in the session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-03-21: Never write session learnings to SKILL.md — use LEARNED.md exclusively
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented skill-system convention:

1. **Check skillnir LEARNED.md first** — the user may have answered this before
2. **Check project files** — `CLAUDE.md`, existing skill directories, `pyproject.toml`
3. **Ask ONE targeted question**:
   - Good: "Should new reference files use hyphens or underscores in filenames?"
   - Bad: "How should I name files? What about directory structure? And formatting?"
4. **Apply consistently** for the rest of the session
5. **Write to LEARNED.md** under `## Preferences`

---

## Common Interaction Scenarios

### Scenario: User Asks to Add a Preference

**Signal**: "Remember that...", "Always do...", "I prefer..."
**Action**: Write to the correct skill's LEARNED.md under `## Preferences`
**Key check**: Is this a domain preference (write to domain skill) or a meta preference (write to skillnir)?

### Scenario: User Asks to Fix a Skill File

**Signal**: "Update the INJECT.md", "Add to references", "Fix the validation script"
**Action**: Read the skill's SKILL.md first, then make the change following its conventions
**Key check**: Are you editing a generated file (SKILL.md) that should be regenerated instead?

### Scenario: User Asks Where Something Goes

**Signal**: "Where should I put this?", "Which file?", "SKILL.md or LEARNED.md?"
**Action**: Use the file ownership table from SKILL.md to route content correctly
**Key check**: Check LEARNED.md for any previous rulings on similar content placement

### Scenario: Ambiguous Skill Activation

**Signal**: Task could belong to multiple skills
**Action**: Use file-based routing from [cross-skill-rules.md](cross-skill-rules.md)
**Key check**: If still ambiguous, ask ONE question to clarify, then record the routing decision

---

## Research-Backed Anti-Patterns

### Anchor Bias in Corrections

**Problem**: AI remembers the first version of a rule and reverts to it after being corrected.
**Mitigation**: Writing corrections to LEARNED.md with explicit dates ensures the AI reads the latest version each session, breaking the anchor.

### Context Window Degradation

**Problem**: Long sessions cause skill conventions to drift as earlier context fades.
**Mitigation**: INJECT.md provides a persistent anchor (always loaded). LEARNED.md is read at activation (refreshed per session). Together they prevent drift.

### Over-Eager Convention Application

**Problem**: AI applies a convention from one skill to another where it doesn't belong.
**Mitigation**: Cross-skill rules in [cross-skill-rules.md](cross-skill-rules.md) define clear boundaries. Each skill owns its domain. Meta-rules live in the skillnir skill only.
