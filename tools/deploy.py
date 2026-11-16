#!/usr/bin/env python3
"""Puts the Hugo build into the web root of www.lead-dbs.org beside WordPress, and takes it out again.

NOT RUN AGAINST THE LIVE SERVER YET. docs/launch.md says when and by whom. Every command works on a folder
path. Run it on the server (over SSH) or on a mounted copy. tests/test_launch_server.py runs it against a
fake web root on this machine.

    tools/deploy.py package [--out dist]                build, check and pack one commit (on any computer)
    tools/deploy.py plan     SITE WEBROOT --state DIR    say what deploy would do, change nothing
                             [--inventory FILE]          ... and write the file lists for a deploy by hand
    tools/deploy.py deploy   SITE WEBROOT --state DIR    put the site in place (after a plan)
                             [--grace-days N]            keep replaced fingerprinted files N days (default 7)
    tools/deploy.py rollback WEBROOT --state DIR         take the site out again, restore what it replaced
    tools/deploy.py csp      BUILD                       print the policy package would give BUILD's pages

SITE is the site/ folder of an unpacked package (the build and its .htaccess); MANIFEST.json beside it lists
every file with its sha256, and plan and deploy refuse a site/ folder that differs from it in any way. STATE
is a folder OUTSIDE the web root where the tool keeps what it needs for a rollback: the list of files it put in
place, every file it replaced (the old .htaccess among them), and a lock. The state belongs to one web root;
used with another, every command refuses.

What it never touches: the folders /release/, /docs/, /forms/, everything of WordPress (wp-*, index.php,
the wp-*.php files), /.well-known/, and any file that is not its own. It refuses to start when the build
would overwrite one of those, when a file or a symbolic link is in the way of one of its files, when WEBROOT
does not look like the lead-dbs.org web root (no release/ folder), when the package, web root and state
folder overlap, while another deploy or rollback holds the lock, and after a deploy that did not finish
(roll that back first).

A rollback restores the web root as it was before the first deploy (WordPress). To go back to an earlier
version of the new site instead, deploy that version's package again.

Python 3.6+, standard library only, on a POSIX system (it locks with fcntl).
"""
import argparse
import base64
import contextlib
import fcntl
import hashlib
import html.parser
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# top-level names of the web root that belong to someone else
PROTECTED = {"release", "docs", "forms", "index.php", "cgi-bin"}
PROTECTED_PREFIXES = ("wp-", ".well-known")
STATE_FILE = "deployed.json"
LOCK_FILE = "deploy.lock"
MANIFEST = "MANIFEST.json"
CSP_MARKER = "INLINE_SCRIPT_HASHES"
GRACE_DAYS = 7
# files whose name changes with their content (Hugo's fingerprints and processed images): a page that is
# already open may still ask for the old name, so a deploy keeps the old file for a while
FINGERPRINTED = re.compile(r"(\.[0-9a-f]{64}\.(css|js|json|woff2)|_hu_[0-9a-f]{8,}\.(webp|avif|png|jpe?g|gif))$")
HISTORY = 20


def protected(rel):
    top = rel.split("/", 1)[0]
    return top in PROTECTED or top.startswith(PROTECTED_PREFIXES)


def safe_rel(rel):
    """a plain relative path below a folder: no absolute path, no empty, '.' or '..' part"""
    return (isinstance(rel, str) and rel != "" and not rel.startswith("/") and "\\" not in rel and "\0" not in rel
            and all(part not in ("", ".", "..") for part in rel.split("/")))


def walk(folder):
    """relative paths of every file under folder, sorted; refuses symbolic links"""
    out = []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames.sort()
        for name in dirnames + filenames:
            path = os.path.join(dirpath, name)
            if os.path.islink(path):
                fail("a symbolic link in " + folder + ": " + os.path.relpath(path, folder))
        for name in filenames:
            out.append(os.path.relpath(os.path.join(dirpath, name), folder).replace(os.sep, "/"))
    return sorted(out)


