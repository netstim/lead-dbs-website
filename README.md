# lead-dbs.org

> [!WARNING]
> **Under construction.** This repository holds the *upcoming* version of the Lead-DBS website.
> The official website is still **[www.lead-dbs.org](https://www.lead-dbs.org)**: use it for
> downloads, documentation and news. The preview at
> [netstim.github.io/lead-dbs-website](https://netstim.github.io/lead-dbs-website/) is a work in
> progress: its forms (download, contact, newsletter) are not connected yet, and its content
> may be incomplete or out of date.

Source of the [Lead-DBS](https://www.lead-dbs.org) website, built with [Hugo](https://gohugo.io).
Pages are Markdown files in `content/`; every push to `main` builds the site and publishes a
preview to GitHub Pages.

Content was imported from the previous WordPress site on 2026-11-10.

## Run it locally

Install Hugo **extended**, version 0.169.0 or newer ([releases](https://github.com/gohugoio/hugo/releases)), then:

```bash
hugo server            # http://localhost:1313, reloads on every save
hugo server -F         # the same, with pages whose date is still in the future
hugo --gc --minify     # production build into public/
```

No npm, bundler or CDN in the build: Hugo is the only tool (`package.json` only locks the checks' and
diagrams' Node tools, Playwright and Pele). The first build of a fresh clone makes the resized
images (a few hundred files in `resources/_gen/`, which is not committed); that takes about half a
minute, later builds take a second.

The build prints a warning for every Markdown image without alt text (`image-alt`): those are the
pictures a screen-reader user cannot see. Write the alt text and the warning goes.

## Where things are explained

| Read | For |
|---|---|
| This file | running the site, page types, where to edit, the checks, deployment |
| [docs/manual.md](docs/manual.md) | the integrated user guide, chapter navigation, imported figures and migration boundaries |
| [docs/editing.md](docs/editing.md) | pictures and videos, writing, shortcodes, atlas catalogues, events, news posts, releases |
| [docs/structure.md](docs/structure.md) | the menu and the footer, search, metadata, old addresses |
| [docs/design.md](docs/design.md) | the design tokens, the palette and type, motion, the CSS and JS files |
| [docs/home-and-media.md](docs/home-and-media.md) | the home page's renders and clip, the electrode insertion, the gallery, the usage figures |

## Page types

A page's look follows from its type alone (front matter `layout`; `hugo new content --kind <type>` writes
it from `archetypes/`); no page switches its own sidebar or contents (`layouts/_partials/page-type.html`
stops the build on `sidebar:`, `related:` and `toc:`, and on an unknown type).

| Type | For | Width | Sidebar |
|---|---|---|---|
| `manual` | the user guide at `/manual/` | reading column | chapters left, local outline right |
| `doc` (default) | Cite, Publications, Slack, Contact, past workshops, the method articles, About the MNI spaces, the atlas catalogues, legal pages, news posts | the text column | "On this page" on a long page |
| `contributors` | Contributors (`layouts/about/contributors.html`): who coordinates Lead-DBS, then the people | the text column | "On this page" |
| `event` | an event page (`layouts/event.html`): title, facts and registration from `data/events.yaml`, the flyer beside them | full | none |
| `showcase` | one tool or atlas (DISTAL, FOCUS, Lead-OR, Lead Tutor, Walkthrough videos) and the Features overview | full | none |
| `hub` | a menu group's page (Docs and help, Atlases and data, About) | full | none; its body is the section's list |
| own template | Home, Download, First steps, Contribute, Events, Gallery, Community, Usage, News | full | none |

The right rail holds only **"On this page"**, when the page has three or more `##` sections
(`site.Params.tocMinHeadings`), sticky while the page is read; a shorter page has no rail. Below 1024px it
folds under the title. `check-site.py` fails on an empty sidebar.

Hubs, showcases and Download open with their menu group's render under the title (the Docs hub opts out);
every other page
opens with its title and its task. Front matter `headRender: true` or `false` overrides that for one page
(`layouts/_partials/page-head-render.html`).

Every page ends with **one** group of links: its **"Related"** (`layouts/_partials/next-steps.html`) when it
has up to three `next:` links to pages outside its own section, else **"More in …"**, the other pages of
its menu group (`section-nav.html`); one hairline row each, title only.

```yaml
next:
  - {page: "/helpsupport/first-steps/"}                                       # named by its linkTitle
  - {page: "/develop/#add-your-atlas-or-dataset", name: "Add your atlas or dataset"}
  - {page: "/manual/", name: "Manual"}                # the integrated manual
```

Point to the related page, the next tutorial step or the section's hub; write no "Next" section in the text.
The build stops on a path that is not a page or is the page itself, on an entry that has neither `page` nor
`url` and `name`, and on more than three entries; links to pages of the page's own section are left out
(the header's menu lists them). News posts link their newer and older post and "All news" by themselves.

### Add a page

```bash
hugo new content about/my-page/index.md                   # a doc page; --kind hub, showcase or event for the others
```

Give it a `title`, a `description` (at most 155 characters) and, if it belongs in the menu, an entry in
`hugo.toml` → `[menus]`. Do not set a width, a sidebar or a table of contents: the type decides them.

## Editing

| What | Where |
|---|---|
| A page | `content/<url path>/index.md` (or `_index.md` if the page has sub-pages) |
| Images of a page | Same folder as its `index.md`: `![What the picture shows](figure.png)` (see [Pictures in pages](docs/editing.md#pictures-in-pages)) |
| A news post | `content/news/<slug>/index.md`; appears at `/<slug>/` (see [Add a news post](docs/editing.md#add-a-news-post)) |
| **A new release** | `data/release.yaml` and `data/releases.yaml`, plus a news post (see [Cut a release](docs/editing.md#cut-a-release)) |
| A paper about Lead-DBS, a method or a tool | `data/papers.yaml` (see [Building blocks](docs/editing.md#building-blocks): `paper`, `papers`) |
| Requirements and install steps (download page; First steps links there) | `data/release.yaml` (MATLAB, toolboxes, SPM12, memory) and `data/install.yaml` (disk space, data, the steps and their small pictures) |
| An atlas or parcellation | `atlases.yaml` next to the atlas page's `index.md` (see [Atlas catalogues](docs/editing.md#atlas-catalogues)) |
| Home page texts, quotes, help links, history, funders, citation; the hero's `proof` (a list of short parts) and `manual` (`{label, url}`, shown as a fact) | `content/_index.md` (front matter only; the layout is `layouts/home.html`) |
| **Events** (developer meetings, workshops) | `data/events.yaml` (see [Events](docs/editing.md#events)) |
| Home page pictures | `assets/images/renders/` (see [Pictures on the home page](docs/home-and-media.md#pictures-on-the-home-page)) |
| Gallery ("Made with Lead-DBS", `/gallery/`) | Figures from papers: `data/gallery.yaml` + image files in `static/gallery/`. Lab renders: their alt text and captions in `data/renders.yaml` (also read by Features), the ones the gallery shows and their order in `content/gallery/_index.md` (see [Gallery](docs/home-and-media.md#the-gallery-of-published-figures)) |
| The footer's link to the institute | the first link of `data/links.yaml` `footer` |
| A page's closing cards | its front matter `next:` (see [Page types](#page-types)) |
| Main menu, legal links, the GitHub link | `hugo.toml` → `[menus]` (the entry with `params.role = "action"`, identifier `download`, is drawn as the header's button) and `[params] github`; see [Site structure](docs/structure.md) |
| Download / contact / developer-meeting form fields | `data/forms.yaml` |
| Colours, fonts, page styles | `assets/css/site.css` (palette, fonts); tokens, buttons, grid: `assets/css/base.css`; one file per component or page family, phone rules included (see [Design](docs/design.md)) |
| Templates | `layouts/` |

## Checks

Every pull request runs `.github/workflows/checks.yml` (and `backend.yml` for the server side), and every deploy runs the same scripts
(`.github/scripts/`, Python standard library only). Run them before you push:

```bash
hugo --gc -d /tmp/site && HUGO_PARAMS_PREVIEW=true hugo --gc -d /tmp/preview --baseURL https://netstim.github.io/lead-dbs-website/
python3 .github/scripts/check-site.py /tmp/site https://www.lead-dbs.org/   # links, anchors, redirects, canonicals, sidebars, forms
python3 .github/scripts/check-site.py /tmp/preview https://netstim.github.io/lead-dbs-website/   # the same, and noindex on every page
python3 .github/scripts/check-design.py                                     # tokens, radii, type, budgets
python3 .github/scripts/check-copy.py /tmp/site                             # leftovers, house spelling and names, editorial surface; prints tone warnings
python3 .github/scripts/check-css-used.py /tmp/site /tmp/preview            # unused CSS class references (not selector structure)
```

A build is the production build when its baseURL is `https://www.lead-dbs.org/`, and a preview otherwise.

A second job opens every page of the build (every `index.html` that is not a redirect, and the 404 page) in
Chromium on a desktop and a phone, light and dark, and fails on script errors, missing files or pictures,
pictures that do not finish loading, anything drawn past the screen's edge, text cut off in its box and
requests to other servers (it measures once the fonts are in, with reduced motion); its screenshots are kept
with the run (Summary → Artifacts). Then `check-interactions.mjs` uses the phone menu (also by Tab and
Shift+Tab, at 820 and 390 px), the search (with "/" and the button), the atlas filter, the download page's terms
dialog and the gallery's lightbox with the mouse and the keyboard, and fails when one stops opening, closing or
giving the focus back, or lets the page scroll behind it. It also opens the home page with motion (the hero's
words and actions show at once; the video, quotes and figure grid can be paused, and the quotes' button is not
covered), the manual at a malformed address fragment (`#%`), the phone menu, the manual's chapters and the videos
without script, and a short WebKit run (menu, manual drawer, search), skipped with a note when WebKit is not
installed. The Pages workflow runs both on the production build before it deploys. They need Node:

```bash
npm ci && npx playwright install chromium webkit   # the versions locked in package-lock.json
node .github/scripts/check-browser.mjs /tmp/site https://www.lead-dbs.org/ /tmp/screenshots   # about a minute
node .github/scripts/check-interactions.mjs /tmp/site https://www.lead-dbs.org/                 # a few seconds
```

The server side (`server/`, `tools/deploy.py`, the importers) is tested by `.github/workflows/backend.yml`,
which runs every test in `tests/` with none skipped. Locally, `python3 -m unittest discover -s tests` skips
what needs PHP, Composer's packages (`composer install` in `server/analytics/`), Apache or Hugo when they are
missing; `LEAD_REQUIRE_INTEGRATION=1` makes those fail instead.

`check-design.py` keeps budgets for literal colours (named colours too), `!important`, px spacing, literal
line-heights and letter-spacings that may only go down;
after removing some, `--ratchet` lowers them. Its `KNOWN` list names the rule breaks the stylesheets already
had when it began to read whole declarations; fix one and remove it from the list. See [docs/design.md](docs/design.md).

## Deployment

The preview is built by `.github/workflows/pages.yml` for GitHub Pages under `/lead-dbs-website/`, with
`HUGO_PARAMS_PREVIEW=true` (banner, `noindex`, canonical addresses pointing at www.lead-dbs.org). The same
workflow also builds the site for `https://www.lead-dbs.org/`, and runs `.github/scripts/check-site.py` on both
builds; the run fails on a broken internal link, image or #anchor, a redirect that leads nowhere or to another
redirect, a canonical or og:url that is not the page's address on www.lead-dbs.org, an og:image or sitemap
address that is not absolute, or front matter shown as page text. It then opens every page of the production
build in a browser (`check-browser.mjs`, `check-interactions.mjs`) and deploys only if all of that passes.
Run it locally the same way:

```bash
hugo --gc -d /tmp/site && python3 .github/scripts/check-site.py /tmp/site https://www.lead-dbs.org/
```

A production build is `hugo --gc --minify` with the default `baseURL` (`https://www.lead-dbs.org/`).

**Before the domain moves:** every download button calls `https://www.lead-dbs.org/release/download.php?id=…`
on the current WordPress server, and several pages link PDFs under `/docs/` and newsletters under `/?na=view&id=…`
there. A static host serves none of these. So either deploy the new site **onto that same server**, leaving
`/release/` and `/docs/` (and their PHP) in place beside it, or give those files a new home first (for example a
`files.lead-dbs.org`) and change the links. Test a download button after the switch.

**The switch** itself (packaging, putting the site into the web root beside WordPress, the `.htaccess`, the
checks and the rollback) is described in [docs/launch.md](docs/launch.md).

The contact and FOCUS forms send to `forms/send.php`, a small PHP script in `server/forms/` that is not on
the server yet; [its README](server/forms/README.md) says how to put it there and check it before
`formsEnabled` is set to true. The newsletter form keeps its News/RSS/Slack line until the newsletter service is
decided.

## Re-importing from WordPress

`tools/import_wordpress.py` converted the WordPress pages to Markdown. It was meant to run once. To look
again, report what it would do, or import into a separate folder and copy what you want by hand
(`--snapshot` keeps WordPress's answers, so a second run asks it for nothing):

```bash
uv run tools/import_wordpress.py --plan --out /tmp/wp-import --snapshot /tmp/wp-snapshot   # report only
uv run tools/import_wordpress.py --out /tmp/wp-import --snapshot /tmp/wp-snapshot          # a new, empty folder
```

Writing straight into `content/` takes `--out content --in-place`; adding `--force` overwrites any edits made
since, `content/news/_index.md` included.

## Templates

- Every page with a text column renders `layouts/_partials/content-page.html`: `single.html`, `list.html`,
  `hub.html` and `showcase.html` pass the page; `event.html` and `about/contributors.html` pass
  `dict "page" "body" "class"` with their own body. Change the common page structure there.
- `layouts/_partials/page-type.html` holds each type's policy (width, sidebar); `has-toc.html`, `sidebar.html`,
  `section-nav.html` and `next-steps.html` apply it.
- `assets/css/base.css` owns form layout and field defaults; a component's variations live in its own file
  (`components.css` for shared ones, else its family's sheet, docs/design.md).
