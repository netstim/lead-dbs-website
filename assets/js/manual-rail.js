import { desktopRailQuery, rememberChapterNavigation, restoreChapterPosition, restoreOpenChapters } from './lib/manual-navigation.js';

// Run beside the rendered tree so it can restore the desktop rail without waiting for a bundle.
const rail = document.querySelector('.manual-nav');
const fold = rail.querySelector('.manual-nav__fold');
const tree = fold.querySelector('.manual-nav__tree');
const desktop = matchMedia(desktopRailQuery);
fold.dataset.railReady = '';
restoreOpenChapters(tree);
if (desktop.matches) {
  fold.open = true;
  restoreChapterPosition(rail, tree, true);
}

document.addEventListener('click', event => {
  const link = event.target.closest('.manual-nav__tree a, .manual-pagination a');
  if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const box = desktop.matches ? rail : tree.closest('.manual-drawer__body');
  rememberChapterNavigation(tree, link, box || tree, desktop.matches);
}, { capture: true });
