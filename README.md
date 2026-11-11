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

No npm, bundler or CDN: Hugo is the only tool. The first build of a fresh clone makes the resized
images (a few hundred files in `resources/_gen/`, which is not committed); that takes about half a
minute, later builds take a second.

The build prints a warning for every Markdown image without alt text (`image-alt`): those are the
pictures a screen-reader user cannot see. Write the alt text and the warning goes.

## Editing

| What | Where |
|---|---|
| A page | `content/<url path>/index.md` (or `_index.md` if the page has sub-pages) |
| Images of a page | Same folder as its `index.md`: `![What the picture shows](figure.png)` (see [Pictures in pages](#pictures-in-pages)) |
| A news post | `content/news/<slug>/index.md`; appears at `/<slug>/` (see [Add a news post](#add-a-news-post)) |
| **A new release** | `data/release.yaml`, plus a news post (see [Cut a release](#cut-a-release)) |
| Home page texts, quotes, help links, history, funders, citation, "From the lab" | `content/_index.md` (front matter only; the layout is `layouts/home.html`) |
| **Events** (developer meetings, workshops) | `data/events.yaml` (see [Events](#events)) |
| Home page pictures | `assets/images/renders/` (see [Pictures on the home page](#pictures-on-the-home-page)) |
| Gallery ("Made with Lead-DBS", `/gallery/`) | Figures from papers: `data/gallery.yaml` + image files in `static/gallery/`. Lab renders: `content/gallery/_index.md` (see [Gallery](#the-gallery-of-published-figures)) |
| Sidebar quick links, footer link columns (Tools, Help, Lab) | `data/links.yaml` |
| Main menu, legal links, the GitHub link in the header | `hugo.toml` → `[menus]` (the entry named "Download" is drawn as the header's button) and `[params] github` |
| Download / contact form fields | `data/forms.yaml` |
| Colours, fonts, page styles | `assets/css/site.css` (tokens, buttons, grid: `assets/css/base.css`) |
| Templates | `layouts/` |

### Pictures in pages

Put the file next to the page's `index.md` and write `![alt](file.png)`; add a title in quotes to put
a caption under it: `![alt](file.png "Caption")`. The alt text says what the picture shows (or, for a
picture that is a link, where it leads); leave it empty only for a picture that is pure decoration.

You can put the original file there as it is, at any size: the site shows resized WebP copies
(480 to 1600 px wide, the browser picks one) and links a picture that is wider than the text to the
original, so readers can open it large. Pictures load only when they come near the screen, and every
one carries its width and height, so the text never jumps. Animated GIFs and SVGs are shown as they
are: keep GIFs small (a 13 MB GIF is 13 MB for everyone who scrolls past it; a short MP4 is a tenth of that).

Videos: `{{< youtube id="VIDEO_ID" title="What the video shows" >}}` (or `{{< vimeo … >}}`). Give a
title: it names the player for screen readers. Nothing is loaded from YouTube or Vimeo until the
visitor presses play.

### Long pages: the table of contents

A page with five or more headings (`##` and `###`) gets a table of contents by itself: at the top of
the text on a phone and a tablet, and in the sidebar on a desktop, where it stays in view while the
text scrolls and marks the section being read. `toc: true` in the front matter forces it, `toc: false`
hides it; the threshold is `tocMinHeadings` in `hugo.toml`. It lists `##` and `###`, so give long
pages real headings in order: the page's title is its only `h1` (a `#` heading in the Markdown is
drawn as `h2`).

### Pictures on the home page

From the top, the home page shows: the hero clip (one directional electrode in the subthalamic nucleus),
the electrode insertion beside "Electrode localization from MRI and CT" (the nine-patient cohort from the
front), three cards (pathway activation, fibre filtering, the cohort from above), and the workshop flyer
beside the events. Each picture shows a different scene; keep it that way when swapping one.

Every still is a file in `assets/images/renders/`, named in `content/_index.md` (`image:`).
**To swap one**, replace the file with a new one of the same name (any size, JPG or PNG; Hugo makes the
WebP sizes the page needs), or put a new file next to it and change the name in `content/_index.md`.
Then run `hugo server` and look at the home page at 1440 wide and on a phone (390): the pictures are
cropped to fixed shapes (4:3 beside the localization text, 16:10 in the three cards), so check that the
subject is still in the crop.
Keep them the lab's own renders: no stock or generated pictures. Renders of the Lead Tutor data are
illustrations, not findings; the texts say so where an analysis is shown.

The renders are BrainDeer renders of **nine** of the ten Lead Tutor patients (2026-11-10: `cohort-*.jpg`,
the insertion frames; `lead-closeup.jpg` and the hero clip show one lead of one of them); the
pathway-activation and fibre-filtering pictures are older example analyses of all ten. A caption or alt text
that gives a number of patients must match its picture. The same `cohort-black.jpg` is the faint picture
behind every inner page's title; `lead-closeup.jpg` is in the gallery.

The hero clip is `static/media/hero-lead-stn.mp4` (desktop and tablet, 1600×1000, 1.25 MB) and
`hero-lead-stn-phone.mp4` (800×500, 0.42 MB): one Boston Scientific Vercise Directed lead with its
segmented contacts in the subthalamic nucleus, the red nucleus behind it, over the 7T slice. The camera sways
slowly around the lead, sinusoidally, ±18° about the best view (32 s per sway, 24 fps, at most 3.5°/s), so the
loop has no jump. It is muted and loops. It does not start for visitors who ask for reduced motion or to save
data, and a button pauses it; the poster (`assets/images/renders/hero-lead-stn-poster.jpg`, the clip's first
frame) shows instead. The render sits on the right of a black 16:10 canvas so the words can stand on the black
left half on a desktop; the canvas is true black (#000) on its left side and along every edge, so no grey
border shows where the clip meets the page. Below 1024 px the page shows the clip in a box cut to the
subject (`.home-hero__media` in `site.css`: it assumes the subject inside x 41–99 % and y 16–72 % of the canvas,
centred near 70 % across and 44 % down).

It was rendered with BrainDeer as 385 frames of half a sway (1600×1000, 2×2 supersampled), each composed on
the canvas, and is played forward then backward. The loop is frames 192…384, 383…1, 0…191: 768 frames,
32.0 s at 24 fps, starting on the centre view; the turning points are the sinusoid's own still ends, so no
frame plays twice and the wrap is one ordinary step. On some camera poses VTK drops the back layer of the
translucent nuclei, which shows as flicker in the clip: check a new render for it, and nudge the camera of an
affected frame by a few thousandths of a degree. The encode commands, from the folder of numbered loop
frames, are below. Keep `accurate_rnd` in the phone's scale: without it the black comes out as (0, 2, 0)
instead of #000.

```bash
X264="aq-mode=3:aq-strength=0.9:deblock=-1,-1"
ffmpeg -framerate 24 -i loop/%04d.png -an -c:v libx264 -preset veryslow -tune film -crf 25 -maxrate 700k -bufsize 1400k \
  -x264-params "$X264" -g 96 -pix_fmt yuv420p -movflags +faststart static/media/hero-lead-stn.mp4
ffmpeg -framerate 24 -i loop/%04d.png -an -vf scale=800:500:flags=lanczos+accurate_rnd+full_chroma_int \
  -c:v libx264 -preset veryslow -tune film -crf 25 -maxrate 260k -bufsize 520k -x264-params "$X264" -g 96 -pix_fmt yuv420p -movflags +faststart static/media/hero-lead-stn-phone.mp4
```

The poster is the first loop frame saved as JPEG (quality 92). A new clip needs the same framing and size
budget (desktop at most 2.5 MB, phone at most 1 MB); check the hero at 1366×768, 1440×900, 1024×768 and on a
phone.

### The electrode insertion (the home page's one scroll moment)

In "Electrode localization from MRI and CT" the leads move into place while the section scrolls through
the window, and back out when scrolling up (`assets/js/insertion.js`). It is a sequence of WebP frames
drawn on a canvas by scroll position:

- `static/media/insertion/webp/*.webp` (1200×900) and `…/webp-small/*.webp` (720×540, used on narrow screens):
  the frames, in file-name order, first frame = leads outside, last = in place.
- `assets/images/renders/insertion-final.png`: the picture shown until the frames have loaded, under
  reduced motion and without script. It must be the same image as the last frame.
- `data/insertion.yaml`: its alt text and the caption printed under it.

The frames load only when the section comes near. Without the frame folders the section shows a still
render instead. Keep it the only scroll-linked motion on the site.

### The gallery of published figures

`/gallery/` shows figures from open-access papers made with Lead-DBS first, in the order of
`data/gallery.yaml`, then the lab's renders. Each figure is one block in that file, starting with `- file:`:

- **To remove a figure**, delete its whole block and its file in `static/gallery/`. Nothing else
  refers to it.
- **To add one**, put the image in `static/gallery/` and copy a block. Fill every field: `authors`, `title`,
  `journal`, `year`, `figure`, `doi`, `license`, `license_url`, `modification` and `shows`; the build stops
  with a message naming the figure and the field if one is missing. The citation and licence are printed
  under the figure because CC BY requires the attribution; `shows` is one plain sentence on what the figure
  shows (check it against the paper's legend); `modification` says how the image differs from the published
  figure (e.g. "cropped to panel a"), or `none`. A figure made with the sister tool Lead-OR gets `tool: "Lead-OR"`,
  printed as "Made with Lead-OR". Only use figures whose licence allows it (for example CC BY).
- Then open `/gallery/` and check the new figure at 1440 and on a phone.

Figures are shown whole (scaled to fit, never cropped) from resized WebP copies; the link under each
opens the original file. Keep it to at most 10 figures, each understandable without context and
really made with Lead-DBS.

### Events

`data/events.yaml` lists developer meetings and workshops; the file's head explains every field. The next
event shows in four places: as the fifth fact in the home page's hero, in the home page's "Workshop and
developer meeting" block (every upcoming event), in the sidebar of every inner page, and on `/events/`
(menu: Events), which lists upcoming events soonest first and past ones latest first. An event that is
over moves to "Past events" by itself; entries can stay in the file.

**To add an event**, copy an entry and change it:

```yaml
  - title: "Lead-DBS Developer Meeting"
    start: "2027-06-16T15:00"      # in the event's own time zone
    end: "2027-06-16T16:30"        # optional; without it the event counts as over at midnight
    timezone: "Europe/Berlin"
    where: "Online (Zoom)"
    online: true
    text: "One or two sentences."
    register_url: ""
```

- The time zone is printed from `timezone` and the date: this entry reads "15:00 CEST (Berlin time)",
  a winter one "15:00 CET". Visitors elsewhere also see the start in their own time. (`tz_label` replaces
  the printed zone; it is rarely needed.)
- **No meeting links on the site.** An online meeting gets `register_url`: the page where people leave their
  e-mail address and are sent the link. While it is empty, the event says that registration opens soon and that
  the link is shared in the user Slack; an event on site says that details and registration will follow.
  Never put a Zoom link in the file.

**How it stays current.** A static site does not know today's date, so two things work together:

1. The templates leave out events that were over when the site was built, and
   `.github/workflows/pages.yml` rebuilds the site every night (`schedule`, 02:17 UTC) as well as on every push.
   GitHub pauses scheduled workflows in a repository with no activity for 60 days, which would freeze the
   "next event": a push, or "Run workflow" on the Actions tab, starts them again.
2. A few lines in `assets/js/main.js` check again by the visitor's clock: they hide an event that has ended since
   the build and show the next one, and on `/events/` move it to "Past events". Without script, the build's
   choice shows.

To see the site as it will look on another day: `hugo server --clock 2026-11-20T10:00:00+01:00`.

### Add a news post

```bash
mkdir content/news/my-post
```

`content/news/my-post/index.md`:

```markdown
---
title: "Lead-DBS 3.3 released"
date: 2026-12-01
slug: "lead-dbs-3-3-released"   # the address: /lead-dbs-3-3-released/ (without it, made from the title)
image: "teaser.png"   # optional, a file in the same folder
image_whole: true     # optional: show the teaser whole in the news list (a flyer, a poster) instead of cut to a strip
image_in_post: false  # optional: do not repeat the teaser at the top of the post (when the text shows it already)
---

Text in Markdown …
```

A post appears on its `date`: one dated in the future is left out of the build (Hugo prints no warning)
until the nightly build of that day. `hugo server -F` shows it now. Pictures in the post: see
[Pictures in pages](#pictures-in-pages).

### Cut a release

1. `data/release.yaml`: `version`, `date`, `summary` (one or two sentences for the home page), `notes`
   (the post about the release), `changes_url` (the GitHub compare view from the release before),
   and `matlab`, `toolboxes`, `standalone` and the rest if they changed. Every version, date and requirement
   on the site comes from this file: the home page, the sidebar card, the footer, and pages that write
   `{{< release version >}}`, `{{< release date >}}`, `{{< release matlab >}}` or `{{< release standalone >}}`.
2. A news post about the release (above), and its address in `notes`.
3. The download links on `/download/` if the files' names changed (they point to `/release/download.php` on
   the current server; see [Deployment](#deployment)).
4. Search the content for the old version number (`grep -rn "3\.2\.1" content/`): old news posts keep theirs,
   anything current should use the shortcode.

### Building blocks

Besides normal Markdown, pages can use these shortcodes (carried over from the old page builder):

```markdown
{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}

{{% row %}}
{{% col "2/3" %}}
Text on the left …
{{% /col %}}
{{% col "1/3" %}}
![What it shows](figure.png)
{{% /col %}}
{{% /row %}}

{{< youtube id="VIDEO_ID" title="…" >}}      {{< vimeo id="VIDEO_ID" title="…" >}}
{{% gallery %}} images {{% /gallery %}}        {{% slideshow %}} images {{% /slideshow %}}
{{% logos %}} linked logos {{% /logos %}}      {{% testimonials %}} > quotes {{% /testimonials %}}
{{< form "contact" >}}            {{< newsletter >}}            {{< childpages >}}
{{< release version >}}           {{< release date >}}          {{< release matlab >}}        {{< release standalone >}}

{{< notice >}}This workshop took place on 22–23 February 2020 in Brisbane. This page is kept as an archive.{{< /notice >}}
{{< notice title="For research use only" id="research-use" >}}Text with **Markdown** …{{< /notice >}}

{{< childpages order="date" >}}     newest first (by each page's date); order="title" for A to Z; default: menu order
{{< childpages order="date" include="/helpsupport/workshops/brisbane-february-2020" >}}   also list pages from elsewhere

{{< downloads >}}
- [pCloud](https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud)
- [OneDrive](https://…)
{{< /downloads >}}

![Alt text](figure.png "A caption under the picture.")
```

- `notice` is a quiet callout for a line that must stand apart: archive notes on past workshops, the
  research-use statement. `title` and `id` are optional (`id` lets other pages link to it, e.g. `/about/#research-use`).
- `childpages order="date"` sorts by the page's `date`: on the past-workshop pages that date is the day the
  workshop began.
- `downloads` turns a list of links into a grid of download buttons (one column on a phone).
- `button` labels may be long: they wrap on a phone.
- A retired address is kept as `aliases:` in the front matter of the page that replaces it; Hugo writes a
  redirect page there.

Column widths: `1/2`, `1/3`, `2/3`, `1/4`, `3/4`, `1/5`, `2/5`, `3/5`, `4/5`. Columns stack on a phone.
`slideshow` shows its pictures as a still grid.

## Design

The styles are the site's own, in two files that `layouts/_partials/head.html` bundles into one
fingerprinted stylesheet:

- `assets/css/base.css`: the tokens (spacing `--s-1`…`--s-9`, type sizes `--t-*`, radii `--r-*`, the page
  margin `--gut`, the header height `--nav`), element defaults, the 12-column grid (`.grid`, `.span-*`,
  `.start-*`, from 1024 px), buttons (`.btn--primary`, `.btn--secondary`), links with an arrow (`.link`, the
  `svg.m-arrow` in the templates), cards, form fields, the focus ring, hover and press feedback, and the
  reduced-motion rules.
- `assets/css/site.css`: the palette and fonts (change colours and fonts here only), the header, the home
  page, the documentation pages, the gallery, events, search and the footer.

The script is `assets/js/main.js` (with `search.js` for the search and `insertion.js` for the electrode
insertion on the home page). It opens the header's menu sheet and panels, plays the hero's entrance and clip,
and checks events against the visitor's clock.

- **Sections take the height of their content.** The hero is at least the window's height (up to 1100 px)
  and grows with its content; the other sections share one vertical rhythm (`--rhythm`).
- **The header switches to its menu sheet below 1200 px**, so the words, search, GitHub and the button never
  collide; between 1200 and 1279 the button says "Download". A word's panel opens after the pointer rests on
  it for 150 ms, at once on keyboard focus.
- **The hero's entrance**: the title's words rise line by line, then the lead, the buttons and the facts fade
  up while the clip settles. The page head hides the words until `main.js` starts it, and shows them anyway
  after 700 ms; under reduced motion nothing moves.

- Palette: off-white ground `#f7f9fa`, ink `#1f3038`, one accent `#0d7480` (buttons, links, focus);
  the renders sit on black, and so does every inner page's title. Font: Open Sans, self-hosted in `static/fonts/`.
- Text pages: 18 px on a desktop (17 on a phone), lines of about 70 characters.
- Motion: the hero's entrance and clip, and the electrode insertion in the localization section. Nothing else
  moves by itself; hover and press feedback are short CSS transitions.
- Nothing loads from other servers (no web fonts, analytics or scripts from elsewhere); YouTube and Vimeo
  players load only when a visitor starts a video.
- The research-use statement is a short line, not a feature: the hero's "Intended use", the
  footer's legal line, a quiet `notice` on /about/ and the download page.
- Icons: Lucide line icons (`static/images/icons/ui-*.svg`, ISC licence, listed in `icons-credits.json`), drawn
  in the accent colour; the header's search and GitHub icons are inline in `layouts/_partials/header.html`.
- After a change to a layout, check the home page at 1366×768, 1440×900 and 390×844, and that no page scrolls
  sideways on a phone.

## Search and the 404 page

The header's search button (or the `/` key) opens a search over every page. Hugo writes the index,
`/search-index.json`, from `layouts/home.searchindex.json` (title, headings, description and the start of the
text of each page); `assets/js/search.js` loads it on first use. A page with `search: false` in its front
matter is left out. `/search/` shows the same box on a page (`/search/?q=atlas`), for visitors without script
it says what to do instead. `layouts/404.html` is the page for every address the site does not have; for the
old forum's addresses it says that the forum has closed.

## Old URLs

Every page keeps its WordPress URL (e.g. `/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`), so
links in papers and slides keep working; retired ones redirect through `aliases:` (see Building blocks).
Files outside WordPress (`/release/download.php`, `/docs/…`) are on the current server; see Deployment.

## Deployment

The preview is built by `.github/workflows/pages.yml` for GitHub Pages under `/lead-dbs-website/`, with
`HUGO_PARAMS_PREVIEW=true` (banner, `noindex`, canonical addresses pointing at www.lead-dbs.org). A
production build is `hugo --gc --minify` with the default `baseURL` (`https://www.lead-dbs.org/`).

**Before the domain moves:** every download button calls `https://www.lead-dbs.org/release/download.php?id=…`
on the current WordPress server, and several pages link PDFs under `/docs/` and newsletters under `/?na=view&id=…`
there. A static host serves none of these. So either deploy the new site **onto that same server**, leaving
`/release/` and `/docs/` (and their PHP) in place beside it, or give those files a new home first (for example a
`files.lead-dbs.org`) and change the links. Test a download button after the switch.

## Re-importing from WordPress

`tools/import_wordpress.py` converted the WordPress pages to Markdown. It was meant to run once;
running it again with `--force` overwrites any edits made since:

```bash
uv run tools/import_wordpress.py --force
```
