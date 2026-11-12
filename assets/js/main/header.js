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
