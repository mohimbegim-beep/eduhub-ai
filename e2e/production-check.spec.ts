import { test, expect } from '@playwright/test';

/**
 * PRODUCTION SMOKE & INTEGRITY CHECKS FOR EDUMATE AI
 * 
 * Target: Production or staging URL specified in playwright.config.ts / BASE_URL
 * Safety guarantees:
 *  - 100% Read-Only: No automated form submits that consume LLM tokens or send external API calls.
 *  - Zero Junk Data: Leaves database and state completely clean.
 *  - Isolated: Low concurrency (1 worker) ensures zero performance impact on real users.
 */

// Key sections and visual landmarks to verify
const CORE_SECTIONS = [
  {
    id: 'hero',
    name: 'Main Landing Page (Hero)',
    path: '/',
    expectedText: 'Autonomous AI Academic Copilot',
  },
  {
    id: 'ielts-widget',
    name: 'IELTS Diagnostic Section',
    path: '/',
    expectedText: 'Instant 15-Second Essay Diagnostic',
  },
  {
    id: 'pricing-tiers',
    name: 'Pricing & Learning Tier Section',
    path: '/',
    expectedText: 'Choose Your Learning Tier',
  },
  {
    id: 'faq',
    name: 'Frequently Asked Questions Section',
    path: '/',
    expectedText: 'Frequently Asked Questions',
  },
];

test.describe('EduMate AI Production Health & Landmark Verification', () => {

  test.beforeEach(async ({ context }) => {
    // Ensure canonical baseline English locale before scripts run
    await context.addInitScript(() => {
      try {
        localStorage.setItem('eduhub_locale', 'en');
      } catch (e) {}
    });
  });

  // 1. Data-driven loop validating HTTP status codes (no 404/500) and essential landmark text
  for (const section of CORE_SECTIONS) {
    test(`Section check: ${section.name} responds with <400 and renders "${section.expectedText}"`, async ({ page }) => {
      const response = await page.goto(section.path, { waitUntil: 'domcontentloaded' });

      // Verify HTTP response status
      expect(response, `Failed to receive HTTP response for ${section.path}`).not.toBeNull();
      const status = response!.status();
      expect(status, `HTTP error ${status} on ${section.path}`).toBeGreaterThanOrEqual(200);
      expect(status, `HTTP error ${status} on ${section.path}`).toBeLessThan(400);

      // Verify landmark text is attached to DOM
      const matches = page.getByText(section.expectedText, { exact: false });
      await expect(matches.first(), `Text "${section.expectedText}" not found in DOM`).toBeAttached();

      const count = await matches.count();
      let hasVisibleMatch = false;
      for (let i = 0; i < count; i++) {
        if (await matches.nth(i).isVisible()) {
          hasVisibleMatch = true;
          break;
        }
      }
      expect(hasVisibleMatch, `Expected visible landmark with text "${section.expectedText}"`).toBeTruthy();
    });
  }

  // 2. Direct tool route checks (shallow HTTP & container verification without token usage)
  const DEDICATED_TOOL_PAGES = [
    { name: 'IELTS Essay Grader Tool', path: '/tools/essay-grader' },
    { name: 'STEM Homework Solver Tool', path: '/tools/homework-solver' },
    { name: 'Citation Generator Tool', path: '/tools/citation-generator' },
    { name: 'AI Report 2026', path: '/report' },
  ];

  for (const tool of DEDICATED_TOOL_PAGES) {
    test(`Direct route health: ${tool.name} (${tool.path}) responds with <400`, async ({ page }) => {
      const response = await page.goto(tool.path, { waitUntil: 'domcontentloaded' });
      expect(response).not.toBeNull();
      expect(response!.status()).toBeLessThan(400);
      await expect(page.locator('body')).not.toBeEmpty();
    });
  }

  // 3. Language switcher functionality test (English -> Uzbek)
  test('Language switcher: clicking "UZ" dynamically updates interface ("Vositalar")', async ({ page }) => {
    const response = await page.goto('/', { waitUntil: 'domcontentloaded' });
    expect(response).not.toBeNull();
    expect(response!.status()).toBeLessThan(400);

    // Locate and click the UZ language switcher button in the navbar
    const uzButton = page.locator('button[data-lang-btn="uz"]').first();
    await expect(uzButton).toBeVisible();
    await uzButton.click();

    // Verify characteristic Uzbek translation appears in UI navbar
    const uzbekElement = page.getByText('Vositalar', { exact: false }).first();
    await expect(uzbekElement).toBeVisible({ timeout: 10000 });
  });

});
