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
  and the white on it) at the top of `assets/css/site.css`;
- literal colours, `!important`, px spacing, literal line-heights and letter-spacings have budgets that may
  only go down.

A value that has to break a rule says why on its line: `/* design-exempt: <reason> */`.
`.github/scripts/check-copy.py` reads the built pages' text and fails on template leftovers, text that
describes the interface, and spelling outside the house style (fibre, colour, modelling, centre, email).

The styles are the site's own, in the files that `layouts/_partials/head.html` bundles into one
fingerprinted stylesheet:

- `assets/css/base.css`: the tokens (spacing `--s-1`…`--s-9`, type sizes `--t-*`, radii `--r-*`, the page
  margin `--gut`, the header height `--nav`), element defaults, the 12-column grid (`.grid`, `.span-*`,
  `.start-*`, from 1024 px), buttons (`.btn--primary`, `.btn--secondary`), links with an arrow (`.link`, the
  `svg.m-arrow` in the templates), the elevation scale (`--shadow-1` a small thing lifted off its ground,
  `--shadow-2` a printed sheet such as a flyer, `--shadow-3` what floats over the page: the menu band and
  dialogs; nothing else casts a shadow), form fields, the focus ring, hover and press feedback, the scroll
  lock under a modal dialog (`html:has(dialog:modal)`), and the reduced-motion rules.
- `assets/css/site.css`: the palette and fonts (change colours and fonts here only), the header, the home
  page, the documentation pages, the gallery, events, search and the footer.
- `assets/css/content.css`: the content building blocks that come after those: hub cards with a line of
  text, the copy box, clips, the newer/older links under news posts, and the Features chapters and cards.
- `assets/css/manual.css`: the manual's three-column reading layout, responsive chapter tree, callouts and previous/next navigation. It shares the existing palette and type tokens.
- `assets/css/phone.css`: the phone layout (below 640px only, every rule in one `@media (max-width: 639px)`
  block) of what several pages share: the header, the inner page head, buttons in heroes, the "Related"
  and "More in …" rows, open frames, chip rows and the download page's small rules.
- `assets/css/phone-home.css`, `assets/css/phone-events.css`, `assets/css/phone-features.css`: the phone
  layout of the home page, the events pages and the Features page, loaded after `phone.css`, below 640px
  only as well.

The site's own script is one file per concern in `assets/js/main/`, which `layouts/baseof.html` bundles into
one `main.js`: `header.js` (the menu sheet, the panels, the header over black), `theme.js` (light and dark),
`page.js` (the table of contents, links into folds, paper rows, citation tabs, the old forum's addresses),
`home.js` (the hero's entrance and clip, the figure strip), `events.js` (events by the visitor's clock, the
countdown), `videos.js`, `news.js`, `features.js` (the capabilities), `gallery.js`, `forms.js`, and `manual.js` (the chapter drawer, long code examples and the command tabs; page-link copying is `clipboard.js`). Each block does
nothing on a page without its markup, and each keeps its names to itself (an arrow-function scope), so
they cannot collide in the one bundle. Beside them, every page loads `search.js` and `clipboard.js`; the
home page `insertion.js` (the electrode insertion) and, once its section is near, `globe.js`; an atlas
catalogue `atlas-filter.js`. (Splitting the stylesheet and the bundle by page family is a later step.)

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
