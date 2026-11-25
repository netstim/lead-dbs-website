import { showPlayState } from '../lib/play-state.js';

// ------------------------------------------------------------------ the home page's row of news and events
(() => {
  const row = document.querySelector('[data-drag-row]');
  if (!row) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  let start = null, dragged = false, v = 0, lx = 0, lt = 0, settle = 0;
  const done = () => { clearTimeout(settle); row.classList.remove('is-dragging'); };
  row.addEventListener('pointerdown', (e) => {
    dragged = false;
    if (e.pointerType !== 'mouse' || e.button !== 0 || row.scrollWidth <= row.clientWidth + 1) return;
    start = { x: e.clientX, left: row.scrollLeft, id: e.pointerId };
    v = 0; lx = e.clientX; lt = e.timeStamp;
  });
  row.addEventListener('pointermove', (e) => {
    if (!start || e.pointerId !== start.id) return;
    if (!e.buttons) { start = null; return; }
    const dx = e.clientX - start.x;
    if (!dragged) {
      if (Math.abs(dx) < 6) return;
      dragged = true; done();
      row.classList.add('is-dragging');
      row.setPointerCapture(e.pointerId);
    }
    const dt = Math.max(1, e.timeStamp - lt);
    v = 0.7 * ((e.clientX - lx) / dt) + 0.3 * v;
    lx = e.clientX; lt = e.timeStamp;
    row.scrollLeft = start.left - dx;
  });
  const end = (e) => {
    if (!start || e.pointerId !== start.id) return;
    start = null;
    if (!dragged) return;
    if (e.timeStamp - lt > 80) v = 0;
    const box = row.getBoundingClientRect();
    const pad = parseFloat(getComputedStyle(row).scrollPaddingLeft) || 0;
    const max = row.scrollWidth - row.clientWidth;
    const aim = row.scrollLeft - v * 250;
    let to = row.scrollLeft, best = Infinity;
    [...row.children].forEach((c) => {
      if (c.hidden) return;
      const x = Math.min(max, Math.max(0, row.scrollLeft + c.getBoundingClientRect().left - box.left - pad - row.clientLeft));
      if (Math.abs(x - aim) < best) { best = Math.abs(x - aim); to = x; }
    });
    row.scrollTo({ left: to, behavior: still.matches ? 'auto' : 'smooth' });
    row.addEventListener('scrollend', done, { once: true });
    settle = setTimeout(done, 700);
  };
  row.addEventListener('pointerup', end);
  row.addEventListener('pointercancel', end);
  row.addEventListener('lostpointercapture', end);
  row.addEventListener('click', (e) => { if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; } }, true);
  row.addEventListener('dragstart', (e) => e.preventDefault());
})();

// ------------------------------------------------------------------ the home page's hero: its entrance
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
  if (root.classList.contains('hero-late')) { setTimeout(shown, 400); return; }

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
    if (root.classList.contains('hero-late')) { over = true; setTimeout(shown, 400); return; }
    words = splitWords();
    hero.classList.add('is-entering');
    const { lines } = words;
    const step = Math.min(50, 100 / Math.max(1, lines.length - 1));
    lines.forEach((line, i) => line.forEach((w) => anims.push(w.animate(
      [{ transform: 'translateY(calc(100% + .2em))' }, { transform: 'none' }],
      { duration: 380, delay: i * step, easing: ease, fill: 'both' }))));
    Promise.all(anims.map((a) => a.finished)).then(finish, finish);
  }).catch(finish);
  setTimeout(finish, 1200);
})();

// ------------------------------------------------------------------ the home page's render clip
(() => {
  const video = document.querySelector('[data-hero-video]');
  const btn = document.querySelector('[data-hero-pause]');
  if (!video || !btn) return;
  const show = (playing) => {
    btn.hidden = false;
    showPlayState(btn, playing, 'the video');
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
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 200));
  const start = () => idle(() => { if (wanted) attach(); watch(); }, { timeout: 2000 });
  if (document.readyState === 'complete') start();
  else addEventListener('load', start, { once: true });
})();

