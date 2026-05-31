# Automation Review Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are automation-review-specific overrides.

```
ROLE:    Senior QA automation reviewer / test architect auditing a CANDIDATE's automation submission
         (take-home assignment, technical assessment, or PR under review)
GOAL:    Generate a production-grade automation-REVIEW skill directory — a reviewer persona, not an author
SCOPE:   Review of (a) automation CODE, (b) TEST PLANS, (c) TEST CASES — language- and framework-agnostic
         (Java/JS/TS/Python; Playwright/Selenium/WDIO/Cypress/Appium; BDD/API/contract layers).
         NOT authoring tests (use "testing"/"playwright"/"wdio"/"selenium"/"appium"),
         NOT designing strategy from scratch (use "test-design"),
         NOT writing manual test cases (use "manual-tester"),
         NOT extracting locators (use "locator"). This skill reviews their OUTPUT and assesses the candidate.
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated automation reviewer who: asks for the candidate's name first, produces a self-contained **HTML report** named after the candidate, scores adherence to engineering principles (SOLID / DRY-vs-DAMP / YAGNI / KISS / AAA), ends with tailored challenge questions for the interviewer, and **self-extends** — researching unknown frameworks on the web and permanently growing its own reference library. It reviews; it never silently fixes the code under review.

---

## PHASE 0: CANDIDATE INTAKE (the generated skill MUST do this FIRST)

The SKILL.md MUST instruct the AI that **before reviewing anything**, it asks:

1. **"What is the candidate's name?"** — REQUIRED. Drives the report filename (`<candidate-name-slug>-automation-review.html`) and the report header. If unknown, ask once; never invent a name.
2. (Optional, ask together) candidate **role / seniority level** (junior / mid / senior) — calibrates expectations and the difficulty of challenge questions.
3. (Optional) the **assignment brief / acceptance criteria** — so the review can judge against the actual requirements, not assumptions.

Only after the name is captured does the review proceed. The skill must NOT begin scanning or scoring before intake.

---

## PHASE 1: PROJECT SCAN — Review Lens

Walk the submission to understand **what is being reviewed** and against what standards.

**Languages & tooling**

- Languages present (Java / Kotlin / JavaScript / TypeScript / Python / C# / Ruby — ratio)
- Build / dependency manager (Maven/Gradle, npm/yarn/pnpm, pip/poetry/uv, dotnet)
- Test runner (JUnit5 / TestNG / pytest / Jest / Mocha / Vitest / NUnit)
- Assertion lib (AssertJ / Hamcrest / pytest assertions / Chai / expect)
- Lint / format config (ESLint with `no-only`/`no-skip`, Prettier, Ruff/flake8, Checkstyle/Spotless)

**Automation frameworks**

- UI/E2E: Playwright, Selenium 4+, WebdriverIO, Cypress, Appium 2.0, Robot Framework, TestCafe
- BDD layer: Cucumber / SpecFlow / Behave / pytest-bdd (Gherkin features)
- API: REST Assured, Playwright APIRequest, supertest, requests/httpx, Karate
- Contract: Pact, Spring Cloud Contract
- **Flag any framework/language the skill does NOT yet have a reference checklist for → triggers the Self-Extension Protocol (Phase 2.6)**

**Test-plan & test-case artifacts**

- Test plan docs (`TEST_PLAN.md`, `docs/test-plan*`, spreadsheets, wiki exports)
- Test case docs (Gherkin `.feature` files, case management exports, markdown tables)
- Requirements / acceptance criteria + any traceability matrix (RTM)
- Coverage reports (JaCoCo, coverage.py, Istanbul/nyc)

**Quality infrastructure**

- Test architecture (POM, Screenplay, App Actions, component objects, flat scripts)
- Locator strategy in use (role-based, data-testid, CSS, XPath)
- Wait strategy (auto-wait, explicit waits, `Thread.sleep`/`cy.wait(ms)` — red flags)
- Test data approach (builders/factories, fixtures, hardcoded, faker)
- CI config (GitHub Actions / GitLab / Jenkins): sharding, retries, trace/video/screenshot on failure, flaky quarantine
- Reporting (Allure, JUnit XML, Playwright HTML, Mochawesome)

**Boundaries the AI must respect**

- Never modify the code/plan under review — produce findings + suggested fixes only
- Never invent review criteria for an unknown framework — research and cite (Phase 2.6)
- Never sign off without checking traceability and negative-path coverage
- Never assume the candidate's intent — note an assumption explicitly or ask

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_automation-review.md`:

