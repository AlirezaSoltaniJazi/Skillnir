# UML & Diagrams Skill Generator

> **Base instructions**: The shared base instructions (structure, quality gates, execution order) are already included above this prompt — do NOT attempt to read \_base-skill-generator.md from disk; it does not exist in the target project. Below are UML-specific overrides.

```
ROLE:     Senior software architect and technical modeler who keeps diagrams correct, small, and in sync with code
GOAL:     Generate a production-grade UML & diagramming skill directory
SCOPE:    Choosing, authoring, reviewing, generating, and maintaining UML / process diagrams as code
          (Mermaid first, PlantUML when Mermaid cannot express it) — for ANY project, including one with zero diagrams today
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/ (+ agents/ if warranted)
```

This is a cross-cutting skill (like security or accessibility): it applies to every language and stack. The generated skill MUST work in a project that has no diagram tooling yet — in that case it defaults to **Mermaid in Markdown** (renders natively on GitHub/GitLab, zero install) and records that default in LEARNED.md.

---

## PHASE 1: PROJECT SCAN — Diagrams & Modelable Behavior

**Existing diagrams & tooling**

- Diagram sources: `*.mmd`, `*.mermaid`, `*.puml`, `*.plantuml`, `*.iuml`, `*.d2`, `*.drawio`, `*.drawio.svg`, `*.excalidraw`, `*.dsl` (Structurizr)
- Embedded diagrams: ` ```mermaid ` / ` ```plantuml ` blocks in `*.md`, `*.mdx`, `*.rst`, ADRs
- Rendered images committed without a source (`docs/**/*.png|svg` with no sibling source) — flag as drift risk
- Where diagrams live (`docs/`, `docs/diagrams/`, `architecture/`, `adr/`, `wiki/`) and file-naming convention in use
- Docs platform and its diagram support: GitHub/GitLab Markdown, MkDocs (Material `pymdownx.superfences`), Docusaurus (`@docusaurus/theme-mermaid`), Sphinx (`sphinxcontrib-mermaid` / `sphinxcontrib-plantuml`), Azure DevOps wiki, Confluence plugins
- Render / lint tooling: `@mermaid-js/mermaid-cli` (`mmdc`), PlantUML jar / Docker image, Kroki, `pyreverse` (ships with pylint), IDE plugins
- CI steps that render or validate diagrams (pre-commit hooks, GitHub Actions, GitLab CI)
- Mermaid config / theme (`%%{init: ...}%%`, frontmatter `config:`, site-level `mermaid` config), PlantUML `!theme` / `skinparam` / shared `!include` style files

**Behavior worth modeling (discover candidates — do not diagram everything)**

- **Lifecycles → state machines**: status/state enums, `status` / `state` columns, FSM libraries (`transitions`, `django-fsm`, XState, Spring Statemachine, `stateless`), status-transition guards in services
- **Workflows → activity diagrams**: orchestration code (Celery chains, Temporal/Cadence workflows, Airflow/Prefect DAGs, AWS Step Functions, GitHub Actions pipelines), multi-step service methods with branching, approval flows
- **Interactions → sequence diagrams**: API routes calling other services, message producers/consumers (Kafka, RabbitMQ, SQS), auth/login/payment flows, webhook handlers, retries and timeouts
- **Structure → class / ER diagrams**: domain models, ORM models (Django, SQLAlchemy, JPA, Prisma, TypeORM), aggregate roots, interfaces/protocols
- **Topology → component / deployment / C4**: `docker-compose.yml`, Kubernetes manifests, Terraform, service directories in a monorepo
- **Actors & goals → use case diagrams**: roles/permissions definitions, user-facing features, README feature lists

**Team conventions**

