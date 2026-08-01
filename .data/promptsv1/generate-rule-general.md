---
name: create-rule
description: Create Cursor rules for persistent AI guidance. Use when you want to create a rule, add coding standards, set up project conventions, configure file-specific patterns, create RULE.md files, or asks about .cursor/rules/ or AGENTS.md.
---

# Creating Cursor Rules

Create project rules in `.cursor/rules/` to provide persistent context for the AI agent.

## Derive Requirements (headless — you cannot ask questions)

You run non-interactively: the user prompt supplies the target project path and
the rule topic, and there is no user available mid-run. Derive everything:

1. **Purpose**: from the rule topic in the user prompt.
2. **Scope**: infer from the topic — language/framework topics get `globs`
   scoped to the matching files; cross-cutting standards get `alwaysApply: true`.
3. **File patterns**: from the file types the project actually contains
   (Glob the tree; never invent extensions the project doesn't use).

## Ground the Rule in the Project

Before writing, scan the codebase (Read/Glob/Grep) for the topic's real
conventions: actual file paths, actual error classes, actual naming. Every
example in the rule must reflect this project — a rule showing code the
project would never contain teaches the agent the wrong dialect. Check
`.data/skills/*/LEARNED.md` for accumulated corrections on this topic first.

If `.cursor/rules/` already has a rule covering this topic, **UPDATE that file
in place** — never create a near-duplicate under a new name.

---

## Rule File Format

Rules are `.mdc` files in `.cursor/rules/` with YAML frontmatter:

```markdown
---
description: Brief description of what this rule does
globs: **/*.ts
alwaysApply: false
---

# Rule Title

Your rule content here...
```

### Frontmatter Fields

| Field         | Type    | Description                                              |
| ------------- | ------- | -------------------------------------------------------- |
| `description` | string  | What the rule does (shown in rule picker)                |
| `globs`       | string  | File pattern — rule applies when matching files are open |
| `alwaysApply` | boolean | If true, applies to every session                        |

### Glob Pattern Reference

| Pattern                | Matches                  |
| ---------------------- | ------------------------ |
| `**/*.ts`              | All TypeScript files     |
| `**/*.{ts,tsx}`        | TypeScript + TSX         |
| `src/api/**/*.py`      | Python files in src/api/ |
| `**/test_*.py`         | Python test files        |
| `docker-compose*.yml`  | Docker compose variants  |
| `**/*.{css,scss,less}` | All style files          |

---

## Rule Configurations

**Always Apply** — universal standards:

```yaml
---
description: Core coding standards for the project
alwaysApply: true
---
```

**File-Specific** — scoped to patterns:

```yaml
---
description: TypeScript conventions
globs: **/*.ts
alwaysApply: false
---
```

---

## Best Practices

- **Under 50 lines** — concise and scannable
- **One concern per rule** — split large rules into focused pieces
- **Concrete examples** — show before/after, not just prose
- **Specify anti-patterns** — what NOT to do with why
- **Reference LEARNED.md** — if `.data/skills/*/LEARNED.md` files contain relevant corrections or conventions, incorporate them into the rule so accumulated learnings persist across tools

---

## Example Rule

```markdown
---
description: Error handling standards
globs: **/*.ts
alwaysApply: false
---

# Error Handling

\`\`\`typescript
// BAD
try { await fetchData(); } catch (e) {}

// GOOD
try {
await fetchData();
} catch (e) {
logger.error('Failed to fetch', { error: e });
throw new DataFetchError('Unable to retrieve data', { cause: e });
}
\`\`\`

- Always log errors with context before re-throwing
- Use custom error classes from `src/errors/`
- Never swallow exceptions silently
```

---

## Cross-Tool Equivalents

Rules created here can be mirrored to other AI tools:

| Cursor                | Claude Code         | Copilot                           | Universal           |
| --------------------- | ------------------- | --------------------------------- | ------------------- |
| `.cursor/rules/*.mdc` | `CLAUDE.md` section | `.github/copilot-instructions.md` | `AGENTS.md` section |

To maximize reach, consider also adding the rule content as a section in the project's `AGENTS.md` (root-level, supported by 60,000+ repos).

---

## Checklist

- [ ] File is `.mdc` format in `.cursor/rules/`
- [ ] Frontmatter configured correctly (description + globs or alwaysApply)
- [ ] Content under 50 lines
- [ ] Includes concrete before/after examples drawn from THIS project's code
- [ ] One concern per rule file
- [ ] Existing rule on the same topic was updated, not duplicated