def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(msg):
    print("refused: " + msg)
    sys.exit(1)


def inside(path, folder):
    """whether path is folder or below it (both already resolved)"""
    return path == folder or path.startswith(folder.rstrip(os.sep) + os.sep)


def now_stamp():
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())


# ---------------------------------------------------------------- files written so that a crash leaves either the
# old or the new version, never half of one, and the change survives a power cut

def fsync_folder(folder):
    fd = os.open(folder, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def put_file(src, dst, token):
    """copies src to dst under a temporary name, then renames it into place"""
    tmp = "{}.lead-deploy-{}.tmp".format(dst, token)
    shutil.copy2(src, tmp)
    with open(tmp, "rb") as f:
        os.fsync(f.fileno())
    os.replace(tmp, dst)
    fsync_folder(os.path.dirname(dst))


def write_json(path, data):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path), prefix="." + os.path.basename(path) + "-")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=1)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
    fsync_folder(os.path.dirname(path))


# ---------------------------------------------------------------- the pages' Content Security Policy

class InlineScripts(html.parser.HTMLParser):
    """the inline scripts a page runs, and what a policy with hashes can't allow (event-handler attributes,
    javascript: links)"""
    JS_TYPES = {"", "module", "text/javascript", "application/javascript", "application/ecmascript",
                "text/ecmascript"}

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.scripts, self.problems = [], []
        self._current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name, value in attrs.items():
            if name.startswith("on"):
                self.problems.append("an event-handler attribute " + name)
            if name in ("href", "src", "action") and (value or "").strip().lower().startswith("javascript:"):
                self.problems.append("a javascript: link")
        if tag == "script" and "src" not in attrs and (attrs.get("type") or "").lower() in self.JS_TYPES:
            self._current = []

    def handle_data(self, data):
        if self._current is not None:
            self._current.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._current is not None:
            self.scripts.append("".join(self._current))
            self._current = None


def inline_script_hashes(site):
    """'sha256-…' of every distinct inline script in the build's pages, sorted"""
    hashes = set()
    for rel in walk(site):
        if not rel.endswith(".html"):
            continue
        parser = InlineScripts()
        with open(os.path.join(site, rel), encoding="utf-8") as f:
            parser.feed(f.read())
        parser.close()
        if parser.problems:
            fail("{} has {}, which the Content Security Policy would block".format(rel, parser.problems[0]))
        for script in parser.scripts:
            hashes.add("'sha256-" + base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode() + "'")
    return sorted(hashes)


def render_htaccess(text, site):
    """server/apache/htaccess with the build's inline-script hashes in its Content Security Policy"""
    lines = text.splitlines(keepends=True)
    rules = [i for i, line in enumerate(lines) if CSP_MARKER in line and not line.lstrip().startswith("#")]
    if len(rules) != 1:
        fail("server/apache/htaccess must name {} in exactly one rule".format(CSP_MARKER))
    lines[rules[0]] = lines[rules[0]].replace(CSP_MARKER, " ".join(inline_script_hashes(site)))
    return "".join(lines)


def page_policy(htaccess):
    m = re.search(r'Content-Security-Policy-Report-Only "([^"]+)"', htaccess)
    if not m or CSP_MARKER in m.group(1):
        fail("no filled-in Content Security Policy in the .htaccess")
    return m.group(1)


# ---------------------------------------------------------------- package

