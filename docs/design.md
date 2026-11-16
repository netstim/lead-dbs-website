# Design

The design system and how CI enforces it. Start with the [README](../README.md).

**The tokens are the design system, and CI enforces them** (`.github/scripts/check-design.py`, run on every
pull request by `.github/workflows/checks.yml` and before every deploy):

- type: `--t-xs` 12, `--t-label` 13, `--t-small` 14, `--t-note` 15, `--t-body` 16, `--t-doc` 17/18 (documentation
  text), `--t-lead`, `--t-card`, `--t-sub`, `--t-statement` (the one-sentence lead under a page head), `--t-h3`,
  `--t-h2`, `--t-h1`, `--t-display`; every `font-size` is one of them;
- font families: a named `--font-*` token or `inherit`, including `font:` shorthands; literal family names belong in font-face declarations and token definitions;
- radius: `--r-xs` 4, `--r-sm` 8, `--r-md` 12, `--r-lg` 20, `--r-pill`; every `border-radius` is one of them (or 0, 50%);
- weights 400, 500 and 600, or a named weight token;
- tokens are defined in `assets/css/base.css`, the palette (and `--render`/`--on-render`, the renders' black
  and the white on it) in `assets/css/site.css`;
- literal colours, `!important`, px spacing, literal line-heights and letter-spacings have budgets that may
  only go down.

A value that has to break a rule says why on its line: `/* design-exempt: <reason> */`.
`.github/scripts/check-copy.py` reads the built pages' text and fails on template leftovers, text that
describes the interface, and spelling outside the house style (fibre, colour, modelling, centre, email).

The styles are the site's own, one file per component in `assets/css/`, each with its tablet and phone
rules next to it (there are no separate phone sheets). `layouts/_partials/head.html` serves them as a few
minified, fingerprinted, render-blocking sheets (with SRI): the **shell** on every page, then the sheets of
the page's **family** (`layouts/_partials/page-family.html` decides which):

