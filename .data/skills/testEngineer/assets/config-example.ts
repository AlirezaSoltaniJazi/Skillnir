/**
 * Test Framework Configuration Template — YOUR_PROJECT
 *
 * Adapt for your framework:
 *   - Playwright: playwright.config.ts
 *   - WebDriverIO: wdio.conf.ts
 *   - Cypress: cypress.config.ts
 *
 * This example shows Playwright config — the most common patterns apply across frameworks.
 */

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // --- Test Discovery ---
  testDir: './tests/e2e/specs',
  testMatch: '**/*.spec.ts',

  // --- Execution ---
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,           // Limit workers in CI
  retries: process.env.CI ? 2 : 0,                   // Retry only in CI
  timeout: 30_000,                                     // Per-test timeout
  expect: { timeout: 5_000 },                         // Assertion timeout

  // --- Reporting ---
  reporter: process.env.CI
    ? [
        ['html', { open: 'never', outputFolder: 'test-results/html' }],
        ['junit', { outputFile: 'test-results/junit.xml' }],
      ]
    : [['html', { open: 'on-failure' }]],

  // --- Artifacts ---
  outputDir: 'test-results/artifacts',
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'retain-on-failure',

    // --- Browser Settings ---
    headless: !!process.env.CI,
    viewport: { width: 1280, height: 720 },
    actionTimeout: 10_000,
    navigationTimeout: 15_000,
  },

  // --- Projects (browsers/devices) ---
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 12'] },
    },
  ],

  // --- Global Setup/Teardown ---
  globalSetup: require.resolve('./tests/support/global-setup'),
  globalTeardown: require.resolve('./tests/support/global-teardown'),

  // --- Dev Server (optional) ---
  // webServer: {
  //   command: 'npm run dev',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  //   timeout: 120_000,
  // },
});
