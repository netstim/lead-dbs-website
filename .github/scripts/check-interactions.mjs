// Interactive journeys. Usage: node check-interactions.mjs <build folder> <baseURL> [--manual-only].
// CHROME_PATH selects a local Chromium; CI requires WebKit.
import { createServer } from 'node:http';
import { readFile, realpath } from 'node:fs/promises';
import { extname, join, normalize, sep } from 'node:path';
import { chromium, webkit } from 'playwright';

const [dir, baseURL, filter] = process.argv.slice(2);
if (!dir || !baseURL || (filter && filter !== '--manual-only')) {
  console.error('usage: check-interactions.mjs <build folder> <baseURL> [--manual-only]');
  process.exit(2);
}

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
async function journey(name, view, steps, { motion = 'reduce', script = true, engine = browser, manual = false } = {}) {
  if (filter === '--manual-only' && !manual) return;
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
const manualJourney = (name, view, steps, options) => journey(name, view, steps, { ...options, manual: true });
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

await journey('phone menu: the button opens the sheet, Escape and the close button close it', phone, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const toggle = page.locator('[data-menu-open]');
  if (!(await toggle.isVisible())) { fail('no menu button on a phone'); return; }
  await toggle.click();
  if (!(await until(page, () => document.getElementById('phone-menu')?.open))) fail('the menu button does not open the sheet');
  if (!(await page.evaluate(() => document.getElementById('phone-menu').contains(document.activeElement)))) fail(`the focus is not in the sheet once it opens (it is on ${await focused(page)})`);
  if (!(await page.locator('#phone-menu .nav-row a').first().isVisible())) fail('the sheet\'s words are not visible');
  await page.keyboard.press('Escape');
  if (!(await until(page, () => !document.getElementById('phone-menu')?.open))) fail('Escape does not close the sheet');
  if (!(await page.evaluate(() => document.activeElement === document.querySelector('[data-menu-open]')))) fail(`after Escape the focus is not on the menu button (it is on ${await focused(page)})`);
  await toggle.click();
  if (!(await until(page, () => document.getElementById('phone-menu')?.open))) { fail('the menu button does not reopen the sheet'); return; }
  await page.locator('#phone-menu [aria-label="Close menu"]').click();
  if (!(await until(page, () => !document.getElementById('phone-menu')?.open))) fail('the close button does not close the sheet');
});

