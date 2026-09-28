# Diagram Style Guide (diagrams-as-code conventions)

## File Naming & Placement

| Situation                                        | Placement                                                        |
| ------------------------------------------------ | ---------------------------------------------------------------- |
| Project already keeps diagrams somewhere         | Follow it — record the location in LEARNED.md                    |
| Diagram explains one doc                         | Embedded ` ```mermaid ` block in that Markdown file              |
| Diagram reused in 2+ docs, or rendered by CI     | `docs/diagrams/<area>/<name>.<type>.mmd` (or `.puml`)            |
| Rendered image needed (slides, Confluence)       | Generate into a build dir from source; never commit image alone  |
| draw.io needed for stakeholders                  | `<name>.drawio.svg` — editable source and image in one file      |

File name pattern: `<kebab-subject>.<type>.<ext>` — `order-lifecycle.state.mmd`, `checkout-payment.sequence.mmd`, `refund-approval.activity.puml`. The `<type>` segment makes `Glob` searches and reviews trivial.

## Header (every diagram, first lines)

```text
%% Title: Order lifecycle
%% Question: What states can an Order be in, and what moves it between them?
%% Audience: Backend + QA
%% Source of truth: path/to/your/order_model.ext :: OrderStatus
%% Last verified: YYYY-MM-DD
```

PlantUML uses `'` instead of `%%`. Put the Mermaid header before the diagram keyword; `accTitle`/`accDescr` go right after it.

## IDs vs Labels

- **IDs**: short PascalCase or camelCase, no spaces, stable across edits (`ValOrder`, `api`). Diffs stay readable when labels change.
- **Labels**: domain language, quoted when containing `()[]{}:;#,` — `A["Retry (max 3)"]`.
- Never use `end`, `graph`, `subgraph`, `class`, `style`, `click` as a bare lowercase ID.
- One node per line; edges after node declarations in large diagrams.

## Naming

| Element           | Rule                       | Good                          | Bad                   |
| ----------------- | -------------------------- | ----------------------------- | --------------------- |
| Action            | Verb-noun                  | `Validate order`              | `Validation`, `Order` |
| State             | Adjective / past participle| `Pending`, `Approved`         | `Approve`, `Submit`   |
| Event             | Verb / past-tense event    | `submit`, `paymentFailed`     | `Submitted` (state)   |
| Decision          | Yes/no question            | `Stock available?`            | `Check stock`         |
| Participant/lane  | Name used in code/glossary | `Order API`, `Finance`        | `Service2`, `Box A`   |
| Message           | Method/endpoint or intent  | `POST /orders/{id}/pay`       | `call`                |

## Direction

| Diagram                   | Direction |
| ------------------------- | --------- |
| Flowchart with lanes      | `LR` (lanes as rows) or `TB` (lanes as columns) — one per diagram |
| Flowchart without lanes   | `TB`      |
| Component / C4            | `TB` (users top, data bottom) |
| State machine             | default (`TB`); `direction LR` for long linear lifecycles |

Never mix directions inside a diagram — nested `direction` in subgraphs only when it removes crossings.

## Layout Discipline

1. Order participants/lanes by first interaction — reduces crossing edges
2. Put the happy path in a straight line; exceptions branch off to one side
3. Consistent shapes: rectangle = action, diamond = decision, cylinder = store, stadium = actor/external
4. Color is secondary only — never the sole carrier of meaning; add a legend when used

## Theming

- Mermaid: prefer site-level config; per-diagram only via frontmatter `config:` block or `%%{init: {"theme": "neutral"}}%%`
- `neutral` / `default` themes render in both light and dark GitHub modes; custom hex colors often vanish in dark mode
- PlantUML: shared `_style.iuml` include; no per-diagram `skinparam` walls

## Size

- Target 7–15 elements. Above 15: overview diagram + linked detail diagrams.
- Labels ≤ 5 words; move detail into notes or the prose summary.
