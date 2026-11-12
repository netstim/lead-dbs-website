// The filter at the top of an atlas catalogue (layouts/_shortcodes/atlas-index.html). The entries on the
// page (shortcode atlas-group) are the index: as you type, the page keeps the entries whose head (name,
// paper, what it covers, "Preinstalled") holds every word typed, hides groups left empty, and says how
// many match. ?atlas=word in the address fills the box. Without script the box stays hidden and every
// entry shows. Loaded once per page by the atlas-index shortcode.
document.querySelectorAll('[data-atlas-index]').forEach((box) => {
  const input = box.querySelector('[data-atlas-filter]');
  if (!input) return; // a short list has no filter
  const count = box.querySelector('[data-atlas-count]');
  const none = box.querySelector('[data-atlas-none]');
  const entries = [...document.querySelectorAll('[data-atlas-entry]')].map((el) => {
    const head = el.querySelector('.atlas__head');
    return [el, (head ? head.textContent : el.textContent).toLowerCase()];
  });
  // a group: its list of entries, and the heading and intro line written before it
  const groups = [...document.querySelectorAll('[data-atlas-group]')].map((list) => {
    const heading = document.getElementById(list.dataset.atlasGroup);
    const intro = list.previousElementSibling !== heading ? list.previousElementSibling : null;
    return { list, parts: [list, heading, intro].filter(Boolean) };
  });
  box.querySelector('[data-atlas-filter-box]').hidden = false;
  const run = () => {
    const words = input.value.toLowerCase().split(/\s+/).filter(Boolean);
    let shown = 0;
    entries.forEach(([el, text]) => {
      const hit = words.every((w) => text.includes(w));
      el.hidden = !hit;
      if (hit) shown += 1;
    });
    groups.forEach(({ list, parts }) => {
      const empty = !list.querySelector('[data-atlas-entry]:not([hidden])');
      parts.forEach((p) => { p.hidden = empty; });
    });
    count.textContent = words.length ? `${shown} of ${entries.length} match` : '';
    none.hidden = shown > 0;
  };
  input.addEventListener('input', run);
  const q = new URLSearchParams(location.search).get('atlas');
  if (q) { input.value = q; run(); }
});

// Every atlas entry folds its text away in a <details>; a link to the entry (from a paper or another
// page, including its older anchors) opens it.
const openAtlasFromHash = () => {
  const id = decodeURIComponent(location.hash.slice(1));
  if (!id) return;
  const target = document.getElementById(id);
  const entry = target && target.closest('[data-atlas-entry]');
  const details = entry && entry.querySelector('details');
  if (details) details.open = true;
};
openAtlasFromHash();
window.addEventListener('hashchange', openAtlasFromHash);
