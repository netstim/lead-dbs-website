"""The switch, rehearsed on this computer: a fake lead-dbs.org web root (WordPress stubs, /release/, /docs/,
/forms/, uploads, WordPress's .htaccess), tools/deploy.py putting the Hugo build in, server/apache/htaccess
answering on a local Apache, and a rollback that leaves the web root exactly as it was. Never talks to
STRATO.

Needs hugo, and Apache for the second half (macOS /usr/sbin/httpd, Debian/Ubuntu apache2); skipped without
them (failed with LEAD_REQUIRE_INTEGRATION=1). Set LEAD_TEST_BUILD to a production build folder to skip the
Hugo build.
"""
import base64
import contextlib
import fcntl
import gzip
import hashlib
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import ssl
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from prerequisites import needs

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = [sys.executable, str(ROOT / 'tools/deploy.py')]
_spec = importlib.util.spec_from_file_location('deploy', ROOT / 'tools/deploy.py')
deploy = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(deploy)

HUGO = bool(shutil.which('hugo') or os.environ.get('LEAD_TEST_BUILD'))
HTTPD = shutil.which('httpd') or shutil.which('apache2') or next(
    (p for p in ('/usr/sbin/httpd', '/usr/sbin/apache2') if Path(p).exists()), None)
MODULES = next((p for p in ('/usr/libexec/apache2', '/usr/lib/apache2/modules', '/usr/lib64/httpd/modules',
                            '/opt/homebrew/lib/httpd/modules') if Path(p, 'mod_rewrite.so').exists()), None)

WP_HTACCESS = """# BEGIN WordPress
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^index\\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
# END WordPress
"""

# a folder's own .htaccess that tries to serve everything in it, as the release folder's might
RELEASE_HTACCESS = """RewriteEngine On
<FilesMatch ".">
  Require all granted
</FilesMatch>
"""

# files that must never be served, whoever put them there (SEC-01)
PRIVATE = {
    '.env': 'SECRET env',
    'composer.json': 'SECRET composer',
    'vendor/demo.txt': 'SECRET vendor',
    'wp-config.php.bak': 'SECRET wp-config backup',
    'error_log': 'SECRET php error log',
    'release/logs/private-test.log': 'SECRET release log',
    'release/.git/config': 'SECRET nested dotfile',
    'release/db.sqlite': 'SECRET database',
    'docs/talks/.DS_Store': 'SECRET finder file',
    'wp-content/uploads/2020/01/shell.php': 'SECRET uploaded php',
    'backups/site.zip': 'SECRET backup',
}

# the web root as it is before the switch: WordPress and the folders that are not WordPress's
WEBROOT = {
    '.htaccess': WP_HTACCESS,
    'index.php': 'WORDPRESS index.php',
    'wp-config.php': 'WORDPRESS config',
    'wp-login.php': 'WORDPRESS login',
    'xmlrpc.php': 'WORDPRESS xmlrpc',
    'wp-admin/index.php': 'WORDPRESS admin',
    'wp-includes/version.php': 'WORDPRESS includes',
    'wp-content/uploads/2015/11/Ilinskyetal15last.pdf': 'UPLOAD pdf',
    'wp-content/plugins/newsletter/plugin.php': 'WORDPRESS newsletter plugin',
    'release/.htaccess': RELEASE_HTACCESS,
    'release/download.php': 'RELEASE download.php',
    'release/logs/2026-11.log': 'RELEASE log',
    'docs/talks/AAN_presentation_Horn_2017.pdf': 'DOCS pdf',
    'forms/send.php': 'FORMS send.php',
    '.well-known/acme-challenge/token123': 'ACME token',
    'favicon.ico': 'OLD favicon',
    'google1234.html': 'search console proof',
    **PRIVATE,
}


def tree(folder):
    """relative path -> sha256 of every file under folder"""
    out = {}
    for dirpath, _, files in os.walk(folder):
        for name in files:
            p = Path(dirpath, name)
            out[str(p.relative_to(folder))] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def folders(folder):
    return sorted(p for p in Path(folder).rglob('*') if p.is_dir())


