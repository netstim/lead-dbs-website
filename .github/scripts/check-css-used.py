#!/usr/bin/env python3
"""Fails on CSS selectors that style nothing: a selector (one item of a rule's comma list) is unused
when one of its classes, outside :is()/:where()/:not()/:has(), is used nowhere: not in a built page's class
attribute (arguments: the build folders, production and preview), a template's class attribute or inline
script, or a script in assets/js.

    python3 .github/scripts/check-css-used.py public preview

Delete the selector (or its rule), or use the class again. Only the Python standard library is used.
"""
import pathlib
import re
import sys

root = pathlib.Path(".")
builds = [pathlib.Path(a) for a in sys.argv[1:]] or [pathlib.Path("public")]

# a class counts as used when it is in a built page's class attribute (pass the production and the preview
# build), in a template's class attribute, or in a script's strings (classList, className, markup it builds)
used, prefixes = set(), set()
for build in builds:
    for f in build.rglob("*.html"):
        for c in re.findall(r'class="?([^">]*)', f.read_text(errors="ignore")):
            used.update(c.split())
for f in (root / "layouts").rglob("*.html"):
    t = f.read_text(errors="ignore")
    for script in re.findall(r"<script[^>]*>(.*?)</script>", t, re.S):      # inline scripts set classes too
        for lit in re.findall(r"'([^'\n]*)'|\"([^\"\n]*)\"", script):
            used.update(re.findall(r"[A-Za-z][\w-]*", " ".join(lit)))
    for c in re.findall(r'class="([^"]*)"', t):
        bare = re.sub(r"\{\{.*?\}\}", " ", c)
        used.update(re.findall(r"[A-Za-z][\w-]*", bare))
        used.update(re.findall(r'"([A-Za-z][\w -]*)"', c))           # names inside template actions
        prefixes.update(re.findall(r"([A-Za-z][\w-]*-)\{\{", c))
for f in (root / "assets/js").rglob("*.js"):
    t = f.read_text(errors="ignore")
    for lit in re.findall(r"'([^'\n]*)'|\"([^\"\n]*)\"|`([^`]*)`", t):
        used.update(re.findall(r"[A-Za-z][\w-]*", " ".join(lit)))


def live(cls):
    return cls in used or any(cls.startswith(p) for p in prefixes)


def split_top(s, sep=","):
    """split at sep outside parentheses"""
    out, depth, cur = [], 0, ""
    for ch in s:
        depth += (ch == "(") - (ch == ")")
        if ch == sep and depth == 0:
            out.append(cur); cur = ""
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]


def outside_parens(s):
    out, depth = "", 0
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif depth == 0:
            out += ch
    return out


problems = 0
for css in sorted((root / "assets/css").glob("*.css")):
    text = css.read_text()
    text = re.sub(r"\{\{.*?\}\}", "", text)          # Hugo template actions
    # walk the stylesheet: a prelude is everything since the last { ; or }
    i, line, prelude, start = 0, 1, "", 1
    in_comment = False
    while i < len(text):
        ch = text[i]
        if in_comment:
            if text.startswith("*/", i):
                in_comment = False; i += 2; continue
            line += ch == "\n"; i += 1; continue
        if text.startswith("/*", i):
            in_comment = True; i += 2; continue
        if ch == "{":
            p = " ".join(prelude.split())
            if p and not p.startswith("@") and not re.match(r"^(from|to|\d+%)", p):
                for sel in split_top(p):
                    dead = [c for c in re.findall(r"\.([A-Za-z][\w-]*)", outside_parens(sel)) if not live(c)]
                    if dead:
                        problems += 1
                        print(f"{css}:{start}: nothing uses .{dead[0]} ({sel[:100]})")
            prelude = ""
        elif ch in "};":
            prelude = ""
        else:
            if not prelude.strip():
                start = line
            prelude += ch
        line += ch == "\n"
        i += 1

print(f"{problems} unused selectors")
sys.exit(1 if problems else 0)
