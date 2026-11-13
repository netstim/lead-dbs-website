// ------------------------------------------------------------------ the home page's endless grid of figures
// Made with Lead-DBS (layouts/home.html): every figure of data/gallery.yaml in masonry columns that repeat
// in both directions, so the grid never ends. Five columns make one period across, each column its own
// period down (the figures in it, a share of its height lower than its neighbour). Only the tiles in
// the frame are in the page, placed with transforms; leaving tiles are kept for reuse. Nothing is built
// (no picture fetched) until the section comes near the screen. It drifts slowly until it is dragged
// (mouse: both ways; a finger: sideways, so the page still scrolls), keeps its momentum after a throw,
// and the arrow keys move it while it has focus. A click that did not drag opens the figure on /gallery/.
// Under reduced motion it does not drift or glide, but can still be dragged.
(() => {
  const grid = document.querySelector('[data-made-grid]');
  const plane = grid?.querySelector('.made-grid__plane');
  if (!plane) return;
  let figs = [];
  try { figs = JSON.parse(grid.querySelector('[data-made-figs]').textContent); } catch (e) { return; }
  const n = figs.length;
  if (!n) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const K = 5, PER = Math.max(2, Math.ceil((2 * n) / K)), DRAG = 6;
  let W = 0, G = 0, cols = [];
  const layout = () => {
    const phone = innerWidth < 640;
    W = phone ? 140 : 172; G = phone ? 8 : 12;
    cols = Array.from({ length: K }, (_, k) => {
      const items = [];
      let y = 0;
      for (let j = 0; j < PER; j++) {
        const f = figs[(k * 2 + j * 3) % n];
        const h = Math.round(W / Math.min(1.6, Math.max(0.72, f.ar)));
        items.push({ f, y, h });
        y += h + G;
      }
      return { items, period: y, shift: [0, 0.42, 0.14, 0.68, 0.3][k] * y };
    });
  };
  const live = new Map(), pool = [];
  const make = () => {
    const a = document.createElement('a');
    a.className = 'made-tile';
    a.tabIndex = -1;
    a.draggable = false;
    // no loading="lazy": a tile exists only while it is in the frame, and the frame only once it is near
    a.innerHTML = '<img alt="" decoding="async" draggable="false">';
    return a;
  };
  const fill = (el, it) => {
    const img = el.firstChild;
    el.href = it.f.href;
    el.style.width = `${W}px`; el.style.height = `${it.h}px`;
    if (img.dataset.src !== it.f.src) { img.dataset.src = it.f.src; img.sizes = `${W}px`; img.srcset = it.f.srcset; img.src = it.f.src; }
    img.alt = it.f.alt;
  };
  let ox = 0, oy = 0, vx = 0, vy = 0;
  const draw = () => {
    const fw = grid.clientWidth, fh = grid.clientHeight, step = W + G, seen = new Set();
    for (let i = Math.floor(-ox / step) - 1; i <= Math.floor((fw - ox) / step); i++) {
      const c = cols[((i % K) + K) % K], x = Math.round(i * step + ox), base = oy + c.shift;
      for (let r = Math.floor(-base / c.period) - 1; r <= Math.floor((fh - base) / c.period); r++) {
        c.items.forEach((it, j) => {
          const y = Math.round(base + r * c.period + it.y);
          if (y + it.h < 0 || y > fh) return;
          const key = `${i}:${r}:${j}`;
          let el = live.get(key);
          if (!el) { el = pool.pop() || make(); fill(el, it); plane.append(el); live.set(key, el); }
          el.style.transform = `translate3d(${x}px, ${y}px, 0)`;
          seen.add(key);
        });
      }
    }
    live.forEach((el, key) => { if (!seen.has(key)) { el.remove(); live.delete(key); pool.push(el); } });
  };

  let raf = 0, last = 0, near = false, built = false, dragging = false, drifting = !still.matches;
  const frame = (t) => {
    raf = 0;
    const dt = last ? Math.min(48, t - last) : 16;
    last = t;
    if (!dragging) {
      if (Math.abs(vx) + Math.abs(vy) > 0.004) {
        ox += vx * dt; oy += vy * dt;
        const k = 0.995 ** dt;
        vx *= k; vy *= k;
      } else {
        vx = vy = 0;
        if (drifting) { ox -= 0.012 * dt; oy -= 0.007 * dt; }
      }
    }
    draw();
    if (near && !document.hidden && (dragging || drifting || vx || vy)) raf = requestAnimationFrame(frame);
    else last = 0;
  };
  const kick = () => { if (built && !raf) raf = requestAnimationFrame(frame); };
  const build = () => { built = true; layout(); draw(); kick(); };

  let start = null, moved = 0, px = 0, py = 0, pt = 0;
  const end = (e) => {
    if (!start || e.pointerId !== start.id) return;
    start = null;
    if (!dragging) return;
    dragging = false;
    grid.classList.remove('is-dragging');
    if (e.type === 'pointercancel' || e.timeStamp - pt > 80 || still.matches) vx = vy = 0;
    kick();
  };
  grid.addEventListener('pointerdown', (e) => {
    if (e.button !== 0 || !built) return;
    start = { x: e.clientX, y: e.clientY, id: e.pointerId, finger: e.pointerType === 'touch' };
    px = e.clientX; py = e.clientY; pt = e.timeStamp; moved = 0;
    vx = vy = 0;
  });
  grid.addEventListener('pointermove', (e) => {
    if (!start || e.pointerId !== start.id) return;
    if (!e.buttons) { end(e); return; }
    const dx = e.clientX - px, dy = start.finger ? 0 : e.clientY - py;
    px = e.clientX; py = e.clientY;
    moved = Math.max(moved, Math.hypot(e.clientX - start.x, start.finger ? 0 : e.clientY - start.y));
    if (!dragging) {
      if (moved < DRAG) return;
      dragging = true; drifting = false;
      grid.classList.add('is-dragging');
      grid.setPointerCapture(e.pointerId);
    }
    ox += dx; oy += dy;
    const dt = Math.max(1, e.timeStamp - pt);
    pt = e.timeStamp;
    const cap = (v) => Math.max(-3, Math.min(3, v));
    vx = cap(0.8 * (dx / dt) + 0.2 * vx); vy = cap(0.8 * (dy / dt) + 0.2 * vy);
    kick();
  });
  grid.addEventListener('pointerup', end);
  grid.addEventListener('pointercancel', end);
  grid.addEventListener('lostpointercapture', end);
  // a drag is not a click
  grid.addEventListener('click', (e) => { if (moved >= DRAG) { e.preventDefault(); e.stopPropagation(); } }, true);
  grid.addEventListener('dragstart', (e) => e.preventDefault());
  grid.addEventListener('keydown', (e) => {
    const d = { ArrowLeft: [1, 0], ArrowRight: [-1, 0], ArrowUp: [0, 1], ArrowDown: [0, -1] }[e.key];
    if (!d || !built) return;
    e.preventDefault();
    drifting = false;
    if (still.matches) { ox += d[0] * 160; oy += d[1] * 160; draw(); return; }
    vx = d[0] * 1.1; vy = d[1] * 1.1;
    kick();
  });
  still.addEventListener('change', () => { if (still.matches) { drifting = false; vx = vy = 0; } });
  let resized = 0;
  addEventListener('resize', () => {
    if (!built) return;
    cancelAnimationFrame(resized);
    resized = requestAnimationFrame(() => { live.forEach((el) => { el.remove(); pool.push(el); }); live.clear(); layout(); draw(); });
  });
  document.addEventListener('visibilitychange', kick);
  if (!('IntersectionObserver' in window)) { near = true; build(); return; }
  new IntersectionObserver((es) => {
    near = es.some((e) => e.isIntersecting);
    if (near && !built) build(); else kick();
  }, { rootMargin: '600px 0px' }).observe(grid);
})();

