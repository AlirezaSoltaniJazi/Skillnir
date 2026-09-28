# Tooling — Renderers, Generators, CI

## Tool Matrix

| Tool                      | Use when                                                                   | Notes                                                                                           |
| ------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| Mermaid                   | Default. Flowchart, sequence, state, class, ER, Gantt, journey             | Native on GitHub/GitLab/Azure DevOps; Live editor at mermaid.live; CLI `mmdc`                   |
| PlantUML                  | Full UML: real activity swimlanes, use case, component, deployment, timing | Needs Java or Docker `plantuml/plantuml`; `!pragma layout smetana` avoids Graphviz; `-checkonly` validates |
| pyreverse                 | Class/package diagrams from Python                                         | Ships with pylint                                                                               |
| C4-PlantUML / Structurizr | Architecture views (context, container, component)                         | Prefer over UML component diagrams for "how does it fit together"                               |
| D2                        | Large architecture diagrams needing better auto-layout                     | Extra install; few native renderers                                                             |
| draw.io                   | Free-form, stakeholder-facing visuals                                      | Save as `.drawio.svg` — image + editable source in one file                                     |
| Excalidraw                | Throwaway whiteboard sketches                                              | Not for maintained docs                                                                         |
| Kroki                     | One HTTP renderer for Mermaid, PlantUML, D2, BPMN                          | Self-host for confidential content                                                              |

## Docs Platform Support

| Platform            | Mermaid                                    | PlantUML                              |
| ------------------- | ------------------------------------------ | ------------------------------------- |
| GitHub / GitLab     | Native ` ```mermaid ` (version lags upstream) | No (GitLab: only if instance enables it) |
| Azure DevOps wiki   | `::: mermaid` blocks                       | No                                    |
| MkDocs Material     | `pymdownx.superfences` custom fence        | `plantuml-markdown` plugin            |
| Docusaurus          | `@docusaurus/theme-mermaid`                | remark plugin / Kroki                 |
| Sphinx              | `sphinxcontrib-mermaid`                    | `sphinxcontrib-plantuml`              |
| Confluence          | Marketplace app                            | Marketplace app                       |

## Commands

```bash
# Mermaid — render/validate one file (no global install)
npx -y -p @mermaid-js/mermaid-cli mmdc -i path/to/diagram.mmd -o /tmp/out.svg

# Mermaid — render every mermaid block in a Markdown file (writes *.md with image refs)
npx -y -p @mermaid-js/mermaid-cli mmdc -i path/to/doc.md -o /tmp/doc-rendered.md

# PlantUML — syntax check only (jar)
java -jar path/to/plantuml.jar -checkonly path/to/diagram.puml

# PlantUML — Docker, no Java install
docker run --rm -v "$PWD":/data plantuml/plantuml -checkonly /data/path/to/diagram.puml
```

## Code-to-Diagram Generators (structure only — behavior is hand-written)

| Language         | Generator                                            | Command (INFERRED — verify installed)                           |
| ---------------- | ---------------------------------------------------- | --------------------------------------------------------------- |
| Python           | pyreverse (pylint)                                   | `pyreverse -o mmd -p YOUR_PROJECT path/to/package` (also `-o puml`) |
| Java / Kotlin    | IntelliJ UML, PlantUML Gradle/Maven plugins, jQAssistant | IDE export or build plugin                                  |
| TypeScript / JS  | tplant, ts-uml, dependency-cruiser (module graph)    | `npx tplant -i 'src/**/*.ts' -o out.puml`                       |
| C# / .NET        | PlantUmlClassDiagramGenerator                        | `puml-gen path/to/src out/ -dir`                                |
| Go               | goplantuml                                           | `goplantuml -recursive path/to/pkg > out.puml`                  |
| Database schema  | SchemaSpy, mermerd, prisma-erd-generator             | `mermerd -c "$DSN" -o out.mmd` (never commit `$DSN`)            |
| Django / SQLAlchemy | django-extensions `graph_models`, eralchemy      | `python manage.py graph_models app -o out.dot`                  |

Rules: generated output goes to a generated dir (e.g. `docs/diagrams/generated/`), header says `GENERATED — do not hand-edit`, regenerate in CI or on demand; prune to the classes that answer the question (use `-c`/filters) rather than dumping the whole package.

## CI — Proposed GitHub Actions Job

```yaml
name: diagrams
on:
  pull_request:
    paths: ["**/*.mmd", "**/*.puml", "**/*.md"]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: "21" }
      - run: bash path/to/skills/diagramArchitect/scripts/validate-diagrams.sh .
```

Pin action versions by SHA in security-sensitive repos. Pre-commit alternative: a `local` hook running the same script on staged `*.mmd|*.puml|*.md`.

## GitHub Mermaid Version Caveat

GitHub bundles a Mermaid version that lags upstream by months. New/beta types (`architecture-beta`, `block-beta`, `packet-beta`, some `C4*`) can render in Mermaid Live and in `mmdc` yet show an error box on GitHub. Stick to: `flowchart`, `sequenceDiagram`, `stateDiagram-v2`, `classDiagram`, `erDiagram`, `gantt`, `journey`, `pie`, `mindmap`, `timeline`.
