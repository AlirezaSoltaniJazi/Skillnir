# Cross-Skill Rules

> Rules that span all skills in the skillnir project. Defines skill interaction, priority, delegation, and coordination patterns.

---

## Skill Inventory

| Skill            | Domain                                | Activates For                                    |
| ---------------- | ------------------------------------- | ------------------------------------------------ |
| backendEngineer  | Python modules, CLI, async, testing   | Any code under `src/skillnir/`, `tests/`      |
| frontendEngineer | NiceGUI UI, Tailwind, HTML generation | `ui.py`, `researcher.py` HTML, styling           |
| devopsEngineer   | CI/CD, Docker, pre-commit, UV         | Workflows, Dockerfiles, config, scripts          |
| skillnir          | Skill system meta-rules               | Skill files, LEARNED.md entries, skill structure |

---

## Priority Rules

When multiple skills could apply to a task, use this priority order:

### 1. Domain Specificity Wins

If the task clearly belongs to one domain, use that domain skill:

- Editing `ui.py` layout → frontendEngineer
- Adding a pytest fixture → backendEngineer
- Modifying `.pre-commit-config.yaml` → devopsEngineer
- Adding a LEARNED.md entry → skillnir

### 2. File-Based Routing

Use the primary file being edited to select the skill:

| File Pattern                                   | Skill                                                   |
| ---------------------------------------------- | ------------------------------------------------------- |
| `src/skillnir/*.py` (except `ui.py`)        | backendEngineer                                         |
| `src/skillnir/ui.py`                        | frontendEngineer                                        |
| `src/skillnir/researcher.py` (HTML parts)   | frontendEngineer                                        |
| `src/skillnir/researcher.py` (Python logic) | backendEngineer                                         |
| `tests/**/*.py`                                | backendEngineer                                         |
| `.github/workflows/*.yml`                      | devopsEngineer                                          |
| `pyproject.toml`, `uv.lock`                    | devopsEngineer                                          |
| `.pre-commit-config.yaml`                      | devopsEngineer                                          |
| `Dockerfile`, `docker-compose.yml`             | devopsEngineer                                          |
| `.data/skills/**/*`                            | skillnir                                                 |
| `scripts/validate-*.sh`                        | devopsEngineer (content) + skillnir (skill system rules) |

### 3. Cross-Domain Tasks

Some tasks span multiple domains. In these cases:

- **Use the primary skill** for the main work
- **Reference other skills** for conventions that apply
- Example: Adding a new CLI command (backendEngineer) that needs a UI page (frontendEngineer) → start with backendEngineer for the CLI + module, then switch to frontendEngineer for the UI page

### 4. Meta-Tasks Always Include skillnir

Any task that touches skill files uses the skillnir skill, even if it's part of a domain task:

- Adding a correction to backendEngineer's LEARNED.md → skillnir rules apply
- Creating a new reference file → skillnir rules for file placement + domain skill for content

---

## Delegation Between Skills

### When to Switch Skills

- Announce the new skill: `"Switching to: Frontend Engineer skill"`
- Read the target skill's LEARNED.md before proceeding
- Apply the target skill's conventions for the remainder of that sub-task

### When NOT to Switch

- Don't switch for a one-line reference to another domain
- Don't switch if you're just reading (not modifying) files in another domain
- Don't switch mid-function — complete the current unit of work first

### Multi-Skill Workflows

For complex tasks touching multiple domains:

1. **Plan phase**: Identify which skills will be needed
2. **Execute sequentially**: Complete each domain's work under its skill
3. **Cross-reference**: Check that changes in one domain don't violate another's conventions
4. **Write learnings**: Any cross-domain convention goes to the skillnir skill's LEARNED.md

---

## Universal Rules (Apply to ALL Skills)

These rules appear in every skill and must always be followed:

1. **Read LEARNED.md first** — before any work in a skill's domain
2. **Announce skill activation** — `"Using: {{Skill Name}} skill"` at response start
3. **Write corrections to LEARNED.md** — date-formatted, one rule per entry
4. **Write preferences to LEARNED.md** — after user states a preference
5. **Write discovered conventions to LEARNED.md** — after confirming with user
6. **Check LEARNED.md on ambiguity** — before asking the user a question
7. **Never put code in SKILL.md** — code blocks >5 lines go in references/
8. **Sub-agents can't spawn sub-agents** — max delegation depth = 1
9. **Pass context explicitly to sub-agents** — they don't see parent conversation
10. **Cap sub-agents at 3-4 per skill** — more causes routing degradation

---

## Skill Interaction Patterns

### Adding a New Skill

1. Create directory under `.data/skills/{{name}}/`
2. Follow the directory layout in [skill-file-guide.md](skill-file-guide.md)
3. Add symlinks from tool dotdirs (`.claude/skills/`, `.cursor/skills/`, etc.)
4. Update cross-skill routing table in this document

### Modifying an Existing Skill

1. Read the skill's SKILL.md first (understand its conventions)
2. If editing LEARNED.md: follow date format, one rule per entry
3. If editing references/: maintain existing structure and naming
4. If editing INJECT.md: stay within 150-token budget
5. Never edit SKILL.md directly — it's generated by the skill generator

### Resolving Conflicts

When two skills give contradictory guidance:

1. Check if one skill's LEARNED.md has a more recent override
2. Prefer the more domain-specific skill's rule
3. If truly ambiguous, ask the user and record the decision in LEARNED.md
