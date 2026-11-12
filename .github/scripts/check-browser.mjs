// Opens every page of a build in Chromium, on a desktop (1440 px) and a phone (390 px), in the light and the
// dark theme, and fails on what only a browser shows:
//   - a script error, or an error logged to the console;
//   - a request to this site that fails (a missing image, script or font);
//   - a picture that does not load;
//   - a page that scrolls sideways, or text cut off at the screen's edge (the page clips what is wider);
//   - a request to another server (nothing loads from elsewhere until a visitor starts a video).
// With a third argument it saves a full-page screenshot of every page and view there, for review.
//
//     npm install --no-save playwright@1.48.2 && npx playwright install chromium
//     node .github/scripts/check-browser.mjs public https://www.lead-dbs.org/ [screenshots/]
//
// The build is served from its folder on a local port; the second argument is its baseURL, which the
// sitemap's addresses start with. CHROME_PATH runs an installed Chrome instead of Playwright's Chromium.
import { createServer } from 'node:http';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { chromium } from 'playwright';

const [dir, baseURL, shots] = process.argv.slice(2);
if (!dir || !baseURL) { console.error('usage: check-browser.mjs <build folder> <baseURL> [screenshot folder]'); process.exit(2); }

const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.xml': 'application/xml',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.mp4': 'video/mp4', '.pdf': 'application/pdf', '.txt': 'text/plain' };
const basePath = new URL(baseURL).pathname;   // "/" for production, "/lead-dbs-website/" for the preview
const server = createServer(async (req, res) => {
  let path = decodeURIComponent(new URL(req.url, 'http://x').pathname);
  if (!path.startsWith(basePath)) { res.writeHead(404).end(); return; }
  path = normalize(path.slice(basePath.length - 1));
  if (path.endsWith('/')) path += 'index.html';
  try {
    const body = await readFile(join(dir, path));
    res.writeHead(200, { 'content-type': types[extname(path)] || 'application/octet-stream' }).end(body);
  } catch {
    try { res.writeHead(404, { 'content-type': 'text/html' }).end(await readFile(join(dir, '404.html'))); } catch { res.writeHead(404).end(); }
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const origin = `http://127.0.0.1:${server.address().port}`;
const local = (u) => origin + basePath + u.slice(baseURL.length);

const sitemap = await readFile(join(dir, 'sitemap.xml'), 'utf8');
const pages = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]).filter((u) => u.startsWith(baseURL) && !u.endsWith('.xml'));
pages.push(baseURL + 'no-such-page/');   // the 404 page

const views = [
  { name: 'desktop', width: 1440, height: 900, mobile: false },
  { name: 'phone', width: 390, height: 844, mobile: true },
];
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const problems = [];
if (shots) await mkdir(shots, { recursive: true });

for (const view of views) {
  for (const scheme of ['light', 'dark']) {
    const context = await browser.newContext({ viewport: { width: view.width, height: view.height }, isMobile: view.mobile, hasTouch: view.mobile,
      colorScheme: scheme, reducedMotion: 'reduce' });
    const page = await context.newPage();
    let current = '';
    const note = (what) => problems.push(`${current} (${view.name}, ${scheme}): ${what}`);
    page.on('pageerror', (e) => note(`script error: ${e.message.split('\n')[0]}`));
    page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) note(`console: ${m.text().slice(0, 200)}`); });
    page.on('requestfailed', (r) => { if (r.url().startsWith(origin)) note(`request failed: ${r.url().slice(origin.length)}`); });
    page.on('response', (r) => {
      if (r.url().startsWith(origin) && r.status() >= 400 && !current.includes('no-such-page')) note(`HTTP ${r.status()}: ${r.url().slice(origin.length)}`);
    });
    await page.route('**/*', (route) => {
      const u = route.request().url();
      if (u.startsWith(origin) || u.startsWith('data:') || u.startsWith('blob:')) return route.continue();
      note(`request to another server: ${u.slice(0, 120)}`);
      return route.abort();
    });
    for (const url of pages) {
      current = url.slice(baseURL.length - 1) || '/';
      try {
        await page.goto(local(url), { waitUntil: 'load', timeout: 30000 });
        // scroll through, so pictures that load near the screen load
        await page.evaluate(async () => {
          for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) { scrollTo(0, y); await new Promise((r) => setTimeout(r, 60)); }
          scrollTo(0, 0);
        });
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        const r = await page.evaluate(() => ({
          wide: document.documentElement.scrollWidth - innerWidth,
          // text past the right edge that no scroll container holds: the page clips it, so it is cut off
          cut: [...document.querySelectorAll('body *')].filter((el) => {
            if (!el.checkVisibility?.() || ![...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim())) return false;
            const r = el.getBoundingClientRect();
            if (r.width === 0 || r.right <= innerWidth + 1) return false;
            for (let a = el.parentElement; a; a = a.parentElement) {
              const o = getComputedStyle(a).overflowX;
              if (o === 'auto' || o === 'scroll' || o === 'hidden') return false;
            }
            return true;
          }).slice(0, 3).map((el) => `${el.tagName.toLowerCase()}${el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : ''} "${el.textContent.trim().slice(0, 40)}"`),
          broken: [...document.images].filter((i) => i.complete && i.currentSrc && i.naturalWidth === 0).map((i) => i.currentSrc.replace(location.origin, '')),
        }));
        if (r.wide > 0) note(`scrolls sideways by ${r.wide}px`);
        for (const c of r.cut) note(`text cut off at the right edge: ${c}`);
        for (const b of r.broken) note(`picture does not load: ${b}`);
        if (shots) {
          const file = `${(current.replace(/^\/|\/$/g, '').replace(/\//g, '_') || 'home')}--${view.name}-${scheme}.png`;
          await writeFile(join(shots, file), await page.screenshot({ fullPage: true }));
        }
      } catch (e) {
        note(`did not open: ${e.message.split('\n')[0]}`);
      }
    }
    await context.close();
  }
}
await browser.close();
server.close();

for (const p of problems) console.log(p);
console.log(`${pages.length} pages in ${views.length * 2} views checked, ${problems.length} problems`);
process.exit(problems.length ? 1 : 0);