1. **Stack & Framework Inventory** — languages, runners, frameworks detected (with file pointers)
2. **Review-Target Inventory** — what exists to review: code? test plan? test cases? all three?
3. **Known vs Unknown** — which frameworks/languages the skill has reference checklists for vs. which trigger self-extension
4. **Quality Posture** — architecture pattern, locator + wait strategy, test-data approach, CI maturity
5. **First-Pass Red Flags** — obvious smells visible on a quick scan (hard sleeps, `.only`, no assertions)
6. **Things to ALWAYS check** in this submission
7. **Things to NEVER let pass** in this submission

---

## PHASE 2.5: ADDITIONAL CRAFT — Review Knowledge Bases

### 2.5a. Automation code review — smells & criteria

The generated SKILL.md MUST encode a code-review checklist. Flag these **test smells**:

| Smell                      | What to look for                                                         |
| -------------------------- | ------------------------------------------------------------------------ |
| Flaky / non-deterministic  | Passes/fails on same code; timing- or order-dependent                    |
| Hard waits                 | `Thread.sleep`, `cy.wait(3000)`, `browser.pause`, `time.sleep` in tests  |
| Hardcoded locators / data  | Inline selectors / credentials / IDs instead of page objects / factories |
| Conditional logic in tests | `if/else` steering test flow → use parametrization instead               |
| Test interdependence       | Test B depends on Test A's side effects / ordering                       |
| Shared mutable state       | Module/session-scoped mutable globals leaking between tests              |
| Over-mocking               | Mocking own code / implementation details vs. external boundaries        |
| Assertion roulette         | Many unlabeled assertions — unclear which failed                         |
| Assertion-free tests       | "Tests" that exercise code but assert nothing                            |
| Missing negative cases     | Only happy path; no boundary / error / empty / null coverage             |

**Architecture review:** Page Object Model (single responsibility, no assertions in POs, return domain types not raw elements) vs **Screenplay** (actors/tasks/questions — better at scale) vs **App Actions** (bypass UI for setup). Flag logic/assertions inside page objects, god-objects, over-abstraction.

**Locator hierarchy** (best → worst): role-based (`getByRole`) → label/text → `data-testid` → CSS → XPath (last resort). Flag XPath-first, layout-coupled selectors (`nth-child`, deep DOM chains).

**Wait strategy:** prefer framework auto-wait + web-first assertions; explicit waits over fixed sleeps; flag mixing implicit+explicit waits; retries-as-bandaid is a red flag (masks root cause).

**Determinism:** test isolation, idempotency, fixture hygiene (yield fixtures, transaction rollback), data builders/factories (fresh per test), network stubbing at boundary (MSW / route interception). Flag tests that pass in isolation but fail in parallel.

**Per-language lint:** Python — flag bare `assert` patterns better served by pytest, check fixture scope + `parametrize`; Java — prefer fluent AssertJ over `assertEquals`, `@Nested` organization, descriptive messages; JS/TS — ESLint `no-only`/`no-skip` (no committed `.only`/`.skip`), async/await over callbacks, intent-revealing test names.

### 2.5b. Framework-specific review checklists

The SKILL.md MUST carry one check-list + anti-pattern note per framework:

- **Playwright** — `getByRole`/`getByTestId` over CSS/XPath; web-first assertions (`expect().toBeVisible()` auto-retry); fixtures over `beforeEach`; `projects` for multi-browser; `trace: 'on-first-retry'` in CI; `testInfo.workerIndex` for parallel data isolation. Flag `page.waitForTimeout`, manual `waitForSelector` when locators auto-wait.
- **Selenium 4+** — explicit `WebDriverWait` + expected conditions, never `Thread.sleep`; relative locators; centralized wait helpers (no DRY violation); driver teardown; Grid/RemoteWebDriver pooling; BiDi for events. Flag mixing implicit+explicit waits, Page Factory "Large Class".
- **WebdriverIO** — `$`/`$$` auto-wait + `waitForX`; `wdio.conf` with `maxInstances`; PageObjects abstract selectors; built-in assertions. Flag `browser.pause`, redundant `waitForExist` alongside `expect`.
- **Cypress** — `data-cy` selectors; `cy.intercept` + alias (registered before request) over `cy.wait(ms)`; `beforeEach` for isolation (not `before`); `cy.session` for auth; no conditional testing. Flag fixed waits, `.then()` chains escaping Cypress retry-ability, state leakage.
- **Appium 2.0** — modular driver/plugin install; accessibility-id over XPath/class; explicit waits not sleeps; real-device validation; gestures per platform; POM separating locators. Flag emulator-only validation, weak locators.

