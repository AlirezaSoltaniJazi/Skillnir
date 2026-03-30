# AI Interaction Guide — Backend Engineer

> Anti-dependency strategies, correction protocols, and interaction patterns for Python backend development.

---

## Anti-Dependency Strategies

### Prevent Pattern Repetition Without Understanding

- After generating 3+ similar dataclasses, ask: "Should I create a base result class?"
- After writing similar CLI commands, point to existing command patterns in `cli.py`
- Reference `references/template.py` for standard module boilerplate

### Promote Self-Sufficiency

- In teaching mode, explain WHY a pattern is used (e.g., result objects vs exceptions)
- After fixing an import error, explain the project's import conventions
- Reference specific project files as examples, not just abstract rules

### Avoid Cargo-Culting

- Don't blindly copy patterns from other projects — match Skillnir's conventions
- If a pattern seems wrong for the use case, say so and suggest alternatives
- Always check LEARNED.md before applying a convention — it may have been corrected

---

## Correction Protocol

When the user corrects Python code:

1. **Acknowledge** the specific mistake:
   - "I used `Optional[str]` instead of `str | None` — that doesn't match the project style."

2. **Restate as a rule**:
   - "Understood: always use `X | None` union syntax, never `Optional[X]`."

3. **Apply immediately** to all code in the current session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-03-31: Always use `X | None` syntax, never `Optional[X]` from typing
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented coding convention:

1. **Check backendEngineer LEARNED.md first**
2. **Check existing code** — look at 2-3 similar files for patterns
3. **Ask ONE targeted question**:
   - Good: "Should error messages use f-strings or .format()?"
   - Bad: "How should I handle errors? What about logging? And string formatting?"
4. **Apply consistently** for the rest of the session
5. **Write to LEARNED.md** under `## Preferences`

---

## Common Interaction Scenarios

### Scenario: New Module Creation

**Signal**: "Create a new module for X", "Add X functionality"
**Action**: Use `references/template.py` as base → follow naming conventions → add test file → update imports
**Key check**: Does a similar module exist? Can this be added to an existing module instead?

### Scenario: Bug Fix

**Signal**: Stack trace, "this doesn't work", error message
**Action**: Read the error → trace to source → understand the pattern → fix minimally → verify with test
**Key check**: Is this a pattern violation? If so, note in LEARNED.md under Discovered Conventions.

### Scenario: Refactoring

**Signal**: "Clean up X", "refactor Y", "simplify Z"
**Action**: Read current code → identify pattern violations → propose changes → spawn code-reviewer agent if complex
**Key check**: Will the refactoring break existing tests? Run tests after.

### Scenario: Dependency Addition

**Signal**: "Add library X", "I need Y package"
**Action**: Check if project already has an equivalent → `uv add X` → update imports → spawn dependency-auditor if security-sensitive
**Key check**: Is this a necessary dependency? Can stdlib achieve the same?

---

## Research-Backed Anti-Patterns

### Copy-Paste Drift

**Problem**: AI copies code from one module but forgets to update module-specific details.
**Mitigation**: Always read the target module's existing code first. Check imports, naming, and return types match the target context.

### Over-Abstraction

**Problem**: AI creates unnecessary abstractions (base classes, protocols) for simple cases.
**Mitigation**: Follow YAGNI. The project uses simple dataclasses and functions — don't introduce class hierarchies unless the user asks.

### Test Symmetry Assumption

**Problem**: AI assumes test structure must mirror source structure exactly.
**Mitigation**: Tests follow behavior boundaries, not module boundaries. One test class per logical behavior group, not per source function.
