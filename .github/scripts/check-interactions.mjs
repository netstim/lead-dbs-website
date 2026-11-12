// Walks through the site's interactive parts in Chromium the way a visitor does, with the mouse and with the
// keyboard, and fails when one of them no longer works (check-browser.mjs only looks at the rendered pages):
//   - the phone menu: the menu button opens the sheet (aria-expanded, the focus on its first word), Escape
//     closes it and leaves the focus on the button, and the button closes it again;
//   - the search: "/" and the header's button open the dialog with the focus in its box, a query lists
//     results, Escape closes the dialog (the first Escape empties a box with text in it, as browsers do in
//     a search field) and gives the focus back to where it was;
//   - the atlas filter: a word narrows the catalogue and says how many match, a word nothing holds says so,
//     and an empty box shows every entry again;
//   - a dialog by keyboard: the download page's "Terms of use" opens with Enter and closes with Escape, the
//     focus back on its button.
// A script error on any of these pages fails the check too.
//
//     npm ci && npx playwright install chromium        (the versions locked in package-lock.json)
//     node .github/scripts/check-interactions.mjs public https://www.lead-dbs.org/
//
// The build is served from its folder on a local port; the second argument is its baseURL. CHROME_PATH runs
// an installed Chrome instead of Playwright's Chromium.
import { createServer } from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { chromium } from 'playwright';

const [dir, baseURL] = process.argv.slice(2);
if (!dir || !baseURL) { console.error('usage: check-interactions.mjs <build folder> <baseURL>'); process.exit(2); }

// the pages the journeys use
const ATLASES = 'helpsupport/knowledge-base/atlasesresources/atlases-2/';
const DOWNLOAD = 'download/';