// ------------------------------------------------------------------ the home page's horizontal gallery ribbon
// Full-width uncropped strip of published figures (layouts/home.html): gently glides sideways while in
// view (looping seamlessly), pauses on hover/focus/drag or via the pause button, supports native swipe,
// trackpad scroll, mouse click-drag with inertia, and prev/next step buttons.
(() => {
  const strip = document.querySelector('[data-made-strip]');
  const track = strip?.querySelector('.made-strip__track');
  if (!strip || !track || track.children.length < 2) return;
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  const controls = document.querySelector('[data-made-controls]');
  const pauseBtn = document.querySelector('[data-made-strip-pause]');
  const prevBtn = document.querySelector('[data-made-prev]');
  const nextBtn = document.querySelector('[data-made-next]');
  if (controls) controls.hidden = false;

  // duplicate the figures once (hidden from screen readers/tab) so the ribbon loops seamlessly
  const originals = [...track.children];
  const clones = originals.map((li) => {
    const c = li.cloneNode(true);
    c.setAttribute('aria-hidden', 'true');
    c.querySelectorAll('a').forEach((a) => { a.tabIndex = -1; });
    return c;
  });
  track.append(...clones);

  const loopWidth = () => {
    const first = originals[0], firstClone = clones[0];
    return first && firstClone ? firstClone.offsetLeft - first.offsetLeft : 0;
  };
  const wrap = () => {
    const w = loopWidth();
    if (!w) return;
    if (strip.scrollLeft >= w) strip.scrollLeft -= w;
    else if (strip.scrollLeft < 0) strip.scrollLeft += w;
  };

  let drifting = !still.matches, held = false, near = false, dragging = false, stepping = false;
  let acc = 0, last = 0, raf = 0, stepTimer = 0;
  const setDrifting = (on) => {
    drifting = on;
    if (pauseBtn) showPlayState(pauseBtn, on, 'the gallery');
  };
  if (pauseBtn) {
    pauseBtn.hidden = still.matches;
    showPlayState(pauseBtn, drifting, 'the gallery');
    pauseBtn.addEventListener('click', () => { setDrifting(!drifting); kick(); });
  }

  const tick = (t) => {
    raf = 0;
    const dt = last ? Math.min(48, t - last) : 16;
    last = t;
    if (near && !document.hidden && drifting && !held && !dragging && !stepping) {
      acc += dt * 0.032; // ~32 px/sec calm gallery glide
      const dx = Math.floor(acc);
      if (dx >= 1) {
        acc -= dx;
        strip.scrollLeft += dx;
        wrap();
      }
      raf = requestAnimationFrame(tick);
    } else {
      last = 0;
    }
  };
  const kick = () => {
    if (near && !document.hidden && drifting && !held && !dragging && !stepping && !raf) {
      raf = requestAnimationFrame(tick);
    }
  };

  const hold = () => { held = strip.matches(':hover, :focus-within'); kick(); };
  ['pointerenter', 'pointerleave', 'focusin', 'focusout'].forEach((ev) => strip.addEventListener(ev, () => requestAnimationFrame(hold)));
  strip.addEventListener('scroll', wrap, { passive: true });
  strip.addEventListener('wheel', () => {
    clearTimeout(stepTimer);
    stepping = true;
    stepTimer = setTimeout(() => { stepping = false; kick(); }, 900);
  }, { passive: true });

  const stepBy = (dir) => {
    clearTimeout(stepTimer);
    stepping = true;
    const w = loopWidth();
    const delta = Math.round(Math.min(540, strip.clientWidth * 0.55)) * dir;
    if (dir < 0 && w && strip.scrollLeft + delta < 0) strip.scrollLeft += w;
    strip.scrollBy({ left: delta, behavior: still.matches ? 'auto' : 'smooth' });
    stepTimer = setTimeout(() => { stepping = false; wrap(); kick(); }, 650);
  };
  prevBtn?.addEventListener('click', () => stepBy(-1));
  nextBtn?.addEventListener('click', () => stepBy(1));

  // mouse drag with smooth feel
  let start = null, dragged = false;
  strip.addEventListener('pointerdown', (e) => {
    dragged = false;
    if (e.pointerType !== 'mouse' || e.button !== 0) return;
    start = { x: e.clientX, left: strip.scrollLeft, id: e.pointerId };
  });
  strip.addEventListener('pointermove', (e) => {
    if (!start || e.pointerId !== start.id) return;
    if (!e.buttons) { start = null; dragging = false; strip.classList.remove('is-dragging'); kick(); return; }
    const dx = e.clientX - start.x;
    if (!dragged) {
      if (Math.abs(dx) < 6) return;
      dragged = true; dragging = true; setDrifting(false);
      strip.classList.add('is-dragging');
      strip.setPointerCapture(e.pointerId);
    }
    const w = loopWidth();
    let target = start.left - dx;
    if (w) {
      if (target < 0) { target += w; start.left += w; }
      else if (target >= w) { target -= w; start.left -= w; }
    }
    strip.scrollLeft = target;
  });
  const endDrag = (e) => {
    if (!start || e.pointerId !== start.id) return;
    start = null;
    if (!dragging) return;
    dragging = false;
    strip.classList.remove('is-dragging');
    kick();
  };
  strip.addEventListener('pointerup', endDrag);
  strip.addEventListener('pointercancel', endDrag);
  strip.addEventListener('lostpointercapture', endDrag);
  strip.addEventListener('click', (e) => { if (dragged) { e.preventDefault(); e.stopPropagation(); dragged = false; } }, true);
  strip.addEventListener('dragstart', (e) => e.preventDefault());

  still.addEventListener('change', () => {
    if (still.matches) setDrifting(false);
    if (pauseBtn) pauseBtn.hidden = still.matches;
    kick();
  });
  document.addEventListener('visibilitychange', kick);
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((es) => { near = es.some((e) => e.isIntersecting); kick(); }, { rootMargin: '200px 0px' }).observe(strip);
  } else { near = true; kick(); }
})();

