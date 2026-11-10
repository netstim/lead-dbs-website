# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4>=4.12", "markdownify>=0.13"]
# ///
"""One-off import of the WordPress site at lead-dbs.org into Hugo content.

Reads pages and posts from the public WordPress REST API, converts the Enfold
page-builder HTML to Markdown plus a few shortcodes (row/col, button, gallery,
slideshow, form, newsletter, childpages), and downloads the images each page
uses into its page bundle.

Usage (from the repository root):

    uv run tools/import_wordpress.py            # writes content/
    uv run tools/import_wordpress.py --force    # overwrite existing files

Re-running overwrites hand edits, so this is meant to be run once.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from markdownify import markdownify

SITE = "https://www.lead-dbs.org"
API = f"{SITE}/wp-json/wp/v2"
UA = {"User-Agent": "Mozilla/5.0 (lead-dbs-website importer)"}
MAX_DOWNLOAD = 20 * 1024 * 1024  # larger files keep pointing at the old server

# Pages that are not migrated: forum and its login/sign-up pages, menu-only
# placeholder pages, and WordPress's default "Hello world" post.
SKIP_LINKS = {
    "/helpsupport/forum/login/",
    "/helpsupport/forum/sign-up/",
    "/news/",
    "/hallo-welt/",
}
FORM_FOR_PAGE = {"/download/": "download", "/downloadfocus/": "downloadfocus", "/contact/": "contact"}
UPLOAD_RE = re.compile(r"^https?://(?:www\.)?lead-dbs\.org/(?:wp-content/uploads|storage)/(.+)$")
SITE_RE = re.compile(r"^https?://(?:www\.)?lead-dbs\.org(/[^?#]*)?(\?[^#]*)?(#.*)?$")
COL_RE = re.compile(r"^av_(one|two|three|four)_(full|half|third|fourth|fifth)$")
FRACTIONS = {"one_full": "1", "one_half": "1/2", "one_third": "1/3", "two_third": "2/3",
             "one_fourth": "1/4", "three_fourth": "3/4", "one_fifth": "1/5",
             "two_fifth": "2/5", "three_fifth": "3/5", "four_fifth": "4/5"}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def fetch_json(url: str):
    raw = fetch(url).decode("utf-8")
    # A login plugin prints an HTML notice before the JSON body.
    start = min(i for i in (raw.find("["), raw.find("{")) if i >= 0)
    return json.loads(raw[start:])


def fetch_all(kind: str) -> list[dict]:
    items, page = [], 1
    while True:
        try:
            batch = fetch_json(f"{API}/{kind}?per_page=100&page={page}")
        except urllib.error.HTTPError as e:
            if e.code == 400:
                break
            raise
        if not batch:
            break
        items += batch
        page += 1
    return items


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def resolve_redirect(url: str) -> str:
    opener = urllib.request.build_opener(NoRedirect)
    try:
        opener.open(urllib.request.Request(url, headers=UA), timeout=30)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308) and e.headers.get("Location"):
            return e.headers["Location"]
        raise
    return url


@dataclass
class Bundle:
    """Collects the files a page needs next to its Markdown file."""

    dir: Path
    files: dict[str, str] = field(default_factory=dict)  # remote url -> local name

    def add(self, url: str) -> str | None:
        if url in self.files:
            return self.files[url]
        name = urllib.parse.unquote(url.rsplit("/", 1)[-1].split("?")[0])
        name = re.sub(r"[^\w.-]+", "-", name, flags=re.ASCII).strip("-")
        stem, dot, ext = name.rpartition(".")
        n, local = 1, name
        while local in self.files.values():
            n += 1
            local = f"{stem}-{n}.{ext}" if dot else f"{name}-{n}"
        target = self.dir / local
        if not target.exists():
            try:
                quoted = urllib.parse.quote(urllib.parse.unquote(url), safe=":/?&=#")
                req = urllib.request.Request(quoted, headers=UA)
                with urllib.request.urlopen(req, timeout=120) as r:
                    size = int(r.headers.get("Content-Length") or 0)
                    if size > MAX_DOWNLOAD:
                        return None
                    data = r.read(MAX_DOWNLOAD + 1)
                if len(data) > MAX_DOWNLOAD:
                    return None
            except urllib.error.HTTPError as e:
                print(f"  ! {e.code} {url}", file=sys.stderr)
                return None
            self.dir.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        self.files[url] = local
        return local


class Converter:
    def __init__(self, sdm_targets: dict[str, str], page_paths: dict[str, str]):
        self.sdm_targets = sdm_targets
        self.page_paths = page_paths  # WordPress page/post id -> path
        self.tokens: dict[str, str] = {}

    # -- helpers ---------------------------------------------------------
    def token(self, markdown: str) -> str:
        key = f"ZZTOK{len(self.tokens)}ZZ"
        self.tokens[key] = markdown
        return key

    def block(self, markdown: str) -> Tag:
        """A <p> holding a token, so markdownify keeps it on its own line."""
        tag = BeautifulSoup("", "html.parser").new_tag("p")
        tag.string = self.token(markdown)
        return tag

    def put_block(self, el: Tag, markdown: str) -> None:
        p = el.parent
        tag = self.block(markdown)
        el.replace_with(tag)
        if p is not None and p.name == "p" and p.get_text(strip=True) == tag.get_text(strip=True):
            p.unwrap()

    def link(self, href: str, bundle: Bundle) -> str:
        href = html.unescape(href.strip())
        if not href or href.startswith(("mailto:", "#", "tel:")):
            return href
        if re.match(r"^(www\.)?[\w-]+\.(org|com|net|de|edu)/", href):
            href = "http://" + href  # a few links were saved without a scheme
        if href.endswith("#new_tab"):
            href = href[: -len("#new_tab")]
        m = UPLOAD_RE.match(href)
        if m:
            local = bundle.add(f"{SITE}/wp-content/uploads/{m.group(1)}")
            return local or href
        m = SITE_RE.match(href)
        if m:
            path, query, frag = m.group(1) or "/", m.group(2) or "", m.group(3) or ""
            if "sdm_process_download" in query:
                did = urllib.parse.parse_qs(query[1:]).get("download_id", [""])[0]
                return self.sdm_targets.get(did, href)
            qs = urllib.parse.parse_qs(query[1:])
            ids = qs.get("page_id") or qs.get("p")
            if ids and ids[0] in self.page_paths:
                return self.page_paths[ids[0]] + frag
            if "forum=" in query or path.startswith("/helpsupport/forum"):
                return "/helpsupport/slack-user-channel/"
            if path.startswith("/release/") or query or "." in path.rsplit("/", 1)[-1]:
                return href  # files outside WordPress (/docs/, /release/) stay on the old server
            if not path.endswith("/"):
                path += "/"
            known = set(self.page_paths.values())
            if path not in known:
                # WordPress redirected moved pages by slug; do the same here.
                slug = path.rstrip("/").rsplit("/", 1)[-1]
                matches = [k for k in known if k.rstrip("/").endswith("/" + slug)]
                if len(matches) == 1:
                    path = matches[0]
            return path + frag
        return href

    @staticmethod
    def video_shortcode(snippet: str) -> str | None:
        m = re.search(r"(?:youtube\.com/(?:embed/|watch\?v=)|youtu\.be/)([\w-]{11})", snippet)
        if m:
            return f"{{{{< youtube {m.group(1)} >}}}}"
        m = re.search(r"vimeo\.com/(?:video/)?(\d+)", snippet)
        if m:
            return f"{{{{< vimeo {m.group(1)} >}}}}"
        return None

    def testimonial(self, el: Tag, bundle: Bundle) -> str:
        text = el.select_one(".avia-testimonial-content")
        name = el.select_one(".avia-testimonial-name")
        role = el.select_one(".avia-testimonial-subtitle")
        body = self.md(str(text), bundle).strip() if text else ""
        quote = "\n".join("> " + line if line else ">" for line in body.splitlines())
        who = "— **" + name.get_text(strip=True) + "**" if name else ""
        if role:
            who += ", " + role.get_text(" ", strip=True)
        return quote + ("\n>\n> " + who if who else "")

    def images_md(self, imgs: list[tuple[str, str, str | None]]) -> str:
        """[(src, alt, link)] -> one Markdown image per line."""
        lines = []
        for src, alt, href in imgs:
            md = f"![{alt}]({src})"
            lines.append(f"[{md}]({href})" if href else md)
        return "\n".join(lines)

    # -- Enfold elements -------------------------------------------------
    def preprocess(self, soup: BeautifulSoup, bundle: Bundle, form: str | None) -> None:
        for el in soup.select(".avia-video"):
            sc = self.video_shortcode(el.get("data-original_url", "") + str(el))
            self.put_block(el, sc or "")
        for el in soup.find_all("iframe"):
            sc = self.video_shortcode(el.get("src", ""))
            if sc:
                self.put_block(el, sc)
        for el in soup.select(".nf-form-cont"):
            self.put_block(el, f'{{{{< form "{form or "contact"}" >}}}}')
        for el in soup.select(".tnp"):
            if el.find_parent(class_="tnp") is None:
                self.put_block(el, "{{< newsletter >}}")
        for el in soup.select(".child_pages"):
            self.put_block(el, "{{< childpages >}}")
        for el in soup.find_all(["script", "style", "noscript", "meta"]):
            el.decompose()
        for el in soup.select(".sdm_download_count"):
            el.decompose()
        for el in soup.select("div.hr"):
            if "hr-invisible" in el.get("class", []):
                el.decompose()
            else:
                el.replace_with(soup.new_tag("hr"))

        for el in soup.select(".avia-slideshow-arrows, .avia-slideshow-dots, .avia-slideshow-controls"):
            el.decompose()
        for el in soup.find_all("img", src=re.compile(r"^data:")):
            el.decompose()

        fakes = soup.select(".av-partner-fake-img")
        if fakes:
            container = fakes[0].parent
            while container.parent is not None and len(container.select(".av-partner-fake-img")) < len(fakes):
                container = container.parent
            logos = []
            for f in fakes:
                m = re.search(r"url\(([^)]+)\)", f.get("style", ""))
                entry = f.find_parent(class_="slide-entry") or f
                link = entry.find("a", href=True)
                if m:
                    logos.append((self.link(m.group(1).strip("'\""), bundle), entry.get("data-avia-tooltip", ""),
                                  self.link(link["href"], bundle) if link else None))
            self.put_block(container, "{{% logos %}}\n" + self.images_md(logos) + "\n{{% /logos %}}")

        for wrap in soup.select(".avia-testimonial-wrapper"):
            quotes = [self.testimonial(t, bundle) for t in wrap.select(".avia-testimonial")]
            self.put_block(wrap, "{{% testimonials %}}\n" + "\n\n".join(quotes) + "\n{{% /testimonials %}}")
        for el in soup.select(".avia-testimonial"):
            self.put_block(el, self.testimonial(el, bundle))

        for show in soup.select(".avia-slideshow"):
            imgs = [(self.link(i["src"], bundle), i.get("alt", ""), None) for i in show.find_all("img")]
            self.put_block(show, "{{% slideshow %}}\n" + self.images_md(imgs) + "\n{{% /slideshow %}}")

        for gal in soup.select(".avia-gallery"):
            imgs = []
            for a in gal.select("a"):
                img = a.find("img")
                if not img:
                    continue
                full = a.get("href", "")
                imgs.append((self.link(img["src"], bundle), img.get("alt", ""), self.link(full, bundle) if full else None))
            self.put_block(gal, "{{% gallery %}}\n" + self.images_md(imgs) + "\n{{% /gallery %}}")

        masonry = soup.select("a.av-masonry-entry")
        if masonry:
            imgs = []
            for a in masonry:
                img = a.find("img")
                if img:
                    imgs.append((self.link(img["src"], bundle), a.get("title", ""), self.link(a["href"], bundle)))
            container = masonry[0].find_parent(class_="av-masonry") or masonry[0].parent
            self.put_block(container, "{{% gallery %}}\n" + self.images_md(imgs) + "\n{{% /gallery %}}")

        for a in soup.select("a.avia-button, a.sdm_download"):
            label = a.get_text(" ", strip=True) or "Download"
            href = self.link(a.get("href", ""), bundle)
            if not href and "publications" in label.lower():
                href = "/about/publications/"
            sc = f'{{{{< button href="{href}" >}}}}{label}{{{{< /button >}}}}'
            wrap = a.find_parent(class_=re.compile(r"avia-button-wrap|sdm_download_button_box"))
            target = wrap if wrap is not None else a
            self.put_block(target, sc)

        for img in soup.find_all("img"):
            img["src"] = self.link(img.get("src", ""), bundle)
            for attr in ("srcset", "sizes", "class", "width", "height", "title", "decoding", "fetchpriority", "loading", "itemprop"):
                img.attrs.pop(attr, None)
        for a in soup.find_all("a", href=True):
            a["href"] = self.link(a["href"], bundle)

    def columns(self, soup: BeautifulSoup, bundle: Bundle) -> None:
        """Replace top-level Enfold columns by tokens; grouped into rows later."""
        for col in soup.select("div.flex_column"):
            if col.find_parent("div", class_="flex_column") is not None:
                continue
            classes = col.get("class", [])
            width = next((c[3:] for c in classes if COL_RE.match(c)), "one_full")
            first = "first" in classes
            inner = BeautifulSoup("".join(str(c) for c in col.contents), "html.parser")
            body = self.convert_soup(inner, bundle)
            col.replace_with(self.block(json.dumps([width, first, body])))

    # -- conversion ------------------------------------------------------
    def md(self, fragment: str, bundle: Bundle) -> str:
        text = markdownify(fragment, heading_style="ATX", bullets="-", escape_underscores=False,
                           strip=["span", "section", "div", "figure", "figcaption"])
        return tidy(text)

    def convert_soup(self, soup: BeautifulSoup, bundle: Bundle) -> str:
        self.columns(soup, bundle)
        return self.md(str(soup), bundle)

    def convert(self, raw_html: str, bundle: Bundle, form: str | None) -> str:
        self.tokens = {}
        soup = BeautifulSoup(raw_html, "html.parser")
        self.preprocess(soup, bundle, form)
        text = self.convert_soup(soup, bundle)
        text = self.group_rows(text)
        # Tokens can nest (a button inside a column), so expand until stable.
        for _ in range(5):
            new = re.sub(r"ZZTOK\d+ZZ", lambda m: self.tokens.get(m.group(0), ""), text)
            if new == text:
                break
            text = new
        return tidy(text)

    def group_rows(self, text: str) -> str:
        out, row = [], []

        def flush():
            if not row:
                return
            if len(row) == 1 and row[0][0] == "one_full":
                out.append(self.group_rows(row[0][2]))
            else:
                parts = ["{{% row %}}"]
                for width, _, body in row:
                    parts.append(f'{{{{% col "{FRACTIONS.get(width, "1")}" %}}}}\n{self.group_rows(body)}\n{{{{% /col %}}}}')
                parts.append("{{% /row %}}")
                out.append("\n".join(parts))
            row.clear()

        for line in text.split("\n"):
            m = re.fullmatch(r"\s*(ZZTOK\d+ZZ)\s*", line)
            payload = self.tokens.get(m.group(1)) if m else None
            if payload and payload.startswith('["'):
                width, first, body = json.loads(payload)
                if first:
                    flush()
                row.append((width, first, body))
                continue
            if line.strip():
                flush()
            out.append(line)
        flush()
        return "\n".join(out)


def is_web_image(path: Path) -> bool:
    head = path.read_bytes()[:12]
    return head.startswith((b"\x89PNG", b"\xff\xd8", b"GIF8")) or (head[:4] == b"RIFF" and head[8:] == b"WEBP")


def tidy(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"^(#+ )\*\*(.+?)\*\*\s*$", r"\1\2", text, flags=re.M)
    text = re.sub(r"[ \t]+\n", lambda m: "  \n" if m.group(0).startswith("  ") else "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


def yaml_str(s: str) -> str:
    return json.dumps(s, ensure_ascii=False)


def front_matter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        if v is None or v == "":
            continue
        lines.append(f"{k}: {v if isinstance(v, int) else yaml_str(str(v))}")
    lines.append("---\n")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("content"))
    ap.add_argument("--force", action="store_true", help="overwrite existing Markdown files")
    args = ap.parse_args()

    print("fetching pages and posts …")
    pages, posts = fetch_all("pages"), fetch_all("posts")
    all_html = "".join(x["content"]["rendered"] for x in pages + posts)
    sdm_ids = sorted(set(re.findall(r"sdm_process_download=1&(?:amp;|#038;)?download_id=(\d+)", all_html)))
    sdm_targets = {i: resolve_redirect(f"{SITE}/?sdm_process_download=1&download_id={i}") for i in sdm_ids}
    print(f"resolved {len(sdm_targets)} download links")
    page_paths = {str(x["id"]): x["link"][len(SITE):] or "/" for x in pages + posts if x["link"].startswith(SITE)}
    conv = Converter(sdm_targets, page_paths)

    parents = {p["parent"] for p in pages}
    for p in pages:
        link = p["link"]
        if not link.startswith(SITE):
            continue  # menu placeholders pointing elsewhere (GitBook, forum)
        path = link[len(SITE):] or "/"
        if path in SKIP_LINKS:
            continue
        if path == "/":
            target = args.out / "_index.md"
        elif p["id"] in parents:
            target = args.out / path.strip("/") / "_index.md"
        else:
            target = args.out / path.strip("/") / "index.md"
        write(conv, p, target, args.force, form=FORM_FOR_PAGE.get(path),
              extra={"weight": p.get("menu_order") or None})

    news = args.out / "news"
    news.mkdir(parents=True, exist_ok=True)
    (news / "_index.md").write_text(front_matter({"title": "News"}))
    for p in posts:
        path = p["link"][len(SITE):]
        if path in SKIP_LINKS:
            continue
        target = news / p["slug"] / "index.md"
        image = None
        if p.get("featured_media"):
            try:
                media = fetch_json(f"{API}/media/{p['featured_media']}")
                # WordPress's resized copies are always web formats; one original is a PSD.
                sizes = media.get("media_details", {}).get("sizes", {})
                src = (sizes.get("large") or sizes.get("full") or {}).get("source_url", media["source_url"])
                image = Bundle(target.parent).add(src)
                if image and not is_web_image(target.parent / image):
                    (target.parent / image).unlink()  # e.g. a PSD uploaded as featured image
                    image = None
            except urllib.error.HTTPError:
                pass
        write(conv, p, target, args.force, form=None, extra={"slug": p["slug"], "image": image})


def write(conv: Converter, item: dict, target: Path, force: bool, form: str | None, extra: dict) -> None:
    if target.exists() and not force:
        print(f"  skip (exists) {target}")
        return
    bundle = Bundle(target.parent)
    body = conv.convert(item["content"]["rendered"], bundle, form)
    fm = {
        "title": html.unescape(item["title"]["rendered"]),
        "date": item["date"],
        "lastmod": item["modified"],
        **extra,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(front_matter(fm) + "\n" + body)
    print(f"  wrote {target} ({len(bundle.files)} files)")


if __name__ == "__main__":
    main()
