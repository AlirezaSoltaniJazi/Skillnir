# Process Modeling Guide — Step by Step

Use this for any activity/swimlane or business-process diagram. Skipping steps produces diagrams with dead ends and missing owners.

## The Method

| # | Step                  | Output                                                            | Check                                        |
|---|-----------------------|-------------------------------------------------------------------|----------------------------------------------|
| 1 | **Scope**             | Trigger (what starts it), outcome(s), boundaries (what's out)     | One sentence each                            |
| 2 | **Actors**            | List of roles/systems that act                                     | Each maps to a lane or participant           |
| 3 | **Happy path**        | Ordered verb-noun steps from trigger to success outcome           | 5–12 steps; no branches yet                  |
| 4 | **Decisions & exceptions** | Each yes/no point, each failure/timeout/rejection path       | Every decision has all outcomes labeled      |
| 5 | **Lanes / owners**    | Assign each step to exactly one actor                              | No step without owner; no lane without steps |
| 6 | **Completeness**      | Walk every path start → end                                        | No dead ends; every loop exits; ≥1 final     |
| 7 | **Review**            | Walk-through with someone who performs the process                 | Their corrections recorded; INFERRED steps resolved |

## Worked Example (synthetic — "refund request")

1. **Scope** — Trigger: customer requests refund. Outcomes: refund issued / refund rejected. Out of scope: chargebacks via bank.
2. **Actors** — Customer, Support Agent, Finance, Payment Gateway (system).
3. **Happy path** — Request refund → Validate order → Issue refund → Notify customer.
4. **Decisions & exceptions**
   - `Eligible?` no → Reject refund
   - `Amount > limit?` yes → Finance approval; `Approved?` no → Reject refund
   - Gateway error → Retry (max 3) → escalate to Finance
5. **Lanes** — Request (Customer); Validate, Reject (Support); Approve, Issue (Finance); Notify (system).
6. **Completeness** — Paths: eligible+small, eligible+large+approved, eligible+large+rejected, ineligible, gateway-failure. All end at a final node; retry loop exits after 3.
7. **Review** — Mark any step read from code but not confirmed by a human as `INFERRED` in a note.

Resulting diagram shape: [mermaid-patterns.md §1](mermaid-patterns.md) / [plantuml-patterns.md §1](plantuml-patterns.md).

## Extracting a Process from Code

| Code signal                                   | Diagram element                  |
| --------------------------------------------- | -------------------------------- |
| Method sequence in a service/orchestrator     | Actions in order                 |
| `if` / `switch` / pattern match on domain data | Decision + labeled guards        |
| `raise` / `throw` / error return              | Exception path to a final node   |
| Retry decorators / loops with max attempts    | Loop with exit guard             |
| Task queue chains, workflow engines, DAGs     | Fork/join, async hand-off        |
| Permission checks / role guards               | Lane ownership                   |
| Status field assignments                       | State machine transitions (use a state diagram instead) |

Record the source-of-truth path + symbol in the header. If a step's owner or condition cannot be read from code, label it `INFERRED` and list it in the chat report.

## Stop Conditions

- The diagram now answers two questions → split
- More than ~15 elements → collapse a sub-process into one node and link a detail diagram
- The reviewer disputes the flow → code or process is wrong; flag, do not "fix" the diagram to match either silently
