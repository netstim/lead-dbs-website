// Renders the Mermaid-style diagrams in assets/diagrams/*.mmd to SVG with Pele (https://pele.run, MIT),
// once, so the site ships plain SVG and no diagram script. Each .mmd gives <name>.svg (left to right) and
// <name>-tb.svg (top to bottom, for phones); layouts inline them and theme them with the --pele-* custom
// properties (assets/css/site.css). Run after editing a .mmd:
//   npm install --no-save pele@1.13.0 && node scripts/diagrams.mjs
import { render } from 'pele';
import fs from 'node:fs';
import path from 'node:path';
const dir = new URL('../assets/diagrams/', import.meta.url).pathname;
for (const f of fs.readdirSync(dir).filter((f) => f.endsWith('.mmd'))) {
  const src = fs.readFileSync(path.join(dir, f), 'utf8');
  const name = f.replace(/\.mmd$/, '');
  for (const [suffix, text] of [['', src], ['-tb', src.replace(/^flowchart LR/m, 'flowchart TB')]]) {
    const { svg } = render(text, { fontFamily: 'Inter', fontSize: 15 });
    fs.writeFileSync(path.join(dir, `${name}${suffix}.svg`), svg.replace(/^<svg /, '<svg aria-hidden="true" focusable="false" ') + '\n');
    console.log(`${name}${suffix}.svg`);
  }
}
