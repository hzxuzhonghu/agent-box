const { chromium } = require('playwright');


(async () => {
  const browser = await chromium.connectOverCDP('ws://localhost:9222');
  const page = await browser.newPage();
  await page.goto('https://www.google.com');
  console.log(page.url());
  await browser.close();
})();
