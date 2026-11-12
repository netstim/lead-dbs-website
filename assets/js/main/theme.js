// ------------------------------------------------------------------ light and dark
// head.html sets html[data-theme] before the first paint: the reader's choice (localStorage "theme"),
// else the system's. The header's button flips it and keeps the choice; without a choice the page
// follows the system when that changes.
(() => {
  const root = document.documentElement;
  const buttons = document.querySelectorAll('[data-theme-toggle]');
  const label = () => {
    const words = root.dataset.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
    buttons.forEach((b) => { b.setAttribute('aria-label', words); b.title = words; });
  };
  const set = (t) => { root.dataset.theme = t; label(); };
  buttons.forEach((b) => b.addEventListener('click', () => {
    const t = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('theme', t); } catch (e) { /* private mode: the choice lasts this page */ }
    set(t);
  }));
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    let saved = null;
    try { saved = localStorage.getItem('theme'); } catch (e) { /* none */ }
    if (!saved) set(e.matches ? 'dark' : 'light');
  });
  label();
})();
