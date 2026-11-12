// Draws the charts of /usage/ from data/usage.json with Pele (https://pele.run, MIT), once, so the page
// ships plain SVG and no chart script: assets/diagrams/usage-<name>.svg, inlined by layouts/usage.html
// and themed with the --pele-* custom properties (assets/css/site.css, "usage"). Run after tools/usage.py:
//   npm ci && node scripts/usage.mjs        (Pele at the version locked in package-lock.json)
import { render } from 'pele';
import fs from 'node:fs';
const root = new URL('../', import.meta.url).pathname;
const D = JSON.parse(fs.readFileSync(process.argv[2] || root + 'data/usage.json', 'utf8'));
if (D.schema !== 2) throw new Error('Expected usage schema 2');
const output = process.argv[3] || root + 'assets/diagrams';
fs.mkdirSync(output, { recursive: true });

// Explicit month positions and null gaps: no interpolated data or dependence on
// the renderer's internal SVG path structure. Partial months remain labelled.
const xml = (s) => String(s).replace(/[&<>"']/g, (c) => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;'}[c]));
const empty = () => '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 200"><text x="300" y="100" text-anchor="middle" fill="currentColor">No recorded observations</text></svg>';
function monthly() {
  if (!D.months.some((m) => m[1] !== null)) return empty();
  const max = Math.max(1, ...D.months.map((m) => m[1] ?? 0));
  const top = Math.ceil(max / 500) * 500;
  const x = (i) => 70 + i * 1060 / Math.max(1, D.months.length - 1);
  const y = (n) => 320 - n / top * 270;
  let svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 390" font-family="Inter, sans-serif" font-size="14" fill="currentColor">';
  for (let i = 0; i <= 4; i++) {
    const n = top * i / 4, at = y(n);
    svg += `<path d="M70,${at}H1130" stroke="var(--pele-line)"/><text x="60" y="${at + 5}" text-anchor="end">${n}</text>`;
  }
  let segment = [];
  const flush = () => {
    if (!segment.length) return;
    const path = segment.map(([px, py], i) => `${i ? 'L' : 'M'}${px},${py}`).join('');
    svg += `<path class="pele-area" d="${path}L${segment.at(-1)[0]},320L${segment[0][0]},320Z"/><path class="pele-line" d="${path}" fill="none" stroke="var(--pele-series-1)"/>`;
    for (const [px, py] of segment) svg += `<circle cx="${px}" cy="${py}" r="2" fill="var(--pele-series-1)"/>`;
    segment = [];
  };
  D.months.forEach(([month, n], i) => {
    if (n === null) flush();
    else if (D.partial_months.includes(month)) {
      flush();
      svg += `<circle cx="${x(i)}" cy="${y(n)}" r="4" fill="var(--pele-bg)" stroke="var(--pele-series-1)"><title>${month}: ${n} (partial month)</title></circle>`;
    } else segment.push([x(i), y(n)]);
    const stride = Math.max(1, Math.ceil(D.months.length / 10));
    if (i % stride === 0 || i === D.months.length - 1) {
      if (i !== D.months.length - 1 && D.months.length - 1 - i < stride / 2) return;
      svg += `<text x="${x(i)}" y="352" text-anchor="middle">${month}</text>`;
    }
  });
  flush();
  const vals = D.months.map((m) => m[1] ?? -1), peak = vals.indexOf(Math.max(...vals));
  const label = `${D.months[peak][0]}: ${vals[peak]}${D.partial_months.includes(D.months[peak][0]) ? ' (partial)' : ''}`;
  svg += `<g class="pele-peak"><circle cx="${x(peak)}" cy="${y(vals[peak])}" r="5"/><text x="${Math.min(950, Math.max(220, x(peak)))}" y="25" text-anchor="middle">${xml(label)}</text></g>`;
  return svg + '</svg>';
}

const toolOrder = ['Lead-DBS', 'Lead Group', 'Lead Connectome', 'Lead Anatomy', 'Other / unknown'];
const presentTools = toolOrder.filter((k) => D.tools[k] > 0);
const charts = {
  // a tile a country, sized by its recorded requests; the smallest are left to the sentence under the chart
  countries: 'treemap-beta\n' + D.countries.slice(0, 36).map((c) => `"${c[1]}": ${c[2]}`).join('\n'),
  // the day as a dial: an axis an hour
  hours: `radar-beta
  axis ${D.hours.map((_, i) => `h${i}["${i % 3 ? ' ' : String(i).padStart(2, '0') + ':00'}"]`).join(', ')}
  curve a["Requests"]{${D.hours.join(', ')}}
  showLegend false
  min 0
  max ${Math.max(1, ...D.hours)}`,
  // requests attributed to each tool
  tools: 'pie\n' + presentTools.map((k) => [k, D.tools[k]]).map(([k, v]) => `  "${k}" : ${v}`).join('\n'),
};

// the part of the world of each country drawn as a tile (ISO 3166 numeric code): the tiles take its colour
const REGIONS = {
  americas: '840 124 076 032 152 484 170 604 858 218 188 591',
  europe: '276 826 380 250 724 756 528 620 056 752 203 643 040 348 703 246 616 578 442 705 208 372 300 642 100 191 688 804 233 428 440 352 196 470',
  asia: '156 392 158 344 410 356 376 702 792 764 458 360 704 608 586 364 682 784 634 400 422 050 144',
  oceania: '036 554',
};
const regionOf = (code) => Object.keys(REGIONS).find((r) => REGIONS[r].split(' ').includes(code)) || 'other';
const esc = (t) => t.replace(/&/g, '&amp;');

for (const [name, src] of Object.entries({months: null, ...charts})) {
  const noData = (name === 'countries' && !D.countries.length) || (name === 'hours' && !D.hours.some((n) => n > 0)) || (name === 'tools' && !Object.values(D.tools).some((n) => n > 0));
  let svg = name === 'months' ? monthly() : noData ? empty() : render(src, {fontFamily: 'Inter', fontSize: 14, idPrefix: `u-${name}-`}).svg;
  // the pie without its legend (the page lists the tools beside it): cut the drawing to the circle
  if (name === 'tools' && !noData) svg = svg.replace(/viewBox="0 0 [\d.]+ ([\d.]+)" width="[\d.]+"/, 'viewBox="0 0 $1 $1" width="$1"').replace(/<g class="pele-legend".*?<\/g><\/g>/s, '');
  // Keep each tool's swatch stable even when preceding categories are absent.
  if (name === 'tools' && !noData) svg = svg.replace(/var\(--pele-series-(\d+),/g, (_, n) => `var(--pele-series-${toolOrder.indexOf(presentTools[Number(n) - 1]) + 1},`);
  // the tiles: each says its part of the world (data-region), which the stylesheet colours
  if (name === 'countries') for (const c of D.countries.slice(0, 36)) svg = svg.replace(`data-id="${esc(c[1])}"`, `data-id="${esc(c[1])}" data-region="${regionOf(c[0])}"`);
  fs.writeFileSync(`${output}/usage-${name}.svg`, svg.replace(/^<svg /, '<svg aria-hidden="true" focusable="false" ') + '\n');
  console.log(`usage-${name}.svg`);
}
