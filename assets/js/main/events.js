// ------------------------------------------------------------------ events (data/events.yaml)
// The build already left out what was over when the site was built; this checks again by the
// visitor's clock, so a page built days ago still shows the right next event.
// [data-ev-next]: show the first [data-ev] that has not ended, hide the block when none is left.
// [data-ev-next-list] (home page): hide every ended event, add the line for no dates when none is left.
// /events/: move ended events from the upcoming list to the past list (latest first), and add the same
// line when the upcoming list is empty. The line is not in the page while events are listed.
// [data-ev-live] / [data-ev-over-note] (an event's page): swap the actions for the "took place" line.
// [data-ev-local]: add the start time in the visitor's own time zone when it differs.
(() => {
  const now = Date.now();
  const over = (el) => Date.parse(el.dataset.evEnds) <= now;
  const noDates = (list) => {
    if (list.parentElement.querySelector('[data-ev-empty]')) return;
    const p = document.createElement('p');
    p.className = 'event-empty';
    p.dataset.evEmpty = '';
    p.append('No dates are set right now. New ones are announced in the ');
    const a = document.createElement('a');
    a.href = list.dataset.evNewsletter || '';
    a.textContent = 'newsletter';
    p.append(a, '.');
    list.after(p);
  };
  document.querySelectorAll('[data-ev-next]').forEach((box) => {
    const items = [...box.querySelectorAll('[data-ev]')];
    const next = items.find((el) => !over(el));
    items.forEach((el) => { el.hidden = el !== next; });
    if (!next) box.hidden = true;
  });
  document.querySelectorAll('[data-ev-next-list]').forEach((list) => {
    const items = [...list.querySelectorAll('[data-ev]')];
    items.forEach((el) => { el.hidden = over(el); });
    if (items.length && items.every((el) => el.hidden)) noDates(list);
  });
  const up = document.querySelector('[data-ev-upcoming]');
  const past = document.querySelector('[data-ev-past]');
  if (up && past) {
    const gone = [...up.querySelectorAll('[data-ev]')].filter(over);
    if (gone.length) {
      gone.forEach((el) => past.append(el));
      [...past.children].sort((a, b) => b.dataset.evStart - a.dataset.evStart).forEach((el) => past.append(el));
      const h = document.querySelector('[data-ev-past-h]');
      if (h) h.hidden = false;
      if (!up.children.length) noDates(up);
    }
  }
  // an event's own page (events/page-body.html): once the event is over, Register and Add to calendar
  // give way to the line that says when it took place, which then also carries the #register anchor
  const live = document.querySelector('[data-ev-live]');
  const note = document.querySelector('[data-ev-over-note]');
  if (live && note && over(live)) {
    live.hidden = true;
    live.removeAttribute('id');
    note.id = 'register';
    note.hidden = false;
  }
  document.querySelectorAll('[data-ev-local]').forEach((el) => {
    try {
      const t = new Date(el.dataset.evLocal);
      const opts = { weekday: 'long', day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit', timeZoneName: 'short' };
      const mine = new Intl.DateTimeFormat(undefined, opts).format(t);
      const theirs = new Intl.DateTimeFormat(undefined, { ...opts, timeZone: el.dataset.evTz }).format(t);
      if (mine !== theirs) { el.textContent = `In your time zone: ${mine}`; el.hidden = false; }
    } catch (e) { /* an old browser without time zones: the event's own time stays */ }
  });
})();

// The countdown at the end of an event's meta line (events/card.html, home.html): "today", "tomorrow",
// "in 6 days", "in 3 months", by the visitor's clock; it stays hidden once the event has started.
document.querySelectorAll('[data-ev-countdown]').forEach((chip) => {
  const start = Number(chip.dataset.evCountdown) * 1000;
  const day = (t) => { const d = new Date(t); d.setHours(0, 0, 0, 0); return d.getTime(); };
  const days = Math.round((day(start) - day(Date.now())) / 864e5);
  if (start <= Date.now() && days < 0) return;
  chip.textContent = days <= 0 ? 'today' : days === 1 ? 'tomorrow' : days < 45 ? `in ${days} days` : `in ${Math.round(days / 30.4)} months`;
  chip.hidden = false;
});
