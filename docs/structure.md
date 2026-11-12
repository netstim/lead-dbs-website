# Site structure, search and addresses

How the menu, search, metadata and old addresses work. Start with the [README](../README.md).

## The menu and the footer

## Site structure

The main menu is grouped by what visitors come for and lists every page of its groups; the footer does not repeat it. The footer carries only what the menu lacks, so it stays short: the logo, four columns (Lead-DBS: download, "Release history" → `/download/#releases`, Cite Lead-DBS, source code, bug reports; Help: first steps, the manual, the user Slack, contact; Stay in touch: events, the newsletter, the news, its feed, Bluesky; Institute: the lab's sites), then one legal line with the research-use statement, and the legal pages (`layouts/_partials/footer.html`). The site's source ("Edit this site") is this repository, linked from the README, not the footer.

| Menu | Page | Holds |
|---|---|---|
| Methods | `/helpsupport/knowledge-base/lead-dbs-methods/` ("Methods": what Lead-DBS does in four numbered chapters, listed 01–04 beside the intro (`{{< jumps >}}`): "Single patients" `#single-patients`, "Groups of patients" `#groups-of-patients`, "In the operating theatre" `#operating-theatre` and "Tools and modules" `#tools`. Each chapter (`{{% chapter %}}`) has a short heading and a one-line lede, then its capabilities as cards (`{{< capabilities >}}`), each with its name, a picture, its manual chapter and papers: renders three to a row, figures from papers two, each opening at full size; a chapter's last figure, and Lead-OR, is a wide row; the tools a table (Lead Group, Lead Connectome, OSS-DBS, Lead Tutor). The renders are credited once, at the end; figures from papers carry their licence under the text; full width, no sidebar) | The page's chapters: the anchors Single patients and Groups of patients, Lead-OR (the page `/about/lead-or/`, the one tool of chapter 03 "In the operating theatre"; the anchor `#operating-theatre` stays on Features) and the anchor Tools and modules; the anchors are listed in the header's panel only, not in the sidebar of the articles (`params.panelOnly`). Under the caption "In depth", the articles: DBS network mapping, subcortical electrophysiology mapping, AC/PC to MNI conversion (with the former article "DBS targets in MNI space" as its background section); then, after a line, Made with Lead-DBS (`/gallery/`). Each article has the same sections: what it does (with a figure), how to use it, what to cite; longer material is folded. The overview is the word "Features" itself, as every group's hub is its word; the tools are its chapter 04 (`#tools`), and the former "Lead tools" page `/about/tools/` forwards there |
| Docs and help | `/helpsupport/` | First steps (step 1 links to the install steps on the download page), the manual (`/manual/`; on a phone a first-level word of the menu instead), Practice dataset (Lead Tutor) (the dataset's reference page; the exercise itself is step 2 of First steps), walkthrough videos (current recordings first, then "Older recordings"), get help (`/helpsupport/#get-help`, the one list of where to ask; the contact page sits under it) |
| Atlases and data | `/helpsupport/knowledge-base/atlasesresources/` | Three catalogues built alike (subcortical atlases with the macaque atlas, DISTAL and FOCUS; cortical parcellations; normative connectomes), then under the caption "By the Lead-DBS team" in the menu the two atlases by the Lead-DBS team, DISTAL and FOCUS (both with What it is, How to get it `#download`, What to cite and How it was built; DISTAL has the newer layout); "Choosing and using an atlas or connectome" (`#choosing` on the hub); under the caption "Background", the article "About the MNI spaces" (`/about-the-mni-spaces/`) |
| Community | `/community/` | Events (with a page for each upcoming event that needs one, both with a summary box (when, where, hosted by, registration): the developer meeting `/events/developer-meeting/` (who it is for, how to register, the flyer), the Hands-on Lead-DBS Workshop 2027 `/events/hands-on-workshop-2027/` (its "Get notified" button leads straight to the newsletter form, `/subscribe-to-our-newsletter/#subscribe`), the one place where the workshop's details grow; its news post only points there; and the past workshops), user Slack, Contribute (`/develop/`: code, atlases and datasets, bug reports; `/about/data-code-inclusion-philosophy/` forwards to its section `#add-your-atlas-or-dataset`), newsletter (with links to recent issues) |
| News | `/news/` | Releases and announcements (each post at `/<slug>/`); posts more than three calendar years older than the newest are listed under "Archive"; the RSS feed `/news/index.xml` |
| About | `/about/` (a paragraph, cards for its pages, then deep brain stimulation, and history with recognition and funding; the history links the 2017 essay "Commercial vs. academic software", which keeps its address `/commercial-vs-academic-software/`, is kept for the record and is left out of the site search) | Cite Lead-DBS, publications (every paper of `data/papers.yaml`, the library of studies that used Lead-DBS, cover art, what other researchers write), contributors (who coordinates Lead-DBS today and who built it), dependencies (the software Lead-DBS builds on, OSS-DBS among them, with what to cite) |
| Download | `/download/` (the header's button) | The current release, requirements and the install steps (`#install`, the only place they are written), standalone builds, licence (one line; the full terms with the research-use statement `#research-use` folded), release history (folded; versions before 3.0 folded again inside) |

The footer's legal line lists Imprint and Privacy Policy (`[menus.footer]`); Contact is in its Help column. The two legal pages end with
"Next" cards to each other, Contact and About like every other page.

**The menu is the ordinary site pages' hierarchy.** The manual uses its own chapter tree in `data/manual.json`; see [manual.md](manual.md). Addresses stay those of the old site, so the folders in
`content/` follow the old addresses, not the menu (the atlases live under
`content/helpsupport/knowledge-base/atlasesresources/`). The header's marked group, the breadcrumb and the
closing cards are therefore all drawn from the menu, not from the folders
(`layouts/_partials/nav-place.html`), so they always agree: a page belongs to the menu entry that is the page
itself, or else its nearest folder that is in the menu. Where that is not the right place, the page (or its
folder's `_index.md`) names it in its front matter, e.g. `menuParent: "/events"` on the past workshops. The breadcrumb then reads Home / Community / Events /
Past workshops. A menu entry that leads to another site gets a small
arrow wherever menus are drawn.

**One name per page.** A page's menu label, its `linkTitle` (breadcrumb, footer, closing cards, search), its
title (the h1) and its browser title are the same words ("Contributors", "DISTAL atlas"). When you rename a
page, change all of them; the address stays.

**Hub pages** (Docs and help, Atlases and data, Community, About) list the pages of their menu group, in
menu order, with the entry's `params.card` line from `hugo.toml`. Docs, Atlases and About are of the type
`hub` (full width, no sidebar) and place the list with a shortcode: Docs with `hub-section` and `link-rows`,
Atlases with `atlas-hub` (picture tiles with counts), About with `resource-index`; Community has its own
template (`layouts/community.html`). A page's `description` is the text search engines show; keep it to 155
characters. A menu entry with `params.divider` gets a line above it in the
header's panel; when the value is a text, that text is the caption over the entries from there on ("In
depth" on Features, "By the Lead-DBS team" over DISTAL and FOCUS, "Background" over the MNI spaces).

**Background articles** (long, lasting texts that began as news posts) live in the folder of the group they
belong to and keep their old address with `url:` in the front matter (`/about-the-mni-spaces/`, and the 2017
essay `/commercial-vs-academic-software/` under About); `showDate: true` prints when they were written under
the title, and `archived: true` adds "kept for the record" to that line for a text that is no longer kept up to
date (the essay, which also has `search: false`). They are not in the news list or feed.

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
there are none) a last line offers the manual, for questions about how to do something in Lead-DBS. Every manual chapter is indexed in full and labelled "Manual". Other results name the page above them as the breadcrumb does. Left out of the index: pages with `search: false`, redirect pages (`layout: redirect`) and the closed
forum's page. A page marked `noindex` for search engines is still in the site search; `search: false` is what
takes it out. The footer's pages (contact,
imprint, privacy) are found by their title only. `/search/` shows the same
box on a page (`/search/?q=atlas`); until a query is typed (and without script, with a line that the search
needs it) it shows the 404 page's nine rows to start from (`layouts/_partials/search-doors.html`), and it is
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
title and, for a page in the menu, the menu entry's `name` and its `linkTitle` (breadcrumb, closing cards, footer). The browser
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
old site's sitemap (`/wp-sitemap.xml`) resolves; the 112 author profiles (`/author/…`) lead to the Contributors page (`/about/team/`). The old feeds `/feed/` and `/news/feed/` lead to `/news/`, which names the
RSS feed `/news/index.xml`; on a server that can redirect, send them straight to the feed.
Files outside WordPress (`/release/download.php`, `/docs/…`) are on the current server; see Deployment.
