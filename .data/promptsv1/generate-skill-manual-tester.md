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
