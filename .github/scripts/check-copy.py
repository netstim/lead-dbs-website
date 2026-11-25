#!/usr/bin/env python3
"""Checks the copy of a built site; exits with 1 on any failure. Warnings are printed for a person to judge
and never fail the run.

    python3 .github/scripts/check-copy.py public

Failures, for copy that is objectively wrong:
  - the visible text of <main> (and of the 404 page), without code blocks, citations, quotations and links'
    addresses: template or comment leftovers, text that describes the interface instead of the content, a
    word written twice in a row (also across inline tags: "the <a>the</a>"), the house spelling (American:
    fiber, color, modeling, center, millimeter, gray, license, practice, program, analyze, -ize; "email"),
    except in the manual, which keeps its imported British spelling until it has a pass of its own; the product names
    (Lead-DBS, Lead Tutor, Lead Group, Lead Connectome, OSS-DBS, WarpDrive) and FOCUS, which is requested,
    not downloaded;
  - the editorial surface around it: every page's <title> and meta description, alt and placeholder texts,
    aria-labels, form labels, and the visible text of the header and footer (leftovers, spelling and names;
    each problem is reported once, at the first page that has it);
  - an action that promises the newsletter ("Subscribe", "Get notified") while the newsletter page has no
    form to subscribe with.
Warnings, for tone:
  - hype words and stock phrases (HYPE);
  - a sentence of eight words or more that stands on several pages, unless REPEATS approves it on exactly
    those pages (an approved entry that no longer matches is reported too, so the list stays true);
  - a first heading after the h1 that repeats the h1;
  - a paragraph with more than one pair of spaced dashes;
  - a header menu entry whose name differs from the h1 of its page (SHORT_LABELS lists the deliberate ones).
Keep spelling and names as published in dated news posts. Run tone warnings unless a page is explicitly
marked as an immutable archive (front matter archived: true, which the page head shows as "kept for the
record"). Never alter paper titles, quotations, literal UI labels or code: paper titles and citations
(.paper, .cite) and quotations (blockquote) are not checked, and literal software labels, sequence names
and the like that keep their own spelling are listed in EXEMPT. The manual's text is checked like every
other page's; its bold interface labels keep the software's spelling but stay in the sentences that warnings
quote.

Only the Python standard library is used.
"""
import collections
import html
import html.parser
import pathlib
import re
import sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "public")

# British forms, in any case ("Fibre tracts" at the start of a heading too); names of institutions that keep
# them ("McConnell Brain Imaging Centre") are in EXEMPT
SPELLING = (r"(?i)\b((sub)?millimetres?|fibres?|colours?|coloured|colouring|modell(ing|ed)|"
            r"centres?|centred|neighbour\w*|behaviour\w*|grey|labell(ed|ing)|catalogues?|programmes?|paediatric|ageing|"
            r"licences?|practis(e|es|ed|ing)|operating theatre)\b")
NAMES = r"\b(LeadDBS|Lead DBS|LEAD-DBS|Lead-Tutor|Lead-Group|Lead-Connectome|OSS DBS|OSSDBS|Warpdrive|Warp Drive)\b"
RULES = [
    (r"-->|–>|\{\{|\}\}|\{[.#][\w-]", "template or Markdown leftover"),
    (r"\b(type in the box|open an entry|the box below|click here|this page (explains|shows|lists))\b", "describes the interface, not the content"),
    (SPELLING, "house spelling (American): fiber, color, modeling, center, millimeter, gray, labeled, catalog, program, license, practice"),
    (r"\be-mail\b", "house spelling: email"),
    (r"\b([Aa]nalys(e|ed|ing)|[Vv]isualis\w*|[Nn]ormalis\w*|[Ll]ocalis\w*|[Oo]rganis(e|es|ed|ing|ation|ations)|"
     r"[Gg]eneralis\w*|[Oo]ptimis\w*|[Cc]haracteris(e|es|ed|ing|ation))\b",
     "house spelling (American): analyze, visualize, normalize, localize, organize, generalize"),
    (NAMES, "product name: Lead-DBS, Lead Tutor, Lead Group, Lead Connectome, OSS-DBS, WarpDrive"),
    (r"\bDownload FOCUS\b", "FOCUS is sent on request: Request FOCUS"),
    (r"forum is closed|Renders by the Lead-DBS team|Just looking for the software|player loads from|Each entry says|"
     r"Plays from (YouTube|Vimeo)|Render credits", "a phrase the owner struck as filler"),
    (r"\bGeneral Public Licence\b", "the licence's name is the GNU General Public License"),
]


