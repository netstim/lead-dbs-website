// The site search. Hugo writes the index (/search-index.json, layouts/home.searchindex.json); this
// loads it the first time a search box is used and ranks pages by where the words occur: a page whose
// title (or keywords) holds the words comes before any page that only mentions them in its text, and
// news posts come after other pages with the same score. The header's button (and the "/" key) opens it in a dialog; /search/
// shows the same box on a page and reads ?q= from the address. Without script the button is a link
// to /search/.
(() => {
  const dialog = document.getElementById('site-search');
  const indexUrl = dialog?.dataset.index;
  if (!indexUrl) return;
  const MANUAL = new URL('manual/', new URL(indexUrl, location.href)).pathname;
  const SHOWN = 12; // results listed; the status line counts them all
  let index = null;
  const load = () => (index ||= fetch(indexUrl).then((r) => {
    if (!r.ok) throw new Error(`Search index: HTTP ${r.status}`);
    return r.json();
  }).then((rows) => rows.map((r) => ({
    ...r, lt: fold(r.t), lk: fold(r.k), lh: fold(r.h), ld: fold(r.d), lx: fold(r.x),
  }))).catch((error) => { index = null; throw error; }));
  const fold = (s) => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[‐-‑]/g, '-');
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const rank = (rows, q) => {
    const words = fold(q).split(/[\s,;]+/).filter((w) => w.length > 1 || /\d/.test(w));
    if (!words.length) return [];
    const phrase = words.join(' ');
    const out = [];
    for (const r of rows) {
      let score = 0;
      for (const w of words) {
        let s = 0;
        const wordStart = (t) => t.startsWith(w) || t.includes(' ' + w) || t.includes('-' + w);
        if (r.lt.includes(w)) s += (wordStart(r.lt) ? 40 : 25) + Math.max(0, 12 - r.lt.length / 6); // short titles first
        if (r.lk.includes(w)) s += 20 + (` ${r.lk} `.includes(` ${w} `) ? 10 : 0); // a whole keyword ("mac", not "macaque") counts more
        if (r.lh.includes(w)) s += 6;
        if (r.ld.includes(w)) s += 4;
        if (r.lx.includes(w)) s += 1 + Math.min(3, r.lx.split(w).length - 2);
        if (!s) { score = 0; break; } // every word must occur somewhere
        score += s;
      }
      if (!score) continue;
      if (words.length > 1 && r.lt.includes(phrase)) score += 20; // the words together, as typed
      if (r.s.startsWith('News')) score = score * 0.85 - 1; // a post after a page that says the same
      out.push([score, r]);
    }
    return out.sort((a, b) => b[0] - a[0]).map(([, r]) => r);
  };
  const snippet = (r, q) => {
    const w = fold(q).split(/\s+/).find((x) => x.length > 1 && r.lx.includes(x));
    const generic = r.d.startsWith('Lead-DBS user guide:');
    const src = generic ? r.x : (r.d || r.x);
    if (!w || (r.d && !generic)) return esc(src.slice(0, 160)) + (src.length > 160 ? '…' : '');
    const at = r.lx.indexOf(w);
    let from = Math.max(0, at - 60);
    if (from) from = r.x.indexOf(' ', from) + 1;
    let end = Math.min(r.x.length, from + 170);
    if (end < r.x.length) end = r.x.lastIndexOf(' ', end);
    return (from ? '…' : '') + esc(r.x.slice(from, end)) + (end < r.x.length ? '…' : '');
  };

  const wire = (box) => {
    const input = box.querySelector('.search__input');
    const list = box.querySelector('.search__results');
    const status = box.querySelector('.search__status');
    const fallback = document.createElement('div');
    fallback.className = 'search__fallback';
    fallback.hidden = true;
    fallback.innerHTML = `<a class="search__hit search__hit--manual" href="${MANUAL}">Browse the Lead-DBS manual →</a>`;
    list.after(fallback);
    let timer = 0, generation = 0;
    const start = box.querySelector('.search__start');
    // on /search/ the cards to start from show only while there is no query
    const doors = box.closest('.search-page')?.querySelectorAll('[data-search-doors]') || [];
    const run = async () => {
      const request = ++generation;
      const q = input.value.trim();
      list.replaceChildren();
      fallback.hidden = true;
      if (start) start.hidden = !!q;
      doors.forEach((d) => { d.hidden = !!q; });
      if (!q) { list.replaceChildren(); status.textContent = ''; return; }
      status.textContent = 'Searching…';
      let rows;
      try { rows = await load(); } catch { if (request === generation) status.textContent = 'Search is unavailable. Please try again.'; return; }
      if (request !== generation || input.value.trim() !== q) return;
      const all = rank(rows, q);
      const hits = all.slice(0, SHOWN);
      status.textContent = !all.length ? 'No results found on this website. Try fewer or different words.'
        : all.length > SHOWN ? `The best ${SHOWN} of ${all.length} results` : `${all.length} result${all.length === 1 ? '' : 's'}`;
      list.innerHTML = hits.map((r) => {
        const section = r.s ? `<span class="search__section">${esc(r.s)}</span>` : '';
        return `<li><a class="search__hit" href="${esc(r.u)}"><span class="search__title">${esc(r.t)}</span>${section}<span class="search__snippet">${snippet(r, q)}</span></a></li>`;
      }).join('');
      fallback.hidden = false;
      return true;
    };
    input.addEventListener('input', () => {
      ++generation;
      list.replaceChildren();
      fallback.hidden = true;
      clearTimeout(timer);
      timer = setTimeout(run, 120);
    });
    box.querySelector('form').addEventListener('submit', async (e) => {
      e.preventDefault();
      clearTimeout(timer);
      if (await run()) list.querySelector('a')?.click();
    });
    // arrow keys: from the box to the results and between them
    box.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      const links = [...box.querySelectorAll('.search__results a, .search__fallback:not([hidden]) a, .search__start:not([hidden]) a')];
      if (!links.length) return;
      const at = links.indexOf(document.activeElement);
      e.preventDefault();
      if (e.key === 'ArrowDown') (links[at + 1] || links[0]).focus();
      else if (at <= 0) input.focus();
      else links[at - 1].focus();
    });
    return { input, run };
  };

  const inDialog = wire(dialog);
  const open = () => {
    if (!dialog.open) { dialog.showModal(); load().catch(() => {}); }
    inDialog.input.focus(); inDialog.input.select();
  };
  document.querySelectorAll('[data-search-open]').forEach((a) => a.addEventListener('click', (e) => {
    if (e.metaKey || e.ctrlKey || e.shiftKey) return;
    e.preventDefault(); open();
  }));
  dialog.querySelector('[data-search-close]')?.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  document.addEventListener('keydown', (e) => {
    const command = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k';
    if (!command && (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey)) return;
    if (e.target.closest?.('input, textarea, select, [contenteditable="true"]')) return;
    e.preventDefault(); open();
  });

  // a box on a page (/search/, the 404 page): it searches in place; /search/ reads ?q=
  document.querySelectorAll('main [data-search]').forEach((box) => {
    const p = wire(box);
    if (!box.closest('.search-page')) return;
    const q = new URLSearchParams(location.search).get('q');
    if (q) { p.input.value = q; p.run(); }
    p.input.focus();
  });
})();
