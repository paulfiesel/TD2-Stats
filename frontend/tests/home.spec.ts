import { test, expect } from '@playwright/test';

test('should load the root path and return 200', async ({ page }) => {
  // Navigate to the root path
  const response = await page.goto('/');
  // Check that the response status is 200
  expect(response?.status()).toBe(200);
});