- the shell, one sheet, in this order:
  - `base.css`: the tokens (spacing `--s-1`…`--s-9`, type sizes `--t-*`, radii `--r-*`, the page margin
    `--gut`, the header height `--nav`), element defaults, the 12-column grid (`.grid`, `.span-*`, `.start-*`,
    from 1024 px), buttons (`.btn--primary`, `.btn--secondary`), links with an arrow (`.link`, the
    `svg.m-arrow` in the templates), the elevation scale (`--shadow-1` a small thing lifted off its ground,
    `--shadow-2` a printed sheet such as a flyer, `--shadow-3` what floats over the page: the menu band and
    dialogs; nothing else casts a shadow), form fields, the focus ring, hover and press feedback, the scroll
    lock under a modal dialog (`html:has(dialog:modal)`), and the reduced-motion rules;
  - `site.css`: the fonts and the palette (change colours and fonts here only; run as a Hugo template), the
    labels and figures every page shares, the preview banner;
  - `header.css`: the header, its menu band and sheet, and the menu without script;
  - `page.css`: an inner page's head and breadcrumb, the documentation text (also the manual's), its tables
    and pictures, the sidebar and the table of contents;
  - `components.css`: what several families share: captions, the citation box, buttons in text, videos and
    the video popup, form notes, the notice, "Related" and "More in …", a clip's pause button;
  - `search.css` (the dialog, /search/, the 404 page's doors) and `footer.css`;
- the families, loaded after the shell:
  - `home.css`: the home page alone, its sections in the order of the page;
  - `manual.css`: the manual (three-column reading layout, chapter tree, callouts, previous/next);
  - `gallery.css`: the gallery alone;
  - `content.css`: every other page: the content building blocks (catalogues, cells, hub sections, papers,
    quotes, video cards…) and the pages built from them (news, contributors, community); after it
    `events.css` on the events pages, `download.css` on Download, First steps and Contribute, and
    `features.css` on a page with the showcase shortcodes (`jumps`, `chapter`, `capabilities`, `tools`).

A rule for a component goes in its file, never in another family's; a rule a second family starts to need
moves down to `components.css` (or the shell file it belongs to). Sheets load in the order above, so a
family's rules come after the shell's at equal specificity.

The site's own script is one file per concern in `assets/js/main/`, with the helpers they share in
`assets/js/lib/` (`fragment.js`, a fragment as an id; `play-state.js`, the pause/play button of what moves by
itself). Hugo (`js.Build`, no npm) bundles them from the entries in `assets/js/bundles/`, which mirror the
style families; `layouts/baseof.html` loads `main.js` on every page and the family's bundle where there is one,
minified, fingerprinted and deferred:

- `main.js`: `header.js` (the menu sheet, the panels, the header over black), `theme.js` (light and dark),
  `page.js` (the table of contents, links into folds, paper rows, citation tabs, the old forum's addresses),
  `search.js` and `clipboard.js` (copy buttons and page-link copying);
- `home.js`: `home.js` (the hero's entrance and clip, the figure grid, the quotes, the globe's loader),
  `events.js` and `insertion.js` (the electrode insertion); once its section is near, home.js adds the
  globe (`globe.js` after its libraries, built in `layouts/home.html`);
- `content.js`: `videos.js`, `forms.js` and `clips.js` (silent clips);
- `events.js` (events by the visitor's clock, the countdown), `features.js` (the capabilities), `gallery.js`,
  `manual.js` (the chapter drawer, long code examples and the command tabs).

Each concern does nothing on a page without its markup and is a module, so its names stay its own. An atlas
catalogue also loads `atlas-filter.js`.

- **Sections take the height of their content.** The hero is the window's height less about 90 px (so the
  row of figures under it shows on the first screen; at least 540, at most 860 px) and grows with its
  content; the other sections share one vertical rhythm (`--rhythm`).
- **The header over black**: while one of the home page's black bands or the Download page's black head
  lies under it, the header is black (clear over the hero on a desktop) with white words; past it, the
  light bar returns (`main/header.js` sets `.is-dark` on `.nav` for any element marked `data-nav-dark`).
- **An inner page opens with its title and its task.** The breadcrumb, the title, then the content. Only
  pages one comes to look around carry their menu group's render in a wide rounded black panel under the
  title: page types hub and showcase, First steps (and Download, whose head is the one black band).
  Front matter `headRender: true` or `false` overrides that for one page
  (`layouts/_partials/page-head-render.html`). Event pages open with the title, the facts as hairline rows,
  the actions and the real flyer beside them (under them on a phone).
- **One group of links ends a page, never two**: its curated "Related" (front matter `next`) when it has
  one, else "More in …", the other pages of its menu group. A long doc page has only "On this page" in its
  right rail, sticky, a fixed gap from the text.
- **One short footer** (`layouts/_partials/footer.html`): the logo, Contact, the source code, News and its
  RSS feed, then the legal line (the institute, the research-use statement, Imprint, Privacy). It does not
  repeat the header's menu. The manual has its own one-line footer in the same 13 px muted type.
- **The menu band is as tall as its content**: a group of one section spreads its entries over the band's
  width; an entry shows the line under its name (`params.card`) unless `params.bandLine = false` in
  `hugo.toml`, for names that explain themselves (Contact, Events, Publications).
- **Lists of pages are rows, not cards**: a hairline row per page with its title, one short line and an
  arrow (`link-rows`, `resource-index`, "Related", "More in …", the atlas catalogues, Contribute's three ways).
  Boxes are kept for pictures (`atlas-hub`, `video-card`, the gallery) and for facts (`cells`, the summary
  box). One arrow everywhere: the chevron that grows a stem on hover.
- **The header switches to its menu sheet below 1200 px**, so the words, search and the button never
  collide. On a desktop the words sit beside the logo with short names (`params.short` in `hugo.toml`:
  "Docs", "Atlases"; breadcrumbs, the band and the sheet keep the full names), and the main action is a
  short "Download" pill (white on the black bar, dark grey on the light one). GitHub is linked from the
  menu sheet and the footer, not from the bar. A word's panel opens after the pointer rests on
  it for a moment (about 180 ms; switching between words is quicker), at once on keyboard focus.
- **The hero's entrance**: the title's words rise out of their lines in under 400 ms while the clip settles;
  the lead and the buttons stand from the first paint, so the main action never looks unavailable. The page
  head hides the title until `main/home.js` starts it, and fades it in anyway after 700 ms; under reduced
  motion nothing moves.

- Palette ("Blend", tokens at the top of `site.css`): white ground `#ffffff`, a grey surface `#f5f6f7`,
  warm dark grey ink `#2f3437`, muted `#6a6f74`; one action colour, deep blue `#2b5c8a` (buttons, links,
  focus); coral `#e0645a` as the one signal; periwinkle `#c6cdf7` and blush `#f4c6cf` as pale tints. The
  colours come from Wes Anderson films (The Darjeeling Limited, The Grand Budapest Hotel), the family of
  the logo's wedges. The renders sit on black: in a rounded panel under the title of a hub or showcase, and
  as the whole head of Download. No glow, grain or gradient is added to a render, on any screen size.
- Main website font: Inter, one variable file per script (`@fontsource-variable/inter` 5.2.5, licence in
  `static/fonts/OFL-inter.txt`) with the weight and optical-size axes, self-hosted in `static/fonts/`, with a
  fallback `@font-face` sized to its metrics so nothing moves when it arrives. The main website uses one face:
  400 text, 500 the menu, labels and values, 600 buttons and headings, large headings tracked tighter.
- Type scale at 1440 (tokens in `base.css`): 80 the hero, 48 home sections and page titles, 32 a page's
  sections, the Features chapters and the smaller home sections ("Upcoming events", "Latest news"), 23
  subsections and Features cards, 20 cards and the lead, 18 documentation text, 16 text elsewhere, 14 small
  print. Labels ("Release", "Input", "Manual", table heads, chapter numbers) are 13 px, medium weight, muted
  and in sentence case, one rule in `site.css` (`--font-label`, `--label-*`). Every date and time is a
  `<time>` element and every version or count a `.num` span, with figures of equal width; where the value
  is a line or cell of its own it is also medium weight.
- Text pages: 18 px on a desktop (17 on a phone), lines of about 70 characters.
- Motion: the hero's entrance and clip, the electrode insertion in the localization section, and on the home
  page the drifting quotes, the drifting grid of figures, the fan of covers and the globe. Each that moves by
  itself has a pause button (or holds on hover and focus) and stands still under reduced motion; hover and
  press feedback are short CSS transitions.
- Nothing loads from other servers (no web fonts, analytics or scripts from elsewhere); YouTube and Vimeo
  players load only when a visitor starts a video.
- The research-use statement is a short line, not a feature: the hero's "Intended use", the
  footer's legal line, and one small-print sentence on /about/ and the download page.
- Icons are inline SVGs in the templates (the header's in `layouts/_partials/header.html`); they take the
  colour of the text around them.
- After a change to a layout, check the home page at 1366×768, 1440×900 and 390×844, and that no page scrolls
  sideways on a phone.

The integrated manual uses the site's Inter, system monospace and palette, with its own compact type scale, open chapter navigation and a single-row header: vercel.com/docs's layout, not its typeface. Details in [manual.md](manual.md#visual-system).

## Manual regression checks

The manual uses the same design-token lint and unused-selector checks as the main site.
No extra lint exemptions were added for it. Manual Markdown and templates also reject
inline style attributes and style blocks, keeping presentation in the checked stylesheet. `check-browser.mjs` also checks the rendered
cascade on every manual page: opening prose must keep the article's body size, and
nested code must keep its containing block's size. The mobile search control must retain
an accessible name when its visible text is hidden.

The browser suite exercises long-code expansion and complete clipboard contents, drawer
focus containment and Escape/focus return, the introduction's next-page link, and search
excerpts. These tests run automatically in the existing pull-request and pre-deployment
workflows. They complement the full-site desktop/mobile light/dark layout and asset checks.
Visual resemblance and editorial quality still require rendered review; passing lint is
not a substitute for that judgment.

Share cards use Inter 4.001 (`git-66647c0bb`, recorded in each TTF name table), instanced at
weights 500 and 600 and `opsz=32` from the served Latin subset,
`static/fonts/inter-latin-var.woff2` (`@fontsource-variable/inter` 5.2.5). The original notice from
https://github.com/rsms/inter/blob/66647c0bb/LICENSE.txt accompanies both `assets/fonts/` and
`static/fonts/`. Reproduce outside Hugo with FontTools and Brotli:

```sh
fonttools ttLib.woff2 decompress static/fonts/inter-latin-var.woff2 -o /tmp/Inter.ttf
fonttools varLib.instancer /tmp/Inter.ttf wght=500 opsz=32 --output=assets/fonts/inter-share-500.ttf
fonttools varLib.instancer /tmp/Inter.ttf wght=600 opsz=32 --output=assets/fonts/inter-share-600.ttf
```

The resulting glyph outlines and horizontal metrics match the checked-in instances. No font build
runs in Hugo.

Docs and First steps open with the title and the task, without a render: they are the
documentation entry, and an image there only delays the choice.
Secondary actions stay plain links in both themes and at every breakpoint. A row without a
`text` value uses the title-only layout and never reserves a description track.
Supported browsers are current Chromium, Firefox and Safari with `:has()`, `:modal` and native
`dialog`. Manual chapter navigation remains a native disclosure if its external script fails.