- Diagram direction and style already used (TB vs LR, color usage, legends, titles)
- Whether diagrams carry owners, dates, or source-of-truth links
- Test-design artifacts that reference diagrams (state tables, path lists) — relevant for QA derivation

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_uml.md`:

1. **Tooling Decision** — primary notation (Mermaid / PlantUML / other) and WHY, based on what the docs platform renders; secondary notation and when it is allowed
2. **Diagram Inventory** — existing diagrams, their type, location, and whether they still match the code (CONFIRMED / STALE / UNKNOWN)
3. **Modeling Candidates** — top 5-10 lifecycles, workflows, and interactions in this codebase that deserve a diagram, each with its source-of-truth file path
4. **Placement & Naming** — where new diagrams go and how they are named in this project
5. **Things to ALWAYS do** — non-negotiable conventions observed or chosen
6. **Things to NEVER do** — anti-patterns seen in existing diagrams or ruled out
7. **Generation vs. Hand-authoring** — which diagrams can be generated from code (class/package via `pyreverse` or equivalent) and which must be hand-written (behavioral)
8. **Validation Path** — how diagrams are syntax-checked locally and in CI (existing, or the one this skill proposes)

---

## PHASE 3: BEST PRACTICES (numbered by priority)

1. **Pick the diagram from the question, not habit.** Steps + decisions + owners → activity (swimlanes). Who-calls-whom over time → sequence. One entity's lifecycle → state machine. Actor goals → use case. Structure → class/ER. System fit → C4 / component / deployment. Business process for non-engineers → BPMN (out of UML, say so).
2. **One diagram = one question, one audience, one abstraction level.** Write the question in the diagram header; if it answers two, split it.
3. **Size cap ~7-15 elements.** Beyond that, produce an overview diagram plus linked detail diagrams — dense diagrams are not read.
4. **Diagrams as code, next to the code they describe.** Text sources in the repo, reviewed in PRs as diffs; never commit a rendered image without its source.
5. **Behavior hand-written, structure generated.** Generate class/package diagrams from code (hand-drawn ones rot within weeks); hand-author activity/sequence/state diagrams from reading the code and link the source-of-truth path.
6. **Notation correctness.** Use real UML semantics: guards in `[brackets]`, labeled decision branches, one initial node, explicit final node(s), sync vs async vs reply arrows, `event [guard] / action` transition labels, correct class relationships (composition ≠ aggregation ≠ association). Wrong notation silently misleads readers.
7. **Process modeling order.** Scope (trigger, outcome, boundaries) → actors → happy path as verb-noun steps → decisions and exceptions → lanes/owners → completeness check (no dead ends, every loop exits) → review with a person who performs the process.
8. **Domain language in labels.** Actions are verb-noun ("Validate order"), states are adjectives/past participles ("Pending", "Approved"), participants use the names found in code or the business glossary.
9. **Layout discipline.** One flow direction per diagram, minimal crossing edges (reorder lanes/participants), consistent shapes, color only as a secondary cue plus a legend.
10. **Render check before done.** Every diagram MUST render without errors (`mmdc` / PlantUML `-checkonly` / Mermaid Live) before it is reported complete; target the Mermaid version the docs platform ships (GitHub lags upstream — avoid beta syntax there).
11. **Accessibility.** Mermaid `accTitle:` / `accDescr:` on every diagram; a one-paragraph prose summary next to complex diagrams so screen-reader and text-only readers get the same information.
12. **Drift control.** Header records source-of-truth path and last-verified date; the skill re-verifies diagrams touched by a code change and flags STALE ones rather than silently "fixing" them.
13. **Diagram-driven test design.** Derive tests from diagrams (see Knowledge Base §E) — state transitions, activity paths, sequence branches become explicit test cases.
14. **Confidentiality.** No secrets, internal hostnames/IPs, or customer data in diagrams; confidential diagrams never go to public render servers.

---

## KNOWLEDGE BASE (the generated skill MUST carry this into references/)

### A. Diagram selection matrix → `references/diagram-selection.md`

| Question the reader has                            | Diagram                         | Mermaid                              | PlantUML                          |
| -------------------------------------------------- | ------------------------------- | ------------------------------------ | --------------------------------- |
| What are the steps, decisions, and who owns each?  | Activity (with partitions)      | `flowchart` + `subgraph` lanes       | `@startuml` activity + `\|Lane\|` |
| Who calls whom, in what order, with what data?     | Sequence                        | `sequenceDiagram`                    | sequence                          |
| What states can X be in and what moves it?         | State machine                   | `stateDiagram-v2`                    | state                             |
| What can each actor do with the system?            | Use case                        | — (not supported; use PlantUML)      | usecase                           |
| How is the domain / code structured?               | Class                           | `classDiagram`                       | class                             |
| How is the data stored and related?                | ER (not UML, standard practice) | `erDiagram`                          | entity (IE notation)              |
| Which deployable parts exist and how do they talk? | Component / C4 container        | `flowchart` (C4 syntax experimental) | component / C4-PlantUML           |
| Where does it run?                                 | Deployment                      | `flowchart` approximation            | deployment                        |
| When do timing constraints matter?                 | Timing                          | —                                    | timing                            |

UML 2.5.1 defines 14 types (7 structural: class, object, component, composite structure, package, deployment, profile; 7 behavioral: use case, activity, state machine, sequence, communication, timing, interaction overview). In practice class, sequence, activity, state machine, and use case cover ~90% of needs — the skill should say so and not push rare types.

### B. Notation cheat-sheet → `references/notation-cheatsheet.md`

- **Activity**: initial node (filled circle), activity final (bullseye), flow final (circled X), decision/merge (diamond), fork/join (bar) for parallelism, guards `[condition]` on every decision edge, partitions = swimlanes (one owner each), object nodes for data passed between actions.
- **Sequence**: lifelines; synchronous call (solid line, filled arrowhead), asynchronous message (open arrowhead), reply (dashed); activation bars; combined fragments `alt` (if/else), `opt` (if), `loop`, `par`, `break`, `critical`, `ref`; create/destroy of participants.
- **State machine**: initial pseudostate, final state, transitions labeled `event [guard] / action`, `entry/` `exit/` `do/` internal activities, composite states, choice pseudostate, history state. A state is a condition that persists; an event is instantaneous — never name a state after an event.
- **Class**: visibility `+` public, `-` private, `#` protected, `~` package; multiplicity `1`, `0..1`, `*`, `1..*`; relationships — association (plain line), aggregation (hollow diamond, shared part), composition (filled diamond, part dies with whole), generalization (hollow triangle), realization (dashed + hollow triangle), dependency (dashed arrow).
- **Use case**: actors outside the system boundary; `<<include>>` = always performed, `<<extend>>` = conditionally performed at an extension point; actor generalization for role hierarchies.

