# Mermaid Patterns — Canonical, Render-Checked Shapes

> Synthetic "order" domain. Replace names with YOUR_PROJECT's domain language found in code or the business glossary. Every example carries the header + `accTitle`/`accDescr`. Targets Mermaid ≥10 syntax that GitHub renders (no beta diagram types).

## 1. Activity with Swimlanes (flowchart + subgraphs)

```mermaid
%% Title: Refund approval
%% Question: What steps and decisions does a refund go through, and who owns each?
%% Audience: Support + Finance
%% Source of truth: path/to/your/refund_service.ext :: RefundService.process
%% Last verified: YYYY-MM-DD
flowchart LR
    accTitle: Refund approval activity
    accDescr: Customer requests a refund, support validates it, finance approves amounts above the limit, and the refund is issued or rejected.
    Start((Start)) --> Req
    subgraph cust["Customer"]
        Req[Request refund]
    end
    subgraph support["Support Agent"]
        Val[Validate order] --> Elig{Eligible?}
        Elig -->|no| Rej[Reject refund]
        Elig -->|yes| Amt{Amount > limit?}
    end
    subgraph fin["Finance"]
        Appr{Approved?}
        Issue[Issue refund]
    end
    Req --> Val
    Amt -->|no| Issue
    Amt -->|yes| Appr
    Appr -->|yes| Issue
    Appr -->|no| Rej
    Issue --> Done(((Done)))
    Rej --> Done
```

Notes: every diamond edge labeled; one start; one explicit end; lanes = one owner each; direction `LR` because lanes read top-to-bottom as rows.

## 2. Sequence with `alt`, `loop`, `par`, activation, async

```mermaid
%% Title: Checkout payment
%% Question: Which calls happen, in what order, when a customer pays?
%% Audience: Backend engineers
%% Source of truth: path/to/your/checkout_controller.ext :: CheckoutController.pay
%% Last verified: YYYY-MM-DD
sequenceDiagram
    accTitle: Checkout payment sequence
    accDescr: The web app calls the order API, which charges the payment gateway with retries, then publishes an OrderPaid event and notifies the customer in parallel.
    autonumber
    actor C as Customer
    participant W as Web App
    participant API as Order API
    participant PG as Payment Gateway
    participant MQ as Message Broker
    C->>W: Click Pay
    W->>+API: POST /orders/{id}/pay
    loop up to 3 attempts
        API->>+PG: charge(amount, token)
        PG-->>-API: result
    end
    alt charge succeeded
        par
            API-)MQ: OrderPaid
        and
            API-)W: push receipt
        end
        API-->>W: 200 OK
    else declined
        API-->>W: 402 Payment Required
    else gateway timeout
        API-->>W: 504 Gateway Timeout
    end
    deactivate API
    W-->>C: Show result
```

Notes: `->>` sync, `-->>` reply, `-)` async; `autonumber` makes steps citable in reviews and test IDs.

## 3. State Machine with Composite State and Choice

```mermaid
%% Title: Order lifecycle
%% Question: What states can an Order be in, and what moves it between them?
%% Audience: Backend + QA
%% Source of truth: path/to/your/order_model.ext :: OrderStatus
%% Last verified: YYYY-MM-DD
stateDiagram-v2
    accTitle: Order lifecycle state machine
    accDescr: An order starts as Draft, becomes Placed on submit, goes through payment and fulfilment inside Active, and ends Delivered or Cancelled.
    [*] --> Draft
    Draft --> Placed: submit [items > 0]
    Placed --> Active: pay / reserveStock
    state Active {
        [*] --> Paid
        Paid --> Packed: pack
        Packed --> Shipped: ship / notifyCustomer
    }
    state check <<choice>>
    Placed --> Cancelled: cancel
    Active --> check: deliveryReported
    check --> Delivered: [signed]
    check --> Active: [not signed]
    Active --> Cancelled: cancel [not shipped] / refund
    Delivered --> [*]
    Cancelled --> [*]
```

