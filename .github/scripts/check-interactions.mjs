// Walks through the site's interactive parts the way a visitor does, with the mouse, the keyboard and a
// finger, and fails when one of them no longer works (check-browser.mjs only looks at the rendered pages).
// In Chromium, with reduced motion unless a journey says otherwise:
//   - the phone menu: the menu button opens the sheet (aria-expanded, the focus on its first word), Escape
//     closes it and leaves the focus on the button, and the button closes it again;
//   - the menu sheet by keyboard (820 and 390 px): Tab runs through the words, GitHub, Search, the theme
//     button, Download and the menu button, then back to the first word; Shift+Tab runs the same way back;
//   - the search: "/" and the header's button open the dialog with the focus in its box, a query lists
//     results, Escape closes the dialog (the first Escape empties a box with text in it, as browsers do in
//     a search field) and gives the focus back to where it was;
//   - a dialog holds the page: with the search or the gallery's lightbox open the wheel does not scroll the
//     page behind it, and closing it leaves the page where it was;
//   - the atlas filter: a word narrows the catalogue and says how many match, a word nothing holds says so,
//     and an empty box shows every entry again;
//   - a dialog by keyboard: the download page's "Terms of use" opens with Enter and closes with Escape, the
//     focus back on its button;
//   - the home page with motion (prefers-reduced-motion: no-preference): the hero's lead and actions are
//     fully visible at once (no fade that makes the main button look disabled), the video's button pauses
//     it (or, where the video cannot play, no button shows and the poster stays), the quotes' pause button
//     is not covered by "All quotes" and pauses them, the figure grid has a pause button that stops it;
//   - a malformed address fragment (/manual/#%, a broken UTF-8 escape) breaks no script: the manual's
//     Chapters button still opens the chapters;
//   - without script: the phone menu opens as a target (#site-menu), the manual's chapters are on the page,
//     and the videos are plain links to their sites.
// Then a short smoke run in WebKit (Safari's engine): the phone menu, the manual's chapters and the search.
// It is skipped, with a note, when Playwright's WebKit is not installed (npx playwright install webkit).
// A script error on any of these pages fails the check too. Text geometry is measured after the fonts are in.
//
//     npm ci && npx playwright install chromium webkit   (the versions locked in package-lock.json)
//     node .github/scripts/check-interactions.mjs public https://www.lead-dbs.org/
//
// The build is served from its folder on a local port; the second argument is its baseURL. CHROME_PATH runs
// an installed Chrome instead of Playwright's Chromium.
import { createServer } from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { chromium, webkit } from 'playwright';

const [dir, baseURL] = process.argv.slice(2);
if (!dir || !baseURL) { console.error('usage: check-interactions.mjs <build folder> <baseURL>'); process.exit(2); }