for (const how of ['the "/" key', 'the header\'s button']) {
  await journey(`search: ${how} opens it, a query finds pages, Escape closes it`, desktop, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    const dialog = page.locator('#site-search');
    const opener = page.locator('.nav [data-search-open]');
    if (how.includes('/')) {
      // from a link in the page, which must have the focus again afterwards
      await page.locator('.nav__bar .site-logo').focus();
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
    const back = how.includes('/') ? '.nav__bar .site-logo' : '.nav [data-search-open]';
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

// The menu sheet (#phone-menu modal dialog) by keyboard: Tab stays inside the modal sheet.
for (const view of [tablet, phone]) {
  await journey(`menu sheet by keyboard (${view.width}px): Tab stays inside the sheet`, view, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('[data-menu-open]').click();
    if (!(await until(page, () => document.getElementById('phone-menu')?.open))) { fail('the menu button does not open the sheet'); return; }
    if (!(await page.evaluate(() => document.getElementById('phone-menu').contains(document.activeElement)))) fail('Opening must move focus into #phone-menu');
    const seen = new Set();
    for (let i = 0; i < 20; i += 1) {
      await page.keyboard.press('Tab');
      const ok = await page.evaluate(() => {
        const dlg = document.getElementById('phone-menu');
        return dlg.contains(document.activeElement) ? (document.activeElement.textContent.trim() || document.activeElement.getAttribute('aria-label') || document.activeElement.tagName) : null;
      });
      if (!ok) { fail(`Tab left #phone-menu (focus on ${await focused(page)})`); return; }
      seen.add(ok);
    }
    if (seen.size < 4) fail(`Tab only reached ${seen.size} controls inside #phone-menu`);
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
await journey('home with motion: the opening words and actions show at once', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);
  const dim = await page.evaluate(() => {
    const seen = (el) => { let o = 1; for (let a = el; a; a = a.parentElement) o *= Number(getComputedStyle(a).opacity); return o; };
    return ['.story__step--first .story__lead', '.story__step--first .btn-row'].map((s) => [s, document.querySelector(s)]).filter(([, el]) => el && seen(el) < 0.99)
      .map(([s, el]) => `${s} at opacity ${seen(el).toFixed(2)}`);
  });
  for (const d of dim) fail(`500 ms after the page's HTML: ${d}`);
}, { motion: 'no-preference' });
await journey('home with motion: the researcher quote panel cycles with its arrow buttons', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  await fonts(page);
  const rot = page.locator('[data-voice-rotator]');
  await rot.scrollIntoViewIfNeeded();
  const next = rot.locator('[data-voice-next]');
  if (!(await next.isVisible())) { fail('the quote arrows are not visible'); return; }
  const q0 = await rot.locator('.voice__slide.is-active .voice__quote').textContent();
  await next.click();
  const q1 = await rot.locator('.voice__slide.is-active .voice__quote').textContent();
  if (q1 === q0) fail('pressing the next quote arrow did not advance the quote');
  await rot.locator('[data-voice-prev]').click();
  const q2 = await rot.locator('.voice__slide.is-active .voice__quote').textContent();
  if (q2 !== q0) fail('pressing the previous quote arrow did not return to the first quote');
}, { motion: 'no-preference' });
await journey('home with motion: the gallery strip has a pause button that stops it', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  const strip = page.locator('[data-made-strip]');
  await strip.scrollIntoViewIfNeeded();
  const btn = page.locator('[data-made-strip-pause]');
  if (!(await until(page, () => { const b = document.querySelector('[data-made-strip-pause]'); return b && !b.hidden && b.checkVisibility(); }))) { fail('no visible pause button by the gallery strip'); return; }
  await page.mouse.move(0, 0);
  await page.evaluate(() => document.activeElement?.blur());
  const x0 = await strip.evaluate((el) => el.scrollLeft);
  await page.waitForTimeout(700);
  if (x0 === await strip.evaluate((el) => el.scrollLeft)) fail('gallery strip never moved before pause');
  await btn.click();
  if (await btn.getAttribute('aria-label') !== 'Play the gallery') fail('pause label did not change');
  await page.waitForTimeout(200);
  const a = await strip.evaluate((el) => el.scrollLeft);
  await page.waitForTimeout(900);
  if (a !== await strip.evaluate((el) => el.scrollLeft)) fail('the gallery strip still glides after pause');
  await btn.click();
  await page.mouse.move(0, 0);
  await btn.evaluate((b) => b.blur());
  await page.waitForTimeout(700);
  if (a === await strip.evaluate((el) => el.scrollLeft)) fail('gallery strip did not resume');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  if (!(await until(page, () => document.querySelector('[data-made-strip-pause]').hidden))) { fail('reduced motion leaves pause visible'); return; }
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  if (!(await until(page, () => !document.querySelector('[data-made-strip-pause]').hidden))) fail('Play control does not return');
  const stopped = await strip.evaluate((el) => el.scrollLeft);
  await page.waitForTimeout(700);
  if (stopped !== await strip.evaluate((el) => el.scrollLeft)) fail('preference change restarted glide');
}, { motion: 'no-preference' });

for (const [name, view] of [['phone', phone], ['desktop', desktop]]) {
  await manualJourney(`manual with blocked bundle on ${name}: chapters and landing sections still work`, view, async (page, fail) => {
    await page.route('**/manual.min.*.js', r => r.abort());
    await page.goto(url(MANUAL), { waitUntil: 'load' });
    const browse = page.getByText('Browse chapters', { exact: true });
    if (await browse.isVisible()) await browse.click();
    const deep = page.locator('.manual-nav__tree a[href$="/checking-the-coregistration/"]');
    await page.locator('.manual-nav__tree summary').filter({ hasText: 'Registration subchapters' }).click();
    if (!(await deep.isVisible())) fail('nested chapters are unavailable');
    if (await page.getByRole('tablist').count()) fail('launch tabs are exposed without their script');
    if ((await page.locator('.manual-launch__command').textContent()).trim() !== 'lead dbs') fail('the fallback command is missing');
    if (name === 'phone') {
      await page.locator('.manual-toc-fold > summary').click();
      if (!(await page.locator('.manual-toc-fold a[href="#workflows"]').isVisible())) fail('fallback contents are unavailable');
    } else if (!(await page.locator('.manual-outline a[href="#workflows"]').isVisible())) {
      fail('desktop contents are unavailable');
    }
    await page.goto(url(MANUAL + 'installation/'));
    const edit = await page.getByRole('link', { name: 'Edit on GitHub' }).boundingBox();
    if (!edit || edit.height < 44) fail('Edit on GitHub has an undersized target');
  });
}

await manualJourney('desktop chapter rail and controls keep their positions', desktop, async (page, fail) => {
  let release;
  const held = new Promise(resolve => { release = resolve; });
  const bundle = /\/(?:main|manual)\.min\.[^/]+\.js$/;
  const holdBundle = async route => { await held; await route.continue(); };
  const registration = page.locator('.manual-nav__tree summary').filter({ hasText: 'Registration subchapters' });
  const chapter = page.locator('.manual-nav__tree').getByRole('link', { name: 'Surface reconstruction', exact: true });
  const search = page.locator('.manual-header__search');
  const edit = page.getByRole('link', { name: 'Edit on GitHub' });
  const normalisation = MANUAL + 'lead-dbs/step3-volume-registrations/normalization-of-images/';
  const position = async () => (await chapter.boundingBox())?.y;
  const compare = (before, after, message) => {
    if (before == null || after == null || Math.abs(before - after) > 1) fail(`${message}: ${before} → ${after}`);
  };
  try {
    await page.route(bundle, holdBundle);
    await page.goto(url(MANUAL + 'lead-dbs/step0-overview/'), { waitUntil: 'commit' });
    await chapter.waitFor();
    await fonts(page);
    const beforeBundle = await position();
    const searchBefore = (await search.boundingBox())?.x;
    const editBefore = (await edit.boundingBox())?.x;
    release();
    await page.locator('html.manual-ready').waitFor();
    compare(beforeBundle, await position(), 'the rail moved when the bundle initialized');
    compare(searchBefore, (await search.boundingBox())?.x, 'search moved when the theme control appeared');
    compare(editBefore, (await edit.boundingBox())?.x, 'the edit link moved when the copy control appeared');
    await page.unroute(bundle, holdBundle);

    await page.goto(url(normalisation));
    await fonts(page);
    const beforeNavigation = await position();
    await chapter.click();
    await page.waitForURL('**/step4-optional-surface-reconstruction/');
    await fonts(page);
    compare(beforeNavigation, await position(), 'the selected row moved when switching chapters');
    if (!(await registration.evaluate(summary => summary.parentElement.open))) fail('navigation lost the open branch');
  } finally {
    release();
  }
});

await manualJourney('the Manual landing stays in place when the bundle arrives', phone, async (page, fail) => {
  let release;
  const ready = new Promise(resolve => { release = resolve; });
  await page.route('**/manual.min.*.js', async route => {
    await ready;
    await route.continue();
  });
  try {
    await page.goto(url(MANUAL), { waitUntil: 'commit' });
    await page.locator('.manual-toc-fold > summary').waitFor();
    await fonts(page);
    const before = await page.locator('#workflows').boundingBox();
    release();
    await page.locator('.manual-sections').waitFor();
    const after = await page.locator('#workflows').boundingBox();
    if (!before || !after || Math.abs(before.y - after.y) > 1) fail('workflows moved when the controls initialized');
  } finally {
    release();
  }
});

await manualJourney('manual skip link puts keyboard focus in the article', desktop, async (page, fail) => {
  await page.goto(url(MANUAL + 'installation/'));
  // The preview banner has one link before the skip link.
  for (let i = 0; i < 2 && !(await page.evaluate(() => document.activeElement.matches('.skip-link'))); i += 1) {
    await page.keyboard.press('Tab');
  }
  await page.keyboard.press('Enter');
  if (!(await until(page, () => document.activeElement === document.getElementById('manual-content')))) fail('Skip to content did not focus the article heading');
  await page.keyboard.press('Tab');
  if (await page.evaluate(() => document.activeElement.closest('.manual-nav') !== null)) fail('Tab entered the chapters after skipping them');
});

await manualJourney('manual outline scrolls its active item into view on short desktop windows', { ...desktop, height: 340 }, async (page, fail) => {
  await page.goto(url(MANUAL + 'installation/#useful-tools'));
  await fonts(page);
  if (!(await until(page, () => {
    const outline = document.querySelector('.manual-outline');
    const active = outline.querySelector('a[aria-current="location"][href="#useful-tools"]');
    return active && active.getBoundingClientRect().bottom <= outline.getBoundingClientRect().bottom + 1;
  }))) fail('the active section is missing or clipped by the outline');

  await page.evaluate(() => {
    document.querySelector('#normal-installation').scrollIntoView();
  });
  const outline = page.locator('.manual-outline');
  await page.waitForFunction(() => document.querySelector('.manual-outline a[aria-current="location"][href="#normal-installation"]'));
  const before = await outline.evaluate(el => {
    el.scrollTop = el.scrollHeight;
    return el.scrollTop;
  });
  await page.evaluate(() => scrollBy(0, 1));
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  if ((await outline.evaluate(el => el.scrollTop)) !== before) fail('article scrolling reset the independent outline scroll');
});

await manualJourney('the last section can become active at the end of a chapter', desktop, async (page, fail) => {
  await page.goto(url(MANUAL + 'installation/#useful-tools'));
  await fonts(page);
  await page.evaluate(() => scrollTo(0, document.scrollingElement.scrollHeight));
  if (!(await until(page, () => document.querySelector('.manual-outline a[aria-current="location"][href="#useful-tools"]') !== null))) {
    fail('the final heading never becomes current');
  }
});

const checkManualContents = async (page, fail) => {
  await page.goto(url(MANUAL));
  await page.locator('.manual-sections').click();
  const entries = await page.locator('#manual-contents a').evaluateAll(links => links.map(link => link.hash));
  if (entries.join(' ') !== '#workflows #research-use') fail('the landing outline differs from article order');
  await page.locator('#manual-contents a[href="#workflows"]').click();
  if (!(await until(page, () => {
    const heading = document.getElementById('workflows');
    return location.hash === '#workflows' && document.activeElement === heading &&
      heading.getBoundingClientRect().top >= document.querySelector('.manual-nav').getBoundingClientRect().bottom;
  }))) fail('the selected section is covered or did not receive focus');

  await page.goto(url(MANUAL + 'installation/#troubleshooting'));
  await page.locator('.manual-sections').click();
  const drawer = await page.locator('#manual-contents').boundingBox();
  if (!drawer || drawer.y + drawer.height > page.viewportSize().height + 1) fail('the contents drawer extends below the viewport');
  await page.keyboard.press('Escape');
  if (!(await until(page, () => document.activeElement.matches('.manual-sections')))) fail('Escape did not return focus to the contents button');
};
await manualJourney('manual contents drawer fits a short tablet and focuses its destination', { ...tablet, height: 340 }, checkManualContents);

for (const [name, view] of [['rail', desktop], ['drawer', phone]]) {
  await manualJourney(`manual ${name} leaves room below the last active chapter`, view, async (page, fail) => {
    await page.goto(url(MANUAL + 'appendix/using-slicer/sweet-sour-spot/'));
    if (view.mobile) await page.locator('.manual-menu').click();
    if (!(await until(page, (mobile) => {
      const box = document.querySelector(mobile ? '.manual-drawer__body' : '.manual-nav');
      const row = box.querySelector('[aria-current="page"]');
      return row && box.getBoundingClientRect().bottom - row.getBoundingClientRect().bottom >= 10;
    }, view.mobile))) fail('the active chapter is flush against the lower edge');
  });
}

await manualJourney('manual dark theme paints a matching page canvas and preview banner', desktop, async (page, fail) => {
  await page.emulateMedia({ colorScheme: 'dark' });
  await page.goto(url(MANUAL));
  if (!await page.evaluate(() => {
    const color = (element) => getComputedStyle(element).backgroundColor;
    const root = document.documentElement;
    const banner = document.querySelector('.manual-header .preview-banner');
    return root.dataset.theme === 'dark' && color(root) === color(document.body) &&
      (!banner || color(banner) === color(document.querySelector('.manual-header__search')));
  })) fail('the viewport canvas or banner still uses the light preview color');
});

await manualJourney('manual breadcrumb contains all ancestors of a nested article', desktop, async (page, fail) => {
  await page.goto(url(MANUAL + 'lead-dbs/step5-optional-reconstruction-of-electrode-trajectories/determining-the-orientation-of-directional-leads/automatic-algorithm/'));
  const crumbs = await page.locator('.manual-crumbs a').allTextContents();
  if (crumbs.length !== 4 || crumbs[0] !== 'Manual') fail(`incomplete breadcrumb: ${crumbs.join(' / ')}`);
});
await manualJourney('manual clipboard unavailable: no dead Copy link control', phone, async (page, fail) => {
  await page.addInitScript(() => Object.defineProperty(navigator, 'clipboard', { value: undefined }));
  await page.goto(url('manual/lead-dbs/step3-volume-registrations/checking-the-coregistration/'), { waitUntil: 'load' });
  if (await page.locator('[data-copy-url]').isVisible()) fail('dead copy control is visible');
});

await manualJourney('manual rejected clipboard: explicit failure feedback', phone, async (page, fail) => {
  await page.addInitScript(() => Object.defineProperty(navigator, 'clipboard', { value: { writeText: () => Promise.reject(new Error('denied')) } }));
  await page.goto(url('manual/lead-dbs/step3-volume-registrations/checking-the-coregistration/'), { waitUntil: 'load' });
  const edit = page.getByRole('link', { name: 'Edit on GitHub' });
  const before = await edit.boundingBox();
  await page.locator('[data-copy-url]').click();
  if (!(await until(page, () => /could not|couldn.t|unable|failed/i.test(document.querySelector('[role="status"]')?.textContent || '')))) fail('copy rejection has no feedback');
  const after = await edit.boundingBox();
  if (!before || !after || Math.abs(before.x - after.x) > 1) fail('copy feedback moved the edit link');
});

await journey('home initially reduced: restoring motion exposes a stopped Play control', desktop, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  if (!(await until(page, () => { const b = document.querySelector('[data-made-strip-pause]'); return b && !b.hidden && b.getAttribute('aria-label') === 'Play the gallery'; }))) fail('initially reduced gallery strip has no stopped Play control');
});