def git(*args, cwd=ROOT):
    return subprocess.run(["git", "-C", cwd] + list(args), stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout.strip()


def export(repo, commit, dest):
    """a fresh clone of repo at commit: the tracked files only (nothing untracked or ignored can enter the
    build), with the history Hugo reads each page's last change from"""
    subprocess.run(["git", "clone", "--quiet", "--no-checkout", repo, dest], check=True)
    r = subprocess.run(["git", "-C", dest, "checkout", "--quiet", "--detach", commit])
    if r.returncode:
        fail("commit {} is not on a branch or tag of {}".format(commit, repo))


def package(out):
    if git("status", "--porcelain", "--untracked-files=no"):
        fail("the checkout has uncommitted changes; a package is built from one commit, so commit them first")
    commit = git("rev-parse", "HEAD")
    name = "lead-dbs-site-" + git("rev-parse", "--short", "HEAD")
    stage = os.path.join(out, name)
    if os.path.exists(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)
    site = os.path.join(stage, "site")
    with tempfile.TemporaryDirectory(prefix="lead-package-") as tmp:
        source = os.path.join(tmp, "source")
        export(ROOT, commit, source)
        # the production build: default baseURL, no preview flags from the environment
        env = {k: v for k, v in os.environ.items() if not k.startswith("HUGO_")}
        subprocess.run(["hugo", "--gc", "--minify", "--source", source, "--destination", site], env=env, check=True)
        for rel in walk(site):
            if protected(rel):
                fail("the build has a file where the server keeps its own: " + rel)
        with open(os.path.join(source, "server/apache/htaccess")) as f:
            htaccess = render_htaccess(f.read(), site)
        with open(os.path.join(site, ".htaccess"), "w") as f:
            f.write(htaccess)
        for check in (["python3", ".github/scripts/check-site.py", site, "https://www.lead-dbs.org/"],
                      ["python3", "tools/check_launch.py", site]):
            subprocess.run(check, cwd=source, check=True)
        shutil.copyfile(os.path.join(source, "tools/deploy.py"), os.path.join(stage, "deploy.py"))
    manifest = {"commit": commit, "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "files": {rel: digest(os.path.join(site, rel)) for rel in walk(site)}}
    with open(os.path.join(stage, MANIFEST), "w") as f:
        json.dump(manifest, f, indent=1)
    tar = os.path.join(out, name + ".tar.gz")
    with tarfile.open(tar, "w:gz") as t:
        t.add(stage, arcname=name)
    print("package: " + tar)
    print("commit: " + commit)
    print("MANIFEST.json sha256: " + digest(os.path.join(stage, MANIFEST)))


# ---------------------------------------------------------------- checks before plan, deploy and rollback

def read_manifest(site):
    """the package's MANIFEST.json, after checking that site/ holds exactly its files with their sha256"""
    path = os.path.join(os.path.dirname(os.path.abspath(site)), MANIFEST)
    if not os.path.isfile(path):
        fail("no {} beside {}: use the site/ folder of an unpacked package".format(MANIFEST, site))
    with open(path) as f:
        manifest = json.load(f)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, dict) or not all(safe_rel(rel) for rel in files):
        fail(path + " is not a package manifest")
    found = set(walk(site))
    missing, extra = sorted(set(files) - found), sorted(found - set(files))
    if missing:
        fail("{} files of {} are missing from the package, e.g. {}".format(len(missing), MANIFEST, missing[0]))
    if extra:
        fail("{} files in the package are not in {}, e.g. {}".format(len(extra), MANIFEST, extra[0]))
    for rel in sorted(files):
        if digest(os.path.join(site, rel)) != files[rel]:
            fail("{} differs from its sha256 in {}".format(rel, MANIFEST))
    manifest["sha256"] = digest(path)
    return manifest


def check_webroot(webroot):
    if not os.path.isdir(os.path.join(webroot, "release")):
        fail(webroot + " has no release/ folder: is this the lead-dbs.org web root?")


def check_places(site, webroot, state):
    check_webroot(webroot)
    if not os.path.isfile(os.path.join(site, "index.html")) or not os.path.isfile(os.path.join(site, ".htaccess")):
        fail(site + " is not the site/ folder of a package (no index.html or .htaccess)")
    real_site, real_root, real_state = (os.path.realpath(p) for p in (site, webroot, state))
    if inside(real_state, real_root) or inside(real_root, real_state):
        fail("the state folder must be outside the web root")
    if inside(real_site, real_root) or inside(real_root, real_site):
        fail("the package must be outside the web root")
    if inside(real_site, real_state) or inside(real_state, real_site):
        fail("the package and the state folder must be separate folders")


def link_in_the_way(webroot, rel):
    """the first part of rel's path under webroot that is a symbolic link or a file where a folder is needed"""
    parts = rel.split("/")
    for i in range(1, len(parts) + 1):
        path = os.path.join(webroot, *parts[:i])
        if os.path.islink(path):
            return "a link is in the way: " + "/".join(parts[:i])
        if i < len(parts) and os.path.isfile(path):
            return "a file is in the way: " + "/".join(parts[:i])
    return None


def load_state(state, webroot):
    """the record of the last deploy, checked: it belongs to this web root and names only paths below it"""
    path = os.path.join(state, STATE_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            data = json.load(f)
    except ValueError:
        fail(path + " is not readable JSON; restore it from a backup or roll back by hand (docs/launch.md)")
    if not (isinstance(data, dict) and isinstance(data.get("files"), list)
            and isinstance(data.get("replaced"), dict) and isinstance(data.get("retired", {}), dict)):
        fail(path + " is not a deploy record")
    if data.get("webroot") != os.path.realpath(webroot):
        fail("the state in {} belongs to the web root {}, not {}".format(state, data.get("webroot"),
                                                                       os.path.realpath(webroot)))
    real_state = os.path.realpath(state)
    for rel in data["files"] + list(data["replaced"]) + list(data.get("retired", {})):
        if not safe_rel(rel):
            fail("{} names a path outside the web root: {!r}".format(path, rel))
    for rel, backup in data["replaced"].items():
        if not safe_rel(backup) or not inside(os.path.realpath(os.path.join(state, backup)), real_state):
            fail("{} names a backup outside the state folder: {!r}".format(path, backup))
    return data


@contextlib.contextmanager
def locked(state):
    """the state folder's lock, held until the end of a deploy or rollback"""
    os.makedirs(state, mode=0o700, exist_ok=True)
    fd = os.open(os.path.join(state, LOCK_FILE), os.O_RDWR | os.O_CREAT, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            fail("another deploy or rollback is running with " + state)
        yield
    finally:
        os.close(fd)


def unfinished(previous):
    if previous and not previous.get("complete"):
        fail("the deploy of {} did not finish. Roll it back first (deploy.py rollback WEBROOT --state STATE), "
             "then deploy again".format(previous.get("deployed")))


# ---------------------------------------------------------------- plan / deploy / rollback

def install_order(files):
    """everything else first, then the pages, the .htaccess last: a page never names a file that isn't there
    yet, and until the new .htaccess is in place the old rules still send unknown addresses to WordPress"""
    return sorted(files, key=lambda rel: (rel == ".htaccess", rel.endswith((".html", ".xml")), rel))


def make_plan(site, webroot, state):
    """what a deploy would do: files to add, to replace (ours or theirs), earlier files of ours to remove,
    and the folders it would make"""
    check_places(site, webroot, state)
    manifest = read_manifest(site)
    previous = load_state(state, webroot)
    unfinished(previous)
    ours = set(previous["files"]) if previous else set()
    new = walk(site)
    plan = {"add": [], "replace_ours": [], "replace_theirs": [], "remove_ours": [], "new_folders": [],
            "refuse": [], "commit": manifest.get("commit"), "manifest_sha256": manifest["sha256"]}
    folders = set()
    for rel in new:
        if protected(rel):
            plan["refuse"].append(rel)
            continue
        problem = link_in_the_way(webroot, rel)
        if problem:
            plan["refuse"].append(rel + " (" + problem + ")")
            continue
        target = os.path.join(webroot, rel)
        if os.path.isdir(target):
            plan["refuse"].append(rel + " (a folder of the same name is there)")
        elif not os.path.exists(target):
            plan["add"].append(rel)
        elif rel in ours:
            plan["replace_ours"].append(rel)
        else:
            plan["replace_theirs"].append(rel)
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            if not os.path.exists(os.path.join(webroot, *parts[:i])):
                folders.add("/".join(parts[:i]))
    plan["remove_ours"] = sorted(ours - set(new))
    plan["new_folders"] = sorted(folders)
    return plan


def print_plan(plan):
    print("package: commit {}, MANIFEST.json sha256 {}".format(plan["commit"], plan["manifest_sha256"]))
    for key, label in (("add", "new files"), ("replace_ours", "updated files of the last deploy"),
                       ("replace_theirs", "files already there that it replaces (kept for a rollback)"),
                       ("remove_ours", "files of the last deploy it removes or keeps for a while"),
                       ("refuse", "REFUSED")):
        print("{}: {}".format(label, len(plan[key])))
        if key in ("replace_theirs", "refuse"):
            for rel in plan[key]:
                print("  " + rel)


def write_inventory(plan, path):
    """the lists a deploy and rollback by hand (SFTP) work from: docs/launch.md, By hand"""
    with open(path, "w") as f:
        json.dump({"commit": plan["commit"], "manifest_sha256": plan["manifest_sha256"],
                   "upload": install_order(plan["add"] + plan["replace_ours"] + plan["replace_theirs"]),
                   "add": plan["add"], "replace": sorted(plan["replace_theirs"] + plan["replace_ours"]),
                   "new_folders": plan["new_folders"], "remove": plan["remove_ours"]}, f, indent=1)
    print("inventory: " + path)


def remove_file(webroot, rel):
    path = os.path.join(webroot, rel)
    if link_in_the_way(webroot, rel) is None and os.path.isfile(path):
        os.remove(path)
        prune(webroot, rel)


def deploy(site, webroot, state, grace_days=GRACE_DAYS):
    plan = make_plan(site, webroot, state)
    print_plan(plan)
    if plan["refuse"]:
        fail("see REFUSED above; nothing was changed")
    with locked(state):
        plan = make_plan(site, webroot, state)    # again, now that no other deploy or rollback can run
        if plan["refuse"]:
            print_plan(plan)
            fail("see REFUSED above; nothing was changed")
        previous = load_state(state, webroot)
        now, stamp, token = time.time(), now_stamp(), secrets.token_hex(6)
        # what the first deploy replaced stays the thing to restore; later deploys add what they replace
        replaced = dict(previous["replaced"]) if previous else {}
        retired = dict(previous.get("retired", {})) if previous else {}
        backup = "backup-{}-{}".format(stamp, token)
        for rel in plan["replace_theirs"]:
            dst = os.path.join(state, backup, rel)
            os.makedirs(os.path.dirname(dst), mode=0o700, exist_ok=True)
            put_file(os.path.join(webroot, rel), dst, token)
            replaced[rel] = backup + "/" + rel
        new = walk(site)
        files = install_order(new)
        history = (previous.get("history", []) if previous else [])[-(HISTORY - 1):]
        history.append({"deployed": stamp, "commit": plan["commit"], "manifest_sha256": plan["manifest_sha256"]})
        record = {"webroot": os.path.realpath(webroot), "deployed": stamp, "token": token, "history": history,
                  "replaced": replaced, "retired": retired, "complete": False,
                  "files": sorted(set(new) | (set(previous["files"]) if previous else set()))}
        # recorded before the web root is touched, so a deploy cut off halfway can still be rolled back
        write_json(os.path.join(state, STATE_FILE), record)
        for rel in files:
            dst = os.path.join(webroot, rel)
            problem = link_in_the_way(webroot, rel)     # checked again right before the write
            if problem:
                fail(rel + ": " + problem + " (the deploy stopped; roll it back)")
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            put_file(os.path.join(site, rel), dst, token)
        for rel in plan["remove_ours"]:
            if rel in replaced:
                put_file(os.path.join(state, replaced[rel]), os.path.join(webroot, rel), token)
            elif grace_days > 0 and FINGERPRINTED.search(rel):
                retired.setdefault(rel, now)
            else:
                remove_file(webroot, rel)
        # a kept file that is back in the build is an ordinary file again; one kept long enough goes
        for rel in sorted(retired):
            if rel in new:
                del retired[rel]
            elif now - retired[rel] >= grace_days * 86400:
                remove_file(webroot, rel)
                del retired[rel]
        record.update(files=sorted(set(new) | set(retired)), retired=retired, complete=True)
        write_json(os.path.join(state, STATE_FILE), record)
    print("deployed commit {} ({} files); to undo: deploy.py rollback {} --state {}".format(
        plan["commit"], len(files), webroot, state))


def prune(webroot, rel):
    """removes the folders a removed file leaves empty, up to the web root"""
    d = os.path.dirname(os.path.join(webroot, rel))
    root = os.path.realpath(webroot)
    while not os.path.islink(d) and os.path.realpath(d) != root and os.path.isdir(d) and not os.listdir(d):
        os.rmdir(d)
        d = os.path.dirname(d)


def rollback(webroot, state):
    check_webroot(webroot)
    if not os.path.exists(os.path.join(state, STATE_FILE)):
        fail("no deploy recorded in " + state)
    with locked(state):
        current = load_state(state, webroot)
        if not current:
            fail("no deploy recorded in " + state)
        files = [rel for rel in current["files"] if not protected(rel)]
        # everything is checked before the first change
        for rel in files:
            problem = link_in_the_way(webroot, rel)
            if problem:
                fail(rel + ": " + problem + "; nothing was changed")
        for rel, backup in current["replaced"].items():
            path = os.path.join(state, backup)
            if rel in files and (os.path.islink(path) or not os.path.isfile(path)):
                fail("the saved original of {} is missing ({}); nothing was changed".format(rel, path))
        token = current.get("token", "")
        # the .htaccess first, then the pages, then the rest
        for rel in sorted(files, key=lambda rel: (rel != ".htaccess", not rel.endswith(".html"), rel)):
            path = os.path.join(webroot, rel)
            if rel in current["replaced"]:
                put_file(os.path.join(state, current["replaced"][rel]), path, "rollback-" + token)
            else:
                remove_file(webroot, rel)
            # what an interrupted deploy (or rollback) left under a temporary name
            for prefix in ("", "rollback-"):
                tmp = "{}.lead-deploy-{}{}.tmp".format(path, prefix, token)
                if token and os.path.isfile(tmp) and not os.path.islink(tmp):
                    os.remove(tmp)
                    prune(webroot, rel)
        os.replace(os.path.join(state, STATE_FILE),
                   os.path.join(state, STATE_FILE + ".rolled-back-" + now_stamp()))
        fsync_folder(state)
    restored = sum(rel in current["replaced"] for rel in files)
    print("rolled back: {} files taken out, {} restored".format(len(files) - restored, restored))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("package")
    p.add_argument("--out", default=os.path.join(ROOT, "dist"))
    for name in ("plan", "deploy"):
        p = sub.add_parser(name)
        p.add_argument("site")
        p.add_argument("webroot")
        p.add_argument("--state", required=True)
    sub.choices["plan"].add_argument("--inventory")
    sub.choices["deploy"].add_argument("--grace-days", type=int, default=GRACE_DAYS)
    p = sub.add_parser("rollback")
    p.add_argument("webroot")
    p.add_argument("--state", required=True)
    p = sub.add_parser("csp")
    p.add_argument("site")
    a = ap.parse_args()
    if a.cmd == "package":
        package(a.out)
    elif a.cmd == "plan":
        plan = make_plan(a.site, a.webroot, a.state)
        print_plan(plan)
        if a.inventory and not plan["refuse"]:
            write_inventory(plan, a.inventory)
        sys.exit(1 if plan["refuse"] else 0)
    elif a.cmd == "deploy":
        if a.grace_days < 0:
            fail("--grace-days must be 0 or more")
        deploy(a.site, a.webroot, a.state, a.grace_days)
    elif a.cmd == "rollback":
        rollback(a.webroot, a.state)
    elif a.cmd == "csp":
        with open(os.path.join(ROOT, "server/apache/htaccess")) as f:
            print(page_policy(render_htaccess(f.read(), a.site)))
    else:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
