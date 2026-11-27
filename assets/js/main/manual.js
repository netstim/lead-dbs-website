import { wireDialog } from '../lib/dialog.js';
import { leadFragment } from '../lib/fragment.js';
import { wireCopyButton } from '../lib/copy.js';
import { desktopRailQuery, restoreChapterPosition, reveal } from '../lib/manual-navigation.js';

const plainClick = (event) => event.button === 0 && !event.metaKey && !event.ctrlKey && !event.shiftKey && !event.altKey;

// Keep the original linked image available when the dialog cannot run.
const imageDialog = document.getElementById('manual-image');
if (typeof imageDialog?.showModal === 'function') {
  const openImage = wireDialog(imageDialog, []);
  const picture = imageDialog.querySelector('.manual-image__picture');
  const caption = imageDialog.querySelector('.manual-image__caption');
  const original = imageDialog.querySelector('.manual-image__original');
  for (const link of document.querySelectorAll('.manual-prose a.img-zoom')) {
    const thumbnail = link.querySelector('img');
    if (!thumbnail) continue;
    link.setAttribute('aria-haspopup', 'dialog');
    link.addEventListener('click', (event) => {
      if (!plainClick(event)) return;
      event.preventDefault();
      picture.alt = thumbnail.alt;
      original.href = link.href;
      const text = link.closest('.img-figure')?.querySelector('.img-figure__caption')?.textContent.trim();
      caption.textContent = text || '';
      caption.hidden = !text;
      picture.src = link.href;
      openImage(link);
    });
  }
}

for (const references of document.querySelectorAll('[data-manual-references]')) {
  const template = document.getElementById('manual-reference-copy');
  references.querySelectorAll('li').forEach((item, index) => {
    const button = template.content.firstElementChild.cloneNode(true);
    button.dataset.copyText = item.innerText.trim();
    const label = `Copy ${references.dataset.manualReferences} ${index + 1}`;
    button.setAttribute('aria-label', label);
    button.title = label;
    item.append(button);
    wireCopyButton(button);
  });
}

