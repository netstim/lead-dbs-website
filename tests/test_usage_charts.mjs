// Synthetic chart edge cases; no private data or browser required.
import {mkdtempSync, writeFileSync, readFileSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import assert from 'node:assert/strict';
const dir = mkdtempSync(join(tmpdir(), 'usage-charts-'));
try {
  for (const months of [[], [['2026-01', 5]], [['2026-01', 5], ['2026-02', 5]], [['2026-01', 5], ['2026-02', null], ['2026-03', 8]]]) {
    const file = join(dir, 'input.json');
    writeFileSync(file, JSON.stringify({schema: 2, months, partial_months: [], countries: [], hours: Array(24).fill(0), tools: {}}));
    execFileSync(process.execPath, ['scripts/usage.mjs', file, dir]);
    for (const name of ['months', 'countries', 'hours', 'tools']) {
      const svg = readFileSync(join(dir, `usage-${name}.svg`), 'utf8');
      assert(!/NaN|Infinity|undefined/.test(svg));
      assert(svg.includes('<svg'));
    }
    if (months.some((m) => m[1] === null)) {
      const svg = readFileSync(join(dir, 'usage-months.svg'), 'utf8');
      assert.equal((svg.match(/class="pele-line"/g) || []).length, 2, 'Do not connect across missing months');
    }
  }
  const file = join(dir, 'input.json');
  writeFileSync(file, JSON.stringify({schema: 2, months: [], partial_months: [], countries: [], hours: Array(24).fill(0), tools: {'Other / unknown': 1}}));
  execFileSync(process.execPath, ['scripts/usage.mjs', file, dir]);
  assert(readFileSync(join(dir, 'usage-tools.svg'), 'utf8').includes('var(--pele-series-5,'), 'Unknown tool must use its own swatch even alone');
  console.log('Chart empty, single-point, flat, gap and tool-colour cases passed.');
} finally { rmSync(dir, {recursive: true, force: true}); }