// the pages the journeys use
const ATLASES = 'helpsupport/knowledge-base/atlasesresources/atlases-2/';
const DOWNLOAD = 'download/';
const MANUAL = 'manual/';
const GALLERY = 'gallery/';
const VIDEOS = 'helpsupport/knowledge-base/walkthrough-videos/';

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
// Options: motion (the reader's motion preference, 'reduce' unless set), script (false: script off), engine
// (another browser, WebKit).
async function journey(name, view, steps, { motion = 'reduce', script = true, engine = browser } = {}) {
  const context = await engine.newContext({ viewport: { width: view.width, height: view.height }, isMobile: view.mobile, hasTouch: view.mobile,
    reducedMotion: motion, javaScriptEnabled: script });
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
const tablet = { width: 820, height: 1180, mobile: true };
// text geometry waits for the fonts: a fallback face lays out lines differently
const fonts = (page) => page.evaluate(() => document.fonts.ready.then(() => null));

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

// The menu sheet by keyboard. A short name for each stop: the sheet's words, then the bar's actions.
const stop = (page) => page.evaluate(() => {
  const el = document.activeElement;
  if (!el || el === document.body) return 'nothing';
  if (el.matches('.nav__toggle')) return 'menu button';
  if (el.matches('.nav__download')) return 'Download';
  if (el.matches('.nav__theme')) return 'theme';
  if (el.matches('.nav__actions [data-search-open]')) return 'Search';
  if (el.closest('.nav__item--sheet') && /github/i.test(el.textContent)) return 'GitHub';
  if (el.closest('#site-menu')) return `word: ${(el.textContent.trim() || el.getAttribute('aria-label') || '').replace(/\s+/g, ' ').slice(0, 30)}`;
  return `outside the sheet: ${el.tagName.toLowerCase()}.${String(el.className).split(' ')[0]}`;
});
for (const view of [tablet, phone]) {
  await journey(`menu sheet by keyboard (${view.width}px): Tab and Shift+Tab run through it and around`, view, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('.nav__toggle').click();
    if (!(await until(page, () => document.querySelector('.nav').classList.contains('is-open')))) { fail('the menu button does not open the sheet'); return; }
    const first = await stop(page);
    const forward = [first];
    for (let i = 0; i < 60; i += 1) {
      await page.keyboard.press('Tab');
      const s = await stop(page);
      if (s === first) break;
      forward.push(s);
    }
    if (forward.length >= 60) { fail(`Tab never comes back to the first word: ${forward.slice(-6).join(' → ')}`); return; }
    const tail = forward.filter((s) => !s.startsWith('word: '));
    const want = ['GitHub', 'Search', 'theme', 'Download', 'menu button'];
    if (tail.join(' → ') !== want.join(' → ')) fail(`after the words Tab goes ${tail.join(' → ')}, not ${want.join(' → ')}`);
    if (forward.some((s) => s.startsWith('outside') || s === 'nothing')) fail(`Tab leaves the sheet: ${forward.find((s) => s.startsWith('outside') || s === 'nothing')}`);
    const back = [];
    for (let i = 0; i < forward.length; i += 1) { await page.keyboard.press('Shift+Tab'); back.push(await stop(page)); }
    const expected = [...forward.slice(1).reverse(), first];
    if (back.join(' | ') !== expected.join(' | ')) fail(`Shift+Tab does not run the same way back: ${back.slice(0, 6).join(' → ')} …`);
  });
}

// A dialog over the page holds it: the wheel does not move the page behind, and closing returns to the same place.
await journey('search dialog holds the page: no scrolling behind it, the same place after closing', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  await page.evaluate(() => scrollTo(0, 1500));
  await page.waitForTimeout(150);
  const y0 = await page.evaluate(() => scrollY);
  await page.locator('.nav [data-search-open]').click();
  if (!(await until(page, () => document.getElementById('site-search')?.open))) { fail('the search dialog does not open'); return; }
  await page.mouse.move(720, 850);
  await page.mouse.wheel(0, 600);
  await page.waitForTimeout(300);
  const y1 = await page.evaluate(() => scrollY);
  if (Math.abs(y1 - y0) > 1) fail(`the wheel scrolls the page behind the open search (${y0} → ${y1})`);
  await page.keyboard.press('Escape');
  if (await page.evaluate(() => document.getElementById('site-search').open)) await page.keyboard.press('Escape');
  await until(page, () => !document.getElementById('site-search').open);
  const y2 = await page.evaluate(() => scrollY);
  if (Math.abs(y2 - y0) > 1) fail(`after closing the search the page is at ${y2}, not ${y0}`);
});
for (const view of [desktop, phone]) {
  await journey(`gallery lightbox holds the page (${view.width}px)`, view, async (page, fail) => {
    await page.goto(url(GALLERY), { waitUntil: 'load' });
    const first = page.locator('.g-item__img').first();
    await first.scrollIntoViewIfNeeded();
    await page.evaluate(() => scrollBy(0, 120));
    await page.waitForTimeout(150);
    const y0 = await page.evaluate(() => scrollY);
    await first.focus();
    await page.keyboard.press('Enter');
    if (!(await until(page, () => document.querySelector('.g-box')?.open))) { fail('Enter on a picture does not open the lightbox'); return; }
    await page.mouse.move(view.width / 2, view.height / 2);
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(300);
    const y1 = await page.evaluate(() => scrollY);
    if (Math.abs(y1 - y0) > 1) fail(`the wheel scrolls the page behind the lightbox (${y0} → ${y1})`);
    await page.keyboard.press('Escape');
    if (!(await until(page, () => !document.querySelector('.g-box').open))) { fail('Escape does not close the lightbox'); return; }
    const y2 = await page.evaluate(() => scrollY);
    if (Math.abs(y2 - y0) > 1) fail(`after closing the lightbox the page is at ${y2}, not ${y0}`);
    if (!(await page.evaluate(() => document.activeElement === document.querySelector('.g-item__img')))) fail(`the focus is not back on the picture (it is on ${await focused(page)})`);
  });
}

