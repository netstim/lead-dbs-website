// The site search. Hugo writes the index (/search-index.json, layouts/home.searchindex.json); this
// loads it the first time a search box is used and ranks pages by where the words occur (title,
// headings, description, text). The header's button (and the "/" key) opens it in a dialog; /search/
// shows the same box on a page and reads ?q= from the address. Without script the button is a link
// to /search/.
(() => {
  const dialog = document.getElementById('site-search');
  const indexUrl = dialog?.dataset.index;
  if (!indexUrl) return;
  let index = null;
  const load = () => (index ||= fetch(indexUrl).then((r) => r.json()).then((rows) => rows.map((r) => ({
    ...r, lt: fold(r.t), lh: fold(r.h), ld: fold(r.d), lx: fold(r.x),
  }))));
  const fold = (s) => (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[‐-‑]/g, '-');
  const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

  const rank = (rows, q) => {
    const words = fold(q).split(/[\s,;]+/).filter((w) => w.length > 1 || /\d/.test(w));
    if (!words.length) return [];
    const out = [];
    for (const r of rows) {
      let score = 0;
      for (const w of words) {
        let s = 0;
        if (r.lt.includes(w)) s += r.lt.startsWith(w) || r.lt.includes(' ' + w) ? 12 : 8;
        if (r.lh.includes(w)) s += 4;
        if (r.ld.includes(w)) s += 3;
        if (r.lx.includes(w)) s += 1 + Math.min(3, r.lx.split(w).length - 2);
        if (!s) { score = 0; break; } // every word must occur somewhere
        score += s;
      }
      if (score) out.push([score - (r.s.startsWith('News') ? 1 : 0), r]);
    }
    return out.sort((a, b) => b[0] - a[0]).slice(0, 12).map(([, r]) => r);
  };
  const snippet = (r, q) => {
    const w = fold(q).split(/\s+/).find((x) => x.length > 1 && r.lx.includes(x));
    const src = r.d || r.x;
    if (!w || r.d) return esc(src.slice(0, 160)) + (src.length > 160 ? '…' : '');
    const at = r.lx.indexOf(w), from = Math.max(0, at - 60);
    return (from ? '…' : '') + esc(r.x.slice(from, from + 170)) + '…';
  };

  const wire = (box) => {
    const input = box.querySelector('.search__input');
    const list = box.querySelector('.search__results');
    const status = box.querySelector('.search__status');
    let timer = 0;
    const run = async () => {
      const q = input.value.trim();
      if (!q) { list.replaceChildren(); status.textContent = ''; return; }
      status.textContent = 'Searching…';
      let rows;
      try { rows = await load(); } catch { status.textContent = 'The search index could not be loaded.'; return; }
      const hits = rank(rows, q);
      status.textContent = hits.length ? `${hits.length}${hits.length === 12 ? ' or more' : ''} pages found` : 'No page found. Try fewer or other words.';
      list.innerHTML = hits.map((r) => `<li><a class="search__hit" href="${esc(r.u)}"><span class="search__title">${esc(r.t)}</span>${r.s ? `<span class="search__section">${esc(r.s)}</span>` : ''}<span class="search__snippet">${snippet(r, q)}</span></a></li>`).join('');
    };
    input.addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(run, 120); });
    box.querySelector('form').addEventListener('submit', (e) => { e.preventDefault(); const first = list.querySelector('a'); if (first) first.click(); else run(); });
    // arrow keys: from the box to the results and between them
    box.addEventListener('keydown', (e) => {
      if (e.key !== 'ArrowDown' && e.key !== 'ArrowUp') return;
      const links = [...list.querySelectorAll('a')];
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
    if (e.key !== '/' || e.ctrlKey || e.metaKey || e.altKey) return;
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