### C. Tooling matrix → `references/tooling.md`

| Tool                      | Use when                                                                   | Notes                                                                                                                              |
| ------------------------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Mermaid                   | Default. Flowchart, sequence, state, class, ER, Gantt, journey             | Native on GitHub/GitLab/Azure DevOps; Live editor at mermaid.live; CLI `npx -p @mermaid-js/mermaid-cli mmdc`                       |
| PlantUML                  | Full UML: real activity swimlanes, use case, component, deployment, timing | Needs Java (or Docker `plantuml/plantuml`); `!pragma layout smetana` avoids the Graphviz dependency; `-checkonly` validates syntax |
| pyreverse                 | Class/package diagrams generated from Python                               | Part of pylint: `pyreverse -o mmd -p <name> <pkg>` (also `-o puml`)                                                                |
| C4-PlantUML / Structurizr | Architecture views (context, container, component)                         | Prefer over UML component diagrams for "how does it fit together"                                                                  |
| D2                        | Large architecture diagrams needing better auto-layout                     | Extra install; fewer native renderers                                                                                              |
| draw.io                   | Free-form, stakeholder-facing visuals                                      | Save as `.drawio.svg` — displayable image AND editable source in one file                                                          |
| Excalidraw                | Throwaway whiteboard sketches                                              | Not for maintained docs                                                                                                            |
| Kroki                     | One HTTP renderer for Mermaid, PlantUML, D2, BPMN, …                       | Self-host for confidential content                                                                                                 |

The generated skill MUST also name the equivalent code-to-diagram generator for the detected language when one exists (verify it is installed or documented in the project; otherwise mark INFERRED).

### D. Syntax gotchas → `references/common-issues.md`

- Mermaid flowchart: a node labeled lowercase `end` breaks parsing — capitalize or quote it.
- Mermaid flowchart: a node ID starting with `o` or `x` right after `---`/`-->` is parsed as a circle/cross edge — add a space or capitalize.
- Mermaid: quote labels containing `()[]{}:;#` → `A["Retry (max 3)"]`; comments are `%%`.
- Mermaid subgraph titles with spaces need an ID: `subgraph qa["QA Lead"]`.
- Mermaid state diagrams: use `stateDiagram-v2`; `[*]` is both start and end.
- Mermaid sequence: `->>` sync, `-->>` reply, `-)` async; `autonumber` for referenceable steps; `+`/`-` suffix for activation.
- GitHub renders a Mermaid version that lags upstream — new/beta diagram types may render locally but fail on GitHub.
- PlantUML: every diagram between `@startuml` / `@enduml`; activity "new syntax" (`:action;`, `if () then`) — never mix with legacy syntax.
- Rendered-image drift: an SVG/PNG with no source cannot be reviewed — regenerate from source or delete.

### E. Diagram-driven test design → `references/test-derivation.md`

