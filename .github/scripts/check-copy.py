#!/usr/bin/env python3
"""Checks the visible text of a built site for leftovers and house-style slips; exits with 1 on any.

    python3 .github/scripts/check-copy.py public

Only the <main> of each page is read, without code blocks, citations and links' addresses.
Checked: template or comment leftovers, text that describes the interface instead of the content,
and the house spelling (British -our/-re/-ll- with -ize: fibre, colour, modelling, centre; "email").
Paper titles and citations (.paper, .cite, blockquote), news posts and texts kept for the record
are left as published.

Only the Python standard library is used.
"""
import html.parser
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")

RULES = [
    (r"-->|–>|\{\{|\}\}|\{[.#][\w-]", "template or Markdown leftover"),
    (r"\b(type in the box|open an entry|the box below|click here|this page (explains|shows|lists))\b", "describes the interface, not the content"),
    (r"\b(fiber|fibers|color|colors|modeling|center)\b", "house spelling: fibre, colour, modelling, centre"),
    (r"\be-mail\b", "house spelling: email"),
    (r"forum is closed|Renders by the Lead-DBS team|Just looking for the software|player loads from|Each entry says|"
     r"Plays from (YouTube|Vimeo)|Render credits", "a phrase the owner struck as filler"),
    (r"\bGeneral Public Licence\b", "the licence's name is the GNU General Public License"),
]
SKIP_TAGS = {"script", "style", "code", "pre", "blockquote", "svg", "nav"}
SKIP_CLASSES = re.compile(r"\b(paper|cite|copy-box|citation|atlas__cite)\b")


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Text(html.parser.HTMLParser):
    """The text of <main>, without skipped subtrees. Depth is counted for every element, so a skipped
    subtree ends exactly where its element ends, whatever is nested inside it."""

    def __init__(self):
        super().__init__()
        self.depth = 0          # open elements
        self.main_at = None     # depth of <main>
        self.skip_at = None     # depth of the element whose subtree is skipped
        self.out = []
        self.repeats = []
        self.body_class = ""

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        self.depth += 1
        if tag == "body":
            self.body_class = a.get("class") or ""
        if tag == "main" and self.main_at is None:
            self.main_at = self.depth
        if self.skip_at is None and (tag in SKIP_TAGS or a.get("aria-hidden") == "true" or SKIP_CLASSES.search(a.get("class") or "")):
            self.skip_at = self.depth

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if self.skip_at == self.depth:
            self.skip_at = None
        if self.main_at == self.depth:
            self.main_at = -1
        self.depth -= 1

    def handle_data(self, data):
        if self.main_at and self.main_at > 0 and self.skip_at is None:
            self.out.append(data)
            for m in re.finditer(r"\b(\w{3,}) \1\b", data):
                self.repeats.append(data[max(0, m.start() - 40): m.end() + 40].strip())


errors = []
pages = 0
for f in sorted(ROOT.rglob("index.html")):
    raw = f.read_text(errors="ignore")
    if 'http-equiv="refresh"' in raw or "http-equiv=refresh" in raw:
        continue
    pages += 1
    p = Text()
    p.feed(raw)
    text = re.sub(r"\s+", " ", " ".join(p.out))
    # news posts and texts kept for the record stay as they were published
    as_published = "section-news" in p.body_class.split() or "kept for the record" in raw.lower()
    for ctx in [] if as_published else p.repeats:
        errors.append(f"{f.relative_to(ROOT)}: repeated word: …{ctx}…")
    for pattern, why in RULES:
        if as_published and "spelling" in why:
            continue
        if "struck" in why and str(f.relative_to(ROOT)).startswith("helpsupport/forum/"):
            continue  # the page old forum links land on says that the forum closed
        for m in re.finditer(pattern, text, flags=re.I if "spelling" not in why else 0):
            ctx = text[max(0, m.start() - 40): m.end() + 40]
            if "spelling" in why and re.search(r"\((19|20)\d\d\)|et al\.|doi|\d+ ?\(\d+\),", ctx):
                continue  # a citation: the paper's own spelling
            errors.append(f"{f.relative_to(ROOT)}: {why}: …{ctx}…")

for e in errors:
    print(e)
print(f"{pages} pages checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