def make_webroot(folder):
    for rel, text in WEBROOT.items():
        p = Path(folder, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


_build = None


def production_build():
    """the Hugo production build, made once per run"""
    global _build
    if os.environ.get('LEAD_TEST_BUILD'):
        return Path(os.environ['LEAD_TEST_BUILD'])
    if _build is None:
        _build = Path(tempfile.mkdtemp(prefix='lead-build-'))
        env = {k: v for k, v in os.environ.items() if not k.startswith('HUGO_')}
        subprocess.run(['hugo', '--gc', '--minify', '--quiet', '--source', str(ROOT), '--destination', str(_build)],
                       env=env, check=True)
    return _build


def seal(site):
    """writes the package's MANIFEST.json beside site/, as deploy.py package does"""
    files = {str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in Path(site).rglob('*') if p.is_file()}
    Path(site).parent.joinpath('MANIFEST.json').write_text(json.dumps({'commit': 'test', 'files': files}))


def make_site(folder):
    """the site/ folder of a package with its manifest: the build and its .htaccess (what deploy.py package
    makes, without git and the checks)"""
    shutil.copytree(production_build(), folder)
    htaccess = deploy.render_htaccess((ROOT / 'server/apache/htaccess').read_text(), str(folder))
    Path(folder, '.htaccess').write_text(htaccess)
    seal(folder)


def run(*args, ok=True):
    r = subprocess.run(DEPLOY + [str(a) for a in args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       universal_newlines=True)
    if ok and r.returncode:
        raise AssertionError(r.stdout)
    return r


@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


@needs(HUGO, 'hugo (or LEAD_TEST_BUILD)')
class DeployTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='lead-deploy-'))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.web, self.state, self.site = self.tmp / 'web', self.tmp / 'state', self.tmp / 'package' / 'site'
        make_webroot(self.web)
        make_site(self.site)
        self.before, self.dirs = tree(self.web), folders(self.web)

    def assertUnchanged(self):
        self.assertEqual(tree(self.web), self.before)
        self.assertEqual(folders(self.web), self.dirs, 'folders left behind')

    def package_copy(self, name):
        """a copy of the package, its manifest included"""
        site = self.tmp / name / 'site'
        shutil.copytree(self.site, site)
        shutil.copy2(self.site.parent / 'MANIFEST.json', site.parent / 'MANIFEST.json')
        return site

    def test_deploy_keeps_everything_that_is_not_its_own_and_rollback_restores_it(self):
        plan = run('plan', self.site, self.web, '--state', self.state).stdout
        self.assertIn('REFUSED: 0', plan)
        self.assertIn('  .htaccess', plan)      # replaced, and kept for the rollback
        self.assertIn('  favicon.ico', plan)
        self.assertIn('commit test', plan)
        self.assertUnchanged()
        self.assertFalse(self.state.exists(), 'plan wrote its state')
        out = run('deploy', self.site, self.web, '--state', self.state).stdout
        self.assertIn('deployed commit test', out)
        after = tree(self.web)
        for rel, h in self.before.items():
            if rel not in ('.htaccess', 'favicon.ico'):
                self.assertEqual(after.get(rel), h, rel + ' was changed')
        self.assertEqual(after['.htaccess'], tree(self.site)['.htaccess'])
        self.assertTrue((self.web / 'index.html').exists())
        self.assertFalse(any('.lead-deploy-' in p.name for p in self.web.rglob('*')))
        state = json.loads((self.state / 'deployed.json').read_text())
        self.assertEqual(state['webroot'], os.path.realpath(self.web))
        self.assertTrue(state['complete'])
        self.assertEqual(state['history'][-1]['commit'], 'test')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_second_deploy_removes_its_old_files_and_rollback_still_restores_the_original(self):
        run('deploy', self.site, self.web, '--state', self.state)
        (self.site / 'gallery' / 'index.html').unlink()
        (self.site / 'index.html').write_text('NEW HOME')
        seal(self.site)
        run('deploy', self.site, self.web, '--state', self.state)
        self.assertFalse((self.web / 'gallery' / 'index.html').exists())
        self.assertEqual((self.web / 'index.html').read_text(), 'NEW HOME')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_replaced_fingerprinted_files_stay_for_open_pages_until_the_grace_period_ends(self):
        run('deploy', self.site, self.web, '--state', self.state)
        old = next((self.site / 'css').glob('*.css'))
        new = old.with_name('style.min.' + 'a' * 64 + '.css')
        old.rename(new)
        seal(self.site)
        run('deploy', self.site, self.web, '--state', self.state)
        # a page that was open before the deploy still gets its stylesheet
        self.assertTrue((self.web / 'css' / old.name).exists())
        self.assertTrue((self.web / 'css' / new.name).exists())
        # unless the deploy says otherwise, the next one inside the grace period keeps it too
        run('deploy', self.site, self.web, '--state', self.state)
        self.assertTrue((self.web / 'css' / old.name).exists())
        run('deploy', self.site, self.web, '--state', self.state, '--grace-days', '0')
        self.assertFalse((self.web / 'css' / old.name).exists())
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_rollback_also_takes_out_the_files_kept_for_the_grace_period(self):
        run('deploy', self.site, self.web, '--state', self.state)
        old = next((self.site / 'css').glob('*.css'))
        old.rename(old.with_name('style.min.' + 'b' * 64 + '.css'))
        seal(self.site)
        run('deploy', self.site, self.web, '--state', self.state)
        self.assertTrue((self.web / 'css' / old.name).exists())
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_files_go_in_before_the_pages_that_name_them_and_the_htaccess_last(self):
        order = []
        original = deploy.put_file

        def record(src, dst, token):
            order.append(os.path.relpath(dst, self.web).replace(os.sep, '/'))
            original(src, dst, token)
        with mock.patch.object(deploy, 'put_file', side_effect=record), quiet():
            deploy.deploy(str(self.site), str(self.web), str(self.state))
        installed = [rel for rel in order if not rel.startswith('..')]   # not the backups in the state folder
        self.assertEqual(installed[-1], '.htaccess')
        pages = [i for i, rel in enumerate(installed) if rel.endswith(('.html', '.xml'))]
        others = [i for i, rel in enumerate(installed[:-1]) if not rel.endswith(('.html', '.xml'))]
        self.assertLess(max(others), min(pages))

    def crash_after(self, calls):
        """a put_file that copies to the temporary name and then fails, like a lost connection, at call n"""
        count = {'n': 0}
        original = deploy.put_file

        def put(src, dst, token):
            count['n'] += 1
            if count['n'] == calls:
                shutil.copy2(src, '{}.lead-deploy-{}.tmp'.format(dst, token))
                raise OSError('connection lost')
            original(src, dst, token)
        return mock.patch.object(deploy, 'put_file', side_effect=put)

    def test_a_deploy_cut_off_at_any_stage_is_refused_again_and_can_be_rolled_back(self):
        files = sum(1 for p in self.site.rglob('*') if p.is_file())
        backups = 2   # .htaccess and favicon.ico are replaced
        for calls in (1, backups + 1, backups + files // 2, backups + files):
            with self.subTest(crash_at=calls):
                with self.crash_after(calls), quiet(), self.assertRaises(OSError):
                    deploy.deploy(str(self.site), str(self.web), str(self.state))
                if calls > backups:   # the web root was touched: the record says so and blocks a new deploy
                    self.assertFalse(json.loads((self.state / 'deployed.json').read_text())['complete'])
                    r = run('deploy', self.site, self.web, '--state', self.state, ok=False)
                    self.assertIn('did not finish', r.stdout)
                    run('rollback', self.web, '--state', self.state)
                else:                 # only the backups were being made: nothing to roll back
                    self.assertFalse((self.state / 'deployed.json').exists())
                self.assertUnchanged()

    def test_a_second_deploy_cut_off_while_removing_old_files_can_be_rolled_back(self):
        run('deploy', self.site, self.web, '--state', self.state)
        (self.site / 'favicon.ico').unlink()     # the original favicon must come back
        seal(self.site)
        installs = sum(1 for p in self.site.rglob('*') if p.is_file())
        with self.crash_after(installs + 1), quiet(), self.assertRaises(OSError):   # restoring the favicon
            deploy.deploy(str(self.site), str(self.web), str(self.state))
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def with_legacy_original(self):
        """an original web-root file in a folder of its own, replaced by a first deploy and dropped by the second
        package; returns that second package"""
        (self.web / 'legacy').mkdir()
        (self.web / 'legacy' / 'x.txt').write_text('ORIGINAL')
        self.before, self.dirs = tree(self.web), folders(self.web)
        first = self.package_copy('first')
        (first / 'legacy').mkdir()
        (first / 'legacy' / 'x.txt').write_text('NEW')
        seal(first)
        run('deploy', first, self.web, '--state', self.state)
        self.assertEqual((self.web / 'legacy' / 'x.txt').read_text(), 'NEW')
        return self.package_copy('second')

    def outside_sentinel(self):
        outside = self.tmp / 'another-site'
        outside.mkdir()
        (outside / 'x.txt').write_text('OUTSIDE')
        return outside

    def test_a_dropped_file_is_never_restored_through_a_link(self):
        second = self.with_legacy_original()
        outside = self.outside_sentinel()
        shutil.rmtree(self.web / 'legacy')
        (self.web / 'legacy').symlink_to(outside, target_is_directory=True)
        deployed = tree(self.web)
        for command in ('plan', 'deploy'):
            with self.subTest(command=command):
                r = run(command, second, self.web, '--state', self.state, ok=False)
                self.assertIn('legacy/x.txt (a link is in the way: legacy)', r.stdout)
                self.assertEqual((outside / 'x.txt').read_text(), 'OUTSIDE')
                self.assertEqual(tree(self.web), deployed)
        # the same in a file's place
        (self.web / 'legacy').unlink()
        (self.web / 'legacy').write_text('a file where the folder was')
        r = run('deploy', second, self.web, '--state', self.state, ok=False)
        self.assertIn('legacy/x.txt (a file is in the way: legacy)', r.stdout)
        (self.web / 'legacy').unlink()
        (self.web / 'legacy').mkdir()
        run('deploy', second, self.web, '--state', self.state)
        self.assertEqual((self.web / 'legacy' / 'x.txt').read_text(), 'ORIGINAL')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_link_made_during_the_deploy_stops_the_restore(self):
        """the restore checks its path again right before writing, not only in the plan"""
        second = self.with_legacy_original()
        outside = self.outside_sentinel()
        original = deploy.put_file

        def swap_then_put(src, dst, token):
            if os.path.isdir(self.web / 'legacy') and not os.path.islink(self.web / 'legacy'):
                shutil.rmtree(self.web / 'legacy')
                (self.web / 'legacy').symlink_to(outside, target_is_directory=True)
            original(src, dst, token)
        with mock.patch.object(deploy, 'put_file', side_effect=swap_then_put), quiet(), \
                self.assertRaises(SystemExit):
            deploy.deploy(str(second), str(self.web), str(self.state))
        self.assertEqual((outside / 'x.txt').read_text(), 'OUTSIDE')
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ['x.txt'])
        self.assertFalse(json.loads((self.state / 'deployed.json').read_text())['complete'])
        r = run('rollback', self.web, '--state', self.state, ok=False)   # the link is still there
        self.assertIn('a link is in the way: legacy', r.stdout)
        (self.web / 'legacy').unlink()
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()
        self.assertEqual((outside / 'x.txt').read_text(), 'OUTSIDE')

    def test_a_deleted_folder_of_a_saved_original_is_made_again(self):
        second = self.with_legacy_original()
        shutil.rmtree(self.web / 'legacy')
        run('deploy', second, self.web, '--state', self.state)
        self.assertEqual((self.web / 'legacy' / 'x.txt').read_text(), 'ORIGINAL')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_rollback_makes_a_deleted_folder_again_and_can_be_retried_after_a_cut(self):
        self.with_legacy_original()
        shutil.rmtree(self.web / 'legacy')
        original = deploy.put_file
        cut = {'done': False}

        def put(src, dst, token):
            if dst.endswith('legacy/x.txt') and not cut['done']:   # cut off while restoring it
                cut['done'] = True
                shutil.copy2(src, '{}.lead-deploy-{}.tmp'.format(dst, token))
                raise OSError('connection lost')
            original(src, dst, token)
        with mock.patch.object(deploy, 'put_file', side_effect=put), quiet(), self.assertRaises(OSError):
            deploy.rollback(str(self.web), str(self.state))
        self.assertTrue(cut['done'])
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_something_in_place_of_a_folder_still_stops_a_rollback(self):
        self.with_legacy_original()
        shutil.rmtree(self.web / 'legacy')
        (self.web / 'legacy').write_text('a file where the folder was')
        deployed = tree(self.web)
        r = run('rollback', self.web, '--state', self.state, ok=False)
        self.assertIn('a file is in the way: legacy', r.stdout)
        self.assertEqual(tree(self.web), deployed)
        (self.web / 'legacy').unlink()
        (self.web / 'legacy').mkdir()
        (self.web / 'legacy' / 'x.txt').mkdir()      # a folder where the original goes
        r = run('rollback', self.web, '--state', self.state, ok=False)
        self.assertIn('a folder is in the way of its saved original', r.stdout)
        (self.web / 'legacy' / 'x.txt').rmdir()
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_one_deploy_or_rollback_at_a_time(self):
        self.state.mkdir()
        with open(self.state / 'deploy.lock', 'w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)    # another deploy is running
            r = run('deploy', self.site, self.web, '--state', self.state, ok=False)
            self.assertIn('another deploy or rollback is running', r.stdout)
            self.assertUnchanged()
        run('deploy', self.site, self.web, '--state', self.state)
        with open(self.state / 'deploy.lock', 'w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            r = run('rollback', self.web, '--state', self.state, ok=False)
            self.assertIn('another deploy or rollback is running', r.stdout)
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_symbolic_links_are_refused(self):
        outside = self.tmp / 'another-site'
        outside.mkdir()
        (self.web / 'css').symlink_to(outside, target_is_directory=True)
        self.dirs, self.before = folders(self.web), tree(self.web)
        r = run('deploy', self.site, self.web, '--state', self.state, ok=False)
        self.assertIn('a link is in the way: css', r.stdout)
        self.assertEqual(list(outside.iterdir()), [], 'wrote through the link')
        (self.web / 'css').unlink()
        (self.web / 'robots.txt').symlink_to(outside / 'robots.txt')
        r = run('deploy', self.site, self.web, '--state', self.state, ok=False)
        self.assertIn('a link is in the way: robots.txt', r.stdout)
        (self.web / 'robots.txt').unlink()
        site = self.package_copy('linked')
        (site / 'linked.html').symlink_to('/etc/hosts')
        r = run('plan', site, self.web, '--state', self.state, ok=False)
        self.assertIn('a symbolic link', r.stdout)
        self.assertFalse(self.state.exists())

    def test_the_state_belongs_to_one_web_root(self):
        run('deploy', self.site, self.web, '--state', self.state)
        other = self.tmp / 'other-web'
        make_webroot(other)
        other_before = tree(other)
        for args in (('rollback', other), ('plan', self.site, other), ('deploy', self.site, other)):
            with self.subTest(command=args[0]):
                r = run(*args, '--state', self.state, ok=False)
                self.assertIn('belongs to the web root', r.stdout)
        self.assertEqual(tree(other), other_before)
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_tampered_state_is_refused_before_any_change(self):
        run('deploy', self.site, self.web, '--state', self.state)
        deployed = tree(self.web)
        good = (self.state / 'deployed.json').read_text()
        victim = self.tmp / 'victim.txt'
        victim.write_text('not the web root')
        state = json.loads(good)
        cases = {
            'a file outside the web root': dict(state, files=state['files'] + ['../victim.txt']),
            'an absolute path': dict(state, files=state['files'] + [str(victim)]),
            'a backup outside the state': dict(state, replaced={**state['replaced'], 'index.html': '../victim.txt'}),
        }
        for why, bad in cases.items():
            with self.subTest(why=why):
                (self.state / 'deployed.json').write_text(json.dumps(bad))
                r = run('rollback', self.web, '--state', self.state, ok=False)
                self.assertIn('outside', r.stdout)
                self.assertEqual(tree(self.web), deployed)
                self.assertTrue(victim.exists())
        (self.state / 'deployed.json').write_text('{"files": [')
        self.assertIn('not readable JSON', run('rollback', self.web, '--state', self.state, ok=False).stdout)
        (self.state / 'deployed.json').write_text(good)
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_the_package_must_match_its_manifest(self):
        edited = self.package_copy('edited')
        (edited / 'about' / 'index.html').write_text('edited after the review')
        missing = self.package_copy('missing')
        (missing / 'robots.txt').unlink()
        extra = self.package_copy('extra')
        (extra / 'extra.html').write_text('uploaded by mistake')
        unsealed = self.package_copy('unsealed')
        (unsealed.parent / 'MANIFEST.json').unlink()
        cases = [(edited, 'about/index.html differs from its sha256'), (missing, 'missing from the package'),
                 (extra, 'not in MANIFEST.json'), (unsealed, 'no MANIFEST.json')]
        for site, why in cases:
            with self.subTest(why=why):
                for command in ('plan', 'deploy'):
                    r = run(command, site, self.web, '--state', self.state, ok=False)
                    self.assertIn(why, r.stdout)
        self.assertUnchanged()
        self.assertFalse(self.state.exists())

    def test_refusals_change_nothing(self):
        cases = []
        bad = self.package_copy('bad1')
        (bad / 'release').mkdir(exist_ok=True)
        (bad / 'release' / 'download.php').write_text('overwrite')
        seal(bad)
        cases.append((bad, self.web, self.state, 'release/download.php'))
        bad = self.package_copy('bad2')
        (bad / 'wp-config.php').write_text('overwrite')
        seal(bad)
        cases.append((bad, self.web, self.state, 'wp-config.php'))
        cases.append((self.site, self.web, self.web / 'state', 'outside the web root'))
        cases.append((self.site, self.web, self.site / 'state', 'separate folders'))
        inside = self.web / 'pkg' / 'site'
        shutil.copytree(self.site, inside)
        seal(inside)
        cases.append((inside, self.web, self.state, 'the package must be outside the web root'))
        noroot = self.tmp / 'not-the-webroot'
        noroot.mkdir()
        cases.append((self.site, noroot, self.state, 'no release/ folder'))
        for site, web, state, why in cases:
            with self.subTest(why=why):
                r = run('deploy', site, web, '--state', state, ok=False)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(why, r.stdout)
        shutil.rmtree(self.web / 'pkg')
        self.assertUnchanged()
        self.assertFalse((self.web / 'state').exists())
        self.assertFalse(self.state.exists())

    def test_a_file_in_the_way_of_a_folder_is_refused(self):
        (self.web / 'about').write_text('a file named like a folder of the build')
        before = tree(self.web)
        r = run('deploy', self.site, self.web, '--state', self.state, ok=False)
        self.assertIn('a file is in the way: about', r.stdout)
        self.assertEqual(tree(self.web), before)

    def test_rollback_without_a_deploy_is_refused(self):
        r = run('rollback', self.web, '--state', self.state, ok=False)
        self.assertIn('no deploy recorded', r.stdout)
        self.assertUnchanged()

    def test_by_hand_with_the_inventory_as_over_sftp(self):
        """docs/launch.md, By hand: plan on a copy of the web root's file names, upload, and roll back using
        only the inventory and the downloaded originals"""
        names = self.tmp / 'names'
        for rel in self.before:
            p = names / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('')                             # only the names matter
        inventory = self.tmp / 'inventory.json'
        run('plan', self.site, names, '--state', self.tmp / 'plan-state', '--inventory', inventory)
        inv = json.loads(inventory.read_text())
        self.assertIn('.htaccess', inv['replace'])
        self.assertEqual(inv['upload'][-1], '.htaccess')
        originals = self.tmp / 'originals'                # 1. download what will be replaced
        for rel in inv['replace']:
            (originals / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.web / rel, originals / rel)
        for rel in inv['upload']:                         # 2.-3. upload, the .htaccess last
            (self.web / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(self.site / rel, self.web / rel)
        self.assertEqual(tree(self.web)['index.html'], tree(self.site)['index.html'])
        shutil.copy2(originals / '.htaccess', self.web / '.htaccess')   # rollback: the old rules first,
        for rel in inv['replace']:                                       # every replaced original,
            shutil.copy2(originals / rel, self.web / rel)
        for rel in inv['add']:                                           # only the added files,
            (self.web / rel).unlink()
        for rel in sorted(inv['new_folders'], key=lambda d: -d.count('/')):  # and the new, now empty folders
            (self.web / rel).rmdir()
        self.assertUnchanged()

    def test_the_policy_names_every_inline_script_and_refuses_inline_handlers(self):
        policy = deploy.page_policy((self.site / '.htaccess').read_text())
        for page in self.site.rglob('*.html'):
            parser = deploy.InlineScripts()
            parser.feed(page.read_text())
            for script in parser.scripts:
                h = "'sha256-" + base64.b64encode(hashlib.sha256(script.encode()).digest()).decode() + "'"
                self.assertIn(h, policy, page)
        site = self.tmp / 'handlers'
        site.mkdir()
        (site / 'index.html').write_text('<button onclick="go()">Go</button>')
        with quiet(), self.assertRaises(SystemExit):
            deploy.render_htaccess((ROOT / 'server/apache/htaccess').read_text(), str(site))


@needs(shutil.which('git'), 'git')
class PackageSourceTests(unittest.TestCase):
    def test_the_package_is_built_from_the_commit_alone(self):
        tmp = Path(tempfile.mkdtemp(prefix='lead-export-'))
        self.addCleanup(shutil.rmtree, tmp)
        repo = tmp / 'repo'
        repo.mkdir()
        git = ['git', '-C', str(repo), '-c', 'user.name=t', '-c', 'user.email=t@example.org']
        subprocess.run(git + ['init', '--quiet'], check=True)
        (repo / 'content.md').write_text('committed')
        subprocess.run(git + ['add', 'content.md'], check=True)
        subprocess.run(git + ['commit', '--quiet', '-m', 'one'], check=True)
        commit = subprocess.run(git + ['rev-parse', 'HEAD'], stdout=subprocess.PIPE, universal_newlines=True,
                                check=True).stdout.strip()
        (repo / 'untracked.md').write_text('not committed')
        (repo / 'static').mkdir()
        (repo / 'static' / 'stray.pdf').write_text('not committed either')
        deploy.export(str(repo), commit, str(tmp / 'source'))
        self.assertEqual((tmp / 'source' / 'content.md').read_text(), 'committed')
        self.assertFalse((tmp / 'source' / 'untracked.md').exists())
        self.assertFalse((tmp / 'source' / 'static').exists())
        log = subprocess.run(['git', '-C', str(tmp / 'source'), 'log', '--format=%H'], stdout=subprocess.PIPE,
                             universal_newlines=True, check=True).stdout.split()
        self.assertEqual(log, [commit])     # with its history, for Hugo's last-modified dates


def committed_copy(dest):
    """a repository at dest holding this checkout as it would be committed: HEAD, plus the tracked files changed
    since and the new files git doesn't ignore (in CI that is HEAD itself)"""
    lines = lambda *args: subprocess.run(['git', '-C', str(ROOT)] + list(args), stdout=subprocess.PIPE,
                                         universal_newlines=True, check=True).stdout.split('\0')
    subprocess.run(['git', 'clone', '--quiet', '--no-checkout', str(ROOT), str(dest)], check=True)
    head = lines('rev-parse', 'HEAD')[0].strip()
    subprocess.run(['git', '-C', str(dest), 'checkout', '--quiet', '-B', 'under-test', head], check=True)
    for rel in filter(None, lines('ls-files', '-z', '--modified', '--others', '--exclude-standard')):
        if (ROOT / rel).is_file():
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest / rel)
    for rel in filter(None, lines('ls-files', '-z', '--deleted')):
        (dest / rel).unlink()
    git = ['git', '-C', str(dest), '-c', 'user.name=t', '-c', 'user.email=t@example.org']
    subprocess.run(git + ['add', '--all'], check=True)
    subprocess.run(git + ['commit', '--quiet', '--allow-empty', '-m', 'the checkout under test'], check=True)


@needs(shutil.which('git') and shutil.which('hugo'), 'git and hugo')
class PackageTests(unittest.TestCase):
    def test_package_with_a_relative_out_folder(self):
        """the documented `package --out dist`, from another folder than the repository's: Hugo, the checks and
        Python must all mean the same folder"""
        tmp = Path(tempfile.mkdtemp(prefix='lead-package-test-'))
        self.addCleanup(shutil.rmtree, tmp)
        repo, work = tmp / 'repo', tmp / 'work'
        committed_copy(repo)
        work.mkdir()
        r = subprocess.run([sys.executable, str(repo / 'tools/deploy.py'), 'package', '--out', 'dist'], cwd=str(work),
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.assertEqual(r.returncode, 0, r.stdout[-3000:])
        short = subprocess.run(['git', '-C', str(repo), 'rev-parse', '--short', 'HEAD'], stdout=subprocess.PIPE,
                               universal_newlines=True, check=True).stdout.strip()
        stage = work / 'dist' / ('lead-dbs-site-' + short)
        self.assertTrue((work / 'dist' / ('lead-dbs-site-' + short + '.tar.gz')).is_file())
        self.assertFalse((repo / 'dist').exists(), 'built into the source instead')
        with quiet():
            manifest = deploy.read_manifest(str(stage / 'site'))     # exits on any difference
        self.assertGreater(len(manifest['files']), 100)
        self.assertIn('index.html', manifest['files'])
        policy = deploy.page_policy((stage / 'site' / '.htaccess').read_text())
        self.assertIn("'sha256-", policy)
        self.assertTrue((stage / 'deploy.py').is_file())


@needs(HTTPD and MODULES and HUGO and shutil.which('openssl') and Path(MODULES, 'mod_ssl.so').exists(), 'Apache (httpd or apache2 with mod_rewrite) and hugo')
class ApacheTests(unittest.TestCase):
    """the deployed web root on a local Apache with AllowOverride All, as on STRATO. The server's own MIME list
    is empty: the .htaccess has to name every type the site serves."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='lead-apache-'))
        cls.web, cls.state, cls.site = cls.tmp / 'web', cls.tmp / 'state', cls.tmp / 'package' / 'site'
        make_webroot(cls.web)
        make_site(cls.site)
        cls.before = tree(cls.web)
        run('deploy', cls.site, cls.web, '--state', cls.state)
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            cls.port = s.getsockname()[1]
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            cls.tls_port = s.getsockname()[1]
        subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes', '-days', '1',
                        '-subj', '/CN=localhost', '-keyout', str(cls.tmp / 'key.pem'),
                        '-out', str(cls.tmp / 'cert.pem')], check=True, capture_output=True)
        mods = ['mpm_prefork', 'unixd', 'authz_core', 'dir', 'mime', 'rewrite', 'headers', 'alias', 'deflate',
                'filter', 'log_config', 'env', 'setenvif', 'socache_shmcb', 'ssl']
        load = '\n'.join('LoadModule {}_module {}/mod_{}.so'.format(m, MODULES, m)
                         for m in mods if Path(MODULES, 'mod_%s.so' % m).exists())
        (cls.tmp / 'mime.types').write_text('')   # Debian's mod_mime wants a file; the .htaccess sets the types
        (cls.tmp / 'httpd.conf').write_text(f"""
ServerRoot "{cls.tmp}"
Mutex file:{cls.tmp} default
Listen 127.0.0.1:{cls.port}
Listen 127.0.0.1:{cls.tls_port}
PidFile "{cls.tmp}/httpd.pid"
TypesConfig "{cls.tmp}/mime.types"
ErrorLog "{cls.tmp}/error.log"
{load}
ServerName www.lead-dbs.org
DocumentRoot "{cls.web}"
<Directory />
  AllowOverride None
  Require all denied
</Directory>
<Directory "{cls.web}">
  AllowOverride All
  Require all granted
</Directory>
<VirtualHost 127.0.0.1:{cls.tls_port}>
  ServerName www.lead-dbs.org
  DocumentRoot "{cls.web}"
  SSLEngine on
  SSLCertificateFile "{cls.tmp}/cert.pem"
  SSLCertificateKeyFile "{cls.tmp}/key.pem"
</VirtualHost>
# as on shared hosting with PHP: a folder's index.php when it has no index.html
DirectoryIndex index.html index.php
""")
        # its own session: Apache signals its process group when it stops
        cls.proc = subprocess.Popen([HTTPD, '-f', str(cls.tmp / 'httpd.conf'), '-DFOREGROUND'],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(100):
            try:
                with socket.create_connection(('127.0.0.1', cls.port), timeout=.1):
                    break
            except OSError:
                time.sleep(.05)
        else:
            raise RuntimeError('Apache did not start: ' + (cls.tmp / 'error.log').read_text())

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=10)
        shutil.rmtree(cls.tmp)

    def request(self, path, host='www.lead-dbs.org', https=True, method='GET', **headers):
        """status, headers and the raw body"""
        con = (http.client.HTTPSConnection('127.0.0.1', self.tls_port, timeout=5,
                                            context=ssl._create_unverified_context()) if https else
               http.client.HTTPConnection('127.0.0.1', self.port, timeout=5))
        headers = {'Host': host, **{k.replace('_', '-'): v for k, v in headers.items()}}
        con.request(method, path, headers=headers)
        r = con.getresponse()
        body = r.read()
        con.close()
        return r.status, r, body

    def get(self, path, host='www.lead-dbs.org', https=True):
        status, r, body = self.request(path, host, https)
        return status, r.getheader('Location'), body.decode('utf-8', 'replace'), r

    def test_pages_come_from_the_build(self):
        status, _, body, r = self.get('/')
        self.assertEqual(status, 200)
        self.assertIn('<title>', body)
        self.assertNotIn('WORDPRESS', body)
        self.assertEqual(r.getheader('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(self.get('/about/')[0], 200)
        self.assertEqual(self.get('/lead-dbs-3-0-out-now/')[0], 200)

    def test_wordpress_keeps_the_newsletter_admin_and_old_ids(self):
        for path in ('/?na=view&id=29', '/?na=s', '/?na=u&nk=1-abc', '/?p=123', '/?page_id=45', '/wp-json/wp/v2/posts'):
            with self.subTest(path=path):
                status, _, body, _ = self.get(path)
                self.assertEqual((status, body), (200, 'WORDPRESS index.php'))
        self.assertEqual(self.get('/wp-admin/')[2], 'WORDPRESS admin')
        self.assertEqual(self.get('/wp-login.php')[2], 'WORDPRESS login')

    def test_the_other_folders_are_served_as_they_are(self):
        self.assertEqual(self.get('/release/download.php?id=lead-dbs')[2], 'RELEASE download.php')
        self.assertEqual(self.get('/docs/talks/AAN_presentation_Horn_2017.pdf')[2], 'DOCS pdf')
        self.assertEqual(self.get('/wp-content/uploads/2015/11/Ilinskyetal15last.pdf')[2], 'UPLOAD pdf')
        self.assertEqual(self.get('/forms/send.php')[2], 'FORMS send.php')
        self.assertEqual(self.get('/google1234.html')[2], 'search console proof')
        self.assertEqual(self.get('/.well-known/acme-challenge/token123')[2], 'ACME token')

    def test_private_files_are_never_served(self):
        paths = ['/' + rel for rel in PRIVATE] + ['/.htaccess', '/release/.htaccess', '/release/logs/2026-11.log',
                                                  '/release/%2egit/config', '/VENDOR/demo.txt',
                                                  '/index.html.lead-deploy-0123abcd.tmp']
        for path in paths:
            with self.subTest(path=path):
                status, _, body, _ = self.get(path)
                self.assertIn(status, (403, 404))
                self.assertNotIn('SECRET', body)

    def test_retired_forum_and_author_addresses_are_permanent_redirects(self):
        """every redirect page of the build under /forums/ and /author/ gets an HTTP 301 to the same place"""
        build = self.site
        stubs = [p for family in ('forums', 'author') for p in (build / family).rglob('index.html')]
        self.assertGreater(len(stubs), 900)
        for page in stubs:
            path = '/' + str(page.parent.relative_to(build)) + '/'
            target = re.search(r'url=https://www\.lead-dbs\.org(/[^"\s>]*)', page.read_text())[1]
            status, location, _, _ = self.get(path)
            if (status, (location or '').endswith(target)) != (301, True):
                self.fail('{} answered {} {} instead of 301 {}'.format(path, status, location, target))
        for path, to in (('/forums/topic/some-question/?replies=3', '/helpsupport/forum/'),
                         ('/forums/users/someone/', '/helpsupport/forum/'),
                         ('/forums', '/helpsupport/forum/'),
                         ('/author/andreashorn/page/2/?x=1', '/about/team/')):
            with self.subTest(path=path):
                status, location, _, _ = self.get(path)
                self.assertEqual(status, 301)
                self.assertTrue(location.endswith(to), location)   # old query strings are dropped

    def test_redirects(self):
        cases = {
            '/?s=atlas': '/search/?q=atlas',
            '/feed/': '/news/index.xml',
            '/news/feed/': '/news/index.xml',
            '/comments/feed/': '/news/index.xml',
        }
        for path, to in cases.items():
            with self.subTest(path=path):
                status, location, _, _ = self.get(path)
                self.assertEqual(status, 301)
                self.assertTrue(location.endswith(to), location)
        status, location, _, _ = self.get('/about/', host='lead-dbs.org')
        self.assertEqual((status, location), (301, 'https://www.lead-dbs.org/about/'))
        status, location, _, _ = self.get('/about/?x=1', https=False)
        self.assertEqual((status, location), (301, 'https://www.lead-dbs.org/about/?x=1'))
        self.assertEqual(self.get('/contact')[0], 301)  # the trailing slash

    def test_unknown_addresses_get_the_404_page_not_wordpress(self):
        status, _, body, _ = self.get('/no-such-page/')
        self.assertEqual(status, 404)
        self.assertNotIn('WORDPRESS', body)
        self.assertIn('<title>', body)
        self.assertEqual(self.get('/xmlrpc.php')[0], 410)

    def files(self, pattern):
        return sorted('/' + str(p.relative_to(self.web)) for p in self.web.rglob(pattern) if p.is_file())

    def test_caching(self):
        year, month = 'public, max-age=31536000, immutable', 'public, max-age=2592000'
        cases = {
            self.files('css/*.css')[0]: year,
            self.files('js/main.min.*.js')[0]: year,
            self.files('data/*.json')[0]: year,          # fingerprinted data
            self.files('*_hu_*.webp')[0]: year,          # Hugo's processed images
            self.files('media/*.mp4')[0]: month,
            self.files('fonts/*.woff2')[0]: year if re.search(r'\.[0-9a-f]{64}\.woff2$', self.files('fonts/*.woff2')[0]) else month,
            '/favicon.ico': month,
            '/': 'no-cache',
            '/about/': 'no-cache',
            '/sitemap.xml': 'no-cache',
            '/news/index.xml': 'no-cache',
            '/search-index.json': 'no-cache',
            '/robots.txt': 'no-cache',
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                status, r, _ = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(r.getheader('Cache-Control'), expected)

    def test_every_type_the_build_serves_has_its_mime_type(self):
        types = {'html': 'text/html', 'css': 'text/css', 'js': 'text/javascript', 'json': 'application/json',
                 'xml': 'application/rss+xml', 'txt': 'text/plain', 'svg': 'image/svg+xml', 'webp': 'image/webp',
                 'avif': 'image/avif', 'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                 'gif': 'image/gif', 'ico': 'image/x-icon', 'woff2': 'font/woff2', 'mp4': 'video/mp4',
                 'webm': 'video/webm', 'pdf': 'application/pdf', 'webmanifest': 'application/manifest+json'}
        found = {}
        for p in sorted(self.site.rglob('*')):
            if p.is_file() and p.name != '.htaccess':
                found.setdefault(p.suffix.lstrip('.').lower(), '/' + str(p.relative_to(self.site)))
        self.assertEqual(sorted(set(found) - set(types)), [], 'a file type without an entry here and in the .htaccess')
        for ext, path in found.items():
            with self.subTest(ext=ext):
                status, r, _ = self.request(path)
                self.assertEqual(status, 200)
                self.assertEqual(r.getheader('Content-Type').split(';')[0], types[ext])
        self.assertEqual(self.request('/sitemap.xml')[1].getheader('Content-Type'), 'application/xml; charset=utf-8')
        self.assertEqual(self.request('/news/index.xml')[1].getheader('Content-Type'), 'application/rss+xml; charset=utf-8')

    def test_text_is_compressed_for_clients_that_ask(self):
        for path in ['/', self.files('css/*.css')[0], self.files('js/main.min.*.js')[0], '/search-index.json',
                     '/sitemap.xml', self.files('images/*.svg')[0]]:
            with self.subTest(path=path):
                status, r, body = self.request(path, Accept_Encoding='gzip')
                self.assertEqual((status, r.getheader('Content-Encoding')), (200, 'gzip'))
                self.assertIn('Accept-Encoding', r.getheader('Vary'))
                plain = self.request(path)
                self.assertIsNone(plain[1].getheader('Content-Encoding'))
                self.assertEqual(gzip.decompress(body), plain[2])
        for path in (self.files('*_hu_*.webp')[0], self.files('media/*.mp4')[0], self.files('fonts/*.woff2')[0]):
            with self.subTest(path=path):
                self.assertIsNone(self.request(path, Accept_Encoding='gzip')[1].getheader('Content-Encoding'))

    def test_videos_answer_byte_ranges(self):
        path = self.files('media/*.mp4')[0]
        size = (self.web / path.lstrip('/')).stat().st_size
        status, r, body = self.request(path, Range='bytes=100-199', Accept_Encoding='gzip')
        self.assertEqual(status, 206)
        self.assertEqual(r.getheader('Content-Range'), 'bytes 100-199/{}'.format(size))
        self.assertEqual(body, (self.web / path.lstrip('/')).read_bytes()[100:200])
        self.assertEqual(r.getheader('Accept-Ranges'), 'bytes')

    def test_security_headers(self):
        status, r, body = self.request('/')
        self.assertEqual(status, 200)
        policy = r.getheader('Content-Security-Policy-Report-Only')
        self.assertIsNotNone(policy)
        self.assertIsNone(r.getheader('Content-Security-Policy'), 'enforced before its time')
        for directive in ("object-src 'none'", "base-uri 'self'", "frame-ancestors 'self'", "form-action 'self'",
                          "frame-src https://www.youtube-nocookie.com https://player.vimeo.com"):
            self.assertIn(directive, policy)
        parser = deploy.InlineScripts()
        parser.feed(body.decode())
        self.assertTrue(parser.scripts)
        for script in parser.scripts:
            h = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
            self.assertIn("'sha256-" + h + "'", policy)
        self.assertEqual(r.getheader('Strict-Transport-Security'), 'max-age=86400')
        self.assertEqual(r.getheader('X-Frame-Options'), 'SAMEORIGIN')
        # WordPress and the PHP folders answer with their own policies
        for path in ('/?na=s', '/wp-admin/', '/release/download.php'):
            with self.subTest(path=path):
                self.assertIsNone(self.request(path)[1].getheader('Content-Security-Policy-Report-Only'))
        # no HSTS over plain HTTP: the redirect to HTTPS comes first
        status, r, _ = self.request('/about/', https=False)
        self.assertEqual(status, 301)
        self.assertIsNone(r.getheader('Strict-Transport-Security'))

    def test_documented_trusted_proxy_alternative(self):
        docs = (ROOT / 'docs/launch.md').read_text()
        proxy = docs.split('**Proxy alternative (only after confirmation).**', 1)[1]
        redirect, hsts = [block.strip() for block in re.findall(r'```apache\n(.*?)\n\s*```', proxy, re.S)[:2]]
        htaccess = self.web / '.htaccess'
        direct = htaccess.read_text()
        changed = re.sub(r'  RewriteCond %\{HTTPS\} !=on.*?\[R=301,L,NE\]', lambda m: redirect, direct, count=1, flags=re.S)
        changed = re.sub(r'  Header always set Strict-Transport-Security[^\n]+', hsts, changed)
        try:
            htaccess.write_text(changed)
            status, r, _ = self.request('/about/', https=False, X_Forwarded_Proto='https')
            self.assertEqual(status, 200)
            self.assertEqual(r.getheader('Strict-Transport-Security'), 'max-age=86400')
            status, r, _ = self.request('/about/', https=False, X_Forwarded_Proto='http')
            self.assertEqual(status, 301)
            self.assertIsNone(r.getheader('Strict-Transport-Security'))
            self.assertEqual(self.request('/about/')[0], 200)
        finally:
            htaccess.write_text(direct)

    def test_forwarded_headers_cannot_forge_direct_tls(self):
        for proto in ('https', 'HTTPS', 'https, http'):
            status, r, _ = self.request('/about/', https=False, X_Forwarded_Proto=proto)
            self.assertEqual(status, 301)
            self.assertEqual(r.getheader('Location'), 'https://www.lead-dbs.org/about/')
            self.assertIsNone(r.getheader('Strict-Transport-Security'))
        status, r, _ = self.request('/about/', X_Forwarded_Proto='http')
        self.assertEqual(status, 200)
        self.assertEqual(r.getheader('Strict-Transport-Security'), 'max-age=86400')

    def test_zz_after_a_rollback_wordpress_answers_everything_again(self):
        run('rollback', self.web, '--state', self.state)
        self.assertEqual(tree(self.web), self.before)
        self.assertEqual(self.get('/')[2], 'WORDPRESS index.php')
        self.assertEqual(self.get('/about/')[2], 'WORDPRESS index.php')
        self.assertEqual(self.get('/release/download.php')[2], 'RELEASE download.php')


if __name__ == '__main__':
    unittest.main()