// An address with a broken fragment must not stop the page's script.
for (const hash of ['#%', '#%E0%A4%A']) {
  await manualJourney(`manual at ${hash}: no script error, the Chapters button still opens`, phone, async (page, fail) => {
    await page.goto(url(MANUAL) + hash, { waitUntil: 'load' });
    const chapters = page.locator('.manual-menu');
    if (!(await until(page, () => document.querySelector('.manual-menu')?.checkVisibility()))) { fail('the Chapters button is not shown'); return; }
    await chapters.click();
    if (!(await until(page, () => document.getElementById('manual-drawer')?.open))) fail('the Chapters button does not open the chapters');
  });
}

// Without script.
await journey('without script: the home story shows its still fallbacks', phone, async (page, fail) => {
  await page.goto(url(''), { waitUntil: 'load' });
  if (!(await page.locator('.story__still img').first().isVisible())) fail('no visible story fallback picture without script');
}, { script: false });
await manualJourney('without script: the manual\'s chapters are on the page', phone, async (page, fail) => {
  await page.goto(url(MANUAL), { waitUntil: 'load' });
  await page.locator('.manual-nav__fold > summary').click();
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
try { wk = await webkit.launch(); } catch (error) { if (process.env.CI || !/Executable doesn't exist/.test(error.message)) throw error; console.log('skip WebKit smoke: executable missing'); }
if (wk) {
  await journey('WebKit: the phone menu opens and Escape closes it', phone, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('[data-menu-open]').click();
    if (!(await until(page, () => document.getElementById('phone-menu')?.open))) { fail('the menu button does not open the sheet'); return; }
    if (!(await page.locator('#phone-menu .nav-row a').first().isVisible())) fail('the sheet\'s words are not visible');
    await page.keyboard.press('Escape');
    if (!(await until(page, () => !document.getElementById('phone-menu')?.open))) fail('Escape does not close the sheet');
  }, { engine: wk });
  await manualJourney('WebKit: the manual\'s Chapters open in a drawer', phone, async (page, fail) => {
    await page.goto(url(MANUAL), { waitUntil: 'load' });
    await page.locator('.manual-menu').click();
    if (!(await until(page, () => document.getElementById('manual-drawer')?.open))) { fail('the Chapters button does not open the drawer'); return; }
    if (!(await page.locator('#manual-drawer .manual-nav__row a').first().isVisible())) fail('the drawer shows no chapters');
    await page.keyboard.press('Escape');
    if (!(await until(page, () => !document.getElementById('manual-drawer').open))) fail('Escape does not close the drawer');
  }, { engine: wk });
  await manualJourney('WebKit: manual contents fit the viewport and focus their destination', phone, checkManualContents, { engine: wk });
  await manualJourney('WebKit: manual figures enlarge in place and remain dismissible', phone, async (page, fail) => {
    await page.goto(url(MANUAL + 'lead-dbs/step0-overview/'));
    const article = page.url();
    await page.locator('.img-figure .img-zoom').first().click();
    if (!(await until(page, () => document.getElementById('manual-image')?.open && document.querySelector('#manual-image img').naturalWidth > 0))) {
      fail('the figure did not load in a dialog'); return;
    }
    if (page.url() !== article) fail('zoom opened another document');
    const box = await page.locator('#manual-image').boundingBox();
    if (!box || box.y < 0 || box.y + box.height > page.viewportSize().height + 1) fail('viewer is clipped by the viewport');
    await page.getByRole('button', { name: 'Close image' }).click();
    if (!(await until(page, () => !document.getElementById('manual-image').open))) fail('the viewer could not be dismissed');
  }, { engine: wk });
  await journey('WebKit: the search opens and finds pages', desktop, async (page, fail) => {
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('.nav [data-search-open]').click();
    if (!(await until(page, () => document.getElementById('site-search')?.open))) { fail('the search dialog does not open'); return; }
    await page.keyboard.type('atlas');
    if (!(await until(page, () => document.querySelectorAll('#site-search .search__results a.search__hit').length > 0))) fail('"atlas" lists no results');
  }, { engine: wk });
  await journey('WebKit: narrow phone actions and root menu lock', { width: 320, height: 667, mobile: true }, async (page, fail) => {
    for (const path of ['', DOWNLOAD, MANUAL, 'contact/', GALLERY]) {
      await page.goto(url(path), { waitUntil: 'load' });
      if (await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1)) fail(`${path}: horizontal page overflow`);
      const tiny = await page.locator('input:not([type="hidden"]), textarea, select').evaluateAll(els => els.filter(el => el.getClientRects().length && parseFloat(getComputedStyle(el).fontSize) < 16).length);
      if (tiny) fail(`${path}: input triggers iOS text zoom`);
    }
    await page.goto(url(''), { waitUntil: 'load' });
    await page.locator('[data-menu-open]').click();
    if (!(await until(page, () => document.getElementById('phone-menu')?.open))) { fail('phone menu did not open'); return; }
    const locked = await page.evaluate(() => getComputedStyle(document.documentElement).overflowY === 'hidden');
    if (!locked) fail('root scroller is unlocked while modal menu is open');
    await page.keyboard.press('Escape');
    if (await page.evaluate(() => getComputedStyle(document.documentElement).overflowY === 'hidden')) fail('root remains locked after Escape');
  }, { engine: wk });
  await wk.close();
}

await browser.close();
server.close();
for (const p of problems) console.log(p);
console.log(`${passed} journeys passed, ${problems.length} problems`);
process.exit(problems.length ? 1 : 0);
