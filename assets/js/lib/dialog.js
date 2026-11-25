// Shared modal behaviour (phone menu): open with showModal and focus the dialog itself (so a
// tap never paints a focus ring on its first button; a dialog may name another start with data-focus-start),
// contain Tab, close on a click outside the panel (the pointer must also have gone down outside it, so the
// tap that opened it never closes it; WebKit reports such clicks on <html>, hence the document listener),
// and return focus to the trigger.
export function wireDialog(dialog, buttons, { dismiss } = {}) {
  let trigger;
  let downOutside = false;
  const outside = (event) => {
    const { left, right, top, bottom } = dialog.getBoundingClientRect();
    return event.clientX < left || event.clientX > right || event.clientY < top || event.clientY > bottom;
  };
  const open = (button) => {
    if (dialog.open) return;
    trigger = button;
    dialog.showModal();
    const start = dialog.querySelector('[data-focus-start]');
    (start || dialog).focus({ preventScroll: true });
  };
  for (const button of buttons) button.addEventListener('click', () => open(button));
  dialog.addEventListener('close', () => { downOutside = false; trigger?.focus({ preventScroll: true }); });
  document.addEventListener('pointerdown', (event) => { downOutside = dialog.open && outside(event); }, true);
  document.addEventListener('click', (event) => {
    if (dialog.open && downOutside && outside(event)) (dismiss ? dismiss() : dialog.close());
    downOutside = false;
  }, true);
  // Tab cycles through the dialog's controls (managed here: WebKit's own Tab order skips links)
  dialog.addEventListener('keydown', (event) => {
    if (event.key !== 'Tab') return;
    const focusable = [...dialog.querySelectorAll('a[href], button, input, summary, [tabindex="0"]')]
      .filter((el) => !el.disabled && el.getClientRects().length && !el.closest('[hidden]'));
    if (!focusable.length) return;
    event.preventDefault();
    const at = focusable.indexOf(document.activeElement);
    const next = event.shiftKey ? (at <= 0 ? focusable.length - 1 : at - 1) : (at === -1 || at === focusable.length - 1 ? 0 : at + 1);
    focusable[next].focus();
  });
  return open;
}
