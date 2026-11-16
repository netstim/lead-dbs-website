#!/usr/bin/env python3
"""Lints the Markdown of the manual (content/manual/**/_index.md); exits with 1 on any violation.

    python3 .github/scripts/check-manual.py             (or name files to check only those)

Each violation is printed as `file:line: rule: message`. The house style follows vercel.com/docs: one
h1 (the page title), sentence-case headings, plain Markdown, labelled code, descriptive links and bold
interface labels. The rules and why each exists:

    rule              why
    ----------------  -----------------------------------------------------------------------------------
    heading-h1        the page title is the only h1; a "#" heading in the body is a second one
    heading-skip      a level skipped (## then ####) breaks the outline and screen-reader navigation
    heading-markup    bold, italic, links or HTML in a heading break its anchor and the outline's text
    heading-punct     a heading is a label, not a sentence: no trailing ":", "." or "\\"
    heading-empty     an empty heading has no anchor and no outline entry
    heading-number    numbering ("1. ", "2.1 ") goes stale when sections move; the outline orders them
    heading-caps      ALL-CAPS shouts; only known acronyms (ACRONYMS) are upper case
    heading-case      sentence case: first word capitalised, later words lower case unless a name
    title-case        the front matter `title` and `linkTitle` (sidebar label) follow the same sentence case as headings
    heading-spacing   a heading needs a blank line before and after it, or it can glue onto a list or paragraph
    heading-duplicate two headings with the same text on a page get colliding anchors
    fence-lang        every code fence names its language (FENCE_LANGS) for highlighting and the label
    html-br           <br> is layout in the text; use a paragraph or a list
    raw-html          HTML tags (<ol>, <code>, <a>, <h4>, tables of <li>) are GitBook leftovers; use Markdown
                      (<details>, <summary>, <kbd>, <sub> and <sup> have no Markdown form and are allowed)
    hard-break        a trailing backslash glues paragraphs together; use a blank line
    trailing-space    trailing whitespace is an invisible hard break in Markdown
    blank-lines       two or more blank lines in a row are noise in the source
    raw-anchor        <a id/name=…> anchors are GitBook leftovers; headings carry their own anchors
    escape            `\\_` outside code is an import leftover; Markdown does not need it mid-word
    image-alt         every image needs alt text for screen readers and when it fails to load
    bare-url          a raw address (<https://…>, plain text or as its own link text) is not link text
    link-here         "here" / "click here" / "this link" tell the reader nothing out of context
    please            instructions are direct; "please" adds length, not politeness
    caps-emphasis     ALL-CAPS emphasis (NOT, IMPORTANT) shouts; use bold or rephrase
    note-indent       a {{% manual-note %}} must start at the line's first column; indented inside a list item it
                      breaks the list's HTML
    note-that         a note block already says "note"; don't open it with "Note that" / "Note:"
    click-on          "click on" is wordy and mouse-specific; write "select" (or "click")
    latin-abbr        "e.g." / "i.e." read poorly and translate badly; write "for example" / "that is"
    gui-code          inline code is for code, commands, files and paths; interface labels are **bold**

A line can opt out of one rule with `<!-- lint-ignore rule -->` on it (several rules: separated by
spaces). Text inside fenced code, inline code, HTML comments and shortcode delimiters is not prose.

Only the Python standard library is used.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("content/manual")

FENCE_LANGS = {"matlab", "python", "bash", "batch", "text", "json"}

# Upper-case words that are not shouting.
ACRONYMS = {
    "AC", "ACPC", "AI", "ANT", "ANTS", "ANTs", "API", "BIDS", "CL", "CPU", "CSF", "CT", "DBS", "DICOM", "DTI",
    "DWI", "ECOG", "FA", "FAQ", "FSL", "FTP", "GB", "GPI", "GPU", "GUI", "HCP", "ID", "LFP", "MER", "MNI",
    "MRI", "NIFTI", "OR", "OSS", "PAM", "PC", "PET", "PPN", "RAM", "ROI", "SEEG", "SPM", "STN", "SWI", "TRAC",
    "CORE", "URL", "UI", "VAT", "VTA", "VIM", "VIM", "XML", "JSON", "MAT", "PNG", "SVG", "NII", "CSV", "HTML",
    "USB", "OS", "PDF", "FEM", "TPM", "DARTEL", "SyN", "ANAT", "GM", "WM", "STL", "TMS", "DMRI", "FMRI",
    "MRTRIX", "QSI", "QSIPREP", "GQI", "FMRIPREP", "MP2RAGE", "FLAIR", "PD", "IIT", "IXI", "ICBM", "ET",
    "OCD", "PD", "TS", "MD", "EEG", "MEG", "STIM", "VTK", "MATLAB", "BRAINSFIT", "PACER", "TOR", "HD",
    "RMS", "SNR", "NA", "II", "III", "IV", "SSD", "LG", "BS", "TOC", "SDK", "CLI", "ROIS", "GM", "SFN",
    "CC", "NAN", "NB", "VA", "XYZ", "RAS", "LPS", "RPI", "LAS", "MG", "LTS", "AWS", "UK", "USA", "EU",
}
# Names that keep their capitals inside a sentence-case heading (multi-word names first).
PROPER = [
    "Lead-DBS", "Lead Group", "Lead Connectome Mapper", "Lead Connectome", "Lead Mapper", "Lead-OR",
    "Lead-Tutor", "Lead Tutor", "Lead Suite", "Lead Neuroimaging Suite", "3D Slicer", "Fiber Filtering Explorer",
    "Fiberfiltering Explorer", "Network Mapping Explorer", "Sweetspot Explorer", "Sweetspot Explorer",
    "Discriminative Fibertracts", "Sweet-sour", "Python", "MATLAB", "Matlab", "Slicer", "SlicerNetstim",
    "Windows", "macOS", "Linux", "Ubuntu", "GitHub", "GitBook", "Git", "Fortran", "Docker", "Apple",
    "Intel", "Silicon", "Homebrew", "Xcode", "Anaconda", "Miniconda", "Conda", "SimBio", "FieldTrip",
    "Brainstorm", "MRtrix", "DSI Studio", "Studio", "FreeSurfer", "Freesurfer", "NIfTI", "LeGUI", "PaCER",
    "TRAC/CORE", "OSS-DBS", "SimNIBS", "Horn", "Schönecker", "Medtronic", "Boston", "Scientific", "Abbott",
    "St. Jude", "PyPI", "Mac", "Rosetta", "ITK", "ITK-SNAP", "Excel", "Zenodo", "Neuromodulation", "MNI",
    "Allen", "DISTAL", "Elvis", "Surfice", "OpenEphys", "Brainhack", "Ewert", "Kalman", "Hamani", "BrainSuite", "SPM12", "Elastix", "Cerebellum",
]
FIRST_LOWER_OK = {"dMRI", "fMRI", "fMRI-analysis", "sEEG", "ea_", "iOS", "macOS", "x", "y", "z"}

# GitBook leftovers and style words in prose.
CAPS_EMPHASIS = {"NOT", "IMPORTANT", "NOTE", "WARNING", "MUST", "ALWAYS", "NEVER", "ONLY", "DO", "DON'T",
                 "ALL", "NO", "CAUTION", "ATTENTION", "VERY", "BEFORE", "AFTER", "EACH", "ANY", "SHOULD"}

RULE_WORDS = [
    (re.compile(r"\bplease\b", re.I), "please", 'drop "please"; write the instruction directly'),
    (re.compile(r"\bclick(?:ing|ed|s)? on\b", re.I), "click-on", 'write "select" (or "click") instead of "click on"'),
    (re.compile(r"\be\.\s?g\.|\bi\.\s?e\.", re.I), "latin-abbr", 'write "for example" / "that is"'),
]

HEADING = re.compile(r"^(#{1,6})(?:\s+(.*?))?\s*$")
FENCE = re.compile(r"^\s*(```+|~~~+)\s*([^\s`{]*)")
INLINE_CODE = re.compile(r"(`+)(.+?)\1")
COMMENT = re.compile(r"<!--.*?-->")
SHORTCODE = re.compile(r"\{\{[<%].*?[%>]\}\}")
IGNORE = re.compile(r"<!--\s*lint-ignore\s+([\w\s-]+?)\s*-->")
ATTR = re.compile(r"\s*\{#[\w-]+\}\s*$")
LINK = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]*)(?:\s+\"[^\"]*\")?\)")
URL = re.compile(r"https?://[^\s)>\]]+")


def mask_code(text):
    """The line with inline code replaced by spaces of the same length (columns stay put)."""
    return INLINE_CODE.sub(lambda m: " " * len(m.group(0)), text)


def name_spans(text):
    """The (start, end) spans of the known names (PROPER) in the text."""
    spans = []
    for name in PROPER:
        for m in re.finditer(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])", text):
            spans.append(m.span())
    return spans


def is_acronym(word):
    core = word.strip("()[],;:'\"/")
    if not core:
        return True
    if core.upper().rstrip("S") in ACRONYMS or core.upper() in ACRONYMS or core in ACRONYMS:
        return True
    if re.fullmatch(r"[A-Z]+\d+[A-Za-z]*|\d+[A-Za-z]+", core):   # T1, MP2RAGE, 3D, 2D
        return True
    if re.fullmatch(r"[A-Z]", core):                             # single letters (axis, option)
        return True
    return False


WORD = re.compile(r"[A-Za-zÀ-ÿ][\w'’À-ÿ.+-]*")


def case_problems(text):
    """Sentence-case problems in a heading or title: a list of (rule, message)."""
    out = []
    plain = re.sub(r"`[^`]*`", lambda m: " " * len(m.group(0)), text)
    words = list(WORD.finditer(plain))
    if not words:
        return out
    first = words[0].group(0)
    if first[0].islower() and first not in FIRST_LOWER_OK and not first.startswith("ea_"):
        out.append(("heading-case", f'capitalise the first word "{first}"'))
    names = name_spans(plain)
    for i, m in enumerate(words):
        core = m.group(0).strip(".'’-+")
        for part in core.split("-"):
            if re.fullmatch(r"[A-Z]{2,}[A-Z'’]*", part) and not is_acronym(part):
                out.append(("heading-caps", f'"{part}" in capitals (add it to ACRONYMS if it is one)'))
        if i == 0 or any(a <= m.start() < b for a, b in names):
            continue
        for part in core.split("-"):
            part = part.strip(".'’+")
            if re.fullmatch(r"[A-Z][a-zà-ÿ'’]+", part):
                out.append(("heading-case", f'"{part}" should be lower case (sentence case) unless it is a name in PROPER'))
    return out


def lint(path):
    problems = []
    rel = path.as_posix()
    lines = path.read_text(encoding="utf-8").split("\n")

    def report(n, rule, message, line=""):
        ignored = IGNORE.search(line)
        if ignored and rule in ignored.group(1).split():
            return
        problems.append(f"{rel}:{n}: {rule}: {message}")

    # front matter (JSON between --- fences, or YAML/TOML: only the title is read)
    start = 0
    if lines and lines[0].strip() == "---":
        end = lines.index("---", 1)
        block = "\n".join(lines[1:end])
        try:
            meta = json.loads(block)
        except ValueError:
            m = re.search(r'^title:\s*"?(.*?)"?\s*$', block, re.M)
            meta = {"title": m.group(1)} if m else {}
        for key in ("title", "linkTitle"):
            if meta.get(key):
                n = next((i + 1 for i, l in enumerate(lines[:end]) if f'"{key}"' in l or l.startswith(key)), 1)
                for rule, message in case_problems(meta[key]):
                    report(n, "title-case", f"{key}: {message}")
        start = end + 1

    in_fence = None
    in_comment = False
    blank_run = 0
    last_level = 1
    seen = {}
    note_open = False
    for i in range(start, len(lines)):
        n = i + 1
        line = lines[i]

        if in_fence:
            if re.match(r"^\s*" + re.escape(in_fence) + r"\s*$", line):
                in_fence = None
            continue
        m = FENCE.match(line)
        if m:
            in_fence = m.group(1)
            lang = m.group(2).lower()
            if lang not in FENCE_LANGS:
                report(n, "fence-lang", f"code fence language {lang or '(none)'!r} is not one of {', '.join(sorted(FENCE_LANGS))}", line)
            blank_run = 0
            continue

        if line != line.rstrip():
            report(n, "trailing-space", "trailing whitespace", line)
        if not line.strip():
            blank_run += 1
            if blank_run == 2:
                report(n, "blank-lines", "two or more blank lines in a row", line)
            continue
        blank_run = 0

        # HTML comments spanning lines are not prose
        text = line
        if in_comment:
            if "-->" not in text:
                continue
            text = text.split("-->", 1)[1]
            in_comment = False
        text = COMMENT.sub(" ", text)
        if "<!--" in text:
            text = text.split("<!--", 1)[0]
            in_comment = True

        prose = SHORTCODE.sub(" ", mask_code(text))

        if re.match(r"\s+\{\{%\s*/?manual-note", line):
            report(n, "note-indent", "indented note shortcode; start it at the first column, outside the list", line)
        if re.search(r"\{\{%\s*manual-note", line):
            note_open = True
            continue
        if note_open:
            note_open = False
            if re.match(r"\s*(\*\*)?(please )?note(\*\*)?( that\b|:|\*\*:)", prose, re.I):
                report(n, "note-that", 'the block is a note already; drop "Note that" / "Note:"', line)

        h = HEADING.match(line)
        if h:
            level, body = len(h.group(1)), (h.group(2) or "").strip()
            if i > start and lines[i - 1].strip() and i - 1 > start:
                report(n, "heading-spacing", "no blank line before the heading", line)
            if i + 1 < len(lines) and lines[i + 1].strip():
                report(n, "heading-spacing", "no blank line after the heading", line)
            body_no_attr = ATTR.sub("", body)
            if level == 1:
                report(n, "heading-h1", "the page title is the only h1; use ## or lower", line)
            elif level > last_level + 1:
                report(n, "heading-skip", f"h{level} after h{last_level}; do not skip levels", line)
            last_level = level
            if not re.sub(r"[\W_]", "", body_no_attr):
                report(n, "heading-empty", "empty heading", line)
                continue
            if re.search(r"\*|(?<![\w])_|_(?![\w])|<[a-zA-Z/]|\]\(", mask_code(body_no_attr)):
                report(n, "heading-markup", "bold, italic, link or HTML in a heading", line)
            if re.search(r"[:.\\]$", body_no_attr):
                report(n, "heading-punct", "trailing punctuation in a heading", line)
            if re.match(r"(\d+(\.\d+)*\.?|[A-Za-z]\.|[IVX]+\.)\s", body_no_attr):
                report(n, "heading-number", "numbered heading; let the outline order sections", line)
            for rule, message in case_problems(body_no_attr):
                report(n, rule, message, line)
            key = re.sub(r"\W+", " ", body_no_attr.replace("`", "").lower()).strip()
            if key in seen:
                report(n, "heading-duplicate", f"same heading as line {seen[key]}; anchors collide", line)
            else:
                seen[key] = n
            continue

        if re.search(r"<br\s*/?>", prose, re.I):
            report(n, "html-br", "<br> in the text; use a paragraph or a list", line)
        for tag in re.findall(r"</?([a-zA-Z][\w-]*)(?=[\s>/])", prose):
            if tag.lower() not in {"details", "summary", "kbd", "sub", "sup", "br"}:
                report(n, "raw-html", f"<{tag.lower()}> in the text; use Markdown", line)
                break
        if re.search(r"(?<!\\)\\$", line) and not line.lstrip().startswith("|"):
            report(n, "hard-break", "trailing backslash line break; use a blank line (a new paragraph)", line)
        if re.search(r"<a\s+(id|name)=", prose, re.I):
            report(n, "raw-anchor", "raw <a id> anchor; a heading has its own anchor", line)
        if "\\_" in prose:
            report(n, "escape", r"unneeded \_ escape outside code", line)

        for link in LINK.finditer(prose):
            bang, label, target = link.groups()
            if bang:
                if not label.strip():
                    report(n, "image-alt", "image without alt text", line)
                continue
            label_plain = label.strip().strip("*_ ").lower()
            if label_plain in {"here", "click here", "this link", "link", "this", "this page", "in here"}:
                report(n, "link-here", f'link text "{label.strip()}" says nothing; name the destination', line)
            if URL.fullmatch(label.strip().strip("*_<>")) or re.fullmatch(r"(www\.)?[\w-]+(\.[\w-]+)+(/\S*)?", label.strip()):
                report(n, "bare-url", "an address as link text; describe the destination", line)
        # images first, so a linked image [![alt](img.png)](https://…) leaves an ordinary link
        outside_links = LINK.sub(" ", re.sub(r"!\[[^\]]*\]\([^)]*\)", "image", prose))
        outside_links = re.sub(r"<(https?://[^>]+)>", lambda m: "BAREURL", outside_links)
        if "BAREURL" in outside_links or URL.search(re.sub(r"<[^>]+>", " ", outside_links)):
            report(n, "bare-url", "a raw address in the text; make it a link with descriptive text", line)

        for pattern, rule, message in RULE_WORDS:
            if pattern.search(prose):
                report(n, rule, message, line)
        for word in re.findall(r"(?<![\w-])[A-Z][A-Z'’]+(?![\w-])", LINK.sub(lambda m: m.group(2), prose)):
            if word in CAPS_EMPHASIS:
                report(n, "caps-emphasis", f'"{word}" in capitals; use **bold** or rephrase', line)

        for code in INLINE_CODE.finditer(COMMENT.sub(" ", text)):
            inner = code.group(2).strip()
            words = inner.split()
            if (len(words) > 1 and not re.search(r"[/._()=\\:;\[\]{}<>$@#|*'\"]", inner)
                    and all(re.match(r"[A-Z0-9&+-]", w) for w in words)
                    and any(re.match(r"[A-Z][a-z]", w) for w in words)):
                report(n, "gui-code", f'interface label `{inner}` in code; write it **bold**', line)

    return problems


def main():
    files = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(ROOT.glob("**/_index.md"))
    problems = []
    for path in files:
        problems += lint(path)
    for p in problems:
        print(p)
    print(f"{len(files)} manual pages checked, {len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
