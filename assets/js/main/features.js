// {{< capabilities >}} (Features): a click on a capability's name chooses it: its sentence and links
// open under the name and its picture shows on the stage. The address takes its id, so the chosen one can
// be linked; a link to a capability (from the home page, the search) chooses it too.
document.querySelectorAll('[data-cap-show]').forEach((show) => {
  const items = [...show.querySelectorAll('.capability')];
  const figs = [...show.querySelectorAll('[data-cap-fig]')];
  if (items.length < 2) return;
  const open = (item) => {
    items.forEach((it) => {
      it.classList.toggle('is-active', it === item);
      it.querySelector('h3 > button').setAttribute('aria-expanded', String(it === item));
    });
    figs.forEach((f) => f.classList.toggle('is-active', f.dataset.capFig === item.id));
  };
  items.forEach((it) => it.querySelector('h3 > button').addEventListener('click', () => {
    open(it);
    history.replaceState(null, '', '#' + it.id);
  }));
  const fromHash = () => {
    const it = items.find((x) => '#' + x.id === location.hash);
    if (!it) return;
    open(it);
    if (matchMedia('(min-width: 1024px)').matches) show.scrollIntoView();
  };
  addEventListener('hashchange', fromHash);
  fromHash();
});
