# PlantUML Patterns — When Mermaid Cannot Express It

> Use PlantUML only for: true activity swimlanes with fork/join, use case, component, deployment, timing, C4. Everything else → Mermaid (zero-install rendering on GitHub/GitLab).
> Every file: `@startuml` … `@enduml`, `'` comment header, `title` + `caption`. Use `!pragma layout smetana` to avoid the Graphviz dependency.

## 1. Activity with `|Lane|` Partitions and Fork/Join

```plantuml
@startuml refund-approval
' Title: Refund approval
' Question: What steps and decisions does a refund go through, and who owns each?
' Audience: Support + Finance
' Source of truth: path/to/your/refund_service.ext :: RefundService.process
' Last verified: YYYY-MM-DD
!pragma layout smetana
title Refund approval
caption Customer requests, support validates, finance approves large amounts.
|Customer|
start
:Request refund;
|Support Agent|
:Validate order;
if (Eligible?) then (yes)
  if (Amount > limit?) then (yes)
    |Finance|
    if (Approved?) then (yes)
    else (no)
      :Reject refund;
      stop
    endif
  else (no)
  endif
  |Finance|
  fork
    :Issue refund;
  fork again
    :Record ledger entry;
  end fork
  |Customer|
  :Receive confirmation;
else (no)
  :Reject refund;
endif
stop
@enduml
```

Never mix new syntax (`:action;`, `if () then`) with legacy syntax (`(*) --> "action"`) — the parser fails or silently misrenders.

## 2. Use Case with Include / Extend and Actor Generalization

```plantuml
@startuml order-use-cases
' Title: Order use cases
' Question: What can each actor do with YOUR_PROJECT's ordering features?
' Audience: Product + QA
' Source of truth: path/to/your/permissions.ext :: ROLES
' Last verified: YYYY-MM-DD
!pragma layout smetana
title Order use cases
caption Admins inherit all customer goals and can additionally issue refunds.
left to right direction
actor Customer
actor Admin
actor "Payment Gateway" as PG <<system>>
Admin --|> Customer
rectangle YOUR_PROJECT {
  usecase "Place order" as UC1
  usecase "Pay for order" as UC2
  usecase "Apply voucher" as UC3
  usecase "Authenticate" as UC4
  usecase "Issue refund" as UC5
}
Customer --> UC1
Customer --> UC2
Admin --> UC5
UC2 --> PG
UC1 ..> UC4 : <<include>>
UC3 ..> UC1 : <<extend>>
@enduml
```

## 3. Component Diagram

```plantuml
@startuml components
' Title: Order components
' Question: Which components make up the order service and which interfaces do they expose?
' Audience: Backend engineers
' Source of truth: path/to/your/order_service/
' Last verified: YYYY-MM-DD
!pragma layout smetana
title Order service components
caption Provided interfaces are lollipops; required are sockets.
package "Order Service" {
  [Order API] as api
  [Order Domain] as domain
  [Payment Adapter] as pay
  interface "REST /orders" as rest
  interface PaymentPort
}
rest - api
api --> domain
domain --> PaymentPort
PaymentPort - pay
pay --> [Payment Gateway] : HTTPS
@enduml
```

## 4. Deployment Diagram

```plantuml
@startuml deployment
' Title: Production deployment
' Question: Where does each YOUR_PROJECT part run?
' Audience: Ops + Engineers
' Source of truth: path/to/your/k8s/ or path/to/your/terraform/
' Last verified: YYYY-MM-DD
!pragma layout smetana
title Production deployment
caption No hostnames or IPs — logical names only.
node "Kubernetes cluster" {
  node "api pod" as apiPod {
    artifact "order-api image" as apiImg
  }
  node "worker pod" as workerPod {
    artifact "order-worker image" as workerImg
  }
}
database "Managed Postgres" as db
queue "Managed Broker" as mq
cloud "Payment Gateway" as pg
apiPod --> db
apiPod --> mq
mq --> workerPod
apiPod --> pg : HTTPS
@enduml
```

## 5. C4-PlantUML Container View

```plantuml
@startuml c4-container
' Title: YOUR_PROJECT container view
' Question: How do YOUR_PROJECT's containers fit together?
' Audience: Engineers, architects
' Source of truth: path/to/your/docker-compose.yml
' Last verified: YYYY-MM-DD
!include path/to/vendored/C4_Container.puml
title YOUR_PROJECT — Container view
Person(customer, "Customer")
System_Boundary(sys, "YOUR_PROJECT") {
  Container(web, "Web App", "SPA", "Customer UI")
  Container(api, "Order API", "REST", "Order logic")
  ContainerDb(db, "Orders DB", "SQL")
  ContainerQueue(mq, "Broker", "AMQP/Kafka")
}
System_Ext(pg, "Payment Gateway")
Rel(customer, web, "Uses", "HTTPS")
Rel(web, api, "Calls", "JSON/HTTPS")
Rel(api, db, "Reads/writes")
Rel(api, mq, "Publishes OrderPaid")
Rel(api, pg, "Charges", "HTTPS")
SHOW_LEGEND()
@enduml
```

Vendor `C4_Container.puml` into the repo and `!include` it locally — `!includeurl` to GitHub pulls remote code at render time (see [security-checklist.md](security-checklist.md)).

## 6. Timing Diagram

```plantuml
@startuml timing
' Title: Session timeout
' Question: When does an idle session expire relative to the token refresh?
' Audience: Backend + Security
' Source of truth: path/to/your/session_config.ext
' Last verified: YYYY-MM-DD
title Session timeout timing
robust "Session" as S
concise "Client" as C
@0
S is Active
C is Idle
@300
C is Requesting
@310
C is Idle
@900
S is Expired
@enduml
```

## 7. Shared Style File

Keep one repo-local style include instead of per-diagram `skinparam` blocks:

```plantuml
' path/to/your/docs/diagrams/_style.iuml
skinparam shadowing false
skinparam defaultFontName "Helvetica"
skinparam ArrowColor #333333
skinparam ActivityBorderColor #333333
```

Use with `!include _style.iuml` right after `@startuml`.
