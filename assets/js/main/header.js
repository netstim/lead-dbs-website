// The header (layouts/_partials/header.html, nav.html): adapted from NetStim's header script, plus
// Lead-DBS dark-ground awareness for dark pages (Download, Gallery).
// The phone menu sheet (lib/dialog.js), its groups that unfold, and the sheets of the desktop menu:
// a sheet opens from its arrow button (click, Enter, Space; a second press closes it), on hover with a
// mouse, and with the Down arrow key. Escape closes it and hands focus back to the button; it also closes
// on a press outside and when focus moves on. Without this script the sheets open on hover and focus.
import { wireDialog } from '../lib/dialog.js';

(() => {
  const phone = document.querySelector('.phone-menu');
  const menu = document.querySelector('[data-menu-open]');
  const nav = document.querySelector('.desktop-nav');
  const header = document.querySelector('.site-header');
  if (!nav || !header) return;
  const wide = matchMedia('(min-width: 1024px)');

  if (phone && menu) {
    wireDialog(phone, [menu]);
    for (const button of phone.querySelectorAll('.nav-group')) {
      button.addEventListener('click', () => {
        const open = button.getAttribute('aria-expanded') !== 'true';
        button.setAttribute('aria-expanded', String(open));
        document.getElementById(button.getAttribute('aria-controls')).hidden = !open;
      });
    }
    phone.addEventListener('click', (event) => {
      if (event.target.closest('a[href]')) phone.close();
    });
  }

  // one sheet is open at a time; `pinned` means a button or key opened it, so the mouse leaving keeps it.
  // `has-open` dims the other items; `is-closing` fades a sheet out (not when switching directly to another).
  let current = null;
  let pinned = false;
  let pressed = false;
  let timer;
  const toggleOf = (item) => item.querySelector('.nav-toggle');

  function hide(fade = true) {
    clearTimeout(timer);
    for (const item of nav.querySelectorAll('.is-closing')) item.classList.remove('is-closing');
    if (!current) return;
    current.classList.remove('is-open', 'is-switch');
    current.classList.toggle('is-closing', fade);
    toggleOf(current)?.setAttribute('aria-expanded', 'false');
    nav.classList.remove('has-open');
    header.classList.remove('is-menu-open');
    current = null;
    pinned = false;
  }

  function show(item, pin) {
    clearTimeout(timer);
    if (current === item) { pinned ||= pin; return; }
    const swap = Boolean(current);
    hide(false);
    current = item;
    pinned = pin;
    item.classList.add('is-open');
    item.classList.toggle('is-switch', swap);
    toggleOf(item)?.setAttribute('aria-expanded', 'true');
    nav.classList.add('has-open');
    header.classList.add('is-menu-open');
  }

  for (const item of nav.querySelectorAll('.has-sub')) {
    const toggle = toggleOf(item);
    const panel = item.querySelector('.nav-panel');
    if (!toggle || !panel) continue;
    panel.addEventListener('animationend', (event) => {
      if (event.target === panel && !event.pseudoElement) item.classList.remove('is-closing');
    });
    toggle.addEventListener('click', () => (current === item && pinned ? hide() : show(item, true)));
    // hover: a short wait before the first sheet, none when moving from one open sheet to the next
    item.addEventListener('pointerenter', (event) => {
      if (event.pointerType !== 'mouse') return;
      clearTimeout(timer);
      if (current) show(item, false);
      else timer = setTimeout(() => show(item, false), 100);
    });
    item.addEventListener('pointerleave', (event) => {
      if (event.pointerType !== 'mouse') return;
      clearTimeout(timer);
      if (current === item && !pinned) timer = setTimeout(hide, 160);
    });
    // Tab walks through the open sheet and closes it on the way out; `pressed` keeps a Safari click alive.
    item.addEventListener('focusout', (event) => {
      if (current !== item || item.contains(event.relatedTarget)) return;
      if (event.relatedTarget || !pressed) hide();
    });
    item.addEventListener('keydown', (event) => {
      if (event.key !== 'ArrowDown' && event.key !== 'ArrowUp') return;
      const links = [...item.querySelectorAll('.nav-sub__link')];
      const at = links.indexOf(document.activeElement);
      const next = event.key === 'ArrowDown' ? at + 1 : at - 1;
      if (at === -1 && event.key === 'ArrowUp') return;
      event.preventDefault();
      show(item, true);
      (links[Math.min(next, links.length - 1)] || toggle).focus();
    });
  }

  document.addEventListener('pointerdown', (event) => {
    pressed = Boolean(current?.contains(event.target));
    if (current && !pressed) hide();
  }, true);
  for (const type of ['pointerup', 'pointercancel']) document.addEventListener(type, () => { pressed = false; }, true);
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape' || !current) return;
    const item = current;
    const inside = item.contains(document.activeElement);
    hide();
    if (inside) toggleOf(item)?.focus();
  });
  addEventListener('pageshow', (event) => { if (event.persisted) hide(false); });
  wide.addEventListener('change', (event) => {
    if (event.matches && phone?.open) phone.close();
    if (!event.matches) hide(false);
  });
  nav.classList.add('is-ready');
})();

// Dark-ground awareness for Lead-DBS dark pages (Download, Gallery): while a [data-nav-dark] region sits
// directly beneath the header, the bar takes the dark ground too.
(() => {
  const header = document.querySelector('.site-header');
  if (!header) return;
  const grounds = [...document.querySelectorAll('[data-nav-dark]')];
  let queued = false;
  const update = () => {
    queued = false;
    const box = header.getBoundingClientRect();
    const top = box.bottom;
    const bottom = box.bottom + box.height;
    const overlap = grounds.reduce((sum, g) => {
      const r = g.getBoundingClientRect();
      return sum + Math.max(0, Math.min(r.bottom, bottom) - Math.max(r.top, top));
    }, 0);
    const dark = overlap / Math.max(1, box.height) > 0.5;
    header.classList.toggle('is-dark', dark);
    header.classList.toggle('is-scrolled', window.scrollY > 0);
  };
  const queue = () => { if (!queued) { queued = true; requestAnimationFrame(update); } };
  addEventListener('scroll', queue, { passive: true });
  addEventListener('resize', queue);
  update();
  requestAnimationFrame(() => document.documentElement.classList.add('nav-ready'));
})();
