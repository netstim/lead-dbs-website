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

// Paper rows (Publications): a year is written once, on its first row.
document.querySelectorAll('.paper-rows').forEach((list) => {
  let last = '';
  list.querySelectorAll('.paper-row__year').forEach((y) => { if (y.textContent === last) y.classList.add('is-repeat'); else last = y.textContent; });
});

// ------------------------------------------------------------------ the citation snippet
// Every citation box (partial cite-box.html): its tabs select a format and point its Copy button at it.
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
