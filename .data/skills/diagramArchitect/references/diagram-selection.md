# Diagram Selection — Question → Diagram

> Pick the diagram from the reader's question, not from habit. One diagram answers one question for one audience at one abstraction level.

## Selection Matrix

| Question the reader has                            | Diagram                         | Mermaid                              | PlantUML                        |
| -------------------------------------------------- | ------------------------------- | ------------------------------------ | ------------------------------- |
| What are the steps, decisions, and who owns each?  | Activity (with partitions)      | `flowchart` + `subgraph` lanes       | activity + `\|Lane\|`           |
| Who calls whom, in what order, with what data?     | Sequence                        | `sequenceDiagram`                    | sequence                        |
| What states can X be in and what moves it?         | State machine                   | `stateDiagram-v2`                    | state                           |
| What can each actor do with the system?            | Use case                        | — (not supported; use PlantUML)      | usecase                         |
| How is the domain / code structured?               | Class                           | `classDiagram`                       | class                           |
| How is the data stored and related?                | ER (not UML, standard practice) | `erDiagram`                          | entity (IE notation)            |
| Which deployable parts exist and how do they talk? | Component / C4 container        | `flowchart` (C4 syntax experimental) | component / C4-PlantUML         |
| Where does it run?                                 | Deployment                      | `flowchart` approximation            | deployment                      |
| When do timing constraints matter?                 | Timing                          | —                                    | timing                          |
| Business process for non-engineers                 | BPMN (NOT UML — say so)         | `flowchart` approximation            | — (use bpmn.io / Camunda Modeler) |

## UML 2.5.1 Coverage

UML defines 14 diagram types:

- **Structural (7)**: class, object, component, composite structure, package, deployment, profile
- **Behavioral (7)**: use case, activity, state machine, sequence, communication, timing, interaction overview

Class, sequence, activity, state machine, and use case cover ~90% of real needs. Do not push rare types (composite structure, profile, interaction overview) — readers rarely know their notation, so they communicate less than a simpler diagram.

## Decision Order (when two diagrams seem to fit)

1. Is the question about **one entity changing over time**? → State machine
2. Is it about **messages between named parts, ordered in time**? → Sequence
3. Is it about **steps, branches, and owners**? → Activity with lanes
4. Is it about **what users can do**, not how? → Use case
5. Is it about **shape of code or data**? → Class (code) / ER (storage)
6. Is it about **how systems fit together / where they run**? → C4 container / deployment

## Worked Examples (synthetic — replace with YOUR_PROJECT names)

| Developer request                                           | Chosen diagram                      | Why                                                                 |
| ----------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------- |
| "How does an order go from placed to shipped?"              | State machine of `Order.status`     | One entity, persistent conditions, events move it                   |
| "What happens when the user clicks Pay?"                    | Sequence (UI → API → PaymentGateway) | Ordered calls across participants, sync vs async matters            |
| "Document the refund approval process for the support team" | Activity with lanes (Customer, Agent, Finance) | Steps + decisions + owners, non-engineer audience        |
| "What can an admin do that a viewer can't?"                 | Use case (PlantUML)                 | Actor goals, role generalization                                     |
| "How are `Order`, `LineItem`, `Product` related?"            | Class (generated) or ER             | Structure — generate from code/schema, never hand-maintain          |
| "Which services talk to the message broker?"                | C4 container view                   | System-fit question, abstraction above classes                      |
| "Explain order checkout" (vague)                            | Ask: steps/owners, or calls over time? | The request contains two questions — split into activity + sequence |

## Split Signals

Split into overview + detail diagrams when any is true:

- More than ~15 elements (nodes, participants, states)
- Two audiences (e.g. support staff and backend engineers)
- Mixed abstraction (service boxes next to class methods)
- Header "Question" line needs "and"
