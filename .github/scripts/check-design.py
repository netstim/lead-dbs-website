#!/usr/bin/env python3
"""Enforces the design tokens in assets/css/*.css; exits with 1 on a violation.

    python3 .github/scripts/check-design.py             (--ratchet lowers the budgets to the counts)

Hard rules (no exceptions without `/* design-exempt: <reason> */` on the same line):
- font-size is a type token var(--t-*), a relative size (em, %), inherit or 0;
- border-radius is a radius token var(--r-*), 0, 50% or inherit;
- font-weight is 400, 500, 600, a var(), inherit or normal (variable-font ranges in @font-face are fine);
- no custom property is defined twice with the same name outside :root/theme blocks for tokens
  (--t-*, --r-*, --s-*): tokens live in base.css and the palette in site.css.

- the size in a `font:` shorthand follows the font-size rule;
- `.btn` is styled in base.css only (one button for the whole site), except the inverted hero pill;
- at most EXEMPT_MAX lines carry `design-exempt:`.

Budgets: the build fails above them AND below them, so a budget is lowered in the same change that removes
literals (it can only go down):
- literal colours (hex, rgb(), hsl()) outside :root / theme blocks;
- `!important`;
- literal px lengths in margin, padding and gap; literal line-height and letter-spacing values.

Only the Python standard library is used.
"""
import pathlib
import re
import sys

BUDGET = {"colour": 152, "important": 72, "spacing": 183, "line-height": 135, "letter-spacing": 43}
EXEMPT_MAX = 6

CSS = sorted(pathlib.Path("assets/css").glob("*.css"))
errors, counts = [], {k: 0 for k in BUDGET}

DECL = re.compile(r"(?<![\w-])(font-size|border-radius|font-weight)\s*:\s*([^;}]+)")
FS_OK = re.compile(r"^(var\(--t-[\w-]+\)|[\d.]+(em|%)|inherit|0)$")
R_OK = re.compile(r"^((var\(--r-[\w-]+\)|0|50%|inherit)\s*)+$")
FW_OK = re.compile(r"^(400|500|600|normal|inherit|var\(--[\w-]+\))$")
COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(rgba?|hsla?)\(")
SPACING = re.compile(r"(?<![\w-])(margin|padding|gap|row-gap|column-gap)(-[a-z-]+)?\s*:\s*([^;}]+)")
TOKEN_DEF = re.compile(r"--(t|r|s)-[\w-]+\s*:")

FONT = re.compile(r"(?<![\w-])font\s*:\s*([^;}]+)")
BTN = re.compile(r"(^|[\s,(>+~])\.btn(--[\w-]+)?\b(?![\w-])")
exempts = 0
for path in CSS:
    in_font_face = False
    selector = ""
    for n, line in enumerate(path.read_text().splitlines(), 1):
        where = f"{path}:{n}"
        exempt = "design-exempt:" in line
        exempts += exempt
        code = re.sub(r"/\*.*?\*/", "", line)
        if "{" in code:
            selector = code.split("{")[0].strip() or selector
        for v in FONT.findall(code):
            size = re.search(r"(?:^|\s)((?:clamp\((?:[^()]|\([^)]*\))*\)|calc\([^)]*\)|var\([^)]*\)|[\d.]+[a-z%]*))\s*(?:/|\s+var\(--font)", v)
            if size and not exempt and not FS_OK.match(size.group(1)):
                errors.append(f"{where}: font size {size.group(1)!r} in a font shorthand is not a type token")
        if path.name != "base.css" and BTN.search(re.sub(r":not\([^)]*\)", "", selector)) and "home-hero" not in selector and not exempt \
                and re.search(r"(?<![\w-])(background|border-radius|height|padding)[\w-]*\s*:", code):
            errors.append(f"{where}: buttons are styled in base.css only ({selector})")
        if "@font-face" in code:
            in_font_face = True
        for prop, value in DECL.findall(code):
            v = value.replace("!important", "").strip()
            if exempt:
                continue
            if prop == "font-size" and not FS_OK.match(v):
                errors.append(f"{where}: font-size {v!r} is not a type token (var(--t-*))")
            if prop == "border-radius" and not R_OK.match(v):
                errors.append(f"{where}: border-radius {v!r} is not a radius token (var(--r-*))")
            if prop == "font-weight" and not FW_OK.match(v) and not in_font_face:
                errors.append(f"{where}: font-weight {v!r}: use 400, 500 or 600")
        if TOKEN_DEF.search(code) and path.name != "base.css":
            errors.append(f"{where}: type, radius and spacing tokens are defined in base.css only")
        in_theme = selector.startswith((":root", "html[data-theme", "[data-theme", ".ground-", "@supports", "@media"))
        if not (in_theme and re.match(r"\s*(:root[^{]*\{)?\s*--", code)):
            counts["colour"] += len(COLOUR.findall(code))
        counts["line-height"] += len(re.findall(r"(?<![\w-])line-height\s*:\s*[\d.]+(px|em|rem)?\s*[;}]", code))
        counts["letter-spacing"] += len(re.findall(r"(?<![\w-])letter-spacing\s*:\s*-?[\d.]+(px|em)", code))
        counts["important"] += code.count("!important")
        for *_, value in SPACING.findall(code):
            counts["spacing"] += len(re.findall(r"(?<![\w.-])\d*\.?\d+px", value))
        if "}" in code:
            in_font_face = False

# the stylesheets must parse: braces balance, no declaration stands outside a rule, no selector list is
# left dangling (a browser drops everything up to the next valid rule, so one slip unstyles the site)
for path in CSS:
    stack, pending, in_comment = [], "", False
    for n, line in enumerate(path.read_text().splitlines(), 1):
        t = line
        if in_comment:
            if "*/" not in t:
                continue
            in_comment, t = False, t.split("*/", 1)[1]
        t = re.sub(r"/\*.*?\*/", "", t)
        if "/*" in t:
            in_comment, t = True, t.split("/*")[0]
        t = re.sub(r"\{\{.*?\}\}", "", t)   # Hugo template actions (site.css is run as a template)
        for part in re.split(r"([{};])", t):
            if part == "{":
                if pending.count("(") != pending.count(")"):
                    errors.append(f"{path}:{n}: unbalanced parentheses in a selector (it swallows the rules after it): {' '.join(pending.split())[:80]!r}")
                stack.append("at" if re.match(r"@(media|supports|container|layer)\b", pending.strip()) else "rule"); pending = ""
            elif part == "}":
                if not stack:
                    errors.append(f"{path}:{n}: a closing brace without its rule")
                else:
                    stack.pop()
                pending = ""
            elif part == ";":
                if (not stack or stack[-1] == "at") and not pending.strip().startswith("@"):
                    errors.append(f"{path}:{n}: a declaration outside any rule: {pending.strip()[:60]!r}")
                pending = ""
            else:
                pending += part
        if pending.strip() and (not stack or stack[-1] == "at") and line.strip() == "" :
            errors.append(f"{path}:{n}: a selector left without its rule: {pending.strip()[:60]!r}")
            pending = ""
    if stack:
        errors.append(f"{path}: {len(stack)} rule(s) not closed")

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
if exempts > EXEMPT_MAX:
    errors.append(f"{exempts} design-exempt lines, more than {EXEMPT_MAX}")

for e in errors:
    print(e)
print(f"{len(CSS)} stylesheets checked, {len(errors)} problems")
sys.exit(1 if errors else 0)
