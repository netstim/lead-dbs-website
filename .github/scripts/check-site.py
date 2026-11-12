#!/usr/bin/env python3
"""Checks a built site (the output folder of `hugo`) and exits with 1 on any problem.

    python3 .github/scripts/check-site.py public https://netstim.github.io/lead-dbs-website/

The second argument is the baseURL the site was built with. A build for https://www.lead-dbs.org/ is the
production build; any other baseURL is a preview (GitHub Pages), which asks search engines to index nothing.
Checked:

- the folder is a build: it has index.html, 404.html and sitemap.xml, and at least one page;
- every internal link, image, script, stylesheet and srcset entry leads to a file of the build, and
  every #anchor to an element with that id on the page it points at. A link is internal when it is a
  path, or a full address on the build's host or on www.lead-dbs.org (the preview is a copy of that
  site), except /release/, /docs/ and /?na=… addresses, which the old server keeps serving;
- every redirect page (old addresses, `<meta http-equiv="refresh">`) leads straight to a page of the
  build (and its #anchor), not to another redirect;
- og:image, the sitemap's addresses and robots.txt's Sitemap line are absolute addresses, the sitemap's
  on the baseURL's host;
- every page that search engines may index has a canonical and an og:url, and both are the page's own
  address on https://www.lead-dbs.org/ (on a preview build too, so the copy points search engines at
  the live site);
- the production sitemap lists no page that asks search engines not to index it (robots noindex), and
  every page of a preview build asks it;
- no page shows front matter as text (a "keywords:" or "title:" line, or a "---" fence) in its main
  content, which happens when a Markdown file's front matter is broken;
- no page has an empty sidebar, the production build has no form that cannot be sent, and no page shows
  escaped HTML as text (a Markdown indent turned a template line into a code block once);
- a page has one name: its browser title is its h1, or its h1 followed by " – Lead-DBS" (a later page of
  the news list adds ", page 2" and so on).

Only the Python standard library is used.
"""
import html.parser
import os
import re
import sys
import urllib.parse

ROOT = sys.argv[1] if len(sys.argv) > 1 else "public"
BASE = sys.argv[2] if len(sys.argv) > 2 else "/"
base = urllib.parse.urlparse(BASE)
BASE_PATH = base.path if base.path.endswith("/") else base.path + "/"
BASE_HOST = base.netloc
# the live site: canonical addresses point there, from the preview too
LIVE = "https://www.lead-dbs.org/"
LIVE_HOST = urllib.parse.urlparse(LIVE).netloc
# decided by the baseURL alone, never by what the build contains, so a production build that says
# noindex on every page cannot pass as a preview
IS_PREVIEW = BASE != LIVE

errors = []


def err(msg):
    errors.append(msg)


