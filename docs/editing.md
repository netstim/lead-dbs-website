# Editing pages

Pictures, shortcodes, events, news posts and releases. Start with the [README](../README.md).

## Pictures in pages

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

## Long pages: the table of contents

A `doc` page with three or more `##` sections gets "On this page" by itself:
at the top of the text on a phone and a tablet, and in the right sidebar on a desktop, where it stays in view
while the text scrolls and marks the section being read; the threshold is `tocMinHeadings` in `hugo.toml`. It lists the `##` sections, so give long
pages real headings in order: the page's title is its only `h1` (a `#` heading in the Markdown is
drawn as `h2`).

## Writing for the site

- **Short and scannable**: a sentence or two on what the page is for, then `##` headings and lists. Put a
  long list that only some readers need (old fees, early papers) in a fold:
  `<details class="more"><summary>What is inside</summary>` … `</details>` (blank lines around the
  Markdown inside). Every fold is as wide as the text column, and folds that follow each other share one line.
- **Contribute** (`/develop/`) has its own template, `layouts/contribute.html` (front matter `layout: contribute`):
  the ways to contribute, the set-up steps, the atlas notes and the facts are lists in the page's front matter.
- **An event's page** is of the type `event` (front matter `layout: event`, `event:` the entry's id in
  `data/events.yaml`; `hugo new content --kind event`): one line of text, the facts as cells, Register or
  Get notified with "Add to calendar", and the flyer named in front matter `flyer:` (see [Events](#events)).
- **First steps** has its own template, `layouts/first-steps.html` (front matter `layout: first-steps`): its steps
  (title, text, picture, actions) and its fixes are lists in the page's front matter.
- **What to cite**: the paper in a `copybox` with "Copy the citation", written with `{{< paper id "full" >}}`
  where the paper is in `data/papers.yaml` (atlas pages, method articles, Lead-OR, Lead Tutor, Cite Lead-DBS).
- **"Lead-DBS" never breaks at its hyphen**: the templates wrap it in a no-wrap span
  (`layouts/_partials/nobreak-html.html`; headings, links, tables, menus, cards, news and atlas entries).
  Write the ordinary hyphen.
- **Old material says it is old**: a news post older than three years shows an archive note with the
  current version above its text (`layouts/news/single.html`); give older recordings and change-logs a
  date in their text.

## Events

`data/events.yaml` lists developer meetings and workshops; the file's head explains every field. The next
event shows in four places: as the fifth fact in the home page's hero, in the home page's "Workshop and
developer meeting" block (every upcoming event), the home page's chip, and `/events/`
(menu: Community › Events), which lists upcoming events soonest first and past ones latest first. An event that is
over moves to "Past events" by itself; entries can stay in the file.

An event with more to say than its card (a flyer, the facts known so far) gets a page of its own in
`content/events/`, such as `/events/developer-meeting/` and `/events/hands-on-workshop-2027/`; its entry links
it under `links`, and other pages link the page rather than a news post about the event.

**To add an event**, copy an entry and change it:

```yaml
  - id: "developer-meeting"        # never changes: the event's #id on /events/ and its page's event:
    title: "Lead-DBS Developer Meeting"
    start: "2027-06-16T15:00"      # in the event's own time zone
    end: "2027-06-16T16:30"        # optional; without it the event counts as over at midnight
    timezone: "Europe/Berlin"
    also_in: "America/New_York"    # optional second zone, printed in brackets
    where: "Online (Zoom)"
    online: true
    text: "One or two sentences."
    register_url: "/events/developer-meeting/"
```

- The build checks every entry and stops with its name on an unknown field, a missing `id`, `title`,
  `start`, `timezone`, `where` or `text`, an id used twice, a date in another format or one that does not
  exist (30 February, or a time the clock skips when summer time begins), an `end` that is not after
  `start`, a `timezone` or `also_in` that is not an IANA zone, an `online` that is not `true` or `false`
  (without quotes), a link without `label` and `url`, and a Zoom join link (`zoom.us/j/`, `/wc/`, `/s/`,
  `/w/`, `/my/`) in `register_url` or `links`.
- "Add to calendar" (on `/events/` and the event's page) is a calendar file made from the entry: a meeting
  with a start time and no end lasts an hour; one whose `end` is a day runs to the end of that day; an event
  whose `start` is a day is entered as whole days. Each date of the monthly meeting is its own calendar entry.
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
2. A few lines in `assets/js/main/events.js` check again by the visitor's clock: they hide an event that has ended since
   the build and show the next one, and on `/events/` move it to "Past events". Without script, the build's
   choice shows.

An event's own page stays when the event is over: Register and "Add to calendar" give way to a line that says
when it took place and leads to `/events/` (by the build's time, and again by the visitor's clock).

To see the site as it will look on another day: `hugo server --clock 2026-11-20T10:00:00+01:00`.

## Add a news post

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
[Pictures in pages](editing.md#pictures-in-pages).

## Cut a release

1. `data/release.yaml`: `version`, `date`, `summary` (one or two sentences for the home page), `notes`
   (the post about the release), `changes_url` (the GitHub compare view from the release before),
   and `matlab`, `toolboxes`, `memory`, `standalone` and the rest if they changed (the manual's
   [installation page](https://netstim.gitbook.io/leaddbs/installation) is the reference for the requirements). Every current version, date and requirement
   on the site comes from this file: the home page, the download page (and its browser title), First steps,
   the structured data, and the archive note on old news posts.
2. `data/releases.yaml`: the same version, date and announcement as a new first row of the release history
   (the table at `/download/#releases`); the build stops if its first row is not the version in `release.yaml`.
3. A news post about the release (above), titled "Lead-DBS 3.3 released" (a few words may follow after a
   colon when there is something urgent to say), and its address in `notes`. The post's date is the day it
   was announced; when that differs from the release date, the post's head and the release history show both.
4. The download links on `/download/` if the files' names changed (they point to `/release/download.php` on
   the current server; see [Deployment](../README.md#deployment)).
5. Search the content for the old version number (`grep -rn "3\.2\.1" content/`): old news posts keep theirs;
   change any other mention by hand.

## Building blocks

Besides normal Markdown, pages can use these shortcodes:

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
{{< form "contact" >}}            {{< newsletter >}}

{{% copybox label="Copy the paragraph" %}}A text with a button that copies it.{{% /copybox %}}
{{< clip src="anim.mp4" poster="anim-poster.jpg" alt="What it shows" >}}

![Alt text](figure.png "A caption under the picture.")
```

- `chapters` lists a video's chapters, one `Title: hh:mm:ss` per line, the time on the left.
- **Citations** in lists are plain text with only the DOI linked: `Author, A. (2020). Title. *Journal*, 1, 2–3. [doi:10.1000/xyz](https://doi.org/10.1000/xyz)`.
- **Papers about Lead-DBS, its methods and tools** are written once, in `data/papers.yaml`: `{{< paper ewert2019 >}}`
  links one by its short name ("Ewert 2019", as in the tools table on Features), `{{< paper ewert2019 "full" >}}`
  prints the full reference (Cite, Lead-OR, Lead Tutor, dependencies), and `{{% papers %}}` lists them all by group
  (Publications). A paper added there appears on Publications by itself.
- The download page has its own template, `layouts/download.html` (front matter `layout: download`): what Lead-DBS
  needs and how to install it come from `data/release.yaml` and `data/install.yaml`, the servers and the standalone
  builds from the page's front matter (First steps links to `/download/#install`).
- `capability` is one thing Lead-DBS does, on the Features page: its name, one sentence, a picture (a lab
  render, a gallery figure credited from `data/gallery.yaml`, or a picture of another page with `alt`), its
  manual chapter, papers and the page that explains it in depth; the shortcode's comment lists the parameters.
  It stands inside `capabilities`, which lays a chapter's capabilities out as a showcase: on the left the
  names, one under the other; the chosen one stands in ink with its sentence and its links (small pills)
  under it, the others are grey; from 1024px one large black stage on the right shows the chosen one's
  picture (a render fills it; a figure from a paper, `fit="contain"`, sits whole on it and opens at full
  size). A click on a name chooses it (`assets/js/main/features.js`); below 1024px the chosen one holds its own
  picture; without script every one is open. Renders carry no credit of their own; the page credits them
  once. Its `id` is the anchor other pages link to (`#stimulation`, `#connectivity` …): such a link chooses
  that one. `tools` shows the named tools of the page's front matter as picture cells, four
  across: a render (`img`), the name, one sentence, its links.
- `chapter` opens a numbered chapter of a long showcase page (Features): `{{% chapter n="1" img="images/renders/…" %}}`
  around the chapter's `##` heading and a one-line lede; from 1024px the render is a low band beside them,
  below that it follows them, and a phone leaves it out. Its number has the style of the numbers of `jumps`
  and of the steps of First steps: a label.
- `copybox` holds a text to copy as a whole (the methods paragraph on `/about/citing_leaddbs/` and every "What to cite"); the button
  copies it as plain text and is hidden where the browser cannot copy. All copy buttons use
  `assets/js/clipboard.js`: `data-copy` names an element ID; `data-copy-text` holds a literal command.
  Citation tabs update the target ID. Success and failure are announced through a status element;
  page templates and shortcodes do not install their own clipboard handlers.
- `video-grid` and `video-card` lay videos out as a grid of cards (Walkthrough videos): the video, a small tag, a
  heading and a sentence; `lead="true"` makes a card span the grid.
- `clip` is a short silent animation (see [Pictures in pages](editing.md#pictures-in-pages)).
- `jumps` is the numbered contents of a long page (Features):
  `{{< jumps "Single patients|#single-patients; Tools|#tools" >}}`; the build stops on an anchor the page lacks.
  With the page's intro between its tags, the intro and the contents sit side by side on a desktop.
- `button` labels may be long: they wrap on a phone.
- A retired address is kept as `aliases:` in the front matter of the page that replaces it; Hugo writes a
  redirect page there (`layouts/alias.html`, marked `noindex`). When the content now lives in one section of
  another page, keep the old page as a stub with `layout: redirect` and `redirect: "/path/#anchor"`
  (`layouts/redirect.html`; see `/about/deep-brain-stimulation-2/`).

**Videos** get a poster: save a still of the video next to the page as `video-<id>.jpg` (the YouTube or
Vimeo id), and the player shows it before it is started; nothing loads from the video site until then.

### Atlas catalogues

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
set in medium weight as on the event pages;
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