// The home page as most visitors see it, with motion.
await journey('home with motion: the hero\'s words and actions show at once', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  const dim = await page.evaluate(() => {
    const seen = (el) => { let o = 1; for (let a = el; a; a = a.parentElement) o *= Number(getComputedStyle(a).opacity); return o; };
    return ['.home-hero .hero__lead', '.home-hero .btn-row'].map((s) => [s, document.querySelector(s)]).filter(([, el]) => el && seen(el) < 0.99)
      .map(([s, el]) => `${s} at opacity ${seen(el).toFixed(2)}`);
  });
  for (const d of dim) fail(`500 ms after the page's HTML: ${d}`);
}, { motion: 'no-preference' });
await journey('home with motion: the video\'s button pauses it, or the poster stands without a button', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const btn = page.locator('[data-hero-pause]');
  const playing = await until(page, () => { const b = document.querySelector('[data-hero-pause]'); return b && !b.hidden && b.checkVisibility(); });
  if (!playing) {
    // the clip did not start here (Playwright's Chromium lacks some codecs): no dead control, the poster stays
    if (await btn.isVisible()) fail('a pause button shows for a video that does not play');
    if (!(await page.evaluate(() => document.querySelector('.hero__bg')?.getAttribute('poster')))) fail('the hero video has no poster');
    return;
  }
  const label = await btn.getAttribute('aria-label');
  await btn.click();
  if (!(await until(page, (l) => document.querySelector('[data-hero-pause]').getAttribute('aria-label') !== l, label))) fail('the video\'s button does not change its name when pressed');
  if (!(await page.evaluate(() => document.querySelector('.hero__bg').paused))) fail('the video plays on after its pause button');
}, { motion: 'no-preference' });
for (const view of [desktop, { width: 820, height: 1180, mobile: false }]) {
  await journey(`home with motion (${view.width}px): the quotes' pause button is not covered and pauses them`, view, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await fonts(page);
    const btn = page.locator('[data-drift-pause]');
    await page.locator('.render-band').scrollIntoViewIfNeeded();
    if (!(await until(page, () => { const b = document.querySelector('[data-drift-pause]'); return b && !b.hidden; }))) { fail('the quotes have no pause button'); return; }
    const hit = await btn.evaluate((b) => {
      const r = b.getBoundingClientRect();
      // its centre and four points around it, inside the round button (a corner of its box is outside the circle)
      const cx = r.left + r.width / 2, cy = r.top + r.height / 2, dx = r.width * 0.3, dy = r.height * 0.3;
      return [[cx, cy], [cx - dx, cy], [cx + dx, cy], [cx, cy - dy], [cx, cy + dy]]
        .map(([x, y]) => { const e = document.elementFromPoint(x, y); return e === b || b.contains(e) ? '' : `${e?.tagName.toLowerCase()}.${String(e?.className).split(' ')[0]}`; })
        .filter(Boolean);
    });
    // a click on a covered button would press what covers it (and may leave the page)
    if (hit.length) { fail(`the quotes' pause button is covered by ${hit[0]}`); return; }
    const before = page.url();
    const label = await btn.getAttribute('aria-label');
    const pressed = await btn.getAttribute('aria-pressed');
    await btn.click();
    await page.waitForTimeout(200);
    if (page.url() !== before) fail(`pressing the quotes' pause button leaves the page (${page.url()})`);
    if (await btn.getAttribute('aria-label') === label && await btn.getAttribute('aria-pressed') === pressed) fail('the quotes\' pause button changes neither its name nor aria-pressed');
    if (!(await page.evaluate(() => [...document.querySelectorAll('.drift__track')].every((t) => getComputedStyle(t).animationPlayState === 'paused')))) fail('the quotes still move after their pause button');
  }, { motion: 'no-preference' });
}
await journey('home with motion: the figure grid has a pause button that stops it', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const grid = page.locator('[data-made-grid]');
  await grid.scrollIntoViewIfNeeded();
  // the button: any visible button of the figures' section whose name says pause
  const find = () => [...document.querySelectorAll('.made button, button[data-made-pause]')].find((b) => /pause/i.test(b.getAttribute('aria-label') || b.textContent) && b.checkVisibility());
  if (!(await until(page, find))) { fail('no visible "Pause figures" button by the figure grid'); return; }
  await (await page.evaluateHandle(find)).asElement().click();
  await page.waitForTimeout(300);
  const at = () => page.evaluate(() => [...document.querySelectorAll('.made-tile')].slice(0, 4).map((t) => t.style.transform).join('|'));
  const a = await at();
  await page.waitForTimeout(1200);
  if (a !== await at()) fail('the figures still drift after "Pause figures"');
}, { motion: 'no-preference' });

