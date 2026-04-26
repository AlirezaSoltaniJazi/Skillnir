# Common Issues — Test Automation

> Troubleshooting flakiness, timeouts, selector failures, data issues, and CI problems.

---

## Flaky Tests

### Test passes locally, fails in CI

**Cause**: Timing differences — CI is slower (shared resources, headless rendering, network latency).
**Fix**: Replace `sleep()` with explicit waits. Use `waitForSelector`, `waitForResponse`, or auto-retry assertions. Increase timeouts for CI via config override.

### Test fails intermittently (1 in 10 runs)

**Cause**: Race condition — test acts before UI/API is ready.
**Fix**: Identify the async operation that isn't awaited. Add explicit wait for the specific condition (element visible, API response received, animation completed). Never rely on page load events alone.

### Test fails when run in parallel but passes solo

**Cause**: Shared state — tests modify the same data or depend on execution order.
**Fix**: Use unique test data per test (factories with random/UUID identifiers). Isolate browser context per test. Use API cleanup in afterEach/afterAll.

### Test fails on first run after deploy

**Cause**: Stale test data or missing seed data in the new environment.
**Fix**: Use setup hooks to create required precondition data via API. Never assume data exists — create what you need.

---

## Timeout Issues

### `TimeoutError: locator.click: Timeout 30000ms exceeded`

**Cause**: Element not found, not visible, or overlapped by another element.
**Fix**:
1. Verify the selector is correct (check data-testid exists in DOM)
2. Check if element is inside an iframe (use `frameLocator`)
3. Check if element is hidden behind a modal, overlay, or loading spinner
4. Add `waitFor({ state: 'visible' })` before interaction

### `Navigation timeout of 30000 ms exceeded`

**Cause**: Page takes too long to load, or SPA routing doesn't trigger navigation events.
**Fix**:
1. For SPAs, wait for specific element instead of navigation: `waitForSelector('[data-testid="dashboard"]')`
2. Increase navigation timeout in config for slow environments
3. Check if the URL pattern in `waitForURL` matches the actual redirect

### API request timeout in tests

**Cause**: Test environment API is slow or unreachable.
**Fix**:
1. Verify base URL is correct for the environment
2. Check network connectivity from CI runner
3. Increase API timeout separately from UI timeouts
4. Add retry logic for infrastructure-level failures only

---

## Selector Issues

### Element found but wrong one (multiple matches)

**Cause**: Selector matches more than one element.
**Fix**: Make selector more specific. Use `nth()`, `filter()`, or add a unique `data-testid`. In Playwright: `page.getByTestId('item').nth(0)` or `page.getByTestId('item').filter({ hasText: 'Expected' })`.

### Element detached from DOM

**Cause**: SPA re-renders the element between finding it and interacting with it.
**Fix**: Use framework auto-retry. In Playwright, `locator.click()` auto-retries. Avoid storing elements in variables — use locators (lazy evaluation).

### Shadow DOM elements not found

**Cause**: Standard selectors don't pierce shadow DOM boundaries.
**Fix**: Playwright pierces shadow DOM by default with `getByTestId`. For other frameworks: Cypress `shadow()` command, WebDriverIO `shadow$()`.

---

## Test Data Issues

### Tests fail due to duplicate data

**Cause**: Factory creates data with static values; parallel tests collide.
**Fix**: Generate unique values per invocation: `const email = \`test-\${Date.now()}-\${Math.random().toString(36).slice(2)}@example.com\``.

### Test data not cleaned up

**Cause**: Test creates data but teardown is missing or conditional.
**Fix**: Always add cleanup in `afterEach`/`afterAll`. Use API deletion, not UI navigation for cleanup. Track created resource IDs for deletion.

### Environment-specific data missing

**Cause**: Test assumes data exists (admin user, default category) that hasn't been seeded.
**Fix**: Create precondition data in `beforeAll` via API. Never assume database state — tests should be environment-agnostic.

---

## CI/CD Issues

### Tests pass locally, timeout in CI (all tests)

**Cause**: CI runner has no display server (headless mode not set) or insufficient resources.
**Fix**: Ensure headless mode in CI config. Check CI runner memory/CPU allocation. Use `--workers=2` instead of `--workers=auto` in resource-constrained CI.

### Screenshots/videos not captured on failure

**Cause**: Reporter not configured or output path wrong.
**Fix**: Verify reporter config specifies output directory. Check CI artifact upload step includes the output path. Ensure `screenshot: 'only-on-failure'` and `video: 'retain-on-failure'` are set.

### Browser binary not found in CI

**Cause**: Browser not installed in CI image.
**Fix**: Add browser install step: `npx playwright install --with-deps` (Playwright), `npx cypress install` (Cypress). Cache the browser binary between runs.

---

## Framework-Specific Issues

### Playwright: `browserType.launch: Executable doesn't exist`

**Fix**: Run `npx playwright install` to download browsers. In CI, add `npx playwright install --with-deps chromium` for the specific browser.

### Cypress: `cy.visit() failed trying to load`

**Fix**: Check `baseUrl` in `cypress.config.ts`. Ensure app is running before tests start. Use `cy.visit('/', { failOnStatusCode: false })` if checking error pages.

### WebDriverIO: `session not created: This version of ChromeDriver only supports Chrome version X`

**Fix**: Use `@wdio/chromedriver-service` with `chromedriver: 'auto'` to auto-detect matching version. Pin chromedriver version to match CI Chrome version.

### pytest: `fixture 'page' not found`

**Fix**: Install `pytest-playwright`: `pip install pytest-playwright`. Run `playwright install`. Ensure conftest.py imports are correct.

---

## Performance Issues

### Tests are too slow (full suite >30 min)

**Fix**:
1. Parallelize: use `--workers=4` or `--shards=N`
2. Use API shortcuts for setup instead of UI navigation
3. Share auth state: authenticate once, reuse storage state
4. Move slow E2E to smoke suite, fast API tests to main suite
5. Profile: identify slowest tests and optimize waits

### Memory leaks in long test runs

**Fix**:
1. Close browser context after each test (not just page)
2. Clear large variables in afterEach
3. Limit parallel workers to available memory
4. Use `--max-workers` to cap concurrency
