// svg2pdf.mjs <out.pdf> <sheet1.svg> [sheet2.svg ...] - A3 landscape multi-page PDF with headless Chromium
import { createRequire } from 'module'; import fs from 'fs';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const [out, ...ins] = process.argv.slice(2);
const pages = ins.map(f => `<div class="pg">${fs.readFileSync(f, 'utf8').replace(/^<\?xml[^>]*>/, '')}</div>`).join('\n');
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
@page { size: 420mm 297mm; margin: 0 }
html, body { margin: 0; padding: 0 }
.pg { width: 420mm; height: 297mm; overflow: hidden; break-after: page }
.pg:last-child { break-after: auto }
.pg svg { display: block }
</style></head><body>${pages}</body></html>`;
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const page = await browser.newPage();
await page.setContent(html, { waitUntil: 'load' });
await page.pdf({ path: out, width: '420mm', height: '297mm', printBackground: true,
  margin: { top: 0, right: 0, bottom: 0, left: 0 } });
await browser.close();
console.log('wrote', out, ins.length, 'page(s)');
