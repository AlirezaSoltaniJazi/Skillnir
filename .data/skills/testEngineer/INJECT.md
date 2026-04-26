# testEngineer — Quick Reference

<!-- INJECT.md is always loaded into the agent's context (50-150 tokens max).
     It serves as a hallucination firewall — a compact cheat-sheet of the
     most critical facts the agent needs to know at all times. -->

- **FIRST**: Read [LEARNED.md](LEARNED.md) — corrections and preferences from previous sessions
- **Stack**: Playwright/Cypress/WebDriverIO/Selenium, Jest/Vitest/Mocha/pytest/JUnit, TypeScript/JavaScript/Python/Java
- **Test types**: E2E/UI, API/integration, component/visual, performance/load
- **Key dirs**: `tests/`, `e2e/`, `integration/`, `pages/` (page objects), `fixtures/`, `helpers/`
- **Patterns**: Page Object Model (no assertions in POs); factory-based test data; explicit waits (never sleep); one assertion per test; isolated tests (no shared state)
- **Never**: `sleep()` for waits; assertions in page objects; shared mutable state between tests; hard-coded test data; brittle XPath/CSS selectors over data-testid
- **Sub-agents**: flake-analyzer (stability), coverage-analyzer (gap analysis), test-data-designer (fixtures)
- **Self-learning**: On correction -> write to LEARNED.md. On ambiguity -> check LEARNED.md first.
- **Full guide**: See [SKILL.md](SKILL.md) for conventions and [references/](references/) for detailed examples
