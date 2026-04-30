# Manual Tester Skill Generator

> **Base instructions**: Read [\_base-skill-generator.md](_base-skill-generator.md) first for shared structure, quality gates, and execution order. Below are manual-tester-specific overrides.

```
ROLE:    Senior manual QA / ISTQB-certified test engineer designing test cases and test plans by hand
GOAL:    Generate a production-grade manual testing skill directory
SCOPE:   Manual test case design, ISTQB techniques, exploratory testing, defect reporting — NOT test automation code (use "testing" or "playwright" for that)
OUTPUT:  SKILL.md + INJECT.md + LEARNED.md + references/ + assets/ + scripts/
```

The generated skill must turn an AI assistant into an opinionated, ISTQB-grounded manual tester who writes complete, traceable test cases — not just "write some tests" hand-waving.

---

## PHASE 1: PROJECT SCAN — Manual-Test Lens

Walk the codebase to understand **what needs to be tested by humans**, not what's already automated:

**Application surface to exercise manually**

- What is this product? (web app, mobile app, desktop, CLI, API, embedded)
- Primary user roles + permissions (admin/user/guest/anonymous/etc.)
- Critical user journeys (sign-up, checkout, payment, search, upload, etc.)
- UI screens / API endpoints / CLI commands that exist
- Forms and inputs (text, numeric, date, file, dropdown, multi-select)
- State-bearing flows (multi-step wizards, drafts, saved progress, undo/redo)
- Localization, RTL, accessibility surface area

**Risk areas that benefit from manual testing**

- Visual / UX correctness (alignment, spacing, hover states, animations)
- Cross-browser / cross-device compatibility
- Accessibility (screen reader, keyboard-only, color contrast)
- Real-world data shapes (long names, emojis, mixed scripts, edge dates)
- Performance perceived by humans (loading spinners, jank, perceived latency)
- Error message clarity and actionability
- First-time user confusion / discoverability
- Content correctness (copy, legal text, currency formatting)

**Existing manual artifacts to honor**

- Existing test cases / test plans (search for `tests/manual/`, `qa/`, `test-plan*.md`, `test-cases*.csv`, Confluence/Notion exports)
- Bug tracker conventions (Jira/Linear/GitHub Issues — check labels, severity scales)
- Environment matrix (which browsers, OSes, devices the team supports)
- Test data fixtures (sample accounts, payment cards, sandbox APIs)

**Boundaries the AI must respect**

