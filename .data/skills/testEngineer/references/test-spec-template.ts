/**
 * Test Spec Template — YOUR_PROJECT
 *
 * Copy this file and rename to match the feature:
 *   feature-name.spec.ts → e.g., login.spec.ts, checkout.spec.ts
 *
 * Rules:
 *   - One describe block per feature/page
 *   - One logical assertion per test
 *   - Use page objects — no direct selectors in specs
 *   - Use fixtures/factories for test data
 *   - Clean up created data in afterAll/afterEach
 */

import { test, expect } from '@playwright/test';
// Import page objects
import { YourPageName } from '../pages/YourPageName';
// Import fixtures
// import { createTestData } from '../fixtures/your-data';

test.describe('Feature Name', () => {
  let yourPage: YourPageName;

  test.beforeEach(async ({ page }) => {
    yourPage = new YourPageName(page);
    await yourPage.navigate();
  });

  // --- Happy Path ---

  test('should display page heading', async () => {
    const heading = await yourPage.getHeadingText();
    expect(heading).toBe('Expected Heading');
  });

  test('should complete primary action successfully', async () => {
    await yourPage.submitForm('valid input');

    // Assert on the outcome — not implementation details
    const error = await yourPage.isErrorVisible();
    expect(error).toBe(false);
  });

  // --- Validation / Error States ---

  test('should display error for empty input', async () => {
    await yourPage.submitForm('');

    const errorText = await yourPage.getErrorText();
    expect(errorText).toContain('required');
  });

  test('should display error for invalid input', async () => {
    await yourPage.submitForm('invalid-value');

    const errorText = await yourPage.getErrorText();
    expect(errorText).toBeTruthy();
  });

  // --- Edge Cases ---

  test('should handle special characters in input', async () => {
    await yourPage.submitForm('<script>alert("xss")</script>');

    // Verify the app handles it safely
    const error = await yourPage.isErrorVisible();
    expect(error).toBe(true);
  });

  // --- State / List ---

  test('should display correct number of list items', async () => {
    const count = await yourPage.getListItemCount();
    expect(count).toBeGreaterThan(0);
  });
});

// --- API Test Template ---
// Uncomment and adapt for API tests

// test.describe('API: Resource Name', () => {
//   let client: YourApiClient;
//   const createdIds: string[] = [];
//
//   test.beforeAll(async ({ request }) => {
//     client = new YourApiClient(request, process.env.BASE_URL!);
//   });
//
//   test.afterAll(async () => {
//     for (const id of createdIds) {
//       await client.delete(id);
//     }
//   });
//
//   test('should create resource', async () => {
//     const resource = await client.create({ name: 'Test' });
//     createdIds.push(resource.id);
//     expect(resource.name).toBe('Test');
//   });
//
//   test('should return 404 for non-existent resource', async () => {
//     const response = await client.getRaw('/api/resources/does-not-exist');
//     expect(response.status).toBe(404);
//   });
// });
