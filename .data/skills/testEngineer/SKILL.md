---
name: testEngineer
description: >-
  Test automation skill for E2E, API, integration, and component testing. Covers
  page object design, test data management, assertion patterns, fixture setup,
  CI/CD test pipelines, flakiness debugging, test configuration, parallel execution,
  and reporting. Activates when writing test specs, creating page objects, designing
  fixtures/factories, configuring test runners, investigating flaky tests, reviewing
  test coverage, or working with any test framework (Playwright/Cypress/WebDriverIO/
  Selenium/pytest/Jest/Vitest/JUnit/TestNG).
compatibility: "Playwright/Cypress/WebDriverIO/Selenium, Jest/Vitest/Mocha/pytest/JUnit, TypeScript/JavaScript/Python/Java"
metadata:
  author: skillnir
  version: "1.0.0"
  sdlc-phase: testing
allowed-tools: Read Edit Write Bash Glob Grep Agent
---

<!-- SKILL.md target: ≤300 lines / <3,500 tokens. Tables, rules, checklists, links only. Code examples go in references/. -->

## Before You Start

**Read [LEARNED.md](LEARNED.md) first.** It contains corrections, preferences, and conventions accumulated from previous sessions. Apply every rule in that file — they override defaults in this skill.

**Announce skill usage.** Always say "Using: testEngineer skill" at the very start of your response before doing any work.

## When to Use

1. Writing or modifying test specs (E2E, API, integration, component)
2. Creating or updating page objects, component objects, or API clients
3. Designing test data fixtures, factories, or seed strategies
4. Configuring test runners, reporters, or CI/CD test pipelines
5. Investigating flaky tests, timeouts, or selector failures
6. Reviewing test coverage gaps or test architecture decisions

## Do NOT Use

- **Production application code** (business logic, UI components, API handlers) — use your project's development skill
- **Unit tests for pure functions** (no browser/API interaction) — use your language-specific skill
- **CI/CD pipeline configuration** (Docker, workflows, infra) — use your devops skill
- **Performance/load test tooling** (k6, Gatling, Locust setup) — use specialized performance skill

## Architecture

```
tests/
├── e2e/specs/          # E2E test scenarios by feature
├── e2e/pages/          # Page Object Model classes
├── e2e/components/     # Reusable component objects
├── api/specs/          # API/integration tests
├── api/clients/        # Typed API client wrappers
├── fixtures/           # Test data factories
├── helpers/            # Shared utilities (waits, auth)
└── support/            # Global setup, custom matchers
```

**Data flow**: Spec → Page Object/API Client → Application → Assertion. Fixtures provide data. Helpers provide utilities. See [references/architecture-guide.md](references/architecture-guide.md).

## Key Patterns

| Pattern              | Approach                                         | Key Rule                                        |
| -------------------- | ------------------------------------------------ | ----------------------------------------------- |
| Page Object Model    | Class per page, encapsulated locators + actions  | NO assertions in page objects — return values   |
| Test Data Factories  | Functions generating unique data per invocation  | UUID/timestamp-based — parallel-safe            |
| Explicit Waits       | Framework auto-wait or targeted waitFor          | NEVER `sleep()` — always condition-based        |
| API Preconditions    | Setup test state via API, not UI navigation      | Faster, more reliable, decoupled from UI        |
| Locator Priority     | data-testid > role > label > text > CSS > XPath  | Stability decreases down the list               |
| Test Isolation       | Unique data, own context, cleanup in teardown    | No shared mutable state between tests           |
| Auth State Reuse     | Authenticate once, share storage state           | Token cache with expiry — not per-test login    |
| Response Validation  | Typed clients + schema validation                | Validate structure, not just status codes        |

See [references/ui-test-patterns.md](references/ui-test-patterns.md) and [references/api-test-patterns.md](references/api-test-patterns.md) for full code examples.

## Code Style

| Rule                  | Convention                                                            |
| --------------------- | --------------------------------------------------------------------- |
| Spec file naming      | `feature-name.spec.ts` / `test_feature_name.py` / `FeatureTest.java` |
| Page object naming    | `PascalCase.ts` / `snake_case_page.py`                               |
| Describe blocks       | Feature or page name: `describe('Login Page', ...)`                   |
| Test names            | Behavior-focused: `should display error for invalid credentials`      |
| One assertion per test | One logical assertion — multiple `expect` OK if same behavior        |
| Locator strategy      | `data-testid` first, accessibility roles second                       |
| Import order          | Framework → page objects → fixtures → helpers                         |
| Assertion style       | BDD `expect` for JS/TS, `assert` for Python, AssertJ for Java        |

