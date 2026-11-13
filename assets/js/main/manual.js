// Reuse the chapter tree in a modal drawer; keep chapter and section controls
// available throughout long mobile articles. Native dialogs contain keyboard focus.
(() => {
  const fold = document.querySelector('.manual-nav__fold');
  if (!fold) return;
  const tree = fold.querySelector('.manual-nav__tree');
  const rail = document.querySelector('.manual-nav');
  const main = document.querySelector('.manual');
  const bar = document.querySelector('.manual-mobile-bar');
  const drawer = document.querySelector('#manual-drawer');
  const trigger = document.querySelector('.manual-menu');
  const body = drawer.querySelector('.manual-drawer__body');
  const contents = document.querySelector('#manual-contents');
  const sections = document.querySelector('.manual-sections');
  const mobile = matchMedia('(max-width: 767px)');
  const pairs = [[drawer, trigger], ...(contents ? [[contents, sections]] : [])];
  const reveal = (box) => {
    const current = tree.querySelector('[aria-current="page"]');
    if (!current) return;
    const item = current.getBoundingClientRect();
    const bounds = box.getBoundingClientRect();
    // Do not recenter a chapter that is already visible: that moves the whole rail
    // when navigating between nearby pages. Scroll only enough to reveal it.
    if (item.top < bounds.top) box.scrollTop += item.top - bounds.top;
    else if (item.bottom > bounds.bottom) box.scrollTop += item.bottom - bounds.bottom;
  };
  const navigationKey = 'lead-manual-navigation';
  let previousNavigation;
  try {
    previousNavigation = JSON.parse(sessionStorage.getItem(navigationKey));
    sessionStorage.removeItem(navigationKey);
  } catch { /* Navigation works when browser storage is unavailable. */ }
  tree.addEventListener('click', (event) => {
    const link = event.target.closest('a');
    if (!link || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const target = new URL(link.href);
    if (target.origin !== location.origin) return;
    const box = mobile.matches ? body : rail;
    try {
      sessionStorage.setItem(navigationKey, JSON.stringify({ path: target.pathname, scrollTop: box.scrollTop }));
    } catch { /* Storage is optional. */ }
  });
  const close = () => pairs.forEach(([dialog]) => { if (dialog.open) dialog.close(); });
  pairs.forEach(([dialog, button]) => {
    dialog.addEventListener('close', () => {
      button.setAttribute('aria-expanded', 'false');
      if (!pairs.some(([d]) => d.open)) document.documentElement.classList.remove('manual-drawer-open');
    });
    dialog.querySelector('[data-manual-close]').addEventListener('click', close);
    dialog.addEventListener('click', (e) => {
      if (e.target === dialog || e.target.closest('a')) close();
    });
    button.addEventListener('click', () => {
      dialog.showModal();
      button.setAttribute('aria-expanded', 'true');
      document.documentElement.classList.add('manual-drawer-open');
      if (dialog === drawer) reveal(body);
      else {
        const links = [...dialog.querySelectorAll('a[href^="#"]')];
        let current = links[0];
        links.forEach((a) => {
          a.removeAttribute('aria-current');
          const heading = document.getElementById(decodeURIComponent(a.hash.slice(1)));
          if (heading?.getBoundingClientRect().top <= innerHeight / 3) current = a;
        });
        current?.setAttribute('aria-current', 'location');
        if (current) {
          const list = dialog.querySelector('nav');
          list.scrollTop += current.getBoundingClientRect().top - list.getBoundingClientRect().top - list.clientHeight / 3;
        }
      }
    });
  });
  const update = () => {
    close();
    main.classList.toggle('manual--mobile-ready', mobile.matches);
    bar.hidden = !mobile.matches;
    pairs.forEach(([, button]) => { button.hidden = !mobile.matches; });
    fold.hidden = mobile.matches;
    fold.open = true;
    (mobile.matches ? body : fold).append(tree);
    if (!mobile.matches) {
      if (previousNavigation?.path === location.pathname && Number.isFinite(previousNavigation.scrollTop)) rail.scrollTop = previousNavigation.scrollTop;
      previousNavigation = null;
      reveal(rail);
    }
  };
  update();
  mobile.addEventListener('change', update);
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') close();
  }, true);
})();
// Use the shared clipboard feedback for page URLs, including a copied section hash.
document.querySelector('[data-copy-link]')?.addEventListener('click', async (event) => {
  const button = event.currentTarget;
  const label = button.querySelector('[data-copy-label]');
  let status = button.querySelector('[role="status"]');
  if (!status) {
    status = document.createElement('span');
    status.className = 'sr-only';
    status.setAttribute('role', 'status');
    button.append(status);
  }
  clearTimeout(button.copyTimer);
  try {
    await navigator.clipboard.writeText(location.href);
    label.textContent = 'Link copied';
    status.textContent = 'Page link copied.';
  } catch {
    label.textContent = 'Copy failed';
    status.textContent = 'Copy the address from your browser.';
  }
  button.copyTimer = setTimeout(() => { label.textContent = 'Copy link'; status.textContent = ''; }, 2000);
});

// Preview long examples without hiding their full source from the copy control.
// No-JavaScript readers get the complete code. Overflow cues reflect the actual viewport.
(() => {
  const blocks = [...document.querySelectorAll('.manual-code')];
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
    const expands = [...block.querySelectorAll('.manual-code__expand')];
    if (expands.length) block.classList.add('manual-code--collapsed');
    expands.forEach((expand) => {
      expand.hidden = false;
      expand.addEventListener('click', () => {
        const collapsed = block.classList.toggle('manual-code--collapsed');
        expands.forEach((button) => {
          button.setAttribute('aria-expanded', String(!collapsed));
          button.textContent = button.classList.contains('manual-code__expand--top')
            ? (collapsed ? 'Expand' : 'Collapse')
            : (collapsed ? `Show all ${block.dataset.codeLines} lines` : 'Collapse code');
        });
        if (collapsed && block.getBoundingClientRect().top < 0) block.scrollIntoView({ block: 'start' });
      });
    });
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
    block.querySelector('.manual-code__foot').hidden = !block.dataset.codeLines;
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
