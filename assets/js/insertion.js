// The electrode insertion on the home page (#localize): the one scroll-linked motion of the site.
// As the section scrolls through the window, the leads move into place (and back out when scrolling
// up): a sequence of WebP frames (static/media/insertion/) drawn on a canvas by scroll position.
// - The final still (an <img>) is the picture until every frame has loaded, and stays the picture
//   under reduced motion, without script, and when a frame fails to load.
// - Frames load only after the page has loaded, once the visitor has scrolled and the section is within
//   a quarter of a screen of the window, so a visitor who never scrolls down does not load them, on a
//   desktop either (where the section starts just under the first screen). The set is chosen by the
//   picture's width in CSS pixels, not device pixels: the small set (720 px wide) wherever the picture
//   is drawn 900 CSS px wide or less, which is every screen up to 1920 px wide, at any pixel density
//   (about 1.4 MB instead of 3.1 MB on a retina laptop); while the frames move, the difference does not
//   show, and at rest the sharp still is the picture. On a phone only every third frame of it is loaded
//   (40 instead of 120, about 0.45 MB). Visitors who ask to save data keep the still.
// - The canvas lies exactly over the still, in a box of fixed aspect ratio: nothing on the page moves.
(() => {
  const fig = document.querySelector('[data-insertion]');
  if (!fig || !('IntersectionObserver' in window)) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches) return;
  if (navigator.connection?.saveData) return;
  const canvas = fig.querySelector('canvas');
  const stage = fig.querySelector('.insertion__stage');
  const ctx = canvas.getContext('2d', { alpha: false });
  if (!ctx) return;

  const pick = () => {
    const small = fig.dataset.listSmall && stage.clientWidth <= 900;
    const base = small ? fig.dataset.framesSmall : fig.dataset.frames;
    let names = (small ? fig.dataset.listSmall : fig.dataset.list).split(',').filter(Boolean).sort();
    // a phone: every third frame, always ending on the last one (the leads in place)
    if (window.innerWidth < 640 && names.length > 60) {
      const last = names[names.length - 1];
      names = names.filter((n, i) => i % 3 === 0);
      if (names[names.length - 1] !== last) names.push(last);
    }
    return names.map((n) => base + n);
  };

  let frames = [], shown = -1, live = false, queued = false;

  // 0 when the stage's top enters the lower edge of the window, 1 when its middle reaches the
  // window's upper 40 %: the leads are in place while the section is comfortably in view
  const progress = () => {
    const r = stage.getBoundingClientRect(), vh = window.innerHeight;
    const start = vh * 0.95, end = vh * 0.4 - r.height / 2;
    return Math.min(1, Math.max(0, (start - r.top) / (start - end)));
  };
  const draw = () => {
    queued = false;
    if (!live) return;
    const i = Math.round(progress() * (frames.length - 1));
    if (i === shown) return;
    shown = i;
    // at rest the sharper still shows (the last frame is the same picture, compressed harder)
    const rest = i === frames.length - 1;
    fig.classList.toggle('is-rest', rest);
    if (!rest) ctx.drawImage(frames[i], 0, 0, canvas.width, canvas.height);
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(draw); } };

  const load = () => {
    const urls = pick();
    if (urls.length < 2) return;
    let left = urls.length, failed = false;
    frames = urls.map((u) => {
      const img = new Image();
      img.decoding = 'async';
      img.onload = () => {
        if (--left || failed) return;
        // every frame is in; the browser decodes each when it is first drawn (decoding all 120 at
        // once would hold some hundred megabytes)
        canvas.width = frames[0].naturalWidth; canvas.height = frames[0].naturalHeight;
        live = true; shown = -1; draw();
        fig.classList.add('is-live');
        addEventListener('scroll', queue, { passive: true });
        addEventListener('resize', queue);
      };
      img.onerror = () => { failed = true; };
      img.src = u;
      return img;
    });
  };
  // not before the page itself has loaded and the browser is idle, so the frames never compete with
  // the hero; then once the visitor has scrolled (a page opened further down counts) and the section
  // is within a quarter of a screen of the window
  const watch = () => {
    let near = false, moved = window.scrollY > 0, started = false;
    const go = () => {
      if (started || !near || !moved) return;
      started = true; io.disconnect(); removeEventListener('scroll', onScroll); load();
    };
    const onScroll = () => { if (window.scrollY > 0) { moved = true; go(); } };
    const io = new IntersectionObserver((es) => {
      near = es.some((e) => e.isIntersecting); go();
    }, { rootMargin: '25% 0px 25% 0px' });
    io.observe(stage);
    addEventListener('scroll', onScroll, { passive: true });
  };
  const idle = window.requestIdleCallback || ((f) => setTimeout(f, 300));
  if (document.readyState === 'complete') idle(watch, { timeout: 2000 });
  else addEventListener('load', () => idle(watch, { timeout: 2000 }), { once: true });
  // reduced motion switched on while the page is open: back to the still
  reduced.addEventListener?.('change', (e) => {
    if (!e.matches) return;
    live = false; fig.classList.remove('is-live');
    removeEventListener('scroll', queue);
  });
})();
