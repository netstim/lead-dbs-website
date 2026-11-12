// The site's own script.
// Each block stands alone and does nothing on a page without its markup. Without script every page
// still works: the header's menu button becomes a link to the footer's list of pages, videos are
// links, events show what the build chose.

// ------------------------------------------------------------------ header
// Below 1200px the menu words live in a sheet the menu button opens; a panel's links open with the
// chevron beside its word. Opening the sheet moves the focus to its first word; Tab and Shift+Tab then
// stay inside the sheet, its bar along the bottom (a phone) and the menu button, which now closes it.
// Escape closes the sheet and leaves the focus on the menu button; a tap on any link in the sheet
// closes it. From 1200px the words are in the bar, each panel under its word (below).
(() => {
  const nav = document.querySelector('.nav');
  const toggle = nav?.querySelector('.nav__toggle');
  if (!nav || !toggle) return;
  const wide = window.matchMedia('(min-width: 1200px)');
  const icon = {
    open: '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M2 5h14M2 13h14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
    close: '<svg width="18" height="18" viewBox="0 0 18 18" aria-hidden="true"><path d="M4 4l10 10M14 4L4 14" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>',
  };
  const menu = nav.querySelector('#site-menu');
  // what Tab may reach while the sheet is open: the sheet's links and buttons, the header's own actions
  // (in the sheet's bottom bar on a phone, in the bar above it on a tablet) and the menu button
  const inSheet = () => [...nav.querySelectorAll('#site-menu a[href], #site-menu button, .nav__actions a[href], .nav__toggle')]
    .filter((el) => el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden');
  const setOpen = (open, focus = false) => {
    nav.classList.toggle('is-open', open);
    document.body.classList.toggle('nav-locked', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close the menu' : 'Open the menu');
    toggle.innerHTML = open ? icon.close : icon.open;
    if (open && focus) inSheet().find((el) => menu?.contains(el))?.focus();
  };
  toggle.addEventListener('click', () => setOpen(!nav.classList.contains('is-open'), true));
  wide.addEventListener('change', (e) => {
    hovered = null; clearTimeout(timer);
    if (e.matches) setOpen(false);
  });
  // A word with pages gets a chevron button beside it (the disclosure pattern with top-level links): the
  // word stays a link to its group's page, the button opens and closes the word's panel and says
  // whether it is open (aria-expanded). In the sheet it opens the pages under the word. On a desktop the
  // panel also opens on hover (assets/css/site.css); from the keyboard, Tab goes from word to word, Enter
  // or Space on the chevron opens the panel and the next Tab enters it, Arrow Down on the word or the
  // chevron opens it and moves to its first link, Arrow Up and Down, Home and End move inside it, and
  // Escape (or the focus leaving the word) closes it, the focus back on the chevron.
  const items = [];
  const close = (item, updateBand = true) => { item.classList.remove('is-expanded'); item.sync(updateBand); };
  // A stable frame holds every desktop panel. Commit all disclosure states before measuring
  // it, so switching groups never briefly closes the band or animates its height.
  const band = document.createElement('div');
  band.className = 'nav__band';
  band.setAttribute('aria-hidden', 'true');
  nav.append(band);
  band.sync = () => {
    const shown = wide.matches && items.some((i) => i.querySelector('.nav__expand')?.getAttribute('aria-expanded') === 'true');
    if (wide.matches) {
      const panels = [...nav.querySelectorAll('.nav__menu')];
      band.style.height = `${Math.ceil(Math.max(0, ...panels.map(p => p.offsetHeight)))}px`;
    }
    nav.classList.toggle('band-open', !!shown);
  };
  addEventListener('resize', () => band.sync());
  document.fonts?.ready.then(() => band.sync());
  nav.querySelectorAll('.nav__item').forEach((item) => {
    const panel = item.querySelector('.nav__menu');
    if (!panel) return;
    const word = item.querySelector('.nav__link');
    const btn = document.createElement('button');
    btn.className = 'nav__expand';
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    if (panel.id) btn.setAttribute('aria-controls', panel.id);
    word.removeAttribute('aria-controls');
    word.removeAttribute('aria-expanded');
    btn.setAttribute('aria-label', `${word.textContent.trim()}: show the pages`);
    btn.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    word.after(btn);
    items.push(item);
    // open: in the sheet, the chevron's state; on a desktop, also while the pointer is on the word or its
    // band (.is-hovered, set below; unless Escape or the chevron closed it there)
    item.sync = (updateBand = true) => {
      const open = item.classList.contains('is-expanded')
        || (wide.matches && !item.classList.contains('is-dismissed') && item.classList.contains('is-hovered'));
      btn.setAttribute('aria-expanded', String(open));
      panel.inert = !open;
      panel.setAttribute('aria-hidden', String(!open));
      if (updateBand) band.sync();
    };
    const links = () => [...panel.querySelectorAll('a[href]')].filter((a) => a.getClientRects().length);
    const openTo = (i) => {
      if (wide.matches) {
        hovered = null;
        items.forEach((other) => {
          if (other !== item) { other.classList.remove('is-hovered'); close(other, false); }
        });
      }
      item.classList.remove('is-dismissed');
      item.classList.add('is-expanded');
      item.sync();
      if (i !== undefined) setTimeout(() => {
        if (btn.getAttribute('aria-expanded') !== 'true') return;
        const l = links();
        l[i < 0 ? l.length - 1 : i]?.focus();
      }, wide.matches ? 120 : 0);
    };
    btn.addEventListener('click', () => {
      const open = btn.getAttribute('aria-expanded') === 'true';
      if (open) { close(item); if (wide.matches) item.classList.add('is-dismissed'); item.sync(); }
      else openTo();
    });
    item.addEventListener('keydown', (e) => {
      if (!wide.matches || e.altKey || e.ctrlKey || e.metaKey) return;
      const l = links();
      const at = l.indexOf(document.activeElement);
      if (e.key === 'Escape' && (item.classList.contains('is-expanded') || item.classList.contains('is-hovered'))) {
        e.preventDefault(); e.stopPropagation();
        close(item); item.classList.add('is-dismissed'); item.sync(); btn.focus();
      } else if (e.key === 'ArrowDown') {
        e.preventDefault();
        if (at < 0) openTo(0); else l[(at + 1) % l.length].focus();
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        if (at < 0) openTo(-1); else if (at === 0) btn.focus(); else l[at - 1].focus();
      } else if ((e.key === 'Home' || e.key === 'End') && at >= 0) {
        e.preventDefault(); l[e.key === 'Home' ? 0 : l.length - 1].focus();
      }
    });
    // a desktop panel closes when the focus leaves its word; it opens on hover again once the focus or
    // the pointer has left and come back
    item.addEventListener('focusout', (e) => {
      if (item.contains(e.relatedTarget)) return;
      item.classList.remove('is-dismissed');
      if (wide.matches) close(item);
    });
    item.addEventListener('pointerleave', () => item.classList.remove('is-dismissed'));
    wide.addEventListener('change', () => { item.classList.remove('is-hovered', 'is-dismissed'); close(item); });
    item.sync();
  });
  // a click elsewhere closes an open desktop panel
  document.addEventListener('click', (e) => {
    if (wide.matches) items.forEach((item) => { if (!item.contains(e.target)) close(item); });
  });
  // Hover on a desktop, for the header as a whole: a panel opens once the pointer has rested 180ms on its
  // word; moving to another word also waits briefly, so a passing pointer opens nothing. The
  // spaces between the words, the band and the bar around them keep the open panel, so moving along the
  // words never closes and reopens it; the logo, the actions on the right and a word without pages (News)
  // close it after 120ms, leaving the header after 200ms, so a pointer that slips out and back keeps it.
  let hovered = null, timer = 0;
  const hover = (item) => {
    clearTimeout(timer);
    if (item === hovered) return;
    hovered = item;
    items.forEach((i) => {
      i.classList.toggle('is-hovered', i === item);
      if (item && i !== item) i.classList.remove('is-expanded');
      i.sync(false);
    });
    band.sync();
  };
  const later = (item, ms) => { clearTimeout(timer); timer = setTimeout(() => hover(item), ms); };
  nav.addEventListener('pointerover', (e) => {
    if (!wide.matches || e.pointerType === 'touch' || nav.classList.contains('is-open')) return;
    const t = e.target;
    if (t.closest('.nav__menu')) { clearTimeout(timer); return; }
    const item = t.closest('.nav__links > .nav__item');
    if (item && items.includes(item)) { if (item !== hovered) later(item, hovered ? 130 : 180); else clearTimeout(timer); return; }
    if (item || t.closest('.nav__logo, .nav__actions')) { later(null, hovered ? 120 : 0); return; }
    clearTimeout(timer); // a space between the words or around them: the open panel stays
  });
  nav.addEventListener('pointerleave', (e) => { if (e.pointerType !== 'touch') later(null, 200); });
  nav.addEventListener('click', (e) => {
    if (nav.classList.contains('is-open') && e.target.closest('a[href]')) setOpen(false);
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      if (nav.classList.contains('is-open')) { setOpen(false); toggle.focus(); }
      return;
    }
    if (e.key !== 'Tab' || !nav.classList.contains('is-open')) return;
    const f = inSheet();
    if (!f.length) return;
    const first = f[0], last = f[f.length - 1];
    if (!f.includes(document.activeElement)) { e.preventDefault(); (e.shiftKey ? last : first).focus(); }
    else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
  });
})();

// ------------------------------------------------------------------ the home page's figure strip
// Where the strip scrolls sideways (a phone or a tablet), its right edge fades out while more figures
// follow, and its left edge once the first has moved away (assets/css/site.css, .fig-strip). While it
// scrolls it is a tab stop of its own (a labelled list), so the arrow keys move it; where every figure
// is in view it is not.
document.querySelectorAll('.fig-strip').forEach((strip) => {
  let queued = false;
  const update = () => {
    queued = false;
    const scrolls = strip.scrollWidth > strip.clientWidth + 4;
    strip.classList.toggle('is-moved', strip.scrollLeft > 4);
    strip.classList.toggle('is-end', strip.scrollLeft + strip.clientWidth >= strip.scrollWidth - 4);
    if (scrolls) strip.tabIndex = 0; else strip.removeAttribute('tabindex');
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  strip.addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  strip.querySelectorAll('img').forEach((img) => img.addEventListener('load', queue));
  update();
});

// ------------------------------------------------------------------ the header over a dark ground
// While a black ground ([data-nav-dark]: the home page's hero and its voices; every
// .page-head) lies under the header, the header takes the black too (.nav.is-dark, assets/css/site.css);
// once the ground has scrolled past, the light bar returns.
// Until this has run, a page that starts on a black ground (body.top-dark) shows the dark header from
// the first paint; html.nav-ready hands the state to this script, and only then do the colours fade.
// .nav.is-scrolled: the page is scrolled at all, so the home page's clear header turns solid before
// any of the hero's words pass under it.
(() => {
  const nav = document.querySelector('.nav');
  if (!nav) return;
  const grounds = [...document.querySelectorAll('[data-nav-dark], .page-head')];
  let queued = false;
  const update = () => {
    queued = false;
    const box = nav.getBoundingClientRect();
    // How much of the strip just under the bar (as tall as the bar) is a dark ground: the bar blends over
    // that much scroll instead of flipping at one line. A page head that starts right under the bar
    // counts in full, so such a page opens with the black bar (as body.top-dark paints it first).
    // Smoothstep gives the surface a gentle arrival at either end of the crossing.
    const top = box.bottom, bottom = box.bottom + box.height;
    const overlap = grounds.reduce((sum, g) => {
      const r = g.getBoundingClientRect();
      return sum + Math.max(0, Math.min(r.bottom, bottom) - Math.max(r.top, top));
    }, 0);
    const coverage = Math.min(1, overlap / Math.max(1, box.height));
    const darkness = coverage * coverage * (3 - 2 * coverage);
    nav.style.setProperty('--nav-darkness', darkness.toFixed(3));
    // A small dead zone prevents theme chatter when the scroll rests at the midpoint.
    if (darkness > .53) nav.classList.add('is-dark');
    else if (darkness < .47) nav.classList.remove('is-dark');
    nav.classList.toggle('is-scrolled', window.scrollY > 0);
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  update();
  requestAnimationFrame(() => document.documentElement.classList.add('nav-ready'));
})();

// ------------------------------------------------------------------ the home page's hero: its entrance
// The page head sets html.hero-wait, which keeps the hero's words hidden and its clip a little larger
// (assets/css/site.css). Here the title's words rise line by line out of their own lines, then the lead,
// the buttons, the proof line and the facts fade up one after another while the clip settles. The hero simply shows under
// reduced motion and when the page opens scrolled past it; if this runs late (html.hero-late, set 700ms
// after the head), the style sheet has already faded it in.
(() => {
  const hero = document.querySelector('.home-hero');
  const h1 = hero?.querySelector('h1');
  const root = document.documentElement;
  if (!hero) return;
  const shown = (still = false) => {
    hero.classList.toggle('is-still', still);
    hero.classList.remove('is-entering');
    hero.classList.add('is-entered');
  };
  if (!h1 || !root.classList.contains('hero-wait') || matchMedia('(prefers-reduced-motion: reduce)').matches
    || hero.getBoundingClientRect().bottom < 0) { shown(true); return; }
  if (root.classList.contains('hero-late')) { setTimeout(shown, 1150); return; }

  const ease = 'cubic-bezier(.22, 1, .36, 1)';
  const anims = [];
  let words = null, over = false;
  const finish = () => {
    if (over) return;
    over = true;
    anims.forEach((a) => a.cancel());
    if (words) { h1.replaceChildren(...words.original); h1.removeAttribute('aria-label'); }
    shown();
  };
  // each word of the title in a box that clips it, so it can rise from below its own line
  const splitWords = () => {
    const original = [...h1.childNodes];
    const copy = h1.cloneNode(true);
    const boxes = [];
    const walk = (node) => [...node.childNodes].forEach((n) => {
      if (n.nodeType === Node.ELEMENT_NODE) { walk(n); return; }
      if (n.nodeType !== Node.TEXT_NODE) return;
      const parts = document.createDocumentFragment();
      n.textContent.split(/(\s+)/).forEach((part) => {
        if (!part) return;
        if (!part.trim()) { parts.append(part); return; }
        const box = document.createElement('span');
        const word = document.createElement('span');
        box.className = 'hero__word';
        box.setAttribute('aria-hidden', 'true');
        word.textContent = part;
        box.append(word);
        boxes.push(box);
        parts.append(box);
      });
      n.replaceWith(parts);
    });
    walk(copy);
    h1.setAttribute('aria-label', h1.textContent.replace(/\s+/g, ' ').trim());
    h1.replaceChildren(...copy.childNodes);
    const lines = [];
    let top = null;
    boxes.forEach((box) => {
      const y = box.getBoundingClientRect().top;
      if (top === null || Math.abs(y - top) > 3) { lines.push([]); top = y; }
      lines[lines.length - 1].push(box.firstChild);
    });
    return { original, lines };
  };
  const fontsIn = Promise.race([document.fonts ? document.fonts.ready : Promise.resolve(), new Promise((r) => setTimeout(r, 250))]);
  fontsIn.then(() => {
    if (over) return;
    if (root.classList.contains('hero-late')) { over = true; setTimeout(shown, 1150); return; }
    words = splitWords();
    hero.classList.add('is-entering');
    const { lines } = words;
    const step = Math.min(80, 240 / Math.max(1, lines.length - 1));
    lines.forEach((line, i) => line.forEach((w) => anims.push(w.animate(
      [{ transform: 'translateY(calc(100% + .2em))' }, { transform: 'none' }],
      { duration: 700, delay: 80 + i * step, easing: ease, fill: 'both' }))));
    const after = 80 + (lines.length - 1) * step + 220;
    const rest = [hero.querySelector('.hero__chip'), hero.querySelector('.hero__lead'), ...hero.querySelectorAll('.btn-row > *'), hero.querySelector('.hero__proof'), hero.querySelector('.home-hero__facts')];
    rest.filter(Boolean).forEach((el, k) => anims.push(el.animate(
      [{ opacity: 0, transform: 'translateY(12px)' }, { opacity: 1, transform: 'none' }],
      { duration: 520, delay: after + Math.min(k, 6) * 60, easing: ease, fill: 'both' })));
    Promise.all([...anims.map((a) => a.finished), new Promise((r) => setTimeout(r, 1150))]).then(finish, finish);
  }).catch(finish);
  setTimeout(finish, 2400);
})();

// ------------------------------------------------------------------ the home page's render clip
// Muted and looping. The poster is the first picture: the clip's sources come without an address
// (data-src, layouts/home.html), and it gets one only once the page has loaded and the browser is idle,
// so the first view never includes the clip. On a phone, under reduced motion and when the visitor
// asks to save data (or is on a slow connection) it gets one only when the play button is pressed.
// It plays only while the hero is on the screen: it starts when the hero comes into view and rests
// while it is scrolled away. The round button pauses and plays it; a visitor's pause holds until they
// press play again. The browser picks the encode from the <source> types (AV1 first) and media queries.
(() => {
  const video = document.querySelector('[data-hero-video]');
  const btn = document.querySelector('[data-hero-pause]');
  if (!video || !btn) return;
  const icons = {
    pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor"/></svg>',
  };
  const show = (playing) => {
    btn.hidden = false;
    btn.setAttribute('aria-label', playing ? 'Pause the video' : 'Play the video');
    btn.innerHTML = playing ? icons.pause : icons.play;
  };
  let attached = false;
  const attach = () => {
    if (attached) return;
    attached = true;
    video.querySelectorAll('source[data-src]').forEach((s) => { s.src = s.dataset.src; });
    video.preload = 'auto';
    video.load();
  };
  let wanted = true, visible = false, watching = false;
  const play = () => { attach(); return video.play().then(() => show(true)).catch(() => { wanted = false; show(false); }); };
  const watch = () => {
    if (watching) return;
    watching = true;
    if (!('IntersectionObserver' in window)) { if (wanted) play(); return; }
    new IntersectionObserver((es) => {
      visible = es.some((e) => e.isIntersecting);
      if (visible && wanted && video.paused) play();
      else if (!visible && !video.paused) video.pause();
    }, { threshold: 0.15 }).observe(video.closest('.home-hero') || video);
  };
  btn.addEventListener('click', () => {
    wanted = !wanted;
    if (wanted) { play(); watch(); } else { video.pause(); show(false); }
  });
  const c = navigator.connection;
  const slow = c && (c.saveData || /(^|-)(2g|3g)$/.test(c.effectiveType || ''));
  const phone = window.matchMedia('(max-width: 639px)').matches;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || slow || phone) { wanted = false; show(false); return; }
  show(true);
  // after the load event, when the browser is idle, so the clip never competes with the page's own files
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 200));
  const start = () => idle(() => { if (wanted) attach(); watch(); }, { timeout: 2000 });
  if (document.readyState === 'complete') start();
  else addEventListener('load', start, { once: true });
})();