def cased(why):
    """Spelling and names are case-sensitive and left as published in news posts ("lead dbs" in lower case
    is the MATLAB command; a capitalized "Center" in an institution's name is a literal, listed in EXEMPT)."""
    return "spelling" in why or why.startswith("product name")


# Literal names that keep their own spelling: software labels, sequence and institution names. A match is
# blanked out before the rules run. Add a phrase here only when it is a literal the reader must find as
# written (a button, a menu, a published name), never to excuse editorial prose.
EXEMPT = [
    r"Fiber Filtering( Explorer)?", r"[Ff]iber [Ff]iltering [Ee]xplorer", r"Fiber Activation", r"fiber_filtering",
    r"[Ff]ast [Gg]ray [Mm]atter [Aa]cquisition", r"Gray Matter", r"gray matter nulled",
    r"Center for [A-Z]\w+", r"[A-Z]\w+ (Medical )?Center\b", r"Medical Center", r"Brain Center",
    r"Color ?map", r"Colorbar", r"McConnell Brain Imaging Centre", r"Centre Hospitalier\b[^,<]*", r"Modeling (Platform|Toolbox)", r"Lead-DBS Main Window", r"Color by regressor",
    r"Group Colors", r"NIfTI and Analyze", r"Analyze (format|image)",
]

SKIP_TAGS = {"script", "style", "code", "pre", "blockquote", "svg", "nav"}
SKIP_CLASSES = re.compile(r"\b(paper|cite|copy-box|citation|atlas__cite)\b")

# Warnings. Context-specific: "streamline" in tractography, "Robust" in NASCAR and paper titles are not
# hype, which is why these never fail.
HYPE = (r"\b(seamless(ly)?|powerful|leverag(e|es|ed|ing)|cutting-edge|state-of-the-art|empower(s|ed|ing)?|unlock(s|ed|ing)?|"
        r"streamlin(e|es|ed|ing) (the|your|our|its)|comprehensive|game-chang\w*|revolutioni[sz]\w*|effortless(ly)?|"
        r"best-in-class|world-class|unparalleled|whether you're|not just\b[^.]{1,60}\bbut|we are (so )?excited|"
        r"to the best of our knowledge|100 ?%|perfectly|most detailed)\b")
# Header menu names that are deliberately shorter than their page's h1.
SHORT_LABELS = {
    ("/helpsupport/", "Docs"), ("/helpsupport/knowledge-base/atlasesresources/", "Atlases"),
    ("/helpsupport/knowledge-base/lead-dbs-methods/", "Methods"), ("/download/", "Download Lead-DBS"),
    ("/helpsupport/#get-help", "Get help"),
}

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# elements inside a line of text: their text runs on with the text around them; every other element (and
# a skipped subtree, and a void element such as <br> or <img>) ends a run, so a word at the end of one
# paragraph and the same word at the start of the next is not a repeat
INLINE = {"a", "abbr", "b", "bdi", "bdo", "cite", "data", "dfn", "em", "i", "kbd", "mark", "q", "s", "samp",
          "small", "span", "strong", "sub", "sup", "time", "u", "var"}
