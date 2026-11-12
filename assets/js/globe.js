// The wireframe globe of the home page's "Used in N countries" section (#worldwide): graticule,
// coastlines and borders as thin ink lines on the white page, the far side showing through faintly;
// the countries that use Lead-DBS tinted periwinkle (deeper with more launches); the launches of one
// day replayed in a minute as small leads with a coral tip. It turns slowly towards where people are
// working; a mouse can drag it and read a country's total; the round button pauses it. Countries only.
// Data: data/usage.json, inlined by layouts/home.html. This file, with d3-array, d3-geo and
// topojson-client (assets/js/vendor/, ISC) bundled before it, is loaded by assets/js/main/home.js when
// the section comes near the screen; the map (assets/data/world-110m.json, Natural Earth via
// world-atlas) is fetched then, at the same distance.
(() => {
  const sec = document.getElementById('worldwide');
  const src = sec && sec.querySelector('[data-globe-data]');
  if (!sec || !src || !window.d3 || !window.topojson || !('IntersectionObserver' in window)) return;
  const $ = (s) => sec.querySelector(s);
  const stage = $('[data-globe-stage]'), canvas = $('[data-globe]'), tip = $('[data-globe-tip]'), now = $('[data-globe-now]'), btn = $('[data-globe-pause]');
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const D = JSON.parse(src.textContent);
  const fmt = new Intl.NumberFormat('en'), DAY = 86400, RAD = Math.PI / 180;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const hhmm = (s) => `${Math.floor(s / 3600) % 24}:${String(Math.floor(s / 60) % 60).padStart(2, '0')}`;
  const rnd = (s) => { const h = Math.sin(s * 127.1 + 311.7) * 43758.5453; return h - Math.floor(h); };
  const dayName = new Date(D.day + 'T12:00:00Z').toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' });

  // the page's colours, as "r,g,b"
  // (read again when the theme changes, so the globe follows light and dark)
  const probe = document.createElement('i'); probe.hidden = true; sec.append(probe);
  const rgb = (v) => { probe.style.color = `var(${v})`; return (getComputedStyle(probe).color.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).join(','); };
  let INK, TINT, ACTION, CORAL, BG;
  const readColours = () => { INK = rgb('--p-ink'); TINT = rgb('--p-tint-1'); ACTION = rgb('--p-action'); CORAL = rgb('--p-accent'); BG = rgb('--p-bg'); };
  readColours();
  new MutationObserver(readColours).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  // the launches of the day: [second of the day, country]; a minute's launches are spread over it
  const L = D.launches.map((e, i) => [e[0] * 60 + Math.floor(rnd(i * 5.3) * 60), e[1]]).sort((a, b) => a[0] - b[0]);
  const names = new Map(D.countries.map((c) => [c[0], c[1]])), totals = new Map(D.countries.map((c) => [c[0], c[2]])), lmax = Math.log1p(D.countries[0][2]);

  let started = false;
  const load = new IntersectionObserver((es) => {
    if (started || !es.some((e) => e.isIntersecting)) return;
    started = true; load.disconnect();
    fetch(sec.dataset.map).then((r) => r.json()).then(start).catch(() => {});
  }, { rootMargin: '800px 0px' });
  load.observe(sec);

  function start(T) {
    sec.classList.add('is-drawn'); // the figure takes its place before it is measured
    const countries = topojson.feature(T, T.objects.countries).features.filter((f) => f.id !== '010');
    const land = topojson.feature(T, T.objects.land), borders = topojson.mesh(T, T.objects.countries, (a, b) => a !== b);
    const grat = d3.geoGraticule().step([20, 20])(), sphere = { type: 'Sphere' };
    // the countries in use in six steps of tint, each step one path
    const steps = Array.from({ length: 6 }, () => ({ type: 'FeatureCollection', features: [] }));
    countries.forEach((f) => { const n = totals.get(f.id); if (n) steps[Math.min(5, Math.floor(Math.log1p(n) / lmax * 6))].features.push(f); });
    const byId = new Map(countries.map((f) => [f.id, f]));
    // where a large country's launches are placed (centre and spread, degrees), and places too small for the map
    const SPOTS = { '840': [-90, 38, 14, 6], '124': [-86, 46, 18, 3], '156': [114, 31, 7, 6], '076': [-46, -20, 6, 5], '643': [38, 55.5, 5, 2], '036': [147, -33, 5, 4], '356': [78, 20, 7, 7] };
    const EXTRA = { '344': [114.17, 22.32], '702': [103.82, 1.35], '446': [113.55, 22.19], '048': [50.55, 26.07], '470': [14.44, 35.9] };
    L.forEach((e, i) => {
      const f = byId.get(e[1]); let c = EXTRA[e[1]] || null, sx = .3, sy = .3;
      if (f) {
        if (SPOTS[e[1]]) [c, sx, sy] = [SPOTS[e[1]].slice(0, 2), SPOTS[e[1]][2], SPOTS[e[1]][3]];
        else {
          let g = f.geometry;
          if (g.type === 'MultiPolygon') g = g.coordinates.map((k) => ({ type: 'Polygon', coordinates: k })).reduce((a, b) => (d3.geoArea(b) > d3.geoArea(a) ? b : a));
          c = d3.geoCentroid(g); sx = sy = Math.min(4, Math.sqrt(d3.geoArea(g)) / RAD * .25);
        }
      }
      if (!c) return;
      e.ll = c;
      for (let k = 0; k < 8; k++) { const p = [c[0] + (rnd(i * 7 + k) - .5) * 2 * sx, c[1] + (rnd(i * 13 + k + 5) - .5) * 2 * sy]; if (!f || d3.geoContains(f, p)) { e.ll = p; break; } }
      e.lean = (rnd(i * 3.1) - .5) * .5;
    });

    const front = d3.geoOrthographic().clipAngle(90).precision(.4), back = d3.geoOrthographic().clipAngle(90).precision(.6).reflectX(true);
    const pf = d3.geoPath(front, ctx), pb = d3.geoPath(back, ctx);
    let W, R, dpr, visible = false, playing = !reduced, last = performance.now(), hold = 0, shown = '', aim = null, offset = [0, 0], drag = null, hover = null, dirty = true;
    let clock = reduced ? DAY - 1 : 0;
    const born = new Map();
    let leads = [];

    function layout() {
      dpr = Math.min(2, devicePixelRatio || 1); W = stage.clientWidth; canvas.width = canvas.height = Math.round(W * dpr); R = W * .46;
      front.scale(R).translate([W / 2, W / 2]); back.scale(R).translate([W / 2, W / 2]); dirty = true;
    }
    // where the globe looks: the weighted middle of the launches around this time, or the newest one when they are far apart
    function turn(dt) {
      let x = 0, y = 0, z = 0, w = 0, latest = null;
      for (const e of L) {
        if (!e.ll || e[0] > clock + 1200) continue;
        const k = Math.exp(-Math.abs(clock - e[0]) / 3600); if (k < .02) continue;
        const lo = e.ll[0] * RAD, la = e.ll[1] * RAD; x += k * Math.cos(la) * Math.cos(lo); y += k * Math.cos(la) * Math.sin(lo); z += k * Math.sin(la); w += k;
        if (e[0] <= clock) latest = e;
      }
      let t = [((12 * 3600 - (clock - 3600)) / 240) % 360 + 40, 22];
      if (w > .15) {
        if (Math.hypot(x, y, z) / w > .6) t = [Math.atan2(y, x) / RAD, Math.max(10, Math.min(34, Math.asin(z / Math.hypot(x, y, z)) / RAD - 8))];
        else if (latest) t = [latest.ll[0], Math.max(10, Math.min(34, latest.ll[1] - 8))];
      }
      if (!aim) { aim = t; return; }
      const k = 1 - Math.exp(-dt / 2600);
      aim = [aim[0] + (((t[0] - aim[0]) % 360 + 540) % 360 - 180) * k, aim[1] + (t[1] - aim[1]) * k];
    }
    function draw(t) {
      const lon = aim[0] + offset[0], lat = aim[1] + offset[1];
      front.rotate([-lon, -lat]); back.rotate([-lon + 180, lat]);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0); ctx.clearRect(0, 0, W, W); ctx.lineJoin = 'round';
      // the far side, faint
      ctx.lineWidth = 1; ctx.strokeStyle = `rgba(${INK},.05)`; ctx.beginPath(); pb(grat); ctx.stroke();
      ctx.strokeStyle = `rgba(${INK},.13)`; ctx.beginPath(); pb(land); ctx.stroke();
      // the near side: graticule, tinted countries, borders, coast, the sphere's edge
      ctx.strokeStyle = `rgba(${INK},.1)`; ctx.beginPath(); pf(grat); ctx.stroke();
      ctx.fillStyle = `rgba(${BG},.82)`; ctx.beginPath(); pf(land); ctx.fill();
      steps.forEach((s, i) => { if (!s.features.length) return; ctx.fillStyle = `rgba(${TINT},${.3 + i * .14})`; ctx.beginPath(); pf(s); ctx.fill(); });
      if (hover) { ctx.fillStyle = `rgba(${ACTION},.28)`; ctx.beginPath(); pf(hover); ctx.fill(); }
      ctx.lineWidth = .6; ctx.strokeStyle = `rgba(${INK},.22)`; ctx.beginPath(); pf(borders); ctx.stroke();
      ctx.lineWidth = 1; ctx.strokeStyle = `rgba(${INK},.62)`; ctx.beginPath(); pf(land); ctx.stroke();
      ctx.strokeStyle = `rgba(${INK},.4)`; ctx.beginPath(); pf(sphere); ctx.stroke();
      // the launches
      const c = [lon, lat], cx = W / 2; leads = [];
      L.forEach((e, i) => {
        if (e[0] > clock || !e.ll || d3.geoDistance(e.ll, c) > Math.PI / 2 - .02) return;
        const base = front(e.ll), age = (t - (born.has(i) ? born.get(i) : -1e9)) / 1000, grow = 1 - Math.pow(1 - Math.min(1, age / 1.1), 3), fresh = Math.max(0, 1 - age / 2);
        const old = clock - e[0], fade = old < 7200 ? 1 : Math.max(.45, 1 - (old - 7200) / 30000), h = .1 * grow;
        const end = [cx + (base[0] - cx) * (1 + h), cx + (base[1] - cx) * (1 + h)]; end[0] += (end[1] - base[1]) * e.lean * .3; end[1] -= (end[0] - base[0]) * e.lean * .3;
        // seen end-on (near the middle) a lead is short: give it a little height towards the top
        end[1] -= R * .05 * grow * Math.cos(d3.geoDistance(e.ll, c));
        if (fresh > 0) { ctx.strokeStyle = `rgba(${CORAL},${fresh * .7})`; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(base[0], base[1], 3 + (1 - fresh) * R * .06, 0, 7); ctx.stroke(); }
        ctx.strokeStyle = `rgba(${INK},${.85 * fade})`; ctx.lineWidth = 1.25; ctx.lineCap = 'round'; ctx.beginPath(); ctx.moveTo(base[0], base[1]); ctx.lineTo(end[0], end[1]); ctx.stroke();
        ctx.fillStyle = `rgba(${CORAL},${fade})`; ctx.beginPath(); ctx.arc(end[0], end[1], 3, 0, 7); ctx.fill();
        ctx.strokeStyle = `rgb(${BG})`; ctx.lineWidth = 1; ctx.stroke();
        leads.push({ e, x: end[0], y: end[1] });
      });
    }
    function frame(t) {
      const dt = Math.min(64, t - last); last = t;
      if (visible && (playing || dirty)) {
        if (playing) {
          if (clock >= DAY - 1) { hold += dt; if (hold > 4000) { clock = 0; hold = 0; born.clear(); } }
          else { const b = clock; clock = Math.min(DAY - 1, clock + dt / 1000 * DAY / 60); L.forEach((e, i) => { if (e[0] > b && e[0] <= clock) born.set(i, t); }); }
        }
        if (playing || !aim) turn(dt); draw(t); dirty = false;
        let n = 0; while (n < L.length && L[n][0] <= clock) n++;
        const s = `${dayName}, ${hhmm(clock)} CET` + (n ? ` · ${n} launch${n === 1 ? '' : 'es'}` : '');
        if (s !== shown) now.textContent = shown = s;
      }
      requestAnimationFrame(frame);
    }

    // the pause button: the same two icons as the hero's
    const icons = {
      pause: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.5v9M11 3.5v9" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>',
      play: '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M5 3.2v9.6L12.6 8z" fill="currentColor"/></svg>',
    };
    const show = () => { btn.hidden = false; btn.setAttribute('aria-label', playing ? 'Pause the globe' : 'Play the globe'); btn.innerHTML = playing ? icons.pause : icons.play; };
    btn.addEventListener('click', () => { playing = !playing; if (playing && clock >= DAY - 1) { clock = 0; hold = 0; born.clear(); } show(); });
    show();

    canvas.addEventListener('pointerdown', (ev) => { if (ev.pointerType !== 'mouse') return; drag = { x: ev.clientX, y: ev.clientY, o: offset.slice() }; canvas.setPointerCapture(ev.pointerId); });
    const end = () => { drag = null; };
    canvas.addEventListener('pointerup', end); canvas.addEventListener('pointercancel', end);
    canvas.addEventListener('pointermove', (ev) => {
      if (drag) { offset = [drag.o[0] - (ev.clientX - drag.x) * .3, Math.max(-50, Math.min(50, drag.o[1] + (ev.clientY - drag.y) * .3))]; tip.hidden = true; hover = null; dirty = true; return; }
      if (ev.pointerType !== 'mouse') return;
      const b = canvas.getBoundingClientRect(), x = ev.clientX - b.left, y = ev.clientY - b.top;
      let name = '', note = ''; const was = hover; hover = null;
      const l = leads.find((l) => Math.hypot(l.x - x, l.y - y) < 9);
      if (l) { name = names.get(l.e[1]); note = `${hhmm(l.e[0])} CET`; }
      else if (Math.hypot(x - W / 2, y - W / 2) < R) {
        const ll = front.invert([x, y]), f = ll && countries.find((f) => totals.has(f.id) && d3.geoContains(f, ll));
        if (f) { hover = f; name = names.get(f.id); note = `${fmt.format(totals.get(f.id))} launches since ${D.since}`; }
      }
      if (hover !== was) dirty = true;
      if (!name) { tip.hidden = true; return; }
      tip.textContent = name + ' '; const sp = document.createElement('span'); sp.textContent = note; tip.append(sp);
      tip.hidden = false; tip.style.transform = `translate(${Math.max(0, Math.min(W - tip.offsetWidth, x + 14))}px, ${Math.max(0, y - 36)}px)`;
    });
    canvas.addEventListener('pointerleave', () => { if (hover) dirty = true; hover = null; tip.hidden = true; });
    layout(); new ResizeObserver(layout).observe(stage);
    new IntersectionObserver((es) => { visible = es[0].isIntersecting; if (visible) dirty = true; }, { threshold: .1 }).observe(stage);
    requestAnimationFrame(frame);
  }
})();
