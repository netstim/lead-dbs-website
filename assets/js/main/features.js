// {{< capabilities >}} (Features): a click on a capability's name chooses it: its sentence and links
// open under the name and its picture shows on the stage. The address takes its id, so the chosen one can
// be linked; a link to a capability (from the home page, the search) chooses it too.
// On a phone (below 640px, assets/css/phone-features.css) the stage is a row of square pictures that
// scrolls sideways, one per name, above the names: swiping it chooses the name, a tap on a name turns it
// to that name's picture, and a row of segments follows. {{< tools >}} becomes the same module there.
// From 640px up nothing of that runs; a phone that turns into a wider window hands its state back.
const phone = matchMedia('(max-width: 639px)');
const still = matchMedia('(prefers-reduced-motion: reduce)');

// One phone module: track (the row of pictures, one per item), its segments, and choose(i), which makes
// the i-th item the chosen one. Returns turn(i, smooth) (the row to that picture), mark(i) (the segments)
// and land(i) (the page scrolled so that the stage and the chosen item are in view).
const carousel = (root, track, items, choose, label) => {
  const slides = [...track.children];
  const segs = [...root.querySelectorAll('.cap-show__segs > span')];
  let current = 0;
  let pending = null;   // the picture a tap turns to: the pictures it passes on the way choose nothing
  const step = () => (slides.length > 1 ? slides[1].offsetLeft - slides[0].offsetLeft : 1);
  const at = () => Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / step())));
  const mark = (i) => { current = i; segs.forEach((s, k) => s.classList.toggle('is-on', k === i)); };
  const turn = (i, smooth) => {
    const left = i * step();
    if (Math.abs(track.scrollLeft - left) < 1) return;
    const glide = smooth && !still.matches;
    pending = glide ? i : null;
    track.scrollTo({ left, behavior: glide ? 'smooth' : 'instant' });
  };
  const follow = () => { const i = at(); if (i !== current) choose(i); };
  track.addEventListener('scroll', () => {
    if (!phone.matches) return;
    if (pending !== null) { if (Math.abs(track.scrollLeft - pending * step()) < 2) pending = null; return; }
    follow();
  }, { passive: true });
  track.addEventListener('scrollend', () => { if (phone.matches) { pending = null; follow(); } });
  // (on a page's first load the browser's own jump to the anchor comes after this script, so it is done
  // again once the page has loaded)
  const land = (i, again = true) => {
    if (again && document.readyState !== 'complete') addEventListener('load', () => requestAnimationFrame(() => land(i, false)), { once: true });
    turn(i, false);
    const nav = document.querySelector('.nav')?.offsetHeight || 0;
    const top = track.getBoundingClientRect().top;
    const item = items[i].getBoundingClientRect();
    const y = item.bottom - top + nav + 16 <= innerHeight ? top - nav - 16 : item.top - nav - 8;
    scrollTo({ top: scrollY + y, behavior: 'instant' });
  };
  // a phone: the row is reachable by keyboard (arrow keys turn it) and named; wider: as it was
  const setup = () => {
    if (phone.matches) {
      track.tabIndex = 0;
      track.setAttribute('role', 'group');
      track.setAttribute('aria-label', label);
      turn(current, false);
    } else {
      track.removeAttribute('tabindex');
      track.removeAttribute('role');
      track.removeAttribute('aria-label');
    }
  };
  phone.addEventListener('change', setup);
  setup();
  return { turn, mark, land };
};

// a chapter's name, for the label of its row of pictures
const chapterName = (el) => {
  const h = el.previousElementSibling?.querySelector('h2');
  return h ? h.firstChild.textContent.trim() : '';
};

document.querySelectorAll('[data-cap-show]').forEach((show) => {
  const items = [...show.querySelectorAll('.capability')];
  const figs = [...show.querySelectorAll('[data-cap-fig]')];
  if (items.length < 2) return;
  let ph = null;
  const open = (item) => {
    items.forEach((it) => {
      it.classList.toggle('is-active', it === item);
      it.querySelector('h3 > button').setAttribute('aria-expanded', String(it === item));
    });
    figs.forEach((f) => f.classList.toggle('is-active', f.dataset.capFig === item.id));
    ph?.mark(items.indexOf(item));
  };
  items.forEach((it, i) => it.querySelector('h3 > button').addEventListener('click', () => {
    open(it);
    history.replaceState(null, '', '#' + it.id);
    if (phone.matches) ph.turn(i, true);
  }));
  ph = carousel(show, show.querySelector('.cap-show__stage'), items, (i) => open(items[i]), `${chapterName(show)}: pictures`);
  const fromHash = () => {
    const it = items.find((x) => '#' + x.id === location.hash);
    if (!it) return;
    open(it);
    if (matchMedia('(min-width: 1024px)').matches) show.scrollIntoView();
    else if (phone.matches) ph.land(items.indexOf(it));
  };
  addEventListener('hashchange', fromHash);
  fromHash();
});

// {{< tools >}} on a phone: the same module, its names made buttons while the window is narrow
document.querySelectorAll('.tool-cells').forEach((cells) => {
  const items = [...cells.querySelectorAll(':scope > .tool')];
  const track = cells.querySelector(':scope > .tool-stage');
  if (items.length < 2 || !track) return;
  let current = 0;
  let ph = null;
  const choose = (i) => {
    current = i;
    items.forEach((it, k) => {
      it.classList.toggle('is-active', k === i);
      it.querySelector('h3 > button')?.setAttribute('aria-expanded', String(k === i));
    });
    ph?.mark(i);
  };
  // the band's black reaches up over the chapter's head above, so the header turns black over all of it
  const head = cells.previousElementSibling;
  const band = cells.querySelector(':scope > .tool-band');
  const size = () => { if (band && head && phone.matches) cells.style.setProperty('--band-head', head.offsetHeight + 'px'); };
  if (head && 'ResizeObserver' in window) new ResizeObserver(size).observe(head);
  const setup = () => {
    items.forEach((it, i) => {
      const h = it.querySelector('h3');
      const b = h.querySelector('button');
      if (phone.matches && !b) {
        const nb = document.createElement('button');
        nb.type = 'button';
        nb.textContent = h.textContent;
        nb.addEventListener('click', () => {
          choose(i);
          history.replaceState(null, '', '#' + it.id);
          ph.turn(i, true);
        });
        h.replaceChildren(nb);
      } else if (!phone.matches && b) {
        h.textContent = b.textContent;
      }
    });
    cells.classList.toggle('is-phone', phone.matches);
    if (phone.matches) { choose(current); size(); }
  };
  phone.addEventListener('change', setup);
  setup();
  ph = carousel(cells, track, items, choose, `${chapterName(cells)}: pictures`);
  ph.mark(current);
  const fromHash = () => {
    const i = items.findIndex((x) => '#' + x.id === location.hash);
    if (i < 0 || !phone.matches) return;
    choose(i);
    ph.land(i);
  };
  addEventListener('hashchange', fromHash);
  fromHash();
});
