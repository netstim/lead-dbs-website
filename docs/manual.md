# The integrated manual

The user guide lives at `/manual/`. Its 61 chapters and 142 images were imported from
the public Lead-DBS GitBook on 2026-11-12. Five section landing pages link to the chapters.
This is a local copy, not a live synchronization with GitBook.

## Editing

- Edit a chapter in `content/manual/<chapter>/_index.md`. Branch bundles preserve the
  nested chapter addresses. Keep existing paths and heading anchors when possible.
- Images are shared Hugo resources in `assets/manual/`. Markdown references them as
  `![Description](manual/filename.png "Optional caption")`; the existing image hook
  makes responsive versions. Large images open in a viewer, with access to the full original.
  Tall screenshots are displayed at no more than 512px high. Small toolbar icons use the
  `manual-toolbar-icon` shortcode with the source display width.
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

The Manual has its own header with a link to the main site, a Manual home link, search, theme and
Download. Its search uses the shared index and limits results to Manual pages. Open it with
`/` or Cmd/Ctrl+K. The main site's header and search retain their site-wide navigation.

## Visual system

The chapter rail stays at the left edge on desktop. The article (at most 736px) and a separately
scrollable outline sit in the remaining width. At 1280px and above, the grid reserves space for
the outline on every chapter so the article stays aligned across pages. Below 1280px the outline
appears in a disclosure above the article. Below 1024px the chapter rail becomes a sticky toolbar
and the reading column gets the full available width. The header height token includes the preview
banner and sets both the sticky offsets and the clearance for fragment links.

It uses the site's own type and colours: Inter for text and headings, the system monospace
(`--font-mono`) for code, and the Blend palette tokens of `site.css` (only the code-highlight colours,
`--docs-code-*`, are the manual's). Its type scale is compact: body text 16px, the sidebar 14px,
semibold headings. Actions are the site's: the ink pill with a plain link beside it. Top-level ordered
lists are procedures, drawn as numbered steps joined by a line. The footer is one quiet 13px line.

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
code keeps its original line breaks. The toolbar has one Copy control. Long examples have one
expand/collapse control below the code. Without JavaScript, the complete example is visible.

Wrap citation lists in `manual-references` to give each entry its own Copy action. For lists headed
Publications, use `kind="publication"` so those buttons are named distinctly.

The narrow layout moves the chapter tree and the inline outline into native modal dialogs after
the manual bundle initializes. Escape, the backdrop and the close button dismiss the dialogs.
Selecting a section moves keyboard focus to its heading. Without the bundle, the chapters are
available in a native disclosure at every width, and the outline stays in the page. The outline
uses the rendered article's second- and third-level headings and also includes the landing
page's template sections and the generated “In this section” heading when present.

A two-column table whose first cells are code names (the command-line options) reads as a list on a
phone, each name unbroken over its description; code names in table cells never break inside.
Figures above 400 pixels wide link to their full-size originals on manual pages.

## Migration boundaries

`tools/import_manual.py` records the one-time import process. It refuses to run while `content/manual`
or `data/manual.json` exists, builds the import in a temporary folder and moves it into place only after
every download succeeded, and has a report-only `--plan`. Subsequent edits include repaired source anchors, a curated documentation landing page, a compact installation requirements table, and editorial corrections;
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

The browser sweep in `.github/scripts/check-browser.mjs` checks desktop and phone layouts in both
themes, plus command tabs, code examples, navigation, and chapter rail geometry with visible
scrollbars. `.github/scripts/check-interactions.mjs` covers keyboard navigation, short viewports,
blocked scripts, and drawer behavior in Chromium and WebKit. The Pages workflow also runs it
with `--manual-only` against the published artifact's base path and preview-banner layout.

The landing page has a short research-use restriction with the complete original notice in a
disclosure. Both command tabs copy the selected MATLAB command. When their script is unavailable,
the Lead-DBS example remains visible and the tabs stay hidden.

The landing page lists four workflow categories linked to the section overview pages from
`data/manual.json`, followed by User Slack, Dependencies and Source code, then the MATLAB
launch terminal. It draws no empty article when the landing page body is absent. On phones,
chapter navigation starts as a native disclosure; only a successfully initialized manual bundle
replaces it with the drawer toolbar. Copy link stays hidden when the clipboard API is unavailable.
