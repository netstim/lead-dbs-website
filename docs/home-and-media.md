# The home page, the gallery and the usage figures

How the renders, the hero clip, the electrode insertion, the gallery and the globe are made and swapped. Start with the [README](../README.md).

## Pictures on the home page

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
depends on the page's menu group (`layouts/_partials/page-head-render.html`): Features `head-features.jpg` (one lead
with its stimulation volume and activated fibres), Docs `lead-closeup.jpg` (one lead, cut to its contacts),
Atlases `head-data.jpg` (DISTAL atlas structures, no leads), Community `head-community.jpg` (the cohort's 18
leads from below), About `fiber-filtering-wide.jpg` (fibre bundles, shown whole) and Download
`cohort-front.jpg`; each group has its own, so keep them distinct. News, Contact, Search, the legal pages and
404 get no render: their head is a lower band of text. All are BrainDeer renders of template-space data
(Lead Tutor, DISTAL, 7T Edlow 2019), 1920 to 3200 px wide and black on the left so the title stays readable;
a crop in the partial is at least 1800 px wide. `head-docs.jpg` and `head-about.jpg` are no longer behind
a title but remain share pictures (Contact, About, Cite).

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
play button and the clip loads only when it is pressed (`assets/js/main/home.js`). It plays only while the hero
is on screen, and a button pauses it; the poster (`assets/images/renders/hero-lead-stn-poster.jpg`, the clip's first
frame) shows instead. The home page's hero is one rounded black panel on the white page, under the light header
(`.home-hero__panel` in `site.css`): the clip fills it and the words stand over its black left half. The
render sits on the right of a black 16:10 canvas for that reason; the canvas is true black (#000) on its left side and along every edge, so no grey
border shows where the clip meets the page. Below 1024 px the clip is a box at the panel's top (square on
phones, with the square encode) and the words follow under it on the same black (`.home-hero__media` in `site.css`).

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

## The electrode insertion (the home page's one scroll moment)

In "Electrode localization from MRI and CT" the leads move into place while the section scrolls through
the window, and back out when scrolling up (`assets/js/insertion.js`). It is a sequence of WebP frames
drawn on a canvas by scroll position:

- `static/media/insertion/webp/*.webp` (1200×900) and `…/webp-small/*.webp` (720×540, used on narrow screens):
  the frames, in file-name order, first frame = leads outside, last = in place.
- `assets/images/renders/insertion-final.png`: the picture shown until the frames have loaded, under
  reduced motion and without script. It must be the same image as the last frame.
- `data/insertion.yaml`: its alt text (the clip has no caption on the home page).

The frames load only after the visitor scrolls and the section is within a quarter screen; a desktop loads
every second frame and blends between them, a phone loads every third frame of the small set, and a
visitor who asks to save data keeps the still. Without the frame folders the section shows a still
render instead. Keep it the only scroll-linked motion on the site.

## The gallery of published figures

`/gallery/` has three sections: the lab's renders (listed by file in its front matter, the first shown large; what each shows, alt text and caption, is in `data/renders.yaml`, which the Features page reads too), the figures
from open-access papers made with Lead-DBS, in the order of `data/gallery.yaml`, and the journal covers. Each figure is one block in that file, starting with `- file:`:

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
opens the original file. Keep it to about a dozen figures, each understandable without context and
really made with Lead-DBS.

## Download figures (the globe on the home page)

The home page's "Downloaded in N countries" section replays the downloads of Lead-DBS since November 2015
on a globe, a month every 0.3 seconds. The figures are a snapshot in `data/downloads.json`. To refresh them,
copy `download.log` (and `download.log.bak`) from the lead-dbs.org server into a folder and run
`python3 tools/downloads.py <log folder> <database.mmdb>` (same packages and database as below).

What is counted: one IP address fetching one item on one day is one download; only Lead-DBS itself
(latest, hotfix, the standalone builds ...), not data packs or atlases; bots are left out (known crawler
and cloud address blocks, and addresses with more than 50 downloads). `tools/downloads.py` says more.
`data/downloads.json` holds downloads by country and month only: no IP address, city or network name.

- **The globe** is drawn by `assets/js/globe.js` with d3-array, d3-geo and topojson-client
  (`assets/js/vendor/`, ISC licence) and the Natural Earth country map `assets/data/world-110m.json`
  (from the world-atlas package), with the download figures (`data/downloads.json`, published by
  `layouts/home.html` as a separate JSON file). The script, then the map and the figures, are fetched when the section comes within
  800 px of the screen (`assets/js/main/home.js` adds the script). Without
  JavaScript the section shows its words only. Its texts are `worldwide:` in `content/_index.md`.

## Usage figures (/usage/)

The page `/usage/` shows how often Lead-DBS is started, by country. The figures are a snapshot in `data/usage.json`; nothing is fetched from the server when the
site is built or viewed. To refresh them:

1. Copy `access.log` (and `access.log.bak`) from the lead-dbs.org server into a folder, and download a free
   IP-to-country database in MaxMind format (for example DB-IP "IP to Country Lite").
2. `python3 -m pip install --require-hashes -r tools/requirements.txt` (exact versions), then `python3 tools/usage.py <log folder> <database.mmdb>`.
   This writes `data/usage.json`.
3. `npm ci && node scripts/usage.mjs` (`npm ci` installs the versions locked in `package-lock.json`). This redraws the charts of `/usage/`
   (`assets/diagrams/usage-*.svg`) with Pele, the tool that also draws the flow diagram on the home page.

What is counted and published: a launch is one start of Lead-DBS, and the same address counts once an
hour. `data/usage.json` holds totals by country, year, month, hour and tool only. It holds no single
launch, IP address, city or network name; do not add any (single launches to the minute could point
to one researcher).

- **The page `/usage/`** is `content/usage/index.md` (chart headings) and `layouts/usage.html`. It runs no
  script: the charts are inline SVG, coloured in `assets/css/site.css` ("usage"). Below them, folded, a
  table of every country with its downloads and launches (`#all-countries`), which the globe's section links to as
  `table_label` ("All countries"): the globe itself can only be read with a mouse.