// An address with a broken fragment must not stop the page's script.
for (const hash of ['#%', '#%E0%A4%A']) {
  await journey(`manual at ${hash}: no script error, the Chapters button still opens`, phone, async (page, fail) => {
    await page.goto(url(MANUAL) + hash, { waitUntil: 'load' });
    const chapters = page.locator('.manual-menu');
    if (!(await until(page, () => document.querySelector('.manual-menu')?.checkVisibility()))) { fail('the Chapters button is not shown'); return; }
    await chapters.click();
    if (!(await until(page, () => document.getElementById('manual-drawer')?.open))) fail('the Chapters button does not open the chapters');
  });
}

// Without script.
await journey('without script: the phone menu opens as #site-menu', phone, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const link = page.locator('.nav__nojs-menu');
  if (!(await link.isVisible())) { fail('no visible Menu link without script'); return; }
  await link.click();
  if (!page.url().endsWith('#site-menu')) fail(`the Menu link goes to ${page.url()}`);
  if (!(await page.locator('#site-menu .nav__link').first().isVisible())) fail('the menu\'s words are not visible after the Menu link');
}, { script: false });
await journey('without script: the manual\'s chapters are on the page', phone, async (page, fail) => {
  await page.goto(url(MANUAL), { waitUntil: 'load' });
  const n = await page.evaluate(() => [...document.querySelectorAll('.manual-nav a[href*="/manual/"], noscript ~ * a[href*="/manual/"]')].filter((a) => a.checkVisibility()).length);
  if (n < 10) fail(`only ${n} chapter links are visible without script`);
}, { script: false });
await journey('without script: the videos are links to their sites', desktop, async (page, fail) => {
  await page.goto(url(VIDEOS), { waitUntil: 'load' });
  const n = await page.evaluate(() => [...document.querySelectorAll('a.video-embed__start')].filter((a) => /^https:\/\/(www\.)?(youtube(-nocookie)?\.com|youtu\.be|vimeo\.com)\//.test(a.href) && a.checkVisibility()).length);
  if (!n) fail('no video is a visible link to its site without script');
}, { script: false });

// A short run in WebKit, Safari's engine: the parts most likely to differ between engines.
let wk = null;
try { wk = await webkit.launch(); } catch { console.log('skip WebKit smoke: Playwright\'s WebKit is not installed (npx playwright install webkit)'); }
if (wk) {
  await journey('WebKit: the phone menu opens and Escape closes it', phone, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('.nav__toggle').click();
    if (!(await until(page, () => document.querySelector('.nav').classList.contains('is-open')))) { fail('the menu button does not open the sheet'); return; }
    if (!(await page.locator('#site-menu .nav__link').first().isVisible())) fail('the sheet\'s words are not visible');
    await page.keyboard.press('Escape');
    if (!(await until(page, () => !document.querySelector('.nav').classList.contains('is-open')))) fail('Escape does not close the sheet');
  }, { engine: wk });
  await journey('WebKit: the manual\'s Chapters open in a drawer', phone, async (page, fail) => {
    await page.goto(url(MANUAL), { waitUntil: 'load' });
    await page.locator('.manual-menu').click();
    if (!(await until(page, () => document.getElementById('manual-drawer')?.open))) { fail('the Chapters button does not open the drawer'); return; }
    if (!(await page.locator('#manual-drawer .manual-nav__row a').first().isVisible())) fail('the drawer shows no chapters');
    await page.keyboard.press('Escape');
    if (!(await until(page, () => !document.getElementById('manual-drawer').open))) fail('Escape does not close the drawer');
  }, { engine: wk });
  await journey('WebKit: the search opens and finds pages', desktop, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('.nav [data-search-open]').click();
    if (!(await until(page, () => document.getElementById('site-search')?.open))) { fail('the search dialog does not open'); return; }
    await page.keyboard.type('atlas');
    if (!(await until(page, () => document.querySelectorAll('#site-search .search__results a.search__hit').length > 0))) fail('"atlas" lists no results');
  }, { engine: wk });
  await wk.close();
}

await browser.close();
server.close();
for (const p of problems) console.log(p);
console.log(`${passed} journeys passed, ${problems.length} problems`);
process.exit(problems.length ? 1 : 0);
