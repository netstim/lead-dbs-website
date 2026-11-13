// Opens every page of a build in Chromium, on a desktop (1440 px) and a phone (390 px), in the light and the
// dark theme, and fails on what only a browser shows:
//   - a script error, or an error logged to the console;
//   - a request to this site that fails or answers with an error (a missing image, script or font);
//   - a picture that does not load, or does not finish loading within 5 seconds of being scrolled to;
//   - anything drawn past the screen's left or right edge (the page clips what is wider, so it would not
//     scroll: the reader just never sees it), and text cut off inside its own box (a line that may not
//     wrap and is wider than its box);
//   - a request to another server (nothing loads from elsewhere until a visitor starts a video).
// With a third argument it saves a full-page screenshot of every page and view there, for review.
//
//     npm install --no-save playwright@1.48.2 && npx playwright install chromium
//     node .github/scripts/check-browser.mjs public https://www.lead-dbs.org/ [screenshots/]
//
// The pages are every index.html of the build that is not a redirect (old addresses), and the 404 page.
// The build is served from its folder on a local port; the second argument is its baseURL, which the
// sitemap's addresses must start with. CHROME_PATH runs an installed Chrome instead of Playwright's Chromium.
import { createServer } from 'node:http';
import { readFile, readdir, mkdir, writeFile, realpath } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { chromium } from 'playwright';

const [dir, baseURL, shots] = process.argv.slice(2);
if (!dir || !baseURL) { console.error('usage: check-browser.mjs <build folder> <baseURL> [screenshot folder]'); process.exit(2); }

// Things that are drawn past the screen's edge on purpose, each with a comment saying why. An element (or an
// ancestor of it) that matches is not reported. Markup can say the same with a data-overflow-ok attribute.
// Today's pages need nothing else: the renders that bleed off a page's side sit in boxes that clip them at
// the screen's edge.
const OVERFLOW_OK = [
  '[data-overflow-ok]',
];
// at least this many pages, or the folder is not the build (or the baseURL is not the build's)
const MIN_PAGES = 10;

const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.xml': 'application/xml',
  '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp', '.gif': 'image/gif',
  '.avif': 'image/avif', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.mp4': 'video/mp4', '.pdf': 'application/pdf', '.txt': 'text/plain' };
