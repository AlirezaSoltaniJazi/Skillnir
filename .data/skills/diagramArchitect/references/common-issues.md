# Common Issues — Render Failures & Fixes

## Mermaid

| Symptom                                             | Cause                                                        | Fix                                                        |
| --------------------------------------------------- | ------------------------------------------------------------ | ---------------------------------------------------------- |
| `Parse error ... Expecting ... got 'end'`           | Node labeled/ID'd lowercase `end` in a flowchart             | `End`, `Finish`, or `E["end"]`                             |
| Edge renders as circle/cross, not arrow             | Node ID starting with `o`/`x` right after `--`: `A---oB`     | Space or capitalize: `A --- oB` → `A --- Ob`, or rename    |
| `Parse error` on a label                            | Unquoted `()[]{}:;#` in label                                | Quote: `A["Retry (max 3)"]`; `#` → `#35;`                  |
| Subgraph title shows as ID / parse error            | Title with spaces and no ID                                  | `subgraph qa["QA Lead"]`                                   |
| State diagram features missing                      | Using legacy `stateDiagram`                                  | `stateDiagram-v2`                                          |
| Sequence arrows wrong semantics                     | Mixed-up arrow syntax                                        | `->>` sync, `-->>` reply, `-)` async                       |
| Activation error "inactive participant"             | `-` deactivation without matching `+`                        | Pair every `+` with one `-` on the same participant        |
| Choice state rendered as normal box                 | Transition referenced the ID before `state x <<choice>>`     | Declare `state x <<choice>>` before first use              |
| Blank block / error box on GitHub, fine locally     | Beta/new syntax newer than GitHub's bundled Mermaid          | Use stable types only (see [tooling.md](tooling.md))       |
| `%%` comment breaks diagram                         | Comment containing `{}` placed like a directive              | Keep comments plain text; directives only as `%%{init: …}%%` |
| Colors invisible in dark mode                       | Hard-coded light fills                                       | `neutral` theme or classDef with contrast in both modes    |
| Crossing-edge spaghetti                             | Declaration order drives layout                              | Declare nodes in flow order; reorder subgraphs/participants |
| Markdown fence not rendered                         | Fence written as ` ```Mermaid ` or indented in list          | Lowercase ` ```mermaid `, no indentation                   |

## PlantUML

| Symptom                                   | Cause                                                   | Fix                                              |
| ----------------------------------------- | ------------------------------------------------------- | ------------------------------------------------ |
| "No @startuml found"                      | Missing delimiters                                      | Wrap in `@startuml` / `@enduml`                  |
| Activity renders garbage                  | Mixed legacy `(*) -->` and new `:action;` syntax        | Use new syntax only                              |
| "Cannot find Graphviz"                    | Non-sequence diagram without `dot` installed            | `!pragma layout smetana` or Docker image         |
| Lanes out of order                        | Lane order = first appearance                           | Declare all `\|Lane\|` at top in desired order   |
| `!include` fails in CI                    | Relative path resolved from CWD                         | Use `-I` / path relative to the file; vendor files |
| Use case arrows backwards                 | include/extend direction confusion                      | include: base → included; extend: extension → base |

## Drift & Repo Hygiene

| Symptom                                           | Fix                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------- |
| `docs/*.png` / `*.svg` with no sibling source     | Regenerate from source, or recreate as `.mmd`; delete orphan image  |
| Diagram names a class/state that no longer exists | Mark STALE in header, report to user; update only after confirming  |
| Hand-drawn class diagram diverges from code        | Replace with generated output (see [tooling.md](tooling.md))        |
| `Last verified` older than last change to source  | Re-verify against source-of-truth path; bump date only after check  |

## Quick Diagnostic Order

1. Paste into the renderer (`mmdc` / `-checkonly`) and read the line number
2. Bisect: comment out half the edges with `%%` until it renders
3. Check reserved words and unquoted special characters on the failing line
4. Check the target renderer's Mermaid version (GitHub vs local)
