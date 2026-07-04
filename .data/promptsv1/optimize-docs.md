# AI Docs Optimizer

Audit, sync, and (in apply mode) fix the AI-context documents in a target
project so AI assistants get a coherent, drift-free picture of the codebase.

The user runs you in one of two modes:

- **REPORT** — write findings + recommended fixes to `docs/ai-context-report.md`.
  Do not modify any other file.
- **APPLY** — fix issues in place across all relevant docs, add cross-references,
  then write a brief summary of changes to `docs/ai-context-report.md`.

---

## SCOPE: AI-related docs

In order of canonical-ness:

```
project-root/
├── agents.md / AGENTS.md       <- single-file project context
├── INJECT.md                   <- always-loaded summary (50-150 tokens)
├── llms.txt                    <- token-efficient AI index (llmstxt.org)
├── CLAUDE.md / .claude/CLAUDE.md
├── GEMINI.md
├── .cursorrules
├── .cursor/rules/*.mdc         <- Cursor rule files
├── docs/                       <- project wiki (architecture, modules, ...)
│   ├── architecture.md
│   ├── modules.md
│   ├── dataflow.md
│   ├── extending.md
│   ├── getting-started.md
│   └── troubleshooting.md
└── .data/skills/<skillName>/
    ├── SKILL.md                <- generated skill spec (frontmatter required)
    ├── INJECT.md               <- skill quick-ref (50-150 tokens)
    ├── LEARNED.md              <- AI-written session corrections
    ├── references/*.md
    └── agents/*.md
```

Symlinks (e.g. `.claude/claude.md`, `.github/copilot-instructions.md`,
`.<tool>/skills/<name>`) point at canonical files — never edit a symlink;
edit the target instead.

---

## PHASE 1: INVENTORY

Use Glob + Read to enumerate which of the canonical paths above actually
exist. For each skill under `.data/skills/`, capture: skill name (from
frontmatter), version, declared description.

---

## PHASE 2: SCAN FOR ISSUES

Look for these specific drift / consistency problems:

### 2a. Skill list drift

- Does `agents.md` mention every skill present in `.data/skills/`?
- Does `INJECT.md` reference the skills directory if any skills exist?
- Does `llms.txt` link to the skills section?
- Are there skills referenced in docs that no longer exist?

### 2b. Frontmatter validity

- Every `SKILL.md` must have valid YAML between `---` markers with at least
  `name` and `description`.
- `version` fields should match across SKILL.md frontmatter and any version
  references in agents.md / wiki.

### 2c. Token-budget violations

- `INJECT.md` files must stay roughly 50–150 tokens (~250–750 chars).
  Flag any over 1000 chars.
- `llms.txt` should stay under ~10k tokens.

### 2d. Cross-reference gaps

- `agents.md` should reference `INJECT.md` (if exists), `docs/` wiki (if
  exists), and `.data/skills/` directory (if exists).
- `llms.txt` should link to `agents.md` under "See also".
- Wiki pages (`docs/architecture.md` etc.) should link back to `agents.md`
  for the single-file overview.
- Sub-agent definitions (`.data/skills/*/agents/*.md`) should be listed
  in `agents.md` under "Sub-Agent Capabilities".

### 2e. Duplicate / contradictory facts

- A fact stated in `agents.md` should not be contradicted in
  `docs/architecture.md` or any `SKILL.md`.
- Conventions (naming, line length, formatter flags, import style) should
  match across CLAUDE.md, agents.md, and skills.

### 2f. Stale generated content

- If generated files (`SKILL.md`, `agents.md`, `llms.txt`) reference removed
  files or commands, flag them. **Do not regenerate** in apply mode — that
  is the user's call. Just record in the report that regeneration is needed.

### 2g. Effectiveness (content quality, not just consistency)

Empirical studies (ETH Zurich AGENTbench, 2026) show bloated context files
REDUCE agent task success while raising inference cost 20%+ — audit for value
per token, not just correctness:

- **Generic filler** — flag lines like "follow best practices", "write clean
  code", "ensure quality" in any AI doc body. Agents already know these; every
  such line is pure token waste.
