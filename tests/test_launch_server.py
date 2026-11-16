"""The switch, rehearsed on this computer: a fake lead-dbs.org web root (WordPress stubs, /release/, /docs/,
/forms/, uploads, WordPress's .htaccess), tools/deploy.py putting the Hugo build in, server/apache/htaccess
answering on a local Apache, and a rollback that leaves the web root exactly as it was. Never talks to
STRATO.

Needs hugo, and Apache for the second half (macOS /usr/sbin/httpd, Debian/Ubuntu apache2); skipped without
them. Set LEAD_TEST_BUILD to a production build folder to skip the Hugo build.
"""
import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEPLOY = [sys.executable, str(ROOT / 'tools/deploy.py')]

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
    'release/download.php': 'RELEASE download.php',
    'release/logs/2026-11.log': 'RELEASE log',
    'docs/talks/AAN_presentation_Horn_2017.pdf': 'DOCS pdf',
    'forms/send.php': 'FORMS send.php',
    'favicon.ico': 'OLD favicon',
    'google1234.html': 'search console proof',
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


def make_site(folder):
    """the site/ folder of a package: the build and its .htaccess (what deploy.py package makes, without git)"""
    shutil.copytree(production_build(), folder)
    shutil.copyfile(ROOT / 'server/apache/htaccess', Path(folder, '.htaccess'))


def run(*args, ok=True):
    r = subprocess.run(DEPLOY + [str(a) for a in args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       universal_newlines=True)
    if ok and r.returncode:
        raise AssertionError(r.stdout)
    return r


@unittest.skipUnless(shutil.which('hugo') or os.environ.get('LEAD_TEST_BUILD'), 'hugo required')
class DeployTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='lead-deploy-'))
        self.addCleanup(shutil.rmtree, self.tmp)
        self.web, self.state, self.site = self.tmp / 'web', self.tmp / 'state', self.tmp / 'site'
        make_webroot(self.web)
        make_site(self.site)
        self.before, self.dirs = tree(self.web), folders(self.web)

    def assertUnchanged(self):
        self.assertEqual(tree(self.web), self.before)
        self.assertEqual(folders(self.web), self.dirs, 'folders left behind')

    def test_deploy_keeps_everything_that_is_not_its_own_and_rollback_restores_it(self):
        plan = run('plan', self.site, self.web, '--state', self.state).stdout
        self.assertIn('REFUSED: 0', plan)
        self.assertIn('  .htaccess', plan)      # replaced, and kept for the rollback
        self.assertIn('  favicon.ico', plan)
        self.assertUnchanged()
        self.assertFalse(self.state.exists(), 'plan wrote its state')
        run('deploy', self.site, self.web, '--state', self.state)
        after = tree(self.web)
        for rel, h in self.before.items():
            if rel not in ('.htaccess', 'favicon.ico'):
                self.assertEqual(after.get(rel), h, rel + ' was changed')
        self.assertEqual(after['.htaccess'], tree(self.site)['.htaccess'])
        self.assertTrue((self.web / 'index.html').exists())
        self.assertFalse(any(p.name.endswith('.lead-deploy-tmp') for p in self.web.rglob('*')))
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_second_deploy_removes_its_old_files_and_rollback_still_restores_the_original(self):
        run('deploy', self.site, self.web, '--state', self.state)
        (self.site / 'gallery' / 'index.html').unlink()
        (self.site / 'index.html').write_text('NEW HOME')
        run('deploy', self.site, self.web, '--state', self.state)
        self.assertFalse((self.web / 'gallery' / 'index.html').exists())
        self.assertEqual((self.web / 'index.html').read_text(), 'NEW HOME')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_a_deploy_cut_off_halfway_can_be_rolled_back(self):
        # the state is written first; simulate a deploy that stopped after some files, before the .htaccess
        run('deploy', self.site, self.web, '--state', self.state)
        state = json.loads((self.state / 'deployed.json').read_text())
        state['complete'] = False
        (self.state / 'deployed.json').write_text(json.dumps(state))
        (self.web / '.htaccess').write_text(WP_HTACCESS)   # it never got this far
        (self.web / 'about' / 'index.html.lead-deploy-tmp').write_text('half copied')
        run('rollback', self.web, '--state', self.state)
        self.assertUnchanged()

    def test_refusals_change_nothing(self):
        cases = []
        bad = self.tmp / 'bad1'
        shutil.copytree(self.site, bad)
        (bad / 'release').mkdir(exist_ok=True)
        (bad / 'release' / 'download.php').write_text('overwrite')
        cases.append((bad, self.web, self.state, 'release/download.php'))
        bad = self.tmp / 'bad2'
        shutil.copytree(self.site, bad)
        (bad / 'wp-config.php').write_text('overwrite')
        cases.append((bad, self.web, self.state, 'wp-config.php'))
        cases.append((self.site, self.web, self.web / 'state', 'outside the web root'))
        noroot = self.tmp / 'not-the-webroot'
        noroot.mkdir()
        cases.append((self.site, noroot, self.state, 'no release/ folder'))
        for site, web, state, why in cases:
            with self.subTest(why=why):
                r = run('deploy', site, web, '--state', state, ok=False)
                self.assertNotEqual(r.returncode, 0)
                self.assertIn(why, r.stdout)
        self.assertUnchanged()
        self.assertFalse((self.web / 'state').exists())

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


