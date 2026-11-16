// ------------------------------------------------------------------ silent clips
// The clips of a page (shortcodes clip and atlas-group, video[data-clip]): a clip plays while it is in view;
// its round button pauses it for good (WCAG 2.2.2) and plays it again. Under reduced motion, or when the
// visitor asks to save data, the clips keep their native controls and play only when started (the hero's
// clip does the same).
import { showPlayState } from '../lib/play-state.js';

(() => {
  const clips = document.querySelectorAll('video[data-clip]');
  if (!clips.length || !('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches || navigator.connection?.saveData) return;
  const held = new WeakSet();
  const io = new IntersectionObserver((entries) => entries.forEach((e) => {
    if (e.isIntersecting && !held.has(e.target)) e.target.play().catch(() => {}); else e.target.pause();
  }), { threshold: 0.25 });
  clips.forEach((v) => {
    v.controls = false;
    const btn = document.createElement('button');
    btn.type = 'button'; btn.className = 'media-pause';
    const show = () => showPlayState(btn, !held.has(v), 'the animation');
    btn.addEventListener('click', () => {
      if (held.has(v)) { held.delete(v); v.play().catch(() => {}); } else { held.add(v); v.pause(); }
      show();
    });
    show();
    v.after(btn);
    v.parentElement.classList.add('has-media-pause');
    io.observe(v);
  });
})();
