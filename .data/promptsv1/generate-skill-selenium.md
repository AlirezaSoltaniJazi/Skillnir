# Selenium Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are Selenium-specific overrides.

```
ROLE:     Senior Selenium test automation engineer analyzing a production Selenium test suite
GOAL:     Generate a production-grade Selenium automation skill directory
SCOPE:    Selenium test code only — tests/, pages/, config, utilities, grid setup. Supports multi-language: Java, Python, C#, JavaScript, Ruby, Kotlin. Ignore application source code, other test frameworks
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Selenium Only

Ignore application source code and non-Selenium test frameworks. Scan for:

**Language & Test Runner**

- Primary language (Java/Python/C#/JavaScript/Ruby/Kotlin)
- Test runner (JUnit 4/5, TestNG, pytest, NUnit, xUnit, Mocha, RSpec)
- Build tool (Maven/Gradle/pip/npm/dotnet/bundler)
- Key dependencies and usage patterns
- Version pinning strategy

**Selenium Version**

- Selenium 3 vs 4+ features in use
- WebDriver BiDi support
- CDP integration
- Relative locators usage
- Selenium Manager

**Driver Management**

- Selenium Manager (4.6+)
- WebDriverManager (bonigarcia for Java)
- Manual driver binary management
- Browser-specific options (ChromeOptions, FirefoxOptions, EdgeOptions)

**Page Object Model**

- PageFactory (@FindBy for Java)
- Base page patterns
- Component objects
- Language-specific POM conventions
- Element caching

**Waits**

- Implicit vs explicit (WebDriverWait + ExpectedConditions)
- FluentWait
- Custom wait conditions
- Polling interval
- Timeout hierarchy

**Actions API**

- Drag-and-drop
- Hover
- Keyboard sequences (sendKeys, keyDown/keyUp)
- Context-click
- Scroll (Selenium 4 ScrollOrigin)
- Pen/touch actions

**Grid**

- Grid 4 architecture (router/distributor/node)
- Docker Selenium Grid
- Standalone vs hub-node
- Session queuing
- VNC debugging
- Dynamic grid

**Browser Management**

- ChromeOptions/FirefoxOptions
- Headless mode (--headless=new)
- Proxy config
- Download handling
- Certificate handling
- Browser arguments
- Extensions

**Advanced Interactions**

- File upload (sendKeys to input[type=file])
- Multi-window/tab (getWindowHandles)
- Alerts (switchTo().alert())
- Frames/iframes (switchTo().frame())
- Shadow DOM (getShadowRoot())

**Reporting**

- Extent Reports
- Allure
- TestNG/JUnit XML listeners
- Custom listeners (WebDriverEventListener/EventFiringDecorator for Selenium 4)
- Screenshot capture

**CI/CD**

- Selenium Grid in CI
- Docker Selenium
- Cloud providers (Sauce Labs, BrowserStack, LambdaTest)
- Retry strategies
- Parallel execution via build tool

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_selenium.md`:

1. **Architecture Patterns** — how this project structures Selenium test code
2. **Coding Conventions** — style, naming, structure conventions
3. **Package Patterns** — key packages and idiomatic usage
4. **Things to ALWAYS do** — non-negotiable patterns observed
5. **Things to NEVER do** — anti-patterns explicitly avoided
6. **Framework-specific wisdom** — patterns unique to the detected language/runner
7. **Page Object conventions** — POM structure, locator strategy, wait patterns

---

## PHASE 3: BEST PRACTICES

Integrate for the detected language/runner:

1. Explicit waits always — never use implicit waits (they conflict with explicit waits, cause unpredictable timing)
2. Selenium Manager for driver management (4.6+) — avoid manual driver binary management
3. Page Object encapsulation — no locators in test files, action methods return page objects for fluent chains
4. Actions API for complex interactions — use Actions class for hover, drag, keyboard instead of JavaScript workarounds
5. Grid 4 for parallel and distributed execution — Docker Selenium for consistent environments
6. Browser options management — centralize capabilities, use Options objects not deprecated DesiredCapabilities
7. Exception hierarchy understanding — NoSuchElementException, StaleElementReferenceException, TimeoutException handling patterns
8. Screenshot and video on failure — TestWatcher/listener integration for automatic failure artifacts
9. Selenium 4 features adoption — relative locators, CDP integration, BiDi protocol, Selenium Manager
10. Multi-language consistency — same POM structure and wait patterns regardless of language

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY Selenium task — test creation, page object design, locator strategy, wait patterns, grid configuration, browser options, actions API, reporting, CI integration, cross-browser testing, driver management.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep` (broad Bash — multi-language: mvn, gradle, pip, npm, dotnet)

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions
2. **Do NOT Use** — cross-references to sibling skills (locator skill for locator-only tasks, testing skill for generic test strategy, appium skill for mobile automation)
3. **Architecture** — project structure diagram, key directories, data flow
4. **Key Patterns** — summary table only (pattern name, approach, key rule). Full code examples in references/ only
5. **Code Style** — rules table only. Import order, naming conventions, formatting details in references/code-style.md
6. **Common Recipes** — numbered step lists only, no code blocks
7. **Testing Standards** — rules list + link to references/wait-strategies-guide.md
8. **Performance Rules** — bullet list, no code examples
9. **Security** — summary + link to references/security-checklist.md for per-component verification
10. **Anti-Patterns** — what NOT to do (with why)
11. **References** — key files, docs, resources
12. **Adaptive Interaction Protocols** — interaction modes with Selenium-specific detection signals (e.g., "NoSuchElementException" for Diagnostic, "another test class like X" for Efficient, "what is WebDriverWait" for Teaching), correction accumulation, proficiency calibration, anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/selenium-config-patterns.md` — driver config, browser options, grid setup examples
- `references/page-object-patterns.md` — POM patterns with full examples per language
- `references/wait-strategies-guide.md` — explicit wait patterns, custom conditions, timeout hierarchy
- `references/grid-setup-guide.md` — Grid 4 architecture, Docker Selenium, cloud provider integration
- `references/actions-api-guide.md` — Actions API patterns for drag, hover, keyboard, scroll
- `references/code-style.md` — import order, naming conventions, formatting with full examples
- `references/security-checklist.md` — credential handling, grid security, browser profile isolation
- `references/common-issues.md` — troubleshooting common Selenium pitfalls
- `references/ai-interaction-guide.md` — research-backed anti-patterns, anti-dependency strategies
- `assets/pom-example.xml` OR `assets/requirements-example.txt` (language-dependent)
- `scripts/validate-selenium.sh` — naming + structure convention checker

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                 | Role                                                        | Tools                | Spawn When                                                             |
| --------------------- | ----------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------- |
| test-reviewer         | Read-only test analysis against SKILL.md patterns           | Read Glob Grep       | PR review, test audit, POM compliance check                           |
| grid-configurator     | Grid setup and configuration analysis                       | Read Glob Grep       | Grid setup, Docker Selenium config, cloud provider integration         |
| cross-browser-auditor | Cross-browser compatibility and browser options audit        | Read Glob Grep Bash  | Browser compatibility review, options audit, headless validation       |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/test-reviewer.md` — read-only Selenium test analysis agent
- `agents/grid-configurator.md` — Grid setup and configuration agent
- `agents/cross-browser-auditor.md` — cross-browser compatibility audit agent
