# UML Notation Cheat-Sheet (with Mermaid + PlantUML equivalents)

Wrong notation silently misleads readers — a dashed arrow that should be solid changes "waits for reply" into "fire and forget".

## Activity Diagram

| UML element           | Meaning                                 | Mermaid flowchart                  | PlantUML (new syntax)         |
| --------------------- | --------------------------------------- | ---------------------------------- | ----------------------------- |
| Initial node          | Filled circle; exactly one per diagram  | `Start((" "))` or `Start([Start])` | `start`                       |
| Activity final        | Bullseye; ends the whole activity       | `Done(((" ")))` or `Done([Done])`  | `stop`                        |
| Flow final            | Circled X; ends one flow only           | `FF((x))` + note                   | `end` (inside branch) / `kill`|
| Action                | Rounded rectangle, verb-noun            | `A[Validate order]`                | `:Validate order;`            |
| Decision / merge      | Diamond                                 | `D{Stock available?}`              | `if (Stock available?) then (yes)` |
| Guard                 | `[condition]` on each outgoing edge      | `D -->\|yes\| B`                   | `then (yes)` / `else (no)`    |
| Fork / join           | Bar — parallel start / sync             | `F[" "]` styled as bar (approx.)   | `fork` / `fork again` / `end fork` |
| Partition (swimlane)  | One owner per lane                      | `subgraph cust["Customer"]`        | `\|Customer\|`                |
| Object node           | Data passed between actions             | `O[/Invoice/]`                     | `:Invoice] ` (SDL) or note    |
| Loop                  | Back-edge with exit guard                | edge back to earlier node          | `repeat` / `repeat while ()`, `while ()` |

Rules: every decision edge labeled; every loop has an exit; no action without an outgoing edge except finals.

## Sequence Diagram

| UML element            | Meaning                                  | Mermaid              | PlantUML            |
| ---------------------- | ---------------------------------------- | -------------------- | ------------------- |
| Synchronous call       | Solid line, filled arrowhead; caller waits | `A->>B: call()`    | `A -> B : call()`   |
| Asynchronous message   | Open arrowhead; caller continues          | `A-)B: event`       | `A ->> B : event`   |
| Reply                  | Dashed line                               | `B-->>A: result`    | `B --> A : result`  |
| Activation bar         | Participant is executing                  | `A->>+B` / `B-->>-A`| `activate B` / `deactivate B` |
| Create participant     | Lifeline starts mid-diagram               | `create participant C` | `create C`       |
| Destroy                | Lifeline ends (X)                         | `destroy C`         | `destroy C`         |
| `alt`                  | if / else                                 | `alt ... else ... end` | same             |
| `opt`                  | if (no else)                              | `opt ... end`       | same                |
| `loop`                 | repetition                                | `loop ... end`      | same                |
| `par`                  | parallel                                  | `par ... and ... end` | `par ... else ... end` |
| `break`                | exit enclosing fragment                   | `break ... end`     | same                |
| `critical`             | atomic region                             | `critical ... end`  | `critical ... end`  |
| `ref`                  | reference to another diagram              | `Note over A,B: ref: Login` | `ref over A,B : Login` |

## State Machine

| UML element          | Meaning                                         | Mermaid `stateDiagram-v2`     | PlantUML                  |
| -------------------- | ----------------------------------------------- | ----------------------------- | ------------------------- |
| Initial pseudostate  | Entry point                                     | `[*] --> Draft`               | `[*] --> Draft`           |
| Final state          | Terminal                                        | `Closed --> [*]`              | `Closed --> [*]`          |
| Transition label     | `event [guard] / action`                        | `A --> B: pay [amount>0] / charge` | same                 |
| Internal activities  | `entry/`, `exit/`, `do/`                        | `note right of A` (approx.)   | `A : entry / notify`      |
| Composite state      | Nested sub-states                               | `state Active { ... }`        | `state Active { ... }`    |
| Choice pseudostate   | Dynamic branch on guard                         | `state check <<choice>>`      | `state check <<choice>>`  |
| Fork / join          | Concurrent regions                              | `state f <<fork>>` / `<<join>>` | same                    |
| History              | Resume last sub-state                           | — (not supported)             | `[H]` / `[H*]`            |

**A state is a condition that persists; an event is instantaneous.** Never name a state after an event ("Submit" is an event; "Submitted" is a state).

## Class Diagram

| Element         | Notation                              | Mermaid                 | PlantUML               |
| --------------- | ------------------------------------- | ----------------------- | ---------------------- |
| Public          | `+`                                   | `+placeOrder()`         | same                   |
| Private         | `-`                                   | `-total`                | same                   |
| Protected       | `#`                                   | `#validate()`           | same                   |
| Package         | `~`                                   | `~helper()`             | same                   |
| Multiplicity    | `1`, `0..1`, `*`, `1..*`              | `Order "1" --> "1..*" LineItem` | same           |
| Association     | Plain line (knows about)              | `A --> B` / `A -- B`    | same                   |
| Aggregation     | Hollow diamond — shared part          | `Team o-- Player`       | same                   |
| Composition     | Filled diamond — part dies with whole | `Order *-- LineItem`    | same                   |
| Generalization  | Hollow triangle (inheritance)         | `Animal <\|-- Dog`      | same                   |
| Realization     | Dashed + hollow triangle (implements) | `IPayment <\|.. CardPayment` | same              |
| Dependency      | Dashed arrow (uses transiently)       | `Service ..> Logger`    | same                   |

Composition ≠ aggregation ≠ association. Test: "If the whole is deleted, is the part deleted?" yes → composition; "Can the part belong to several wholes?" yes → aggregation or association.

## Use Case Diagram (PlantUML only)

| Element                 | Meaning                                                  | PlantUML                         |
| ----------------------- | -------------------------------------------------------- | -------------------------------- |
| Actor                   | Role outside the system boundary                         | `actor Customer`                 |
| Use case                | User goal, verb-noun                                     | `usecase "Place order" as UC1`   |
| System boundary         | Rectangle                                                | `rectangle YOUR_PROJECT { ... }` |
| `<<include>>`           | Always performed as part of base use case                | `UC1 ..> UC2 : <<include>>`      |
| `<<extend>>`            | Conditionally performed at an extension point            | `UC3 ..> UC1 : <<extend>>`       |
| Actor generalization    | Role hierarchy                                           | `Admin --\|> User`               |

Include arrow points from base → included; extend arrow points from extension → base.

## ER Diagram (Mermaid crow's foot)

| Cardinality       | Left | Right |
| ----------------- | ---- | ----- |
| Zero or one       | `\|o` | `o\|` |
| Exactly one       | `\|\|` | `\|\|` |
| Zero or more      | `}o` | `o{` |
| One or more       | `}\|` | `\|{` |

`CUSTOMER ||--o{ ORDER : places` — solid `--` identifying, dotted `..` non-identifying.