// ------------------------------------------------------------------ the home page's cycling researcher quotes
// Crossfades through similarly sized researcher quotes beside the globe every 6s while visible;
// pauses on hover, focus, or reduced motion. Clicking the panel navigates to Publications#what-others-write.
(() => {
  const root = document.querySelector('[data-voice-rotator]');
  if (!root) return;
  const slides = [...root.querySelectorAll('.voice__slide')];
  if (slides.length < 2) return;
  const controls = root.querySelector('[data-voice-controls]');
  const prev = root.querySelector('[data-voice-prev]');
  const next = root.querySelector('[data-voice-next]');
  const still = matchMedia('(prefers-reduced-motion: reduce)');
  if (controls) controls.hidden = false;

  let cur = 0, held = false, focused = false, seen = false, timer = 0;
  const show = (k) => {
    cur = ((k % slides.length) + slides.length) % slides.length;
    slides.forEach((s, i) => {
      const on = i === cur;
      s.classList.toggle('is-active', on);
      s.setAttribute('aria-hidden', String(!on));
    });
  };
  const reset = () => {
    clearInterval(timer);
    timer = setInterval(() => {
      if (!still.matches && seen && !held && !focused && !document.hidden) show(cur + 1);
    }, 6000);
  };
  prev?.addEventListener('click', (e) => { e.stopPropagation(); show(cur - 1); reset(); });
  next?.addEventListener('click', (e) => { e.stopPropagation(); show(cur + 1); reset(); });
  reset();
  root.addEventListener('pointerenter', () => { held = true; });
  root.addEventListener('pointerleave', () => { held = false; });
  root.addEventListener('focusin', () => { focused = true; });
  root.addEventListener('focusout', () => { focused = false; });
  if ('IntersectionObserver' in window) {
    new IntersectionObserver((es) => { seen = es.some((e) => e.isIntersecting); }).observe(root);
  } else seen = true;
})();

// ------------------------------------------------------------------ the home page's globe: its script
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