const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.xml': 'application/xml',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.mp4': 'video/mp4', '.pdf': 'application/pdf', '.txt': 'text/plain' };
const root = await realpath(dir);
const basePath = new URL(baseURL).pathname;   // "/" for production, "/lead-dbs-website/" for the preview
const server = createServer(async (req, res) => {
  let path;
  try { path = decodeURIComponent(new URL(req.url, 'http://x').pathname); } catch { res.writeHead(400).end(); return; }
  if (!path.startsWith(basePath)) { res.writeHead(404).end(); return; }
  path = normalize(path.slice(basePath.length - 1));
  if (path.endsWith('/')) path += 'index.html';
  try {
    const file = await realpath(join(root, path));
    if (file !== root && !file.startsWith(root + sep)) { res.writeHead(403).end(); return; }
    res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' }).end(await readFile(file));
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const origin = `http://127.0.0.1:${server.address().port}`;
const url = (p) => origin + basePath + p;

const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const problems = [];
let passed = 0;

// One journey in a fresh page: `steps` gets the page and a function that records a failed expectation.
// Requests to other servers are refused (as in check-browser.mjs); script errors are failures.
async function journey(name, view, steps) {
  const context = await browser.newContext({ viewport: { width: view.width, height: view.height }, isMobile: view.mobile, hasTouch: view.mobile,
    reducedMotion: 'reduce' });
  const page = await context.newPage();
  const before = problems.length;
  const fail = (what) => problems.push(`${name}: ${what}`);
  page.on('pageerror', (e) => fail(`script error: ${e.message.split('\n')[0]}`));
  await page.route('**/*', (route) => (route.request().url().startsWith(origin) || route.request().url().startsWith('data:') ? route.continue() : route.abort()));
  try {
    await steps(page, fail);
  } catch (e) {
    fail(e.message.split('\n')[0]);
  }
  await context.close();
  if (problems.length === before) passed += 1;
  console.log(`${problems.length === before ? 'ok  ' : 'FAIL'} ${name}`);
}
// waits up to 3 s for a condition in the page; false if it never holds
const until = (page, fn, arg) => page.waitForFunction(fn, arg, { timeout: 3000, polling: 50 }).then(() => true, () => false);
// what has the focus, as a short description
const focused = (page) => page.evaluate(() => {
  const el = document.activeElement;
  return el && el !== document.body ? `${el.tagName.toLowerCase()}${el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : ''}` : 'nothing';
});

const desktop = { width: 1440, height: 900, mobile: false };
const phone = { width: 390, height: 844, mobile: true };

await journey('phone menu: the button opens the sheet, Escape and the button close it', phone, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const toggle = page.locator('.nav__toggle');
  if (!(await toggle.isVisible())) { fail('no menu button on a phone'); return; }
  await toggle.click();
  if (!(await until(page, () => document.querySelector('.nav').classList.contains('is-open')))) fail('the menu button does not open the sheet');
  if (await toggle.getAttribute('aria-expanded') !== 'true') fail('the open sheet\'s button does not say aria-expanded="true"');
  if (!(await page.evaluate(() => document.getElementById('site-menu').contains(document.activeElement)))) fail(`the focus is not in the sheet once it opens (it is on ${await focused(page)})`);
  if (!(await page.locator('#site-menu .nav__link').first().isVisible())) fail('the sheet\'s words are not visible');
  await page.keyboard.press('Escape');
  if (!(await until(page, () => !document.querySelector('.nav').classList.contains('is-open')))) fail('Escape does not close the sheet');
  if (!(await page.evaluate(() => document.activeElement === document.querySelector('.nav__toggle')))) fail(`after Escape the focus is not on the menu button (it is on ${await focused(page)})`);
  if (await toggle.getAttribute('aria-expanded') !== 'false') fail('the closed sheet\'s button does not say aria-expanded="false"');
  await toggle.click();
  try {
    await toggle.click({ timeout: 5000 });
  } catch {
    fail('the menu button cannot be pressed while the sheet is open (it is off the screen or covered)'); return;
  }
  if (!(await until(page, () => !document.querySelector('.nav').classList.contains('is-open')))) fail('the menu button does not close the sheet');
});

for (const how of ['the "/" key', 'the header\'s button']) {
  await journey(`search: ${how} opens it, a query finds pages, Escape closes it`, desktop, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    const dialog = page.locator('#site-search');
    const opener = page.locator('.nav [data-search-open]');
    if (how.includes('/')) {
      // from a link in the page, which must have the focus again afterwards
      await page.locator('.nav__bar .nav__logo').focus();
      await page.keyboard.press('/');
    } else {
      await opener.click();
    }
    if (!(await until(page, () => document.getElementById('site-search')?.open))) { fail('the search dialog does not open'); return; }
    if (!(await page.evaluate(() => document.activeElement?.matches('#site-search .search__input')))) fail(`the focus is not in the search box (it is on ${await focused(page)})`);
    await page.keyboard.type('atlas');
    if (!(await until(page, () => document.querySelectorAll('#site-search .search__results a.search__hit:not(.search__hit--manual)').length > 0))) {
      fail(`"atlas" lists no results (status: ${await dialog.locator('.search__status').textContent()})`);
    }
    // the box is a search field: in Chromium the first Escape empties it (the browser's own behaviour),
    // and the next one closes the dialog
    await page.keyboard.press('Escape');
    if (await page.evaluate(() => document.getElementById('site-search').open)) {
      if (await dialog.locator('.search__input').inputValue() !== '') fail('the first Escape neither closes the dialog nor empties the box');
      await page.keyboard.press('Escape');
    }
    if (!(await until(page, () => !document.getElementById('site-search').open))) { fail('Escape does not close the search dialog'); return; }
    const back = how.includes('/') ? '.nav__bar .nav__logo' : '.nav [data-search-open]';
    if (!(await page.evaluate((s) => document.activeElement === document.querySelector(s), back))) fail(`after Escape the focus is not back on ${back} (it is on ${await focused(page)})`);
  });
}

await journey('atlas filter: a word narrows the catalogue, an empty box shows it all', desktop, async (page, fail) => {
  await page.goto(url(ATLASES), { waitUntil: 'load' });
  const input = page.locator('[data-atlas-filter]');
  if (!(await input.isVisible())) { fail(`no visible filter on /${ATLASES}`); return; }
  const shown = () => page.evaluate(() => [...document.querySelectorAll('[data-atlas-entry]')].filter((e) => !e.hidden).length);
  const all = await shown();
  await input.fill('thalamus');
  const some = await shown();
  if (!(some > 0 && some < all)) fail(`"thalamus" leaves ${some} of ${all} entries`);
  const count = (await page.locator('[data-atlas-count]').textContent()).trim();
  if (count !== `${some} of ${all} match`) fail(`the count says "${count}", not "${some} of ${all} match"`);
  if (!(await page.locator('[data-atlas-none]').isHidden())) fail('"nothing matches" shows while entries match');
  await input.fill('qqqzzz');
  if (await shown() !== 0) fail('a word no entry holds leaves entries shown');
  if (!(await page.locator('[data-atlas-none]').isVisible())) fail('"nothing matches" does not show when nothing matches');
  await input.fill('');
  if (await shown() !== all) fail(`an empty box shows ${await shown()} of ${all} entries`);
});

await journey('dialog by keyboard: "Terms of use" opens with Enter, closes with Escape', desktop, async (page, fail) => {
  await page.goto(url(DOWNLOAD), { waitUntil: 'load' });
  const button = page.locator('[data-terms-open]');
  if (!(await button.isVisible())) { fail(`no "Terms of use" button on /${DOWNLOAD}`); return; }
  await button.focus();
  await page.keyboard.press('Enter');
  if (!(await until(page, () => document.getElementById('terms')?.open))) { fail('Enter on the button does not open the terms'); return; }
  if (!(await page.evaluate(() => document.getElementById('terms').contains(document.activeElement)))) fail(`the focus is not in the open dialog (it is on ${await focused(page)})`);
  await page.keyboard.press('Escape');
  if (!(await until(page, () => !document.getElementById('terms').open))) { fail('Escape does not close the terms'); return; }
  if (!(await page.evaluate(() => document.activeElement?.matches('[data-terms-open]')))) fail(`after Escape the focus is not back on the button (it is on ${await focused(page)})`);
});

await browser.close();
server.close();
for (const p of problems) console.log(p);
console.log(`${passed} journeys passed, ${problems.length} problems`);
process.exit(problems.length ? 1 : 0);
