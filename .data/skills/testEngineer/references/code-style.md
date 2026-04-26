# Test Code Style Guide

> Test naming, file naming, assertion conventions, and formatting rules with full examples.

---

## File Naming

| Framework          | Pattern                                 | Examples                                         |
| ------------------ | --------------------------------------- | ------------------------------------------------ |
| Playwright         | `feature-name.spec.ts`                  | `login.spec.ts`, `checkout.spec.ts`              |
| Cypress            | `feature-name.cy.ts`                    | `login.cy.ts`, `checkout.cy.ts`                  |
| WebDriverIO        | `feature-name.e2e.ts`                   | `login.e2e.ts`, `checkout.e2e.ts`                |
| Jest/Vitest        | `feature-name.test.ts`                  | `login.test.ts`, `api-users.test.ts`             |
| pytest             | `test_feature_name.py`                  | `test_login.py`, `test_checkout.py`              |
| JUnit/TestNG       | `FeatureNameTest.java`                  | `LoginTest.java`, `CheckoutTest.java`            |
| Page Objects (JS)  | `PascalCase.ts` or `kebab-case.page.ts` | `LoginPage.ts`, `login.page.ts`                 |
| Page Objects (Py)  | `snake_case_page.py`                    | `login_page.py`, `dashboard_page.py`             |

---

## Test Naming (describe/it blocks)

### JavaScript / TypeScript

```typescript
// ✅ Correct — describes user behavior
describe('Login Page', () => {
  it('should display error message for invalid credentials', async () => {
    // ...
  });

  it('should redirect to dashboard after successful login', async () => {
    // ...
  });

  it('should disable submit button while request is pending', async () => {
    // ...
  });
});

// ❌ Wrong — vague, implementation-focused
describe('Login', () => {
  it('test1', async () => { /* ... */ });
  it('works', async () => { /* ... */ });
  it('should call the API', async () => { /* ... */ });
});
```

### Python (pytest)

```python
# ✅ Correct — behavior + condition
class TestLoginPage:
    def test_displays_error_for_invalid_credentials(self, login_page):
        ...

    def test_redirects_to_dashboard_after_successful_login(self, login_page):
        ...

    def test_disables_submit_while_request_pending(self, login_page):
        ...

# ❌ Wrong — vague naming
class TestLogin:
    def test_login(self): ...
    def test_it_works(self): ...
```

### Java (JUnit/TestNG)

```java
// ✅ Correct — method name describes behavior
@Test
void shouldDisplayErrorForInvalidCredentials() { ... }

@Test
void shouldRedirectToDashboardAfterSuccessfulLogin() { ... }

// ❌ Wrong
@Test
void testLogin() { ... }
```

---

## Assertion Style

### BDD-style (expect) — preferred for JS/TS

```typescript
// ✅ Preferred — reads like a sentence
expect(errorMessage).toBeVisible();
expect(title).toHaveText('Dashboard');
expect(items).toHaveLength(3);
expect(response.status).toBe(200);

// ✅ Playwright built-in assertions (auto-retry)
await expect(page.getByTestId('error')).toBeVisible();
await expect(page.getByRole('heading')).toHaveText('Welcome');

// ❌ Avoid — generic truthiness checks
expect(errorMessage !== null).toBe(true);
expect(title.includes('Dashboard')).toBeTruthy();
```

### pytest assertions — preferred for Python

```python
# ✅ Direct assertions with descriptive messages
assert login_page.error_message.is_displayed(), 'Error message should be visible'
assert response.status_code == 200, f'Expected 200, got {response.status_code}'
assert len(items) == 3, f'Expected 3 items, got {len(items)}'

# ✅ pytest-specific matchers
import pytest
with pytest.raises(ValueError, match='invalid email'):
    validate_email('')
```

### AssertJ — preferred for Java

```java
// ✅ Fluent assertions
assertThat(errorMessage).isDisplayed();
assertThat(response.statusCode()).isEqualTo(200);
assertThat(items).hasSize(3).extracting("name").contains("Item A");
```

---

## Locator Strategy (Priority Order)

1. **data-testid** — `[data-testid="login-submit"]` — most stable, test-specific
2. **Accessibility role** — `getByRole('button', { name: 'Submit' })` — accessible + stable
3. **Label/placeholder** — `getByLabel('Email')` — user-facing text
4. **Text content** — `getByText('Sign In')` — visible text (fragile with i18n)
5. **CSS selector** — `.login-form .submit-btn` — structural coupling
6. **XPath** — `//div[@class='form']//button` — last resort, fragile

```typescript
// ✅ Priority 1: data-testid
page.getByTestId('login-submit');

// ✅ Priority 2: accessibility role
page.getByRole('button', { name: 'Submit' });

// ✅ Priority 3: label
page.getByLabel('Email address');

// ❌ Avoid: fragile CSS
page.locator('.btn.btn-primary.submit-action');

// ❌ Avoid: XPath
page.locator('//div[@class="form"]/div[3]/button');
```

---

## Page Object Style

### TypeScript/JavaScript

```typescript
// ✅ Correct — encapsulated locators, action methods, no assertions
export class LoginPage {
  private readonly emailInput = this.page.getByTestId('email-input');
  private readonly passwordInput = this.page.getByTestId('password-input');
  private readonly submitButton = this.page.getByTestId('login-submit');
  private readonly errorMessage = this.page.getByTestId('login-error');

  constructor(private readonly page: Page) {}

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async getErrorText(): Promise<string> {
    return this.errorMessage.textContent() ?? '';
  }

  // ❌ NEVER: assertions inside page objects
  // async verifyErrorShown() { expect(this.errorMessage).toBeVisible(); }
}
```

### Python

```python
# ✅ Correct — no assertions, returns values
class LoginPage:
    def __init__(self, page):
        self.page = page
        self._email_input = page.get_by_test_id('email-input')
        self._password_input = page.get_by_test_id('password-input')
        self._submit_button = page.get_by_test_id('login-submit')
        self._error_message = page.get_by_test_id('login-error')

    def login(self, email: str, password: str) -> None:
        self._email_input.fill(email)
        self._password_input.fill(password)
        self._submit_button.click()

    def get_error_text(self) -> str:
        return self._error_message.text_content() or ''
```

---

## Import Order (JavaScript/TypeScript)

```typescript
// 1. Test framework imports
import { test, expect } from '@playwright/test';

// 2. Page objects and components
import { LoginPage } from '../pages/LoginPage';
import { NavBar } from '../components/NavBar';

// 3. Fixtures and factories
import { createUser } from '../fixtures/users';

// 4. Helpers and utilities
import { waitForNetworkIdle } from '../helpers/waits';
```

---

## Import Order (Python)

```python
# 1. stdlib
import json
from pathlib import Path

# 2. third-party + test framework
import pytest
from playwright.sync_api import Page, expect

# 3. local test code — page objects
from pages.login_page import LoginPage

# 4. local test code — fixtures, helpers
from fixtures.users import create_test_user
from helpers.api_client import ApiClient
```
