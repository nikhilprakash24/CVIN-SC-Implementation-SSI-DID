// Render every SVG in sheets/ to sheets/png/*.png with the pre-installed Chromium.
// Usage: node render_png.js [sheet-number-prefix]
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = path.join(__dirname, 'sheets');
  const out = path.join(dir, 'png');
  fs.mkdirSync(out, { recursive: true });
  const filt = process.argv[2] || '';
  const files = fs.readdirSync(dir).filter(f => f.endsWith('.svg') && f.startsWith(filt)).sort();
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM_PATH || undefined });
  const page = await browser.newPage({ viewport: { width: 1600, height: 1000 }, deviceScaleFactor: 1.25 });
  for (const f of files) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8');
    await page.setContent(`<html><body style="margin:0;background:#0b2a5b">${svg}</body></html>`);
    await page.screenshot({ path: path.join(out, f.replace(/\.svg$/, '.png')), clip: { x: 0, y: 0, width: 1600, height: 1000 } });
    console.log('rendered', f);
  }
  await browser.close();
})();