// Keep the server-rendered disclosures until the drawer controls are ready.
(() => {
  const fold = document.querySelector('.manual-nav__fold');
  if (!fold) return;
  const tree = fold.querySelector('.manual-nav__tree');
  const rail = document.querySelector('.manual-nav');
  const drawer = document.querySelector('#manual-drawer');
  if (typeof drawer.showModal !== 'function') return;
  const trigger = document.querySelector('.manual-menu');
  const body = drawer.querySelector('.manual-drawer__body');
  const contents = document.querySelector('#manual-contents');
  const sections = document.querySelector('.manual-sections');
  const contentsList = contents?.querySelector('.manual-contents__list');
  const outlineFold = document.querySelector('.manual-toc-fold');
  const inlineOutline = outlineFold?.querySelector('.manual-toc');
  const side = document.querySelector('.manual-outline');
  const sideLinks = side ? [...side.querySelectorAll('.manual-toc a')] : [];
  const headings = sideLinks.map((link) => document.getElementById(leadFragment(link.hash.slice(1))));
  const desktop = matchMedia(desktopRailQuery);
  const dialogs = [[drawer, trigger], ...(contents ? [[contents, sections]] : [])];
  let drawerPositionRestored = false;

  const activeIndex = () => {
    const offset = headings[0] ? parseFloat(getComputedStyle(headings[0]).scrollMarginTop) : 0;
    const { scrollTop, scrollHeight, clientHeight } = document.scrollingElement;
    const atEnd = scrollHeight > clientHeight && scrollHeight - clientHeight - scrollTop <= 2;
    const top = atEnd ? innerHeight : Math.max(offset + 1, innerHeight / 3);
    if (scrollHeight <= clientHeight) {
      const anchor = headings.findIndex((heading) => heading?.id === leadFragment(location.hash.slice(1)));
      if (anchor >= 0) return anchor;
    }
    let active = 0;
    headings.forEach((heading, index) => {
      if (heading?.getClientRects().length && heading.getBoundingClientRect().top <= top) active = index;
    });
    return active;
  };
  const highlight = (links, active, box, revealCurrent = false) => {
    const link = links[active];
    const changed = link.getAttribute('aria-current') !== 'location';
    if (changed) {
      box.querySelector('a[aria-current="location"]')?.removeAttribute('aria-current');
      link.setAttribute('aria-current', 'location');
    }
    if (changed || revealCurrent) reveal(box, link);
  };

  const close = () => dialogs.forEach(([dialog]) => { if (dialog.open) dialog.close(); });
  let sectionTarget;
  dialogs.forEach(([dialog, button]) => {
    wireDialog(dialog, [button]);
    button.addEventListener('click', () => {
      button.setAttribute('aria-expanded', 'true');
      if (dialog !== drawer) highlight([...inlineOutline.querySelectorAll('a')], activeIndex(), contentsList, true);
      else if (!drawerPositionRestored) {
        restoreChapterPosition(body, tree, false);
        drawerPositionRestored = true;
      }
    });
    dialog.addEventListener('close', () => {
      button.setAttribute('aria-expanded', 'false');
      if (dialog === contents && sectionTarget) {
        sectionTarget.setAttribute('tabindex', '-1');
        sectionTarget.focus({ preventScroll: true });
        sectionTarget.scrollIntoView({ block: 'start' });
        sectionTarget = null;
      }
    });
    dialog.querySelector('[data-manual-close]').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (e) => {
      const link = e.target.closest('a');
      if (!link || !plainClick(e)) return;
      if (dialog === contents) sectionTarget = document.getElementById(leadFragment(link.hash.slice(1)));
      dialog.close();
    });
  });

  let queued = false;
  const updateOutline = () => {
    if (queued || !sideLinks.length) return;
    queued = true;
    requestAnimationFrame(() => {
      queued = false;
      if (side.getClientRects().length) highlight(sideLinks, activeIndex(), side);
    });
  };
  const updateLayout = () => {
    close();
    fold.open = desktop.matches;
    const treeContainer = desktop.matches ? fold : body;
    if (tree.parentElement !== treeContainer) {
      treeContainer.append(tree);
      if (desktop.matches) restoreChapterPosition(rail, tree, true);
      else drawerPositionRestored = false;
    }
    if (inlineOutline) (desktop.matches ? outlineFold : contentsList).append(inlineOutline);
    updateOutline();
  };
  document.documentElement.classList.add('manual-ready');
  updateLayout();
  desktop.addEventListener('change', updateLayout);
  addEventListener('scroll', updateOutline, { passive: true });
  addEventListener('resize', updateOutline);
  addEventListener('hashchange', updateOutline);
  if (sideLinks.length) document.fonts.ready.then(updateOutline);
  document.addEventListener('keydown', (e) => {
    if (e.target.closest?.('input, textarea, select, [contenteditable="true"]')) return;
    const command = (e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k';
    if (command || (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey)) close();
  }, true);
})();
// Preview long examples without hiding their full source from the copy control.
// No-JavaScript readers get the complete code. Overflow cues reflect the actual viewport.
(() => {
  const blocks = [...document.querySelectorAll('.manual-code:has(.manual-code__source)')];
  blocks.forEach((block) => {
    block.querySelectorAll('.line').forEach((line) => {
      const indent = line.textContent.match(/^[\t ]*/)[0].replace(/\t/g, '    ').length;
      line.style.setProperty('--code-indent', `${indent}ch`);
      // Keep the original newline in textContent for verbatim copy, but hide it
      // visually in wrap mode: each logical line then supplies its own line box.
      const walker = document.createTreeWalker(line, NodeFilter.SHOW_TEXT);
      let last, node;
      while ((node = walker.nextNode())) last = node;
      if (last?.textContent.endsWith('\n')) {
        const newline = last.splitText(last.length - 1);
        const end = document.createElement('span');
        end.className = 'manual-code__newline';
        newline.replaceWith(end);
        end.append(newline);
      }
    });
    const expand = block.querySelector('.manual-code__expand');
    if (expand) {
      const source = block.querySelector('.manual-code__source');
      source.tabIndex = -1;
      const expandLabel = expand.textContent;
      block.classList.add('manual-code--collapsed');
      expand.parentElement.hidden = false;
      expand.addEventListener('click', () => {
        const collapsed = block.classList.toggle('manual-code--collapsed');
        expand.setAttribute('aria-expanded', String(!collapsed));
        expand.textContent = collapsed ? expandLabel : 'Collapse code';
        if (collapsed) expand.scrollIntoView({ block: 'nearest' });
        else {
          source.focus({ preventScroll: true });
          source.scrollIntoView({ block: 'start' });
        }
      });
    }
    const wrap = block.querySelector('.manual-code__wrap');
    wrap.addEventListener('click', () => {
      const wrapped = block.classList.toggle('manual-code--wrapped');
      wrap.setAttribute('aria-pressed', String(wrapped));
      wrap.setAttribute('aria-label', wrapped ? 'Disable code wrapping' : 'Wrap code lines');
      wrap.textContent = wrapped ? 'Unwrap' : 'Wrap';
      update();
    });
  });
  const update = () => blocks.forEach((block) => {
    const pre = block.querySelector('pre');
    const overflows = pre.scrollWidth > pre.clientWidth + 1;
    block.querySelector('.manual-code__wrap').hidden = !(overflows || block.classList.contains('manual-code--wrapped'));
    block.querySelector('.manual-code__overflow').hidden = !overflows;
  });
  const observer = new ResizeObserver(update);
  blocks.forEach((block) => observer.observe(block));
  document.fonts.ready.then(update);
  update();
})();

// The quick-start examples use the same command for display and copying.
(() => {
  const tabs = document.querySelector('.manual-launch-tabs');
  if (!tabs) return;
  const buttons = [...tabs.querySelectorAll('[role="tab"]')];
  const panel = document.getElementById('launch-command');
  panel.setAttribute('role', 'tabpanel');
  panel.setAttribute('tabindex', '0');
  const select = (button) => {
    buttons.forEach((tab) => {
      tab.setAttribute('aria-selected', String(tab === button));
      tab.tabIndex = tab === button ? 0 : -1;
    });
    panel.setAttribute('aria-labelledby', button.id);
    panel.querySelector('.manual-launch__command').textContent = button.dataset.command;
    panel.querySelector('.manual-terminal__comment').textContent = button.dataset.comment;
    const copy = panel.querySelector('[data-copy-text]');
    copy.dataset.copyText = button.dataset.command;
    delete copy.dataset.copyState;
    copy.querySelector('[data-copy-label]').textContent = 'Copy';
  };
  buttons.forEach((button, i) => {
    button.addEventListener('click', () => select(button));
    button.addEventListener('keydown', (event) => {
      const next = { ArrowRight: (i + 1) % buttons.length, ArrowLeft: (i + buttons.length - 1) % buttons.length, Home: 0, End: buttons.length - 1 }[event.key];
      if (next === undefined) return;
      event.preventDefault();
      select(buttons[next]);
      buttons[next].focus();
    });
  });
  select(buttons[0]);
  tabs.hidden = false;
})();
