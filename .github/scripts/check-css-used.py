#!/usr/bin/env python3
"""Fails on CSS selectors that style nothing: a selector (one item of a rule's comma list) is unused
when one of its classes, outside :is()/:where()/:not()/:has(), is used nowhere: not in a built page's class
attribute (arguments: the build folders, production and preview), a template's class attribute, or a
script (inline in a template, or in assets/js) that sets or looks for it: classList.add/remove/toggle/
contains/replace, className or setAttribute('class', …), class="…" in markup the script builds, and
querySelector(All)/closest/matches selectors. Any other string in a script does not count, so a log
message or a key that happens to spell a class name does not keep a dead rule alive.

    python3 .github/scripts/check-css-used.py public preview

Delete the selector (or its rule), or use the class again. Only the Python standard library is used.
"""
import pathlib
import re
import sys

root = pathlib.Path(".")
builds = [pathlib.Path(a) for a in sys.argv[1:]] or [pathlib.Path("public")]

STRING = r"'(?:[^'\\\n]|\\.)*'|\"(?:[^\"\\\n]|\\.)*\"|`(?:[^`\\]|\\.)*`"
NAME = r"[A-Za-z][\w-]*"


def args(js, start):
    """The text of a call's arguments: from start (just after its opening parenthesis) to the
    parenthesis that closes it, skipping parentheses inside strings."""
    depth, i = 1, start
    while i < len(js) and depth:
        m = re.compile(STRING).match(js, i)
        if m:
            i = m.end(); continue
        depth += (js[i] == "(") - (js[i] == ")")
        i += 1
    return js[start:i - 1]


def literals(text):
    """The contents of the string literals in text, template literals without their ${…} parts."""
    return [re.sub(r"\$\{[^}]*\}", " ", m.group(0)[1:-1]) for m in re.finditer(STRING, text)]


def script_classes(js):
    """The class names a script sets or looks for."""
    found = set()
    # classList.add('a', 'b'), .toggle('a', on), .replace('a', 'b'), setAttribute('class', 'a b')
    for m in re.finditer(r"\.classList\s*\.\s*(?:add|remove|toggle|contains|replace)\s*\(|\.setAttribute\s*\(\s*['\"]class['\"]\s*,", js):
        for lit in literals(args(js, m.end()) if m.group(0).endswith("(") else js[m.end():js.find(")", m.end())]):
            found.update(re.findall(NAME, lit))
    # el.className = 'a b' (or +=), up to the end of the statement
    for m in re.finditer(r"\.className\s*\+?=(?!=)", js):
        end = re.compile(r";|\n").search(js, m.end())
        for lit in literals(js[m.end():end.start() if end else len(js)]):
            found.update(re.findall(NAME, lit))
    # class="…" in markup a script builds (innerHTML, template literals)
    for m in re.finditer(r"\bclass=\\?([\"'])((?:(?!\1)[^\\])*)", re.sub(r"\$\{[^}]*\}", " ", js)):
        found.update(re.findall(NAME, m.group(2)))
    # selectors: querySelector('.a .b'), closest('.a'), matches('.a')
    for m in re.finditer(r"\.(?:querySelector(?:All)?|closest|matches)\s*\(", js):
        for lit in literals(args(js, m.end())):
            found.update(re.findall(r"\.(" + NAME + ")", lit))
    return found


# a class counts as used when it is in a built page's class attribute (pass the production and the preview
# build), in a template's class attribute, or in what a script sets or looks for (script_classes)
used, prefixes = set(), set()
for build in builds:
    for f in build.rglob("*.html"):
        for c in re.findall(r'class="?([^">]*)', f.read_text(errors="ignore")):
            used.update(c.split())
for f in (root / "layouts").rglob("*.html"):
    t = f.read_text(errors="ignore")
    for script in re.findall(r"<script[^>]*>(.*?)</script>", t, re.S):      # inline scripts set classes too
        used.update(script_classes(script))
    for c in re.findall(r'class="([^"]*)"', t):
        bare = re.sub(r"\{\{.*?\}\}", " ", c)
        used.update(re.findall(r"[A-Za-z][\w-]*", bare))
        used.update(re.findall(r'"([A-Za-z][\w -]*)"', c))           # names inside template actions
        prefixes.update(re.findall(r"([A-Za-z][\w-]*-)\{\{", c))
for f in (root / "assets/js").rglob("*.js"):
    used.update(script_classes(f.read_text(errors="ignore")))


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
