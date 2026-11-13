#!/usr/bin/env python3
"""Enforces the design tokens in assets/css/*.css; exits with 1 on a violation.

    python3 .github/scripts/check-design.py             (--ratchet lowers the budgets to the counts)

Each stylesheet is read once into declarations, each with its property, its value, the selector of the rule
it is in and the @-rules around it (comments removed, a declaration may span lines). The rules below apply
to those declarations, so a shorthand, a longhand or a declaration over several lines is checked like any
other, and a commented-out declaration is not checked at all.

Hard rules (no exceptions without `/* design-exempt: <reason> */` on a line of the declaration):
- font-size, and the size in a `font:` shorthand, is a type token var(--t-*), a relative size (em, %),
  inherit or 0;
- font-family uses a named --font-* token or inherits (except @font-face declarations);
- font shorthands also use a named --font-* family token or inherit;
- border-radius and its longhands (border-top-left-radius, border-start-end-radius, …) are a radius token
  var(--r-*), 0, 50% or inherit;
- font-weight, and the weight in a `font:` shorthand, is 400, 500, 600, a var(), inherit or normal
  (variable-font ranges in @font-face are fine);
- type, radius and spacing tokens (--t-*, --r-*, --s-*) are defined in base.css only, and there in a :root
  rule only, so no component can set its own size under a token's name;
- `.btn` is styled in base.css only (one button for the whole site), except the inverted hero pill;
- at most EXEMPT_MAX lines carry `design-exempt:`.

Budgets: the build fails above them AND below them, so a budget is lowered in the same change that removes
literals (it can only go down):
- literal colours (hex, rgb(), hsl(), and named colours such as `red`) outside the palette, that is
  outside custom properties set in :root, [data-theme] and .ground-* rules;
- `!important`;
- literal px lengths in margin, padding and gap; literal line-height and letter-spacing values.

The stylesheets must also parse: braces balance, no declaration stands outside a rule, no selector list is
left dangling (a browser drops everything up to the next valid rule, so one slip unstyles the site).

Only the Python standard library is used.
"""
import pathlib
import re
import sys

BUDGET = {"colour": 146, "important": 35, "spacing": 177, "line-height": 131, "letter-spacing": 42}
EXEMPT_MAX = 6
# hard-rule violations the stylesheets already had when this script began to read whole declarations (the
# line-by-line reading missed them): "file: selector property". Each is allowed until it is fixed, and then
# has to go from this list, like a budget.
KNOWN = {
    "site.css: .btn height",          # the phone's wrapping button (@media (max-width: 639px))
    "site.css: .btn padding-block",
}

CSS = sorted(pathlib.Path("assets/css").glob("*.css"))
errors, counts = [], {k: 0 for k in BUDGET}

if not CSS:
    # nothing read means nothing counted: a ratchet would set every budget to 0
    print("no stylesheets in assets/css: run this from the repository's root")
    sys.exit(2)

