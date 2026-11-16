# The integrated manual

The user guide lives at `/manual/`. Its 61 chapters and 142 images were imported from
the public Lead-DBS GitBook on 2026-11-12. Five section landing pages link to the chapters.
This is a local copy, not a live synchronization with GitBook.

## Editing

- Edit a chapter in `content/manual/<chapter>/_index.md`. Branch bundles preserve the
  nested chapter addresses. Keep existing paths and heading anchors when possible.
- Images are shared Hugo resources in `assets/manual/`. Markdown references them as
  `![Description](manual/filename.png "Optional caption")`; the existing image hook
  makes responsive versions and links large images to their originals. Tall screenshots are displayed at no more than 512px high; their source files remain unchanged. Small toolbar icons use the `manual-toolbar-icon` shortcode with the source display width.
- `data/manual.json` is the only place that orders the manual: groups, and in each group the chapters
  with their nested `children`. The sidebar, the previous/next links (the sidebar read top to bottom) and
  each section's overview cards all come from it. A chapter's sidebar label is its `linkTitle`; its page
  heading is `title`. Keep sidebar labels unique.
- A group whose folder has an `_index.md` (`/manual/lead-dbs/` and the others) gets an overview page of
  cards built from the sidebar; its body is not shown. A chapter with sub-pages lists them under
  "In this section" at its end.
- In the sidebar, a chapter with sub-pages has a link and a separate chevron. Only the branch holding the
  current page starts open; the chevron opens others without leaving the page.
- Notes use `{{% manual-note "info" %}}` or `"warning"`, closed by `{{% /manual-note %}}`. They
  carry an icon and no "Note" heading, so do not start them with "Note that". Existing expandable explanations remain native HTML details.
- `source_url` preserves provenance and links to the original chapter. The edit link
  goes to this repository. Published scientific terminology and GUI labels retain their
  original spelling, so the house-spelling copy rule excludes manual pages. Other copy,
  link, image, layout and browser checks still apply.

The manual shares the site's theme and search, with a dedicated compact docs header and article footer. The header exposes search (Cmd/Ctrl+K), learning resources and the download link. Search indexes each chapter's
full text, not just its opening paragraphs. It requires no new runtime or build dependency.

## Visual system

The documentation follows vercel.com/docs: one 64px header row (brand, Tutorials, Community, GitHub,
search, theme, Download), a chapter rail fixed to the window's left edge with a hairline border, and the
article (at most 736px) with its outline centred in the remaining width. No breakpoint moves the rail, so
nothing jumps between long and short pages. Below 1280px the outline moves above the article; below
1024px the resource links hide; below 768px the chapters open in a modal drawer.

It uses self-hosted **Geist** (Fontsource variable package 5.3.0, SIL OFL; `static/fonts/OFL-geist.txt`)
with Geist Mono for code; the main website keeps Inter. Body text is 16px, headings are semibold, and
the sidebar is 14px. Top-level ordered lists are procedures, drawn as numbered steps joined by a line.

`assets/css/manual.css` owns the layout, in one pass from tokens to phones. Size tokens live in
`base.css`; font faces and palette tokens live in `site.css`.

## Article components

Every chapter has a short `manual_lead` summary above its copy/edit actions. The local
outline includes second- and third-level headings. Keep procedure alternatives at the
same heading level, and preserve anchor IDs when changing titles.

Long inline filesystem paths can use `{{< manual-path "path/to/file" >}}` so they
prefer directory boundaries when wrapping, without changing copied text.

Fenced code uses an explicit language (`matlab`, `python`, `bash`, `batch` or `text`).
The render hook supplies syntax highlighting, a language label and shared clipboard
feedback. Examples over 20 lines start as expandable previews when JavaScript is
available; copying always includes the entire example. Overflow cues appear only when
the code needs horizontal scrolling. A wrapping toggle changes presentation only; copied
code keeps its original line breaks. Long examples have collapse controls at both ends. Without JavaScript, the complete example is visible.

Mobile navigation reuses the desktop tree in a native modal dialog, preserving the
active branch. Escape, backdrop and close control dismiss it; the article does not shift. A compact
sticky toolbar keeps chapters and a page-contents dialog available during deep reading.
Figures above 400 pixels wide link to their full-size originals on manual pages.

## Migration boundaries

`tools/import_manual.py` records the one-time import process and refuses to overwrite an
existing manual. Subsequent edits include repaired source anchors, a curated documentation landing page, a compact installation requirements table, and editorial corrections;
do not re-import over those edits. The source cache is optional and kept outside the repository.

Existing website links now point to local chapters. The old GitBook remains available:
redirecting addresses on `netstim.gitbook.io` requires changes there, and cannot be achieved
with Hugo aliases on this domain. No external account or hosting settings were changed.
Existing `/docs/` downloads remain untouched.

Scientific accuracy, obsolete instructions and missing descriptive image alt text inherited
from the original manual still need subject-matter review. Figures without source alt text
use their caption or a chapter-based label; the importer does not infer scientific descriptions.

## Screenshot follow-up

The existing GitBook screenshots are accepted for this migration. Replace the soft
GUI figures with authentic higher-resolution captures later, starting with:

- Coregistration controls: `assets/manual/16d44d8d6ed46fdd.png`, used in
  `content/manual/lead-dbs/step3-volume-registrations/coregister-volumes/_index.md`.
- Sweetspot Explorer overview and model setup: `assets/manual/3ae1e40a0a40ebff.png`
  and `assets/manual/e433ef760758138f.png`, used in
  `content/manual/lead-group/sweetspot-explorer/_index.md`.

When replacing these figures, verify that their GUI labels, numbered arrows and
captions still agree with the written steps. Keep the current images until the
replacement captures are available and checked.

## Checks

The existing PR and deployment workflows enforce the manual's design tokens, links,
copy rules and CSS usage. `check-design.py` also rejects un-tokenized font families
and inline styles in manual content and components.

Docs interaction tests live in `.github/scripts/check-browser.mjs`; there is no separate
`check-interactions` command. Its normal run checks every page at desktop and phone sizes
in both themes, then exercises quick-start command tabs and keyboard selection, search result counts, code expansion, wrapping and complete copying, narrow-screen
copy feedback, chapter-drawer focus and dismissal, sticky page navigation, and search.
It also checks that a chapter's chevron opens its pages without navigating, that previous/next follow the sidebar, and long-to-short page transitions at 1280, 1440, 1920 and 3000px with visible scrollbars, asserting stable header, chapter-rail and article geometry and retained rail scroll position. Headless Chromium normally hides scrollbars, so this check explicitly enables them.
Run it with the production build as documented in the script header.

The introduction keeps a concise research-use restriction above the first action, with
the complete original notice in the adjacent disclosure. Both command tabs copy only
the selected MATLAB command; without JavaScript, the Lead-DBS example remains visible.
