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
hugo --gc --minify     # production build into public/
```

## Editing

| What | Where |
|---|---|
| A page | `content/<url path>/index.md` (or `_index.md` if the page has sub-pages) |
| Images of a page | Same folder as its `index.md`; reference them by file name: `![alt](figure.png)` |
| A news post | `content/news/<slug>/index.md`; appears at `/<slug>/` |
| Main menu, footer links | `hugo.toml` → `[menus]` |
| Download / contact form fields | `data/forms.yaml` |
| Look and layout | `assets/css/main.css`, `layouts/` |

### Add a news post

```bash
mkdir content/news/my-post
```

`content/news/my-post/index.md`:

```markdown
---
title: "Lead-DBS 3.3 released"
date: 2026-12-01
slug: "lead-dbs-3-3-released"
image: "teaser.png"   # optional, a file in the same folder
---

Text in Markdown …
```

### Building blocks

Besides normal Markdown, pages can use these shortcodes (carried over from the old page builder):

```markdown
{{< button href="/download/" >}}Download Lead-DBS{{< /button >}}

{{% row %}}
{{% col "2/3" %}}
Text on the left …
{{% /col %}}
{{% col "1/3" %}}
![](figure.png)
{{% /col %}}
{{% /row %}}

{{< youtube VIDEO_ID >}}          {{< vimeo VIDEO_ID >}}
{{% gallery %}} images {{% /gallery %}}        {{% slideshow %}} images {{% /slideshow %}}
{{< form "contact" >}}            {{< newsletter >}}            {{< childpages >}}
```

Column widths: `1/2`, `1/3`, `2/3`, `1/4`, `3/4`, `1/5`, `2/5`, `3/5`, `4/5`.

## Old URLs

Every page keeps its WordPress URL (e.g. `/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`), so
links in papers and slides keep working. Files outside WordPress (`/release/download.php`,
`/docs/…`) are still linked on the old server.

## Re-importing from WordPress

`tools/import_wordpress.py` converted the WordPress pages to Markdown. It was meant to run once;
running it again with `--force` overwrites any edits made since:

```bash
uv run tools/import_wordpress.py --force
```