FS_OK = re.compile(r"^(var\(--t-[\w-]+\)|[\d.]+(em|%)|inherit|0)$")
R_OK = re.compile(r"^((var\(--r-[\w-]+\)|0|50%|inherit)\s*/?\s*)+$")
FW_OK = re.compile(r"^(400|500|600|normal|inherit|var\(--[\w-]+\))$")
RADIUS = re.compile(r"^border(-(top|bottom|start|end)-(left|right|start|end))?-radius$")
SPACING = re.compile(r"^(margin|padding|gap|row-gap|column-gap)(-[a-z-]+)?$")
TOKEN = re.compile(r"^--(t|r|s)-[\w-]+$")
THEME = (":root", "html[data-theme", "[data-theme", ".ground-")
BTN = re.compile(r"(^|[\s,(>+~])\.btn(--[\w-]+)?\b(?![\w-])")
HEX_FN = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?)\(")
NAMED = re.compile(r"(?<![\w-])(" + "|".join("""
    aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet brown
    burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
    darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid
    darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet
    deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro
    ghostwhite gold goldenrod gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki
    lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan lightgoldenrodyellow
    lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen lightskyblue lightslategray
    lightslategrey lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine
    mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen mediumturquoise
    mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite navy oldlace olive olivedrab
    orange orangered orchid palegoldenrod palegreen paleturquoise palevioletred papayawhip peachpuff peru
    pink plum powderblue purple rebeccapurple red rosybrown royalblue saddlebrown salmon sandybrown
    seagreen seashell sienna silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
    teal thistle tomato turquoise violet wheat white whitesmoke yellow yellowgreen""".split()) + r")(?![\w-])", re.I)
# properties whose values are names, not colours ("tan" may name an animation, "white" a grid area)
NOT_COLOUR = re.compile(r"^(font(-family)?|grid(-[a-z-]+)?|animation(-name)?|transition(-property)?|will-change|"
                        r"counter-[a-z]+|content|quotes|container(-name)?|view-transition-name|list-style-type|"
                        r"anchor-name|position-anchor)$")
FONT_KEYWORDS = {"normal", "italic", "oblique", "small-caps", "bold", "bolder", "lighter", "ultra-condensed",
                 "extra-condensed", "condensed", "semi-condensed", "semi-expanded", "expanded", "extra-expanded",
                 "ultra-expanded"}
FONT_WHOLE = {"inherit", "initial", "unset", "revert", "revert-layer", "caption", "icon", "menu", "message-box",
              "small-caption", "status-bar"}


def blank(m):
    """The matched text as spaces, keeping its line breaks (so line numbers stay right)."""
    return re.sub(r"[^\n]", " ", m.group(0))


def split_top(value):
    """The value's parts, split at spaces outside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch.isspace() and depth == 0:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    return out + ([cur] if cur else [])


def font_parts(value):
    """The weight and the size of a `font:` shorthand (either may be None)."""
    parts = split_top(value)
    if value in FONT_WHOLE or len(parts) < 2:
        return None, None   # a whole font from elsewhere (a system font, inherit, a var())
    # the family is the last part, or starts at the first name ("Inter", Arial, sans-serif,)
    family = next((i for i, p in enumerate(parts) if p[0] in "\"'"
                   or re.fullmatch(r"[A-Za-z][\w-]*,?", p) and p.lower() not in FONT_KEYWORDS), len(parts) - 1)
    before = parts[:family]
    if not before:
        return None, None
    # the part just before the family is the size (with its /line-height); a weight comes before it
    size = re.split(r"/(?![^(]*\))", before[-1])[0]
    weight = next((p for p in before[:-1] if re.fullmatch(r"\d{1,4}|bolder|lighter|var\([^)]*\)", p)), None)
    return weight, size


def parse(path):
    """The declarations of one stylesheet, as dicts, and the problems that keep it from parsing.

    Template actions ({{ … }}, site.css is run as a Hugo template), comments and strings are blanked out
    first; a comment that says design-exempt: marks its lines."""
    text = path.read_text()
    exempt_lines, marks = set(), set()
    problems = []

    def comment(m):
        if "design-exempt:" in m.group(0):
            first = text.count("\n", 0, m.start()) + 1
            marks.add(first)
            exempt_lines.update(range(first, first + m.group(0).count("\n") + 1))
        return blank(m)

    code = re.sub(r"\{\{.*?\}\}", blank, text, flags=re.S)
    # comments and strings in one pass, so a "/*" inside a string or a quote inside a comment is read as
    # what it is; a string keeps its quotes (a font family stays recognisable as one)
    out, i = [], 0
    for m in re.finditer(r"/\*.*?(?:\*/|\Z)|\"(?:[^\"\\\n]|\\.)*\"|'(?:[^'\\\n]|\\.)*'", code, re.S):
        out.append(code[i:m.start()])
        if m.group(0).startswith("/*"):
            if not m.group(0).endswith("*/"):
                problems.append(f"{path}:{code.count(chr(10), 0, m.start()) + 1}: a comment that is never closed")
            out.append(comment(m))
        else:
            out.append(m.group(0)[0] + " " * (len(m.group(0)) - 2) + m.group(0)[-1])
        i = m.end()
    out.append(code[i:])
    code = "".join(out)

    decls, stack, start = [], [], 0   # stack: (kind, prelude), kind "at" or "rule"
    line_of = lambda pos: code.count("\n", 0, pos) + 1
    for m in re.finditer(r"[{};]", code):
        seg, pos = code[start:m.start()], m.start()
        s = " ".join(seg.split())
        first = line_of(start + len(seg) - len(seg.lstrip()))
        if m.group(0) == "{":
            if s.count("(") != s.count(")"):
                problems.append(f"{path}:{first}: unbalanced parentheses in a selector (it swallows the rules after it): {s[:80]!r}")
            if re.search(r"\n[ \t]*\n", seg.strip()) and not s.startswith("@"):
                problems.append(f"{path}:{first}: a selector left without its rule: {seg.strip().splitlines()[0][:60]!r}")
            stack.append(("at" if s.startswith("@") else "rule", s))
        elif s:
            # declarations stand in a style rule or in an @-rule that holds them directly (@font-face)
            in_rule = stack and (stack[-1][0] == "rule"
                                 or re.match(r"@(font-face|page|property|counter-style|font-palette-values)\b", stack[-1][1]))
            if ":" not in s or not in_rule:
                if not (s.startswith("@") and m.group(0) == ";"):
                    problems.append(f"{path}:{first}: a declaration outside any rule: {s[:60]!r}")
            else:
                prop, value = s.split(":", 1)
                prop, value = prop.strip(), value.strip()
                important = bool(re.search(r"!\s*important\s*$", value, re.I))
                value = re.sub(r"\s*!\s*important\s*$", "", value, flags=re.I)
                last = line_of(pos)
                rules = [p for k, p in stack if k == "rule"]
                decls.append({
                    "where": f"{path}:{first}", "file": path.name, "prop": prop if prop.startswith("--") else prop.lower(),
                    "value": value, "important": important, "selector": rules[-1] if rules else "",
                    "at": [p for k, p in stack if k == "at"],
                    "exempt": any(n in exempt_lines for n in range(first, last + 1)),
                })
        if m.group(0) == "}":
            if not stack:
                problems.append(f"{path}:{line_of(pos)}: a closing brace without its rule")
            else:
                stack.pop()
        start = m.end()
    if code[start:].strip():
        problems.append(f"{path}:{line_of(start)}: a selector left without its rule: {code[start:].strip()[:60]!r}")
    if stack:
        problems.append(f"{path}: {len(stack)} rule(s) not closed")
    return decls, problems, len(marks)


exempts = 0
seen = set()


def rule(d, message):
    """A hard-rule violation, unless it is a known one (KNOWN)."""
    key = f"{d['file']}: {d['selector']} {d['prop']}"
    if key in KNOWN:
        seen.add(key)
    else:
        errors.append(f"{d['where']}: {message}")


for path in CSS:
    decls, problems, n_exempt = parse(path)
    errors += problems
    exempts += n_exempt
    for d in decls:
        prop, v, where, sel = d["prop"], d["value"], d["where"], d["selector"]
        in_font_face = any(a.startswith("@font-face") for a in d["at"])
        if not d["exempt"]:
            if prop == "font-size" and not FS_OK.match(v):
                rule(d, f"font-size {v!r} is not a type token (var(--t-*))")
            if RADIUS.match(prop) and not R_OK.match(v):
                rule(d, f"{prop} {v!r} is not a radius token (var(--r-*))")
            if prop == "font-weight" and not FW_OK.match(v) and not in_font_face:
                rule(d, f"font-weight {v!r}: use 400, 500 or 600")
            if prop == "font-family" and not in_font_face and not re.fullmatch(r"var\(--font-[\w-]+\)|inherit", v):
                rule(d, f"font-family {v!r}: use a named font token (var(--font-*)) or inherit")
            if prop == "font":
                if v != "inherit" and not re.search(r"var\(--font-[\w-]+\)$", v):
                    rule(d, f"font family in {v!r}: use a named font token (var(--font-*))")
                weight, size = font_parts(v)
                if size and not FS_OK.match(size):
                    rule(d, f"font size {size!r} in a font shorthand is not a type token")
                if weight and not FW_OK.match(weight):
                    rule(d, f"font weight {weight!r} in a font shorthand: use 400, 500 or 600")
            if path.name != "base.css" and BTN.search(re.sub(r":not\([^)]*\)", "", sel)) and "home-hero" not in sel \
                    and re.match(r"(background|border-radius|height|padding)", prop):
                rule(d, f"buttons are styled in base.css only ({sel})")
        if TOKEN.match(prop) and (path.name != "base.css" or not sel.startswith(":root")):
            rule(d, f"{prop}: type, radius and spacing tokens are defined in base.css's :root only ({sel or 'outside a rule'})")
        palette = prop.startswith("--") and sel.startswith(THEME)
        if not palette:
            counts["colour"] += len(HEX_FN.findall(v))
            if not NOT_COLOUR.match(prop):
                bare = re.sub(r"var\([^)]*\)|url\([^)]*\)|[\"'][^\"']*[\"']", " ", v)
                counts["colour"] += len(NAMED.findall(bare))
        if prop == "line-height" and re.fullmatch(r"[\d.]+(px|em|rem)?", v):
            counts["line-height"] += 1
        if prop == "letter-spacing" and re.match(r"-?[\d.]+(px|em)", v):
            counts["letter-spacing"] += 1
        counts["important"] += d["important"]
        if SPACING.match(prop):
            counts["spacing"] += len(re.findall(r"(?<![\w.-])\d*\.?\d+px", v))

# Manual articles use shared components; presentation cannot bypass token lint
# through a one-off style attribute or style block in Markdown/templates.
manual_sources = list(pathlib.Path("content/manual").rglob("*.md"))
manual_sources += list(pathlib.Path("layouts/_partials").glob("manual-*.html"))
manual_sources += list(pathlib.Path("layouts/_shortcodes").glob("manual-*.html"))
manual_sources += [pathlib.Path(name) for name in (
    "layouts/manual.html", "layouts/_markup/render-codeblock.html")]
for path in manual_sources:
    if not path.exists():
        continue
    source = path.read_text()
    if path.suffix == ".md":
        source = re.sub(r"(?ms)^```[^\n]*\n.*?^```[ \t]*$", "", source)
        source = re.sub(r"`[^`\n]+`", "", source)
    if re.search(r"<style(?:\s|>)|<[^>]+\sstyle\s*=", source, re.I):
        errors.append(f"{path}: manual presentation belongs in shared CSS, not inline styles")

if "--ratchet" in sys.argv:
    # lower each budget to its count (never raise one), then check as usual
    src = pathlib.Path(__file__).read_text()
    for key, limit in BUDGET.items():
        if counts[key] < limit:
            src = re.sub(rf'("{re.escape(key)}": )\d+', rf"\g<1>{counts[key]}", src)
            BUDGET[key] = counts[key]
    pathlib.Path(__file__).write_text(src)

for key, limit in BUDGET.items():
    if counts[key] > limit:
        errors.append(f"{counts[key]} {key} literals, over the budget of {limit}: use a token")
    elif counts[key] < limit:
        errors.append(f"{key} literals are down to {counts[key]}: lower BUDGET[{key!r}] to {counts[key]} in {__file__}")
for key in sorted(KNOWN - seen):
    errors.append(f"{key} is fixed: remove it from KNOWN in {__file__}")
if exempts > EXEMPT_MAX:
    errors.append(f"{exempts} design-exempt lines, more than {EXEMPT_MAX}")

for e in errors:
    print(e)
print(f"{len(CSS)} stylesheets checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
