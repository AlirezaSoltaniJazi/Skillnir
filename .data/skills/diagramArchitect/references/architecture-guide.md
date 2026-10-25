# Architecture Guide — How This Skill Is Organized

## Skill Layout

| Path                                   | Purpose                                                           | Loaded       |
| -------------------------------------- | ----------------------------------------------------------------- | ------------ |
| `INJECT.md`                            | Always-on quick reference                                         | Always       |
| `SKILL.md`                             | Decision guide: selection, workflow, rules, checklist             | On activation|
| `LEARNED.md`                           | Corrections, preferences, discovered conventions                 | First, every session |
| `references/diagram-selection.md`      | Question → diagram matrix with worked examples                    | On demand    |
| `references/notation-cheatsheet.md`    | UML notation per type, Mermaid + PlantUML equivalents             | On demand    |
| `references/mermaid-patterns.md`       | Full Mermaid examples per type                                    | On demand    |
| `references/plantuml-patterns.md`      | Full PlantUML examples (activity lanes, use case, C4, deployment) | On demand    |
| `references/process-modeling-guide.md` | 7-step process modeling method                                    | On demand    |
| `references/test-derivation.md`        | State tables, path lists, traceability                            | On demand    |
| `references/tooling.md`                | Renderers, generators, CI                                         | On demand    |
| `references/code-style.md`             | Naming, IDs, header, direction, theming                           | On demand    |
| `references/security-checklist.md`     | Severity-classified confidentiality checks                        | On demand    |
| `references/common-issues.md`          | Render failures and fixes                                         | On demand    |
| `references/ai-interaction-guide.md`   | Calibration, anti-dependency                                      | On demand    |
| `references/diagram-template.{mmd,puml}` | Copy-paste starters                                             | On demand    |
| `assets/`                              | Header block, Mermaid site config, pre-commit hook                | Copy as-is   |
| `scripts/validate-diagrams.sh`         | Render check + orphan-image detection                             | Run          |
| `agents/`                              | flow-extractor, diagram-reviewer, drift-detector (read-only)      | On delegation|

## Data Flow of a Diagram Task

1. Request → classify mode (Teaching / Efficient / Diagnostic) → read LEARNED.md
2. Detect notation + placement convention (existing `*.mmd`/`*.puml`/fenced blocks) or apply Mermaid default
3. Select diagram type from the reader's question
4. Extract model from code (inline, or flow-extractor for 3+ files) → steps/participants/states with source paths
5. Author with header + accessibility lines → validate render
6. Report (type + why, path, element count, INFERRED items) → offer test-derivation table

## Recommended Repo Layout for Diagrams (INFERRED default — adapt to YOUR_PROJECT)

| Location                                 | Content                                        |
| ---------------------------------------- | ---------------------------------------------- |
| `path/to/your/doc.md`                    | Embedded ` ```mermaid ` for single-use diagrams |
| `docs/diagrams/<area>/*.mmd` / `*.puml`  | Reused or CI-rendered diagrams                 |
| `docs/diagrams/generated/`               | Code-generated class/package/ER output         |
| `docs/diagrams/_style.iuml`              | Shared PlantUML style                          |
| `docs/adr/`                              | ADRs embedding diagrams of the decision        |