See [references/code-style.md](references/code-style.md) for full naming and formatting examples.

## Common Recipes

1. **New E2E test**: Check if page object exists → create if needed → write spec in feature directory → use factories for data → add cleanup in afterAll
2. **New page object**: Identify page elements → use data-testid locators → create action methods (return void) → create query methods (return data) → extend BasePage
3. **New API test**: Create/extend API client → write CRUD lifecycle spec → add response schema validation → track created resources for cleanup
4. **New test data factory**: Create function returning unique data → use UUID/timestamp for identifiers → add cleanup helper → export from fixtures index
5. **Fix flaky test**: Remove `sleep()` → add explicit wait → check for shared state → ensure unique test data → verify cleanup runs
6. **Add to CI pipeline**: Configure headless mode → set worker count → add retry for CI → configure artifact capture → add JUnit reporter for CI integration

## Data Management

- Every test creates its own data — no shared mutable state
- Factories generate unique values per invocation (UUID, timestamp, random suffix)
- Preconditions set up via API calls, not UI navigation
- Cleanup happens in `afterEach`/`afterAll` — track created resource IDs
- Sensitive data (credentials, tokens) from environment variables only
- Static reference data (countries, categories) in config files, not inline

## Reliability Rules

- NEVER use `sleep()`, `waitForTimeout()`, `browser.pause()`, or `cy.wait(ms)` — use explicit waits or auto-retry assertions
- NEVER depend on test execution order — each test runs independently
- NEVER share browser state between tests — isolate contexts
- Use framework auto-waiting (Playwright, Cypress) before adding manual waits
- Add retry (`retries: 2`) in CI config only — not in local development
- Capture screenshots, video, and trace on failure — configure in test runner
- Use `data-testid` attributes — never rely on CSS classes or DOM structure
- Validate test stability: run new tests 10x before merging

## CI/CD Integration

- Headless mode in CI: `headless: true` or `--headed=false`
- Limit workers in CI: `workers: 2` (not `auto` — CI resources are shared)
- Retry only in CI: `retries: process.env.CI ? 2 : 0`
- Artifacts: screenshots + video + trace on failure, JUnit XML for CI parsers
- Cache browser binaries between CI runs
- Separate smoke suite (fast, critical paths) from full regression

See [assets/config-example.ts](assets/config-example.ts) for a complete framework configuration template.

## Anti-Patterns

| Anti-Pattern                                | Why It's Wrong                                                     |
| ------------------------------------------- | ------------------------------------------------------------------ |
| `sleep(3000)` for waits                     | Non-deterministic — too slow or too fast depending on environment  |
| Assertions inside page objects              | Violates encapsulation — specs own assertions, POs own interaction |
| Hard-coded test data                        | Parallel tests collide — use factories with unique values          |
| Testing implementation details              | Refactoring breaks tests — test observable behavior instead        |
| Shared mutable state between tests          | Order-dependent, flaky, impossible to parallelize                  |
| XPath/CSS selectors over data-testid        | Brittle — breaks on any markup change                              |
| UI navigation for test setup                | Slow and fragile — use API shortcuts for preconditions             |
| No cleanup in teardown                      | Data accumulates, tests interact, suite degrades over time         |
| Catch-all `try/catch` hiding test failures  | Swallows real failures — let assertions throw                      |
| Testing everything via E2E                  | Slow, expensive — use test pyramid (unit > API > E2E)              |

## Communication Style

- **Lead with the answer** — no preamble, no "Let me explain", no "Great question"
- **Strip filler words** — remove "basically", "essentially", "actually", "just", "simply" from responses
- **No trailing summaries** — the user can read the diff/output, don't restate what you did
- **Bullet points over paragraphs** — use lists, tables, one-liners
- **Code over explanation** — show the fix, not a lecture about the fix
- **Maximum 2-3 sentences** per explanation unless the user asks "why" or is in Teaching mode
- **No hedging** — say "do X" not "you might want to consider doing X"
- **No apologies** — don't say "sorry" for mistakes, just fix them

## Code Generation Rules

1. **Read before writing** — always read the target test file, page object, and related specs before making changes
2. **Match existing style** — follow the project's naming, assertion, and locator conventions exactly
3. **Page objects return data** — never put assertions in page objects; return values for specs to assert
4. **One behavior per test** — each test method verifies one logical behavior
5. **Cleanup always** — every test that creates data must clean it up in teardown
6. **On correction** — acknowledge, restate as rule, apply to all subsequent actions, write to [LEARNED.md](LEARNED.md)
7. **On ambiguity** — check [LEARNED.md](LEARNED.md) first, then existing test files, ask ONE question, write preference to [LEARNED.md](LEARNED.md)

