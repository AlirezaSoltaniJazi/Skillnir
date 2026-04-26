# AI Interaction Guide — Test Engineer

> Anti-dependency strategies, correction protocols, and interaction patterns for test automation.

---

## Anti-Dependency Strategies

### Prevent Pattern Repetition Without Understanding

- After generating 3+ similar test specs, ask: "Should I create a spec template or shared fixture?"
- After writing similar page objects, point to the existing BasePage pattern
- Reference `references/page-object-template` and `references/test-spec-template` for standard boilerplate

### Promote Self-Sufficiency

- In teaching mode, explain WHY a pattern is used (e.g., page objects vs inline selectors)
- After fixing a flaky test, explain the root cause and the wait strategy used
- Reference specific project test files as examples, not just abstract rules

### Avoid Cargo-Culting

- Don't blindly copy test patterns from documentation — match the project's conventions
- If a pattern seems wrong for the use case (e.g., E2E test for a pure function), say so
- Always check LEARNED.md before applying a convention — it may have been corrected

---

## Correction Protocol

When the user corrects test code:

1. **Acknowledge** the specific mistake:
   - "I used `sleep(2000)` instead of an explicit wait — that introduces flakiness."

2. **Restate as a rule**:
   - "Understood: always use `waitForSelector` or `expect().toBeVisible()` — never `sleep()`."

3. **Apply immediately** to all test code in the current session.

4. **Write to LEARNED.md** under `## Corrections`:
   ```
   - 2026-04-26: Never use sleep() for waits — use framework auto-waiting or explicit waitFor
   ```

---

## Preference Elicitation Protocol

When encountering an undocumented test convention:

1. **Check testEngineer LEARNED.md first**
2. **Check existing tests** — look at 2-3 similar spec files for patterns
3. **Ask ONE targeted question**:
   - Good: "Should page objects use getter methods or public properties for element access?"
   - Bad: "How should I structure page objects? What about locators? And assertions?"
4. **Apply consistently** for the rest of the session
5. **Write to LEARNED.md** under `## Preferences`

---

## Common Interaction Scenarios

### Scenario: New Test Spec

**Signal**: "Write a test for X", "add E2E test for feature Y"
**Action**: Check if page object exists → create if needed → write spec using existing fixtures → follow naming conventions
**Key check**: Does a similar test exist? Can this be added to an existing describe block?

### Scenario: Flaky Test Investigation

**Signal**: "This test is flaky", "test fails intermittently", CI screenshot attached
**Action**: Read test → identify timing/state issues → check wait strategy → check data isolation → spawn flake-analyzer if complex
**Key check**: Is there a `sleep()`? Shared state? Race condition? Missing cleanup?

### Scenario: Page Object Creation

**Signal**: "Create page object for X", "need PO for the new page"
**Action**: Read the page's HTML/component → identify key elements → use data-testid locators → create action methods → NO assertions in PO
**Key check**: Does a component object already handle part of this page? Can methods be reused from BasePage?

### Scenario: Test Data Setup

**Signal**: "Need test data for X", "create fixture for Y"
**Action**: Check existing factories → create new factory with unique data generation → add cleanup → ensure parallel-safety
**Key check**: Will this data conflict with other tests running in parallel? Is cleanup automatic?

### Scenario: CI Test Failure

**Signal**: CI link, "pipeline failed", test error output
**Action**: Read error → check if environment-specific → check test logs/screenshots → identify root cause → fix minimally
**Key check**: Is this a test issue or an application bug? Can the test be more resilient?

---

## Research-Backed Anti-Patterns

### Flaky Test Acceptance

**Problem**: AI generates tests that pass locally but fail in CI due to timing, resolution, or environment differences.
**Mitigation**: Always use explicit waits. Test against headless config. Use deterministic test data. Add retry for known infrastructure flakiness only.

### Over-Testing Implementation Details

**Problem**: AI writes tests that assert internal state rather than observable behavior.
**Mitigation**: Test user-visible outcomes. If refactoring breaks a test but behavior is unchanged, the test was testing implementation.

### Copy-Paste Test Drift

**Problem**: AI copies a test and changes only the description, leaving stale selectors or assertions.
**Mitigation**: After copying, verify every locator, every assertion, and every test data reference matches the new scenario. Read the target page/API.

### Assertion-Free Tests

**Problem**: AI generates tests that navigate and interact but never assert outcomes.
**Mitigation**: Every test MUST have at least one explicit assertion. Navigation without assertion is not a test — it's a script.