@unittest.skipUnless(HTTPD and MODULES and (shutil.which('hugo') or os.environ.get('LEAD_TEST_BUILD')),
                     'Apache (httpd or apache2 with mod_rewrite) and hugo required')
class ApacheTests(unittest.TestCase):
    """the deployed web root on a local Apache with AllowOverride All, as on STRATO"""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix='lead-apache-'))
        cls.web, cls.state, cls.site = cls.tmp / 'web', cls.tmp / 'state', cls.tmp / 'site'
        make_webroot(cls.web)
        make_site(cls.site)
        cls.before = tree(cls.web)
        run('deploy', cls.site, cls.web, '--state', cls.state)
        with socket.socket() as s:
            s.bind(('127.0.0.1', 0))
            cls.port = s.getsockname()[1]
        mods = ['mpm_prefork', 'unixd', 'authz_core', 'dir', 'mime', 'rewrite', 'headers', 'alias', 'deflate',
                'filter', 'log_config', 'env', 'setenvif']
        load = '\n'.join('LoadModule {}_module {}/mod_{}.so'.format(m, MODULES, m)
                         for m in mods if Path(MODULES, 'mod_%s.so' % m).exists())
        (cls.tmp / 'mime.types').write_text('')   # Debian's mod_mime wants a file; the types are set below
        (cls.tmp / 'httpd.conf').write_text(f"""
ServerRoot "{cls.tmp}"
Listen 127.0.0.1:{cls.port}
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
# as on shared hosting with PHP: a folder's index.php when it has no index.html
DirectoryIndex index.html index.php
AddType text/html .html
AddType text/css .css
AddType text/javascript .js
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

    def get(self, path, host='www.lead-dbs.org', https=True):
        con = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        headers = {'Host': host}
        if https:
            headers['X-Forwarded-Proto'] = 'https'
        con.request('GET', path, headers=headers)
        r = con.getresponse()
        body = r.read().decode('utf-8', 'replace')
        con.close()
        return r.status, r.getheader('Location'), body, r

    def test_pages_come_from_the_build(self):
        status, _, body, r = self.get('/')
        self.assertEqual(status, 200)
        self.assertIn('<title>', body)
        self.assertNotIn('WORDPRESS', body)
        self.assertEqual(r.getheader('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(self.get('/about/')[0], 200)
        self.assertEqual(self.get('/lead-dbs-3-0-out-now/')[0], 200)
        self.assertIn('http-equiv', self.get('/author/andreashorn/')[2])   # an old address, now a redirect page

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

    def test_caching(self):
        css = next(p for p in (self.web / 'css').iterdir() if p.suffix == '.css')
        self.assertIn('immutable', self.get('/css/' + css.name)[3].getheader('Cache-Control'))
        self.assertEqual(self.get('/')[3].getheader('Cache-Control'), 'no-cache')

    def test_zz_after_a_rollback_wordpress_answers_everything_again(self):
        run('rollback', self.web, '--state', self.state)
        self.assertEqual(tree(self.web), self.before)
        self.assertEqual(self.get('/')[2], 'WORDPRESS index.php')
        self.assertEqual(self.get('/about/')[2], 'WORDPRESS index.php')
        self.assertEqual(self.get('/release/download.php')[2], 'RELEASE download.php')


if __name__ == '__main__':
    unittest.main()
