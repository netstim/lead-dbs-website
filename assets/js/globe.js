// The wireframe globe of the home page's "Downloaded in N countries" section (#worldwide): graticule,
// coastlines and borders as thin ink lines on the white page, the far side showing through faintly. It
// replays the downloads of Lead-DBS from November 2015 to now, a month every 0.3 seconds: a country
// lights up periwinkle with its first download (a coral ring marks the moment) and grows a small lead
// with a coral tip; both deepen and grow as its downloads add up. The globe turns once in the replay,
// holds at the end for a few seconds and starts again. A mouse can drag it and read a country's
// downloads so far; the round button pauses it; with reduced motion it shows the end, still.
// Data: data/downloads.json (tools/downloads.py), published by layouts/home.html as a JSON file that is
// fetched with the map. This file, with d3-array, d3-geo and topojson-client (assets/js/vendor/, ISC)
// bundled before it, is loaded by assets/js/main/home.js when the section comes near the screen; the map
// (assets/data/world-110m.json, Natural Earth via world-atlas) and the figures are fetched then, at the
// same distance.
(() => {
  const sec = document.getElementById('worldwide');
  if (!sec || !sec.dataset.map || !sec.dataset.downloads || !window.d3 || !window.topojson || !('IntersectionObserver' in window)) return;
  const $ = (s) => sec.querySelector(s);
  const stage = $('[data-globe-stage]'), canvas = $('[data-globe]'), tip = $('[data-globe-tip]'), now = $('[data-globe-now]'), btn = $('[data-globe-pause]');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const fmt = new Intl.NumberFormat('en'), RAD = Math.PI / 180;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const MONTH = 300, HOLD = 5000; // milliseconds a month takes, and the pause at the end
  const LON = -20, LAT = 24; // where the globe looks at the start and the end (the Atlantic)
  const rnd = (s) => { const h = Math.sin(s * 127.1 + 311.7) * 43758.5453; return h - Math.floor(h); };

  // the page's colours, as "r,g,b"
  // (read again when the theme changes, so the globe follows light and dark)
  const probe = document.createElement('i'); probe.hidden = true; sec.append(probe);
  const rgb = (v) => { probe.style.color = `var(${v})`; return (getComputedStyle(probe).color.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).join(','); };
  let INK, TINT, ACTION, CORAL, BG, repaint = () => {};
  const readColours = () => { INK = rgb('--p-ink'); TINT = rgb('--p-tint-1'); ACTION = rgb('--p-action'); CORAL = rgb('--p-accent'); BG = rgb('--p-bg'); repaint(); };
  readColours();
  new MutationObserver(readColours).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  let started = false;
  const load = new IntersectionObserver((es) => {
    if (started || !es.some((e) => e.isIntersecting)) return;
    started = true; load.disconnect();
    const json = (u) => fetch(u).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
    Promise.all([json(sec.dataset.map), json(sec.dataset.downloads)]).then(([T, D]) => start(T, D)).catch(() => {});
  }, { rootMargin: '800px 0px' });
  load.observe(sec);

  function start(T, D) {
    // the downloads: per country, the running total at the start of each month (and at the end)
    const M = D.months.length;
    const names = new Map(D.countries.map((c) => [c[0], c[1]])), lmax = Math.log1p(D.countries[0][2]);
    const cum = new Map(D.countries.map((c) => [c[0], new Float64Array(M + 1)])), all = new Float64Array(M + 1);
    D.months.forEach(([, by], i) => {
      cum.forEach((a, id) => { a[i + 1] = a[i] + (by[id] || 0); });
      all[i + 1] = all[i] + Object.values(by).reduce((a, b) => a + b, 0);
    });
    // the running total at a moment of the replay (t in months; a month's downloads come in evenly)
    const at = (a, t) => { const i = Math.min(M - 1, Math.floor(t)), f = Math.min(1, t - i); return a[i] + (a[i + 1] - a[i]) * f; };
    const month = (t) => { const [y, m] = D.months[Math.min(M - 1, Math.floor(t))][0].split('-'); return new Date(Date.UTC(+y, m - 1, 15)).toLocaleDateString('en-GB', { month: 'short', year: 'numeric', timeZone: 'UTC' }); };

    sec.classList.add('is-drawn'); // the figure takes its place before it is measured
    const countries = topojson.feature(T, T.objects.countries).features.filter((f) => f.id !== '010' && cum.has(f.id));
    const land = topojson.feature(T, T.objects.land), borders = topojson.mesh(T, T.objects.countries, (a, b) => a !== b);
    const grat = d3.geoGraticule().step([20, 20])(), sphere = { type: 'Sphere' };
    const byId = new Map(countries.map((f) => [f.id, f]));
    // where a country's lead stands: the middle of its largest part, a chosen place for a few large or
    // spread-out countries, and places too small for the map
    const SPOTS = { '840': [-90, 38], '124': [-79, 45.5], '156': [114, 31], '076': [-46, -20], '643': [38, 55.5], '036': [147, -33], '356': [78, 20] };
    const EXTRA = { '344': [114.17, 22.32], '702': [103.82, 1.35], '446': [113.55, 22.19], '048': [50.55, 26.07], '470': [14.44, 35.9], '020': [1.52, 42.51], '312': [-61.55, 16.25], '638': [55.53, -21.13], '660': [-63.05, 18.22], '316': [144.79, 13.44] };
    const pins = [];
    D.countries.forEach(([id], i) => {
      const f = byId.get(id); let c = SPOTS[id] || EXTRA[id] || null;
      if (!c && f) {
        let g = f.geometry;
        if (g.type === 'MultiPolygon') g = g.coordinates.map((k) => ({ type: 'Polygon', coordinates: k })).reduce((a, b) => (d3.geoArea(b) > d3.geoArea(a) ? b : a));
        c = d3.geoCentroid(g);
      }
      if (c) pins.push({ id, ll: c, f, a: cum.get(id), lean: (rnd(i * 3.1) - .5) * .5 });
    });

    const front = d3.geoOrthographic().clipAngle(90).precision(.4), back = d3.geoOrthographic().clipAngle(90).precision(.6).reflectX(true);
    const pf = d3.geoPath(front, ctx), pb = d3.geoPath(back, ctx);
    let W, R, dpr, visible = false, playing = !reduced, last = performance.now(), hold = 0, shown = '', offset = [0, 0], drag = null, hover = null, dirty = true;
    let clock = reduced ? M : 0; // the replay's moment, in months since November 2015
    const born = new Map(); // country → when it lit up (for the ring and the fade-in)
    let leads = [];
    repaint = () => { dirty = true; };
    const restart = () => { clock = 0; hold = 0; born.clear(); };

    function layout() {
      dpr = Math.min(2, devicePixelRatio || 1); W = stage.clientWidth; canvas.width = canvas.height = Math.round(W * dpr); R = W * .46;
      front.scale(R).translate([W / 2, W / 2]); back.scale(R).translate([W / 2, W / 2]); dirty = true;
    }
    function draw(t) {
      // one turn in the replay, from the Atlantic back to it
      const lon = LON - 360 * clock / M + offset[0], lat = LAT + offset[1];
      front.rotate([-lon, -lat]); back.rotate([-lon + 180, lat]);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, W); ctx.lineJoin = 'round';
      // the far side, faint
      ctx.lineWidth = 1; ctx.strokeStyle = `rgba(${INK},.05)`; ctx.beginPath(); pb(grat); ctx.stroke();
      ctx.strokeStyle = `rgba(${INK},.13)`; ctx.beginPath(); pb(land); ctx.stroke();
      // the near side: graticule, the countries with downloads (deeper with more), borders, coast, the sphere's edge
      ctx.strokeStyle = `rgba(${INK},.1)`; ctx.beginPath(); pf(grat); ctx.stroke();
      ctx.fillStyle = `rgba(${BG},.82)`; ctx.beginPath(); pf(land); ctx.fill();
      for (const p of pins) {
        if (!p.f || !born.has(p.id)) continue;
        const n = at(p.a, clock), lit = Math.min(1, (t - born.get(p.id)) / 800);
        ctx.fillStyle = `rgba(${TINT},${(.3 + .7 * Math.min(1, Math.log1p(n) / lmax)) * lit})`; ctx.beginPath(); pf(p.f); ctx.fill();
      }
      if (hover && hover.f) { ctx.fillStyle = `rgba(${ACTION},.28)`; ctx.beginPath(); pf(hover.f); ctx.fill(); }
      ctx.lineWidth = .6; ctx.strokeStyle = `rgba(${INK},.22)`; ctx.beginPath(); pf(borders); ctx.stroke();
      ctx.lineWidth = 1; ctx.strokeStyle = `rgba(${INK},.62)`; ctx.beginPath(); pf(land); ctx.stroke();
      ctx.strokeStyle = `rgba(${INK},.4)`; ctx.beginPath(); pf(sphere); ctx.stroke();
      // the leads: taller with more downloads; the newest country rings once
      const c = [lon, lat], cx = W / 2; leads = [];
      for (const p of pins) {
        if (!born.has(p.id) || d3.geoDistance(p.ll, c) > Math.PI / 2 - .02) continue;
        const s = Math.min(1, Math.log1p(at(p.a, clock)) / lmax), base = front(p.ll), age = (t - born.get(p.id)) / 1000;
        const grow = 1 - Math.pow(1 - Math.min(1, age / 1.1), 3), fresh = Math.max(0, 1 - age / 2), h = (.015 + .11 * s) * grow;
        const end = [cx + (base[0] - cx) * (1 + h), cx + (base[1] - cx) * (1 + h)]; end[0] += (end[1] - base[1]) * p.lean * .3; end[1] -= (end[0] - base[0]) * p.lean * .3;
        // seen end-on (near the middle) a lead is short: give it a little height towards the top
        end[1] -= R * (.012 + .045 * s) * grow * Math.cos(d3.geoDistance(p.ll, c));
        if (fresh > 0) { ctx.strokeStyle = `rgba(${CORAL},${fresh * .7})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(base[0], base[1], 3 + (1 - fresh) * R * .06, 0, 7); ctx.stroke(); }
        ctx.strokeStyle = `rgba(${INK},.85)`; ctx.lineWidth = 1.25; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(base[0], base[1]); ctx.lineTo(end[0], end[1]); ctx.stroke();
        ctx.fillStyle = `rgb(${CORAL})`; ctx.beginPath(); ctx.arc(end[0], end[1], 2.2 + s, 0, 7); ctx.fill();
        ctx.strokeStyle = `rgb(${BG})`; ctx.lineWidth = 1; ctx.stroke();
        leads.push({ p, x: end[0], y: end[1] });
      }
    }
    // a country lights up when its first download comes in
    function light(t) { for (const p of pins) if (!born.has(p.id) && at(p.a, clock) >= .5) born.set(p.id, t); }
    function frame(t) {
      const dt = Math.min(64, t - last); last = t;
      if (visible && (playing || dirty)) {
        if (playing) {
          if (clock >= M) { hold += dt; if (hold > HOLD) restart(); }
          else clock = Math.min(M, clock + dt / MONTH);
        }
        light(playing || !reduced ? t : -1e9); draw(t); dirty = false;
        const s = `${month(clock)} · ${fmt.format(Math.round(at(all, clock)))} downloads`;
        if (s !== shown) now.textContent = shown = s;
        if (hover && !born.has(hover.p.id)) unhover(); else if (hover) note();
      }
      requestAnimationFrame(frame);
    }

    // the pause button: the same two icons as the hero's
    const icons = {
      pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
      play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor"/></svg>',
    };
    const show = () => { btn.hidden = false; btn.setAttribute('aria-label', playing ? 'Pause the globe' : 'Play the globe'); btn.innerHTML = playing ? icons.pause : icons.play; };
    btn.addEventListener('click', () => { playing = !playing; if (playing && clock >= M) restart(); show(); });
    show();

    // the tooltip: a country and its downloads so far (kept up to date while the replay runs)
    let tipAt = [0, 0], tipText = '';
    function note() {
      const n = Math.round(at(hover.p.a, clock));
      const s = `${fmt.format(n)} download${n === 1 ? '' : 's'} by ${month(clock)}`;
      if (s === tipText) return;
      tipText = s; tip.textContent = names.get(hover.p.id) + ' '; const sp = document.createElement('span'); sp.textContent = s; tip.append(sp);
      tip.hidden = false; tip.style.transform = `translate(${Math.max(0, Math.min(W - tip.offsetWidth, tipAt[0] + 14))}px, ${Math.max(0, tipAt[1] - 36)}px)`;
    }
    const unhover = () => { if (hover) dirty = true; hover = null; tip.hidden = true; tipText = ''; };
    canvas.addEventListener('pointerdown', (ev) => { if (ev.pointerType !== 'mouse') return; drag = { x: ev.clientX, y: ev.clientY, o: offset.slice() }; canvas.setPointerCapture(ev.pointerId); });
    const end = () => { drag = null; };
    canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
    canvas.addEventListener('pointermove', (ev) => {
      if (drag) { offset = [drag.o[0] - (ev.clientX - drag.x) * .3, Math.max(-50, Math.min(50, drag.o[1] + (ev.clientY - drag.y) * .3))]; unhover(); dirty = true; return; }
      if (ev.pointerType !== 'mouse') return;
      const b = canvas.getBoundingClientRect(), x = ev.clientX - b.left, y = ev.clientY - b.top;
      const l = leads.find((l) => Math.hypot(l.x - x, l.y - y) < 9);
      let p = l ? l.p : null;
      if (!p && Math.hypot(x - W / 2, y - W / 2) < R) {
        const ll = front.invert([x, y]);
        p = (ll && pins.find((p) => p.f && born.has(p.id) && d3.geoContains(p.f, ll))) || null;
      }
      if (!p) { unhover(); return; }
      if (p !== hover?.p) { hover = { p, f: p.f }; dirty = true; }
      tipAt = [x, y]; tipText = ''; note();
    });
    canvas.addEventListener('pointerleave', unhover);
    layout(); new ResizeObserver(layout).observe(stage);
    new IntersectionObserver((es) => { visible = es[0].isIntersecting; if (visible) dirty = true; }, { threshold: .1 }).observe(stage);
    requestAnimationFrame(frame);
  }
})();