## Adaptive Interaction Protocols

Corrections and preferences persist via [LEARNED.md](LEARNED.md).

| Mode       | Detection Signal                                                        | Behavior                                                             |
| ---------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------- |
| Diagnostic | "flaky test", "timeout", "selector not found", CI failure log           | Read test + error, trace to root cause, fix with minimal changes     |
| Efficient  | "another test like X", "add spec for Y", "same pattern as login tests" | Minimal explanation, replicate existing patterns, apply conventions   |
| Teaching   | "how does this fixture work", "explain page objects", "why auto-wait"  | Explain with references to project examples, link to references/     |
| Review     | "review these tests", "check my page object", "audit test coverage"    | Read-only analysis, check against conventions, report without changes |

**Self-Learning**: All learnings are **written** to LEARNED.md — not suggested, written:

- Corrections → `## Corrections` section
- Preferences → `## Preferences` section
- Discovered conventions → `## Discovered Conventions` section
- Format: `- YYYY-MM-DD: rule description`

## Sub-Agent Delegation

| Agent                                                    | Role                        | Spawn When                          | Tools              |
| -------------------------------------------------------- | --------------------------- | ----------------------------------- | ------------------- |
| [flake-analyzer](agents/flake-analyzer.md)               | Flaky test root cause analysis | "flaky test", stability review    | Read Glob Grep Bash |
| [coverage-analyzer](agents/coverage-analyzer.md)         | Test coverage gap analysis     | "what's untested", coverage audit | Read Glob Grep Bash |
| [test-data-designer](agents/test-data-designer.md)       | Test data strategy design      | Fixture design, data isolation    | Read Glob Grep      |

**Delegation rules**: Spawn when task is self-contained and won't need follow-up context. Never delegate tasks requiring architectural decisions. See [agents/](agents/) for full definitions.

## Freedom Levels

| Level             | Scope                                                                          | Examples                                                              |
| ----------------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| **MUST** follow   | No sleep, no assertions in POs, unique test data, cleanup, explicit waits      | "MUST use explicit waits", "MUST return values from page objects"     |
| **SHOULD** follow | data-testid locators, API preconditions, factory pattern, test pyramid balance | "SHOULD use data-testid", "SHOULD set up via API not UI"             |
| **CAN** customize | Fixture organization, page object inheritance depth, assertion library choice  | "CAN group fixtures by feature", "CAN use custom matchers"           |

## References

| File                                                                     | Description                                         |
| ------------------------------------------------------------------------ | --------------------------------------------------- |
| [LEARNED.md](LEARNED.md)                                                 | **Auto-updated.** Corrections, preferences, conventions |
| [INJECT.md](INJECT.md)                                                   | Always-loaded quick reference (hallucination firewall)   |
| [references/architecture-guide.md](references/architecture-guide.md)     | Test directory structure, layers, data flow               |
| [references/code-style.md](references/code-style.md)                     | Test naming, file naming, assertion conventions           |
| [references/ui-test-patterns.md](references/ui-test-patterns.md)         | Page objects, waits, UI interactions with examples        |
| [references/api-test-patterns.md](references/api-test-patterns.md)       | API clients, CRUD tests, mock servers with examples      |
| [references/security-checklist.md](references/security-checklist.md)     | Auth, authorization, injection, OWASP checklists         |
| [references/ai-interaction-guide.md](references/ai-interaction-guide.md) | Anti-dependency strategies, correction protocols         |
| [references/common-issues.md](references/common-issues.md)               | Flakiness, timeouts, selectors, CI troubleshooting       |
| [references/page-object-template.ts](references/page-object-template.ts) | Copy-paste page object boilerplate                       |
| [references/test-spec-template.ts](references/test-spec-template.ts)     | Copy-paste test spec boilerplate                         |
| [assets/config-example.ts](assets/config-example.ts)                     | Test framework configuration template                    |
| [scripts/validate-tests.sh](scripts/validate-tests.sh)                   | Test naming + convention checker                         |
| [agents/flake-analyzer.md](agents/flake-analyzer.md)                     | Flaky test root cause analysis agent                     |
| [agents/coverage-analyzer.md](agents/coverage-analyzer.md)               | Test coverage gap analysis agent                         |
| [agents/test-data-designer.md](agents/test-data-designer.md)             | Test data strategy design agent                          |
