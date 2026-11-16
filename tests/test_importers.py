"""The one-time importers (tools/import_wordpress.py, tools/import_manual.py), run offline against small fixtures.

Every network path is replaced: urllib's OpenerDirector.open (used by every WordPress request, download and redirect
lookup) answers only the URLs a test lists and fails the test on any other, and the manual importer's fetch() is a
fake while curl itself is blocked. Every output goes to a temporary folder that stands in for the repository.
"""
import contextlib
import email.message
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import urllib.error
import urllib.request

from prerequisites import needs
from tools import import_manual as im

try:
    from tools import import_wordpress as wp
except ImportError:  # beautifulsoup4 or markdownify is not installed
    wp = None

SITE = 'https://www.lead-dbs.org'
API = SITE + '/wp-json/wp/v2'
GITBOOK = 'https://netstim.gitbook.io/leaddbs/'
PNG = b'\x89PNG\r\n\x1a\n' + bytes(24)
DOWNLOAD = SITE + '/?sdm_process_download=1&download_id=7'
DOWNLOAD_TARGET = 'https://downloads.example.org/lead-dbs.zip'
PICTURE = SITE + '/wp-content/uploads/2020/01/pic.png'
FEATURED = SITE + '/wp-content/uploads/2020/01/feat.png'


def wp_item(item_id, link, body, **fields):
    return {'id': item_id, 'parent': 0, 'link': link, 'slug': link.rstrip('/').rsplit('/', 1)[-1],
            'title': {'rendered': 'Title'}, 'content': {'rendered': body}, 'date': '2020-01-01T00:00:00',
            'modified': '2020-01-02T00:00:00', 'menu_order': 0, 'featured_media': 0, **fields}


PAGE = wp_item(1, SITE + '/about/', f'<p>Get <a href="{DOWNLOAD.replace("&", "&amp;")}">Lead-DBS</a></p>'
                                    f'<p><img src="{PICTURE}" alt="Pic"></p>')
POST = wp_item(10, SITE + '/2020/01/hello/', '<p>News text</p>', featured_media=55)


class Redirect:
    def __init__(self, location):
        self.location = location


class FakeResponse(io.BytesIO):
    def __init__(self, data):
        super().__init__(data)
        self.headers = {'Content-Length': str(len(data))}


class FakeWeb:
    """Stands in for the internet: answers only the URLs it was given and records every request."""

    def __init__(self, routes):
        self.routes = routes
        self.requests = []

    def open(self, fullurl, data=None, timeout=None):
        url = fullurl.full_url if isinstance(fullurl, urllib.request.Request) else fullurl
        self.requests.append(url)
        if url not in self.routes:
            raise AssertionError('unexpected network request: ' + url)
        answer = self.routes[url]
        if isinstance(answer, Redirect):
            headers = email.message.Message()
            headers['Location'] = answer.location
            raise urllib.error.HTTPError(url, 302, 'Found', headers, None)
        if isinstance(answer, BaseException):
            raise answer
        return FakeResponse(answer)

    @contextlib.contextmanager
    def active(self):
        def opener_open(opener, fullurl, data=None, timeout=None):
            return self.open(fullurl, data, timeout)
        with mock.patch.object(urllib.request.OpenerDirector, 'open', opener_open):
            yield self

    def api_requests(self):
        return [url for url in self.requests if '/wp-json/' in url or 'sdm_process_download' in url]


def wordpress_web(pages=(PAGE,), posts=(POST,), media=None, **overrides):
    routes = {}
    for kind, items in (('pages', pages), ('posts', posts)):
        routes[f'{API}/{kind}?per_page=100&page=1'] = json.dumps(list(items)).encode()
        routes[f'{API}/{kind}?per_page=100&page=2'] = b'[]'
    routes[f'{API}/media/55'] = json.dumps(media or {'source_url': FEATURED}).encode()
    routes[DOWNLOAD] = Redirect(DOWNLOAD_TARGET)
    routes[PICTURE] = PNG
    routes[FEATURED] = PNG
    routes.update(overrides)
    return FakeWeb(routes)


def listing(folder):
    """Every file and folder below folder, relative to it."""
    return sorted(str(p.relative_to(folder)) for p in Path(folder).rglob('*'))


