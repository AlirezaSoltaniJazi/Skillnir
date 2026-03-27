# Web Locator Extraction Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are locator-specific overrides.

```
ROLE:     Senior test automation engineer specializing in element locator strategies
GOAL:     Generate a production-grade locator extraction skill directory
SCOPE:    Element locators + selector strategies only — ignore test logic, assertions, test data, CI pipelines
OUTPUT:   SKILL.md + INJECT.md + references/ + assets/ + scripts/
```

---

## PHASE 1: PROJECT SCAN — Locator Strategy Focus

Scan directories: `test/`, `tests/`, `e2e/`, `integration/`, `spec/`, `__tests__/`, `cypress/`, `playwright/`, `wdio/`, `pages/`, `page-objects/`, `page_objects/`, `selectors/`, `locators/`, `*.spec.*`, `*.test.*`, `*.page.*`, `*.po.*`

**Test Framework Detection**

- Primary framework: Playwright / Cypress / WebDriverIO / Selenium / Robot Framework / Appium
- Detection sources: config files (`playwright.config.*`, `cypress.config.*`, `wdio.conf.*`, `robot.yaml`, `selenium-*.json`), dependencies (`package.json`, `requirements.txt`, `pom.xml`, `build.gradle`), import patterns in test files
- Language: JavaScript / TypeScript / Python / Java / C# / Ruby
- Supporting libraries: @testing-library/*, axe-core, Pa11y, custom assertion libs

**Current Locator Inventory**

- Count by strategy: data-testid, data-test, data-cy, CSS class, CSS ID, XPath absolute, XPath relative, role-based, text-based, name-based, tag-based
- Brittle pattern prevalence: nth-child, nth-of-type, generated class names (CSS modules, Tailwind hash), absolute XPath, deeply nested selectors, index-based
- Robust pattern prevalence: data-testid, role selectors, label selectors, text content selectors
- Ratio of brittle vs robust locators (quantify if possible)

**Page Object Architecture**

- Page object model present? (classes, functions, singletons, none)
- Locator organization: inline in tests, centralized in PO files, separate locator files, component-based
- Naming conventions for locator variables/properties
- Base page/component classes with shared locator utilities
- Locator return type: raw string, framework locator object, wrapped element

**Custom Locator Utilities**

- Helper functions for element interaction (click, type, wait + locate)
- Custom commands: Cypress `cy.custom()`, WDIO `browser.custom()`, Playwright fixtures
- Locator factories or builders (dynamic locator construction)
- Retry/wait wrappers around locator resolution

**Shadow DOM / iFrame Usage**

- Web components with shadow DOM (open vs closed)
- iFrame nesting depth and cross-origin restrictions
- Framework-specific piercing strategies in use
- Custom shadow DOM / iFrame utilities

**Dynamic Content Patterns**

- Dynamic IDs (auto-generated, session-based, React keys)
- Lazy-loaded elements (infinite scroll, virtual lists, deferred rendering)
- SPA routing (client-side navigation, DOM teardown/rebuild)
- Animation/transition states affecting element availability
- Modal/overlay/drawer patterns

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_locator.md`:

1. **Locator Architecture** — how this project organizes and manages locators
2. **Framework API Usage** — which locator APIs from the detected framework are actively used vs available but unused
3. **Locator Quality Assessment** — ratio of robust vs brittle selectors, specific gaps and risks
4. **Coding Conventions** — naming, organization, encapsulation patterns for locators
5. **Things to ALWAYS do** — non-negotiable locator patterns for this project
6. **Things to NEVER do** — anti-patterns found or to avoid
7. **Framework-specific wisdom** — locator patterns unique to the detected framework

---

## PHASE 3: BEST PRACTICES (priority order)

1. **Accessibility-first selectors** — prefer role, label, text-based locators; best for both testing resilience and a11y compliance. Use `getByRole`, `getByLabel`, `getByText` (Playwright/Testing Library), `cy.findByRole` (Cypress + Testing Library), `By.cssSelector('[aria-label="..."]')` (Selenium)
2. **data-testid as reliable fallback** — when semantic/accessibility selectors are ambiguous or unavailable; stable across refactors, explicitly maintained by developers
3. **CSS selectors over XPath** — faster execution, more readable, better cross-browser consistency; XPath only for text content matching or ancestor traversal
4. **Unique identifiers over structural** — avoid nth-child, index-based, parent-child chains; prefer attributes that uniquely identify the target element
5. **Locator encapsulation** — centralize locators in page objects or component objects; never scatter raw selectors across test steps
6. **Framework-native API preference** — use the framework's built-in locator methods before falling back to raw CSS/XPath; each framework optimizes its native locators (auto-waiting, retry, logging)
7. **Resilience to UI changes** — locators must survive minor styling, layout, and class name changes; test for semantic meaning, not visual implementation
8. **Shadow DOM / iframe handling** — use framework-specific pierce strategies; document workarounds for closed shadow roots and cross-origin iframes
9. **Wait strategy alignment** — pair locators with appropriate wait conditions; prefer framework auto-wait over explicit waits; never use hard-coded sleep
10. **Locator debugging and validation** — use browser DevTools, Playwright Inspector, Cypress Selector Playground, WDIO `debug()` to validate locators before committing

---

## LOCATOR STRATEGY PRIORITY TABLE

Generate this decision table in the SKILL.md body. The AI must try the first applicable strategy and fall back sequentially:

| Priority | Strategy                   | Use When                                                                       | Avoid When                                                  | Example (Playwright)              |
| -------- | -------------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------------------- | --------------------------------- |
| 1        | Role + accessible name     | Element has a clear semantic role and accessible name                           | Multiple identical roles without distinguishing name        | `getByRole('button', {name: X})` |
| 2        | Label association           | Form elements with associated labels                                           | Labels are dynamic or generated                             | `getByLabel('Email')`             |
| 3        | Text content               | Visible text uniquely identifies the element                                   | Text is localized, dynamic, or appears in multiple elements | `getByText('Submit')`             |
| 4        | data-testid / data-test    | No reliable semantic selector; team maintains test attributes                  | Test attributes not in project convention                   | `getByTestId('login-form')`       |
| 5        | CSS selector (attribute)   | Unique attributes (name, type, href) available                                 | Attribute values are dynamic or generated                   | `locator('[name="email"]')`       |
| 6        | CSS selector (ID)          | Stable, developer-maintained IDs                                               | IDs are auto-generated (React, Angular)                     | `locator('#submit-btn')`          |
| 7        | CSS selector (class combo) | Stable, semantic class names (BEM or equivalent)                               | Classes are generated (CSS modules, Tailwind hash)          | `locator('.form__submit')`        |
| 8        | XPath (relative)           | Need ancestor/sibling traversal or text matching not covered by framework APIs | Any higher-priority strategy is viable                      | `locator('//button[text()="X"]')` |

**Fallback rule**: If strategy N is not viable, try N+1. Document why N was skipped.

---

## FRAMEWORK-SPECIFIC LOCATOR APIS

Generate framework-specific sections in references/ files. Each MUST include: preferred API order, code examples, framework-specific gotchas.

### Playwright

- **Preferred order**: `getByRole()` → `getByLabel()` → `getByText()` → `getByTestId()` → `getByPlaceholder()` → `locator()` (CSS) → `locator()` (XPath)
- **Key APIs**: `page.getByRole()`, `page.getByText()`, `page.getByTestId()`, `page.getByLabel()`, `page.getByPlaceholder()`, `page.getByAltText()`, `page.getByTitle()`, `page.locator()`, `locator.filter()`, `locator.nth()`, `locator.first`, `locator.last`
- **Chaining**: `page.getByRole('list').getByRole('listitem').filter({hasText: 'X'})`
- **Shadow DOM**: Playwright pierces open shadow DOM by default with `locator()`
- **Frames**: `page.frameLocator('#frame-id').getByRole(...)`
- **Gotchas**: `getByRole` uses accessibility tree (not DOM attributes); `locator()` does NOT auto-pierce shadow DOM when using CSS; strict mode rejects ambiguous locators

### Cypress

- **Preferred order**: `cy.findByRole()` (with @testing-library/cypress) → `cy.contains()` → `cy.get('[data-testid=...]')` → `cy.get('[data-cy=...]')` → `cy.get()` (CSS) → `cy.xpath()` (plugin)
- **Key APIs**: `cy.get()`, `cy.contains()`, `cy.find()`, `cy.findByRole()`, `cy.findByText()`, `cy.findByLabelText()`, `cy.findByTestId()`, `.within()`, `.first()`, `.last()`, `.eq()`
- **Chaining**: `cy.get('[data-testid="list"]').find('li').contains('Item')`
- **Shadow DOM**: `cy.get('my-component').shadow().find('.inner')`; or `includeShadowDom: true` in config
- **Frames**: `cy.iframe()` (cypress-iframe plugin) or `cy.get('iframe').its('0.contentDocument.body').find(...)`
- **Gotchas**: Cypress auto-retries failed locators; `cy.contains()` matches partial text by default; no native XPath support (needs plugin); chained commands are not Promises

### WebDriverIO (WDIO)

- **Preferred order**: `$('[data-testid=...]')` → `$('aria/...')` (aria selector) → `$('=text')` (link text) → `$('*=partial')` (partial link) → `$('css')` → `$('xpath=//...')`
- **Key APIs**: `$()`, `$$()`, `custom$()`, `shadow$()`, `react$()`, `$('aria/name')`, `$('=exact text')`, `$('*=partial text')`, `$('[data-testid]')`
- **Chaining**: `$('.parent').$('.child')`, `$$('li')[0]`
- **Shadow DOM**: `$('my-component').shadow$('.inner')` or `shadow$$()` for multiple
- **Frames**: `browser.switchToFrame($('#frame'))` then `$('selector')`
- **Gotchas**: `$` returns single element, `$$` returns array; WDIO v8+ uses WebDriver BiDi; custom selectors via `addLocatorStrategy()`; element references can go stale across navigations

### Selenium

- **Preferred order**: `By.id()` → `By.cssSelector('[data-testid=...]')` → `By.name()` → `By.cssSelector()` → `By.xpath()` → `By.className()` → `By.tagName()`
- **Key APIs**: `findElement(By.id())`, `findElement(By.cssSelector())`, `findElement(By.xpath())`, `findElement(By.name())`, `findElement(By.className())`, `findElement(By.tagName())`, `findElement(By.linkText())`, `findElement(By.partialLinkText())`, `findElements()` (returns list)
- **Language-specific**: Java (`driver.findElement(By.cssSelector(...))`), Python (`driver.find_element(By.CSS_SELECTOR, ...)`), C# (`driver.FindElement(By.CssSelector(...))`)
- **Shadow DOM**: Selenium 4+: `element.getShadowRoot().findElement(By.cssSelector(...))`
- **Frames**: `driver.switchTo().frame("frame-name")` then `findElement()`
- **Gotchas**: No auto-waiting (must use explicit `WebDriverWait`); `findElement` throws `NoSuchElementException` (not null); stale element references require re-find; relative locators (`RelativeLocator.with()`) added in Selenium 4

### Robot Framework

- **Preferred order**: `id:` → `data:testid:` (custom) → `name:` → `css:` → `xpath:` → `class:` → `tag:`
- **SeleniumLibrary keywords**: `Get WebElement`, `Get WebElements`, `Click Element`, `Input Text`, locator prefixes: `id:`, `name:`, `class:`, `tag:`, `xpath:`, `css:`, `link:`, `partial link:`
- **Browser library (Playwright-based)**: `Get Element`, `Click`, `Fill Text`, uses Playwright locators: `role=button[name="Submit"]`, `data-testid=login`, `text=Hello`, `css=.class`
- **Custom locator strategies**: Register via `Add Location Strategy` keyword
- **Shadow DOM**: Browser library pierces shadow DOM natively; SeleniumLibrary requires JavaScript executor
- **Frames**: `Select Frame`, `Unselect Frame` keywords
- **Gotchas**: SeleniumLibrary default locator strategy is `id`; Browser library uses Playwright engine (different locator syntax); mixing libraries causes confusion; `Wait Until Element Is Visible` for explicit waits

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY locator extraction task — finding elements in HTML, writing selectors, page object locators, data-testid strategy, XPath vs CSS decisions, accessibility selectors, locator refactoring, brittle selector fixes, shadow DOM element access, iframe element targeting, dynamic content locators, locator debugging.

**`allowed-tools`**: `Read Edit Write Bash Glob Grep Agent`

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (extracting locators from HTML, writing page object selectors, refactoring brittle locators, choosing locator strategy for new elements, debugging element-not-found errors, adding data-testid attributes to source code)
2. **Do NOT Use** — cross-references to sibling skills: use "testing" for test logic/assertions/data management, use "frontend" for UI component implementation, use "test-design" for test case design/coverage strategy
3. **Locator Strategy Priority** — the priority decision table from PHASE 3 (MUST include in SKILL.md as a table)
4. **Framework-Specific Locator API** — detected framework's preferred API order, 1-2 line summary per tier. Full examples in references/ only
5. **Page Object Locator Patterns** — how to organize, name, and encapsulate locators per the project's detected conventions
6. **Key Patterns** — summary table only (pattern name, selector approach, key rule). Full code examples in references/ only
7. **Code Style** — locator variable naming conventions, file organization, formatting rules (table format)
8. **Common Recipes** — numbered step lists only, no code blocks:
   - Add locators for a new page/component
   - Refactor brittle selectors to robust alternatives
   - Handle dynamically generated elements
   - Pierce shadow DOM / access iframe content
   - Debug "element not found" failures
9. **Anti-Patterns** — what NOT to do with locators (with why):
   - Absolute XPath (`/html/body/div[2]/...`) — breaks on any DOM change
   - Generated class names as selectors — change on every build
   - Index-based selectors without context — order-dependent, brittle
   - Hard-coded waits before locator resolution — flaky and slow
   - Locators scattered across test files — unmaintainable
   - Overly specific selectors — couple tests to implementation
10. **References** — links to references/ files
11. **Adaptive Interaction Protocols** — interaction modes with locator-specific detection signals:
    - **Teaching**: "what selector should I use for...", "why prefer role over CSS", "how does shadow DOM work"
    - **Efficient**: "locator for this element", "extract selectors from this HTML", "update page object for new page"
    - **Diagnostic**: "element not found", "stale element reference", "locator matches multiple elements", "flaky selector"

**Suggested reference files**:

- `LEARNED.md` — auto-updated template (Corrections, Preferences, Discovered Conventions sections)
- `references/locator-strategy-guide.md` — full decision tree with code examples per strategy tier, framework-specific comparison table
- `references/playwright-locators.md` — Playwright locator API with full code examples: getByRole, getByTestId, getByText, getByLabel, locator(), chaining, filtering
- `references/cypress-locators.md` — Cypress locator API with full code examples: cy.get, cy.contains, @testing-library integration, custom commands
- `references/wdio-locators.md` — WDIO locator API with full code examples: $, $$, custom$, shadow$, aria selectors, custom strategies
- `references/selenium-locators.md` — Selenium locator API with code examples per language (Java, Python, C#): By.*, WebDriverWait, relative locators
- `references/robot-framework-locators.md` — Robot Framework locator API: SeleniumLibrary vs Browser library, locator prefixes, custom strategies
- `references/shadow-dom-iframe-guide.md` — cross-framework guide for shadow DOM piercing and iframe access with code examples
- `references/code-style.md` — locator naming conventions, page object organization, file structure patterns with examples
- `references/common-issues.md` — troubleshooting: stale elements, dynamic IDs, timing issues, not-found errors, ambiguous locators
- `references/ai-interaction-guide.md` — anti-dependency strategies, correction protocols, locator-specific teaching patterns
- `references/security-checklist.md` — locator security: avoid exposing internal selectors in production, sanitize dynamic locator inputs
- `assets/page-object-template.{{ext}}` — copy-paste page object boilerplate with locator section (use detected test language extension)
- `scripts/validate-locators.sh` — checks for brittle locator anti-patterns (grep for nth-child, absolute XPath, generated class patterns, hard-coded sleeps near locators)

---

## SUB-AGENT RECOMMENDATIONS

When generating skills for this domain, evaluate whether sub-agent delegation adds value using the decision table in the base scaffold. If the project warrants delegation, include these recommended sub-agents (adjust names, tools, and triggers based on actual project patterns):

| Agent                | Role                                                            | Tools               | Spawn When                                                                               |
| -------------------- | --------------------------------------------------------------- | -------------------- | ---------------------------------------------------------------------------------------- |
| locator-auditor      | Audit existing locators for brittleness and suggest improvements | Read Glob Grep Bash | Locator review request, brittle selector audit, locator quality assessment, pre-refactor |
| page-object-builder  | Generate or update page objects with proper locator strategies  | Read Edit Write Glob Grep | New page creation, page object refactoring, locator centralization task               |

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules
3. Link to agents/ for full definitions

Add to suggested reference files:

- `agents/locator-auditor.md` — locator brittleness analysis agent
- `agents/page-object-builder.md` — page object generation and locator centralization agent
