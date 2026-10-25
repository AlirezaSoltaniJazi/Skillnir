# Diagram-Driven Test Design

Behavioral diagrams are test oracles. Offer the derived table after drawing — do not auto-generate test code (that belongs to the testing skill).

## State Machine (ISTQB CTFL v4.0 — state transition testing)

1. Build a **state table**: every state × every event → next state or `—` (invalid)
2. Derive coverage levels:
   - **All states** — every state visited at least once
   - **Valid transitions (0-switch)** — every arrow in the diagram exercised once
   - **All transitions** — valid transitions + every invalid (state, event) pair attempted and **rejected**
3. Every missing arrow = a negative test.

### State Table Template (synthetic Order lifecycle)

| Current \ Event | submit         | pay            | cancel          | ship     | deliveryReported |
| --------------- | -------------- | -------------- | --------------- | -------- | ---------------- |
| Draft           | Placed [items>0] | —            | —               | —        | —                |
| Placed          | —              | Active/Paid    | Cancelled       | —        | —                |
| Active/Paid     | —              | —              | Cancelled/refund| —        | choice           |
| Active/Packed   | —              | —              | Cancelled/refund| Shipped  | choice           |
| Active/Shipped  | —              | —              | — [shipped]     | —        | Delivered [signed] |
| Delivered       | —              | —              | —               | —        | —                |
| Cancelled       | —              | —              | —               | —        | —                |

`—` cells → expect rejection (error, no state change, no side effect).

## Activity Diagram

| Element               | Test cases                                                   |
| --------------------- | ------------------------------------------------------------ |
| Decision              | One per outcome (decision coverage)                          |
| Loop                  | 0, 1, many iterations; exactly-at-limit and limit+1          |
| Exception exit        | One per exception final node                                 |
| Fork/join             | Branch completion in each order; one branch failing          |
| Lane hand-off         | Permission: wrong actor attempts the step → rejected         |

### Path List Template

| Path ID | Route (node IDs)                         | Expected outcome  | Test file / status          |
| ------- | ---------------------------------------- | ----------------- | --------------------------- |
| P1      | Start → Req → Val → Elig(yes) → Amt(no) → Issue → Done | Refund issued | path/to/your/test_file.ext / missing |
| P2      | … → Amt(yes) → Appr(yes) → Issue → Done  | Refund issued     | missing                     |
| P3      | … → Amt(yes) → Appr(no) → Rej → Done     | Refund rejected   | missing                     |
| P4      | … → Elig(no) → Rej → Done                | Refund rejected   | missing                     |

## Sequence Diagram

| Element                    | Test case                                                  |
| -------------------------- | ---------------------------------------------------------- |
| Each message               | Contract assertion: request shape, response shape, status  |
| Each `alt` / `opt` branch  | One test per branch                                        |
| Reply error paths          | 4xx, 5xx, timeout — each a negative test                   |
| `loop` with retries        | Succeeds on attempt N; exhausts retries                    |
| Async message (`-)`)       | Idempotency (duplicate delivery), retry, out-of-order      |
| `par`                      | No ordering assumption between parallel branches           |

## Use Case

Main success scenario + each alternate flow + each exception flow = one scenario. Maps 1:1 to Gherkin:

```gherkin
Scenario: Customer applies an expired voucher (extension UC3, exception)
  Given a placed order
  When the customer applies voucher "EXPIRED10"
  Then the voucher is rejected with "expired"
```

## Traceability Table (report format)

| Diagram element           | Test case ID | Existing test                          |
| ------------------------- | ------------ | -------------------------------------- |
| `Draft --submit--> Placed` | TC-ST-01    | path/to/your/test_order.ext::test_submit (CONFIRMED) |
| `Draft --pay--> —`         | TC-ST-02    | missing                                |
| `alt declined`             | TC-SQ-04    | missing                                |

Only mark CONFIRMED after reading the test file.