@needs(wp is not None, 'the WordPress importer needs beautifulsoup4 and markdownify')
class WordPressImportTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()
        self.repo = self.tmp / 'repo'  # stands in for the repository
        (self.repo / 'content').mkdir(parents=True)
        self.site = self.tmp / 'site'  # an existing editorial tree, for --in-place

    def run_import(self, web, *args):
        output = io.StringIO()
        argv = ['import_wordpress.py', *map(str, args)]
        with web.active(), mock.patch.object(sys, 'argv', argv), \
                mock.patch.object(wp, 'ROOT', self.repo, create=True), \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            wp.main()
        return output.getvalue()

    def edited(self, relative, text='edited by hand\n'):
        path = self.site / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_existing_post_is_skipped_before_its_featured_media_is_fetched(self):
        post = self.edited('news/hello/index.md')
        web = wordpress_web()
        self.run_import(web, '--out', self.site, '--in-place')
        self.assertEqual(post.read_text(), 'edited by hand\n')
        self.assertNotIn(f'{API}/media/55', web.requests)
        self.assertNotIn(FEATURED, web.requests)
        self.assertEqual(listing(post.parent), ['index.md'])

    def test_download_links_are_resolved_only_for_pages_that_are_written(self):
        page = self.edited('about/index.md')
        web = wordpress_web()
        self.run_import(web, '--out', self.site, '--in-place')
        self.assertEqual(page.read_text(), 'edited by hand\n')
        self.assertNotIn(DOWNLOAD, web.requests)
        self.assertNotIn(PICTURE, web.requests)

    def test_news_index_is_kept_unless_forced(self):
        index = self.edited('news/_index.md', '---\ntitle: "Updates"\n---\n')
        self.run_import(wordpress_web(), '--out', self.site, '--in-place')
        self.assertEqual(index.read_text(), '---\ntitle: "Updates"\n---\n')
        self.run_import(wordpress_web(), '--out', self.site, '--in-place', '--force')
        self.assertIn('"News"', index.read_text())

    def test_plan_reports_without_writing_or_downloading(self):
        out, snapshot = self.tmp / 'work' / 'site', self.tmp / 'snapshot'
        web = wordpress_web()
        report = self.run_import(web, '--plan', '--out', out, '--snapshot', snapshot)
        self.assertIn(f'would write {out / "about" / "index.md"}', report)
        self.assertIn(f'would write {out / "news" / "hello" / "index.md"}', report)
        self.assertFalse(out.exists())
        self.assertFalse(snapshot.exists())
        self.assertFalse((self.tmp / 'work').exists())
        self.assertEqual(web.requests, [f'{API}/pages?per_page=100&page=1', f'{API}/pages?per_page=100&page=2',
                                        f'{API}/posts?per_page=100&page=1', f'{API}/posts?per_page=100&page=2'])

    def test_rerun_from_snapshot_asks_wordpress_for_nothing(self):
        snapshot = self.tmp / 'snapshot'
        first, second = self.tmp / 'work' / 'first', self.tmp / 'work' / 'second'
        self.run_import(wordpress_web(), '--out', first, '--snapshot', snapshot)
        self.assertEqual(listing(snapshot), ['media', 'media/55.json', 'pages.json', 'posts.json', 'redirects.json'])

        offline = FakeWeb({PICTURE: PNG, FEATURED: PNG})  # images only: any API request fails the test
        self.run_import(offline, '--out', second, '--snapshot', snapshot)
        self.assertEqual(offline.api_requests(), [])
        self.assertEqual(listing(first), listing(second))
        for name in ('about/index.md', 'news/hello/index.md', 'news/_index.md'):
            self.assertEqual((first / name).read_text(), (second / name).read_text())
        about = (second / 'about' / 'index.md').read_text()
        self.assertIn(DOWNLOAD_TARGET, about)
        self.assertIn('![Pic](pic.png)', about)
        self.assertIn('image: "feat.png"', (second / 'news' / 'hello' / 'index.md').read_text())

    def test_traversing_page_link_or_post_slug_is_refused(self):
        cases = {'page link': dict(pages=[wp_item(2, SITE + '/../../escape/', '<p>x</p>')], posts=[]),
                 'post slug': dict(pages=[], posts=[wp_item(11, SITE + '/2020/x/', '<p>x</p>', slug='..')])}
        for case, items in cases.items():
            with self.subTest(case):
                parent = self.tmp / case / 'a' / 'b'
                with self.assertRaises(SystemExit):
                    self.run_import(wordpress_web(**items), '--out', parent / 'site')
                self.assertEqual(listing(self.tmp / case), ['a', 'a/b'])

    def test_unsafe_bundle_file_name_is_refused(self):
        for number, name in enumerate(('..', '.', '%2e%2e')):
            with self.subTest(name=name):
                page = wp_item(3, SITE + '/odd/', f'<p><img src="{SITE}/wp-content/uploads/{name}"></p>')
                out = self.tmp / f'case{number}' / 'site'
                web = wordpress_web(pages=[page], posts=[])
                with self.assertRaises(SystemExit):
                    self.run_import(web, '--out', out)
                self.assertNotIn(f'{SITE}/wp-content/uploads/{name}', web.requests)
                self.assertEqual(listing(out.parent), [])

    def test_assets_from_other_origins_are_refused(self):
        sources = ('https://evil.example/x.png', 'http://www.lead-dbs.org/wp-content/uploads/x.png',
                   'https://www.lead-dbs.org.evil.example/x.png', 'https://user@evil.example/x.png')
        for number, source in enumerate(sources):
            with self.subTest(source=source):
                out = self.tmp / f'case{number}' / 'site'
                web = wordpress_web(pages=[], media={'source_url': source})
                with self.assertRaises(SystemExit):
                    self.run_import(web, '--out', out)
                self.assertNotIn(source, web.requests)
                self.assertEqual(listing(out.parent), [])

    def test_download_redirect_to_another_origin_is_refused(self):
        handler = wp.AssetRedirect()
        request = urllib.request.Request(PICTURE)
        with self.assertRaises(wp.UnsafeImport):
            handler.redirect_request(request, None, 302, 'Found', {}, 'https://evil.example/pic.png')
        followed = handler.redirect_request(request, None, 302, 'Found', {}, 'https://lead-dbs.org/pic.png')
        self.assertEqual(followed.full_url, 'https://lead-dbs.org/pic.png')

    def test_output_must_be_new_and_outside_the_repository_unless_in_place(self):
        self.edited('about/index.md')
        for out in (self.repo / 'content', self.repo / 'staging', self.site):
            with self.subTest(out=out):
                before = listing(self.tmp)
                web = wordpress_web()
                with self.assertRaises(SystemExit):
                    self.run_import(web, '--out', out)
                self.assertEqual(web.requests, [])
                self.assertEqual(listing(self.tmp), before)

    def test_failed_import_leaves_nothing_and_can_be_retried(self):
        out = self.tmp / 'work' / 'site'
        with self.assertRaises(urllib.error.URLError):
            self.run_import(wordpress_web(**{FEATURED: urllib.error.URLError('connection reset')}), '--out', out)
        self.assertEqual(listing(out.parent), [])
        self.run_import(wordpress_web(), '--out', out)
        self.assertEqual(listing(out), ['about', 'about/index.md', 'about/pic.png', 'news',
                                        'news/_index.md', 'news/hello', 'news/hello/feat.png',
                                        'news/hello/index.md'])