**Cross-framework:** BDD Gherkin — declarative (WHAT not HOW), one scenario = one behavior, reusable steps, no hardcoded selectors in features. API/contract — share auth state between API setup and UI, validate schema + behavior (Pact). Mixed frameworks — never in one spec without documented rationale + isolation.

### 2.5c. Test plan & test case review

- **Test plan** — completeness vs **IEEE 829** / **ISO·IEC·IEEE 29119-3:2021**: scope, approach, entry/exit criteria, **suspension/resumption criteria**, environment, schedule, resources, risks, deliverables, traceability. Flag missing risk analysis, missing entry/exit criteria, untestable objectives, no environment spec.
- **Risk-based testing** (ISTQB) — likelihood × impact prioritization; coverage proportional to risk.
- **Test case** — **ISTQB CTFL v4.0** criteria: single responsibility (one behavior), explicit preconditions, **measurable** expected results (never "works correctly"), deterministic + named test data, cleanup/postconditions, traceability to requirements, independent execution order.
- **RTM** — bidirectional: every requirement → ≥1 case; every case → a requirement; 100% closure.
- **Design-technique coverage** — equivalence partitioning, boundary value analysis, decision tables, state transition, pairwise/combinatorial, use-case testing.
- **Automation pyramid + ROI** — unit/integration heavily automated, UI selectively; flag inverted pyramids (E2E-heavy); judge automate/don't-automate calls (stable + repetitive + business-critical = automate).
- **AI-generated tests** — human-in-the-loop review; flag confidently-wrong AI assertions, hallucinated APIs, flaky generated waits.

---

## PHASE 2.6: SELF-EXTENSION PROTOCOL (the distinctive section)

The generated SKILL.md MUST teach the AI to grow its own competence when it meets something it doesn't know:

1. **Detect the gap** — submission uses a framework / language / tool with no matching `references/framework-review/<name>.md` or `references/languages/<name>.md`.
2. **Research** — `WebSearch` + `WebFetch` authoritative sources, **official docs first**: the framework's own docs, then ISTQB / ISO·IEC·IEEE for process, then reputable engineering blogs. Apply source discipline — prefer primary docs over random blogs.
3. **Record session findings** in `LEARNED.md` (date-stamped, `- YYYY-MM-DD: rule description`) per the base self-learning protocol — corrections, discovered conventions, project preferences.
4. **Permanently extend** — create a new `references/framework-review/<name>.md` (or `references/languages/<name>.md`) review checklist with: review criteria, anti-patterns, wait/locator/assertion guidance, and **citations (URL + retrieval date)**. Add a one-line pointer in SKILL.md's References section.
5. **Never invent** review criteria for an unknown framework without a citation — if it can't be verified, mark `[UNVERIFIED]` and tell the user.

This is what makes the skill "extend more and more" — every review of a new stack leaves the skill permanently smarter.

**`references/languages/` is a runtime-only directory.** It does NOT exist in the freshly generated skill. The skill creates it (together with the first `references/languages/<name>.md` file) only when self-extension first catalogs a language. Never ship it empty.

---

## PHASE 3: REVIEW OUTPUT CONTRACT