// ------------------------------------------------------------------ events (data/events.yaml)
// The build already left out what was over when the site was built; this checks again by the
// visitor's clock, so a page built days ago still shows the right next event.
// [data-ev-next]: show the first [data-ev] that has not ended, hide the block when none is left.
// [data-ev-next-list] (home page): hide every ended event, add the line for no dates when none is left.
// /events/: move ended events from the upcoming list to the past list (latest first), and add the same
// line when the upcoming list is empty. The line is not in the page while events are listed.
// [data-ev-local]: add the start time in the visitor's own time zone when it differs.
(() => {
  const now = Date.now();
  const over = (el) => Date.parse(el.dataset.evEnds) <= now;
  const noDates = (list) => {
    if (list.parentElement.querySelector('[data-ev-empty]')) return;
    const p = document.createElement('p');
    p.className = 'event-empty';
    p.dataset.evEmpty = '';
    p.append('No dates are set right now. New ones are announced in the ');
    const a = document.createElement('a');
    a.href = list.dataset.evNewsletter || '';
    a.textContent = 'newsletter';
    p.append(a, '.');
    list.after(p);
  };
  document.querySelectorAll('[data-ev-next]').forEach((box) => {
    const items = [...box.querySelectorAll('[data-ev]')];
    const next = items.find((el) => !over(el));
    items.forEach((el) => { el.hidden = el !== next; });
    if (!next) box.hidden = true;
  });
  document.querySelectorAll('[data-ev-next-list]').forEach((list) => {
    const items = [...list.querySelectorAll('[data-ev]')];
    items.forEach((el) => { el.hidden = over(el); });
    if (items.length && items.every((el) => el.hidden)) noDates(list);
  });
  const up = document.querySelector('[data-ev-upcoming]');
  const past = document.querySelector('[data-ev-past]');
  if (up && past) {
    const gone = [...up.querySelectorAll('[data-ev]')].filter(over);
    if (gone.length) {
      gone.forEach((el) => past.append(el));
      [...past.children].sort((a, b) => b.dataset.evStart - a.dataset.evStart).forEach((el) => past.append(el));
      const h = document.querySelector('[data-ev-past-h]');
      if (h) h.hidden = false;
      if (!up.children.length) noDates(up);
    }
  }
  document.querySelectorAll('[data-ev-local]').forEach((el) => {
    try {
      const t = new Date(el.dataset.evLocal);
      const opts = { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' };
      const mine = new Intl.DateTimeFormat(undefined, opts).format(t);
      const theirs = new Intl.DateTimeFormat(undefined, { ...opts, timeZone: el.dataset.evTz }).format(t);
      if (mine !== theirs) { el.textContent = `In your time zone: ${mine}`; el.hidden = false; }
    } catch (e) { /* an old browser without time zones: the event's own time stays */ }
  });
})();

// ------------------------------------------------------------------ videos (youtube / vimeo shortcodes)
// Nothing loads from YouTube or Vimeo until the visitor starts a video: then the privacy-enhanced
// player takes the place of the button. A click with a modifier key opens the video's own page.
// On a video-grid (the videos page) a card's video opens in a popup instead (.v-box): the player
// large on black, the card's tag, title and sentence under it, its chapters beside it as buttons that
// start the video at that time. In the card the chapters fold to one "n chapters" button. Closing the
// popup removes the player, which stops the video.
const vbox = (() => {
  const cards = document.querySelectorAll('.video-card');
  if (!cards.length || !window.HTMLDialogElement) return null;
  const d = document.createElement('dialog');
  d.className = 'v-box';
  d.setAttribute('aria-label', 'Video');
  d.innerHTML = '<div class="v-box__main"><div class="v-box__player"></div><div class="v-box__info"><div class="v-box__words"></div>'
    + '<form method="dialog"><button class="v-box__close" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></form></div></div><div class="v-box__chapters" hidden></div>';
  document.body.append(d);
  const player = d.querySelector('.v-box__player'), info = d.querySelector('.v-box__words'), side = d.querySelector('.v-box__chapters');
  let src = '', label = '';
  const chapters = new WeakMap();  // a card's chapters, taken out of the card
  const secs = (t) => t.split(':').reduce((n, x) => n * 60 + Number(x), 0);
  const play = (start) => {
    let u = src;
    if (start) u = /vimeo/.test(u) ? `${u}#t=${start}s` : `${u}&start=${start}`;
    const f = document.createElement('iframe');
    f.src = u; f.title = label;
    f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    player.replaceChildren(f);
  };
  d.addEventListener('close', () => { player.replaceChildren(); document.documentElement.classList.remove('v-box-open'); });
  d.addEventListener('click', (e) => {
    if (e.target === d) { d.close(); return; }
    const c = e.target.closest('.v-box__chapter');
    if (!c) return;
    side.querySelectorAll('.v-box__chapter').forEach((b) => b.setAttribute('aria-current', String(b === c)));
    play(Number(c.dataset.t));
  });
  const open = (card, start = 0) => {
    const box = card.querySelector('.video-embed');
    src = box.dataset.embed; label = box.dataset.embedTitle;
    info.replaceChildren();
    const tag = card.querySelector('.video-card__tag'), h = card.querySelector('h2, h3');
    if (tag) { const t = document.createElement('p'); t.className = 'v-box__tag'; t.textContent = tag.textContent; info.append(t); }
    if (h) { const t = document.createElement('h2'); t.className = 'v-box__title'; t.textContent = [...h.childNodes].filter((n) => !n.classList?.contains('heading-anchor')).map((n) => n.textContent).join('').trim(); info.append(t); }
    card.querySelectorAll(':scope > p:not(.video-card__tag)').forEach((p) => { const t = p.cloneNode(true); t.className = 'v-box__text'; info.append(t); });
    const rows = [...(chapters.get(card)?.querySelectorAll('li') || [])];
    side.hidden = !rows.length;
    side.replaceChildren();
    if (rows.length) {
      const hd = document.createElement('p'); hd.className = 'v-box__chapters-h'; hd.textContent = `${rows.length} chapters`;
      const ol = document.createElement('ol');
      rows.forEach((li) => {
        const t = li.querySelector('time').textContent, n = secs(t);
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'v-box__chapter'; b.dataset.t = n;
        b.setAttribute('aria-current', String(n === start));
        b.innerHTML = '<time></time><span></span>';
        b.firstChild.textContent = t; b.lastChild.textContent = li.querySelector('span').textContent;
        const item = document.createElement('li'); item.append(b); ol.append(item);
      });
      side.append(hd, ol);
    }
    d.classList.toggle('v-box--chapters', rows.length > 0);
    play(start);
    document.documentElement.classList.add('v-box-open');
    d.showModal();
    d.querySelector('.v-box__close').focus();
  };
  cards.forEach((card) => {
    const ch = card.querySelector('.chapters');
    if (!ch) return;
    const n = ch.querySelectorAll('li').length;
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'video-card__chapters';
    b.innerHTML = `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 4h10M3 8h10M3 12h6"/></svg>${n} chapters`;
    b.addEventListener('click', () => open(card));
    chapters.set(card, ch);
    ch.replaceWith(b);
  });
  return open;
})();

document.addEventListener('click', (e) => {
  const a = e.target.closest?.('.video-embed__start');
  if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
  const box = a.closest('.video-embed');
  e.preventDefault();
  const card = box.closest('.video-card');
  if (vbox && card) { vbox(card); return; }
  const f = document.createElement('iframe');
  f.src = box.dataset.embed;
  f.title = box.dataset.embedTitle;
  f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
  f.allowFullscreen = true;
  f.referrerPolicy = 'strict-origin-when-cross-origin';
  box.replaceChildren(f);
  box.classList.add('is-playing');
  f.focus();
});

// ------------------------------------------------------------------ table of contents
// The sticky contents on a desktop mark the section being read (the last heading above the top third).
(() => {
  const toc = document.querySelector('[data-toc]');
  if (!toc) return;
  const links = new Map([...toc.querySelectorAll('a[href^="#"]')].filter((a) => a.hash.length > 1).map((a) => [decodeURIComponent(a.hash.slice(1)), a]));
  const heads = [...links.keys()].map((id) => document.getElementById(id)).filter(Boolean);
  if (!heads.length) return;
  let current = null, queued = false;
  const update = () => {
    queued = false;
    const line = window.innerHeight / 3;
    let best = heads[0];
    for (const h of heads) { if (h.getBoundingClientRect().top <= line) best = h; else break; }
    if (best.id === current) return;
    links.get(current)?.removeAttribute('aria-current');
    current = best.id;
    const a = links.get(current);
    a.setAttribute('aria-current', 'location');
    // keep the marked entry in view inside a long list
    const t = a.offsetTop, box = toc;
    if (t < box.scrollTop + 40 || t > box.scrollTop + box.clientHeight - 60) box.scrollTop = t - box.clientHeight / 2;
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  update();
})();

// ------------------------------------------------------------------ the old forum's addresses
// /?forum=… reached the WordPress forum; a static site serves the home page for it, so say what happened.
(() => {
  const note = document.querySelector('main.home [data-forum-note]');
  if (note && /[?&](forum|topic)=/.test(location.search)) note.hidden = false;
})();

// ------------------------------------------------------------------ links into a fold
// A link to a section that is folded (#releases on /download/, or anything inside a fold) opens the
// fold, so the visitor lands on what the link promised: the fold the address points into, or the one
// right after the heading it names.
(() => {
  const open = () => {
    const id = decodeURIComponent(location.hash.slice(1));
    const target = id && document.getElementById(id);
    if (!target) return;
    let fold = target.closest('details');
    if (!fold) {
      const next = target.nextElementSibling;
      if (next && next.matches('details')) fold = next;
    }
    if (!fold || fold.open) return;
    for (let d = fold; d; d = d.parentElement?.closest('details')) d.open = true;
    target.scrollIntoView();
  };
  open();
  addEventListener('hashchange', open);
})();

// ------------------------------------------------------------------ the citation snippet
// The home page citation tabs select a format and update the shared clipboard controller's target.
document.querySelectorAll('.cite-snip').forEach((box) => {
  const bar = box.querySelector('.cite-snip__bar');
  if (!bar) return;
  bar.hidden = false;
  const tabs = [...box.querySelectorAll('.cite-snip__tab')];
  const texts = [...box.querySelectorAll('[data-fmt]')];
  tabs.forEach((tab) => tab.addEventListener('click', () => {
    tabs.forEach((t) => t.setAttribute('aria-pressed', String(t === tab)));
    texts.forEach((t) => { t.hidden = t.dataset.fmt !== tab.dataset.show; });
    box.querySelector('[data-copy]').dataset.copy = texts.find((t) => !t.hidden).id;
  }));

});

// The news rail follows the reading position; stories remain visible and stationary.
document.querySelectorAll('.news-timeline').forEach((timeline) => {
  const stories = [...timeline.querySelectorAll('.news-story')];
  if (!stories.length) return;
  let queued = false;
  const update = () => {
    queued = false;
    const navHeight = document.querySelector('.nav')?.getBoundingClientRect().bottom || 0;
    const readingLine = navHeight + Math.min(180, (innerHeight - navHeight) * .25);
    const boxes = stories.map(story => story.getBoundingClientRect());
    const top = boxes[0].top + 9;
    const length = Math.max(1, boxes[boxes.length - 1].top - boxes[0].top);
    const progress = Math.max(0, Math.min(1, (readingLine - top) / length));
    timeline.style.setProperty('--rail-top', `${top - timeline.getBoundingClientRect().top}px`);
    timeline.style.setProperty('--rail-length', `${length}px`);
    timeline.style.setProperty('--rail-progress', progress.toFixed(5));
    let current = 0;
    boxes.forEach((box, i) => { if (box.top + 9 <= readingLine) current = i; });
    stories.forEach((story, i) => {
      story.classList.toggle('is-current', i === current);
      story.classList.toggle('is-passed', i < current);
    });
    timeline.classList.add('is-tracked');
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  new ResizeObserver(queue).observe(timeline);
  update();
});

// The countdown at the end of an event's meta line (events/card.html, home.html): "today", "tomorrow",
// "in 6 days", "in 3 months", by the visitor's clock; it stays hidden once the event has started.
document.querySelectorAll('[data-ev-countdown]').forEach((chip) => {
  const start = Number(chip.dataset.evCountdown) * 1000;
  const day = (t) => { const d = new Date(t); d.setHours(0, 0, 0, 0); return d.getTime(); };
  const days = Math.round((day(start) - day(Date.now())) / 864e5);
  if (start <= Date.now() && days < 0) return;
  chip.textContent = days <= 0 ? 'today' : days === 1 ? 'tomorrow' : days < 45 ? `in ${days} days` : `in ${Math.round(days / 30.4)} months`;
  chip.hidden = false;
});

// Paper rows (Publications): a year is written once, on its first row.
document.querySelectorAll('.paper-rows').forEach((list) => {
  let last = '';
  list.querySelectorAll('.paper-row__year').forEach((y) => { if (y.textContent === last) y.classList.add('is-repeat'); else last = y.textContent; });
});

// {{< capabilities >}} (Features): a click on a capability's name chooses it: its sentence and links
// open under the name and its picture shows on the stage. The address takes its id, so the chosen one can
// be linked; a link to a capability (from the home page, the search) chooses it too.
document.querySelectorAll('[data-cap-show]').forEach((show) => {
  const items = [...show.querySelectorAll('.capability')];
  const figs = [...show.querySelectorAll('[data-cap-fig]')];
  if (items.length < 2) return;
  const open = (item) => {
    items.forEach((it) => {
      it.classList.toggle('is-active', it === item);
      it.querySelector('h3 > button').setAttribute('aria-expanded', String(it === item));
    });
    figs.forEach((f) => f.classList.toggle('is-active', f.dataset.capFig === item.id));
  };
  items.forEach((it) => it.querySelector('h3 > button').addEventListener('click', () => {
    open(it);
    history.replaceState(null, '', '#' + it.id);
  }));
  const fromHash = () => {
    const it = items.find((x) => '#' + x.id === location.hash);
    if (!it) return;
    open(it);
    if (matchMedia('(min-width: 1024px)').matches) show.scrollIntoView();
  };
  addEventListener('hashchange', fromHash);
  fromHash();
});

// The gallery (layouts/gallery/list.html): the pills show one section (a kind of picture) or all; a click on a
// picture opens the lightbox with the picture larger and its words (its .g-item__info), arrows and the
// arrow keys step through the pictures shown; #fig-… or #covers in the address opens or filters at once.
(() => {
  const walls = document.querySelectorAll('[data-gallery]');
  const box = document.querySelector('.g-box');
  if (!walls.length) return;
  const items = [...document.querySelectorAll('[data-gallery] .g-item')];
  const secs = document.querySelectorAll('.g-sec');
  const pills = document.querySelector('.g-pills');
  const show = (kind) => {
    pills?.querySelectorAll('button').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.show === kind)));
    items.forEach((it) => { it.hidden = kind !== 'all' && it.dataset.kind !== kind; });
    secs.forEach((sec) => { sec.hidden = kind !== 'all' && sec.dataset.kind !== kind; });
  };
  if (pills) { pills.hidden = false; pills.addEventListener('click', (e) => { const b = e.target.closest('button'); if (b) show(b.dataset.show); }); }
  if (!box || !box.showModal) return;
  const img = box.querySelector('.g-box__img'), info = box.querySelector('.g-box__info');
  let cur = -1;
  const visible = () => items.filter((it) => !it.hidden);
  const open = (it) => {
    const a = it.querySelector('.g-item__img');
    img.src = a.href; img.alt = a.querySelector('img').alt;
    info.innerHTML = it.querySelector('.g-item__info').innerHTML;
    cur = visible().indexOf(it);
    if (!box.open) box.showModal();
  };
  const step = (d) => { const v = visible(); if (v.length) open(v[(cur + d + v.length) % v.length]); };
  items.forEach((it) => it.querySelector('.g-item__img').addEventListener('click', (e) => { e.preventDefault(); open(it); }));
  box.querySelector('.g-box__nav--prev').addEventListener('click', () => step(-1));
  box.querySelector('.g-box__nav--next').addEventListener('click', () => step(1));
  box.addEventListener('keydown', (e) => { if (e.key === 'ArrowLeft') step(-1); if (e.key === 'ArrowRight') step(1); });
  box.addEventListener('click', (e) => { if (e.target === box) box.close(); });
  const hash = () => {
    if (location.hash === '#covers') show('cover');
    else if (location.hash === '#renders') show('render');
    const it = location.hash.startsWith('#fig-') && document.getElementById(location.hash.slice(1));
    if (it) open(it);
  };
  hash(); addEventListener('hashchange', hash);
})();

// ------------------------------------------------------------------ light and dark
// head.html sets html[data-theme] before the first paint: the reader's choice (localStorage "theme"),
// else the system's. The header's button flips it and keeps the choice; without a choice the page
// follows the system when that changes.
(() => {
  const root = document.documentElement;
  const buttons = document.querySelectorAll('[data-theme-toggle]');
  const label = () => {
    const words = root.dataset.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    buttons.forEach((b) => { b.setAttribute('aria-label', words); b.title = words; });
  };
  const set = (t) => { root.dataset.theme = t; label(); };
  buttons.forEach((b) => b.addEventListener('click', () => {
    const t = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('theme', t); } catch (e) { /* private mode: the choice lasts this page */ }
    set(t);
  }));
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    let saved = null;
    try { saved = localStorage.getItem('theme'); } catch (e) { /* none */ }
    if (!saved) set(e.matches ? 'dark' : 'light');
  });
  label();
})();