- **State machine** (ISTQB CTFL v4.0 state transition testing): build a state table; derive _all states_ coverage, _valid transitions (0-switch)_ coverage, and _all transitions_ coverage (valid + attempted invalid transitions that must be rejected). Each missing arrow in the diagram is a negative test.
- **Activity diagram**: one test per decision outcome (decision coverage), loops at 0 / 1 / many iterations, one test per exception exit, parallel branches checked for ordering assumptions.
- **Sequence diagram**: each message = a contract assertion (request shape, response shape, status); each `alt`/`opt` branch = a test; each reply error path (4xx/5xx/timeout) = a negative test; async messages get idempotency/retry tests.
- **Use case**: main success scenario + each alternate flow + each exception flow = one scenario (maps directly to Gherkin `Scenario`s).
- Output as a traceability table: diagram element → test case ID → existing test file (CONFIRMED) or "missing".

### F. Security & confidentiality → `references/security-checklist.md` (severity-classified)

- **Critical**: secrets, tokens, credentials, or connection strings in diagram labels/notes.
- **High**: confidential diagrams rendered via public servers (public PlantUML server, public Kroki) — the diagram source is transmitted and encoded into the URL; use the local jar/CLI or a self-hosted renderer. Mermaid Live share links also embed the full source.
- **High**: Mermaid `securityLevel` set to `loose` (enables HTML labels and click callbacks) on a site rendering untrusted diagram content — XSS risk (OWASP A03 Injection); keep the default `strict`.
- **Medium**: PlantUML `!include` / `!includeurl` pulling remote files — pin to repo-local includes.
- **Medium**: internal hostnames, IPs, account IDs, or customer names in diagrams published outside the team.
- **Low**: architecture diagrams revealing unannounced components in public repos — confirm audience first.

---

## OUTPUT CONTRACT FOR DIAGRAMS THE SKILL PRODUCES

The generated SKILL.md MUST instruct the consuming AI to:

1. **Place** diagrams where the project already keeps them; if none exist, embed ` ```mermaid ` blocks in the relevant Markdown doc, and use standalone files under `docs/diagrams/<area>/<name>.<type>.mmd` only when a diagram is reused or rendered by CI.
2. **Start every diagram with a header** (Mermaid `%%` / PlantUML `'` comments): Title, Question it answers, Audience, Source of truth (file path + symbol), Last verified (`YYYY-MM-DD`). Template in `assets/diagram-header-template.md`.
3. **Add `accTitle` / `accDescr`** (Mermaid) or a `title` + `caption` (PlantUML).
4. **Validate** the diagram renders (via `scripts/validate-diagrams.sh`, or state explicitly that no renderer was available and the Live editor must be used).
5. **Report** in chat: diagram type chosen and why (one line), the path written, elements count, and any INFERRED steps the reader must confirm — never paste the full diagram back if it was written to a file.
6. **Offer** (do not auto-generate) the derived test-case table for behavioral diagrams.

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY diagramming or modeling task — UML, activity diagram, sequence diagram, state machine / state diagram, class diagram, use case diagram, ER diagram, component / deployment diagram, C4, flowchart, process flow, swimlanes, "draw", "diagram", "visualize the flow", "model this process", Mermaid, PlantUML, draw.io, pyreverse, diagram review, fixing a diagram that won't render, updating stale diagrams, deriving test cases from a diagram.

**`allowed-tools`**: `Read Edit Write Glob Grep WebFetch Bash(npx:*) Bash(mmdc:*) Bash(plantuml:*) Bash(java:*) Bash(docker:*) Bash(pyreverse:*)` — add `Agent` only if agents/ is generated. `WebFetch` is for checking current Mermaid/PlantUML syntax docs when a construct is uncertain, never for sending diagram content anywhere.

**`metadata.sdlc-phase`**: `development`

**Body sections** (all required in SKILL.md):

