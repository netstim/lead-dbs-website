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

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT/'collector' if (ROOT/'collector').is_dir() else ROOT/'server/analytics'

@unittest.skipUnless(shutil.which('php') and (COLLECTOR/'vendor/autoload.php').exists(), 'PHP CLI and composer install required')
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
        config = self.root/'config.json'
        config.write_text(json.dumps({'database':str(self.db),'key_file':str(self.root/'key'),
            'country_database':str(ROOT/'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb')}))
        self.env = {**os.environ, 'LEAD_ANALYTICS_CONFIG':str(config)}

    def call(self, artifact='latest', version='3.2', method='GET', **headers):
        server = {'REQUEST_METHOD':method, 'REMOTE_ADDR':'81.2.69.160', 'DOCUMENT_ROOT':str(self.web), **headers}
        code = '$_SERVER=json_decode($argv[2],true); require $argv[1]; echo json_encode(lead_analytics_download($argv[3],"redirect",$argv[4]));'
        proc = subprocess.run(['php','-r',code,str(self.web/'download-hook.php'),json.dumps(server),artifact,version],
                              env=self.env,capture_output=True,text=True,check=True)
        return json.loads(proc.stdout)

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