README = ('# Lead-DBS\n\nWelcome. See [Installation](getting-started/installation.md).\n\n'
          '<figure><img src="https://files.gitbook.example/one.png" alt="One"><figcaption>First</figcaption></figure>\n')
INSTALL = '# Installation\n\n![](https://files.gitbook.example/two.png)\n'
CHAPTERS = {'readme.md': ('Lead-DBS', README), 'getting-started/installation.md': ('Installation', INSTALL)}
IMAGES = ('https://files.gitbook.example/one.png', 'https://files.gitbook.example/two.png')


class FakeFetch:
    """Stands in for the manual importer's fetch(): answers only the URLs it was given and records every request."""

    def __init__(self, routes):
        self.routes = routes
        self.requests = []

    def __call__(self, url):
        self.requests.append(url)
        if url not in self.routes:
            raise AssertionError('unexpected network request: ' + url)
        answer = self.routes[url]
        if isinstance(answer, BaseException):
            raise answer
        return answer


def no_curl(*args, **kwargs):
    raise AssertionError(f'unexpected subprocess: {args}')


class ManualImportTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.tmp = Path(temp.name).resolve()
        self.repo = self.tmp / 'repo'  # stands in for the repository
        (self.repo / 'content').mkdir(parents=True)
        self.cache = self.tmp / 'c1' / 'c2' / 'cache'

    def run_import(self, fetch, *args):
        argv = ['import_manual.py', *map(str, args), str(self.cache)]
        output = io.StringIO()
        with mock.patch.object(im, 'fetch', fetch), mock.patch.object(subprocess, 'check_output', no_curl), \
                mock.patch.object(sys, 'argv', argv), mock.patch.object(im, 'ROOT', self.repo), \
                mock.patch.object(im, 'OUT', self.repo / 'content' / 'manual', create=True), \
                mock.patch.object(im, 'CACHE', self.cache, create=True), contextlib.redirect_stdout(output):
            im.main()
        return output.getvalue()

    def write_cache(self, chapters=CHAPTERS, extra_rows=()):
        rows = [[title, GITBOOK + slug] for slug, (title, _) in chapters.items()] + list(extra_rows)
        self.cache.mkdir(parents=True)
        (self.cache / 'index.json').write_text(json.dumps(rows))
        for slug, (_, text) in chapters.items():
            (self.cache / slug).parent.mkdir(parents=True, exist_ok=True)
            (self.cache / slug).write_text(text)

    def test_failed_download_leaves_no_manual_and_a_retry_succeeds(self):
        self.write_cache()
        failing = FakeFetch({IMAGES[0]: PNG, IMAGES[1]: subprocess.CalledProcessError(22, 'curl')})
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_import(failing)
        self.assertEqual(listing(self.repo), ['content'])

        self.run_import(FakeFetch({IMAGES[0]: PNG, IMAGES[1]: PNG}))
        readme = (self.repo / 'content' / 'manual' / '_index.md').read_text()
        self.assertIn('[Installation](/manual/getting-started/installation/)', readme)
        self.assertTrue((self.repo / 'content' / 'manual' / 'getting-started' / 'installation' / '_index.md').exists())
        self.assertEqual(len(list((self.repo / 'assets' / 'manual').iterdir())), 2)
        pages = json.loads((self.repo / 'data' / 'manual.json').read_text())['pages']
        self.assertEqual([p['page'] for p in pages], ['/manual/', '/manual/getting-started/installation/'])
        self.assertEqual(sorted(os.listdir(self.repo)), ['assets', 'content', 'data'])

        # The manual now exists, so the importer refuses to run again.
        unused = FakeFetch({})
        with self.assertRaises(SystemExit):
            self.run_import(unused)
        self.assertEqual(unused.requests, [])

    def test_each_publication_move_failure_is_undone_and_retryable(self):
        self.write_cache()
        rename = Path.rename
        for cut in range(1, 5):  # two images, content, navigation
            with self.subTest(move=cut):
                calls = [0]
                def failing(src, dst):
                    calls[0] += 1
                    if calls[0] == cut:
                        raise OSError('publication interrupted')
                    return rename(src, dst)
                with mock.patch.object(Path, 'rename', failing), self.assertRaises(OSError):
                    self.run_import(FakeFetch({image: PNG for image in IMAGES}))
                self.assertEqual(listing(self.repo), ['content'])
        self.run_import(FakeFetch({image: PNG for image in IMAGES}))
        self.assertTrue((self.repo / 'data/manual.json').exists())

    def test_interrupted_recovery_keeps_staging_and_can_be_retried(self):
        self.write_cache()
        rename = Path.rename
        def failing(src, dst):
            if src.name == 'manual.json' or str(dst).find('.manual-import-') >= 0:
                raise OSError('publication and undo interrupted')
            return rename(src, dst)
        with mock.patch.object(Path, 'rename', failing), self.assertRaises(OSError):
            self.run_import(FakeFetch({image: PNG for image in IMAGES}))
        stage, = self.repo.glob('.manual-import-*')
        self.assertTrue((stage / 'manual.json').exists())
        self.assertTrue((stage / 'publication.json').exists())
        with self.assertRaises(SystemExit):
            self.run_import(FakeFetch({}))
        self.run_import(FakeFetch({}), '--recover', stage)
        self.assertEqual(listing(self.repo), ['content'])
        self.run_import(FakeFetch({image: PNG for image in IMAGES}))
        self.assertTrue((self.repo / 'data/manual.json').exists())

    def test_index_url_outside_the_gitbook_is_refused(self):
        urls = ('https://evil.example/leaddbs/x.md', 'http://netstim.gitbook.io/leaddbs/x.md',
                'https://netstim.gitbook.io.evil.example/leaddbs/x.md', GITBOOK + 'x.txt')
        for number, url in enumerate(urls):
            with self.subTest(url=url):
                self.cache = self.tmp / f'case{number}' / 'cache'
                self.write_cache(extra_rows=[['Elsewhere', url]])
                fetch = FakeFetch({url: b'# Elsewhere\n', **{image: PNG for image in IMAGES}})
                with self.assertRaises(SystemExit):
                    self.run_import(fetch)
                self.assertEqual(fetch.requests, [])
                self.assertEqual(listing(self.repo), ['content'])

    def test_chapter_path_that_leaves_the_cache_is_refused(self):
        for number, slug in enumerate(('../../../outside.md', 'lead-dbs/../../../outside.md', 'lead-dbs/./outside.md')):
            with self.subTest(slug=slug):
                self.cache = self.tmp / 'c1' / 'c2' / f'case{number}' / 'cache'
                self.write_cache(extra_rows=[['Outside', GITBOOK + slug]])
                before = listing(self.tmp)
                fetch = FakeFetch({GITBOOK + slug: b'# Outside\n', **{image: PNG for image in IMAGES}})
                with self.assertRaises(SystemExit):
                    self.run_import(fetch)
                self.assertEqual(fetch.requests, [])
                self.assertEqual(listing(self.tmp), before)

    def test_image_that_is_not_https_on_a_public_host_is_refused(self):
        images = ('http://files.gitbook.example/x.png', 'https://127.0.0.1/x.png', 'https://localhost/x.png',
                  'https://user@files.gitbook.example/x.png', 'https://files.gitbook.example:8443/x.png')
        for number, image in enumerate(images):
            with self.subTest(image=image):
                self.cache = self.tmp / f'case{number}' / 'cache'
                self.write_cache({'readme.md': ('Lead-DBS', f'# Lead-DBS\n\n![]({image})\n')})
                fetch = FakeFetch({image: PNG})
                with self.assertRaises(SystemExit):
                    self.run_import(fetch)
                self.assertEqual(fetch.requests, [])
                self.assertEqual(listing(self.repo), ['content'])

    def test_plan_reports_without_writing_or_downloading(self):
        llms = ''.join(f'- [{title}]({GITBOOK}{slug})\n' for slug, (title, _) in CHAPTERS.items())
        routes = {GITBOOK + 'llms.txt': llms.encode()}
        routes.update({GITBOOK + slug: text.encode() for slug, (_, text) in CHAPTERS.items()})
        fetch = FakeFetch(routes)
        report = self.run_import(fetch, '--plan')
        self.assertIn('would write content/manual/_index.md', report)
        self.assertIn('would write content/manual/getting-started/installation/_index.md', report)
        self.assertIn('would download 2 of 2 images', report)
        self.assertEqual(listing(self.repo), ['content'])
        self.assertFalse(self.cache.exists())
        self.assertFalse(set(IMAGES) & set(fetch.requests))

    def test_curl_is_limited_to_https_including_redirects(self):
        with mock.patch.object(subprocess, 'check_output', return_value=b'body') as curl:
            self.assertEqual(im.fetch(GITBOOK + 'readme.md'), b'body')
        command = curl.call_args.args[0]
        self.assertEqual(command[command.index('--proto') + 1], '=https')
        self.assertEqual(command[command.index('--proto-redir') + 1], '=https')


if __name__ == '__main__':
    unittest.main()