Notes: states are adjectives/past participles; transitions `event [guard] / action`; every state reachable and every non-final state has an exit.

## 4. Class Diagram with Every Relationship Type

```mermaid
%% Title: Order domain model
%% Question: How are the core order-domain types related?
%% Audience: Backend engineers
%% Source of truth: path/to/your/domain/ (GENERATED — do not hand-edit)
%% Last verified: YYYY-MM-DD
classDiagram
    accTitle: Order domain class diagram
    accDescr: Customer places Orders; an Order is composed of LineItems referencing Products; payments implement PaymentMethod.
    class Customer {
        +String id
        +String email
        +placeOrder() Order
    }
    class Order {
        -Money total
        +OrderStatus status
        +addItem(Product, int)
        #recalculate()
    }
    class LineItem {
        +int quantity
    }
    class Product {
        +String sku
    }
    class Catalog
    class PaymentMethod {
        <<interface>>
        +charge(Money) Receipt
    }
    class CardPayment
    class BaseEntity {
        <<abstract>>
        +String id
    }
    class Clock
    Customer "1" --> "0..*" Order : places
    Order "1" *-- "1..*" LineItem : composition
    LineItem "*" --> "1" Product : refers to
    Catalog o-- Product : aggregation
    PaymentMethod <|.. CardPayment : realization
    BaseEntity <|-- Order : generalization
    Order ..> Clock : dependency
```

Hand-authored class diagrams rot — generate this from code where a generator exists (see [tooling.md](tooling.md)).

## 5. ER Diagram

```mermaid
%% Title: Order storage schema
%% Question: How are order tables related?
%% Audience: Backend + Data
%% Source of truth: path/to/your/migrations/ (latest)
%% Last verified: YYYY-MM-DD
erDiagram
    accTitle: Order storage ER diagram
    accDescr: A customer places zero or more orders; each order has one or more line items; each line item references exactly one product.
    CUSTOMER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "referenced by"
    CUSTOMER {
        string id PK
        string email UK
    }
    ORDER {
        string id PK
        string customer_id FK
        string status
    }
    LINE_ITEM {
        string order_id FK
        string product_id FK
        int quantity
    }
    PRODUCT {
        string id PK
        string sku UK
    }
```

## 6. Component / C4-style Container (flowchart approximation)

```mermaid
%% Title: YOUR_PROJECT containers
%% Question: Which deployable parts exist and how do they talk?
%% Audience: Engineers, new joiners
%% Source of truth: path/to/your/docker-compose.yml
%% Last verified: YYYY-MM-DD
flowchart TB
    accTitle: YOUR_PROJECT container view
    accDescr: Users reach the web app, which calls the API; the API uses a database and publishes to a broker consumed by a worker.
    User([Customer])
    subgraph sys["YOUR_PROJECT"]
        Web["Web App<br/>(SPA)"]
        API["Order API<br/>(REST)"]
        Worker["Worker<br/>(async jobs)"]
        DB[("Orders DB")]
        MQ[["Message Broker"]]
    end
    PG["Payment Gateway<br/>(external)"]
    User -->|HTTPS| Web
    Web -->|JSON/HTTPS| API
    API -->|SQL| DB
    API -->|publish OrderPaid| MQ
    MQ -->|consume| Worker
    API -->|HTTPS| PG
```

Mermaid's native `C4Context` syntax is experimental and renders inconsistently on GitHub — prefer this approximation or C4-PlantUML.

## 7. Overview + Detail Linking

When an overview exceeds ~15 elements, collapse a region into one node and link the detail file:

- Overview node: `Pay["Process payment (see payment.sequence.mmd)"]`
- Optional clickable link (only with default `securityLevel: strict` + `click Pay href "path/to/detail.md"`) — Mermaid allows `href` links in strict mode; JS callbacks require `loose` and are forbidden (see [security-checklist.md](security-checklist.md)).
