"""Real download-hook/MaxMind integration, using only upstream test data."""
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import unittest

from prerequisites import needs

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT/'collector' if (ROOT/'collector').is_dir() else ROOT/'server/analytics'

@needs(shutil.which('php') and (COLLECTOR/'vendor/autoload.php').exists(), 'PHP CLI and composer install required')
class DownloadHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='lead-hook-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.web = self.root/'web'
        shutil.copytree(COLLECTOR, self.web)
        registry = ROOT/'analytics/artifacts.json' if (ROOT/'analytics').is_dir() else COLLECTOR/'artifacts.json'
        shutil.copyfile(registry, self.web/'artifacts.json')
        (self.root/'key').write_bytes(os.urandom(32))
        self.db = self.root/'events.sqlite'
        self.config = self.root/'config.json'
        self.settings = {'database':str(self.db),'key_file':str(self.root/'key'),
            'country_database':str(ROOT/'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb')}
        self.config.write_text(json.dumps(self.settings))
        self.env = {**os.environ, 'LEAD_ANALYTICS_CONFIG':str(self.config)}

    def timed_call(self, artifact='latest', version='3.2', method='GET', **headers):
        """The hook's return value and how long it took inside PHP, in seconds."""
        server = {'REQUEST_METHOD':method, 'REMOTE_ADDR':'81.2.69.160', 'DOCUMENT_ROOT':str(self.web), **headers}
        code = ('$_SERVER=json_decode($argv[2],true); require $argv[1]; $started=microtime(true); '
                '$result=lead_analytics_download($argv[3],"redirect",$argv[4]); '
                'echo json_encode([$result, microtime(true)-$started]);')
        proc = subprocess.run(['php','-r',code,str(self.web/'download-hook.php'),json.dumps(server),artifact,version],
                              env=self.env,capture_output=True,text=True,check=True,timeout=30)
        return json.loads(proc.stdout)

    def call(self, *args, **kwargs):
        return self.timed_call(*args, **kwargs)[0]

    def count_events(self):
        with closing(sqlite3.connect(self.db)) as db:
            return db.execute('SELECT COUNT(*) FROM events').fetchone()[0]

    def test_versions_aliases_and_real_country_lookup(self):
        for artifact,version in [('latest',''),('unrecognized_artifact','v3.2'),('updates_32-321','3.2.1')]:
            self.assertTrue(self.call(artifact,version))
        with closing(sqlite3.connect(self.db)) as db:
            rows = db.execute('SELECT item,app_version,country FROM events ORDER BY item').fetchall()
        self.assertEqual(rows,[('latest','unknown','GB'),('unknown','unknown','GB'),('updates_32-321','3.2.1','GB')])
        self.assertNotIn(b'81.2.69.160',self.db.read_bytes())

    def test_head_and_privacy_signals_do_not_record(self):
        self.assertTrue(self.call(method='HEAD'))
        for header in ['HTTP_DNT','HTTP_SEC_GPC']:
            self.assertTrue(self.call(**{header:'1'}))
        self.assertFalse(self.db.exists())

    def test_missing_registry_fails_without_breaking_response(self):
        (self.web/'artifacts.json').unlink()
        self.assertFalse(self.call())
        self.assertFalse(self.db.exists())

    def test_real_reader_ipv6_and_unknown(self):
        code = 'require $argv[1]; $r=new MaxMind\\Db\\Reader($argv[2]); echo json_encode([$r->get("2001:218::")["country"]["iso_code"],$r->get("127.0.0.1")]);'
        proc = subprocess.run(['php','-r',code,str(COLLECTOR/'vendor/autoload.php'),
                              str(ROOT/'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb')],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(proc.stdout),['JP',None])

    def test_locked_database_returns_false_fast(self):
        self.assertTrue(self.call())
        with closing(sqlite3.connect(self.db, isolation_level=None)) as other:
            other.execute('BEGIN IMMEDIATE')
            result, seconds = self.timed_call()
            other.execute('ROLLBACK')
        self.assertFalse(result)
        self.assertLess(seconds, 0.6)  # the 200 ms hook budget, not the 3 s maintenance timeout
        self.assertEqual(self.count_events(), 1)

    def test_storage_ceiling_returns_false_without_writing(self):
        self.assertTrue(self.call())
        for ceiling in [{'max_database_bytes': 1}, {'min_free_bytes': 2 ** 62}]:
            with self.subTest(**ceiling):
                self.config.write_text(json.dumps({**self.settings, **ceiling}))
                self.assertFalse(self.call())
        self.assertEqual(self.count_events(), 1)

    def test_rate_limited_requests_never_open_the_country_database(self):
        code = ('$_SERVER=json_decode($argv[2],true); require $argv[1]; $results=[]; '
                'for ($i = 0; $i < 60; $i++) { $results[] = lead_analytics_download("latest","redirect","3.2"); } '
                'echo json_encode($results);')
        server = {'REQUEST_METHOD':'GET', 'REMOTE_ADDR':'81.2.69.160', 'DOCUMENT_ROOT':str(self.web)}
        proc = subprocess.run(['php','-r',code,str(self.web/'download-hook.php'),json.dumps(server)],
                              env=self.env,capture_output=True,text=True,check=True,timeout=60)
        self.assertEqual(json.loads(proc.stdout), [True] * 60)
        # Over the limit, the hook succeeds without the (now missing) country database.
        self.config.write_text(json.dumps({**self.settings, 'country_database': str(self.root/'missing.mmdb')}))
        self.assertTrue(self.call())
        self.assertEqual(self.count_events(), 60)
