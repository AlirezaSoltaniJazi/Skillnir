# UI / E2E Test Patterns

> Browser automation, page object design, wait strategies, and common UI interaction patterns with full examples.

---

## Page Object Model — Full Example

### BasePage (shared across all page objects)

```typescript
import { Page, Locator } from '@playwright/test';

export abstract class BasePage {
  protected readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  // Navigation
  async navigate(path: string): Promise<void> {
    await this.page.goto(path);
  }

  async getCurrentUrl(): Promise<string> {
    return this.page.url();
  }

  // Common elements (header, footer, nav)
  get navBar(): Locator {
    return this.page.getByTestId('nav-bar');
  }

  get loadingSpinner(): Locator {
    return this.page.getByTestId('loading-spinner');
  }

  // Common waits
  async waitForPageLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async waitForSpinnerToDisappear(): Promise<void> {
    await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 });
  }
}
```

### Concrete Page Object

```typescript
import { Locator, Page } from '@playwright/test';
import { BasePage } from './BasePage';

export class CheckoutPage extends BasePage {
  // Locators — private, using data-testid
  private readonly cartItems: Locator;
  private readonly subtotalAmount: Locator;
  private readonly promoCodeInput: Locator;
  private readonly applyPromoButton: Locator;
  private readonly placeOrderButton: Locator;
  private readonly orderConfirmation: Locator;

  constructor(page: Page) {
    super(page);
    this.cartItems = page.getByTestId('cart-item');
    this.subtotalAmount = page.getByTestId('subtotal-amount');
    this.promoCodeInput = page.getByTestId('promo-code-input');
    this.applyPromoButton = page.getByTestId('apply-promo');
    this.placeOrderButton = page.getByTestId('place-order');
    this.orderConfirmation = page.getByTestId('order-confirmation');
  }

  // Actions — return void or data, NEVER assert
  async applyPromoCode(code: string): Promise<void> {
    await this.promoCodeInput.fill(code);
    await this.applyPromoButton.click();
  }

  async placeOrder(): Promise<void> {
    await this.placeOrderButton.click();
  }

  // Queries — return data for specs to assert
  async getCartItemCount(): Promise<number> {
    return this.cartItems.count();
  }

  async getSubtotal(): Promise<string> {
    return (await this.subtotalAmount.textContent()) ?? '';
  }

  async getConfirmationText(): Promise<string> {
    return (await this.orderConfirmation.textContent()) ?? '';
  }

  // State checks — return booleans
  async isOrderButtonEnabled(): Promise<boolean> {
    return this.placeOrderButton.isEnabled();
  }
}
```

---

## Wait Strategies

### Playwright Auto-Waiting (preferred)

```typescript
// ✅ Playwright auto-waits for actionability
await page.getByTestId('submit').click();          // waits for visible + enabled
await page.getByTestId('input').fill('value');     // waits for visible + editable

// ✅ Assertion auto-retry (up to timeout)
await expect(page.getByTestId('result')).toBeVisible();
await expect(page.getByTestId('count')).toHaveText('5');
```

### Explicit Waits (when auto-wait isn't enough)

```typescript
// Wait for element state
await page.getByTestId('modal').waitFor({ state: 'visible', timeout: 5000 });
await page.getByTestId('spinner').waitFor({ state: 'hidden' });

// Wait for network
await page.waitForResponse(resp => resp.url().includes('/api/data') && resp.status() === 200);

// Wait for navigation
await Promise.all([
  page.waitForURL('**/dashboard'),
  page.getByTestId('login-submit').click(),
]);
```

### Cypress Auto-Retry

```typescript
// ✅ Cypress commands auto-retry
cy.getByTestId('submit').click();
cy.getByTestId('result').should('be.visible');
cy.getByTestId('count').should('have.text', '5');

// ✅ Intercept + wait for network
cy.intercept('GET', '/api/data').as('getData');
cy.getByTestId('load-button').click();
cy.wait('@getData');
```

### What NEVER to Do

```typescript
// ❌ NEVER use arbitrary sleep
await page.waitForTimeout(3000);  // Playwright
cy.wait(3000);                     // Cypress
await browser.pause(3000);         // WebDriverIO
time.sleep(3);                     // Python

// ❌ NEVER poll with setTimeout
while (!await element.isVisible()) {
  await new Promise(r => setTimeout(r, 100));
}
```

---

## Common UI Interaction Patterns

### Form Filling

```typescript
async function fillRegistrationForm(page: Page, data: RegistrationData): Promise<void> {
  await page.getByLabel('First Name').fill(data.firstName);
  await page.getByLabel('Last Name').fill(data.lastName);
  await page.getByLabel('Email').fill(data.email);
  await page.getByLabel('Password').fill(data.password);

  // Dropdown selection
  await page.getByLabel('Country').selectOption(data.country);

  // Checkbox
  if (data.acceptTerms) {
    await page.getByLabel('I accept the terms').check();
  }

  // Radio button
  await page.getByLabel(data.plan).check();
}
```

### File Upload

```typescript
test('should upload profile image', async ({ page }) => {
  const fileInput = page.getByTestId('file-upload');
  await fileInput.setInputFiles('path/to/test-image.png');
  await expect(page.getByTestId('upload-preview')).toBeVisible();
});
```

### Multi-Tab / New Window

```typescript
test('should open help in new tab', async ({ page, context }) => {
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.getByTestId('help-link').click(),
  ]);

  await newPage.waitForLoadState();
  expect(newPage.url()).toContain('/help');
});
```

### Iframe Interaction

```typescript
test('should interact with embedded widget', async ({ page }) => {
  const frame = page.frameLocator('[data-testid="payment-iframe"]');
  await frame.getByPlaceholder('Card number').fill('4242424242424242');
  await frame.getByPlaceholder('MM/YY').fill('12/28');
});
```

### Drag and Drop

```typescript
test('should reorder items via drag and drop', async ({ page }) => {
  const source = page.getByTestId('item-1');
  const target = page.getByTestId('item-3');
  await source.dragTo(target);
  await expect(page.getByTestId('item-list').nth(2)).toHaveText('Item 1');
});
```

---

## Visual Regression Testing

```typescript
// Playwright visual comparison
test('dashboard matches snapshot', async ({ page }) => {
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await expect(page).toHaveScreenshot('dashboard.png', {
    maxDiffPixelRatio: 0.01,
  });
});

// Component snapshot
test('button states match snapshot', async ({ page }) => {
  await expect(page.getByTestId('primary-button')).toHaveScreenshot('button-default.png');
  await page.getByTestId('primary-button').hover();
  await expect(page.getByTestId('primary-button')).toHaveScreenshot('button-hover.png');
});
```

---

## Accessibility Testing in E2E

```typescript
import AxeBuilder from '@axe-core/playwright';

test('login page has no accessibility violations', async ({ page }) => {
  await page.goto('/login');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});

// Targeted scan — specific rule set
test('form meets WCAG AA', async ({ page }) => {
  await page.goto('/registration');
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();
  expect(results.violations).toEqual([]);
});
```
