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

## Site structure

The main menu is grouped by what visitors come for and lists every page of its groups; the footer does not repeat it. The footer follows the menu's groups and names: seven columns (Get Lead-DBS, Features, Docs and help, Atlases and data, Community, About, Institute; four per row below 1280 px) with what a visitor looks for at the end of a page and what the menu lacks (source code, bug reports, "Release history" → `/download/#releases`, the news feed, search, the lab's sites), then the legal line with the research-use statement and the render credits (`layouts/_partials/footer.html`).

| Menu | Page | Holds |
|---|---|---|
| Features | `/helpsupport/knowledge-base/lead-dbs-methods/` ("Features": what Lead-DBS does in four numbered chapters, listed 01–04 beside the intro (`{{< jumps >}}`): "Single patients" `#single-patients`, "Groups of patients" `#groups-of-patients`, "In the operating theatre" `#operating-theatre` and "Tools and modules" `#tools`. Each chapter (`{{% chapter %}}`) has a short heading and a one-line lede, in the first two with a low render beside them, then its capabilities as cards (`{{< capabilities >}}`), each with its name, a picture, its manual chapter and papers: renders three to a row, figures from papers two, each opening at full size; a chapter's last figure, and Lead-OR, is a wide row; the tools a table (Lead Group, Lead Connectome, OSS-DBS, Lead Tutor). The renders are credited once, at the end; figures from papers carry their licence under the text; full width, no sidebar) | The page's chapters: the anchors Single patients and Groups of patients, Lead-OR (the page `/about/lead-or/`, the one tool of chapter 03 "In the operating theatre"; the anchor `#operating-theatre` stays on Features) and the anchor Tools and modules; the anchors are listed in the header's panel only, not in the sidebar of the articles (`params.panelOnly`). Under the caption "In depth", the articles: DBS network mapping, subcortical electrophysiology mapping, AC/PC to MNI conversion (with the former article "DBS targets in MNI space" as its background section); then, after a line, Made with Lead-DBS (`/gallery/`). Each article has the same sections: what it does (with a figure), how to use it, what to cite; longer material is folded. The overview is the word "Features" itself, as every group's hub is its word; the tools are its chapter 04 (`#tools`), and the former "Lead tools" page `/about/tools/` forwards there |
| Docs and help | `/helpsupport/` | First steps (step 1 links to the install steps on the download page), the manual (another site; on a phone a first-level word of the menu instead), Practice dataset (Lead Tutor) (the dataset's reference page; the exercise itself is step 2 of First steps), walkthrough videos (current recordings first, then "Older recordings"), get help (`/helpsupport/#get-help`, the one list of where to ask; the contact page sits under it) |
| Atlases and data | `/helpsupport/knowledge-base/atlasesresources/` | Three catalogues built alike (subcortical atlases with the macaque atlas, DISTAL and FOCUS; cortical parcellations; normative connectomes), then under the caption "By the Lead-DBS team" in the menu the two atlases by the Lead-DBS team, DISTAL and FOCUS (both pages built alike: summary box, What it is, How to get it `#download`, What to cite, How it was built, folded); "Choosing and using an atlas or connectome" (`#choosing` on the hub); under the caption "Background", the article "About the MNI spaces" (`/about-the-mni-spaces/`) |
| Community | `/community/` | Events (with a page for each upcoming event that needs one, both with a summary box (when, where, hosted by, registration): the developer meeting `/events/developer-meeting/` (who it is for, how to register, the flyer), the Hands-on Lead-DBS Workshop 2027 `/events/hands-on-workshop-2027/` (its "Get notified" button leads straight to the newsletter form, `/subscribe-to-our-newsletter/#subscribe`), the one place where the workshop's details grow; its news post only points there; and the past workshops), user Slack, Contribute (`/develop/`: code, atlases and datasets, bug reports; `/about/data-code-inclusion-philosophy/` forwards to its section `#add-your-atlas-or-dataset`), newsletter (with links to recent issues) |
| News | `/news/` | Releases and announcements (each post at `/<slug>/`); posts more than three calendar years older than the newest are listed under "Archive"; the RSS feed `/news/index.xml` |
| About | `/about/` (a paragraph, cards for its pages, then deep brain stimulation, and history with recognition and funding; the history links the 2017 essay "Commercial vs. academic software", which keeps its address `/commercial-vs-academic-software/`, is kept for the record and is left out of the site search) | Cite Lead-DBS, publications (every paper of `data/papers.yaml`, the library of studies that used Lead-DBS, cover art, what other researchers write), contributors (who coordinates Lead-DBS today and who built it), dependencies (the software Lead-DBS builds on, OSS-DBS among them, with what to cite) |
| Download | `/download/` (the header's button; its sidebar is its contents list) | The current release, requirements and the install steps (`#install`, the only place they are written), standalone builds, licence (one line; the full terms with the research-use statement `#research-use` folded), release history (folded; versions before 3.0 folded again inside) |

The footer's legal line lists Contact, Imprint and Privacy Policy (`[menus.footer]`); the two legal pages end with
"Next" cards to each other, Contact and About like every other page.

**The menu is the site's one hierarchy.** Addresses stay those of the old site, so the folders in
`content/` follow the old addresses, not the menu (the atlases live under
`content/helpsupport/knowledge-base/atlasesresources/`). The header's marked group, the breadcrumb and the
sidebar's list of pages are therefore all drawn from the menu, not from the folders
(`layouts/_partials/nav-place.html`), so they always agree: a page belongs to the menu entry that is the page
itself, or else its nearest folder that is in the menu. Where that is not the right place, the page (or its
folder's `_index.md`) names it in its front matter, e.g. `menuParent: "/events"` on the past workshops. The breadcrumb then reads Home / Community / Events /
Past workshops. A menu entry that leads to another site (the manual) gets a small
arrow wherever menus are drawn.

**One name per page.** A page's menu label, its `linkTitle` (breadcrumb, footer, sidebar, search), its
title (the h1) and its browser title are the same words ("Contributors", "DISTAL atlas"). When you rename a
page, change all of them; the address stays.

**Hub pages** are built alike: a paragraph, then a card with one line for each page of the group, then at
most two short sections. `{{< childpages menu="true" >}}` draws the cards from the menu, in menu order; a
card's line is the page's `description` (also the text search engines show; keep it to 155 characters),
or for a menu entry that is not a page (the manual) the entry's `params.description` in `hugo.toml`. A menu
entry that points to the hub itself or a section of it (Get help) gets no card. The cards are text, a title
over its line, on all four hubs (Docs and help, Atlases and data, Community, About), two to a row beside
the sidebar. A menu entry with `params.divider` gets a line above it in the
header's panel; when the value is a text, that text is the caption over the entries from there on ("In
depth" on Features, "By the Lead-DBS team" over DISTAL and FOCUS, "Background" over the MNI spaces).

**Background articles** (long, lasting texts that began as news posts) live in the folder of the group they
belong to and keep their old address with `url:` in the front matter (`/about-the-mni-spaces/`, and the 2017
essay `/commercial-vs-academic-software/` under About); `showDate: true` prints when they were written under
the title, and `archived: true` adds "kept for the record" to that line for a text that is no longer kept up to
date (the essay, which also has `search: false`). They are not in the news list or feed.

**The sidebar** has one model: the group's pages (the open entry shows the pages under it, and pages whose
`menuParent` is the group's own page follow the entries); the current release only on the groups' hub
pages; then two to four pages related to this one, from the page's front matter:

```yaml
related:
  - "/about/citing_leaddbs/"                                   # labelled with the page's linkTitle
  - {name: "Add your atlas", url: "/develop/#add-your-atlas-or-dataset"}
  - {name: "Connectomics in the manual", url: "https://netstim.gitbook.io/leaddbs/connectomics/connectomic-analyses"}
```

A page with its own `url:` is named by its folder; the build stops on a path that is not a page or is the
page itself. Pick pages of other groups where you can (the group's own pages are listed above). Then on a
long page its table of contents, on a short page the next event, and on News the newsletter and the link to
the news feed.

**Every page ends with "Next"**: one to three cards, each a page's name and a few words, drawn by
`layouts/_partials/next-steps.html` from the page's front matter (the same on every layout):

```yaml
next:
  - {page: "/helpsupport/first-steps/", text: "Your first electrode localization"}  # named by its linkTitle
  - {page: "/develop/#add-your-atlas-or-dataset", name: "Add your atlas or dataset", text: "Missing an atlas?"}
  - {url: "https://netstim.gitbook.io/leaddbs", name: "Manual", text: "Each step of a full analysis"}
```

Point to the related page, the next tutorial step or the section's hub; write no "Next" section in the text.
The build stops on a path that is not a page, on an entry without `text`, and on more than three entries. News
posts get their newer and older post and "All news" as their cards by themselves.

## Editing

| What | Where |
|---|---|
| A page | `content/<url path>/index.md` (or `_index.md` if the page has sub-pages) |
| Images of a page | Same folder as its `index.md`: `![What the picture shows](figure.png)` (see [Pictures in pages](#pictures-in-pages)) |
| A news post | `content/news/<slug>/index.md`; appears at `/<slug>/` (see [Add a news post](#add-a-news-post)) |
| **A new release** | `data/release.yaml` and `data/releases.yaml`, plus a news post (see [Cut a release](#cut-a-release)) |
| A paper about Lead-DBS, a method or a tool | `data/papers.yaml` (see [Building blocks](#building-blocks): `paper`, `papers`) |
| Requirements and install steps (download page; First steps links there) | `data/release.yaml` (MATLAB, toolboxes, SPM12, memory) and `data/install.yaml` (the steps) |
| An atlas or parcellation | `atlases.yaml` next to the atlas page's `index.md` (see [Atlas catalogues](#atlas-catalogues)) |
| Home page texts, quotes, help links, history, funders, citation; the hero's `proof` (a list of short parts) and `manual` (`{label, link, url}`, shown as a fact) | `content/_index.md` (front matter only; the layout is `layouts/home.html`) |
| **Events** (developer meetings, workshops) | `data/events.yaml` (see [Events](#events)) |
| Home page pictures | `assets/images/renders/` (see [Pictures on the home page](#pictures-on-the-home-page)) |
| Gallery ("Made with Lead-DBS", `/gallery/`) | Figures from papers: `data/gallery.yaml` + image files in `static/gallery/`. Lab renders: `content/gallery/_index.md` (see [Gallery](#the-gallery-of-published-figures)) |
| The footer's "Institute" column | `data/links.yaml` |
| A page's related links (sidebar) | its front matter `related:` (see [Site structure](#site-structure)) |
| Main menu, legal links, the GitHub link in the header | `hugo.toml` → `[menus]` (the entry named "Download" is drawn as the header's button) and `[params] github`; see [Site structure](#site-structure) |
| Download / contact / developer-meeting form fields | `data/forms.yaml` |
| Colours, fonts, page styles | `assets/css/site.css` (tokens, buttons, grid: `assets/css/base.css`) |
| Templates | `layouts/` |

### Pictures in pages

Put the file next to the page's `index.md` and write `![alt](file.png)`; add a title in quotes to put
a caption under it: `![alt](file.png "Caption")`. The alt text says what the picture shows (or, for a
picture that is a link, where it leads); leave it empty only for a picture that is pure decoration.

You can put the original file there as it is, at any size: the site shows resized WebP copies
(480 to 1600 px wide, the browser picks one) and links a picture that is wider than the text to the
original, so readers can open it large. Pictures load only when they come near the screen, and every
one carries its width and height, so the text never jumps. SVGs and small GIFs are shown as they are.
A figure with large labels that should not fill the text column gets `{.fig-medium}` on the line right
after it (at most 600px wide). Every caption has one style (small, muted): write it as the title, also for
numbered figures (`![alt](fig.png "Fig. 2: What it shows.")`), and give a clip its `caption=`.

**An animation** (instead of an animated GIF, which is many times larger): convert it to a muted MP4 with a
poster frame, put both next to the page, and use the `clip` shortcode. The clip loads only when it comes
near the screen and plays while it is in view; visitors who ask for reduced motion get the poster and the
player's controls.

```bash
ffmpeg -i anim.gif -an -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p" -c:v libx264 -preset veryslow -crf 26 -movflags +faststart anim.mp4
ffmpeg -i anim.mp4 -frames:v 1 -q:v 3 anim-poster.jpg
```

```markdown
{{< clip src="anim.mp4" poster="anim-poster.jpg" alt="What it shows" caption="Optional caption" >}}
```

(A GIF wider than about 1000 px: use `-vf "scale=960:-2:flags=lanczos,format=yuv420p"`.)

Videos: `{{< youtube id="VIDEO_ID" title="What the video shows" >}}` (or `{{< vimeo … >}}`). Give a
title: it is printed on the player and names it for screen readers; say what the video shows and, for an
old recording, which version of Lead-DBS it shows. Nothing is loaded from YouTube or Vimeo until the
visitor presses play. The build stops if an id is not a plain video id.

### Long pages: the table of contents

A page with five or more headings (`##` and `###`) gets a table of contents by itself: at the top of
the text on a phone and a tablet, and in the sidebar on a desktop, where it stays in view while the
text scrolls and marks the section being read. `toc: true` in the front matter forces it, `toc: false`
hides it; the threshold is `tocMinHeadings` in `hugo.toml`. It lists `##` and `###`, so give long
pages real headings in order: the page's title is its only `h1` (a `#` heading in the Markdown is
drawn as `h2`).
`sidebar: false` in the front matter drops the sidebar: the page uses the full width (running text keeps its
line length), as on Features.

### Writing for the site

- **Short and scannable**: a sentence or two on what the page is for, then `##` headings and lists. Put a
  long list that only some readers need (old fees, early papers) in a fold:
  `<details class="more"><summary>What is inside</summary>` … `</details>` (blank lines around the
  Markdown inside). Every fold is as wide as the text column, and folds that follow each other share one line.
- **Steps of a how-to** (First steps): mark each step's heading `{.step}` (`## Install Lead-DBS {#install .step}`);
  the site numbers them 01, 02 … in the style of the chapter numbers on Features.
- **What to cite**: the paper in a `copybox` with "Copy the citation", written with `{{< paper id "full" >}}`
  where the paper is in `data/papers.yaml` (atlas pages, method articles, Lead-OR, Lead Tutor, Cite Lead-DBS).
- **"Lead-DBS" never breaks at its hyphen**: the templates wrap it in a no-wrap span
  (`layouts/_partials/nobreak-html.html`; headings, links, tables, menus, cards, news and atlas entries).
  Write the ordinary hyphen.
- **Old material says it is old**: a news post older than three years shows an archive note with the
  current version above its text (`layouts/news/single.html`); give older recordings and change-logs a
  date in their text.

### Pictures on the home page

From the top, the home page shows: the hero clip (one directional electrode in the subthalamic nucleus),
the electrode insertion beside "Electrode localization from MRI and CT" (the nine-patient cohort from the
front), three cards (pathway activation, fibre filtering, the cohort from above), a slim atlases band (its
picture, a line of text and the number of subcortical atlases, cortical parcellations and normative
connectomes, counted at build time from each page's `atlases.yaml`; `features.data` in
`content/_index.md` names the page, text, image, crop and counts), a full-width render
with the quotes, and figures from the gallery. Each picture shows a different scene; keep it that way when swapping one.

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
that gives a number of patients must match its picture. The faint picture behind an inner page's title
depends on the page's menu group (`layouts/_partials/page-head-render.html`): `head-features.jpg` (one lead
with its stimulation volume and activated fibres), `head-docs.jpg` (a lead on the axes of MNI space),
`head-data.jpg` (DISTAL atlas structures, no leads), `head-community.jpg` (the cohort's 18 leads from below),
`head-about.jpg` (a 7T slab from above), plus `lead-closeup.jpg` for News and `cohort-front.jpg` for
Download; each group has its own, so keep them distinct. All are 3200×1440 BrainDeer renders of template-
space data (Lead Tutor, DISTAL, 7T Edlow 2019), black on the left so the title stays readable.

The hero clip comes in six files in `static/media/`, each size as AV1 (taken first, by every browser
that can play it) and a fallback: `hero-lead-stn-av1.mp4` (1600×1000 AV1, 0.45 MB) for windows from
1024 px, with `hero-lead-stn-hevc.mp4` (the same in HEVC, 0.65 MB) for desktop browsers without AV1
(Safari on older Macs); `hero-lead-stn-1280-av1.mp4` (1280×800, 0.31 MB) and `hero-lead-stn-1280.mp4`
(H.264, 0.49 MB) for the other windows from 640 px; `hero-lead-stn-phone-av1.mp4` (0.23 MB) and
`hero-lead-stn-phone.mp4` (H.264, 0.49 MB), a 640×640 square crop around the render for
phones). It shows one Boston Scientific Vercise Directed lead with its
segmented contacts in the subthalamic nucleus, the red nucleus behind it, over the 7T slice. The camera sways
slowly around the lead, sinusoidally, ±18° about the best view (32 s per sway, 24 fps, at most 3.5°/s), so the
loop has no jump. It is muted and loops. Its file is fetched only after the page has loaded; on phones,
for visitors who ask for reduced motion or to save data, and on slow connections the poster shows with a
play button and the clip loads only when it is pressed (`assets/js/main.js`). It plays only while the hero
is on screen, and a button pauses it; the poster (`assets/images/renders/hero-lead-stn-poster.jpg`, the clip's first
frame) shows instead. The render sits on the right of a black 16:10 canvas so the words can stand on the black
left half on a desktop; the canvas is true black (#000) on its left side and along every edge, so no grey
border shows where the clip meets the page. On phones the hero stays black: the square clip fills a box and
the title starts over its dark lower third (`.home-hero__media` in `site.css`).

It was rendered with BrainDeer as 385 frames of half a sway (1600×1000, 2×2 supersampled), each composed on
the canvas, and is played forward then backward. The loop is frames 192…384, 383…1, 0…191: 768 frames,
32.0 s at 24 fps, starting on the centre view; the turning points are the sinusoid's own still ends, so no
frame plays twice and the wrap is one ordinary step. On some camera poses VTK drops the back layer of the
translucent nuclei, which shows as flicker in the clip: check a new render for it, and nudge the camera of an
affected frame by a few thousandths of a degree. The encode commands, from the folder of numbered loop
frames, are below. Keep `accurate_rnd` in the smaller scales: without it the black comes out as (0, 2, 0)
instead of #000.

```bash
AV1="-c:v libsvtav1 -preset 3 -crf 36 -g 384 -svtav1-params tune=0:enable-overlays=1:scd=0 -pix_fmt yuv420p -movflags +faststart"
SCALE=flags=lanczos+accurate_rnd+full_chroma_int
ffmpeg -framerate 24 -i loop/%04d.png -an $AV1 static/media/hero-lead-stn-av1.mp4
ffmpeg -framerate 24 -i loop/%04d.png -an -vf scale=1280:800:$SCALE $AV1 static/media/hero-lead-stn-1280-av1.mp4
ffmpeg -framerate 24 -i loop/%04d.png -an -vf crop=1000:1000:520:0,scale=640:640:$SCALE $AV1 static/media/hero-lead-stn-phone-av1.mp4
ffmpeg -framerate 24 -i loop/%04d.png -an -c:v libx265 -preset slow -crf 26 -tag:v hvc1 -x265-params keyint=384 \
  -pix_fmt yuv420p -movflags +faststart static/media/hero-lead-stn-hevc.mp4
X264="aq-mode=3:aq-strength=0.9:deblock=-1,-1"
ffmpeg -framerate 24 -i loop/%04d.png -an -vf scale=1280:800:$SCALE \
  -c:v libx264 -preset veryslow -tune film -crf 29 -maxrate 360k -bufsize 720k -x264-params "$X264:bframes=8:ref=8" -g 384 -pix_fmt yuv420p -movflags +faststart static/media/hero-lead-stn-1280.mp4
ffmpeg -framerate 24 -i loop/%04d.png -an -vf crop=1000:1000:520:0,scale=640:640:$SCALE \
  -c:v libx264 -preset veryslow -tune film -crf 26 -maxrate 260k -bufsize 520k -x264-params "$X264" -g 96 -pix_fmt yuv420p -movflags +faststart static/media/hero-lead-stn-phone.mp4
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

The frames load only after the visitor scrolls and the section is within a quarter screen; a desktop loads
every second frame and blends between them, a phone loads every third frame of the small set, and a
visitor who asks to save data keeps the still. Without the frame folders the section shows a still
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
(menu: Community › Events), which lists upcoming events soonest first and past ones latest first. An event that is
over moves to "Past events" by itself; entries can stay in the file.

An event with more to say than its card (a flyer, the facts known so far) gets a page of its own in
`content/events/`, such as `/events/developer-meeting/` and `/events/hands-on-workshop-2027/`; its entry links
it under `links`, and other pages link the page rather than a news post about the event.

**To add an event**, copy an entry and change it:

```yaml
  - title: "Lead-DBS Developer Meeting"
    start: "2027-06-16T15:00"      # in the event's own time zone
    end: "2027-06-16T16:30"        # optional; without it the event counts as over at midnight
    timezone: "Europe/Berlin"
    also_in: "America/New_York"    # optional second zone, printed in brackets
    where: "Online (Zoom)"
    online: true
    text: "One or two sentences."
    register_url: "/events/developer-meeting/"
```

- The time zone is printed from `timezone` and the date: this entry reads "15:00 CEST (09:00 EDT)",
  a winter one "15:00 CET (09:00 EST)"; without `also_in` just "15:00 CEST". Visitors elsewhere also see the
  start in their own time. (`tz_label` replaces the printed zone; it is rarely needed.)
- **No meeting links on the site.** An online meeting gets `register_url`: the page where people leave their
  e-mail address and are sent the link. For the developer meeting that is its Zoom registration page
  (`…zoom.us/meeting/register/…`); `/events/developer-meeting/` (`content/events/developer-meeting/index.md`)
  links it and offers the meeting's flyer for download. While `register_url` is empty, the event says that
  registration opens soon and that the link is shared in the user Slack; an event on site says that details
  and registration will follow. Never put the meeting's own join link in the file.
- The past workshops of 2016 to 2020 are one page, `/helpsupport/workshops/` ("Past workshops"), with a section
  per workshop, newest first: `#brisbane-2020`, `#berlin-2019`, `#deep-learning-2019`, `#hamburg-2019`,
  `#shanghai-2018`, `#berlin-2016`. Their old pages are redirect stubs that lead to these sections; keep the
  anchors.

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
image_alt: "What the picture shows"   # its alt text, for the top of the post
image_in_post: false  # optional: do not show the teaser at the top of the post
description: "One sentence on what the post says (the news list and search engines show it)."
---

Text in Markdown …
```

The news list shows each post's date, title and its front matter `description` (write one, at most 155
characters: it is also the search snippet). The teaser is the post's share picture and is shown at the top of
the post unless the text shows the same file already.

A post appears on its `date`: one dated in the future is left out of the build (Hugo prints no warning)
until the nightly build of that day. `hugo server -F` shows it now. Pictures in the post: see
[Pictures in pages](#pictures-in-pages).

### Cut a release

1. `data/release.yaml`: `version`, `date`, `summary` (one or two sentences for the home page), `notes`
   (the post about the release), `changes_url` (the GitHub compare view from the release before),
   and `matlab`, `toolboxes`, `memory`, `standalone` and the rest if they changed (the manual's
   [installation page](https://netstim.gitbook.io/leaddbs/installation) is the reference for the requirements). Every version, date and requirement
   on the site comes from this file: the home page, the sidebar card, the footer, and pages that write
   `{{< release version >}}`, `{{< release date >}}`, `{{< release matlab >}}` or `{{< release standalone >}}`.
2. `data/releases.yaml`: the same version, date and announcement as a new first row of the release history
   (the table at `/download/#releases`); the build stops if its first row is not the version in `release.yaml`.
3. A news post about the release (above), titled "Lead-DBS 3.3 released" (a few words may follow after a
   colon when there is something urgent to say), and its address in `notes`. The post's date is the day it
   was announced; when that differs from the release date, the post's head and the release history show both.
4. The download links on `/download/` if the files' names changed (they point to `/release/download.php` on
   the current server; see [Deployment](#deployment)).
5. Search the content for the old version number (`grep -rn "3\.2\.1" content/`): old news posts keep theirs,
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
{{< gallery >}} linked pictures {{< /gallery >}}  {{% slideshow %}} images {{% /slideshow %}}
{{% logos %}} linked logos {{% /logos %}}      {{% testimonials %}} > quotes {{% /testimonials %}}
{{< form "contact" >}}            {{< newsletter >}}            {{< childpages >}}
{{< release version >}}           {{< release date >}}          {{< release matlab >}}        {{< release standalone >}}
{{< release standalone_date >}}   the release date of the standalone builds' version (from data/releases.yaml)

{{< notice title="For research use only" id="research-use" >}}Text with **Markdown** …{{< /notice >}}

{{< childpages order="date" >}}     newest first (by each page's date); order="title" for A to Z; default: menu order
{{< childpages descriptions="true" >}}   each card with the page's description under its title
{{< childpages order="include" descriptions="true" include="/events, /develop, /contact" >}}   exactly these pages, in this order

{{% copybox label="Copy the paragraph" %}}A text with a button that copies it.{{% /copybox %}}
{{< clip src="anim.mp4" poster="anim-poster.jpg" alt="What it shows" >}}

{{< downloads >}}
- [pCloud](https://www.lead-dbs.org/release/download.php?id=leaddbs_pcloud)
- [OneDrive](https://…)
{{< /downloads >}}

![Alt text](figure.png "A caption under the picture.")
```

- `notice` is a quiet callout for a line that must stand apart: the closed forum, the research-use
  statement. `title` and `id` are optional (`id` lets other pages link to it, e.g. `/about/#research-use`).
- `childpages order="date"` sorts by the page's `date`; `childpages menu="true"` draws a hub's cards from the menu.
- `quote` is a sentence quoted from a paper, typed out with its source (never a picture of the page):
  `{{< quote source="Husch et al. (2018), *NeuroImage: Clinical* 17" doi="10.1016/j.nicl.2017.10.004" >}}The words.{{< /quote >}}`
  (`url` and `label` instead of `doi` for a source without one). Keep the wording exactly as printed.
- `chapters` lists a video's chapters, one `Title: hh:mm:ss` per line, the time on the left.
- **Citations** in lists are plain text with only the DOI linked: `Author, A. (2020). Title. *Journal*, 1, 2–3. [doi:10.1000/xyz](https://doi.org/10.1000/xyz)`.
- **Papers about Lead-DBS, its methods and tools** are written once, in `data/papers.yaml`: `{{< paper ewert2019 >}}`
  links one by its short name ("Ewert 2019", as in the tools table on Features), `{{< paper ewert2019 "full" >}}`
  prints the full reference (Cite, Lead-OR, Lead Tutor, dependencies), and `{{% papers %}}` lists them all by group
  (Publications). A paper added there appears on Publications by itself.
- `install "requirements"` and `install "steps"` print what Lead-DBS needs and how to install it, from
  `data/release.yaml` and `data/install.yaml`, on the download page (First steps links to `/download/#install`).
- `capability` is one thing Lead-DBS does, on the Features page: its name, a picture (a lab render, a gallery
  figure credited from `data/gallery.yaml`, or a picture of another page with `alt` and `caption`), what it does,
  its manual chapters, papers and the page that explains it in depth, then the figure's credit; the shortcode's
  comment lists the parameters. Inside `capabilities` it is a card whose name, picture, text, references and
  credit line up across the row: renders three to a row on a desktop, figures from papers (`fit="contain"`) two,
  two of either below 1200px. On its own it is a wide row, the picture left. Every picture has the same 4:3
  frame: renders fill it, figures from papers sit whole on the light mat and open at full size. Renders carry
  no credit of their own; the page credits them once. Its `id` is the anchor other pages link to
  (`#stimulation`, `#connectivity` …); the page scrolls it below the header and outlines it.
- `chapter` opens a numbered chapter of a long showcase page (Features): `{{% chapter n="1" img="images/renders/…" %}}`
  around the chapter's `##` heading and a one-line lede; from 1024px the render is a low band beside them,
  below that it follows them, and a phone leaves it out. Its number has the style of the numbers of `jumps`
  and of the steps of First steps: a label.
- `copybox` holds a text to copy as a whole (the methods paragraph on `/about/citing_leaddbs/` and every "What to cite"); the button
  copies it as plain text and is hidden where the browser cannot copy.
- `clip` is a short silent animation (see [Pictures in pages](#pictures-in-pages)).
- `downloads` turns a list of links into a grid of download buttons (one column on a phone);
  `variant="secondary"` draws them as underlined words, for downloads that are not the recommended one.
- `download-release` is the block under the download page's title: the current release in one line, one
  large button for the first server listed, and the other servers as underlined words.
- `release-history` is the table of released versions (`data/releases.yaml`); versions before 3.0 are folded under it.
- `childpages section="/path"` lists the pages of another section.
- `jumps` is the numbered contents of a long page (Features):
  `{{< jumps "Single patients|#single-patients; Tools|#tools" >}}`; the build stops on an anchor the page lacks.
  With the page's intro between its tags, the intro and the contents sit side by side on a desktop.
- `gallery` is a grid of small pictures that open large (the journal covers): one `[![alt](small.png)](large.png)`
  per line; each is shown as WebP copies 240 and 480 px wide, whatever the size of the file.
- `button` labels may be long: they wrap on a phone.
- A retired address is kept as `aliases:` in the front matter of the page that replaces it; Hugo writes a
  redirect page there (`layouts/alias.html`, marked `noindex`). When the content now lives in one section of
  another page, keep the old page as a stub with `layout: redirect` and `redirect: "/path/#anchor"`
  (`layouts/redirect.html`; see `/about/deep-brain-stimulation-2/`).

**Videos** get a poster: save a still of the video next to the page as `video-<id>.jpg` (the YouTube or
Vimeo id), and the player shows it before it is started; nothing loads from the video site until then.

#### Atlas catalogues

The subcortical atlases, the cortical parcellations and the normative connectomes are catalogues: the page's own `atlases.yaml`
(next to its `index.md`) holds one entry per atlas, and the page only places them:

```markdown
{{< atlas-index >}}            at the top: a filter box and one link per group
{{% atlas-group "thalamus" %}}  one group: its heading (in the table of contents), then its atlases
```

Every entry is drawn in the same order: a small thumbnail, name and paper, what it covers, "Preinstalled";
then, folded away under "About, get it, cite" so the page stays short, a few lines, "Get it", "Cite" and the
picture on a light mat. The entries are the index: the filter keeps those whose head matches every word
typed (`?atlas=word` in the address fills it in), and a link to an entry's `#id` opens it. The header of `atlases.yaml` lists the fields. To add an atlas,
add an entry with a new `id` to the right group and put its picture next to the page; to add a group, add it
under `groups` and a `{{% atlas-group %}}` line on the page. The site search finds every atlas by itself and
opens the page at its entry. Never change an existing `id`: it is the entry's address (`#id`).

**An atlas page of its own** (DISTAL, FOCUS) opens with its summary box (Lead-OR and Lead Tutor have the same box after
a one-line intro); a date in it is a `<time datetime="2018-02-05">` element and a version a `<span class="num">`, both
set in medium weight as on the event cards;
background and change-logs follow, longer parts folded:

```markdown
{{< summary >}}
What
: The structures it holds

Space
: MNI ICBM 2009b NLIN Asym

Get it
: Comes with Lead-DBS

Version
: <span class="num">1.1</span>, released <time datetime="2018-02-05">5 February 2018</time>
{{< /summary >}}
```

Such an atlas is also an entry in the catalogue, with `page:` pointing to its page.

Column widths: `1/2`, `1/3`, `2/3`, `1/4`, `3/4`, `1/5`, `2/5`, `3/5`, `4/5`. Columns stack on a phone.
`slideshow` shows its pictures as a still grid.

## Design

The styles are the site's own, in three files that `layouts/_partials/head.html` bundles into one
fingerprinted stylesheet:

- `assets/css/base.css`: the tokens (spacing `--s-1`…`--s-9`, type sizes `--t-*`, radii `--r-*`, the page
  margin `--gut`, the header height `--nav`), element defaults, the 12-column grid (`.grid`, `.span-*`,
  `.start-*`, from 1024 px), buttons (`.btn--primary`, `.btn--secondary`), links with an arrow (`.link`, the
  `svg.m-arrow` in the templates), cards, form fields, the focus ring, hover and press feedback, and the
  reduced-motion rules.
- `assets/css/site.css`: the palette and fonts (change colours and fonts here only), the header, the home
  page, the documentation pages, the gallery, events, search and the footer.
- `assets/css/content.css`: the content building blocks that come after those: hub cards with a line of
  text, the copy box, clips, the newer/older links under news posts, and the Features chapters and cards.

The script is `assets/js/main.js` (with `search.js` for the search and `insertion.js` for the electrode
insertion on the home page). It opens the header's menu sheet and panels, plays the hero's entrance and clip,
and checks events against the visitor's clock.

- **Sections take the height of their content.** The hero is the window's height less about 90 px (so the
  row of figures under it shows on the first screen; at least 600, at most 1040 px) and grows with its
  content; the other sections share one vertical rhythm (`--rhythm`).
- **The header over black**: while the home page's hero or an inner page's black head lies under it, the
  header is black (clear over the hero on a desktop) with white words; past it, the light bar returns
  (`main.js` sets `.is-dark` on `.nav` for any element marked `data-nav-dark`).
- **Three kinds of card**: the outlined link card (`.card`: help, atlases, child pages), the filled panel
  (`.panel`: events, quotes, the citation) and the media card (a picture with its words under it). One arrow
  everywhere: the chevron that grows a stem on hover.
- **The header switches to its menu sheet below 1200 px**, so the words, search, GitHub and the button never
  collide; between 1200 and 1279 the button says "Download". A word's panel opens after the pointer rests on
  it for 150 ms, at once on keyboard focus.
- **The hero's entrance**: the title's words rise line by line, then the lead, the buttons and the facts fade
  up while the clip settles. The page head hides the words until `main.js` starts it, and shows them anyway
  after 700 ms; under reduced motion nothing moves.

- Palette ("Blend", tokens at the top of `site.css`): white ground `#ffffff`, a grey surface `#f5f6f7`,
  warm dark grey ink `#2f3437`, muted `#6f7479`; one action colour, deep blue `#2b5c8a` (buttons, links,
  focus); coral `#e0645a` as the one signal; periwinkle `#c6cdf7` and blush `#f4c6cf` as pale tints. The
  colours come from Wes Anderson films (The Darjeeling Limited, The Grand Budapest Hotel), the family of
  the logo's wedges. The renders sit on black, and so does every inner page's title.
- Font: Inter, one variable file per script (`@fontsource-variable/inter` 5.2.5, licence in
  `static/fonts/OFL-inter.txt`) with the weight and optical-size axes, self-hosted in `static/fonts/`, with a
  fallback `@font-face` sized to its metrics so nothing moves when it arrives. One face for everything:
  400 text, 500 the menu, labels and values, 600 buttons and headings, large headings tracked tighter.
- Type scale at 1440 (tokens in `base.css`): 80 the hero, 48 home sections and page titles, 32 a page's
  sections, the Features chapters and the smaller home sections ("Upcoming events", "Latest news"), 23
  subsections and Features cards, 20 cards and the lead, 18 documentation text, 16 text elsewhere, 14 small
  print. Labels ("Release", "Input", "Manual", table heads, chapter numbers) are 13 px, medium weight, muted
  and in sentence case, one rule in `site.css` (`--font-label`, `--label-*`). Every date and time is a
  `<time>` element and every version or count a `.num` span, with figures of equal width; where the value
  is a line or cell of its own it is also medium weight.
- Text pages: 18 px on a desktop (17 on a phone), lines of about 70 characters.
- Motion: the hero's entrance and clip, and the electrode insertion in the localization section. Nothing else
  moves by itself; hover and press feedback are short CSS transitions.
- Nothing loads from other servers (no web fonts, analytics or scripts from elsewhere); YouTube and Vimeo
  players load only when a visitor starts a video.
- The research-use statement is a short line, not a feature: the hero's "Intended use", the
  footer's legal line, and one small-print sentence on /about/ and the download page.
- Icons: Lucide line icons (`static/images/icons/ui-*.svg`, ISC licence, listed in `icons-credits.json`), drawn
  in the accent colour; the header's search and GitHub icons are inline in `layouts/_partials/header.html`.
- After a change to a layout, check the home page at 1366×768, 1440×900 and 390×844, and that no page scrolls
  sideways on a phone.

## Search and the 404 page

The header's search button (or the `/` key) opens a search over every page. Hugo writes the index,
`/search-index.json`, from `layouts/home.searchindex.json` (title, the page above it, keywords, headings,
description and the start of the text of each page); `assets/js/search.js` loads it on first use. A page
whose title holds the searched words comes first, then pages with them in their `keywords`, headings,
description and text; news posts come after a page that scores the same. Add `keywords: ["install", …]` to
a page's front matter for words that visitors search for but the title does not contain. Each atlas of an
atlas catalogue is a result of its own that opens at its entry; so is each section a page lists in its
front matter `searchEntries` (`{title, id, keywords, description}`; the build stops when the page has no
anchor `id`): the tools on Features, "Lead-DBS 4.0" on the download page (`/download/#lead-dbs-4`, the one
place that says what may be said about it), troubleshooting on First steps. Below the results (or in their place when
there are none) a last line offers the manual, for questions about how to do something in Lead-DBS. The manual has a
result of its own (its menu entry's `params.keywords`), and each result names the page above it as the breadcrumb
does. Left out of the index: pages with `search: false` and the closed forum's page; the footer's pages (contact,
imprint, privacy) are found by their title only. `/search/` shows the same
box on a page (`/search/?q=atlas`); until a query is typed (and without script, with a line that the search
needs it) it shows the 404 page's ten cards to start from (`layouts/_partials/search-doors.html`), and it is
marked `noindex`. `layouts/404.html` is the page for every address the site does not have; for the old
forum's addresses it says that the forum has closed.

## Metadata

`layouts/_partials/head.html` writes the title, description, canonical address, Open Graph tags and the
news feed link. The share picture is the page's `share:` (a file next to the page, or a path under `assets/`
such as `images/renders/cohort-top.jpg`), else a news post's teaser (`image:`), else `assets/images/share.jpg`.
A page without a `description` gets the start of its text, cut at 155 characters. The news list's later pages
(`/news/page/2/`), the closed forum's page and the 2017 essay are `noindex` and not in the sitemap (a page with
`search: false` also needs `sitemap: {disable: true}`; `check-site.py` stops on a noindex page in the sitemap); `static/favicon.ico` is
there for browsers that ask for it. `head-jsonld.html` adds structured data:
the software (`SoftwareApplication`) on the home and download pages, the upcoming events (`Event`) on
`/events/` and each on its own page (the page its entry in `data/events.yaml` links to; only the facts of that
entry), `NewsArticle` on every post, and on every inner page a `BreadcrumbList` from the same trail as the
visible breadcrumb (`layouts/_partials/crumbs.html`). A later page of the news list is its own canonical address. A page's last-modified date (sitemap, `dateModified`) is its
front matter `lastmod`, else the date of the last commit that changed its file (`enableGitInfo`; the Pages
workflow checks out the full history), never the build day. A page has one name: its `title` is its h1, its browser
title and, for a page in the menu, the menu entry's `name` and its `linkTitle` (breadcrumb, sidebar, footer). The browser
title is "Page – Lead-DBS" (the home page: its headline – Lead-DBS); a title that names Lead-DBS stands alone
("Cite Lead-DBS", "Lead-DBS 3.2 released").

## Old URLs

Every page keeps its WordPress URL (e.g. `/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`), so
links in papers and slides keep working; retired ones redirect through `aliases:` (see Building blocks).
Pages that were merged into others redirect there: the Knowledge Base hub (to `/helpsupport/`), "Other
Videos" (to the walkthrough videos), "Screenshots" (to the gallery), "Download FOCUS" (to the FOCUS atlas),
the IXI database (to the AC/PC to MNI conversion), the second list of past workshops, the six workshop pages
and two workshop posts (to their sections of "Past workshops"), the four cover-art posts (to
`/about/publications/#cover-art`), the Max Rubner Prize post (to `/about/#recognition-and-funding`), two
notices of 2014 about papers (to `/about/publications/`), three notices of 2014 to 2018 (to `/about/#history`),
"Introducing Lead Connectome" (to its page), the post on subcortical electrophysiology mapping (to the worked
example on the method's page), old posts whose content now lives elsewhere (the OHBM poster and hackathon of 2014, the
first meetup of 2015 and a call for letters of support: to `/about/#history`; "Lead-DBS is on Twitter and
Facebook": to `/community/#follow-lead-dbs`; two lists of new DBS papers: to `/about/publications/#applications`), the macaque atlases (to
their entry among the subcortical atlases) and "What is deep brain stimulation?" (to its section on `/about/`).
An old page whose content now sits in a section of another is a stub with `layout: redirect`; an alias of such
a stub goes straight to the final address. The old forum's index, topics, replies and topic
tags all lead to `/helpsupport/forum/`, which says that the forum is closed and where to ask instead; the
old "portfolio" pages of software lead to the dependencies page (3D Slicer to Lead-OR). Every address in the
old site's sitemap (`/wp-sitemap.xml`) resolves, except the forum's user profiles (`/author/…`). The old feeds `/feed/` and `/news/feed/` lead to `/news/`, which names the
RSS feed `/news/index.xml`; on a server that can redirect, send them straight to the feed.
Files outside WordPress (`/release/download.php`, `/docs/…`) are on the current server; see Deployment.

## Deployment

The preview is built by `.github/workflows/pages.yml` for GitHub Pages under `/lead-dbs-website/`, with
`HUGO_PARAMS_PREVIEW=true` (banner, `noindex`, canonical addresses pointing at www.lead-dbs.org). The same
workflow also builds the site for `https://www.lead-dbs.org/`, and runs `.github/scripts/check-site.py` on both
builds; the run fails on a broken internal link, image or #anchor, a redirect that leads nowhere or to another
redirect, a canonical, og:image or sitemap address that is not absolute, or front matter shown as page text.
Run it locally the same way:

```bash
hugo --gc -d /tmp/site && python3 .github/scripts/check-site.py /tmp/site https://www.lead-dbs.org/
``` A
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
