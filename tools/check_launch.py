#!/usr/bin/env python3
"""Checks that a build is the one to put on www.lead-dbs.org, not a preview or a test build.

    python3 tools/check_launch.py <build folder>

Errors (exit 1): a page of the preview (noindex, nofollow, the "under construction" banner), a robots.txt
that shuts search engines out or names no absolute sitemap, a sitemap address that is not
https://www.lead-dbs.org/…, a link to a preview of this site or to this computer, visible TODO/FIXME/TBD or
lorem ipsum text, or a missing 404 page, news feed or search index.
Notes (listed, exit 0): forms that are still switched off, and the addresses the site expects the server
to keep (/release/, /docs/, /wp-content/uploads/, /?na=…), so they can be checked after the switch.

tools/deploy.py package runs it; check-site.py checks links, canonicals and redirects. Standard library only.
"""
import html.parser
import os
import re
import sys

LIVE = "https://www.lead-dbs.org/"
# the site's own previews (other projects' github.io pages are fine) and this computer
PREVIEW_HOSTS = re.compile(r"(?:[a-z0-9-]+\.github\.io/lead-dbs-website|//localhost|//127\.0\.0\.1|//0\.0\.0\.0)(?::\d+)?[/\"']", re.I)
UNFINISHED = re.compile(r"\b(TODO|FIXME|TBD)\b|(?i:lorem ipsum)")
SERVER_PATHS = re.compile(r"(?:https://www\.lead-dbs\.org)?/(release/[^\"'#?\s]*|docs/[^\"'#\s]*\.pdf|wp-content/uploads/[^\"'\s]+|\?na=view[^\"'\s]*)")


class Text(html.parser.HTMLParser):
    """the words a visitor sees (not scripts, styles or templates)"""
    def __init__(self):
        super().__init__()
        self.skip, self.parts = 0, []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template") and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def main(root):
    errors, notes = [], []
    err, note = errors.append, notes.append
    for need in ("index.html", "404.html", "robots.txt", "sitemap.xml", "news/index.xml", "search-index.json"):
        if not os.path.isfile(os.path.join(root, need)):
            err("missing " + need)

    robots = read(os.path.join(root, "robots.txt")) if os.path.isfile(os.path.join(root, "robots.txt")) else ""
    if re.search(r"(?mi)^\s*Disallow:\s*/\s*$", robots):
        err("robots.txt shuts every search engine out (Disallow: /)")
    if not re.search(r"(?mi)^Sitemap:\s*" + re.escape(LIVE) + r"sitemap\.xml\s*$", robots):
        err("robots.txt does not name " + LIVE + "sitemap.xml")
    if os.path.isfile(os.path.join(root, "sitemap.xml")):
        locs = re.findall(r"<loc>([^<]+)</loc>", read(os.path.join(root, "sitemap.xml")))
        if not locs:
            err("the sitemap lists no pages")
        for l in [l for l in locs if not l.startswith(LIVE)][:5]:
            err("sitemap address not on " + LIVE + ": " + l)

    server_paths, offline_forms, pages = set(), set(), 0
    for dirpath, _, files in os.walk(root):
        for name in files:
            if not name.endswith(".html"):
                continue
            path = os.path.join(dirpath, name)
            url = "/" + os.path.relpath(path, root).replace(os.sep, "/").replace("index.html", "")
            raw = read(path)
            if 'http-equiv="refresh"' in raw or "http-equiv=refresh" in raw:
                continue  # a redirect page of an old address
            pages += 1
            if re.search(r"<meta name=\"?robots\"? content=\"?noindex, ?nofollow", raw):
                err(url + ": noindex, nofollow (a preview build)")
            if "preview-banner" in raw or 'class="is-preview"' in raw or "class=is-preview" in raw:
                err(url + ": the preview's under-construction banner")
            m = PREVIEW_HOSTS.search(raw)
            if m:
                err(url + ": a link to a preview or local host: " + raw[max(0, m.start() - 20):m.end() + 20].replace("\n", " "))
            t = Text()
            t.feed(raw)
            m = UNFINISHED.search(" ".join(t.parts))
            if m:
                err(url + ": unfinished text: " + m.group(0))
            if "form-offline" in raw:
                offline_forms.add(url)
            for m in SERVER_PATHS.finditer(raw):
                p = m.group(1)
                server_paths.add(p.split("?")[0] if p.startswith("release/") else p.replace("&amp;", "&"))

    for url in sorted(offline_forms):
        note("form still switched off (shows its email/RSS line): " + url)
    kinds = {}
    for p in server_paths:
        kinds.setdefault("?na=view" if p.startswith("?") else p.split("/", 1)[0], []).append(p)
    for kind, items in sorted(kinds.items()):
        note("expects the server to keep {} address(es) under {}: e.g. {}".format(len(items), kind, sorted(items)[0]))

    for n in notes:
        print("note   " + n)
    for e in errors:
        print("ERROR  " + e)
    print("{} pages checked, {} problems, {} notes".format(pages, len(errors), len(notes)))
    return 1 if errors else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