// ------------------------------------------------------------------ the home page's fan of covers
// Seven journal covers fanned out like a hand of cards (layouts/home.html): one lifts after another, slowly,
// its journal and date in the caption under the fan. A pointer on a card lifts that one, and the fan holds
// while the pointer or the focus is on it, or while it is off the screen. Under reduced motion it stands.
(() => {
  const fan = document.querySelector('[data-made-fan]');
  const cards = fan ? [...fan.querySelectorAll('.made-fan__card')] : [];
  const n = cards.length;
  if (!n) return;
  const cap = fan.querySelector('.made-fan__cap');
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  let cur = cards.findIndex((c) => c.classList.contains('is-up'));
  let held = false, focused = false, seen = false, timer = 0;
  const up = (k) => {
    if (k === cur) return;
    cur = k;
    cards.forEach((c, i) => c.classList.toggle('is-up', i === k));
    if (!cap) return;
    cap.classList.add('is-changing');
    clearTimeout(timer);
    timer = setTimeout(() => {
      cap.querySelector('[data-made-journal]').textContent = cards[k].dataset.journal;
      cap.querySelector('[data-made-date]').textContent = cards[k].dataset.date;
      cap.classList.remove('is-changing');
    }, still.matches ? 0 : 220);
  };
  cards.forEach((c, k) => c.addEventListener('pointerenter', () => up(k)));
  fan.addEventListener('pointerenter', () => { held = true; });
  fan.addEventListener('pointerleave', () => { held = false; });
  fan.addEventListener('focusin', () => { focused = true; });
  fan.addEventListener('focusout', () => { focused = false; });
  if ('IntersectionObserver' in window) new IntersectionObserver((es) => { seen = es.some((e) => e.isIntersecting); }).observe(fan);
  else seen = true;
  setInterval(() => {
    if (!still.matches && seen && !held && !focused && !document.hidden) up((cur + n - 1) % n);
  }, 3600);
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
    const rest = [hero.querySelector('.hero__chip'), hero.querySelector('.home-chip'), hero.querySelector('.hero__lead'), ...hero.querySelectorAll('.btn-row > *'), hero.querySelector('.hero__proof'), hero.querySelector('.home-hero__facts')];
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

// ------------------------------------------------------------------ the quotes on a phone
// There the two rows stand still and the quotes are one row of cards that scrolls sideways
// (assets/css/phone-home.css): while it scrolls it is a tab stop of its own, so the arrow keys move it.
(() => {
  const drift = document.querySelector('.drift');
  if (!drift) return;
  const update = () => {
    if (drift.scrollWidth > drift.clientWidth + 4) drift.tabIndex = 0; else drift.removeAttribute('tabindex');
  };
  addEventListener('resize', update);
  update();
})();

// ------------------------------------------------------------------ the home page's drifting quotes
// The round button beside "All quotes" holds both rows until it is pressed again (hover holds them only
// while the pointer rests). Under reduced motion the rows stand anyway, so the button stays hidden.
(() => {
  const btn = document.querySelector('[data-drift-pause]');
  const drift = document.querySelector('.drift');
  if (!btn || !drift || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const icons = {
    pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
    play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor"/></svg>',
  };
  btn.hidden = false;
  btn.addEventListener('click', () => {
    const held = drift.classList.toggle('is-held');
    btn.innerHTML = held ? icons.play : icons.pause;
    btn.setAttribute('aria-label', held ? 'Play the quotes' : 'Pause the quotes');
  });
})();

// ------------------------------------------------------------------ the home page's globe: its script
// The globe (assets/js/globe.js with d3 and topojson, about 70 KB) is not needed until its section is
// near: its script is added when the section comes within 800 px of the screen, the distance at which
// globe.js then fetches the map (layouts/home.html, data-globe-src and data-globe-integrity).
(() => {
  const sec = document.getElementById('worldwide');
  const src = sec?.dataset.globeSrc;
  if (!src || !('IntersectionObserver' in window)) return;
  const io = new IntersectionObserver((es) => {
    if (!es.some((e) => e.isIntersecting)) return;
    io.disconnect();
    const s = document.createElement('script');
    s.src = src;
    s.integrity = sec.dataset.globeIntegrity;
    document.head.append(s);
  }, { rootMargin: '800px 0px' });
  io.observe(sec);
})();
