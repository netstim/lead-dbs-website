// Draws the charts of /usage/ from data/usage.json with Pele (https://pele.run, MIT), once, so the page
// ships plain SVG and no chart script: assets/diagrams/usage-<name>.svg, inlined by layouts/usage.html
// and themed with the --pele-* custom properties (assets/css/site.css, "usage"). Run after tools/usage.py:
//   npm ci && node scripts/usage.mjs        (Pele at the version locked in package-lock.json)
import { render } from 'pele';
import fs from 'node:fs';
const root = new URL('../', import.meta.url).pathname;
const D = JSON.parse(fs.readFileSync(root + 'data/usage.json', 'utf8'));

// the months as a number line of years: the first and last month as fractions of their year
const frac = (k) => +k.slice(0, 4) + (+k.slice(5, 7) - 1) / 12;
const first = frac(D.months[0][0]), last = frac(D.months.at(-1)[0]);
const wide = { xyChart: { width: 1200, height: 380 } };

const charts = {
  // launches per month, the years named on the axis
  months: `xychart-beta
  x-axis ${first} --> ${last}
  y-axis 0 --> ${Math.ceil(Math.max(...D.months.map((m) => m[1])) / 500) * 500}
  line [${D.months.map((m) => m[1]).join(', ')}]`,
  // a tile a country, sized by its launches; the smallest are left to the sentence under the chart
  countries: 'treemap-beta\n' + D.countries.slice(0, 36).map((c) => `"${c[1]}": ${c[2]}`).join('\n'),
  // the day as a dial: an axis an hour
  hours: `radar-beta
  axis ${D.hours.map((_, i) => `h${i}["${i % 3 ? ' ' : String(i).padStart(2, '0') + ':00'}"]`).join(', ')}
  curve a["Launches"]{${D.hours.join(', ')}}
  showLegend false
  min 0
  max ${Math.max(...D.hours)}`,
  // which tool is started
  tools: 'pie\n' + Object.entries(D.tools).sort((a, b) => b[1] - a[1]).map(([k, v]) => `  "${k}" : ${v}`).join('\n'),
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

for (const [name, src] of Object.entries(charts)) {
  let { svg } = render(src, { fontFamily: 'Inter', fontSize: 14, idPrefix: `u-${name}-`, config: name === 'months' ? wide : undefined });
  // the pie without its legend (the page lists the tools beside it): cut the drawing to the circle
  if (name === 'tools') svg = svg.replace(/viewBox="0 0 [\d.]+ ([\d.]+)" width="[\d.]+"/, 'viewBox="0 0 $1 $1" width="$1"').replace(/<g class="pele-legend".*?<\/g><\/g>/s, '');
  // the tiles: each says its part of the world (data-region), which the stylesheet colours
  if (name === 'countries') for (const c of D.countries.slice(0, 36)) svg = svg.replace(`data-id="${esc(c[1])}"`, `data-id="${esc(c[1])}" data-region="${regionOf(c[0])}"`);
  // the months: the area under the line, and a dot with its figure on the busiest month
  if (name === 'months') {
    const d = svg.match(/class="pele-series pele-line"[^>]*><path d="([^"]+)"/)[1];
    const pts = d.slice(1).split('L').map((p) => p.split(',').map(Number));
    const vals = D.months.map((m) => m[1]);
    const hi = vals.indexOf(Math.max(...vals)), lo = vals.indexOf(Math.min(...vals));
    const base = pts[lo][1] + (pts[lo][1] - pts[hi][1]) * vals[lo] / (vals[hi] - vals[lo]);   // y of 0 launches
    const area = `<path class="pele-area" d="${d}L${pts.at(-1)[0]},${base.toFixed(2)}L${pts[0][0]},${base.toFixed(2)}Z"/>`;
    const when = new Date(D.months[hi][0] + '-15').toLocaleDateString('en-GB', { month: 'long', year: 'numeric' });
    const peak = `<g class="pele-peak"><circle cx="${pts[hi][0]}" cy="${pts[hi][1]}" r="5"/><text x="${pts[hi][0] - 12}" y="${pts[hi][1] - 4}" text-anchor="end" font-size="13">${vals[hi].toLocaleString('en')} in ${when}</text></g>`;
    svg = svg.replace('<g class="pele-series pele-line"', area + '<g class="pele-series pele-line"').replace(/<\/svg>\s*$/, peak + '</svg>');
  }
  fs.writeFileSync(`${root}assets/diagrams/usage-${name}.svg`, svg.replace(/^<svg /, '<svg aria-hidden="true" focusable="false" ') + '\n');
  console.log(`usage-${name}.svg`);
}