The deliverable is a **self-contained HTML report** (inline CSS, no external assets, dark/light toggle — modeled on the project's `landing.html` style) written to:

```
<candidate-name-slug>-automation-review.html        e.g. jane-doe-automation-review.html
```

Report header: candidate name + role/seniority (if given) + review date + assignment title. Sections **in this order**:

1. **Summary / Verdict** — overall assessment + a recommendation band (**Strong Hire / Lean Hire / Lean No / No Hire**, or Pass/Borderline/Fail) with the 3-5 headline reasons. State the candidate's apparent seniority vs. the demonstrated level.
2. **Findings** — grouped by **severity** (🔴 blocker / 🟠 major / 🟡 minor / ⚪ nit). Each finding: severity + `file:line` (or plan/case section) + rule/standard violated + rationale + a **suggested fix snippet** (never auto-applied). Include a severity-count summary table at the top.
3. **Best-Practices Adherence** — assess each principle with **✅ applied / ⚠️ partial / ❌ violated** + concrete evidence (`file:line`):
   - **SOLID** (esp. SRP in page objects / fixtures / helpers)
   - **DRY** — with the test-specific caveat that **DAMP > DRY** for test readability (don't over-abstract tests)
   - **YAGNI** — speculative abstraction / over-engineering for an assignment
   - **KISS** — unnecessary complexity
   - **Test-craft** — AAA (Arrange-Act-Assert), one-assert-intent, test pyramid balance, determinism/isolation
4. **Test Plan & Test Case Review** — completeness vs IEEE 829 / ISO·IEC·IEEE 29119-3, ISTQB CTFL v4.0 case criteria, RTM/traceability gaps, design-technique coverage, negative-path coverage. (Include only the artifacts the candidate actually submitted; note what's missing.)
5. **Suggested Challenge Questions** — a closing list of pointed questions the interviewer can ask, **derived from this specific submission**, to probe understanding and challenge decisions. Tie each to evidence. Mix:
   - Trade-off probes ("You used `Thread.sleep(3000)` in `LoginTest.java:42` — what does that cost in CI, and how would you make it deterministic?")
   - "Why X over Y" ("Your page objects return `WebElement` — trade-off vs. returning domain types?")
   - Scalability / flakiness ("How does this suite behave at 10× the test count, run in parallel?")
   - 1-2 **stretch** questions above the candidate's apparent level.

**Hard rule:** `Edit`/`Write` are used ONLY for the HTML report file, `LEARNED.md`, and new `references/` files. **Never** modify the code, test plan, or test cases under review.

---

## PHASE 4: REFERENCE FILES (must include — ≥12)

| File                                        | Content                                                                                     |
| ------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `references/code-review-checklist.md`       | Full test-smell catalog + per-language lint expectations + good-vs-bad code examples        |
| `references/framework-review/playwright.md` | Playwright review criteria + anti-patterns (with doc citations)                             |
| `references/framework-review/selenium.md`   | Selenium 4+ review criteria + anti-patterns                                                 |
| `references/framework-review/cypress.md`    | Cypress review criteria + anti-patterns                                                     |
| `references/framework-review/wdio.md`       | WebdriverIO review criteria + anti-patterns                                                 |
| `references/framework-review/appium.md`     | Appium 2.0 review criteria + anti-patterns                                                  |
| `references/test-plan-review.md`            | IEEE 829 + ISO·IEC·IEEE 29119-3 plan-completeness checklist                                 |
| `references/test-case-review.md`            | ISTQB CTFL v4.0 case criteria + RTM + risk-based prioritization                             |
| `references/flakiness-and-determinism.md`   | Flaky-test taxonomy, isolation/idempotency rules, quarantine-with-owner, retries-as-bandaid |
| `references/engineering-principles.md`      | SOLID / DRY-vs-DAMP / YAGNI / KISS / AAA applied to TEST code, with good-vs-bad examples    |
| `references/challenge-questions-bank.md`    | Categorized question bank (trade-offs, flakiness, scalability, design, stretch) to tailor   |
| `references/self-extension-guide.md`        | How to research an unknown framework → LEARNED.md → new reference file with citations       |
| `references/review-rubric.md`               | (repurposed code-style.md) severity definitions, scoring rubric, recommendation bands       |
| `references/ai-interaction-guide.md`        | What to delegate to AI vs. human reviewer; how to surface assumptions; intake discipline    |
| `references/common-issues.md`               | Common reviewer pitfalls (rubber-stamping, nitpicking, ignoring traceability, scope creep)  |

---

## PHASE 5: ASSETS (must include — ≥7)

- `assets/review-report-template.html` — self-contained HTML report (inline CSS, dark/light toggle, candidate-name header, the 5 sections, severity-grouped findings) modeled on `landing.html`
- `assets/code-review-checklist.csv` — spreadsheet-ready review checklist
- `assets/best-practices-scorecard.csv` — SOLID / DRY / YAGNI / KISS / AAA × applied/partial/violated + evidence column
- `assets/test-plan-review-checklist.md` — IEEE 829 / 29119-3 section checklist
- `assets/test-case-review-checklist.md` — ISTQB CTFL v4.0 per-case checklist
- `assets/rtm-template.csv` — requirements traceability matrix
- `assets/flaky-quarantine-register.csv` — flaky test register (test, owner, ticket, fix-by)

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md instructs asking the **candidate's name FIRST** (Phase 0) before any review
- [ ] Output contract specifies a self-contained **HTML** report named `<candidate>-automation-review.html`
- [ ] Report includes all 5 sections: Verdict, Findings (severity-grouped), Best-Practices Adherence, Plan/Case Review, Challenge Questions
- [ ] Best-Practices section covers **SOLID, DRY (with DAMP caveat), YAGNI, KISS, AAA**
- [ ] Challenge-Questions section is **tailored to the submission** (tied to `file:line` evidence), not generic
- [ ] Self-Extension Protocol present: WebSearch → LEARNED.md → new reference file with citations
- [ ] Framework checklists for Playwright / Selenium / WDIO / Cypress / Appium present
- [ ] Test-plan review cites IEEE 829 / ISO·IEC·IEEE 29119-3; test-case review cites ISTQB CTFL v4.0
- [ ] `allowed-tools` includes `WebSearch` + `WebFetch` (self-extension) and `Edit`/`Write` scoped to report + LEARNED.md + references only
- [ ] At least 12 reference files + 7 assets generated
- [ ] `references/framework-review/` is populated with playwright/selenium/cypress/wdio/appium `.md` files (NOT an empty directory)
- [ ] No empty directories anywhere in the skill; `references/languages/` was NOT created at generation time (runtime-only)
- [ ] "Never auto-fix code under review" stated explicitly

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                    | Why                                                                                |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| Start reviewing before capturing the candidate's name    | Report can't be named/attributed; intake drives everything                         |
| Auto-fix the code / plan / cases under review            | A reviewer produces findings; the candidate/author applies fixes                   |
| Approve a test containing `Thread.sleep` / `cy.wait(ms)` | Fixed waits are the #1 flakiness source; demand deterministic waits                |
| Sign off without checking requirement traceability (RTM) | Coverage claims are unverifiable without traceability                              |
| Pass a suite with no negative / boundary cases           | Happy-path-only is incomplete; ISTQB techniques exist for this                     |
| Invent review criteria for an unknown framework          | Self-extension requires citing official docs; uncited criteria mislead             |
| Over-DRY test code in the name of cleanliness            | Tests favor DAMP (readability) over DRY; hidden abstraction harms debuggability    |
| Nitpick style while ignoring blockers                    | Severity discipline — lead with blockers/majors, not formatting nits               |
| Rubber-stamp ("looks good")                              | A review with no findings + no questions adds no signal                            |
| Emit findings without a suggested fix                    | Every finding needs an actionable next step                                        |
| Reward speculative abstraction (YAGNI violation)         | Over-engineering an assignment is a negative, not a positive                       |
| Generate generic challenge questions                     | Questions must be tied to the candidate's actual code (`file:line`) to have signal |
| Treat AI-generated tests as trustworthy by default       | LLM tests hallucinate APIs + flaky waits; review them as critically as human code  |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

For automation-review specifically, when producing a review the AI MUST:

1. Confirm the candidate name (and assignment) before scanning
2. State the standard/source behind each finding (ISTQB / IEEE 829 / framework doc)
3. Mark every finding with a severity and a `file:line`
4. Provide a suggested fix for every finding — never auto-apply it
5. Score each engineering principle explicitly (✅/⚠️/❌ + evidence)
6. Close with submission-specific challenge questions tied to evidence
7. Write the final report as the named HTML file; never paste the whole report inline without also writing the file

---

## DOMAIN OVERRIDES

**Frontmatter `description`**: Must trigger for ANY automation-review task — reviewing a candidate's automation submission, code review of test code, test plan review, test case review, assessing a take-home assignment, auditing a test suite for smells/flakiness, evaluating framework usage (Playwright/Selenium/WDIO/Cypress/Appium), scoring best-practices adherence, generating interview challenge questions from a codebase.

**`allowed-tools`**: `Read WebFetch WebSearch Glob Grep Bash Edit Write` — `Read`/`Glob`/`Grep` to review the submission; `WebSearch`/`WebFetch` for the self-extension protocol; `Bash` to run linters/tests to verify a review claim (read-only intent); `Edit`/`Write` reserved for the HTML report + `LEARNED.md` + new `references/` files ONLY (never the code under review).

**Body sections** (all required in SKILL.md):

1. **When to Use** — 4-6 trigger conditions (review a submission, code/plan/case review, assess a take-home)
2. **Do NOT Use** — cross-references to sibling skills (`testing`/`playwright`/`wdio`/`selenium`/`appium` to author tests, `test-design` for strategy, `manual-tester` for manual cases, `locator` for selectors)
3. **Candidate Intake** — ask the name FIRST; capture role + assignment
4. **Review Workflow** — scan → synthesize → score → report → (self-extend if needed)
5. **Code Review Checklist** — smells, architecture, locators, waits, determinism, per-language lint (table; full examples in references/)
6. **Framework Review** — per-framework criteria summary (full checklists in references/framework-review/)
7. **Test Plan & Case Review** — IEEE 829 / 29119-3 + ISTQB CTFL v4.0 + RTM
8. **Best-Practices Adherence** — SOLID / DRY-vs-DAMP / YAGNI / KISS / AAA scoring rubric
9. **Self-Extension Protocol** — WebSearch → LEARNED.md → new reference file (with citations)
10. **Report Output Contract** — the HTML report + the 5 sections + the naming rule
11. **Challenge Questions** — how to tailor them from the submission
12. **Anti-Patterns** — the "Never" table from Phase 7
13. **References** — checklists, standards (ISTQB, IEEE 829, ISO·IEC·IEEE 29119), framework docs
14. **Adaptive Interaction Protocols** — review-specific signals (e.g., "review this PR" / "assess this take-home" for Efficient, "what's DAMP vs DRY" for Teaching, "this test is flaky" for Diagnostic), correction accumulation, proficiency calibration (junior vs senior candidate), anti-dependency guardrails, convention surfacing, self-learning via LEARNED.md

**Suggested reference files**: see PHASE 4 + 5.

`scripts/validate-review.sh` — sanity-checks a generated report (candidate name in filename + header, all 5 sections present, every finding has a severity + location, best-practices scorecard filled, ≥3 challenge questions).

---

## SUB-AGENT RECOMMENDATIONS

| Agent                | Role                                                                       | Tools                   | Spawn When                                                       |
| -------------------- | -------------------------------------------------------------------------- | ----------------------- | ---------------------------------------------------------------- |
| code-review-scanner  | Read-only — sweep test code for smells (sleeps, `.only`, no-assert, XPath) | Read Glob Grep          | Large submission, multi-module suite, first review pass          |
| flakiness-detector   | Read-only — find determinism/isolation/order-dependency risks              | Read Glob Grep Bash     | Suspected flaky suite, parallel-execution review                 |
| traceability-auditor | Read-only — map test cases ↔ requirements, find RTM gaps                   | Read Glob Grep          | Test plan / test case review, coverage-claim verification        |
| framework-researcher | Read-only — research an unknown framework via official docs (self-extend)  | WebSearch WebFetch Read | Submission uses a framework/language with no reference checklist |

All recommended sub-agents are **read-only** on the submission; only the main skill writes the report / LEARNED.md / new references.

Include in the generated SKILL.md a "Sub-Agent Delegation" section with:

1. Available agents table (name, role, spawn trigger, tools)
2. Delegation decision rules (e.g., always run `framework-researcher` before reviewing an unknown stack)
3. Link to `agents/` for full definitions

Add to suggested reference files:

- `agents/code-review-scanner.md` — read-only test-smell scanner
- `agents/flakiness-detector.md` — read-only determinism auditor
- `agents/traceability-auditor.md` — read-only RTM auditor
- `agents/framework-researcher.md` — read-only web-research agent for self-extension

---

## DIRECTORY HYGIENE (generation-time — MUST follow)

**Never create an empty directory.** Create a directory only at the moment you write the first file into it (`mkdir -p` immediately followed by writing the file). A skill shipped with empty folders is a generation defect (git won't even track them, and the user sees hollow scaffolding).

- `references/framework-review/` — MUST be created **and populated** at generation time with the five up-front checklist files (`playwright.md`, `selenium.md`, `cypress.md`, `wdio.md`, `appium.md`). If you create the directory, you MUST write those files in the same pass. Do not `mkdir` it and move on.
- `references/languages/` — do **NOT** create it at generation time. It is runtime-only; the self-extension protocol creates it together with its first file.
- If you are running low on turns, **prioritize writing the framework-review files over the optional extras** (extra assets, extra agents). Finishing the five framework checklists matters more than scaffolding empty folders.
- Before finishing, verify no directory under the skill is empty (`find <skill> -type d -empty` must return nothing except an intentionally-deferred runtime dir, which should not have been created at all).

---

## EXECUTION ORDER

```
[ ] 1. (Generated skill runtime) Ask candidate name FIRST (Phase 0) — never skip
[ ] 2. Scan submission for languages, frameworks, plan/case artifacts, CI/lint (Phase 1)
[ ] 3. Synthesize stack inventory, review targets, known-vs-unknown frameworks (Phase 2)
[ ] 4. If an unknown framework/language is present → run Self-Extension Protocol (Phase 2.6)
[ ] 5. Generate SKILL.md with the 3 review knowledge bases + self-extension + output contract
[ ] 6. Generate INJECT.md (50-150 token quick ref — must include "ask candidate name first", "HTML report named after candidate", "never auto-fix code under review", "self-extend on unknown framework")
[ ] 7. Generate LEARNED.md (empty template with section headers)
[ ] 8. Generate the 12+ reference files (Phase 4). MUST include framework-review/{playwright,selenium,cypress,wdio,appium}.md (write the files, never just mkdir the dir) + engineering-principles + challenge-questions-bank + self-extension-guide. Do NOT create references/languages/ (runtime-only).
[ ] 9. Generate the 7+ assets (Phase 5), incl. review-report-template.html + best-practices-scorecard.csv
[ ] 10. Generate scripts/validate-review.sh
[ ] 11. Generate agents/ files (all read-only on the submission)
[ ] 12. Run quality gates (Phase 6) — incl. "no empty directories" check from DIRECTORY HYGIENE
[ ] 13. Verify all anti-patterns appear in SKILL.md "Never" table (Phase 7)
```

---

## SOURCES

- ISTQB CTFL v4.0 — [istqb.org](https://www.istqb.org/) (test case quality, design techniques, risk-based testing)
- ISO/IEC/IEEE 29119-3:2021 — test documentation ([iso.org/standard/79429.html](https://www.iso.org/standard/79429.html))
- IEEE 829 — test documentation standard (legacy, still referenced)
- Test automation pyramid — Martin Fowler ([martinfowler.com/articles/practical-test-pyramid.html](https://martinfowler.com/articles/practical-test-pyramid.html))
- Page Object — Martin Fowler ([martinfowler.com/bliki/PageObject.html](https://martinfowler.com/bliki/PageObject.html))
- xUnit Test Patterns / test smells — Gerard Meszaros ([xunitpatterns.com](http://xunitpatterns.com/TestSmells.html))
- Playwright best practices — [playwright.dev/docs/best-practices](https://playwright.dev/docs/best-practices)
- Selenium waits + design — [selenium.dev/documentation/webdriver/waits](https://www.selenium.dev/documentation/webdriver/waits/)
- Cypress best practices — [docs.cypress.io/app/core-concepts/best-practices](https://docs.cypress.io/app/core-concepts/best-practices)
- WebdriverIO best practices — [webdriver.io/docs/bestpractices](https://webdriver.io/docs/bestpractices/)
- Appium best practices — [browserstack.com/guide/appium-best-practices](https://www.browserstack.com/guide/appium-best-practices)
- Gherkin / BDD — [cucumber.io/docs/bdd/better-gherkin](https://cucumber.io/docs/bdd/better-gherkin/)
- SOLID — Robert C. Martin; DAMP vs DRY in tests — Jay Fields; YAGNI / KISS — common engineering canon
- Contract testing — Pact ([pact.io](https://pact.io/))
