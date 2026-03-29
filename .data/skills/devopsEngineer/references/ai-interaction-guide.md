# AI Interaction Guide — Infrastructure

> Research-backed anti-patterns, anti-dependency strategies, and correction protocols for infrastructure tasks.

---

## Anti-Dependency Strategies

### Problem: Over-reliance on AI for Infrastructure Decisions

Infrastructure mistakes have blast radius — a bad workflow config affects every PR, a broken pre-commit hook blocks every developer.

### Guardrails

1. **Never auto-apply infrastructure changes without review** — always show the diff first
2. **Explain the "why" for non-obvious config** — CI timeout values, permission scopes, hook ordering
3. **Reference existing patterns** — "this matches check-style.yml" rather than generating from scratch
4. **Encourage local testing** — suggest `pre-commit run --all-files` before committing
5. **Teach debugging skills** — show how to read CI logs, not just fix the error

---

## Common AI Anti-Patterns in Infrastructure

| Anti-Pattern                              | Better Approach                                |
| ----------------------------------------- | ---------------------------------------------- |
| Generating complex workflows from scratch | Copy existing workflow, modify incrementally   |
| Adding permissions without justification  | Explain why each permission is needed          |
| Using latest/unpinned versions            | Always pin, explain version strategy           |
| Ignoring pre-commit/CI alignment          | Check both when modifying either               |
| Over-engineering simple tasks             | Start minimal, add complexity only when needed |

---

## Correction Protocol

When the user corrects an infrastructure decision:

1. **Acknowledge** the correction immediately
2. **Restate** as a rule: "Infrastructure rule: always X, never Y"
3. **Apply** to current and all subsequent output
4. **Write** to [LEARNED.md](../LEARNED.md) under `## Corrections`
5. **Verify** the correction doesn't conflict with existing conventions

---

## Convention Surfacing

When discovering implicit infrastructure conventions:

1. **Observe** — note the pattern across multiple files
2. **Verify** — check at least 2-3 instances before declaring a convention
3. **Document** — write to [LEARNED.md](../LEARNED.md) under `## Discovered Conventions`
4. **Apply** — use the convention in subsequent output

Examples:

- "All workflows use `timeout-minutes: 10`" → convention
- "Pre-commit hooks exclude `.data/` for code quality" → convention
- "Composite actions stored in `.github/actions/{name}/`" → convention

---

## Proficiency Signals

| Signal                                           | Response                                            |
| ------------------------------------------------ | --------------------------------------------------- |
| User pastes CI error log                         | Diagnostic mode — read the log, identify root cause |
| User says "add a workflow like X"                | Efficient mode — copy pattern, minimal explanation  |
| User asks "what does this permission do"         | Teaching mode — explain with context                |
| User requests "review my workflow"               | Review mode — delegate to security-scanner agent    |
| User modifies generated config before committing | Senior signal — reduce explanations                 |
| User asks "is this right?" repeatedly            | Learning signal — increase guidance                 |