BREAK = "\x00"   # \s does not match it, so a repeat never spans a break
SURFACE_ATTRS = ("alt", "placeholder", "aria-label")
# the end of a sentence, for the repeated-sentence warning; not after an abbreviation inside one
SENTENCE_END = r"(?<!\bvs\.)(?<!\bal\.)(?<!\bFig\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<=[.!?])\s+|" + BREAK
# Repetition that is right where it stands: a sentence (as the warning quotes it, the manual's bold
# interface labels included) and the exact set of pages (site paths) it may stand on. A sentence that
# spreads to another page warns again. Approve a sentence only when each page needs it to stand alone;
# never reword a safety notice, a prerequisite or an interface label to silence the warning.
CA = "/manual/connectomics/connectomic-analyses/"
DFA, FFE, NME = CA + "discriminative-fibertracts-analysis/", CA + "fiber-filtering-explorer/", CA + "network-mapping-explorer/"
SSE = "/manual/lead-group/sweetspot-explorer/"
REG = "/manual/lead-dbs/step3-volume-registrations/"
NORM, REFINE = REG + "normalization-of-images/", REG + "subcortical-refine-post-to-pre-transforms/"
REPEATS = {
    # the research-use notice, word for word on Download and at the start of the manual
    "It is not intended for diagnosis, treatment planning, surgical targeting, DBS programming, patient management, or any other clinical decision concerning an individual patient.":
        {"/download/", "/manual/"},
    "Lead-DBS is research software intended for retrospective scientific analysis of neuroimaging data, electrode locations and group-level associations in research studies.":
        {"/download/", "/manual/"},
    "Outputs must not be used as a basis for clinical care.":
        {"/download/", "/manual/"},
    # the methods pop-up of both registration steps
    "A pop-up window with information about methods and references.":
        {NORM, REFINE},
    # the connectomic explorers share their method, prerequisites and steps; each page stands alone
    "After this calculation, you can explore the results interactively.":
        {DFA, FFE, NME},
    "Alternatively, you can simply use the peak value (more conforming to the “all or nothing” principle of action potentials) or the 5% peak values.":
        {DFA, FFE},
    "Current validation strategies include permutation (Leave-Nothing-Out) based approaches, as well as Leave-One-Patient-Out, Leave-One-Cohort-Out, and k-fold (randomized) cross-validations (Image 4, arrow 1).":
        {FFE, NME},
    "Depending on the analysis, average or sum these values.":
        {DFA, FFE},
    "Each tract in the normative connectome is analysed separately.":
        {DFA, FFE},
    "For each E-field, sample its values at the points along the tract, whether the field is shown in yellow or blue in panel A.":
        {DFA, FFE},
    "For this step, all the VTAs/E-fields have to be calculated (select the Calculate stats & VTA button in the Lead Group interface).":
        {FFE, NME},
    "In this method, the same is done for binary VTAs (which in the case of Lead-DBS are thresholded E-Fields).":
        {DFA, FFE},
    "Parts of this tract pass through some of the E-fields shown in yellow.":
        {DFA, FFE},
    "Subcohorts can be created by selecting patients in the bottom window.":
        {FFE, SSE},
    "The final step across frameworks is Crossvalidation & Prediction (Image 1, red arrow 3).":
        {FFE, NME, SSE},
    "They traverse less closely to the ones shown in blue but will still traverse through areas of those E-Fields that have a lower magnitude sum (remember that the E-Field is the estimated vector field denoting changes in voltage induced by the stimulation; its magnitude would be the absolute difference of voltage between two points).":
        {DFA, FFE},
    "This effect could be clinical (for example, %-UPDRS-III improvement following STN-DBS) or behavioural (for example, change in risk-taking behaviour or movement speed in a motor task).":
        {DFA, NME},
    "Thus, each single tract splits the group of VTAs (in template space) into two sets.":
        {DFA, FFE},
    "Use this step to assess model validity within cohorts and generalization across cohorts.":
        {FFE, NME, SSE},
    "Variable of interest (VOI) is the dependent variable, such as clinical score (Image 2, arrow 2).":
        {FFE, NME},
    "You can also generate predictions for individual patients, predefined subcohorts, cohorts and sets (Image 4, arrow 2).":
        {FFE, NME, SSE},
}


