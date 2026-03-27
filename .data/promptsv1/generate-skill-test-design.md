# Test Case Design Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are test-design-specific overrides.

```
ROLE:     Senior QA engineer / test architect analyzing a production codebase for test strategy
GOAL:     Generate a production-grade test case design skill directory
SCOPE:    Test strategy, coverage, and scenario design — NOT test automation code (use the "testing" scope for automation)
OUTPUT:   SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Test Design Focus

Scan the ENTIRE codebase (not just test dirs) to understand what needs testing:

**Application Domain**

- What does the application do? (API, web app, mobile, CLI, data pipeline, library)
- Who are the users? (end users, developers, internal teams, API consumers)
- Critical user journeys (login, CRUD, payment, data processing, etc.)
- Business rules and domain logic locations
- External integrations (APIs, databases, message queues, file storage)

**Existing Test Coverage**

- What test types exist? (unit, integration, E2E, contract, performance, security)
- What test types are MISSING?
- Coverage metrics (if available)
- Test file organization and naming
- Which features/modules have no tests?

**Risk Areas**

- Security-sensitive code (auth, payments, PII handling, encryption)
- Data integrity points (transactions, migrations, concurrent access)
- External service dependencies (API calls, webhooks, third-party SDKs)
- Edge cases in business logic (boundaries, nulls, concurrent operations)
- Performance-critical paths (queries, bulk operations, file processing)

**API Surface** (if applicable)

- Endpoints and HTTP methods
- Request/response schemas
- Authentication/authorization flows
- Error responses and status codes
- Rate limiting and pagination

**Data Model**

- Key entities and relationships
- Validation rules and constraints
- State transitions (status workflows, lifecycle)
- Soft-delete, archival, or audit patterns

**Configuration & Environment**

- Environment-specific behavior (dev/staging/prod)
- Feature flags or toggles
- Configuration-driven behavior

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_test-design.md`:

1. **Test Coverage Map** — what's tested, what's missing, priority gaps
2. **Risk Matrix** — high-risk areas ranked by impact and likelihood
3. **User Journey Map** — critical paths that need E2E coverage
4. **Boundary Analysis** — edge cases, limits, error conditions per feature
5. **Test Type Recommendations** — which type fits each area (unit/integration/E2E)
6. **Things to ALWAYS test** — non-negotiable test scenarios
7. **Things commonly missed** — blind spots in the current test suite

---

## PHASE 3: BEST PRACTICES

Integrate for the detected stack:

- Test pyramid / test trophy — right balance of test types for this project
- Equivalence partitioning — group inputs into equivalent classes
- Boundary value analysis — test at limits, just inside, just outside
- State transition testing — verify all valid state changes AND invalid transitions
- Decision table testing — combinatorial coverage for complex business rules
- Error guessing — based on common bugs in the detected framework
- Pairwise/combinatorial testing — efficient coverage of parameter combinations
- Security test scenarios — OWASP-aligned test cases
- Performance test scenarios — load, stress, endurance patterns
- Accessibility test scenarios — WCAG 2.1 AA coverage
- API contract testing — request/response validation, backward compatibility
- Data integrity testing — concurrent access, transaction isolation, migration safety
- Negative testing — invalid inputs, unauthorized access, resource exhaustion

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY test design task — test strategy, test case writing, coverage analysis, scenario identification, edge case discovery, test plan creation, risk-based testing, boundary analysis, test prioritization, regression test selection.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (test planning, coverage gaps, new features, risk analysis)
2. **Do NOT Use** — test automation code (use "testing" scope), CI/CD pipeline config (use "infra" scope)
3. **Test Strategy** — project-specific test type allocation (what to unit test vs integration vs E2E)
4. **Key Scenarios** — summary table only (feature, scenario category, priority). Full scenario lists in references/
5. **Boundary Analysis** — rules table for identified boundaries and limits
6. **Common Recipes** — step lists for designing tests for new features, APIs, state machines
7. **Coverage Gaps** — known untested areas ranked by risk
8. **Security Test Scenarios** — summary + link to references/security-test-scenarios.md
9. **Negative Testing** — patterns for invalid inputs, error conditions, unauthorized access
10. **Anti-Patterns** — what NOT to do in test design (with why)
11. **References** — test scenario files, coverage reports, risk matrices
12. **Adaptive Interaction Protocols** — interaction modes with test-design-specific detection signals (e.g., "what should I test for this feature" for Teaching, "same pattern as X feature" for Efficient, "test is flaky" for Diagnostic), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/test-scenarios.md` — comprehensive test scenario lists per feature (ALL detailed scenarios go here)
- `references/boundary-analysis.md` — boundary values, equivalence classes, edge cases
- `references/security-test-scenarios.md` — OWASP-aligned security test cases
- `references/api-test-matrix.md` — endpoint x method x auth x status code coverage matrix
- `references/common-issues.md` — commonly missed test scenarios and blind spots
- `assets/test-case-template.md` — copy-paste test case template (Given/When/Then format)
- `scripts/validate-coverage.sh` — coverage gap checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent              | Role                                                   | Tools                     | Spawn When                                                               |
| ------------------ | ------------------------------------------------------ | ------------------------- | ------------------------------------------------------------------------ |
| risk-analyzer      | Risk-based test prioritization and regression analysis | Read Glob Grep            | Test strategy review, regression prioritization, risk assessment         |
| scenario-generator | Test scenario generation with boundary analysis        | Read Edit Write Glob Grep | "generate test cases for X", boundary analysis, equivalence partitioning |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/risk-analyzer.md` — risk-based test prioritization agent
- `agents/scenario-generator.md` — test scenario generation agent
