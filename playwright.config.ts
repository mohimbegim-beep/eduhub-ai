import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright E2E Configuration for EduHub AI
 * Non-intrusive, isolated production smoke & health checks
 */
export default defineConfig({
  testDir: './e2e',
  /* Maximum time one test can run for (30 seconds) */
  timeout: 30 * 1000,
  expect: {
    /* Timeout for each individual assertion */
    timeout: 10 * 1000,
  },
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code */
  forbidOnly: !!process.env.CI,
  /* Retry on CI if needed */
  retries: process.env.CI ? 1 : 0,
  /* Isolated execution: single worker avoids overloading production */
  workers: 1,
  /* Reporters: concise console list + static HTML report */
  reporter: [
    ['list'],
    ['html', { open: 'never', outputFolder: 'playwright-report' }]
  ],
  /* Shared settings for all the projects below */
  use: {
    /* Base URL to use in actions like `await page.goto('/')` */
    baseURL: process.env.BASE_URL || 'https://onrender.com',

    /* Collect screenshot ONLY when a test fails */
    screenshot: 'only-on-failure',

    /* Retain trace recording ONLY when a test fails */
    trace: 'retain-on-failure',

    /* Headless background mode to prevent UI interruptions */
    headless: true,

    /* Ensure consistent canonical locale for tests regardless of host OS timezone */
    locale: 'en-US',
    timezoneId: 'UTC',

    /* Bypass certificate mismatches if custom domain is in propagation */
    ignoreHTTPSErrors: true,
  },

  /* Configure Chromium browser */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