class Text(html.parser.HTMLParser):
    """The text of <main>, without skipped subtrees, plus the editorial surface of the whole page, the
    headings and paragraphs of <main> in order. Depth is counted for every element, so a skipped subtree
    ends exactly where its element ends, whatever is nested inside it."""

    def __init__(self):
        super().__init__()
        self.depth = 0          # open elements
        self.main_at = None     # depth of <main>
        self.skip_at = None     # depth of the element whose subtree is skipped
        self.quote_at = None    # depth of a quotation or citation (its alt texts are left as published)
        self.out = []           # visible text of <main>, the manual's bold interface labels blanked
        self.full = []          # the same with those labels kept: the sentences that warnings compare
        self.body_class = ""
        self.surface = []       # strings of the editorial surface
        self.chrome_at = None   # depth of the <header>/<footer> outside <main>, or of a <label>/<title>
        self.chrome = []        # its text so far
        self.headings = []      # (level, text) in <main>
        self.paragraphs = []    # the text of each <p> in <main>
        self.block = None       # [kind, depth, parts] of the heading or paragraph being read
        self.literal_at = None  # depth of a bold interface label in the manual
        self.link_at = None     # depth of the <a> being read
        self.linked = []        # the text of each link in <main>: a card that quotes another page's lead

    def in_main(self):
        return bool(self.main_at and self.main_at > 0)

    def handle_starttag(self, tag, attrs):
        if tag not in INLINE:
            self.out.append(BREAK)
            self.full.append(BREAK)
        a = dict(attrs)
        if tag == "meta" and a.get("name") == "description":
            self.surface.append(a.get("content") or "")
        if self.quote_at is None and tag != "svg":
            self.surface.extend(a[k] for k in SURFACE_ATTRS if a.get(k))
        if tag in VOID:
            return
        self.depth += 1
        if tag == "body":
            self.body_class = a.get("class") or ""
        if tag == "main" and self.main_at is None:
            self.main_at = self.depth
        if self.skip_at is None and (tag in SKIP_TAGS or a.get("aria-hidden") == "true" or SKIP_CLASSES.search(a.get("class") or "")):
            self.skip_at = self.depth
        if self.quote_at is None and (tag == "blockquote" or SKIP_CLASSES.search(a.get("class") or "")):
            self.quote_at = self.depth
        if tag == "a" and self.link_at is None and self.in_main():
            self.link_at = self.depth
            self.linked.append("")
        if self.chrome_at is None and (tag in ("title", "label") or (tag in ("header", "footer") and not self.in_main())):
            self.chrome_at, self.chrome = self.depth, []
        if self.chrome_at is not None and tag in ("script", "style", "svg", "a", "li", "p", "h2", "h3", "span", "button"):
            self.chrome.append(BREAK)
        # the manual writes interface labels in bold (check-manual.py): they keep the software's spelling
        if self.literal_at is None and tag in ("strong", "b", "kbd") and "section-manual" in self.body_class.split():
            self.literal_at = self.depth
        if self.in_main() and self.block is None and (re.fullmatch(r"h[1-6]", tag) or tag == "p"):
            self.block = [tag, self.depth, []]

    def handle_endtag(self, tag):
        if tag not in INLINE:
            self.out.append(BREAK)
            self.full.append(BREAK)
        if tag in VOID:
            return
        if self.block and self.block[1] == self.depth:
            text = re.sub(r"\s+", " ", "".join(self.block[2])).strip()
            if self.block[0] == "p":
                self.paragraphs.append(text)
            else:
                self.headings.append((int(self.block[0][1]), text))
            self.block = None
        if self.chrome_at == self.depth:
            self.surface.extend("".join(self.chrome).split(BREAK))
            self.chrome_at = None
        if self.skip_at == self.depth:
            self.skip_at = None
        if self.literal_at == self.depth:
            self.literal_at = None
        if self.link_at == self.depth:
            self.link_at = None
        if self.quote_at == self.depth:
            self.quote_at = None
        if self.main_at == self.depth:
            self.main_at = -1
        self.depth -= 1

    def handle_data(self, data):
        if self.chrome_at is not None and self.skip_at is None:
            self.chrome.append(data)
        if self.in_main() and self.skip_at is None:
            # a line break alone between two elements is a template's markup between parts that CSS sets
            # apart (a tile's title and its text), not a space inside a sentence
            gap = not data.strip() and "\n" in data
            self.out.append(BREAK if gap else " " * len(data) if self.literal_at else data)
            self.full.append(BREAK if gap else data)
            if self.block:
                self.block[2].append(data)
            if self.link_at is not None:
                self.linked[-1] += data

    def repeats(self):
        """A word written twice in a row, in the visible text with inline tags removed."""
        runs = re.sub(r"[ \t\r\n ]+", " ", "".join(self.out))
        for m in re.finditer(r"\b(\w{3,}) \1\b", runs, re.I):
            yield runs[max(0, m.start() - 40): m.end() + 40].replace(BREAK, " ").strip()


