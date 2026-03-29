# WebDriverIO Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are WebDriverIO-specific overrides.

```
ROLE:     Senior WebDriverIO test automation engineer analyzing a production WDIO test suite
GOAL:     Generate a production-grade WebDriverIO automation skill directory
SCOPE:    WDIO test code only — tests/, pages/, wdio.conf, custom commands, services, utilities. Ignore application source code, other test frameworks
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — WebDriverIO Only

Ignore application source code and other test frameworks. Scan for:

**Configuration**

- wdio.conf.js/ts structure and organization
- Capabilities (desiredCapabilities vs W3C format)
- Services array and service configuration
- Reporters array and reporter configuration
- Hooks (onPrepare, onComplete, beforeTest, afterTest, before, after)
- Framework selection (mocha/jasmine/cucumber)
- Specs and suites organization
- baseUrl configuration

**Custom Commands**

- browser.addCommand usage and patterns
- element.addCommand usage and patterns
- Overwriting existing commands
- TypeScript declarations for custom commands

**Services**

- devtools service usage
- chromedriver service
- selenium-standalone service
- appium service
- visual service (wdio-image-comparison-service)
- sauce and browserstack services
- intercept service
- shared-store service

**Page Objects**

- WDIO POM patterns (getter-based locators with `get`)
- Chainable action methods
- Base page class inheritance
- Component objects
- Lazy evaluation of locators

**WebDriver BiDi**

- v8+ BiDi protocol features
- Bidirectional communication patterns
- CDP integration via devtools service
- Network interception via BiDi

**Parallel & Multi-Remote**

- maxInstances configuration
- Capabilities array for parallel execution
- Multiremote setup for multi-browser testing
- shardTestFiles usage

**Reporters**

- Allure reporter setup
- Spec reporter configuration
- JUnit reporter for CI
- HTML reporter
- Dot and JSON reporters
- Custom reporter implementations
- Reporter hooks

**Visual Testing**

- wdio-image-comparison-service configuration
- checkScreen/checkElement/checkFullPage patterns
- Baseline management
- Diff thresholds configuration
- Ignore regions

**Network**

- Mock/respond via devtools/intercept service
- Request logging
- Response modification patterns

**Mobile**

- Appium service integration (defer deep Appium to appium skill)
- Mobile capabilities configuration
- Context switching patterns

**CI/CD**

- Docker integration
- Selenium Grid integration
- Cloud services (Sauce Labs/BrowserStack) configuration
- Retry config (specFileRetries)
- wdio-timeline-reporter for CI visibility

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_wdio.md`:

1. **Architecture Patterns** — how this project structures WDIO tests, page objects, and services
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected WDIO configuration and test framework
7. **Service conventions** — service composition, custom command patterns, hook usage

---

## PHASE 3: BEST PRACTICES

Integrate for the detected WDIO configuration and project setup:

1. Configuration-as-code (typed wdio.conf.ts, environment-specific config merging)
2. Service composition over monolithic setup (modular services, lazy service loading)
3. Custom commands for DRY interactions (browser.addCommand for reusable actions)
4. Getter-based locators in page objects (lazy evaluation, no stale elements)
5. Explicit waits over implicit (waitForDisplayed, waitForExist, waitUntil)
6. WebDriver BiDi adoption for modern features (network interception, console capture)
7. Parallel safety (no shared state between specs, isolated test data)
8. Allure reporting as default (rich reporting, screenshots, video, step annotations)
9. Flakiness mitigation (specFileRetries, screenshot on failure, waitFor* over sleep)
10. Cross-browser matrix strategy (capabilities array, cloud provider integration)

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY WebDriverIO task — test creation, page object development, wdio.conf changes, custom command creation, service configuration, visual testing, reporter setup, parallel execution, CI pipeline setup, debugging test failures, mobile test setup.

**`allowed-tools`**: `Read Edit Write Bash(npx:*) Bash(npm:*) Glob Grep`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (locator skill for locator-only tasks, testing skill for generic strategy, appium skill for deep mobile automation)
3. **Architecture** — test structure diagram, key directories, service/page object data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only (TypeScript conventions, imports). Full formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only (add new spec, create page object, add custom command), no code blocks
7. **Testing Standards** — rules list + link to references/
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for test data handling, credential management
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, WebDriverIO docs
12. **Adaptive Interaction Protocols** — interaction modes with WDIO-specific detection signals (e.g., "wdio.conf error" for Diagnostic, "another spec like X" for Efficient, "what does addCommand do" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/wdio-config-patterns.md` — configuration patterns and examples
- `references/custom-commands-guide.md` — browser.addCommand and element.addCommand examples
- `references/page-object-template.ts` — copy-paste page object template with getter-based locators
- `references/service-patterns.md` — service composition and configuration examples
- `references/visual-testing-guide.md` — image comparison, baseline management
- `references/code-style.md` — import order, TypeScript conventions, formatting with full examples
- `references/security-checklist.md` — test data handling, credential management, CI secrets
- `references/common-issues.md` — troubleshooting common WDIO pitfalls
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `assets/wdio-conf-example.ts` — wdio.conf.ts starter template
- `scripts/validate-wdio.sh` — config + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent            | Role                                                    | Tools                          | Spawn When                                                       |
| ---------------- | ------------------------------------------------------- | ------------------------------ | ---------------------------------------------------------------- |
| test-reviewer    | Read-only test analysis against SKILL.md patterns       | Read Glob Grep                 | PR review, test audit, pattern compliance check                  |
| config-auditor   | WDIO configuration analysis and optimization            | Read Glob Grep                 | Config refactoring, service audit, capability review             |
| service-designer | Service composition and custom command architecture     | Read Glob Grep                 | New service integration, custom command design, hook patterns    |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/test-reviewer.md` — read-only WDIO test analysis agent
- `agents/config-auditor.md` — WDIO configuration analysis agent
- `agents/service-designer.md` — service composition and custom command agent
