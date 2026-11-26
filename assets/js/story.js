// The home page's scroll story ([data-story], layouts/_partials/home-story.html): one drawing that stays
// on the screen while the first parts of the page scroll past it, and changes with them. It is drawn
// like a technical sketch, ink on the page's ground, from real data in MNI space (assets/data/story.json,
// packed by tools/story.py): the right lead of one Lead Tutor patient, the DISTAL nuclei as stacked
// outlines and the STN motor tract.
//   0  the lead, drawn with its measures, above the target
//   1  it moves into place among the nuclei (localization)
//   2  a hypothetical bipolar stimulation: the field lines of the two contacts, with current running
//      along them, and the OCD sweet and sour spot it reaches (stimulation modelling)
//   3  the fibres of the OCD response tract; those within reach of the field take colour, and the view
//      rides one of them forwards, between caudate and putamen, past a lead in the capsule (connectivity)
//   4  out to the whole brain and the leads of both sides, then a real Lead-DBS render (group analysis)
// Colour comes late: everything is ink until the fibres are activated.
// The canvas is decoration (aria-hidden); every word of the story is in the page. Until the data has
// loaded, without script and when the canvas cannot be drawn, each step shows its own still render
// instead. Under reduced motion nothing moves by itself and the drawing changes step by step.
(() => {
  const root = document.querySelector('[data-story]');
  const canvas = root?.querySelector('canvas');
  const ctx = canvas?.getContext('2d');
  const fallback = () => {
    document.documentElement.classList.remove('story-live');
    root?.classList.remove('is-live');
  };
  if (!ctx || !('IntersectionObserver' in window)) { fallback(); return; }
  const stage = canvas.parentElement;
  const steps = [...root.querySelectorAll('[data-story-step]')];
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');

  // ---------------------------------------------------------------- small helpers
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const ramp = (x, a, b) => clamp((x - a) / (b - a));
  const ease = (x) => x * x * x * (x * (6 * x - 15) + 10);
  const smooth = (x) => x * x * (3 - 2 * x);
  const lerp = (a, b, t) => a + (b - a) * t;
  const hash = (i) => { const s = Math.sin(i * 127.1 + 311.7) * 43758.5453; return s - Math.floor(s); };
  const scale = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const add = (a, b, s = 1) => [a[0] + b[0] * s, a[1] + b[1] * s, a[2] + b[2] * s];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const norm = (a) => { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
  const mix3 = (a, b, t) => [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];
  const rgb = (c, a = 1) => `rgb(${c[0] | 0} ${c[1] | 0} ${c[2] | 0} / ${a})`;

  // ---------------------------------------------------------------- colours
  // ink and paper are the page's own (so the dark theme draws light on dark); the colours of the
  // activated fibres run from coral through violet to blue along a fibre
  let INK = [47, 52, 55], PAPER = [255, 255, 255], ACCENT = [224, 100, 90], dark = false;
  const SPECTRUM = [[255, 122, 69], [240, 78, 110], [196, 76, 200], [118, 96, 240], [48, 140, 240], [38, 190, 200]];
  const SPOT = { sweet: [226, 62, 52], sour: [44, 104, 222] };
  const NUCLEUS = { STN: [240, 150, 40], GPi: [60, 170, 110], RN: [220, 70, 70], Ca: [70, 130, 220], Pu: [130, 110, 210] };
  const spectrum = (u) => {
    const x = clamp(u) * (SPECTRUM.length - 1), i = Math.min(SPECTRUM.length - 2, Math.floor(x));
    return mix3(SPECTRUM[i], SPECTRUM[i + 1], x - i);
  };
  // a fibre of the response tract runs warm, the colour of the sweet spot; one that goes with a worse
  // outcome runs cold, the colour of the sour spot
  const two = (a, b, c, u) => (u < 0.5 ? mix3(a, b, u * 2) : mix3(b, c, u * 2 - 1));
  const warm = (u) => two([250, 150, 60], [226, 62, 52], [196, 56, 130], clamp(u));
  const cold = (u) => two([44, 104, 222], [40, 150, 225], [40, 190, 205], clamp(u));
  const parse = (s) => { const m = s.match(/[\d.]+/g); return m ? m.slice(0, 3).map(Number) : null; };
  const probe = document.createElement('span');
  probe.style.cssText = 'position:absolute;visibility:hidden;pointer-events:none';
  let FONT = 'ui-monospace, Menlo, monospace';
  const readTheme = () => {
    stage.append(probe);
    const cs = getComputedStyle(probe);
    probe.style.color = 'var(--ink)'; INK = parse(cs.color) || INK;
    probe.style.color = 'var(--bg)'; PAPER = parse(cs.color) || PAPER;
    probe.style.color = 'var(--p-accent)'; ACCENT = parse(cs.color) || ACCENT;
    probe.style.fontFamily = 'var(--font-mono)'; FONT = cs.fontFamily || FONT;
    probe.remove();
    dark = PAPER[0] + PAPER[1] + PAPER[2] < 380;
  };

  // ---------------------------------------------------------------- the camera
  let W = 0, H = 0, DPR = 1, CX = 0, CY = 0, F = 1, phone = false;
  let E = [0, 0, 0], R = [1, 0, 0], U = [0, 0, 1], Fw = [0, 1, 0], DIST = 1;
  let px = 0, py = 0, pz = 0;
  const project = (x, y, z) => {
    const dx = x - E[0], dy = y - E[1], dz = z - E[2];
    pz = dx * Fw[0] + dy * Fw[1] + dz * Fw[2];
    const k = F / Math.max(pz, 0.5);
    px = CX + (dx * R[0] + dy * R[1] + dz * R[2]) * k;
    py = CY - (dx * U[0] + dy * U[1] + dz * U[2]) * k;
  };
  const orbit = (T, dist, az, el) => {
    const a = az * Math.PI / 180, e = el * Math.PI / 180;
    return { T, E: [T[0] + dist * Math.cos(e) * Math.cos(a), T[1] + dist * Math.cos(e) * Math.sin(a), T[2] + dist * Math.sin(e)] };
  };
  const lookAt = (eye, T) => { E = eye; Fw = norm(sub(T, E)); R = norm(cross(Fw, [0, 0, 1])); U = cross(R, Fw); DIST = Math.hypot(...sub(T, E)); };

  // ---------------------------------------------------------------- drawing: sketched lines
  // a polyline (xyz triples) up to its n-th point, each point a little off its place as a hand would
  // leave it (the offsets are fixed per point, so a line does not shiver)
  const trace = (pts, n, close, jit, seed) => {
    const m = Math.min(pts.length / 3, Math.ceil(n));
    let on = false;
    for (let i = 0; i < m; i++) {
      project(pts[3 * i], pts[3 * i + 1], pts[3 * i + 2]);
      if (pz < 1) { on = false; continue; }
      const x = px + (jit ? (hash(seed + i * 2) - 0.5) * jit : 0), y = py + (jit ? (hash(seed + i * 2 + 1) - 0.5) * jit : 0);
      if (on) ctx.lineTo(x, y); else ctx.moveTo(x, y);
      on = true;
    }
    if (close && on && m === pts.length / 3) ctx.closePath();
  };
  // the same line twice, the second pass thinner and off the first: pencil over pencil
  const sketch = (pts, n, close, width, alpha, seed) => {
    ctx.beginPath(); trace(pts, n, close, 0.9, seed);
    ctx.lineWidth = width; ctx.strokeStyle = rgb(INK, alpha); ctx.stroke();
    ctx.beginPath(); trace(pts, n, close, 1.6, seed + 91);
    ctx.lineWidth = width * 0.55; ctx.strokeStyle = rgb(INK, alpha * 0.5); ctx.stroke();
  };
  const label = (text, x, y, alpha, align = 'left', size = 11) => {
    ctx.font = `500 ${size}px ${FONT}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
    ctx.fillStyle = rgb(INK, alpha); ctx.fillText(text, x, y);
  };

  // ---------------------------------------------------------------- the scene, built once from the data
  // A closed surface as the drawing needs it: its points, its triangles (wound outwards), their normals
  // and middles, and its edges with the two triangles that meet at each.
  const mesh = (v, f) => {
    const nf = f.length / 3, nv = v.length / 3, n = new Float32Array(nf * 3), mid = new Float32Array(nf * 3), seen = new Map(), edges = [];
    for (let i = 0; i < nf; i++) {
      const A = [0, 1, 2].map((c) => v[3 * f[3 * i] + c]), B = [0, 1, 2].map((c) => v[3 * f[3 * i + 1] + c]), C = [0, 1, 2].map((c) => v[3 * f[3 * i + 2] + c]);
      const nn = norm(cross(sub(B, A), sub(C, A)));
      for (let c = 0; c < 3; c++) { n[3 * i + c] = nn[c]; mid[3 * i + c] = (A[c] + B[c] + C[c]) / 3; }
      for (let e = 0; e < 3; e++) {
        const p = f[3 * i + e], q2 = f[3 * i + (e + 1) % 3], key = Math.min(p, q2) * 65536 + Math.max(p, q2);
        if (seen.has(key)) edges.push(p, q2, seen.get(key), i); else seen.set(key, i);
      }
    }
    const c = [0, 0, 0]; let top = 0;
    for (let i = 0; i < nv; i++) { c[0] += v[3 * i] / nv; c[1] += v[3 * i + 1] / nv; c[2] += v[3 * i + 2] / nv; if (v[3 * i + 2] > v[3 * top + 2]) top = i; }
    return { v, f, n, mid, edges, c, top: [v[3 * top], v[3 * top + 1], v[3 * top + 2]], nf, nv,
      sx: new Float32Array(nv), sy: new Float32Array(nv), sz: new Float32Array(nv), front: new Uint8Array(nf), tone: new Float32Array(nf), vt: new Float32Array(nv), vn: new Uint8Array(nv) };
  };
  let S = null;
  const build = (d) => {
    const u = d.unit;
    const mm = (a) => { const f = new Float32Array(a.length); for (let i = 0; i < a.length; i++) f[i] = a[i] * u; return f; };
    const mk = (o, a, b1, k, L) => ({ o, a, b1, b2: cross(a, b1), k, r: L.diameter / 2 * k, half: L.contact / 2 * k, tip: L.tip * k, rings: L.rings, act: 0 });
    const real = d.leads.map((L) => mk([L.origin[0] * u, L.origin[1] * u, L.origin[2] * u], L.axis, L.face, L.pitch / 2, L));
    const lead = real[0], { o, a, k } = lead;
    // a hypothetical bipolar setting: the cathode is a segment of the second ring (the one that faces
    // the view of the stimulation step), the anode the segment above it
    const eye = orbit([0, 0, 0], 1, AZ_STIM, 14).E;
    lead.act = [0, 1, 2].map((i) => i * 2 * Math.PI / 3).reduce((m, th) => (dot(eye, add([0, 0, 0], add(scale(lead.b1, Math.cos(th)), lead.b2, Math.sin(th)))) > dot(eye, add(scale(lead.b1, Math.cos(m)), lead.b2, Math.sin(m))) ? th : m), 0);
    const b1 = add(scale(lead.b1, Math.cos(lead.act)), lead.b2, Math.sin(lead.act)), b2 = cross(a, b1);
    const cathode = add(add(o, a, 2 * k), b1, lead.r), anode = add(add(o, a, 4 * k), b1, lead.r);
    // hypothetical leads at the two other published targets the followed fibre passes: the anterior
    // limb of the internal capsule and the nucleus accumbens, both coming from the front and above
    const others = d.alic.map((c, i) => {
      const ax = norm(d.axes[i]), f = norm(cross(ax, [0, 0, 1]));
      return mk(add([c[0] * u, c[1] * u, c[2] * u], ax, -3 * k), ax, f, k, d.leads[0]);
    });
    [lead, ...others].forEach((L, i) => { L.entry = d.entry[i]; });   // where it passes out through the cortex
    const nuclei = d.nuclei.map((n) => Object.assign(mesh(mm(n.v), n.f), { name: n.name, colour: NUCLEUS[n.name] }));
    // what each lead stimulates: a volume about its second contact (the first lead's on the side its
    // active segment faces)
    // What a lead stimulates, drawn as its field: lines from points around the anode (the contact above),
    // along the field, to the cathode. Only the closed ones are kept, so it reads as nested loops; they
    // leave the anode in a fan of planes through the two contacts, on the side the segment faces.
    // (round: ring contacts, so the loops stand all round the lead, each in its own plane through the axis)
    const fieldOf = (L, b1f, b2f, PH, round) => {
      const lines = [];
      const inLead = (q2) => { const v = sub(q2, L.o), sa = dot(v, L.a); return Math.hypot(...sub(v, scale(L.a, sa))) < L.r * 0.92; };
      const TH = [0.4, 0.52, 0.63, 0.73, 0.82, 0.9];
      for (let q2 = 0; q2 < PH; q2++) for (let h = 0; h < TH.length; h++) {
        const th = TH[h] * Math.PI, turn = round ? q2 / PH * 2 * Math.PI : 0, ph = round ? 0 : (q2 / (PH - 1) - 0.5) * 1.05 * Math.PI;
        const c1 = add(scale(b1f, Math.cos(turn)), b2f, Math.sin(turn)), c2 = cross(L.a, c1);
        const A = add(add(L.o, L.a, 4 * L.k), c1, L.r), C = add(add(L.o, L.a, 2 * L.k), c1, L.r), mid = mix3(C, A, 0.5);
        const dir = add(add(scale(L.a, Math.cos(th)), c1, Math.sin(th) * Math.cos(ph)), c2, Math.sin(th) * Math.sin(ph));
        let pt = add(A, dir, 0.4), closed = false;
        const line = [];
        for (let st = 0; st < 700; st++) {
          line.push(pt[0], pt[1], pt[2]);
          const va = sub(pt, A), vc = sub(pt, C), la = Math.hypot(...va), lc = Math.hypot(...vc);
          if (lc < 0.4) { closed = true; break; }
          pt = add(pt, norm([va[0] / la ** 3 - vc[0] / lc ** 3, va[1] / la ** 3 - vc[1] / lc ** 3, va[2] / la ** 3 - vc[2] / lc ** 3]), 0.12);
          if (Math.hypot(...sub(pt, mid)) > 9 || inLead(pt)) break;
        }
        if (closed && line.length > 30) lines.push({ p: new Float32Array(line), ph: 1 - TH[h], sp: hash(q2 * 7.7 + h * 3.3 + L.o[0]) });
      }
      return lines;
    };
    lead.field = fieldOf(lead, b1, b2, 9, false);
    const fibres = d.fibres.map((f, i) => {
      const p = mm(f);
      // where the fibre passes the cathode: there it takes up the signal
      let dmin = 1e9, jn = 0;
      for (let j = 0; j < p.length; j += 3) { const l = Math.hypot(p[j] - cathode[0], p[j + 1] - cathode[1], p[j + 2] - cathode[2]); if (l < dmin) { dmin = l; jn = j / 3; } }
      return { p, w: new Float32Array(p.length), dmin, jn, ph: hash(i * 3.1) * 6.283, i };
    });
    // the one the view follows (the first of the data: it passes the lead and runs far forwards), drawn
    // with four points for every one of the data (Catmull-Rom)
    const hero = fibres[0];
    const n = hero.p.length / 3, sub4 = 4, hp = new Float32Array(((n - 1) * sub4 + 1) * 3);
    const at = (i, c) => hero.p[3 * clamp(i, 0, n - 1) + c];
    for (let i = 0; i < n - 1; i++) for (let s = 0; s < sub4; s++) for (let c = 0; c < 3; c++) {
      const t = s / sub4, p0 = at(i - 1, c), p1 = at(i, c), p2 = at(i + 1, c), p3 = at(i + 2, c);
      hp[(i * sub4 + s) * 3 + c] = 0.5 * (2 * p1 + (p2 - p0) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (3 * p1 - p0 - 3 * p2 + p3) * t * t * t);
    }
    for (let c = 0; c < 3; c++) hp[(n - 1) * sub4 * 3 + c] = at(n - 1, c);
    hero.hero = true;
    const stn = nuclei.find((x) => x.name === 'STN').c;
    // Relay choreography across the three electrodes (no electrode ever blocks another when firing):
    //   1. STN (lead)       -> wave 0: warm fibres ignite from STN and travel forward strictly up to the ALIC gate (f.ja)
    //   2. ALIC (others[0]) -> wave 1: lands unobstructed on the waiting tips, unlocks wave 0 past f.ja into frontal cortex,
    //                          AND sparks 36 additional warm anterior-capsule fibres right out of ALIC's cathode
    //   3. NAc  (others[1]) -> wave 2: lands unobstructed in front/below, firing all 23 cold blue fibres
    const cNAc = add(others[1].o, others[1].a, 2 * others[1].k);
    others.forEach((L, li) => {
      const c = add(L.o, L.a, 2 * L.k);
      if (li === 0) {
        let best = 1e9, q2 = c;
        for (let j = 0; j < hp.length; j += 3) { const l = Math.hypot(hp[j] - c[0], hp[j + 1] - c[1], hp[j + 2] - c[2]); if (l < best) { best = l; q2 = [hp[j], hp[j + 1], hp[j + 2]]; } }
        if (best > 1.5) L.o = add(L.o, sub(q2, c), 1 - 1.5 / best);
      }
      L.field = fieldOf(L, L.b1, L.b2, 10, true);
    });
    const cALIC2 = add(others[0].o, others[0].a, 2 * others[0].k);
    const reach0 = 2.0;
    fibres.forEach((f) => {
      f.wave = -1;
      let zmax = -1e9, da = 1e9, ja = 0, dn = 1e9, jn2 = 0;
      for (let j = 0; j < f.p.length; j += 3) {
        if (f.p[j + 2] > zmax) zmax = f.p[j + 2];
        const la = Math.hypot(f.p[j] - cALIC2[0], f.p[j + 1] - cALIC2[1], f.p[j + 2] - cALIC2[2]);
        if (la < da) { da = la; ja = j / 3; }
        const ln = Math.hypot(f.p[j] - cNAc[0], f.p[j + 1] - cNAc[1], f.p[j + 2] - cNAc[2]);
        if (ln < dn) { dn = ln; jn2 = j / 3; }
      }
      f.zmax = zmax; f.da = da; f.ja = ja; f.dn = dn; f.jn2 = jn2;
    });
    // Wave 2 (NAc, 3rd electrode): all 23 cold blue fibres passing near NAc
    const wNAc = fibres.filter((f) => f.dn < 9).sort((x, y) => x.dn - y.dn);
    wNAc.forEach((f, r) => {
      f.wave = 2; f.bad = true; f.jn = f.jn2;
      f.dmin = reach0 * 0.9 * r / Math.max(1, wNAc.length);
    });
    // Wave 0 (STN, 1st electrode): 18 fibres closest to STN; their forward end pauses at ALIC (f.ja) until wave 1 fires
    const wSTN = fibres.filter((f) => f.wave < 0 && f.dmin < 3.5).sort((x, y) => x.dmin - y.dmin).slice(0, 18);
    wSTN.forEach((f, r) => {
      f.wave = 0; f.bad = false;
      f.dmin = reach0 * 0.9 * r / Math.max(1, wSTN.length);
    });
    // Wave 1 (ALIC, 2nd electrode): 38 anterior-capsule fibres ignited straight out of ALIC's contacts
    const wALIC = fibres.filter((f) => f.wave < 0 && f.da < 4).sort((x, y) => x.da - y.da).slice(0, 38);
    wALIC.forEach((f, r) => {
      f.wave = 1; f.bad = false; f.jn = f.ja;
      f.dmin = reach0 * 0.9 * r / Math.max(1, wALIC.length);
    });
    const reach = reach0;
    const spots = d.spots.map((sp) => Object.assign(mesh(mm(sp.v), sp.f), { name: sp.name, colour: SPOT[sp.name] }));
    const cortex = (d.cortex || []).map((c) => Object.assign(mesh(mm(c.v), c.f), { colour: [128, 128, 128] }));
    return { cortex, lead, others, cathode, anode, cALIC: cALIC2, cNAc, nuclei, fibres, hero, hp, reach, stn, spots, view: d.view, points: d.points };
  };

  // ---------------------------------------------------------------- the view at a place in the story
  // One continuous, monotonic camera path:
  //   0.02 -> 0.90: gentle zoom-in on STN as nuclei appear
  //   0.90 -> 2.15: smooth pull-out & orbit right framing STN -> ALIC (2nd electrode, completely unobstructed)
  //   2.25 -> 3.05: smooth glide framing NAc (3rd electrode, clearly in foreground with full bottom margin)
  //   3.28 -> 3.90: pull back to the whole 3D brain
  const AZ_STIM = -132;
  const heroS = (p) => lerp(S.hero.ja / (S.points - 1), 0.92, smooth(ramp(p, 2.10, 3.30)));
  const heroPoint = (s) => {
    const m = S.hp.length / 3 - 1, x = clamp(s) * m, i = Math.min(m - 1, Math.floor(x)), t = x - i;
    return [0, 1, 2].map((c) => lerp(S.hp[3 * i + c], S.hp[3 * i + 3 + c], t));
  };
  const camera = (p, t) => {
    const zIn = smooth(ramp(p, 0.02, 0.9));      // gentle zoom-in as nuclei come in
    const toALIC = smooth(ramp(p, 0.9, 1.95));   // frame STN -> ALIC relay cleanly
    const toNAc = smooth(ramp(p, 2.2, 2.95));    // shift smoothly to frame NAc (3rd electrode) + all 3 leads
    const wide = smooth(ramp(p, 3.3, 3.92));     // final pull-back to frame the whole brain
    const glide = smooth(ramp(p, 0.9, 3.92));    // monotonic orbit right from STN to whole brain
    const startT = add(S.stn, [-1.0, 0, 1.0]);
    const stimT = add(S.stn, [0.4, 0.8, 0.6]);
    const alicT = mix3(S.stn, S.cALIC, 0.64);    // centered right on the STN -> ALIC corridor
    const nacT = mix3(mix3(S.stn, S.cALIC, 0.45), S.cNAc, 0.56); // low enough to keep NAc tip & blue bundle well above bottom
    const T = mix3(mix3(mix3(mix3(startT, stimT, zIn), alicT, toALIC), nacT, toNAc), S.view.target, wide);
    const dist = lerp(lerp(lerp(lerp(50, 34, zIn), 72, toALIC), 90, toNAc), S.view.dist, wide * wide);
    const az = lerp(lerp(-146, AZ_STIM, zIn), S.view.az, glide ** 1.15);
    const el = lerp(lerp(12, 15, zIn), lerp(18, S.view.el, wide), glide);
    const v = orbit(T, dist, az, el);
    let off = sub(v.E, T);
    if (phone) off = scale(off, lerp(1.12, 1, ramp(p, 3.45, 3.7)));
    const sw = (reduced.matches ? 0 : 1) * (0.45 * (1 - ramp(p, 1.2, 1.6)) + 0.5 * ramp(p, 3.75, 4)) * 0.087 * Math.sin(t * 0.21), c = Math.cos(sw), sn = Math.sin(sw);
    lookAt(add(T, [off[0] * c - off[1] * sn, off[0] * sn + off[1] * c, off[2]]), T);
  };

  // ---------------------------------------------------------------- the lead
  const drawLead = (Ld, raise, intro, dims, glow, solid) => {
    ctx.globalAlpha = solid;
    const { a, b1, b2, k, r, half, tip, rings } = Ld;
    const o = add(Ld.o, a, raise);
    const P = (s, c = 0, sn = 0) => { // a point at s along the axis, on the surface at the angle (c, sn)
      project(o[0] + a[0] * s + r * (c * b1[0] + sn * b2[0]), o[1] + a[1] * s + r * (c * b1[1] + sn * b2[1]), o[2] + a[2] * s + r * (c * b1[2] + sn * b2[2]));
    };
    // the side of the lead the eye sees: n lies across the axis and across the line of sight
    const toEye = norm(sub(E, o)), nv = norm(cross(a, toEye));
    const nc = dot(nv, b1), ns = dot(nv, b2);
    const fc = dot(toEye, b1), fs = dot(toEye, b2), fl = Math.hypot(fc, fs) || 1;
    const facing = (c, sn) => (c * fc + sn * fs) / fl;
    const s0 = -half - tip + r, top = Ld.entry * intro;
    // the trajectory: a dash-dot centre line through the lead and on below the tip
    ctx.setLineDash([10, 4, 2, 4]); ctx.lineWidth = 0.8; ctx.strokeStyle = rgb(INK, 0.3 * intro); ctx.beginPath();
    project(...add(o, a, -9 - raise * 0.9)); ctx.moveTo(px, py); project(...add(o, a, top)); ctx.lineTo(px, py); ctx.stroke(); ctx.setLineDash([]);
    // the ground under the lead: the paper, so what lies behind it does not show through
    ctx.beginPath(); P(top, nc, ns); ctx.moveTo(px, py); P(s0, nc, ns); ctx.lineTo(px, py);
    for (let i = 1; i < 12; i++) { const th = Math.PI * i / 12; project(...add(add(o, a, s0 - r * Math.sin(th)), nv, r * Math.cos(th))); ctx.lineTo(px, py); }
    P(s0, -nc, -ns); ctx.lineTo(px, py); P(top, -nc, -ns); ctx.lineTo(px, py); ctx.closePath();
    ctx.fillStyle = rgb(PAPER, 0.94 * solid * solid); ctx.fill();
    // the active segment takes the accent colour once current flows
    const seg = (ring, c0, w) => { // the surface patch of a contact between two angles
      const s = ring * 2 * k, pts = [];
      for (let i = 0; i <= 10; i++) { const ph = c0 + w * (i / 10 - 0.5); pts.push([s - half, Math.cos(ph), Math.sin(ph)]); }
      for (let i = 10; i >= 0; i--) { const ph = c0 + w * (i / 10 - 0.5); pts.push([s + half, Math.cos(ph), Math.sin(ph)]); }
      ctx.beginPath(); pts.forEach((q, i) => { P(q[0], q[1], q[2]); if (i) ctx.lineTo(px, py); else ctx.moveTo(px, py); }); ctx.closePath();
    };
    if (glow > 0) {
      seg(1, Ld.act, Math.PI / 2); ctx.fillStyle = rgb(ACCENT, 0.85 * glow); ctx.fill();
      seg(2, Ld.act, Math.PI / 2); ctx.fillStyle = rgb(INK, 0.3 * glow); ctx.fill();
    }
    // the contacts: hatched along the axis, darker towards the edges, so the metal reads as round
    ctx.lineWidth = 0.7;
    rings.forEach((count, ring) => {
      const s = ring * 2 * k;
      for (let j = 0; j < 40; j++) {
        const ph = j / 40 * 2 * Math.PI, c = Math.cos(ph), sn = Math.sin(ph), f = facing(c, sn);
        if (f < 0.06) continue;
        if (count === 3) { const m = ((ph + Math.PI / 4) % (2 * Math.PI / 3)); if (m > Math.PI / 2) continue; }
        ctx.strokeStyle = rgb(INK, (0.16 + 0.6 * (1 - f) ** 1.5) * intro);
        ctx.beginPath(); P(s - half + hash(j + ring * 50) * 0.08, c, sn); ctx.moveTo(px, py); P(s + half - hash(j + ring * 50 + 9) * 0.08, c, sn); ctx.lineTo(px, py); ctx.stroke();
      }
      if (count === 3) for (let q = 0; q < 6; q++) {
        const ph = Math.floor(q / 2) * 2 * Math.PI / 3 + (q % 2 ? 1 : -1) * Math.PI / 4, c = Math.cos(ph), sn = Math.sin(ph);
        if (facing(c, sn) < 0.02) continue;
        ctx.strokeStyle = rgb(INK, 0.8 * intro); ctx.beginPath(); P(s - half, c, sn); ctx.moveTo(px, py); P(s + half, c, sn); ctx.lineTo(px, py); ctx.stroke();
      }
      // the two rims of the contact, the half the eye sees
      [s - half, s + half].forEach((e, q) => {
        ctx.beginPath(); let on = false;
        for (let j = 0; j <= 48; j++) {
          const ph = j / 48 * 2 * Math.PI, c = Math.cos(ph), sn = Math.sin(ph);
          if (facing(c, sn) < -0.02) { on = false; continue; }
          P(e, c, sn); if (on) ctx.lineTo(px + (hash(j + q * 60 + ring * 7) - 0.5) * 0.5, py); else ctx.moveTo(px, py); on = true;
        }
        ctx.lineWidth = 1; ctx.strokeStyle = rgb(INK, 0.8 * intro); ctx.stroke(); ctx.lineWidth = 0.7;
      });
    });
    // the outline: two sides and the round tip, sketched
    const side = (sg) => { const pts = []; for (let i = 0; i <= 24; i++) { const s = lerp(s0, top, (i / 24) ** 2); pts.push(...add(add(o, a, s), nv, sg * r)); } return new Float32Array(pts); };
    const cap = []; for (let i = 0; i <= 14; i++) { const th = Math.PI * i / 14; cap.push(...add(add(o, a, s0 - r * Math.sin(th)), nv, r * Math.cos(th))); }
    sketch(side(1), 25, false, 1.3, 0.9 * intro, 11); sketch(side(-1), 25, false, 1.3, 0.9 * intro, 37);
    sketch(new Float32Array(cap), 15 * intro, false, 1.3, 0.9 * intro, 53);
    // its measures, as on a drawing: the length of a contact, the spacing of the rings, the diameter
    if (dims > 0.01) {
      const off = (s, m) => add(add(o, a, s), nv, m * r);
      const dim = (s1, s2, m, text) => {
        const A = off(s1, m), B = off(s2, m);
        ctx.lineWidth = 0.8; ctx.strokeStyle = rgb(INK, 0.55 * dims); ctx.beginPath();
        project(...off(s1, Math.sign(m) * 1.25)); ctx.moveTo(px, py); project(...off(s1, m + Math.sign(m) * 0.5)); ctx.lineTo(px, py);
        project(...off(s2, Math.sign(m) * 1.25)); ctx.moveTo(px, py); project(...off(s2, m + Math.sign(m) * 0.5)); ctx.lineTo(px, py);
        project(...A); const ax = px, ay = py; ctx.moveTo(px, py); project(...B); ctx.lineTo(px, py); const bx = px, by = py; ctx.stroke();
        const l = Math.hypot(bx - ax, by - ay) || 1, ux = (bx - ax) / l, uy = (by - ay) / l;
        ctx.beginPath(); [[ax, ay, 1], [bx, by, -1]].forEach(([x, y, g]) => { ctx.moveTo(x + g * (ux * 6 - uy * 2.5), y + g * (uy * 6 + ux * 2.5)); ctx.lineTo(x, y); ctx.lineTo(x + g * (ux * 6 + uy * 2.5), y + g * (uy * 6 - ux * 2.5)); }); ctx.stroke();
        const right = (bx + ax) / 2 > (project(...add(o, a, (s1 + s2) / 2)), px);
        label(text, (ax + bx) / 2 + (right ? 10 : -10), (ay + by) / 2, 0.8 * dims, right ? 'left' : 'right');
      };
      dim(-half, half, 3.4, '1.5 mm');
      dim(2 * k + half, 4 * k - half, 3.4, '0.5 mm');
      dim(2 * k, 4 * k, -3.4, '2.0 mm');
      project(...off(9.5 * k, 1)); const x1 = px, y1 = py; project(...off(9.5 * k, -1)); const x2 = px, y2 = py;
      ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.strokeStyle = rgb(INK, 0.55 * dims); ctx.stroke();
      const left = x1 < x2 ? [x1, y1] : [x2, y2];
      label('⌀ 1.36 mm', left[0] - 10, left[1], 0.8 * dims, 'right');
    }
    ctx.globalAlpha = 1;
  };

  // ---------------------------------------------------------------- surfaces, drawn as the brain is
  // A form with an outline, a ground of soft colour, and hatching where it turns away from the eye or
  // from the light (crossed where it is darkest): the pen of tools/story.py's brain, at every view.
  // o.colour: how much of the form's colour its ground takes; o.ground: how much the ground covers.
  const HATCH = 3.2;
  const hatch = (M, level, deg, cx, cy, rad, colour, a, width = 0.6) => {
    ctx.save(); ctx.beginPath();
    let any = false;
    for (let i = 0; i < M.nf; i++) {
      if (!M.front[i]) continue;
      // the part of the triangle that is darker than the level: tone runs evenly between its corners
      let first = true;
      for (let e = 0; e < 3; e++) {
        const p = M.f[3 * i + e], q2 = M.f[3 * i + (e + 1) % 3], tp = M.vt[p] - level, tq = M.vt[q2] - level;
        if (tp >= 0) { if (first) ctx.moveTo(M.sx[p], M.sy[p]); else ctx.lineTo(M.sx[p], M.sy[p]); first = false; }
        if (tp >= 0 !== tq >= 0) {
          const u = tp / (tp - tq), x = M.sx[p] + (M.sx[q2] - M.sx[p]) * u, y = M.sy[p] + (M.sy[q2] - M.sy[p]) * u;
          if (first) ctx.moveTo(x, y); else ctx.lineTo(x, y); first = false;
        }
      }
      if (!first) { ctx.closePath(); any = true; }
    }
    if (any) {
      ctx.clip(); ctx.beginPath();
      const th = deg * Math.PI / 180, dx = Math.cos(th), dy = Math.sin(th);
      for (let k = -rad; k <= rad; k += HATCH) { ctx.moveTo(cx - dy * k - dx * rad, cy + dx * k - dy * rad); ctx.lineTo(cx - dy * k + dx * rad, cy + dx * k + dy * rad); }
      ctx.lineWidth = width; ctx.strokeStyle = rgb(colour, a); ctx.stroke();
    }
    ctx.restore();
  };
  const drawSurface = (M, alpha, o) => {
    if (alpha <= 0.01) return;
    const { v, f, n, mid } = M;
    let x0 = 1e9, x1 = -1e9, y0 = 1e9, y1 = -1e9, behind = false;
    const gr = o.grow === undefined ? 1 : o.grow, c0 = M.c;
    for (let i = 0; i < M.nv; i++) {
      project(c0[0] + (v[3 * i] - c0[0]) * gr, c0[1] + (v[3 * i + 1] - c0[1]) * gr, c0[2] + (v[3 * i + 2] - c0[2]) * gr);
      M.sx[i] = px; M.sy[i] = py; M.sz[i] = pz; M.vt[i] = 0; M.vn[i] = 0;
      if (pz < 1) behind = true;
      if (px < x0) x0 = px; if (px > x1) x1 = px; if (py < y0) y0 = py; if (py > y1) y1 = py;
    }
    if (behind || x1 < 0 || x0 > W || y1 < 0 || y0 > H) return;   // not in the picture, or the eye is inside it
    const L = norm(add(add(scale(R, -0.45), U, 0.6), Fw, -0.66));
    for (let i = 0; i < M.nf; i++) {
      const ex = E[0] - mid[3 * i], ey = E[1] - mid[3 * i + 1], ez = E[2] - mid[3 * i + 2];
      const d = (n[3 * i] * ex + n[3 * i + 1] * ey + n[3 * i + 2] * ez) / Math.hypot(ex, ey, ez);
      M.front[i] = d > 0 ? 1 : 0;
      const lam = Math.max(0, n[3 * i] * L[0] + n[3 * i + 1] * L[1] + n[3 * i + 2] * L[2]);
      const tone = d > 0 ? 0.75 * (1 - d) ** 1.6 + 0.45 * (1 - lam) ** 2 : 1.1;
      for (let e = 0; e < 3; e++) { M.vt[f[3 * i + e]] += tone; M.vn[f[3 * i + e]]++; }
    }
    // tone evened out over the points, so the hatching ends along a line and not along triangles
    for (let i = 0; i < M.nv; i++) M.vt[i] /= M.vn[i] || 1;
    const ink = mix3(INK, M.colour, 0.5 * o.colour);
    ctx.globalAlpha = alpha;
    // the outline: where a triangle that faces the eye meets one that does not. It goes down
    // first, twice as wide: the ground covers its inner half, and with it every stroke inside the form
    ctx.beginPath();
    for (let e = 0; e < M.edges.length; e += 4) {
      if (M.front[M.edges[e + 2]] === M.front[M.edges[e + 3]]) continue;
      ctx.moveTo(M.sx[M.edges[e]], M.sy[M.edges[e]]); ctx.lineTo(M.sx[M.edges[e + 1]], M.sy[M.edges[e + 1]]);
    }
    ctx.lineCap = 'round'; ctx.lineWidth = 2 * (o.line || 1.2); ctx.strokeStyle = rgb(ink, 0.85); ctx.stroke(); ctx.lineCap = 'butt';
    if (o.ground > 0) {
      ctx.beginPath();
      for (let i = 0; i < M.nf; i++) {
        if (!M.front[i]) continue;
        const p = f[3 * i], q2 = f[3 * i + 1], r = f[3 * i + 2];
        ctx.moveTo(M.sx[p], M.sy[p]); ctx.lineTo(M.sx[q2], M.sy[q2]); ctx.lineTo(M.sx[r], M.sy[r]); ctx.closePath();
      }
      ctx.fillStyle = rgb(mix3(PAPER, M.colour, o.tint * o.colour), o.ground); ctx.fill();
    }
    project(M.c[0], M.c[1], M.c[2]);
    const cx = px, cy = py, rad = Math.min(Math.hypot(x1 - x0, y1 - y0) / 2 + 8, Math.hypot(W, H));
    const fine = clamp((x1 - x0) / 40, 0.35, 1);   // a small form takes less hatching, or it turns grey
    hatch(M, 0.3, 58, cx, cy, rad, ink, 0.3 * fine, 0.5);
    hatch(M, 0.52, 58, cx, cy, rad, ink, 0.3 * fine, 0.9);   // the same lines again, heavier: they swell into the dark
    hatch(M, 0.74, -32, cx, cy, rad, ink, 0.36 * fine, 0.7);
    ctx.globalAlpha = 1;
  };
  // the nuclei, the sweet and the sour spot and what the leads stimulate, the furthest first
  const drawForms = (list) => {
    list.forEach((it) => { const c = it.M.c; it.z = (c[0] - E[0]) * Fw[0] + (c[1] - E[1]) * Fw[1] + (c[2] - E[2]) * Fw[2]; });
    list.sort((x, y) => y.z - x.z).forEach((it) => drawSurface(it.M, it.alpha, it.o));
  };
  const nucleiForms = (reveal, alpha, tint, stn, later) => S.nuclei.map((M, ni) => ({ M,   // later: caudate and putamen, met on the way; stn: the target is on the sheet from the start
    alpha: alpha * (ni === 0 ? Math.max(stn * lerp(0.6, 1, reveal), reveal) : ni > 2 ? later : clamp(reveal * 2.2 - ni * 0.5)),
    o: { colour: tint, tint: 0.2, ground: 0.93 } }));
  // the field of a lead: its lines in ink, and on every line current that runs from the anode to the
  // cathode, its tail fading behind it. The current is the first colour of the drawing.
  const drawField = (field, reveal, alpha, t) => {
    if (alpha <= 0.01 || reveal <= 0) return;
    const vis = (f) => f.p.length / 3 * clamp(reveal * 1.6 - f.ph);
    ctx.beginPath();
    field.forEach((f) => trace(f.p, vis(f), false, 0, 0));
    ctx.lineWidth = 0.7; ctx.strokeStyle = rgb(INK, 0.3 * alpha); ctx.stroke();
    // the widest strokes are its light on the paper around it
    const TAIL = [[9, 15, 0.05], [9, 9, 0.09], [22, 1.2, 0.3], [11, 1.9, 0.6], [4, 2.9, 1]];
    ctx.lineCap = 'round';
    TAIL.forEach(([tail, width, a]) => {
      ctx.beginPath();
      field.forEach((f) => {
        const n = f.p.length / 3, v = vis(f);
        for (let c = 0; c < 3; c++) {   // three on every line, one behind the other
          const head = ((t * 0.26 + f.sp + c / 3) % 1) * (n + tail);
          let on = false;
          for (let j = Math.max(0, Math.floor(head - tail)); j <= Math.min(v - 1, n - 1, head); j++) {
            project(f.p[3 * j], f.p[3 * j + 1], f.p[3 * j + 2]);
            if (pz < 1) { on = false; continue; }
            if (on) ctx.lineTo(px, py); else ctx.moveTo(px, py); on = true;
          }
        }
      });
      ctx.lineWidth = width; ctx.strokeStyle = rgb(ACCENT, a * alpha); ctx.stroke();
    });
    ctx.lineCap = 'butt';
  };
  const nameSTN = (nm) => {   // only the target is named
    if (nm <= 0.01) return;
    project(...S.nuclei[0].top);
    const x = px, y = py, x2 = x - 26, y2 = y - 34;
    ctx.lineWidth = 0.8; ctx.strokeStyle = rgb(INK, 0.5 * nm); ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x2, y2); ctx.lineTo(x2 - 16, y2); ctx.stroke();
    label('STN', x2 - 22, y2, 0.85 * nm, 'right');
  };

  // ---------------------------------------------------------------- the fibres
  // every fibre sways a little along its length (more the further from the nucleus), as the lines of a
  // flow diagram do; the swayed points are kept, so every pass draws the same line
  const sway = (f, t, amp) => {
    const p = f.p, w = f.w, n = p.length / 3;
    for (let j = 0; j < n; j++) {
      const g = amp;
      w[3 * j] = p[3 * j] + g * Math.sin(j * 0.33 - t * 1.1 + f.ph);
      w[3 * j + 1] = p[3 * j + 1] + g * Math.cos(j * 0.29 - t * 0.9 + f.ph * 1.7);
      w[3 * j + 2] = p[3 * j + 2];
    }
  };
  // A fibre within reach of an electrified electrode takes up the signal where it passes that cathode;
  // each electrode drives its own wave (WAVES[0..2]) only after that electrode has landed and turned on.
  let WAVES = [0, 0, 0];
  const lit = (f) => {
    if (f.wave < 0) return 0;
    const a = WAVES[f.wave] || 0;
    return clamp((a - 0.45 * clamp(f.dmin / S.reach)) / 0.55);
  };
  const drawFibres = (reveal, act, alpha, t, heroOn, amp) => {
    if (reveal <= 0) return;
    const n = S.points, every = phone ? 2 : 1, world = F / DIST;
    const shown = (f) => n * clamp(reveal * 1.5 - hash(f.i) * 0.5);
    S.fibres.forEach((f) => sway(f, t, amp));
    // in ink: all of them
    ctx.beginPath();
    S.fibres.forEach((f) => { if (f.i % every === 0 || f.wave >= 0) trace(f.w, shown(f), false, 0, 0); });
    ctx.lineWidth = clamp(0.04 * world, 0.6, 1.3); ctx.strokeStyle = rgb(INK, 0.2 * alpha * (1 - 0.75 * ramp(act, 0.3, 0.8))); ctx.stroke();
    if (act <= 0) return;
    const on = S.fibres.filter((f) => f.wave >= 0 && lit(f) > 0);
    if (!on.length) return;
    on.forEach((f) => {
      const g = ease(lit(f));
      f.lo = Math.floor(f.jn * (1 - g));
      if (f.wave === 0) {
        // Wave 0 (STN) travels forward strictly up to the ALIC gate (f.ja), then unlocks past f.ja once ALIC sparks (WAVES[1])
        const gate = Math.max(f.jn, f.ja);
        const past = ease(WAVES[1] || 0);
        f.hi = Math.ceil(f.jn + (gate - f.jn) * g + (n - 1 - gate) * past);
      } else {
        f.hi = Math.ceil(f.jn + (n - 1 - f.jn) * g);
      }
    });
    const B = 18, len = n / B, width = clamp(0.085 * world, 1, 3.2);
    ctx.lineWidth = width; ctx.lineCap = 'round';
    for (let pass = 0; pass < 2; pass++) for (let b = 0; b < B; b++) {
      ctx.beginPath();
      on.forEach((f) => {
        if ((heroOn && f.hero) || !!f.bad !== !!pass) return;
        const j0 = Math.max(f.lo, Math.floor(b * len)), m = Math.min(f.hi, Math.floor((b + 1) * len));
        for (let j = j0, on = false; j <= m; j++) { project(f.w[3 * j], f.w[3 * j + 1], f.w[3 * j + 2]); if (pz < 2) { on = false; continue; } if (on) ctx.lineTo(px, py); else ctx.moveTo(px, py); on = true; }
      });
      ctx.strokeStyle = rgb((pass ? cold : warm)((b + 0.5) / B), 0.8 * alpha); ctx.stroke();
    }
    // the signal on each: a short gap of paper that runs up the fibre, away from the contact
    ctx.beginPath();
    on.forEach((f) => {
      const head = f.jn + ((t * 0.22 + f.ph) % 1) * (n - f.jn);
      if (head > f.hi) return;
      for (let j = Math.max(f.lo, Math.floor(head) - 2), q = 0; j <= Math.min(n - 1, head); j++, q++) { project(f.w[3 * j], f.w[3 * j + 1], f.w[3 * j + 2]); if (pz < 2) return; if (q) ctx.lineTo(px, py); else ctx.moveTo(px, py); }
    });
    ctx.lineWidth = width * 0.8; ctx.strokeStyle = rgb(PAPER, 0.9 * alpha); ctx.stroke(); ctx.lineCap = 'butt';
    // the ring where a fibre has just taken up the signal
    on.forEach((f) => {
      const g = lit(f);
      if (g >= 0.5) return;
      project(f.w[3 * f.jn], f.w[3 * f.jn + 1], f.w[3 * f.jn + 2]);
      if (pz < 2) return;
      ctx.beginPath(); ctx.arc(px, py, 3 + 26 * g, 0, 6.3); ctx.lineWidth = 1.2; ctx.strokeStyle = rgb(ACCENT, (1 - g * 2) * 0.9 * alpha); ctx.stroke();
    });
  };

  // ---------------------------------------------------------------- the fibre the view follows
  // a tube with a body: its shade on the paper, a darker rim, the colour, and a light along its upper
  // left side. The colours travel slowly along it.
  const hx = [], hy = [], hw = [], hz = [];
  const drawHero = (s, t, grow, down, amp) => {
    if (grow <= 0) return;
    const m = S.hp.length / 3, jn = S.hero.jn * 4, alpha = 1;
    const last = Math.max(jn + 2, Math.floor(s * (m - 1))), first = Math.max(0, Math.floor(jn - 16 * down));
    for (let j = first; j <= last; j++) {
      const g = amp;
      project(S.hp[3 * j] + g * Math.sin(j * 0.0825 - t * 1.1 + S.hero.ph), S.hp[3 * j + 1] + g * Math.cos(j * 0.0725 - t * 0.9 + S.hero.ph * 1.7), S.hp[3 * j + 2]);
      hx[j] = px; hy[j] = py; hz[j] = pz;
      hw[j] = grow * clamp(0.13 * F / Math.max(pz, 1), 1.4, 4) * Math.min(1, (last - j + 2) / 10 + 0.25, (j - first + 2) / 10 + 0.25);
    }
    const layer = (scale, ox, oy, colour, a, plus = 0) => {
      for (let j = first + 1; j <= last; j++) {
        const w = hw[j];
        if (hz[j] < 3 || hz[j - 1] < 3) continue;
        ctx.beginPath(); ctx.moveTo(hx[j - 1] + ox * w, hy[j - 1] + oy * w); ctx.lineTo(hx[j] + ox * w, hy[j] + oy * w);
        ctx.lineWidth = w * scale + plus; ctx.strokeStyle = rgb(colour(j / (m - 1)), a); ctx.stroke();
      }
    };
    // the fibre's own colours, as on the others around it
    const col = (u) => warm(u);
    ctx.lineCap = 'round';
    // drawn like the rest: an ink outline, flat colour, one pale line along it
    layer(1, 0, 0, col, alpha);
    // light running up it: the signal
    for (let c = 0; c < 3; c++) {
      const head = jn + ((t * 0.16 + c / 3) % 1) * (m - jn);
      if (head > last - 6) continue;
      const j = Math.floor(head);
      if (hz[j] < 3 || hz[Math.max(first, j - 5)] < 3) continue;
      ctx.beginPath(); ctx.moveTo(hx[Math.max(first, j - 5)], hy[Math.max(first, j - 5)]); ctx.lineTo(hx[j], hy[j]);
      ctx.lineWidth = hw[j] * 0.5; ctx.strokeStyle = rgb([255, 255, 255], 0.55); ctx.stroke();
    }
    ctx.lineCap = 'butt';
    // its head: where the signal is now
    const x = hx[last], y = hy[last], w = hw[last] * 4;
    ctx.beginPath(); ctx.arc(x, y, w * (0.5 + 0.08 * Math.sin(t * 3)), 0, 6.3); ctx.strokeStyle = rgb(INK, 0.35 * alpha); ctx.lineWidth = 0.8; ctx.stroke();
  };

  // ---------------------------------------------------------------- the brain
  // A drawing of the cortex made ahead of time (tools/story.py) for the view the story ends on: ink on
  // nothing. It is tinted with the page's ink on a sheet of its own and laid under the drawing once the
  // eye has come to rest in that view.
  const sheet = document.createElement('canvas'), sctx = sheet.getContext('2d'), brainImg = new Image();
  brainImg.onload = () => { layerKey = ''; kick(); };
  if (root.dataset.storyBrain) brainImg.src = root.dataset.storyBrain;
  const veil = document.createElement('canvas'), vctx = veil.getContext('2d'), part = document.createElement('canvas'), pctx = part.getContext('2d');
  veil.width = veil.height = 256;
  const win = document.createElement('canvas'), layers = [0, 1, 2].map(() => document.createElement('canvas'));
  win.width = win.height = 256;
  let seeds = null, layerKey = '';
  // The near hemisphere is seen through where the fibres run: there its lines stay, thinner, its tone
  // and its paper all but go, and behind the fibres stands the inner wall of the far hemisphere. So the
  // fibres lie between two drawn walls, inside the brain. Away from the fibres the cortex is whole.
  const THROUGH = [1, 1, 1], WHOLE = [0, 0.2, 0.1];
  const prepare = () => {
    const h = S.view.half * F, at = (x, y, z) => { project(x, y, z); return [(px - CX + h) / (2 * h) * 256, (py - CY + h) / (2 * h) * 256]; };
    const w = win.getContext('2d');
    w.clearRect(0, 0, 256, 256); w.globalCompositeOperation = 'lighter';
    const stamp = (q2, r, a) => {
      const gd = w.createRadialGradient(q2[0], q2[1], 0, q2[0], q2[1], r);
      gd.addColorStop(0, `rgb(0 0 0 / ${a})`); gd.addColorStop(1, 'rgb(0 0 0 / 0)');
      w.fillStyle = gd; w.fillRect(q2[0] - r, q2[1] - r, 2 * r, 2 * r);
    };
    S.fibres.forEach((f) => {
      if (f.dmin >= S.reach) return;
      const n = f.p.length / 3;
      // the window narrows towards a fibre's ends, so the fibre goes into the cortex there
      for (let j = 0; j < n; j += 5) stamp(at(f.p[3 * j], f.p[3 * j + 1], f.p[3 * j + 2]), 22, 0.22 * Math.min(1, j / n * 5, (n - 1 - j) / n * 5));
    });
    for (let j = 0; j < S.hp.length / 3; j += 8) stamp(at(S.hp[3 * j], S.hp[3 * j + 1], S.hp[3 * j + 2]), 30, 0.3);
    S.nuclei.forEach((M) => stamp(at(...M.c), 26, 0.5));
    // the brain comes up from the tract outwards, to its outline last
    const m = S.hp.length / 3 - 1;
    seeds = [0.1, 0.5, 0.9].map((u) => { const j = Math.round(u * m), q2 = at(S.hp[3 * j], S.hp[3 * j + 1], S.hp[3 * j + 2]); return [q2[0] / 256, q2[1] / 256]; });
  };
  const tinted = () => {
    const key = INK.join() + PAPER.join();
    if (key === layerKey) return;
    layerKey = key;
    const side = brainImg.naturalHeight;
    sheet.width = side; sheet.height = side;   // the far hemisphere, in ink
    sctx.globalCompositeOperation = 'copy'; sctx.drawImage(brainImg, 3 * side, 0, side, side, 0, 0, side, side);
    sctx.globalCompositeOperation = 'source-in'; sctx.fillStyle = rgb(INK); sctx.fillRect(0, 0, side, side);
    layers.forEach((c, k) => {   // the near one: its paper, its lines, its tone, each with the window in it
      c.width = side; c.height = side;
      const x = c.getContext('2d');
      x.drawImage(brainImg, [2, 0, 1][k] * side, 0, side, side, 0, 0, side, side);
      x.globalCompositeOperation = 'source-in'; x.fillStyle = rgb(k ? INK : PAPER); x.fillRect(0, 0, side, side);
      x.globalCompositeOperation = 'destination-out'; x.globalAlpha = 1 - THROUGH[k]; x.drawImage(win, 0, 0, side, side);
    });
  };
  // one sheet, as far as it has come up (gk): it spreads from where the activated fibres end
  const lay = (src, gk, alpha) => {
    if (gk <= 0) return;
    const side = src.width, h = S.view.half * F;
    if (gk < 1) {
      vctx.globalCompositeOperation = 'source-over'; vctx.clearRect(0, 0, 256, 256); vctx.globalCompositeOperation = 'lighter';
      const r = 256 * (0.1 + 1.3 * gk);
      seeds.forEach(([x, y]) => {
        const gd = vctx.createRadialGradient(x * 256, y * 256, r * 0.15, x * 256, y * 256, r);
        gd.addColorStop(0, 'rgb(0 0 0 / 1)'); gd.addColorStop(0.5, 'rgb(0 0 0 / 0.35)'); gd.addColorStop(1, 'rgb(0 0 0 / 0)');
        vctx.fillStyle = gd; vctx.fillRect(0, 0, 256, 256);
      });
      if (part.width !== side) { part.width = side; part.height = side; }
      pctx.globalCompositeOperation = 'copy'; pctx.drawImage(src, 0, 0);
      pctx.globalCompositeOperation = 'destination-in'; pctx.drawImage(veil, 0, 0, side, side);
      src = part;
    }
    ctx.globalAlpha = alpha; ctx.drawImage(src, CX - h, CY - h, 2 * h, 2 * h); ctx.globalAlpha = 1;
  };
  // g: how far the brain has come up. The far wall goes under the drawing, the near hemisphere over it:
  // first its paper, then its lines, then its tone, as a hand would draw it.
  const ready = (g) => {
    if (g <= 0.005 || !brainImg.naturalWidth) return false;
    if (!seeds) { prepare(); layerKey = ''; }
    tinted();
    return true;
  };
  const drawFar = (g) => { if (ready(g)) lay(sheet, clamp(g / 0.75), dark ? 0.4 : 0.5); };
  const drawBrain = (g) => {
    if (!ready(g)) return;
    [clamp(g / 0.75), clamp(g / 0.75), clamp((g - 0.35) / 0.65)].forEach((gk, k) => lay(layers[k], gk, WHOLE[k] * (k && dark ? 0.82 : 1)));
  };
  // A lead does not stand out of the head: it ends at the skull, just over the cortex, under a small
  // cap (the cable that goes on from there, under the scalp to the pulse generator, is left out).
  // Drawn after the brain: the lead's way in is a faint pair of lines seen through the cortex.
  const drawShaft = (Ld, alpha, i) => {
    if (alpha <= 0.01) return;
    const { o, a, r } = Ld, toEye = norm(sub(E, o)), nv = norm(cross(a, toEye));
    ctx.globalAlpha = alpha;
    [1, -1].forEach((sg, k) => { const pts = []; for (let j = 0; j <= 8; j++) pts.push(...add(add(o, a, lerp(12, Ld.entry, j / 8)), nv, sg * r)); sketch(new Float32Array(pts), 9, false, 0.8, 0.3, 211 + k * 17); });
    const top = add(o, a, Ld.entry + 1.5);
    // the cap over the burr hole
    project(...top);
    const cr = clamp(2.6 * F / pz, 2.5, 9);
    ctx.beginPath(); ctx.ellipse(px, py, cr, cr * 0.62, -0.5, 0, 6.3); ctx.fillStyle = rgb(PAPER, 1); ctx.fill(); ctx.lineWidth = 1.2; ctx.strokeStyle = rgb(INK, 0.9); ctx.stroke();
    ctx.globalAlpha = 1;
  };

  // ---------------------------------------------------------------- one frame
  let P = 0, T0 = performance.now(), born = 0, shownReal = -1;
  const render = root.querySelector('[data-story-render]'), note = root.querySelector('[data-story-note]');
  const frame = (now) => {
    const t = reduced.matches ? 40 : (now - T0) / 1000;
    // the opening plays by itself: the lead comes down into the nucleus without waiting for a scroll
    const p = reduced.matches ? Math.round(P) : P;
    // the lead comes down briskly as you begin scrolling (or gently on load)
    const down = reduced.matches ? 1 : Math.max(ramp(p, 0.02, 0.48), ramp((now - born) / 1000, 0.4, 3.0));
    const intro = reduced.matches ? 1 : ease(ramp((now - born) / 1000, 0, 1.1));
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, W, H);
    ctx.lineJoin = 'round';
    camera(p, t);
    const brain = ramp(p, 3.55, 4.0);
    const out = ramp(p, 3.25, 3.68);
    // brisk opening: nuclei appear while zooming in, then lead 1's field + spots switch on
    const reveal = ramp(p, 0.08, 0.56);
    const on = ramp(p, 0.54, 0.90);
    const stim = ramp(p, 0.84, 1.22);
    const near = 1 - 0.55 * ramp(p, 2.3, 2.85);
    // unhurried 3-electrode relay:
    //   1st: STN (S.lead) -> warm fibres travel up to ALIC gate and pause
    //   2nd: ALIC (others[0]) -> lands unobstructed, electrifies, unlocks STN fibres forward + sparks 38 frontal-capsule fibres
    //   3rd: NAc (others[1])  -> lands unobstructed in foreground, electrifies, sparks all 23 cold blue fibres
    const START = [1.72, 2.48];
    const leadIn = (i) => ease(ramp(p, START[i], START[i] + 0.32));
    const fieldIn = (i) => ramp(p, START[i] + 0.34, START[i] + 0.56);
    WAVES = [
      on >= 0.85 ? ramp(p, 1.08, 1.66) : 0,  // wave 0: STN warm fibres up to ALIC gate
      ramp(p, 2.10, 2.58),                    // wave 1: ALIC unlocks STN fibres forward + sparks 38 capsule fibres (after ALIC lands at 2.04 & field at 2.06)
      ramp(p, 2.86, 3.36),                    // wave 2: all 23 NAc blue fibres (after NAc lands at 2.80 & field at 2.82)
    ];
    const actAny = Math.max(WAVES[0], WAVES[1], WAVES[2]);
    const calm = 0.45 * (1 - 0.7 * ramp(p, 2.2, 2.7));
    drawForms(nucleiForms(reveal, 1 - 0.3 * ramp(p, 2.5, 3.0) - 0.2 * out, ramp(p, 0.82, 1.22), intro, 0.6 * ramp(p, 1.55, 2.1) + 0.4 * out));
    // inside the target, so drawn over it: the sweet and the sour spot
    drawForms(S.spots.map((M) => ({ M, alpha: stim * near, o: { colour: 1, tint: 0.36, ground: 0.9 } })));
    nameSTN(Math.max(ramp(p, 0.45, 0.62) * (1 - ramp(p, 0.68, 0.85)), intro * (1 - reveal)));
    // subtle grey tracts fade in as STN field turns on, then each wave lights strictly after its electrode's field
    drawFibres(ramp(p, 1.0, 1.45), actAny, 1 - 0.15 * ramp(p, 3.0, 3.35) * (1 - out), t, p > 2.10, calm);
    S.others.forEach((Ld, i) => {
      const g = leadIn(i);
      if (g > 0) {
        drawField(Ld.field, g >= 1 ? fieldIn(i) : 0, 1, t);
        drawLead(Ld, 30 * (1 - g), 1, 0, g >= 1 ? fieldIn(i) : 0, g);
      }
    });
    drawField(S.lead.field, down >= 1 ? on : 0, 1 - 0.55 * ramp(p, 2.3, 2.85) * (1 - out), t);
    drawLead(S.lead, 15 * (1 - ease(down)), intro, (1 - ramp(p, 0.18, 0.45)) * intro, down >= 1 ? ramp(p, 0.54, 0.78) : 0, 1 - 0.25 * ramp(p, 2.65, 3.0) * (1 - out));
    // the lead is in the nucleus, not before it: the nucleus once more, thin, over the lead
    const inside = 0.5 * reveal * (1 - ramp(p, 0.58, 0.78));
    if (inside > 0.01) drawSurface(S.nuclei[0], inside, { colour: 0, tint: 0, ground: 0.5 });
    drawHero(heroS(p), t, ease(ramp(p, 2.10, 2.36)), ramp(p, 2.28, 2.7), calm);
    // the brain closes over all of it; only the shafts outside the head stay in front
    S.cortex.forEach((M) => drawSurface(M, 0.9 * ease(brain), { colour: 0, tint: 0, ground: 0, line: 0.8, grow: lerp(0.94, 1, ease(brain)) }));
    [S.lead, ...S.others].forEach((Ld, i) => drawShaft(Ld, clamp(brain * 3), i));
    // the last step: the drawing gives way to a real render
    const real = render ? ease(ramp(p, 4.28, 4.48)) : 0;
    if (real !== shownReal) { shownReal = real; canvas.style.opacity = 1 - real; if (note) note.style.opacity = 1 - real; if (render) render.style.opacity = real; }
  };

  // ---------------------------------------------------------------- scroll, size, and when to draw
  // P: 0 when the first step's words stand in the middle of the window, 1 at the second step's, and so
  // on. A phone shows the words in place, so there P simply runs with the scroll, STEP of a window per step.
  const STEP = 0.5;
  const place = () => {
    const y = -root.getBoundingClientRect().top, H = window.innerHeight;
    if (phone) P = clamp(y / (H * STEP), 0, steps.length);
    else {
      const at = steps.map((s) => Math.max(0, s.offsetTop + s.offsetHeight / 2 - H / 2));
      at.push(at[at.length - 1] + steps[steps.length - 1].offsetHeight);
      let i = 0;
      while (i < steps.length - 1 && y > at[i + 1]) i++;
      P = clamp(i + (y - at[i]) / Math.max(1, at[i + 1] - at[i]), 0, steps.length);
    }
    const now = clamp(Math.round(P + 0.08), 0, steps.length - 1);
    steps.forEach((s, i) => s.classList.toggle('is-current', i === now));
  };
  const size = () => {
    W = stage.clientWidth; H = stage.clientHeight; phone = W < 760;
    DPR = Math.min(window.devicePixelRatio || 1, 2, Math.sqrt(5e6 / (W * H)));
    canvas.width = Math.round(W * DPR); canvas.height = Math.round(H * DPR);
    // the drawing's centre: right of the words on a desktop, above them on a phone
    CX = phone ? W * 0.5 : W * 0.69; CY = phone ? H * 0.35 : H * 0.52;
    F = (phone ? Math.min(W * 1.05, H * 0.6) : Math.min(W * 0.6, H * 1.05)) / (2 * Math.tan(20 * Math.PI / 180));
  };
  let raf = 0, seen = false;
  const loop = (now) => {
    raf = 0;
    if (!S || !seen || document.hidden) return;
    frame(now);
    if (!reduced.matches) raf = requestAnimationFrame(loop);
  };
  const kick = () => { if (!raf) raf = requestAnimationFrame(loop); };

  const start = (d) => {
    S = build(d);
    if (window.innerHeight < 520) { fallback(); return; }   // too low a window for a screen-tall stage: the stills stay
    readTheme(); size(); place();
    born = performance.now();
    root.classList.add('is-live');
    size();
    new IntersectionObserver((es) => { seen = es.some((e) => e.isIntersecting); kick(); }).observe(stage);
    addEventListener('scroll', () => { place(); kick(); }, { passive: true });
    addEventListener('resize', () => { size(); place(); kick(); });
    document.addEventListener('visibilitychange', kick);
    reduced.addEventListener?.('change', kick);
    new MutationObserver(() => { readTheme(); kick(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => { readTheme(); kick(); });
  };
  fetch(root.dataset.story).then((r) => (r.ok ? r.json() : Promise.reject())).then(start).catch(fallback);
})();
