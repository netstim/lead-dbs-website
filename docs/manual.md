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
- `data/manual.json` supplies the ordered reading sequence (`pages`) and the expandable
  sidebar (`groups[].chapters`, with nested `children`). Optional `label` values shorten sidebar wording without changing chapter titles. Update both when adding or moving
  chapters. Previous/next links derive directly from `pages`; chapter front matter does not duplicate the reading order.
- The `manual` layout is a deliberate exception to ordinary pages' single right sidebar.
  It has chapter navigation on the left and a local outline on the right; below 1200px
  the outline moves below the page summary, and below 768px chapters open in a modal drawer.
- GitBook hints use `{{% manual-note "info" %}}` or `"warning"`, closed by
  `{{% /manual-note %}}`. Existing expandable explanations remain native HTML details.
- `source_url` preserves provenance and links to the original chapter. The edit link
  goes to this repository. Published scientific terminology and GUI labels retain their
  original spelling, so the house-spelling copy rule excludes manual pages. Other copy,
  link, image, layout and browser checks still apply.

The manual shares the site's theme and search, with a dedicated compact docs header and article footer. The header exposes search (Cmd/Ctrl+K), learning resources and the download link. Search indexes each chapter's
full text, not just its opening paragraphs. It requires no new runtime or build dependency.

## Visual system

The documentation uses self-hosted **Geist** (Fontsource variable package 5.3.0, SIL OFL;
`static/fonts/OFL-geist.txt`). The main website continues to use Inter. Geist Mono is
used for code. Only manual pages override the font and neutral surface/ink tokens.
The Lead-DBS logo and blue action colour are retained.

The reference pages were inspected in a browser at 1280 × 800. xAI's article used its
`xVf` font, a 48px / 450 heading, 14px body text with 24px leading, and a reading column
starting at x=328. Vercel used Geist, 14px navigation, and 16px article text. The manual
combines Geist with a lighter 48px / 450 chapter heading, 15px body text, a single 72px
header and an open three-column layout. At that viewport the reading column starts
at x=328 and is 688px wide. These are intentional choices between the references,
not a claim that the pages are identical.

`assets/css/manual.css` owns the layout. Size tokens live in `base.css`; font faces and
palette tokens live in `site.css`. The docs font preload is conditional in `head.html`.
Keep the header to one row; resource links hide below 1024px, the local outline moves
above the article below 1200px, and chapters open in a modal drawer below 768px.

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

## Checks

The existing PR and deployment workflows enforce the manual's design tokens, links,
copy rules and CSS usage. `check-design.py` also rejects un-tokenized font families
and inline styles in manual content and components.

Docs interaction tests live in `.github/scripts/check-browser.mjs`; there is no separate
`check-interactions` command. Its normal run checks every page at desktop and phone sizes
in both themes, then exercises quick-start command tabs and keyboard selection, search result counts, code expansion, wrapping and complete copying, narrow-screen
copy feedback, chapter-drawer focus and dismissal, sticky page navigation, and search.
Run it with the production build as documented in the script header.

The introduction keeps a concise research-use restriction above the first action, with
the complete original notice in the adjacent disclosure. Both command tabs copy only
the selected MATLAB command; without JavaScript, the Lead-DBS example remains visible.
