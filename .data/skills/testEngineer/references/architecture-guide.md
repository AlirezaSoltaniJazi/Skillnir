# Test Architecture Guide

> Test directory structure, layer responsibilities, data flow, and design principles for production test suites.

---

## Layered Test Architecture

```
YOUR_PROJECT/
├── tests/                          # Test root
│   ├── e2e/                        # End-to-end UI tests
│   │   ├── specs/                  # Test spec files
│   │   │   ├── auth/               # Feature-grouped specs
│   │   │   │   ├── login.spec.ts
│   │   │   │   └── registration.spec.ts
│   │   │   ├── checkout/
│   │   │   └── dashboard/
│   │   ├── pages/                  # Page Object Model classes
│   │   │   ├── BasePage.ts         # Shared page abstractions
│   │   │   ├── LoginPage.ts
│   │   │   └── DashboardPage.ts
│   │   ├── components/             # Reusable component objects
│   │   │   ├── NavBar.ts
│   │   │   └── Modal.ts
│   │   ├── fixtures/               # Test data factories + setup
│   │   │   ├── users.ts
│   │   │   ├── products.ts
│   │   │   └── index.ts
│   │   └── helpers/                # Utility functions
│   │       ├── waits.ts
│   │       ├── auth.ts
│   │       └── api-client.ts
│   ├── api/                        # API/integration tests
│   │   ├── specs/
│   │   │   ├── users.api.spec.ts
│   │   │   └── orders.api.spec.ts
│   │   ├── clients/                # API client abstractions
│   │   │   ├── BaseClient.ts
│   │   │   └── UsersClient.ts
│   │   └── schemas/                # Response validation schemas
│   │       └── user.schema.ts
│   ├── component/                  # Component/visual tests
│   ├── performance/                # Load/performance tests
│   ├── support/                    # Cross-cutting test support
│   │   ├── conftest.py             # pytest shared fixtures (Python)
│   │   ├── global-setup.ts         # Global setup (JS/TS)
│   │   ├── global-teardown.ts      # Global teardown
│   │   └── custom-matchers.ts      # Extended assertions
│   └── config/                     # Test configuration
│       ├── environments.ts         # Environment-specific config
│       └── test-data.ts            # Static reference data
├── playwright.config.ts            # Framework config (example)
├── wdio.conf.ts                    # or WebDriverIO config
└── cypress.config.ts               # or Cypress config
```

---

## Layer Responsibilities

### Specs Layer (tests/e2e/specs/, tests/api/specs/)

- **Purpose**: Test scenarios — describe user behaviors and API contracts
- **Contains**: describe/it blocks, test functions, scenario steps
- **Rules**:
  - One logical assertion per test method
  - Tests read like user stories ("user logs in", "user adds item to cart")
  - No direct element selectors — delegate to page objects
  - No HTTP calls — delegate to API clients
  - No test data construction — delegate to fixtures/factories

### Page Objects Layer (tests/e2e/pages/)

- **Purpose**: Encapsulate UI interaction for a single page or view
- **Contains**: Locator definitions, action methods, state queries
- **Rules**:
  - NO assertions in page objects — return values, let specs assert
  - Each page object maps to one page/view in the application
  - Methods return `this` (fluent) or typed data (query results)
  - Locators use `data-testid` first, accessibility roles second, CSS last
  - Extend BasePage for shared navigation, header, footer interactions

### Fixtures Layer (tests/e2e/fixtures/, tests/support/)

- **Purpose**: Test data creation, setup, and teardown
- **Contains**: Factory functions, builder patterns, seed data
- **Rules**:
  - Factories generate unique data per invocation (parallel-safe)
  - Use API shortcuts for precondition setup (don't navigate UI)
  - Every created resource has a cleanup strategy
  - Sensitive data (passwords, tokens) comes from environment variables

### Helpers Layer (tests/e2e/helpers/)

- **Purpose**: Cross-cutting utilities reused across specs
- **Contains**: Custom waits, auth helpers, file upload utilities, retry logic
- **Rules**:
  - Stateless functions only — no instance state
  - No business logic — only test infrastructure
  - Typed parameters and return values

### API Clients Layer (tests/api/clients/)

- **Purpose**: Typed HTTP client wrappers for API testing
- **Contains**: Request builders, response parsers, auth token management
- **Rules**:
  - One client per API domain/resource
  - Extend BaseClient for shared auth, base URL, headers
  - Return typed response objects — not raw HTTP responses
  - Include request/response logging for debugging

---

## Data Flow

```
Test Spec
  │
  ├── calls ──► Page Object ──► Browser/Driver ──► Application UI
  │                │
  │                └── uses ──► Component Object (reusable parts)
  │
  ├── calls ──► API Client ──► HTTP ──► Application API
  │
  ├── uses ──► Fixture/Factory ──► Test Data (unique per test)
  │                │
  │                └── calls ──► API Client (precondition setup via API)
  │
  └── asserts ──► Expected values (from fixtures or inline)
```

**Key principle**: Specs orchestrate. Page objects interact. Fixtures provide data. Helpers provide utilities. Never mix responsibilities.

---

## Test Pyramid / Test Trophy

```
        ╱ E2E ╲               Few — critical user journeys only
       ╱────────╲
      ╱ API/Int  ╲            Many — contract + integration coverage
     ╱────────────╲
    ╱  Component   ╲          Many — isolated UI behavior
   ╱────────────────╲
  ╱    Unit Tests    ╲        Most — business logic, pure functions
```

| Type      | Count    | Speed    | Confidence | When to Write                      |
| --------- | -------- | -------- | ---------- | ---------------------------------- |
| E2E/UI    | Fewest   | Slowest  | Highest    | Critical user journeys, smoke      |
| API/Int   | Many     | Fast     | High       | Every API endpoint, integrations   |
| Component | Many     | Fast     | Medium     | Interactive components, edge cases |
| Unit      | Most     | Fastest  | Lowest     | Business logic, utilities, parsers |

---

## Environment Strategy

```
Test Config
  │
  ├── base config ──► shared settings (timeouts, retries, reporters)
  │
  ├── env override ──► environment-specific (base URL, credentials)
  │     ├── local
  │     ├── staging
  │     └── ci
  │
  └── runtime override ──► CLI flags, env vars (headless, workers)
```

Configuration should be layered: base defaults, environment overrides, runtime overrides. Never hard-code environment-specific values in test code.