const root = await realpath(dir);
const basePath = new URL(baseURL).pathname;   // "/" for production, "/lead-dbs-website/" for the preview
const server = createServer(async (req, res) => {
  let path;
  try { path = decodeURIComponent(new URL(req.url, 'http://x').pathname); } catch { res.writeHead(400).end(); return; }   // %ZZ
  if (!path.startsWith(basePath)) { res.writeHead(404).end(); return; }
  path = normalize(path.slice(basePath.length - 1));
  if (path.endsWith('/')) path += 'index.html';
  try {
    // only files inside the build: a symlink that leads out of it is not served
    const file = await realpath(join(root, path));
    if (file !== root && !file.startsWith(root + sep)) { res.writeHead(403).end(); return; }
    const body = await readFile(file);
    res.writeHead(200, { 'content-type': types[extname(file)] || 'application/octet-stream' }).end(body);
  } catch {
    try { res.writeHead(404, { 'content-type': 'text/html' }).end(await readFile(join(root, '404.html'))); } catch { res.writeHead(404).end(); }
  }
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const origin = `http://127.0.0.1:${server.address().port}`;

const fail = (why) => { console.log(why); server.close(); process.exit(1); };
const sitemap = await readFile(join(root, 'sitemap.xml'), 'utf8').catch(() => '');
const locs = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
if (!locs.length || !locs.every((u) => u.startsWith(baseURL))) {
  fail(`${dir}/sitemap.xml has ${locs.length ? `addresses that do not start with ${baseURL}, e.g. ${locs.find((u) => !u.startsWith(baseURL))}` : 'no addresses'}: is ${baseURL} the baseURL this build was made with?`);
}
// every page of the build, not only those in the sitemap (search, the forum's note, noindex pages)
const pages = [];
for (const f of (await readdir(root, { recursive: true })).sort()) {
  if (f !== 'index.html' && !f.endsWith(`${sep}index.html`)) continue;
  if (/<meta[^>]+http-equiv=["']?refresh/i.test(await readFile(join(root, f), 'utf8'))) continue;   // a redirect
  pages.push(f.slice(0, -'index.html'.length).split(sep).join('/'));
}
if (pages.length < MIN_PAGES) fail(`${dir}: only ${pages.length} pages: is it the output folder of hugo?`);
const NOT_FOUND = 'no-such-page/';   // the 404 page
pages.push(NOT_FOUND);

const views = [
  { name: 'desktop', width: 1440, height: 900, mobile: false },
  { name: 'phone', width: 390, height: 844, mobile: true },
];
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const problems = [];
if (shots) await mkdir(shots, { recursive: true });

// What the reader cannot see, measured in the page (see the list at the top).
function measure(okSelectors) {
  const edge = document.documentElement.clientWidth;
  const ok = okSelectors.join(', ');
  const name = (el) => `${el.tagName.toLowerCase()}${el.id ? '#' + el.id : ''}${typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/)[0] : ''}`
    + (el.textContent.trim() ? ` "${el.textContent.trim().replace(/\s+/g, ' ').slice(0, 40)}"` : '');
  const shown = (el) => el.checkVisibility({ visibilityProperty: true, opacityProperty: false });
  const out = [], cut = [], reported = new Set();
  let hidden = null;   // the last visually hidden box (.sr-only: 1 px, clipped); what is inside it is not drawn
  for (const el of document.querySelectorAll('body *')) {
    if (hidden?.contains(el) || el.closest(ok) || !shown(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width <= 1 && r.height <= 1) { hidden = el; continue; }
    if (r.width < 1 || r.height < 1) continue;
    const past = Math.max(r.right - edge, -r.left);
    if (past > 1) {
      // inside a box that scrolls sideways, the reader can scroll to it; inside a box that clips, it is cut
      // at that box's edge, which is a problem only if that box is itself past the screen's edge (and then
      // the box is reported). The page itself (html, body) clips at the screen's edge: that does not count.
      let excused = false;
      for (let a = el.parentElement; a && a !== document.body && a !== document.documentElement; a = a.parentElement) {
        if (reported.has(a)) { excused = true; break; }
        const o = getComputedStyle(a).overflowX;
        if (o === 'auto' || o === 'scroll') { excused = true; break; }
        if (o === 'hidden' || o === 'clip') {
          const b = a.getBoundingClientRect();
          if (b.right <= edge + 1 && b.left >= -1) { excused = true; break; }
        }
      }
      if (!excused) { reported.add(el); out.push(`${name(el)} by ${Math.round(past)}px`); }
    }
    // a line that may not wrap and is wider than its own box: the rest of it is hidden or spills (SVG text
    // never wraps and has no box of its own to measure against). The text itself is measured too, since
    // scrollWidth also counts a decoration that pokes out (a button's arrow has a negative margin).
    const texts = el instanceof SVGElement ? [] : [...el.childNodes].filter((n) => n.nodeType === 3 && n.textContent.trim());
    if (texts.length) {
      const s = getComputedStyle(el);
      const nowrap = s.whiteSpace === 'nowrap' || s.whiteSpace === 'pre' || s.textWrapMode === 'nowrap';
      if (nowrap && s.display !== 'inline' && ['visible', 'hidden', 'clip'].includes(s.overflowX) && el.scrollWidth > el.clientWidth + 1) {
        const range = document.createRange();
        const right = Math.max(...texts.map((n) => { range.selectNodeContents(n); return range.getBoundingClientRect().right; }));
        const box = r.left + el.clientLeft + el.clientWidth;
        if (right > box + 1) cut.push(`${name(el)} (${Math.round(right - box)}px)`);
      }
    }
  }
  const style = [];
  const article = document.querySelector('.manual-prose');
  if (article) {
    const proseSize = getComputedStyle(article).fontSize;
    const intro = article.querySelector(':scope > p:first-child:not([class])');
    if (intro && getComputedStyle(intro).fontSize !== proseSize) style.push('global lead styles override the manual body size');
    for (const code of article.querySelectorAll('pre code')) {
      if (getComputedStyle(code).fontSize !== getComputedStyle(code.closest('pre')).fontSize) {
        style.push('nested code inherits the inline-code size reduction'); break;
      }
    }
    const search = document.querySelector('.docs-search');
    if (!search?.getAttribute('aria-label')) style.push('documentation search has no name when its visible label is hidden');
  }
  return { out, cut, style };
}

async function check(view, scheme) {
  const context = await browser.newContext({ viewport: { width: view.width, height: view.height }, isMobile: view.mobile, hasTouch: view.mobile,
    colorScheme: scheme, reducedMotion: 'reduce' });
  const page = await context.newPage();
  let current = '';
  const note = (what) => problems.push(`${current} (${view.name}, ${scheme}): ${what}`);
  page.on('pageerror', (e) => note(`script error: ${e.message.split('\n')[0]}`));
  page.on('console', (m) => { if (m.type() === 'error' && !/Failed to load resource/.test(m.text())) note(`console: ${m.text().slice(0, 200)}`); });
  page.on('requestfailed', (r) => { if (r.url().startsWith(origin)) note(`request failed: ${r.url().slice(origin.length)}`); });
  page.on('response', (r) => {
    if (!r.url().startsWith(origin) || r.status() < 400) return;
    // the 404 page's own document answers 404; anything it loads must not
    const own404 = current === '/' + NOT_FOUND && r.status() === 404 && r.request().isNavigationRequest() && r.frame() === page.mainFrame();
    if (!own404) note(`HTTP ${r.status()}: ${r.url().slice(origin.length)}`);
  });
  await page.route('**/*', (route) => {
    const u = route.request().url();
    if (u.startsWith(origin) || u.startsWith('data:') || u.startsWith('blob:')) return route.continue();
    note(`request to another server: ${u.slice(0, 120)}`);
    return route.abort();
  });
  for (const p of pages) {
    current = '/' + p;
    try {
      await page.goto(origin + basePath + p, { waitUntil: 'load', timeout: 30000 });
      // scroll through, so pictures that load near the screen load, and through every box that scrolls
      // sideways (a row of covers), as a reader would
      await page.evaluate(async () => {
        const pause = () => new Promise((r) => setTimeout(r, 60));
        for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight * 0.8) {
          scrollTo(0, y); await pause();
          for (const box of document.querySelectorAll('body *')) {
            const o = getComputedStyle(box).overflowX;
            const r = box.getBoundingClientRect();
            if ((o !== 'auto' && o !== 'scroll') || box.scrollWidth <= box.clientWidth + 1 || r.bottom < 0 || r.top > innerHeight) continue;
            for (let x = 0; x < box.scrollWidth; x += box.clientWidth * 0.8) { box.scrollLeft = x; await pause(); }
            box.scrollLeft = 0;
          }
        }
        scrollTo(0, 0);
      });
      // then give the pictures that were scrolled to 5 seconds to finish (a picture that is not drawn, in a
      // closed menu or hidden at this width, is never fetched and is not waited for)
      const waiting = () => [...document.querySelectorAll('img[loading]')].filter((i) => !i.complete && i.checkVisibility()).map((i) => (i.currentSrc || i.src).replace(location.origin, ''));
      await page.waitForFunction(() => ![...document.querySelectorAll('img[loading]')].some((i) => !i.complete && i.checkVisibility()),
        null, { timeout: 5000, polling: 100 }).catch(() => {});   // what is still loading then is reported below
      const r = await page.evaluate(measure, OVERFLOW_OK);
      const slow = await page.evaluate(waiting);
      const broken = await page.evaluate(() => [...document.images].filter((i) => i.complete && i.currentSrc && i.naturalWidth === 0).map((i) => i.currentSrc.replace(location.origin, '')));
      for (const o of r.out) note(`past the screen's edge: ${o}`);
      for (const c of r.cut) note(`text cut off in its box: ${c}`);
      for (const issue of r.style) note(`manual style regression: ${issue}`);
      for (const b of broken) note(`picture does not load: ${b}`);
      for (const s of slow) note(`picture did not finish loading: ${s}`);
      if (shots) {
        const file = `${(p.replace(/\/$/, '').replace(/\//g, '_') || 'home')}--${view.name}-${scheme}.png`;
        await writeFile(join(shots, file), await page.screenshot({ fullPage: true }));
      }
    } catch (e) {
      note(`did not open: ${e.message.split('\n')[0]}`);
    }
  }
  await context.close();
}

// Check the manual's stateful controls once, after the parallel page sweep so clipboard
// operations cannot race between contexts. This runs in both PR and pre-deploy CI.
async function checkManualInteractions() {
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 }, permissions: ['clipboard-read', 'clipboard-write'] });
  const page = await context.newPage();
  const manual = origin + basePath + 'manual/';
  const require = (ok, message) => { if (!ok) throw new Error(message); };
  try {
    await page.goto(manual);
    const next = await page.locator('.manual-pagination__next').getAttribute('href');
    require(next && new URL(next, manual).href !== manual, 'Introduction next link points to itself');
    await page.goto(manual + 'appendix/useful-command-line-tools/installing-an-atlas-from-a-repository/');
    const example = page.locator('.manual-code[data-code-lines]').first();
    const expand = example.getByRole('button', { name: /^Show all/ });
    await expand.click();
    require(await example.locator('.manual-code__expand').first().getAttribute('aria-expanded') === 'true', 'Long code did not expand');
    const source = (await example.locator('.manual-code__source').textContent()).trim();
    await example.getByRole('button', { name: 'Wrap code lines', exact: true }).click();
    require(await example.locator('pre').evaluate((e) => e.scrollWidth <= e.clientWidth + 1), 'Wrapped code still overflows horizontally');
    require(source.split('\n').length > 20, 'The test needs a complete long example');
    await example.getByRole('button', { name: 'Copy full code', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.manual-code[data-code-lines] .manual-code__foot [data-copy-label]')?.textContent === 'Copied');
    require(await page.evaluate(() => navigator.clipboard.readText()) === source, 'Clipboard omitted part of the example');
    const copiedIcon = example.locator('.manual-code__foot [data-icon="check"]');
    require(await copiedIcon.isVisible(), 'Code copy succeeded without visible confirmation');
    await example.getByRole('button', { name: 'Collapse', exact: true }).click();
    require(await example.locator('.manual-code__expand').first().getAttribute('aria-expanded') === 'false', 'Long code did not collapse');

    await page.setViewportSize({ width: 390, height: 844 });
    await page.evaluate(() => scrollTo(0, 0));
    const before = await page.locator('h1').boundingBox();
    const chapters = page.getByRole('button', { name: 'Chapters', exact: true });
    await chapters.click();
    await page.locator('#manual-drawer[open]').waitFor();
    require(await page.evaluate(() => getComputedStyle(document.documentElement).overflowY === 'hidden'), 'The chapter drawer does not lock background scrolling');
    const after = await page.locator('h1').boundingBox();
    require(before.y === after.y, 'Mobile chapters shifted the article');
    await page.keyboard.press('Tab');
    require(await page.evaluate(() => document.querySelector('#manual-drawer').contains(document.activeElement)), 'Focus escaped the modal drawer');
    await page.keyboard.press('Escape');
    require(await page.locator('#manual-drawer').getAttribute('open') === null, 'Escape did not close the drawer');
    require(await chapters.evaluate((e) => e === document.activeElement), 'Drawer did not return focus to its trigger');
    await page.locator('#combine-the-four-scales').scrollIntoViewIfNeeded();
    const toolbar = await page.locator('.manual-mobile-bar').boundingBox();
    require(toolbar.y >= 0 && toolbar.y < 120, 'Mobile navigation disappeared during deep reading');
    await page.getByRole('button', { name: 'On this page', exact: true }).click();
    await page.locator('#manual-contents[open]').waitFor();
    await page.locator('#manual-contents a[href="#save-and-view-the-result"]').click();
    require(await page.locator('#manual-contents').getAttribute('open') === null, 'Section navigation stayed open after choosing a heading');
    const target = await page.locator('#save-and-view-the-result').boundingBox();
    require(target.y >= toolbar.y + toolbar.height, 'Section heading is hidden beneath sticky navigation');
    await page.getByRole('link', { name: 'Search documentation', exact: true }).click();
    await page.locator('#site-search[open]').waitFor();
    await page.locator('#site-search .search__input').fill('coregistration');
    await page.locator('#site-search .search__hit').first().waitFor();
    require(!(await page.locator('#site-search .search__results').innerText()).includes('#:'), 'Search snippets contain heading-anchor punctuation');
    await page.locator('#site-search .search__input').fill('BRAINSFit');
    await page.waitForFunction(() => /^\d+ results?$/.test(document.querySelector('#site-search .search__status')?.textContent || ''));
    const resultCount = parseInt(await page.locator('#site-search .search__status').innerText(), 10);
    require(await page.locator('#site-search .search__results > li').count() === resultCount, 'Search count includes an uncounted browse link');
    await page.keyboard.press('Escape');
    await page.setViewportSize({ width: 320, height: 568 });
    await page.goto(manual + 'appendix/useful-command-line-tools/installing-an-atlas-from-a-repository/');
    const narrowCopy = page.locator('.manual-code__head').first().getByRole('button', { name: 'Copy code', exact: true });
    await narrowCopy.click();
    await page.waitForFunction(() => document.querySelector('.manual-code__head [data-copy]')?.dataset.copyState === 'copied');
    require(await narrowCopy.locator('[data-icon="check"]').isVisible(), 'Icon-only copy has no visible success state');
    await page.goto(manual);
    require(await page.locator('.manual-terminal pre').evaluate((e) => e.scrollWidth <= e.clientWidth + 1), 'Starter terminal overflows at 320px');
    await page.getByRole('tab', { name: 'Lead Group', exact: true }).click();
    require(await page.locator('.manual-launch__command').textContent() === 'lead group', 'Group tab shows the wrong command');
    await page.getByRole('button', { name: 'Copy MATLAB command', exact: true }).click();
    await page.waitForFunction(() => document.querySelector('.manual-terminal [data-copy-text]')?.dataset.copyState === 'copied');
    require(await page.evaluate(() => navigator.clipboard.readText()) === 'lead group', 'Group tab copies a different command');
    await page.getByRole('tab', { name: 'Lead Group', exact: true }).focus();
    await page.keyboard.press('ArrowLeft');
    require(await page.getByRole('tab', { name: 'Lead-DBS', exact: true }).getAttribute('aria-selected') === 'true', 'Keyboard cannot switch the command tab');
    require(await page.locator('.manual-launch__command').textContent() === 'lead dbs', 'Keyboard tab selection did not update the command');
  } catch (e) {
    problems.push(`manual interactions: ${e.message.split('\n')[0]}`);
  } finally {
    await context.close();
  }
}

// Headless Chromium normally hides scrollbars, masking the horizontal jump between
// a long article and a short one. Exercise real scrollbar space as well as wide rails.
async function checkManualLayout() {
  const visibleScrollbars = await chromium.launch({
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {}),
    ignoreDefaultArgs: ['--hide-scrollbars'],
  });
  const context = await visibleScrollbars.newContext();
  await context.addInitScript(() => {
    const addScrollbar = () => {
      const style = document.createElement('style');
      // Force a measurable scrollbar even on machines that prefer overlay scrollbars.
      style.textContent = 'html::-webkit-scrollbar { width: 16px; }';
      document.head.append(style);
    };
    if (document.head) addScrollbar();
    else document.addEventListener('DOMContentLoaded', addScrollbar, { once: true });
  });
  const page = await context.newPage();
  const manual = origin + basePath + 'manual/';
  const require = (ok, message) => { if (!ok) throw new Error(message); };
  const ready = () => page.evaluate(() => document.fonts.ready.then(() => null));
  const geometry = () => page.evaluate(() => {
    const rect = (selector) => {
      const box = document.querySelector(selector).getBoundingClientRect();
      return { x: box.x, y: box.y, width: box.width, right: box.right };
    };
    return {
      gutter: innerWidth - document.documentElement.clientWidth,
      viewport: document.documentElement.clientWidth,
      brand: rect('.docs-brand > a'), links: rect('.docs-links'),
      download: rect('.docs-download'), rail: rect('.manual-nav'), article: rect('.manual-body'), bar: rect('.docs-header__bar'),
    };
  });
  try {
    for (const width of [1280, 1440, 1920, 3000]) {
      await page.setViewportSize({ width, height: 1308 });
      let baseline;
      for (const chapter of ['installation/', 'ways-to-contribute-to-lead-dbs/', 'lead-dbs/step2-image-import/']) {
        await page.goto(manual + chapter);
        await ready();
        const box = await geometry();
        require(box.gutter >= 12, `Scrollbar space is not reserved on ${chapter} at ${width}px`);
        require(Math.abs(box.rail.x - 24) <= 1, `Chapter rail drifts away from the viewport edge at ${width}px`);
        require(Math.abs(box.brand.x - 24) <= 1, `Docs brand drifts away from the viewport edge at ${width}px`);
        // measured against the header bar itself: a fixed header's width next to a forced scrollbar differs between Chrome builds
        require(Math.abs(box.download.right - (box.bar.right - 24)) <= 1, `Header actions are inset at ${width}px`);
        require(box.article.width <= 737 && box.article.x >= box.rail.right + 47, `Article overlaps navigation or exceeds its reading width at ${width}px`);
        if (baseline) {
          for (const part of ['brand', 'links', 'download', 'rail', 'article']) {
            for (const dimension of ['x', 'y', 'width']) {
              require(Math.abs(box[part][dimension] - baseline[part][dimension]) <= 1,
                `${part} ${dimension} jumps between long and short pages at ${width}px`);
            }
          }
        } else baseline = box;
      }
    }
    await page.goto(manual + 'installation/');
    await ready();
    const before = await page.evaluate(() => {
      const rail = document.querySelector('.manual-nav');
      rail.scrollTop = 40;
      return { scroll: rail.scrollTop, linkY: rail.querySelector('a[href$="/ways-to-contribute-to-lead-dbs/"]').getBoundingClientRect().y };
    });
    require(before.scroll > 0, 'The navigation stability check needs a scrolled rail');
    await Promise.all([
      page.waitForURL(manual + 'ways-to-contribute-to-lead-dbs/'),
      page.locator('.manual-nav a[href$="/ways-to-contribute-to-lead-dbs/"]').click(),
    ]);
    await ready();
    const after = await page.evaluate(() => ({
      scroll: document.querySelector('.manual-nav').scrollTop,
      linkY: document.querySelector('.manual-nav a[aria-current="page"]').getBoundingClientRect().y,
    }));
    require(Math.abs(after.scroll - before.scroll) <= 1 && Math.abs(after.linkY - before.linkY) <= 1,
      'An already-visible chapter jumps when navigating to it');
  } catch (e) {
    problems.push(`manual layout: ${e.message.split('\n')[0]}`);
  } finally {
    await visibleScrollbars.close();
  }
}

// the four views run side by side, each in its own browser context
await Promise.all(views.flatMap((view) => ['light', 'dark'].map((scheme) => check(view, scheme))));
await checkManualInteractions();
await checkManualLayout();
await browser.close();
server.close();

for (const p of problems.sort()) console.log(p);
console.log(`${pages.length} pages in ${views.length * 2} views checked, ${problems.length} problems`);
process.exit(problems.length ? 1 : 0);
