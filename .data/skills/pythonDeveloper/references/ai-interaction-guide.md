# AI Interaction Guide — Python Developer

> Anti-dependency strategies, correction protocols, and interaction patterns for backend Python development in the Skillnir project.

---

## Anti-Dependency Strategies

### Prevent Over-Reliance on Code Generation

- After generating 3+ similar modules (dataclasses, CLI handlers, result types), suggest creating a project-level template
- Point to existing patterns in `src/skillnir/` as references rather than generating from scratch
- Reference `references/model-template.py` for copy-paste boilerplate

### Promote Self-Sufficiency

- In Teaching mode, explain WHY a pattern is used (e.g., why result dataclasses over exceptions) before generating code
- After correcting a type hint or import, ask: "Want me to explain the project's type hint conventions?"
- Reference [code-style.md](code-style.md) for comprehensive formatting rules

### Avoid Pattern Drift

- Always check existing modules for how similar functionality is implemented before writing new code
- If a pattern deviates from project conventions, flag it explicitly before proceeding
- When unsure about a convention, check LEARNED.md first, then existing code, then ask

---

## Correction Protocol

When the user corrects a code-related action:

1. **Acknowledge** the specific mistake:
   - "I used `os.path.join` instead of `pathlib.Path` — that violates the project convention."

2. **Restate as a rule**:
   - "Understood: all path operations use `pathlib.Path`, never `os.path`."

3. **Apply immediately** to all subsequent code in the session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-03-29: Never use os.path — all path operations use pathlib.Path exclusively
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented coding convention:

1. **Check LEARNED.md first** — the user may have answered this before
2. **Check existing code** — look at 2-3 similar modules for established patterns
3. **Ask ONE targeted question**:
   - Good: "Should this result dataclass use `frozen=True` like BackendInfo, or regular like SyncResult?"
   - Bad: "How should I structure this class? What fields? What about immutability? And naming?"
4. **Apply consistently** for the rest of the session
5. **Write to LEARNED.md** under `## Preferences`

---

## Common Interaction Scenarios

### Scenario: User Asks for a New Module

**Signal**: "Create a module for...", "Add a new feature..."
**Action**: Check existing modules for structure patterns → use result dataclasses → add type hints → add docstring → add to tests
**Key check**: Does it follow the modular pattern? (one module = one concern)

### Scenario: User Reports a Bug

**Signal**: Traceback, "this doesn't work", error output
**Action**: Read the relevant module → check type hints for mismatches → check Path operations → verify error handling
**Key check**: Is the error in result handling or in an uncaught exception?

### Scenario: User Asks for Tests

**Signal**: "Write tests for...", "Add coverage for..."
**Action**: Follow pytest patterns from conftest.py → use tmp_path fixture → class-based organization → assert on result dataclass fields
**Key check**: Are you testing behavior (results) or implementation (mocks)?

### Scenario: User Wants to Add a Backend

**Signal**: "Add support for...", "New backend..."
**Action**: Add to AIBackend enum → create BackendInfo entry → add model list → implement stream parsing → add to command builder
**Key check**: Does it follow the existing BACKENDS registry pattern?

---

## Research-Backed Anti-Patterns

### Anchor Bias in Code Style

**Problem**: AI generates code in a generic Python style, ignoring project-specific conventions (e.g., double quotes, os.path).
**Mitigation**: INJECT.md provides critical conventions loaded every response. LEARNED.md captures corrections for cross-session persistence.

### Over-Mocking in Tests

**Problem**: AI mocks everything, creating fragile tests that pass but don't verify behavior.
**Mitigation**: Project uses tmp_path for real file operations. Only mock external dependencies (subprocess, network). Test result dataclass fields directly.

### Exception-Based Flow Control

**Problem**: AI defaults to raising exceptions for expected outcomes (missing files, version mismatches).
**Mitigation**: Project uses result dataclasses exclusively. Reference SyncResult, InjectionResult, GenerationResult patterns.

### Type Hint Inconsistency

**Problem**: AI uses legacy typing module (Optional, List, Dict) instead of modern syntax.
**Mitigation**: Project requires Python 3.14 syntax: `str | None`, `list[X]`, `dict[K, V]`, `tuple[X, ...]`.
