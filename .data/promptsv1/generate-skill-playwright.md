# Playwright Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Playwright-specific overrides.

```
ROLE:     Senior Playwright test automation engineer analyzing a production Playwright test suite
GOAL:     Generate a production-grade Playwright automation skill directory
SCOPE:    Playwright test code only — tests/, pages/, fixtures, playwright.config, utilities. Ignore application source code, other test frameworks
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Playwright Only

Ignore application source code and other test frameworks. Scan for:

**Configuration**

- playwright.config.ts patterns (projects, use, webServer, reporter)
- Base URL configuration
- Retries and workers settings
- Timeout configuration
- Trace, screenshot, and video settings
- Global setup/teardown files

**Fixtures**

- test.extend usage and custom fixture definitions
- Worker vs test fixture scoping
- Auto fixtures
- Fixture dependencies and composition
- Fixture teardown patterns
- Merging fixtures from multiple files

**Page Object Model**

- Class structure and inheritance
- Locator encapsulation patterns
- Action methods and assertion helpers
- Component objects
- Base page patterns

**Assertions**

- expect patterns and usage
- Custom matchers (expect.extend)
- Soft assertions
- Polling assertions (toPass)
- Visual assertions (toHaveScreenshot, toMatchSnapshot)
- Negation patterns

**Network**

- route/fulfill/abort patterns
- Request interception strategies
- HAR recording and replay
- APIRequestContext for API testing
- Mock patterns and response modification

**Emulation**

- Device emulation configuration
- Viewport settings
- Locale and timezone
- Geolocation and permissions
- Color scheme and reducedMotion

**Debugging & Tracing**

- trace.zip analysis patterns
- Playwright Inspector usage
- Codegen usage
- Screenshot on failure configuration
- Video recording setup
- Step annotations (test.step)
- Console log capture

**Parallel Execution**

- Workers configuration
- Sharding (--shard) setup
- test.describe.parallel usage
- test.describe.serial usage
- fullyParallel configuration
- Test isolation patterns

**CI/CD**

- Docker image (mcr.microsoft.com/playwright) usage
- GitHub Actions configuration
- Azure Pipelines configuration
- Retry strategies
- Artifact storage
- Blob reporter setup

**Accessibility**

- @axe-core/playwright integration
- Accessibility scanning patterns
- ARIA assertions

**Component Testing**

- Experimental CT setup
- Mount patterns
- Framework integrations (React, Vue, Svelte)

**API Testing**

- Request context usage
- APIRequestContext patterns
- Standalone API test suites
- Combined UI+API test patterns

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_playwright.md`:

1. **Architecture Patterns** — how this project structures Playwright tests, fixtures, and page objects
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected Playwright configuration and project setup
7. **Test conventions** — fixture design, assertion patterns, test organization

---

## PHASE 3: BEST PRACTICES

Integrate for the detected Playwright configuration and project setup:

1. Fixture-first design (test.extend for shared setup, avoid beforeEach/afterEach when fixtures suffice)
2. Locator best practices (defer to locator skill for deep strategy, prefer getByRole/getByText/getByTestId)
3. Auto-waiting over explicit waits (trust Playwright's auto-wait, avoid page.waitForTimeout)
4. Test isolation via browser contexts (new context per test, avoid shared state)
5. Visual regression management (toHaveScreenshot with maxDiffPixelRatio, update baselines deliberately)
6. Network mocking discipline (route/fulfill for deterministic tests, HAR for regression)
7. CI optimization (sharding for speed, selective retry with --retries, trace on first retry)
8. Trace-based debugging over console.log (attach traces on failure, use Playwright Inspector)
9. API testing for setup/teardown (APIRequestContext for data seeding, avoid UI for test data)
10. Accessibility as default (@axe-core/playwright scan in smoke tests)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Playwright task — test creation, fixture design, page object development, playwright.config changes, assertions, network mocking, visual testing, tracing, CI pipeline setup, accessibility testing, API testing, debugging test failures.

**`allowed-tools`**: `Read Edit Write Bash(npx:*) Bash(npm:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (frontend skill for web app UI, backend skill for API code)
3. **Architecture** — test structure diagram, key directories, fixture/page object data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only (TypeScript conventions, imports). Full formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only (add new test, create page object, add fixture), no code blocks
7. **Testing Standards** — rules list + link to references/
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for test data handling, credential management
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, Playwright docs
12. **Adaptive Interaction Protocols** — interaction modes with Playwright-specific detection signals (e.g., "fixture error" for Diagnostic, "another test like X" for Efficient, "how does test.extend work" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/playwright-config-patterns.md` — configuration patterns and examples
- `references/fixture-patterns.md` — fixture design, composition, and teardown examples
- `references/page-object-template.ts` — copy-paste page object template
- `references/network-mocking-guide.md` — route/fulfill patterns, HAR usage examples
- `references/visual-testing-guide.md` — screenshot comparison, baseline management
- `references/code-style.md` — import order, TypeScript conventions, formatting with full examples
- `references/security-checklist.md` — test data handling, credential management, CI secrets
- `references/common-issues.md` — troubleshooting common Playwright pitfalls
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `assets/ci-config-example.yml` — CI pipeline configuration template
- `scripts/validate-playwright.sh` — test structure + convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                    | Tools                          | Spawn When                                                       |
| ---------------- | ------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| test-reviewer    | Read-only test analysis against SKILL.md patterns       | Read Glob Grep                 | PR review, test audit, pattern compliance check                  |
| fixture-designer | Fixture architecture and composition analysis           | Read Glob Grep                 | Fixture refactoring, new fixture design, dependency analysis     |
| flake-analyzer   | Flaky test detection and root cause analysis            | Read Glob Grep Bash            | Test instability, intermittent failures, CI flake investigation  |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/test-reviewer.md` — read-only Playwright test analysis agent
- `agents/fixture-designer.md` — fixture architecture and composition agent
- `agents/flake-analyzer.md` — flaky test detection and root cause agent
