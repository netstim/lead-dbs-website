// ------------------------------------------------------------------ videos (youtube / vimeo shortcodes)
// Nothing loads from YouTube or Vimeo until the visitor starts a video: then the privacy-enhanced
// player takes the place of the button. A click with a modifier key opens the video's own page.
// On a video-grid (the videos page) a card's video opens in a popup instead (.v-box): the player
// large on black, the card's tag, title and sentence under it, its chapters beside it as buttons that
// start the video at that time. In the card the chapters fold to one "n chapters" button. Closing the
// popup removes the player, which stops the video.
const vbox = (() => {
  const cards = document.querySelectorAll('.video-card');
  if (!cards.length || !window.HTMLDialogElement) return null;
  const d = document.createElement('dialog');
  d.className = 'v-box';
  d.setAttribute('aria-label', 'Video');
  d.innerHTML = '<div class="v-box__main"><div class="v-box__player"></div><div class="v-box__info"><div class="v-box__words"></div>'
    + '<form method="dialog"><button class="v-box__close" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6 6 18"/></svg></button></form></div></div><div class="v-box__chapters" hidden></div>';
  document.body.append(d);
  const player = d.querySelector('.v-box__player'), info = d.querySelector('.v-box__words'), side = d.querySelector('.v-box__chapters');
  let src = '', label = '';
  const chapters = new WeakMap();  // a card's chapters, taken out of the card
  const secs = (t) => t.split(':').reduce((n, x) => n * 60 + Number(x), 0);
  const play = (start) => {
    let u = src;
    if (start) u = /vimeo/.test(u) ? `${u}#t=${start}s` : `${u}&start=${start}`;
    const f = document.createElement('iframe');
    f.src = u; f.title = label;
    f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
    f.allowFullscreen = true;
    f.referrerPolicy = 'strict-origin-when-cross-origin';
    player.replaceChildren(f);
  };
  d.addEventListener('close', () => { player.replaceChildren(); document.documentElement.classList.remove('v-box-open'); });
  d.addEventListener('click', (e) => {
    if (e.target === d) { d.close(); return; }
    const c = e.target.closest('.v-box__chapter');
    if (!c) return;
    side.querySelectorAll('.v-box__chapter').forEach((b) => b.setAttribute('aria-current', String(b === c)));
    play(Number(c.dataset.t));
  });
  const open = (card, start = 0) => {
    const box = card.querySelector('.video-embed');
    src = box.dataset.embed; label = box.dataset.embedTitle;
    info.replaceChildren();
    const tag = card.querySelector('.video-card__tag'), h = card.querySelector('h2, h3');
    if (tag) { const t = document.createElement('p'); t.className = 'v-box__tag'; t.textContent = tag.textContent; info.append(t); }
    if (h) { const t = document.createElement('h2'); t.className = 'v-box__title'; t.textContent = [...h.childNodes].filter((n) => !n.classList?.contains('heading-anchor')).map((n) => n.textContent).join('').trim(); info.append(t); }
    card.querySelectorAll(':scope > p:not(.video-card__tag)').forEach((p) => { const t = p.cloneNode(true); t.className = 'v-box__text'; info.append(t); });
    const rows = [...(chapters.get(card)?.querySelectorAll('li') || [])];
    side.hidden = !rows.length;
    side.replaceChildren();
    if (rows.length) {
      const hd = document.createElement('p'); hd.className = 'v-box__chapters-h'; hd.textContent = `${rows.length} chapters`;
      const ol = document.createElement('ol');
      rows.forEach((li) => {
        const t = li.querySelector('time').textContent, n = secs(t);
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'v-box__chapter'; b.dataset.t = n;
        b.setAttribute('aria-current', String(n === start));
        b.innerHTML = '<time></time><span></span>';
        b.firstChild.textContent = t; b.lastChild.textContent = li.querySelector('span').textContent;
        const item = document.createElement('li'); item.append(b); ol.append(item);
      });
      side.append(hd, ol);
    }
    d.classList.toggle('v-box--chapters', rows.length > 0);
    play(start);
    document.documentElement.classList.add('v-box-open');
    d.showModal();
    d.querySelector('.v-box__close').focus();
  };
  cards.forEach((card) => {
    const ch = card.querySelector('.chapters');
    if (!ch) return;
    const n = ch.querySelectorAll('li').length;
    const b = document.createElement('button');
    b.type = 'button'; b.className = 'video-card__chapters';
    b.innerHTML = `<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 4h10M3 8h10M3 12h6"/></svg>${n} chapters`;
    b.addEventListener('click', () => open(card));
    chapters.set(card, ch);
    ch.replaceWith(b);
  });
  return open;
})();

document.addEventListener('click', (e) => {
  const a = e.target.closest?.('.video-embed__start');
  if (!a || e.metaKey || e.ctrlKey || e.shiftKey || e.button !== 0) return;
  const box = a.closest('.video-embed');
  e.preventDefault();
  const card = box.closest('.video-card');
  if (vbox && card) { vbox(card); return; }
  const f = document.createElement('iframe');
  f.src = box.dataset.embed;
  f.title = box.dataset.embedTitle;
  f.allow = 'autoplay; fullscreen; picture-in-picture; encrypted-media';
  f.allowFullscreen = true;
  f.referrerPolicy = 'strict-origin-when-cross-origin';
  box.replaceChildren(f);
  box.classList.add('is-playing');
  f.focus();
});