def blank_exempt(text):
    """The text with every EXEMPT literal replaced by spaces of the same length."""
    for pattern in EXEMPT:
        text = re.sub(pattern, lambda m: " " * len(m.group(0)), text)
    return text


def matches(text, as_published, manual=False):
    """(why, context) for every rule that the text breaks. The manual is not checked for spelling."""
    checked = blank_exempt(text)
    for pattern, why in RULES:
        if as_published and cased(why):
            continue
        if manual and "spelling" in why:
            continue
        for m in re.finditer(pattern, checked, flags=0 if cased(why) else re.I):
            if why.startswith("house spelling") and re.search(r"\((19|20)\d\d\)|et al\.|doi|Proceedings|\d+ ?\(\d+\),",
                                                              text[max(0, m.start() - 40): m.end() + 40]):
                continue  # a citation: the paper's own spelling
            yield why, text[max(0, m.start() - 40): m.end() + 40]


def h1_of(path):
    """The h1 text of a built page (a site path), or None."""
    f = ROOT / path.strip("/") / "index.html"
    if not f.is_file():
        return None
    m = re.search(r"<h1[^>]*>(.*?)</h1>", f.read_text(errors="ignore"), re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", m.group(1)))).strip() if m else None


errors, warnings = [], []
surface_seen = set()
sentences = collections.defaultdict(set)
pages = 0

newsletter = ROOT / "subscribe-to-our-newsletter" / "index.html"
newsletter_live = newsletter.is_file() and any(
    "/search/" not in f for f in re.findall(r"<form\b[^>]*>", newsletter.read_text(errors="ignore")))

for f in sorted(ROOT.rglob("index.html")) + [ROOT / "404.html"]:
    raw = f.read_text(errors="ignore")
    if 'http-equiv="refresh"' in raw or "http-equiv=refresh" in raw:
        continue
    pages += 1
    rel = str(f.relative_to(ROOT))
    p = Text()
    p.feed(raw)
    text = re.sub(r"\s+", " ", "".join(p.out).replace(BREAK, " "))
    # a dated news post keeps its spelling and names; an archived page (front matter archived: true, which
    # its head shows as "kept for the record") stays entirely as published, without repeats or warnings
    archived = bool(re.search(r'\bpage-head__meta\b[^>]*>(?:(?!</p>).)*kept for the record', raw, re.S))
    as_published = archived or "section-news" in p.body_class.split()
    manual = "section-manual" in p.body_class.split()
    for ctx in [] if archived else p.repeats():
        errors.append(f"{rel}: repeated word: …{ctx}…")
    for why, ctx in matches(text, as_published, manual):
        if "struck" in why and rel.startswith("helpsupport/forum/"):
            continue  # the page old forum links land on says that the forum closed
        errors.append(f"{rel}: {why}: …{ctx}…")
    for s in p.surface:
        s = re.sub(r"\s+", " ", s).strip()
        if not s:
            continue
        for why, ctx in matches(s, as_published, manual):
            if "struck" in why and rel.startswith("helpsupport/forum/"):
                continue
            if (why, ctx) not in surface_seen:
                surface_seen.add((why, ctx))
                errors.append(f"{rel}: (title, alt, label or menu) {why}: …{ctx}…")
    if not newsletter_live:
        for href, label in re.findall(r'<a\b[^>]*href="([^"]*subscribe-to-our-newsletter[^"]*)"[^>]*>(.*?)</a>', raw, re.S):
            label = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", label)).strip()
            if re.search(r"\b(subscribe|get notified|notify me)\b", label, re.I):
                errors.append(f"{rel}: “{label}” leads to the newsletter, which has no sign-up form: name an "
                              f"action that exists (News, RSS, Slack) until it has one")

    if archived:
        continue
    for m in re.finditer(HYPE, blank_exempt(text), re.I):
        warnings.append(f"{rel}: hype or stock phrase: …{text[max(0, m.start() - 50): m.end() + 50]}…")
    for sentence in re.split(SENTENCE_END, "".join(p.full)):
        sentence = re.sub(r"\s+", " ", sentence).strip()
        # a sentence inside a link is a card quoting the lead of the page it leads to
        if len(sentence.split()) >= 8 and sentence.endswith((".", "!", "?")) and not any(sentence in re.sub(r"\s+", " ", t) for t in p.linked):
            sentences[sentence].add(rel)
    if p.headings and p.headings[0][0] == 1 and len(p.headings) > 1:
        h1, (_, nxt) = p.headings[0][1], p.headings[1]
        if len(h1) > 3 and h1.casefold() in nxt.casefold():
            warnings.append(f"{rel}: the first heading repeats the h1: “{h1}” → “{nxt}”")
    for para in p.paragraphs:
        if len(re.findall(r"\s[–—]\s", para)) > 2:
            warnings.append(f"{rel}: more than one pair of dashes in a paragraph: {para[:120]}…")

seen = set()   # approved sentences that still repeat (on their pages or not)
for sentence, where in sorted(sentences.items()):
    if len(where) > 1:
        if sentence in REPEATS:
            seen.add(sentence)
            if REPEATS[sentence] == {"/" + w.removesuffix("index.html") for w in where}:
                continue
        shown = ", ".join(sorted(where)[:3]) + (f" and {len(where) - 3} more" if len(where) > 3 else "")
        warnings.append(f"the same sentence on {len(where)} pages ({shown}): {sentence[:140]}")

for sentence in sorted(set(REPEATS) - seen):
    warnings.append(f"REPEATS approves a sentence that no longer repeats; remove it: {sentence[:140]}")

home = ROOT / "index.html"
if home.is_file():
    header = re.search(r"<header\b.*?</header>", home.read_text(errors="ignore"), re.S)
    for href, name in re.findall(r'<a\b[^>]*href="(/[^"]*)"[^>]*>\s*<span class="menu-entry__title"[^>]*>(.*?)</span>',
                                 header.group(0) if header else "", re.S):
        name = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", name))).strip()
        if "#" in href or (href, name) in SHORT_LABELS:
            continue
        h1 = h1_of(href)
        if h1 and h1 != name:
            warnings.append(f"menu: “{name}” leads to {href}, whose h1 is “{h1}”")

for e in errors:
    print(e)
for w in warnings:
    print(f"warning: {w}")
print(f"{pages} pages checked, {len(errors)} problems, {len(warnings)} warnings to review")
sys.exit(1 if errors else 0)
