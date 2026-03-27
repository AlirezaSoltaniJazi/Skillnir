# Test Automation Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are testing-specific overrides.

```
ROLE:     Senior test automation engineer analyzing a production test suite
GOAL:     Generate a production-grade test automation skill directory
SCOPE:    Test code + test infra only — ignore production business logic, UI components, API handlers
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Test Code Only

Scan directories: `test/`, `tests/`, `e2e/`, `integration/`, `spec/`, `__tests__/`, `cypress/`, `playwright/`, `wdio/`, `*.spec.*`, `*.test.*`, `*_test.*`, `test_*.*`

**Test Framework**

- Primary framework(s) (WebDriverIO/Playwright/Cypress/Selenium/Appium)
- Test runner (Mocha/Jest/Vitest/pytest/JUnit/TestNG/XCTest)
- Language (JavaScript/TypeScript/Python/Java/Kotlin/Swift)
- Assertion library (Chai/expect/assert/Hamcrest/AssertJ/custom)
- Package manager + key test dependencies

**Test Types Present**

- E2E/UI tests (browser, mobile automation)
- API/integration tests (HTTP endpoint testing)
- Component/visual tests (Storybook, snapshots)
- Performance/load tests (k6, Gatling, Locust, Artillery)
- Contract tests (Pact, Spring Cloud Contract)
- Which types exist vs missing?

**Test Architecture**

- Directory structure (flat, by feature, by layer, by type)
- Page object model (classes, functions, singletons)
- Service/API client layer abstraction
- Data store/state management (aliases, fixtures, factories)
- Helper/utility classes (waiters, loggers, reporters)
- Base classes/shared abstractions (BaseTest, BasePage, BaseService)

**Test Data**

- Strategy (factories, fixtures, seed data, API-generated, inline)
- Cleanup (teardown hooks, API cleanup, DB reset)
- Environment-specific data configuration
- Sensitive data handling (credentials, tokens, secrets)
- Data isolation (parallel-safe? shared state?)

**Configuration**

- Config files (wdio.conf, playwright.config, cypress.config, pytest.ini)
- Environment management (base URLs, credentials, feature flags)
- Browser/device config (headless, headed, mobile emulation)
- Parallel execution (workers, sharding, concurrent sessions)
- Retry + timeout configuration
- CI/CD integration

**Reporting**

- Reporters (Allure, Mochawesome, HTML, JUnit XML, custom)
- Screenshot/video capture on failure
- Logging patterns + test tagging (@smoke, @regression, @critical)

**UI Interaction** (for UI tests)

- Locator strategy (data-testid, CSS, XPath, accessibility selectors)
- Wait strategy (explicit, implicit, auto-waiting)
- Action patterns + wrappers
- Iframe/shadow DOM, file upload/download, multi-tab handling

**API Testing**

- HTTP client (built-in, Axios, supertest, requests, RestAssured)
- Request building + response validation patterns
- Auth handling in tests (token management, session setup)
- Mock server usage (MSW, WireMock, nock, responses)

**Code Quality in Tests**

- Naming conventions (files, describe/it blocks, functions)
- DRY patterns (shared fixtures, hooks, helper reuse)
- Assertion style (BDD expect/should vs assert vs custom matchers)
- Error handling + linting for test code

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_testing.md`:

1. **Test Architecture Patterns** — how this project structures test code
2. **Data Flow** — how test data is created, used, cleaned up
3. **Interaction Patterns** — how tests interact with system under test
4. **Coding Conventions** — test naming, file structure, assertion style
5. **Things to ALWAYS do** — non-negotiable test patterns
6. **Things to NEVER do** — anti-patterns explicitly avoided
7. **Framework-specific wisdom** — patterns unique to the detected test framework

---

## PHASE 3: BEST PRACTICES (priority order)

1. **Test isolation** — no shared state, no order dependency
2. **Deterministic tests** — eliminate flakiness, proper waits, retry strategies
3. **Test data management** — factory pattern, cleanup, idempotent setup
4. **Parallel execution safety** — no shared resources, unique identifiers
5. **Test pyramid/trophy** — appropriate balance of test types
6. **Page object best practices** — encapsulation, no assertions in POs
7. **CI/CD integration** — fast feedback, selective execution, reporting
8. **Assertion best practices** — one logical assertion per test, descriptive messages
9. **Configuration management** — environment-agnostic, externalized config
10. **Debugging** — screenshots, logs, video, trace
11. **Security testing integration** — auth, injection, OWASP in E2E
12. **Accessibility testing** — axe, Pa11y, WAVE in test suites
13. **Performance testing** — timing assertions, lighthouse, web vitals

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY test automation task — E2E tests, API tests, integration tests, page objects, test data setup, assertion patterns, test configuration, CI test pipelines, test debugging, flakiness investigation, test reporting, test architecture.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep` (test tools vary too widely for platform-specific scoping)

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills + scope boundaries (e.g., unit tests if E2E-only)
3. **Architecture** — test directory structure diagram, layer responsibilities, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Test naming, file naming, assertion style details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Data Management** — rules list, no code examples
8. **Reliability Rules** — bullet list, no code examples
9. **CI/CD Integration** — summary + link to references/ for pipeline config examples
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — config files, framework docs, test utilities
12. **Adaptive Interaction Protocols** — interaction modes with testing-specific detection signals (e.g., "how does this fixture work" for Teaching, "another test like X" for Efficient, "flaky test failure" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/architecture-guide.md` — test architecture, layers, data flow
- `references/code-style.md` — test naming, file naming, assertion conventions with examples
- `references/security-checklist.md` — auth testing, injection testing, OWASP checklists
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `references/api-test-patterns.md` — API/integration test patterns with examples (ALL code examples)
- `references/ui-test-patterns.md` — UI/E2E test patterns with examples
- `references/page-object-template.{{ext}}` — copy-paste PO boilerplate (use detected test language extension)
- `references/test-spec-template.{{ext}}` — copy-paste test spec boilerplate (use detected test language extension)
- `references/common-issues.md` — troubleshooting flakiness, timeouts, selectors
- `assets/config-example.{{ext}}` — test framework config template (use actual config extension: .ts, .js, .json, .ini)
- `scripts/validate-tests.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent              | Role                                                       | Tools               | Spawn When                                                               |
| ------------------ | ---------------------------------------------------------- | ------------------- | ------------------------------------------------------------------------ |
| flake-analyzer     | Flaky test root cause analysis and stability review        | Read Glob Grep Bash | Flaky test investigation, test stability review, retry pattern analysis  |
| coverage-analyzer  | Test coverage gap analysis and missing test identification | Read Glob Grep Bash | Coverage report review, missing test identification, dead code detection |
| test-data-designer | Test data strategy and fixture design                      | Read Glob Grep      | Fixture design, factory pattern review, data isolation analysis          |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/flake-analyzer.md` — flaky test root cause analysis agent
- `agents/coverage-analyzer.md` — coverage gap analysis agent
- `agents/test-data-designer.md` — test data strategy agent