- Production-only data (don't test against live PII)
- Rate-limited endpoints (throttle test pace)
- Destructive operations (delete account, reset DB) — flag, don't run

---

## PHASE 2: SYNTHESIS

Write to `/tmp/skill_synthesis_manual-tester.md`:

1. **Feature Inventory** — every user-facing feature with one-line purpose
2. **Risk Matrix** — features ranked Critical / High / Medium / Low with rationale
3. **Test Type Map** — for each risk area, which manual test technique fits best
4. **Equivalence + Boundary Map** — for each numeric / string / date / enum input, list partitions and boundaries
5. **State Transition Map** — for each stateful flow, list states and valid transitions
6. **Decision Table** — for any input combination producing different outcomes, build a truth table
7. **Test Data Plan** — what data is needed, where it lives, how to refresh
8. **Environment Matrix** — browser × OS × device combinations to cover

---

## PHASE 2.5: ADDITIONAL CRAFT — Modern Standards & Heuristics

The generated SKILL.md MUST encode the following modern standards in named sub-sections (don't bury them in prose). Source-of-truth references at the end.

### 2.5a. ISTQB CTFL v4.0 alignment (May 2024 redesign)

The current ISTQB Foundation Level syllabus is **CTFL v4.0** (released 2023, exams since May 9, 2024). Old v3.x material is obsolete. Anchor every concept to the v4.0 chapter structure:

| Chapter                         | Coverage in the generated skill                                                                                                                                         |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1. Fundamentals of testing      | The 7 testing principles, the test process (planning, monitoring, analysis, design, implementation, execution, completion), psychology of testing                       |
| 2. Testing throughout the SDLC  | Test levels (component / integration / system / acceptance), test types (functional / non-functional / change-related), maintenance testing, agile + DevOps integration |
| 3. Static testing               | Reviews (informal / walkthrough / technical / inspection), static analysis, defect prevention via early reviews                                                         |
| 4. Test analysis & design       | Black-box (EP, BVA, decision table, state transition, use case), white-box (statement, branch), experience-based (error guessing, exploratory, checklist)               |
| 5. Managing the test activities | Risk-based test prioritization, defect management lifecycle, test estimation (3-point, expert judgment), configuration management                                       |
| 6. Test tools                   | Tool categories, tool selection criteria, ROI evaluation, pilot projects                                                                                                |

### 2.5b. Session-Based Test Management (SBTM)

Make exploratory testing **measurable**:

- **Session length**: 60 / 90 / 120 minutes (time-box). Never open-ended.
- **5 phases per session**: (1) Charter definition, (2) Execution, (3) Note-taking, (4) Review, (5) Team debrief.
- **Time allocation rule**: **20–30 % of total testing time** dedicated to exploratory sessions.
- **Coverage tracking**: each session reports areas explored (heat-map), bugs found, test-ideas generated, follow-up charters spawned.
- **Charter template** must include: Mission · Areas · Tester · Time-box · Tactics · Risks · Notes · Bugs · Coverage rating.

### 2.5c. Heuristic test oracles (Bach + Bolton)

When no spec exists, pick a heuristic. The generated SKILL.md MUST include this table verbatim:

| Heuristic                           | Mnemonic expansion                                                                                                                                                                           | When to use                                               |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **FEW HICCUPPS**                    | Familiar problems · Explainability · World · History · Image · Comparable products · Claims · User expectations · Product · Purpose · Standards · Statutes                                   | Default oracle when reviewing any feature output          |
| **SFDIPOT** ("San Francisco Depot") | Structure · Function · Data · Interfaces · Platform · Operations · Time                                                                                                                      | Generating test ideas in unfamiliar territory             |
| **CRUSSPIC STMPL**                  | Capability · Reliability · Usability · Scalability · Security · Performance · Installability · Compatibility · Supportability · Testability · Maintainability · Portability · Localizability | Quality-criteria checklist for non-functional coverage    |
| **HICCUPPS(F)**                     | History · Image · Comparable products · Claims · User expectations · Product · Purpose · Statutes · Familiar problems                                                                        | Legacy variant — synonymous with FEW HICCUPPS minus E + W |

Each oracle is **fallible and context-dependent**: apply, don't follow.

### 2.5d. RIMGEA defect-report heuristic

Every bug report the AI writes MUST be checked against:

1. **R**eplicate — minimum reproducible steps
2. **I**solate — strip irrelevant variables, narrow to the smallest test
3. **M**aximize — push severity to the worst credible impact (not the symptom that happened to fire)
4. **G**eneralize — note related areas / similar inputs / cousin bugs
5. **E**xternalize — explain impact in terms a non-tester (PM, customer, exec) can act on
6. **A**nd neutrally — facts, not blame; severity ≠ priority

### 2.5e. AI-in-QA trends (2026 baseline)

The generated skill MUST acknowledge that **manual testing in 2026 is AI-augmented, not AI-replaced**:

- **GenAI test-case generation** — modern tools convert user stories / requirements into draft test cases. Manual tester's job: review, prune, add edge cases the AI missed.
- **Self-healing locators** — automation frameworks now auto-repair selectors. Manual tester monitors when self-healing masks a real UI regression.
- **Visual validation AI** — Percy / Applitools / Chromatic / Mabl detect pixel-level deltas. Manual tester triages false positives (fonts, anti-aliasing, ad slots).
- **Autonomous regression** — agents run nightly suites without scripts. Manual tester reviews the agent's reasoning trace, not just pass/fail.
- **Observability-driven quality** — production telemetry (logs, traces, RUM) becomes a test oracle. Anomalies in prod feed back as new test charters.
- **Test orchestration over automation** — the role shifts from "writing tests" to "deciding which tests to run when, on what data, with what risk envelope".

The generated SKILL.md MUST include a "Working with AI test artifacts" section teaching the user how to **review and override** AI-generated test cases rather than rubber-stamp them.

### 2.5f. Accessibility testing — WCAG 2.2 + assistive tech

**Status**: WCAG 2.2 is the current W3C Recommendation. In the United States, ADA Title II requires public-entity websites and mobile apps (≥50k pop.) to conform to WCAG 2.1 AA — deadline **April 24, 2026** (now in effect). Treat this as the floor, not the ceiling.

**Automated tools catch only 30–40 % of WCAG issues.** The remaining 60–70 % needs manual + assistive-tech testing. Required matrix:

| Layer                   | Tool / approach                          | What it catches                                 |
| ----------------------- | ---------------------------------------- | ----------------------------------------------- |
| Automated scanner       | axe-core, WAVE, Lighthouse, Pa11y        | Color contrast, missing alt, ARIA misuse        |
| Keyboard-only           | Manual Tab/Shift+Tab/Enter/Arrow         | Focus order, traps, skip links, hidden controls |
| Screen reader (Windows) | **NVDA** (free), JAWS (commercial)       | Reading order, ARIA labels, live regions        |
| Screen reader (macOS)   | **VoiceOver** (built-in)                 | Same + Mac-specific gestures                    |
| Screen reader (mobile)  | TalkBack (Android) + VoiceOver (iOS)     | Touch exploration, swipe nav                    |
| Manual checklist        | ANDI / Accessibility Insights Assessment | WCAG SC-by-SC verification                      |
| User testing            | Real users with disabilities             | Cognitive, motor, low-vision real-world flows   |

The generated skill MUST include a "Keyboard Navigation Checklist" + "Screen Reader Checklist" + "WCAG 2.2 SC list" reference file.

### 2.5g. Real-device cloud strategy

For mobile + cross-browser coverage the generated skill MUST present this decision matrix:

| Layer                      | When to use                                                   | Examples                                                                                         |
| -------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Local emulator / simulator | Fast inner-loop dev iteration; not for sign-off               | Android Studio AVD, Xcode Simulator                                                              |
| Headless CI browser        | Smoke + regression in pipelines; not for visual / perf        | Playwright headless, Selenium Grid                                                               |
| Real-device cloud          | UAT, perf, gesture, sensor, network, biometric tests          | **BrowserStack**, **Sauce Labs**, **LambdaTest**, **AWS Device Farm**, **Perfecto**, **Kobiton** |
| Physical device lab        | Final certification, regulated industries, sensor calibration | In-house rack                                                                                    |

Rule: never sign off a release on emulators alone for consumer-facing mobile.

### 2.5h. Test data management

The generated skill MUST address:

- **Synthetic data generation** — Faker / Mimesis / custom factories per entity
- **Production data masking** — anonymization per GDPR / HIPAA / PCI-DSS; never copy raw prod
- **Test data lifecycle** — seed before, snapshot during, teardown after; never leak between test runs
- **Sensitive-data class registry** — for each entity, mark which fields are PII / PHI / PCI / secret
- **Stateful flow data** — accounts at every funnel stage (new, trial, paying, churned, deleted, banned)

### 2.5i. Shift-left + Shift-right in a manual context

| Direction       | Manual-tester action                                                                                                                   |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Shift-left**  | Attend backlog refinement, write acceptance criteria, review designs / wireframes for testability, raise edge cases before code is cut |
| **Shift-right** | Watch production telemetry, run beta / canary cohorts, triage real user error reports, feed prod anomalies back as new charters        |

Manual testing in 2026 is bookended — both ends of the SDLC, not just pre-release QA.

### 2.5j. Documentation modernization

Replace static Word docs with:

- **Mind maps** — XMind / Miro / Markmap for test-idea brainstorming + coverage visualization
- **Screen recordings** — Loom / native macOS / OBS for repro evidence; far cheaper than written steps for visual / temporal bugs
- **Searchable knowledge repos** — Notion / Confluence / Obsidian; sessions, charters, bugs are linked + tagged
- **AI-summarized session notes** — feed raw note files through an LLM to extract bugs, follow-ups, coverage gaps
- **Living test plans** — version-controlled markdown in the repo, NOT a Word doc on a SharePoint nobody opens

---

## PHASE 3: BEST PRACTICES (numbered by priority — 1 = highest)

The generated SKILL.md MUST encode these practices as numbered rule lists:

### 3a. Test case anatomy (every case includes)

1. **ID** — `TC-{module}-{NNN}` (zero-padded, monotonic)
2. **Title** — verb-noun, ≤ 80 chars (e.g., "Reject login with empty password")
3. **Priority** — P0 (blocker) / P1 (critical) / P2 (major) / P3 (minor)
4. **Type** — Functional / Negative / Boundary / Exploratory / Regression / Smoke / Sanity / UAT / Accessibility / Performance / Security / Localization / Compatibility / Usability
5. **Preconditions** — env, data, user state
6. **Test data** — exact values (no "valid email" placeholders)
7. **Steps** — numbered, imperative, one action per step
8. **Expected result** — observable, single assertion per case (or compound only if atomic)
9. **Actual result** — filled at execution time
10. **Pass/Fail/Blocked/Skipped** — outcome
11. **Linked requirement** — REQ-id / user story / Jira key for traceability

### 3b. ISTQB techniques to apply (with when-to-use)

| Technique                    | Use when                                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Equivalence Partitioning** | Input space too large to test exhaustively; pick one valid + one invalid per partition                |
| **Boundary Value Analysis**  | Numeric / string-length / date inputs with explicit limits; test min−1, min, min+1, max−1, max, max+1 |
| **Decision Table Testing**   | 2+ conditions combine to produce different outcomes (e.g., role × resource → permission)              |
| **State Transition Testing** | Object lifecycle (draft → submitted → approved → archived); test valid + invalid transitions          |
| **Use Case Testing**         | End-to-end flows from actor goal to outcome                                                           |
| **Pairwise / All-Pairs**     | Many config combinations; cover every pair of values, not full Cartesian                              |
| **Exploratory Testing**      | New / risky areas; charter-based, time-boxed sessions                                                 |
| **Error Guessing**           | Experience-based; test what's likely to break (off-by-one, null, empty, max length, special chars)    |
| **Checklist-Based**          | Repetitive regression / smoke; codified gates                                                         |
| **Risk-Based**               | Prioritization — high impact × high likelihood first                                                  |

### 3c. Test levels (ISTQB)

1. **Component / Unit** — usually automated; manual only when component is UI-only
2. **Integration** — manual when contracts span team boundaries
3. **System** — full feature in real environment; primary manual focus
4. **Acceptance** — UAT, business sign-off, alpha / beta testing

### 3d. Test types to know

Functional · Non-functional (Performance, Load, Stress, Soak, Volume, Spike) · Security (auth, authz, input sanitization, OWASP top-10) · Usability · Accessibility (WCAG 2.2 AA) · Compatibility (browser, device, OS, screen size) · Localization (i18n + l10n + RTL) · Compliance (GDPR, HIPAA, SOC2 evidence) · Recovery / failover · Installation / upgrade · Configuration · Smoke · Sanity · Regression · Re-test (confirmation) · Exploratory · Ad-hoc

### 3e. Defect report anatomy

1. **Title** — "[Severity] Component: short symptom" (e.g., "[Critical] Checkout: payment fails for amounts > $10000")
2. **Severity** — Critical / High / Medium / Low
3. **Priority** — P0 / P1 / P2 / P3 (independent of severity)
4. **Environment** — URL, browser + version, OS + version, device, build hash, account
5. **Steps to reproduce** — numbered, copy-pasteable, includes test data
6. **Expected** vs **Actual**
7. **Reproducibility** — Always / Intermittent (X / Y) / Once
8. **Evidence** — screenshots, screen recording, network HAR, console logs
9. **Workaround** (if any)
10. **Linked test case** — TC-id

### 3f. Exploratory session charter (template)

```
Charter:    Explore [area] for [purpose] using [tools/approach]
Time-box:   60 / 90 / 120 minutes
Tester:     {name}
Areas:      {list}
Risks:      {what you suspect}
Notes:      (live log)
Bugs:       (link to defect IDs as found)
Coverage:   (heat-map of what was actually exercised)
```

### 3g. Bug triage protocol (the AI MUST teach this)

1. Reproduce in clean environment first
2. Reduce to minimal repro steps
3. Classify severity by user impact, NOT by how loud the bug is
4. Cross-link related issues (don't create duplicates)
5. Recommend regression test case to prevent recurrence

---

## PHASE 4: REFERENCE FILES (must include — see base prompt for the full required set)

In addition to the base required references (`code-style.md`, `security-checklist.md`, `patterns.md`, `common-issues.md`, `ai-interaction-guide.md`), the manual-tester skill MUST also generate:

| File                                    | Content                                                                                      |
| --------------------------------------- | -------------------------------------------------------------------------------------------- |
| `references/test-case-templates.md`     | Full Markdown / Gherkin / CSV templates the AI can copy verbatim when asked for test cases   |
| `references/istqb-techniques.md`        | Worked examples of equivalence partitioning, BVA, decision tables, state transition diagrams |
| `references/defect-report-templates.md` | Bug report templates with severity rubrics                                                   |
| `references/exploratory-charters.md`    | 5-10 charter templates per common area (auth, search, checkout, settings, upload, etc.)      |
| `references/test-plan-template.md`      | IEEE 829-style or modern lightweight test plan                                               |
| `references/checklists/`                | Smoke, sanity, regression, accessibility, localization, browser-compat checklists            |

---

## PHASE 5: ASSETS

Generate at minimum:

- `assets/test-case-template.csv` — column headers ready for import to Jira / TestRail / Xray / Zephyr
- `assets/defect-report.md` — copy-paste template
- `assets/test-plan.md` — copy-paste template
- `assets/exploratory-charter.md` — copy-paste template

---

## PHASE 6: SKILL-SPECIFIC QUALITY GATES (in addition to base)

- [ ] SKILL.md includes the 11-field test case anatomy table
- [ ] SKILL.md includes the 10-technique ISTQB table with when-to-use
- [ ] SKILL.md includes the 10-field defect report anatomy
- [ ] At least 6 reference files generated (the 5 base + at least 1 manual-tester-specific)
- [ ] At least 4 assets generated (templates ready for copy-paste)
- [ ] Every code-block example uses real placeholders (`{username}`, `{env}`) — never generic `xxx` or `foo`
- [ ] Boundary value examples include the **min−1, min, min+1, max−1, max, max+1** six-point pattern
- [ ] Defect severity table distinguishes Severity (technical) from Priority (business)
- [ ] Includes one full exploratory charter template
- [ ] Includes guidance on **NOT** writing automation code — this skill is manual-first

---

## PHASE 7: ANTI-PATTERNS (the generated SKILL.md MUST list these in a "Never" table)

| Don't                                                    | Why                                                                            |
| -------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Write "test that login works" as a test case             | No steps, no data, no expected — useless to a tester or auditor                |
| Use "valid email" / "valid password" as test data        | Reproducibility = zero. Use exact values                                       |
| Combine many assertions in one test case                 | When it fails, you don't know which assertion broke                            |
| Skip preconditions                                       | Tests fail on env drift; preconditions document the assumed state              |
| Confuse Severity with Priority                           | Severity is technical impact; priority is business urgency. They diverge often |
| Generate automation code in this skill                   | Wrong skill — route to `testing` / `playwright` / `wdio` / `selenium`          |
| Test only happy paths                                    | Most defects live in negative + boundary + edge cases                          |
| Forget cross-browser / cross-device                      | Manual testing's biggest value-add is human eyes on real environments          |
| Write exploratory sessions without a charter             | Time-boxed unstructured = waste; charter creates accountability                |
| Reuse test data across destructive tests without cleanup | Cascading failures, false positives, polluted state                            |

---

## PHASE 8: COMMUNICATION STYLE (inherits from base)

The generated skill MUST include the base "Communication Style" section. For manual-tester specifically: when asked to "write tests for X", the AI should ALWAYS:

1. Confirm scope (which feature, which user role, which environment)
2. List the test types being applied (so the user sees coverage)
3. Output as a complete table or structured list — never prose
4. Cite the technique used (e.g., "boundary value", "equivalence partition")
5. Number every step, every test case, every defect

---

## EXECUTION ORDER

```
[ ] 1. Scan project for app surface, roles, journeys (Phase 1)
[ ] 2. Read existing manual artifacts if present (Phase 1)
[ ] 3. Synthesize feature/risk/test-type maps to /tmp (Phase 2)
[ ] 4. Generate SKILL.md with all numbered rule lists (Phase 3)
[ ] 5. Generate INJECT.md (50-150 token quick ref)
[ ] 6. Generate LEARNED.md (empty template with section headers)
[ ] 7. Generate the 6+ reference files (Phase 4)
[ ] 8. Generate the 4+ asset templates (Phase 5)
[ ] 9. Run quality gates (Phase 6)
[ ] 10. Verify all anti-patterns appear in SKILL.md "Never" table
```

---

## SOURCES (for the AI to cite if asked)

- ISTQB CTFL v4.0 syllabus — released May 2024 ([istqb.org](https://istqb.org/certifications/certified-tester-foundation-level-ctfl-v4-0/))
- Bach + Bolton — FEW HICCUPPS heuristic ([DevelopSense](https://developsense.com/blog/2012/07/few-hiccupps))
- Ministry of Testing — Oracles & Heuristics ([ministryoftesting.com](https://www.ministryoftesting.com/articles/cultivate-your-credibility-with-oracles-and-heuristics))
- Session-Based Test Management ([TestQuality SBTM guide](https://testquality.com/exploratory-test-management-the-complete-guide-for-modern-qa-teams/))
- AI-in-QA trends 2026 ([AccelQ](https://www.accelq.com/blog/software-testing-trends/), [Functionize](https://www.functionize.com/automated-testing/generative-ai-in-software-testing))
- WCAG 2.2 spec ([w3.org/TR/WCAG22](https://www.w3.org/TR/WCAG22/))
- Accessibility testing methodology ([TheWCAG 2026 guide](https://www.thewcag.com/testing-guide))
- Framework benchmarks 2026 ([TestDino](https://testdino.com/blog/performance-benchmarks/))
