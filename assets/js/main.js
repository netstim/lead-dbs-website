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
  wide.addEventListener('change', (e) => { if (e.matches) setOpen(false); });
  // A word with pages gets a chevron button beside it (the disclosure pattern with top-level links): the
  // word stays a link to its group's page, the button opens and closes the word's panel and says
  // whether it is open (aria-expanded). In the sheet it opens the pages under the word. On a desktop the
  // panel also opens on hover (assets/css/site.css); from the keyboard, Tab goes from word to word, Enter
  // or Space on the chevron opens the panel and the next Tab enters it, Arrow Down on the word or the
  // chevron opens it and moves to its first link, Arrow Up and Down, Home and End move inside it, and
  // Escape (or the focus leaving the word) closes it, the focus back on the chevron.
  const items = [];
  const close = (item) => { item.classList.remove('is-expanded'); item.sync(); };
  // On a desktop the panels share one ground: a band under the header (.nav__band) that stays while the
  // pointer moves from word to word and only eases to the height of the panel now shown; the panels
  // themselves are clear and cross-fade on it (assets/css/site.css). It opens without easing its height.
  const band = document.createElement('div');
  band.className = 'nav__band';
  band.setAttribute('aria-hidden', 'true');
  nav.append(band);
  band.sync = () => {
    const shown = wide.matches && items.find((i) => i.querySelector('.nav__expand')?.getAttribute('aria-expanded') === 'true');
    const panel = shown && shown.querySelector('.nav__menu');
    if (panel) {
      if (!nav.classList.contains('band-open')) {
        nav.classList.add('band-instant');
        requestAnimationFrame(() => requestAnimationFrame(() => nav.classList.remove('band-instant')));
      }
      band.style.height = `${panel.offsetHeight}px`;
    }
    nav.classList.toggle('band-open', !!panel);
  };
  addEventListener('resize', () => band.sync());
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
    item.sync = () => {
      const open = item.classList.contains('is-expanded')
        || (wide.matches && !item.classList.contains('is-dismissed') && item.classList.contains('is-hovered'));
      btn.setAttribute('aria-expanded', String(open));
      band.sync();
    };
    const links = () => [...panel.querySelectorAll('a[href]')].filter((a) => a.getClientRects().length);
    const openTo = (i) => {
      if (wide.matches) items.forEach((other) => { if (other !== item) close(other); });
      item.classList.remove('is-dismissed');
      item.classList.add('is-expanded');
      item.sync();
      if (i !== undefined) requestAnimationFrame(() => { const l = links(); l[i < 0 ? l.length - 1 : i]?.focus(); });
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
    wide.addEventListener('change', () => { close(item); item.classList.remove('is-dismissed'); });
    item.sync();
  });
  // a click elsewhere closes an open desktop panel
  document.addEventListener('click', (e) => {
    if (wide.matches) items.forEach((item) => { if (!item.contains(e.target)) close(item); });
  });
  // Hover on a desktop, for the header as a whole: a panel opens once the pointer has rested 150ms on its
  // word (one passing over opens nothing); while a panel is open, the next word's opens at once. The
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
      i.sync();
    });
  };
  const later = (item, ms) => { clearTimeout(timer); timer = setTimeout(() => hover(item), ms); };
  nav.addEventListener('pointerover', (e) => {
    if (!wide.matches || e.pointerType === 'touch' || nav.classList.contains('is-open')) return;
    const t = e.target;
    if (t.closest('.nav__menu')) { clearTimeout(timer); return; }
    const item = t.closest('.nav__links > .nav__item');
    if (item && items.includes(item)) { if (item !== hovered) later(item, hovered ? 0 : 150); else clearTimeout(timer); return; }
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

// ------------------------------------------------------------------ the footer on a phone
// Below 640px each column of the footer folds to its heading, with a chevron button that opens its links
// (assets/css/site.css, "footer"). Without script, and from 640px up, every column is open.
(() => {
  const footer = document.querySelector('.footer');
  const cols = footer ? [...footer.querySelectorAll('.footer__col')] : [];
  if (!cols.length) return;
  cols.forEach((col, i) => {
    const h = col.querySelector('.footer__h');
    const list = col.querySelector('ul');
    if (!h || !list) return;
    if (!list.id) list.id = `footer-list-${i + 1}`;
    const btn = document.createElement('button');
    btn.className = 'footer__expand';
    btn.type = 'button';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', list.id);
    btn.setAttribute('aria-label', `${h.textContent.trim()}: show the links`);
    btn.innerHTML = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 6l4 4 4-4" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
    h.after(btn);
    btn.addEventListener('click', () => {
      const open = !col.classList.contains('is-expanded');
      col.classList.toggle('is-expanded', open);
      btn.setAttribute('aria-expanded', String(open));
    });
  });
  footer.classList.add('is-foldable');
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
    const line = nav.getBoundingClientRect().bottom;
    nav.classList.toggle('is-dark', grounds.some((g) => {
      const r = g.getBoundingClientRect();
      return r.height > 0 && r.top < line + 1 && r.bottom > line;
    }));
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
    const rest = [hero.querySelector('.hero__lead'), ...hero.querySelectorAll('.btn-row > *'), hero.querySelector('.hero__proof'), hero.querySelector('.home-hero__facts')];
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
document.addEventListener('click', (e) => {
  const a = e.target.closest?.('.video-embed__start');
  if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
  const box = a.closest('.video-embed');
  e.preventDefault();
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
// The home page's citation (layouts/home.html): two tabs show the reference or its BibTeX; Copy puts the
// shown one on the clipboard and says so for two seconds. Without the clipboard the bar stays hidden.
document.querySelectorAll('.cite-snip').forEach((box) => {
  const bar = box.querySelector('.cite-snip__bar');
  if (!bar || !navigator.clipboard?.writeText) return;
  bar.hidden = false;
  const tabs = [...box.querySelectorAll('.cite-snip__tab')];
  const texts = [...box.querySelectorAll('[data-fmt]')];
  tabs.forEach((tab) => tab.addEventListener('click', () => {
    tabs.forEach((t) => t.setAttribute('aria-pressed', String(t === tab)));
    texts.forEach((t) => { t.hidden = t.dataset.fmt !== tab.dataset.show; });
  }));
  const copy = box.querySelector('.cite-snip__copy');
  const label = copy.querySelector('span');
  copy.addEventListener('click', async () => {
    const shown = texts.find((t) => !t.hidden);
    try { await navigator.clipboard.writeText(shown.innerText.trim()); label.textContent = 'Copied'; }
    catch { label.textContent = 'Copy failed'; }
    setTimeout(() => { label.textContent = 'Copy'; }, 2000);
  });
});

// Researcher testimonials: one quote at a time, advancing every 8 s with a crossfade; it holds while the
// pointer or focus is on it, while it is out of view or the tab hidden, and with reduced motion.
document.querySelectorAll('.voices__carousel').forEach((carousel) => {
  const slides = [...carousel.querySelectorAll('.voices__slide')];
  const controls = carousel.querySelector('.voices__controls');
  if (slides.length < 2 || !controls) return;
  const count = carousel.querySelector('.voices__count');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)');
  let index = 0, timer, visible = false, hovered = false, focused = false, paused = reduce.matches;
  carousel.classList.add('is-carousel');
  carousel.setAttribute('aria-roledescription', 'carousel');
  const show = (next) => {
    index = (next + slides.length) % slides.length;
    slides.forEach((slide, i) => {
      const active = i === index;
      slide.classList.toggle('is-active', active);
      slide.setAttribute('aria-hidden', String(!active));
      slide.inert = !active;
    });
    count.textContent = `${index + 1} / ${slides.length}`;
  };
  const schedule = () => {
    clearTimeout(timer);
    const stopped = paused || hovered || focused || !visible || document.hidden;
    count.setAttribute('aria-live', stopped ? 'polite' : 'off');
    if (!stopped) timer = setTimeout(() => { show(index + 1); schedule(); }, 8000);
  };
  const navigate = (step) => { show(index + step); schedule(); };
  controls.hidden = false;
  carousel.querySelector('.voices__prev').addEventListener('click', () => navigate(-1));
  carousel.querySelector('.voices__next').addEventListener('click', () => navigate(1));
  carousel.addEventListener('mouseenter', () => { hovered = true; schedule(); });
  carousel.addEventListener('mouseleave', () => { hovered = false; schedule(); });
  carousel.addEventListener('focusin', () => { focused = true; schedule(); });
  carousel.addEventListener('focusout', (event) => {
    if (!carousel.contains(event.relatedTarget)) { focused = false; schedule(); }
  });
  controls.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      navigate(event.key === 'ArrowRight' ? 1 : -1);
    }
  });
  document.addEventListener('visibilitychange', schedule);
  reduce.addEventListener('change', () => { paused = reduce.matches; schedule(); });
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; schedule(); }, { threshold: .5 }).observe(carousel);
  show(0);
  schedule();
});

