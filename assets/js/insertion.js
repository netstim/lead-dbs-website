// The electrode insertion on the home page (#localize): the one scroll-linked motion of the site.
// As the section scrolls through the window, the leads move into place (and back out when scrolling
// up): a sequence of WebP frames (static/media/insertion/) drawn on a canvas by scroll position.
// - The final still (an <img>) is the picture until every frame has loaded, and stays the picture
//   under reduced motion, without script, and when a frame fails to load.
// - Frames load only after the page has loaded, when the section is within a screen of the window;
//   the small set (720 px) when the picture is drawn at 900 device pixels or less.
// - The canvas lies exactly over the still, in a box of fixed aspect ratio: nothing on the page moves.
(() => {
  const fig = document.querySelector('[data-insertion]');
  if (!fig || !('IntersectionObserver' in window)) return;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (reduced.matches) return;
  const canvas = fig.querySelector('canvas');
  const stage = fig.querySelector('.insertion__stage');
  const ctx = canvas.getContext('2d', { alpha: false });
  if (!ctx) return;

  const pick = () => {
    const small = fig.dataset.listSmall && stage.clientWidth * (window.devicePixelRatio || 1) <= 900;
    const base = small ? fig.dataset.framesSmall : fig.dataset.frames;
    const names = (small ? fig.dataset.listSmall : fig.dataset.list).split(',').filter(Boolean).sort();
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
  // the hero; then as soon as the section is within a screen of the window
  const watch = () => {
    const io = new IntersectionObserver((es) => {
      if (es.some((e) => e.isIntersecting)) { io.disconnect(); load(); }
    }, { rootMargin: '100% 0px 100% 0px' });
    io.observe(stage);
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
