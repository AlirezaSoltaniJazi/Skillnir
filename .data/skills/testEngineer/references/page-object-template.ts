/**
 * Page Object Template — YOUR_PROJECT
 *
 * Copy this file and rename to match the page:
 *   YourPageName.ts → e.g., LoginPage.ts, DashboardPage.ts
 *
 * Rules:
 *   - NO assertions in page objects — return values, let specs assert
 *   - Locators use data-testid first, accessibility roles second
 *   - Action methods return void or typed data
 *   - Extend BasePage for shared elements (nav, header, footer)
 */

import { Locator, Page } from '@playwright/test';

// If you have a BasePage, extend it instead of using Page directly:
// import { BasePage } from './BasePage';
// export class YourPageName extends BasePage {

export class YourPageName {
  // --- Locators (private, lazy via page methods) ---

  private readonly heading: Locator;
  private readonly primaryAction: Locator;
  private readonly inputField: Locator;
  private readonly errorMessage: Locator;
  private readonly listItems: Locator;

  constructor(private readonly page: Page) {
    this.heading = page.getByTestId('page-heading');
    this.primaryAction = page.getByTestId('primary-action');
    this.inputField = page.getByTestId('input-field');
    this.errorMessage = page.getByTestId('error-message');
    this.listItems = page.getByTestId('list-item');
  }

  // --- Navigation ---

  async navigate(): Promise<void> {
    await this.page.goto('/your-page-path');
  }

  // --- Actions (return void — let specs assert) ---

  async fillInput(value: string): Promise<void> {
    await this.inputField.fill(value);
  }

  async clickPrimaryAction(): Promise<void> {
    await this.primaryAction.click();
  }

  async submitForm(inputValue: string): Promise<void> {
    await this.fillInput(inputValue);
    await this.clickPrimaryAction();
  }

  // --- Queries (return data — let specs assert) ---

  async getHeadingText(): Promise<string> {
    return (await this.heading.textContent()) ?? '';
  }

  async getErrorText(): Promise<string> {
    return (await this.errorMessage.textContent()) ?? '';
  }

  async getListItemCount(): Promise<number> {
    return this.listItems.count();
  }

  async getListItemTexts(): Promise<string[]> {
    return this.listItems.allTextContents();
  }

  // --- State Checks (return booleans) ---

  async isErrorVisible(): Promise<boolean> {
    return this.errorMessage.isVisible();
  }

  async isPrimaryActionEnabled(): Promise<boolean> {
    return this.primaryAction.isEnabled();
  }
}