1. **Before You Start** — announcement rule, read LEARNED.md, detect the project's primary notation (or apply the Mermaid default)
2. **When to Use** — 5-7 trigger conditions (explain a flow, document a process, review a diagram, diagram won't render, code changed under a diagram, derive tests from a lifecycle)
3. **Do NOT Use** — cross-references: long-form architecture docs / wiki (wiki generator or docs skills), threat models (security skill), writing the test code itself (testing / test-design skills), UI mockups (ui-ux-designer skill)
4. **Diagram Selection** — the question → diagram table (short form of §A) with this project's notation column
5. **Project Diagram Map** — existing diagrams, location, status (CONFIRMED / STALE), plus the top modeling candidates from Phase 2 with source-of-truth paths
6. **Authoring Workflow** — the numbered process-modeling order (Best Practice 7) plus the output contract steps
7. **Notation Rules** — rules table per diagram type (one line each); full cheat-sheet in references/notation-cheatsheet.md
8. **Style Rules** — direction, size cap, naming (verb-noun actions, adjective states), header, legend, accessibility
9. **Generation from Code** — which diagrams to generate, the exact command for this project, where output goes
10. **Validation & CI** — local render check, CI hook (existing or proposed), GitHub Mermaid-version caveat
11. **Test Derivation** — summary rules per diagram type + link to references/test-derivation.md
12. **Review Checklist** — 8-12 checks (question stated, ≤15 elements, one start / explicit end, every decision branch labeled, no dead ends, lanes owned, correct arrows, renders, source-of-truth linked, no confidential data)
13. **Anti-Patterns** — what NOT to do with WHY (diagramming everything, mixing abstraction levels, images without sources, states named after events, unlabeled decision branches, color-only meaning, hand-maintained class diagrams)
14. **Communication Style** — per base template
15. **Freedom Levels** — per base template (MUST: header + render check + no secrets; SHOULD: Mermaid default, size cap; CAN: theme, layout direction per diagram type)
16. **Session Protocols** (≤20 lines) — detection signals: Teaching ("what is a sequence diagram", "which diagram should I use"), Efficient ("another state diagram like the order one", "just draw it"), Diagnostic ("diagram won't render", "parse error", "GitHub shows a blank block"); self-learning via LEARNED.md
17. **References** — links to references/ and assets/

**Suggested reference files**:

- `LEARNED.md` — template (Corrections, Preferences, Discovered Conventions); first entry records the chosen primary notation and why
- `references/diagram-selection.md` — full selection matrix with worked "question → diagram" examples from this project
- `references/notation-cheatsheet.md` — UML notation per diagram type (§B) with Mermaid and PlantUML equivalents
- `references/mermaid-patterns.md` — full, rendering-verified examples: swimlane activity, sequence with `alt`/`loop`/`par`, state machine with composite state, class diagram with all relationship types, ER — each using this project's real domain names
- `references/plantuml-patterns.md` — activity with `|Lane|` partitions, use case with include/extend, component, deployment, C4-PlantUML container view
- `references/code-style.md` — diagram style guide: IDs vs labels, naming, direction, header format, theming, file naming
- `references/process-modeling-guide.md` — the step-by-step process-modeling method with a worked example from this codebase
- `references/test-derivation.md` — §E with a state table and path-list template
- `references/tooling.md` — §C plus install/run commands for this project's OS/CI
- `references/security-checklist.md` — §F, severity-classified
- `references/common-issues.md` — §D plus fixes for render failures seen in this repo
- `references/ai-interaction-guide.md` — anti-dependency strategies (e.g., ask the user to list the steps before drawing; offer a skeleton for the user to complete in Teaching mode)
- `references/diagram-template.mmd` and `references/diagram-template.puml` — copy-paste starters with header + accessibility lines
- `assets/diagram-header-template.md` — the header block
- `scripts/validate-diagrams.sh` — finds `*.mmd`/`*.puml` files and ` ```mermaid ` blocks in Markdown, renders Mermaid via `mmdc` to a temp dir and PlantUML via `-checkonly`, skips gracefully (non-zero only on real syntax errors) when a renderer is not installed, and flags committed images with no sibling source

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation (typically: many existing diagrams, or a large codebase with several modelable flows), include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                                          | Tools          | Spawn When                                                         |
| ---------------- | ----------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------ |
| flow-extractor   | Reads code and returns steps, participants, states, and transitions as a list | Read Glob Grep | Diagramming a flow spread across 3+ files or services              |
| diagram-reviewer | Reviews diagrams against the notation rules and review checklist              | Read Glob Grep | PR touching diagrams, "review this diagram", pre-release doc audit |
| drift-detector   | Compares diagrams' source-of-truth code against the diagram and reports STALE | Read Glob Grep | Code change under a diagrammed area, periodic docs audit           |

All three are read-only — only the parent writes diagram files. Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/flow-extractor.md` — read-only code-to-model extraction agent
- `agents/diagram-reviewer.md` — read-only notation and checklist review agent
- `agents/drift-detector.md` — read-only diagram-vs-code drift agent
