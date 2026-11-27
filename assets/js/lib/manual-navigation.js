const navigationKey = 'lead-manual-navigation';
const branchSelector = '.manual-nav__subchapters';

export const desktopRailQuery = '(width >= 1024px)';

export function reveal(box, item) {
  if (!item?.getClientRects().length) return;
  const bounds = box.getBoundingClientRect();
  const row = item.getBoundingClientRect();
  const style = getComputedStyle(box);
  const top = bounds.top + box.clientTop + (parseFloat(style.scrollPaddingTop) || 0);
  const bottom = bounds.top + box.clientTop + box.clientHeight - (parseFloat(style.scrollPaddingBottom) || 0);
  if (row.top < top) box.scrollTop += row.top - top;
  else if (row.bottom > bottom) box.scrollTop += row.bottom - bottom;
}

function savedNavigation() {
  try {
    const state = JSON.parse(sessionStorage.getItem(navigationKey));
    if (state?.path === location.pathname) return state;
  } catch { /* The rail works without browser storage. */ }
}

export function rememberChapterNavigation(tree, link, box, desktop) {
  const target = new URL(link.href);
  if (target.origin !== location.origin || target.pathname === location.pathname) return;
  try {
    sessionStorage.setItem(navigationKey, JSON.stringify({
      path: target.pathname,
      branches: Array.from(tree.querySelectorAll(`${branchSelector}[open]`), branch => branch.id),
      desktop,
      scrollTop: box.scrollTop,
      rowTop: tree.contains(link) ? link.getBoundingClientRect().top - box.getBoundingClientRect().top : null,
    }));
  } catch { /* The rail works without browser storage. */ }
}

export function restoreOpenChapters(tree) {
  const { branches } = savedNavigation() || {};
  if (!Array.isArray(branches)) return;
  const openIds = new Set(branches);
  for (const branch of tree.querySelectorAll(branchSelector)) {
    if (openIds.has(branch.id)) branch.open = true;
  }
}

export function restoreChapterPosition(box, tree, desktop) {
  const state = savedNavigation();
  const current = tree.querySelector('[aria-current="page"]');
  if (state) {
    try { sessionStorage.removeItem(navigationKey); } catch { /* Storage is optional. */ }
    if (state.desktop === desktop && Number.isFinite(state.scrollTop)) {
      box.scrollTop = state.scrollTop;
      if (current && Number.isFinite(state.rowTop)) {
        box.scrollTop += current.getBoundingClientRect().top - box.getBoundingClientRect().top - state.rowTop;
      }
    }
  }
  reveal(box, current);
}
