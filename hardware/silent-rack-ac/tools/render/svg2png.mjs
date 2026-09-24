// svg2png.mjs <in.svg> <out.png> [pxWidth] - rasterise an A3 drawing with headless Chromium
import { createRequire } from 'module'; import fs from 'fs'; import path from 'path';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [inp, out, pw = '3508'] = process.argv.slice(2);
const w = parseInt(pw, 10), h = Math.round(w * 297 / 420);
const svg = fs.readFileSync(inp, 'utf8').replace('width="420mm" height="297mm"', `width="${w}" height="${h}"`);
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage({ viewport: { width: w, height: h } });
await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
await page.screenshot({ path: out, clip: { x: 0, y: 0, width: w, height: h } });
await browser.close();
console.log('wrote', out, w, 'x', h);
