// Headless renders of cad/exports/SilentRackAC.glb -> renders/*.png
import { createRequire } from 'module';
import fs from 'fs'; import path from 'path'; import url from 'url'; import { execFileSync } from 'child_process';
const require = createRequire(import.meta.url);
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const here = path.dirname(url.fileURLToPath(import.meta.url));
const root = path.resolve(here, '..', '..');
const glb = fs.readFileSync(path.join(root, 'cad/exports/SilentRackAC.glb')).toString('base64');
const outDir = path.join(root, 'renders'); fs.mkdirSync(outDir, { recursive: true });

const doors = ['Door lower (AC bay)', 'Door lower MLV', 'Door upper (rack)', 'Door upper MLV', 'Handle upper door',
  'Handle lower door', 'Window pane outer', 'Window pane inner', 'Foam door lower', 'Foam door upper'];
const rightSide = ['Side panel right', 'Side panel right MLV', 'Foam side right lower', 'Foam side right mid',
  'Foam side right rack front', 'Foam side right rack middle', 'Foam side right rack rear', 'Skirt right'];
const top = ['Top panel', 'Top panel MLV', 'Foam top'];
const views = [
  { file: 'hero_front_left.png', dir: [-1.0, -1.25, 0.75], fov: 26, margin: 0.92 },
  { file: 'rear_right.png', dir: [1.0, 1.35, 0.65], fov: 26, margin: 0.92 },
  { file: 'cutaway_front_right.png', hide: [...doors, ...rightSide], dir: [1.25, -1.0, 0.7], fov: 26, margin: 0.92 },
  { file: 'section_airflow.png', hide: [...doors, ...top], clipX: 330, flowsX: 322, dir: [1, 0.0, 0.12], fov: 24, margin: 0.98, w: 1100, h: 1500 },
  { file: 'ac_bay_detail.png', hide: [...doors, ...rightSide], dir: [1.1, -0.55, 0.35], target: [360, 470, 560], fov: 30, margin: 0.55 },
];
// three.js is fetched once with curl (trusts the system CA bundle) and served to the
// page through request interception, so the browser never needs network/TLS access.
const CDN = 'https://cdn.jsdelivr.net/npm/three@0.160.0/';
const VENDOR = ['build/three.module.js', 'examples/jsm/loaders/GLTFLoader.js',
  'examples/jsm/utils/BufferGeometryUtils.js', 'examples/jsm/environments/RoomEnvironment.js'];
for (const f of VENDOR) {
  const dst = path.join(here, 'vendor', f);
  if (!fs.existsSync(dst)) {
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    execFileSync('curl', ['-sSf', '-o', dst, CDN + f]);
  }
}
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1600, height: 1200 } });
page.on('console', m => { if (m.type() === 'error') console.log('page error:', m.text()); });
await page.route('**/*', route => {
  const u = route.request().url();
  const hdr = { 'Access-Control-Allow-Origin': '*' };
  if (u.startsWith(CDN)) return route.fulfill({ path: path.join(here, 'vendor', u.slice(CDN.length)), contentType: 'application/javascript', headers: hdr });
  if (u === 'https://sra.local/render.html') return route.fulfill({ path: path.join(here, 'render.html'), contentType: 'text/html', headers: hdr });
  return route.abort();
});
await page.goto('https://sra.local/render.html');
await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
const n = await page.evaluate(b => window.loadModel(b), glb);
console.log('nodes', n);
for (const v of views) {
  const missing = await page.evaluate(o => window.renderView(o), v);
  await page.setViewportSize({ width: v.w || 1600, height: v.h || 1200 });
  await page.evaluate(o => window.renderView(o), v);
  await page.screenshot({ path: path.join(outDir, v.file) });
  console.log('wrote', v.file, missing.length ? 'MISSING: ' + missing.join(', ') : '');
}
await browser.close();