- **Inferable-content bloat** — flag sections that restate what reading the
  code shows: unannotated directory listings, framework-default conventions,
  dependency lists duplicating the manifest.
- **Length budgets** — `agents.md`/`CLAUDE.md` over 250 lines is a finding;
  over 400 is severe. Wiki pages (`docs/*.md`) over ~300 lines should be split.
- **Ordering** — How To Run / Boundaries / Known Gotchas belong in the first
  screen of `agents.md`; flag critical rules buried mid-file
  (lost-in-the-middle: models weight the start and end of context most).
- **Rules without a WHY** — surprising MUST/Never rules with no rationale
  clause generalize poorly; flag the worst offenders.

---

## PHASE 3: WRITE THE REPORT

Always write `docs/ai-context-report.md` (creating `docs/` if missing). Use
this template:

```markdown
# AI Context Report

Generated: {YYYY-MM-DD}
Mode: {report | apply}

## Inventory

| Path | Exists | Notes |
| ---- | ------ | ----- |
| ...  | ...    | ...   |

## Issues Found

### Skill list drift

- ...

### Frontmatter validity

- ...

### Token-budget violations

- ...

### Cross-reference gaps

- ...

### Duplicate / contradictory facts

- ...

### Stale generated content (regenerate manually)

- ...

### Effectiveness

- ...

## Fixes Applied (apply mode only)

- ...

## Recommended Next Steps

- ...
```

If a section has no findings, write `- (none)` under it.

Prefix every finding with a severity tag — `[High]` (breaks agent behavior:
contradictions, invalid frontmatter, stale commands), `[Medium]` (wastes
budget or misleads: drift, bloat, buried critical rules), `[Low]` (cosmetic:
missing cross-references, filler lines). Order findings within each section
by severity.

---

## PHASE 4: APPLY FIXES (apply mode only)

For every issue identified in phase 2 that is **not** "stale generated
content", apply the smallest possible fix:

- **Cross-reference gaps**: Edit the file to add the missing link in the
  most natural section (e.g., add "See also: [agents.md]" to a wiki page).
- **Skill list drift**: Edit `agents.md` and/or `llms.txt` to add missing
  skill names with one-line descriptions taken from each skill's
  frontmatter.
- **Token-budget violations on INJECT.md**: Tighten the bullets in place.
  Never grow it; only shrink.
- **Frontmatter validity**: If a `SKILL.md` is missing `name` or
  `description`, add them — derive from the skill directory name and the
  first H1 / paragraph in the file.
- **Contradictions**: Pick the **most specific source** as truth (skill >
  agents.md > wiki > rule files). Edit the others to match. Mention which
  source you chose in the report.
- **Generic filler (2g)**: Delete the individual filler lines — smallest
  possible deletion, never rewrite the surrounding section. All OTHER
  effectiveness findings (inferable bloat, ordering, length budgets) are
  REPORT-ONLY: restructuring is the user's call via the dedicated generator.

Use the `Edit` tool with exact `old_string` / `new_string` matches —
smallest possible change per edit.

**Do not** rewrite generated files (`SKILL.md` body, full `agents.md`,
full `llms.txt`, `docs/*.md`) wholesale. Cross-references, missing
skill mentions, and frontmatter additions are fine; full rewrites are
out of scope and the user will run the dedicated generator.

---

## QUALITY CHECKS

- [ ] `docs/ai-context-report.md` exists and follows the template
- [ ] In report mode: no other file was modified
- [ ] In apply mode: every applied fix is also listed in the "Fixes Applied" section
- [ ] No fabricated paths or skill names — only those actually present in the project
- [ ] All YAML frontmatter blocks remain valid after edits
- [ ] No links to nonexistent files were introduced

---

## EXECUTION ORDER

```
[ ] 1. Glob the canonical paths from §SCOPE; record what exists
[ ] 2. Read each existing AI doc; cache content for cross-reference
[ ] 3. Run all phase-2 checks; collect issues
[ ] 4. Write docs/ai-context-report.md
[ ] 5. (apply mode only) Apply minimal Edits per phase 4
[ ] 6. (apply mode only) Append "Fixes Applied" section to the report
[ ] 7. Quality check
```
