#!/usr/bin/env python3
"""Puts the Hugo build into the web root of www.lead-dbs.org beside WordPress, and takes it out again.

NOT RUN AGAINST THE LIVE SERVER YET. docs/launch.md says when and by whom. Every command works on a folder
path. Run it on the server (over SSH) or on a mounted copy. tests/test_launch_server.py runs it against a
fake web root on this machine.

    tools/deploy.py package [--out dist]              build, check and pack the site (on any computer)
    tools/deploy.py plan     SITE WEBROOT --state DIR  say what deploy would do, change nothing
    tools/deploy.py deploy   SITE WEBROOT --state DIR  put the site in place (after a plan)
    tools/deploy.py rollback WEBROOT --state DIR       take the last deploy out again, restore what it replaced

SITE is the site/ folder of an unpacked package (the build and its .htaccess). STATE is a folder OUTSIDE
the web root where the tool keeps what it needs for a rollback: the list of files it put in place, and
every file it replaced (the old .htaccess among them).

What it never touches: the folders /release/, /docs/, /forms/, everything of WordPress (wp-*, index.php,
the wp-*.php files), /.well-known/, and any file that is not its own. A deploy refuses to start when the
build would overwrite one of those or a file is in the way of one of its folders, or when WEBROOT does not
look like the lead-dbs.org web root (no release/ folder).

Python 3.6+, standard library only.
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# top-level names of the web root that belong to someone else
PROTECTED = {"release", "docs", "forms", "index.php", "cgi-bin"}
PROTECTED_PREFIXES = ("wp-", ".well-known")
STATE_FILE = "deployed.json"


def protected(rel):
    top = rel.split("/", 1)[0]
    return top in PROTECTED or top.startswith(PROTECTED_PREFIXES)


def walk(folder):
    """relative paths of every file under folder, sorted"""
    out = []
    for dirpath, dirnames, filenames in os.walk(folder):
        dirnames.sort()
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


# ---------------------------------------------------------------- package

def git(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args), stdout=subprocess.PIPE,
                          universal_newlines=True, check=True).stdout.strip()


def package(out):
    if git("status", "--porcelain", "--untracked-files=no"):
        fail("the checkout has uncommitted changes; a package must be one commit")
    sha = git("rev-parse", "--short", "HEAD")
    name = "lead-dbs-site-" + sha
    stage = os.path.join(out, name)
    if os.path.exists(stage):
        shutil.rmtree(stage)
    os.makedirs(stage)
    site = os.path.join(stage, "site")
    # the production build: default baseURL, no preview flags from the environment
    env = {k: v for k, v in os.environ.items() if not k.startswith("HUGO_")}
    subprocess.run(["hugo", "--gc", "--minify", "--source", ROOT, "--destination", site], env=env, check=True)
    shutil.copyfile(os.path.join(ROOT, "server/apache/htaccess"), os.path.join(site, ".htaccess"))
    for rel in walk(site):
        if protected(rel):
            fail("the build has a file where the server keeps its own: " + rel)
    for check in (["python3", ".github/scripts/check-site.py", site, "https://www.lead-dbs.org/"],
                  ["python3", "tools/check_launch.py", site]):
        subprocess.run(check, cwd=ROOT, check=True)
    with open(os.path.join(stage, "MANIFEST.json"), "w") as f:
        json.dump({"commit": git("rev-parse", "HEAD"), "built": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                   "files": {rel: digest(os.path.join(site, rel)) for rel in walk(site)}}, f, indent=1)
    shutil.copyfile(os.path.join(ROOT, "tools/deploy.py"), os.path.join(stage, "deploy.py"))
    tar = os.path.join(out, name + ".tar.gz")
    with tarfile.open(tar, "w:gz") as t:
        t.add(stage, arcname=name)
    print("package: " + tar)


# ---------------------------------------------------------------- plan / deploy / rollback

def load_state(state):
    path = os.path.join(state, STATE_FILE)
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def check_webroot(webroot):
    if not os.path.isdir(os.path.join(webroot, "release")):
        fail(webroot + " has no release/ folder: is this the lead-dbs.org web root?")


def check_places(site, webroot, state):
    check_webroot(webroot)
    if not os.path.isfile(os.path.join(site, "index.html")) or not os.path.isfile(os.path.join(site, ".htaccess")):
        fail(site + " is not the site/ folder of a package (no index.html or .htaccess)")
    real_root, real_state = os.path.realpath(webroot), os.path.realpath(state)
    if real_state == real_root or real_state.startswith(real_root + os.sep):
        fail("the state folder must be outside the web root")


def make_plan(site, webroot, state):
    """what a deploy would do: files to add, to replace (ours or theirs), and earlier files of ours to remove"""
    check_places(site, webroot, state)
    previous = load_state(state)
    ours = set(previous["files"]) if previous else set()
    new = walk(site)
    plan = {"add": [], "replace_ours": [], "replace_theirs": [], "remove_ours": [], "refuse": []}
    for rel in new:
        if protected(rel):
            plan["refuse"].append(rel)
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
        # a file of the web root where the build needs a folder
        parts = rel.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            if os.path.isfile(os.path.join(webroot, *parts[:i])):
                plan["refuse"].append(rel + " (a file is in the way: " + "/".join(parts[:i]) + ")")
                break
    plan["remove_ours"] = sorted(ours - set(new))
    return plan


def print_plan(plan):
    for key, label in (("add", "new files"), ("replace_ours", "updated files of the last deploy"),
                       ("replace_theirs", "files already there that it replaces (kept for a rollback)"),
                       ("remove_ours", "files of the last deploy it removes"), ("refuse", "REFUSED")):
        print("{}: {}".format(label, len(plan[key])))
        if key in ("replace_theirs", "refuse"):
            for rel in plan[key]:
                print("  " + rel)


def deploy(site, webroot, state):
    plan = make_plan(site, webroot, state)
    print_plan(plan)
    if plan["refuse"]:
        fail("see REFUSED above; nothing was changed")
    os.makedirs(state, exist_ok=True)
    previous = load_state(state)
    stamp = time.strftime("%Y%m%dT%H%M%S")
    backup = os.path.join(state, "backup-" + stamp)
    # what the first deploy replaced stays the thing to restore; later deploys add what they replace
    replaced = dict(previous["replaced"]) if previous else {}
    for rel in plan["replace_theirs"]:
        dst = os.path.join(backup, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(webroot, rel), dst)
        replaced[rel] = dst
    # record the deploy before touching the web root, so a deploy cut off halfway can still be rolled back
    files = [rel for rel in walk(site) if rel != ".htaccess"] + [".htaccess"]
    everything = sorted(set(files) | (set(previous["files"]) if previous else set()))
    write_state(state, {"deployed": stamp, "files": everything, "replaced": replaced, "complete": False})
    # each file is copied in under a temporary name and renamed into place, the .htaccess last: until it is
    # in place, the old rules still send unknown addresses to WordPress
    for rel in files:
        dst = os.path.join(webroot, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        tmp = dst + ".lead-deploy-tmp"
        shutil.copy2(os.path.join(site, rel), tmp)
        os.replace(tmp, dst)
    for rel in plan["remove_ours"]:
        if rel in replaced:
            shutil.copy2(replaced[rel], os.path.join(webroot, rel))
            continue
        path = os.path.join(webroot, rel)
        if os.path.isfile(path):
            os.remove(path)
        prune(webroot, rel)
    write_state(state, {"deployed": stamp, "files": walk(site), "replaced": replaced, "complete": True})
    print("deployed {} files; to undo: deploy.py rollback {} --state {}".format(len(files), webroot, state))


def write_state(state, data):
    tmp = os.path.join(state, STATE_FILE + ".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, os.path.join(state, STATE_FILE))


def prune(webroot, rel):
    """removes the folders a removed file leaves empty, up to the web root"""
    d = os.path.dirname(os.path.join(webroot, rel))
    root = os.path.realpath(webroot)
    while os.path.realpath(d) != root and os.path.isdir(d) and not os.listdir(d):
        os.rmdir(d)
        d = os.path.dirname(d)


def rollback(webroot, state):
    current = load_state(state)
    if not current:
        fail("no deploy recorded in " + state)
    check_webroot(webroot)
    # the .htaccess first, so WordPress answers again while the rest is taken out
    for rel in sorted(current["files"], key=lambda rel: rel != ".htaccess"):
        if protected(rel):
            continue
        path = os.path.join(webroot, rel)
        if rel in current["replaced"]:
            shutil.copy2(current["replaced"][rel], path)
        elif os.path.isfile(path):
            os.remove(path)
            prune(webroot, rel)
        tmp = path + ".lead-deploy-tmp"
        if os.path.isfile(tmp):
            os.remove(tmp)
    os.replace(os.path.join(state, STATE_FILE),
               os.path.join(state, STATE_FILE + ".rolled-back-" + time.strftime("%Y%m%dT%H%M%S")))
    print("rolled back: {} files taken out, {} restored".format(
        len(current["files"]) - len(current["replaced"]), len(current["replaced"])))


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
    p = sub.add_parser("rollback")
    p.add_argument("webroot")
    p.add_argument("--state", required=True)
    a = ap.parse_args()
    if a.cmd == "package":
        package(a.out)
    elif a.cmd == "plan":
        plan = make_plan(a.site, a.webroot, a.state)
        print_plan(plan)
        sys.exit(1 if plan["refuse"] else 0)
    elif a.cmd == "deploy":
        deploy(a.site, a.webroot, a.state)
    elif a.cmd == "rollback":
        rollback(a.webroot, a.state)
    else:
        ap.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
