// A live form (layouts/_partials/form.html, data-form-live) is sent in the background to server/forms/send.php,
// so the visitor stays on the page: the button says it is sending, then the status line says what happened. On
// success the form is emptied; on failure what was typed stays, and the form's offline line (the email way)
// follows the message. The browser's own checks of required fields and email addresses run first. Without
// script the form is posted normally and send.php answers with a page of its own.
document.querySelectorAll('form[data-form-live]').forEach((form) => {
  const status = form.querySelector('.form-status');
  const button = form.querySelector('button[type="submit"]');
  const fallback = form.querySelector('.form-fallback');
  const label = button.textContent;
  let busy = false;
  const say = (text, state) => {
    status.textContent = text;
    status.dataset.state = state;
    if (state === 'error' && fallback) status.append(' ', fallback.content.cloneNode(true));
  };
  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (busy) return;
    busy = true;
    button.disabled = true;
    button.textContent = 'Sending…';
    say('', 'busy');
    try {
      const response = await fetch(form.action, {
        method: 'POST', body: new FormData(form), headers: { Accept: 'application/json' }, credentials: 'same-origin',
      });
      const data = await response.json().catch(() => ({}));
      if (response.ok && data.ok) {
        form.reset();
        say(data.message || 'Thanks, it’s sent.', 'sent');
      } else {
        say(data.message || 'Sending didn’t work.', 'error');
      }
    } catch {
      say('Sending didn’t work: the connection failed.', 'error');
    } finally {
      busy = false;
      button.disabled = false;
      button.textContent = label;
    }
  });
});