class Page(html.parser.HTMLParser):
    """Collects links, ids, metadata and the text of <main> of one HTML file."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.meta = [], set(), {}
        self.refresh = None
        self.main_depth = 0
        self.skip_depth = 0
        self.text = []
        self.title, self.h1 = None, None
        self.in_title = self.in_h1 = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a" and "name" in a:
            self.ids.add(a["name"])
        for key in ("href", "src", "poster"):
            if a.get(key) and not (tag == "link" and a.get("rel") in ("canonical", "alternate")):
                self.links.append((tag, a[key]))
        if a.get("srcset"):
            for part in a["srcset"].split(","):
                url = part.strip().split(" ")[0]
                if url:
                    self.links.append((tag, url))
        if tag == "link" and a.get("rel") == "canonical":
            self.meta["canonical"] = a.get("href", "")
        if tag == "meta":
            prop = a.get("property") or a.get("name")
            if prop in ("og:url", "og:image", "robots"):
                self.meta[prop] = a.get("content", "")
            if (a.get("http-equiv") or "").lower() == "refresh":
                m = re.search(r"url=(.+)$", a.get("content", ""), re.I)
                if m:
                    self.refresh = m.group(1).strip()
        if tag == "title" and self.title is None:
            self.in_title, self.title = True, ""
        if tag == "h1" and self.h1 is None:
            self.in_h1, self.h1 = True, ""
        if tag == "main":
            self.main_depth += 1
        if self.main_depth and tag in ("script", "style", "pre", "code", "template"):
            self.skip_depth += 1

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
        if self.main_depth and tag in ("script", "style", "pre", "code", "template") and self.skip_depth:
            self.skip_depth -= 1
        if tag == "main" and self.main_depth:
            self.main_depth -= 1

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1 += data
        if self.main_depth and not self.skip_depth:
            self.text.append(data)


def to_file(path):
    """The file in ROOT that serves a site path (without query or fragment), or None."""
    if not path.startswith(BASE_PATH):
        return None
    rel = urllib.parse.unquote(path[len(BASE_PATH):])
    cand = os.path.join(ROOT, rel)
    if rel == "" or rel.endswith("/"):
        cand = os.path.join(cand, "index.html")
    if os.path.isfile(cand):
        return cand
    if os.path.isdir(cand) and os.path.isfile(os.path.join(cand, "index.html")):
        return os.path.join(cand, "index.html")
    return None


OWN_HOSTS = {h for h in (BASE_HOST, LIVE_HOST, LIVE_HOST.removeprefix("www.")) if h}


def internal_path(url, page_url):
    """The site path (under BASE_PATH) a link points at, or None for links to other sites, to files the
    old server keeps serving, and to non-web schemes."""
    u = urllib.parse.urlparse(url)
    if u.scheme in ("mailto", "tel", "data", "javascript"):
        return None
    if u.scheme or u.netloc:
        if u.scheme not in ("http", "https", "") or u.netloc not in OWN_HOSTS:
            return None
        # a full address on the site's own host: on the build's host the path already starts with
        # BASE_PATH; on the live site it is the same page at the root
        path = u.path or "/"
        if u.netloc == BASE_HOST and path.startswith(BASE_PATH):
            live_path = "/" + path[len(BASE_PATH):]
        else:
            live_path, path = path, BASE_PATH + path.lstrip("/")
        # the downloads (/release/download.php), PDFs (/docs/) and newsletters (/?na=view&id=…) stay on
        # the old WordPress server beside the site (README, Deployment)
        if live_path.startswith(("/release/", "/docs/")) or (live_path == "/" and u.query):
            return None
        return u._replace(scheme="", netloc="", path=path)
    full = urllib.parse.urljoin(page_url, url)
    return urllib.parse.urlparse(full)


for need in ("index.html", "404.html", "sitemap.xml"):
    if not os.path.isfile(os.path.join(ROOT, need)):
        err(f"{ROOT} has no {need}: is it the output folder of hugo?")

pages = {}
for dirpath, _, files in os.walk(ROOT):
    for f in files:
        if f.endswith(".html"):
            fp = os.path.join(dirpath, f)
            p = Page()
            with open(fp, encoding="utf-8") as fh:
                p.feed(fh.read())
            pages[fp] = p


def page_url(fp):
    rel = os.path.relpath(fp, ROOT).replace(os.sep, "/")
    if rel.endswith("index.html"):
        rel = rel[: -len("index.html")]
    return BASE_PATH + rel


LEAK = re.compile(r"(?m)^\s*(?:---\s*$|(?:keywords|aliases|menuParent|linkTitle|lastmod|htmlTitle|description|title|date|weight|slug):\s)")
absolute_live = None
checked = 0
for fp, p in sorted(pages.items()):
    url = page_url(fp)
    if p.refresh is not None:
        # redirect pages name their target as a full address on the site's own host
        target = internal_path(p.refresh, url)
        if target is not None:
            tf = to_file(target.path)
            if not tf:
                err(f"{url}: redirects to {p.refresh}, which is not in the build")
            elif target.fragment and target.fragment not in pages[tf].ids:
                err(f"{url}: redirects to {p.refresh}, but that page has no #{target.fragment}")
            elif tf in pages and pages[tf].refresh is not None:
                err(f"{url}: redirects to {p.refresh}, which redirects again")
        continue
    checked += 1
    for tag, link in p.links:
        target = internal_path(link, url)
        if target is None:
            continue
        tf = to_file(target.path)
        if not tf:
            err(f"{url}: <{tag}> {link} is not in the build")
            continue
        if target.fragment and tf.endswith(".html") and target.fragment not in pages[tf].ids:
            err(f"{url}: {link}: no element with id {target.fragment!r} there")
    v = p.meta.get("og:image")
    if v is not None and not re.match(r"https?://", v):
        err(f"{url}: og:image is not an absolute address: {v!r}")
    noindex = "noindex" in p.meta.get("robots", "")
    if IS_PREVIEW and not noindex:
        err(f"{url}: a page of the preview build without robots noindex")
    # the preview says noindex on every page because it is the preview, so there every page counts
    own = LIVE + url[len(BASE_PATH):]
    for key in ("canonical", "og:url"):
        v = p.meta.get(key)
        if v is None:
            if IS_PREVIEW or not noindex:
                err(f"{url}: no {key} (expected {own})")
        elif v != own:
            err(f"{url}: {key} is {v!r}, not the page's address on the live site, {own}")
    if p.title is not None and p.h1 is not None:
        name = lambda t: re.sub(r"\s+", " ", re.sub("[\u00ad\u200b\u2060]", "", t)).strip()
        title, h1 = re.sub(r", page \d+(?= – |$)", "", name(p.title)), name(p.h1).rstrip("#").strip()
        if title not in (h1, f"{h1} – Lead-DBS"):
            err(f"{url}: the browser title {name(p.title)!r} is not the h1 {h1!r}")
    raw = open(fp, encoding="utf-8", errors="ignore").read()
    if re.search(r'<aside class="?sidebar"?[^>]*>\s*</aside>', raw):
        err(f"{url}: an empty sidebar (a page with nothing to put in it has none)")
    if not IS_PREVIEW and ("form-note" in raw or re.search(r"<form[^>]*>(?:(?!</form>).)*<button[^>]*\bdisabled", raw, re.S)):
        err(f"{url}: a form that cannot be sent on the production site")
    m = re.search(r"&lt;/?(span|a|div|p|svg|img|br)\b", raw)
    if m:
        err(f"{url}: escaped HTML shown as text: {raw[m.start():m.start() + 60]!r}")
    text = "".join(p.text)
    m = LEAK.search(text)
    if m:
        line = text[m.start(): text.find("\n", m.start() + 1)].strip()
        err(f"{url}: front matter shown as text in the page: {line[:80]!r}")

sitemap = os.path.join(ROOT, "sitemap.xml")
if os.path.isfile(sitemap):
    locs = re.findall(r"<loc>([^<]+)</loc>", open(sitemap, encoding="utf-8").read())
    for loc in locs:
        tf = to_file(urllib.parse.urlparse(loc).path)
        if not re.match(r"https?://", loc):
            err(f"sitemap.xml: not an absolute address: {loc}")
        elif BASE_HOST and urllib.parse.urlparse(loc).netloc != BASE_HOST:
            err(f"sitemap.xml: {loc} is not on {BASE_HOST}")
        elif not tf:
            err(f"sitemap.xml: {loc} is not in the build")
        elif not IS_PREVIEW and tf in pages and "noindex" in pages[tf].meta.get("robots", ""):
            err(f"sitemap.xml: {loc} is marked noindex")
robots = os.path.join(ROOT, "robots.txt")
if os.path.isfile(robots):
    for line in open(robots, encoding="utf-8"):
        if line.lower().startswith("sitemap:") and not re.match(r"https?://", line.split(":", 1)[1].strip()):
            err(f"robots.txt: the Sitemap line is not an absolute address: {line.strip()}")

if not checked:
    err(f"{ROOT}: no pages")

for e in errors:
    print("ERROR", e)
print(f"{checked} pages and {len(pages) - checked} redirect pages checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
