// The pages' Content Security Policy, measured: every page of a build in Chromium with the policy that
// tools/deploy.py package puts in the .htaccess (server/apache/htaccess, inline-script hashes filled in), but
// ENFORCED rather than report-only, so that anything it would block shows up here first. On each page it also
// starts the first click-to-load video (the player's request is answered locally, nothing leaves this computer).
// Fails on any violation. Run before switching the header from Report-Only to enforced (docs/launch.md).
//
//     npm ci && npx playwright install chromium
//     hugo --gc --minify && node tests/test_csp_browser.mjs public
import { execFileSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile, readdir } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';

const [dir] = process.argv.slice(2);
if (!dir) { console.error('usage: test_csp_browser.mjs <build folder>'); process.exit(2); }
const root = fileURLToPath(new URL('..', import.meta.url));
const policy = execFileSync('python3', [join(root, 'tools/deploy.py'), 'csp', dir], { encoding: 'utf8' }).trim();

const TYPES = { '.html': 'text/html; charset=utf-8', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json',
  '.xml': 'application/xml', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.avif': 'image/avif', '.png': 'image/png',
  '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif', '.ico': 'image/x-icon', '.woff2': 'font/woff2',
  '.mp4': 'video/mp4', '.webm': 'video/webm', '.txt': 'text/plain', '.webmanifest': 'application/manifest+json' };

const server = createServer(async (req, res) => {
  let path = normalize(decodeURIComponent(new URL(req.url, 'http://x').pathname));
  if (path.endsWith(sep)) path = join(path, 'index.html');
  try {
    const body = await readFile(join(dir, path));
    const headers = { 'Content-Type': TYPES[extname(path)] || 'application/octet-stream' };
    if (path.endsWith('.html')) headers['Content-Security-Policy'] = policy;
    res.writeHead(200, headers).end(body);
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((ok) => server.listen(0, '127.0.0.1', ok));
const origin = `http://127.0.0.1:${server.address().port}`;

// every page of the build that is not a redirect to an old address
const pages = [];
for (const entry of await readdir(dir, { recursive: true })) {
  if (!entry.endsWith('index.html') && entry !== '404.html') continue;
  const html = await readFile(join(dir, entry), 'utf8');
  if (/http-equiv=["']?refresh/i.test(html)) continue;
  pages.push('/' + entry.replace(/index\.html$/, '').split(sep).join('/'));
}
if (pages.length < 50) { console.error(`only ${pages.length} pages in ${dir}: is it the build?`); process.exit(2); }

const browser = await chromium.launch();
const context = await browser.newContext();
// a started video asks YouTube or Vimeo for its player: answered here, after the policy has allowed or blocked it
await context.route((url) => !url.href.startsWith(origin), (route) => route.fulfill({ status: 200, contentType: 'text/html', body: '' }));
await context.addInitScript(() => {
  window.__violations = [];
  document.addEventListener('securitypolicyviolation', (e) => {
    window.__violations.push(`${e.effectiveDirective} blocked ${e.blockedURI || 'inline'}${e.sourceFile ? ` (${e.sourceFile}:${e.lineNumber})` : ''}`);
  });
});

const problems = [];
let videos = 0;
const queue = [...pages];
await Promise.all(Array.from({ length: 4 }, async () => {
  const page = await context.newPage();
  const reported = [];
  page.on('console', (m) => { if (/Content Security Policy/i.test(m.text())) reported.push(m.text()); });
  for (let path = queue.shift(); path; path = queue.shift()) {
    reported.length = 0;
    await page.goto(origin + path, { waitUntil: 'load' });
    const start = page.locator('.video-embed__start').first();
    if (await start.count() && await start.isVisible()) {
      await start.click();
      await page.waitForSelector('iframe', { timeout: 5000 }).catch(() => problems.push(`${path}: the video did not start`));
      videos++;
    }
    await page.waitForTimeout(100);
    const seen = await page.evaluate(() => window.__violations);
    for (const v of new Set([...seen, ...reported])) problems.push(`${path}: ${v}`);
  }
  await page.close();
}));
await browser.close();
server.close();

if (problems.length) {
  console.error(`Content Security Policy violations (${problems.length}):\n  ` + problems.join('\n  '));
  process.exit(1);
}
console.log(`Content Security Policy: ${pages.length} pages and ${videos} started videos, no violations.`);
