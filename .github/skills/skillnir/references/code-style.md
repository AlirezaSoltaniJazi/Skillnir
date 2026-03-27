# Skill File Code Style Guide

> Formatting, naming, and structural conventions for all skill files in the skillnir project.

---

## SKILL.md Formatting

### Frontmatter

```yaml
---
name: skill-name # lowercase, hyphens only, max 64 chars
description: >-
  Multi-line YAML folded string. Third person. Include WHAT the skill does,
  WHEN it activates, and trigger terms for discovery. Max 1024 chars.
compatibility: "Language version, framework, key libs"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: development # development | testing | deployment
allowed-tools: Read Edit Write Bash(python:*) Glob Grep Agent
---
```

### Section Headers

- Use `##` (H2) for top-level sections
- Use `###` (H3) for sub-sections within
- Keep headers short and descriptive
- Standard section order matches template in [skill-file-guide.md](skill-file-guide.md)

### Tables

Tables are the primary content format in SKILL.md:

**Good table** (concise, scannable):

```markdown
| Pattern      | Approach                          | Key Rule                    |
| ------------ | --------------------------------- | --------------------------- |
| Result types | `@dataclass` with `success: bool` | Return results, never raise |
```

**Bad table** (too verbose, paragraph-length cells):

```markdown
| Pattern      | Approach                                                                                                                                                                                                         |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Result types | You should use Python dataclasses decorated with @dataclass and include a success boolean field and an optional error string field and return these from your functions instead of raising exceptions because... |
```

### Lists

- Use numbered lists for ordered procedures (recipes, steps)
- Use bullet lists for unordered items (rules, conventions)
- Keep items to one line where possible

### Links

- Always use relative paths: `[LEARNED.md](LEARNED.md)`
- Reference directory: `[references/](references/)`
- Cross-skill: `[backendEngineer](../backendEngineer/SKILL.md)`

---

## INJECT.md Formatting

- Start with `# {{Skill Name}} — Quick Reference`
- HTML comment explaining purpose and token budget
- Bullet points only, each starting with `**bold label**:`
- Keep each bullet to one line
- No tables, no headers (except the title), no code blocks

---

## LEARNED.md Formatting

### Entry Format

```
- YYYY-MM-DD: Single sentence describing one rule
```

### Good Entries

```
- 2026-03-21: Always use single quotes in Python strings (Black -S flag)
- 2026-03-21: Pre-commit hooks must exclude .data/ directory
- 2026-03-21: Validation scripts must use set -euo pipefail
```

### Bad Entries

```
- 2026-03-21: The project uses single quotes and also pathlib and also dataclasses
- Mar 21: Use single quotes (wrong date format)
- 2026-03-21: Always use single quotes in Python strings (Black -S flag). Also remember
  that the line length is 100 characters. And imports should be sorted. (multiple rules)
```

### Section Comments

- Keep the HTML comment placeholders for empty sections
- Never remove the section headers even when empty

---

## references/ Formatting

### File Naming

- Use lowercase with hyphens: `code-style.md`, `api-patterns.md`
- Template files use project language extension: `model-template.py`
- Prefix with domain when needed: `component-patterns.md`, `pipeline-patterns.md`

### Document Structure

```markdown
# Title

> One-line description of what this reference covers.

---

## Section 1

Content with full code examples...

## Section 2

More detailed content...
```

### Code Blocks

- Always specify language: ` ```python `, ` ```yaml `, ` ```bash `
- Include enough context to be copy-pasteable
- Add inline comments for non-obvious logic

---

## scripts/ Formatting

### Shell Script Structure

```bash
#!/usr/bin/env bash
set -euo pipefail

# Description of what this script validates
# Usage: ./validate-{{scope}}.sh [project-root]

PASS=0
FAIL=0

check() {
    local description="$1"
    local result="$2"
    if [[ "$result" == "pass" ]]; then
        echo "  PASS  $description"
        ((PASS++))
    else
        echo "  FAIL  $description"
        ((FAIL++))
    fi
}

# ... checks ...

echo ""
echo "Results: $PASS passed, $FAIL failed"
exit $FAIL
```

### Naming

- Always `validate-{{scope}}.sh`
- Scope matches the skill domain: `validate-backend.sh`, `validate-frontend.sh`, `validate-skill-system.sh`
