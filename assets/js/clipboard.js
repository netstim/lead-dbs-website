// Shared clipboard behavior. data-copy names an element ID; data-copy-text holds a literal command.
// Read the target on each click so citation tabs can change it. Buttons stay hidden without the API.
(() => {
  if (!navigator.clipboard?.writeText) return;
  document.querySelectorAll('[data-copy], [data-copy-text]').forEach((button) => {
    const label = button.querySelector('[data-copy-label]') || [...button.childNodes].find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
    const original = label?.textContent;
    let status = button.parentElement.querySelector('[data-copy-status]');
    if (!status) {
      status = document.createElement('span');
      status.className = 'sr-only';
      status.setAttribute('role', 'status');
      button.after(status);
    }
    let timer;
    button.hidden = false;
    button.addEventListener('click', async () => {
      clearTimeout(timer);
      button.disabled = true;
      status.textContent = '';
      try {
        const target = document.getElementById(button.dataset.copy);
        const text = button.hasAttribute('data-copy-text')
          ? button.dataset.copyText
          : (target?.hasAttribute('data-copy-verbatim') ? target.textContent : target?.innerText)?.trim();
        if (text == null) throw new Error('Missing copy target');
        await navigator.clipboard.writeText(text);
        button.dataset.copyState = 'copied';
        status.textContent = 'Copied.';
        if (label) label.textContent = 'Copied';
      } catch {
        button.dataset.copyState = 'error';
        status.textContent = 'Could not copy: please select the text instead.';
        if (label) label.textContent = 'Copy failed';
      } finally {
        button.disabled = false;
        timer = setTimeout(() => { if (label) label.textContent = original; delete button.dataset.copyState; }, 2000);
      }
    });
  });
})();
