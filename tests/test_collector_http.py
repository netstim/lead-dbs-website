"""Loopback-only endpoint integration with the locked MaxMind reader and upstream test database; never calls STRATO."""
import http.client
import datetime as dt
from tools import analytics_ops as ops
from contextlib import closing
import json
import os
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT/'collector' if (ROOT/'collector').is_dir() else ROOT/'server/analytics'

@unittest.skipUnless(shutil.which('php') and (COLLECTOR/'vendor/autoload.php').exists(), 'PHP CLI and composer install required for collector integration')
class CollectorHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='lead-collector-http-')
        cls.root=Path(cls.tmp.name)
        cls.web=cls.root/'web'
        shutil.copytree(COLLECTOR,cls.web)
        cls.db=cls.root/'events.sqlite'
        (cls.root/'key').write_bytes(os.urandom(32))
        shutil.copyfile(ROOT/'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb',cls.root/'country.mmdb')
        cls.config=cls.root/'config.json'
        cls.config.write_text(json.dumps({'database':str(cls.db),'key_file':str(cls.root/'key'),'country_database':str(cls.root/'country.mmdb')}))
        with socket.socket() as sock:sock.bind(('127.0.0.1',0));cls.port=sock.getsockname()[1]
        cls.log=(cls.root/'php.log').open('w+')
        cls.proc=subprocess.Popen(['php','-S',f'127.0.0.1:{cls.port}','-t',str(cls.web)],env={**os.environ,'LEAD_ANALYTICS_CONFIG':str(cls.config)},stdout=cls.log,stderr=cls.log)
        for _ in range(50):
            try:
                with socket.create_connection(('127.0.0.1',cls.port),timeout=.1):break
            except OSError:time.sleep(.02)
        else:raise RuntimeError('Local PHP fixture did not start')
    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate();cls.proc.wait(timeout=5);cls.log.close();cls.tmp.cleanup()
    def request(self,body=None,method='POST',headers=None):
        con=http.client.HTTPConnection('127.0.0.1',self.port,timeout=5)
        con.request(method,'/collect.php',body=body,headers=headers or {'Content-Type':'application/json'})
        response=con.getresponse();data=response.read();con.close();return response.status,data
    def event(self):
        return {'schema':1,'event_id':'12345678-1234-4234-8234-123456789012','kind':'access','item':'dbs','outcome':'request','consent':True}
    def test_accepted_and_idempotent_no_raw_address(self):
        body=json.dumps(self.event())
        self.assertEqual(self.request(body)[0],204)
        self.assertEqual(self.request(body)[0],204)
        with closing(sqlite3.connect(self.db)) as db:self.assertEqual(db.execute('SELECT COUNT(*) FROM events').fetchone()[0],1)
        self.assertNotIn(b'127.0.0.1',self.db.read_bytes())
    def test_consent_and_payload_bounds(self):
        body=self.event();body['consent']=False
        self.assertEqual(self.request(json.dumps(body))[0],400)
        body=self.event();body['patient']='sensitive'
        self.assertEqual(self.request(json.dumps(body))[0],400)
        self.assertEqual(self.request('x'*4097)[0],413)
        self.assertEqual(self.request('{}',headers={'Content-Type':'text/plain'})[0],415)
        self.assertEqual(self.request(method='GET')[0],405)
    def test_privacy_signals_and_server_only_outcomes(self):
        for header in ['DNT','Sec-GPC']:
            self.assertEqual(self.request('{}',headers={'Content-Type':'application/json',header:'1'})[0],204)
        body=self.event();body['kind']='download';body['item']='latest';body['outcome']='redirect'
        self.assertEqual(self.request(json.dumps(body))[0],400)
    def test_private_storage_must_be_outside_document_root(self):
        original=self.config.read_text()
        try:
            config=json.loads(original);config['database']=str(self.web/'exposed.sqlite');self.config.write_text(json.dumps(config))
            self.assertEqual(self.request(json.dumps(self.event()))[0],503)
            self.assertFalse((self.web/'exposed.sqlite').exists())
        finally:self.config.write_text(original)
    def test_z_maintenance_end_to_end(self):
        # Actual PHP CLI -> private archive -> minimized report -> retention.
        script = "require $argv[1]; $c=lead_analytics_collector(); $e=json_decode($argv[2],true); $c->record($e,'192.0.2.50','MATLAB',new DateTimeImmutable('yesterday')); $e['event_id']='12345678-1234-4234-8234-123456789099'; $c->record($e,'192.0.2.50','MATLAB',new DateTimeImmutable('-40 days'));"
        body=self.event();body['event_id']='12345678-1234-4234-8234-123456789098'
        subprocess.run(['php','-r',script,str(self.web/'bootstrap.php'),json.dumps(body)],env={**os.environ,'LEAD_ANALYTICS_CONFIG':str(self.config)},check=True,capture_output=True)
        config={'php':shutil.which('php'),'collector_dir':str(self.web),'collector_config':str(self.config),
                'private_dir':str(self.root/'operations'),'output':str(self.root/'operations'/'public.json')}
        status=ops.run(config)
        self.assertTrue(status['ok'])
        first=Path(config['output']).read_bytes()
        self.assertEqual(json.loads(first)['access']['total'],2)
        self.assertNotIn(b'subject',first)
        self.assertGreater(status['retention']['events'],0)
        ops.run(config)
        self.assertEqual(first,Path(config['output']).read_bytes())


    def test_zz_failed_export_still_runs_real_retention(self):
        body=self.event();body['event_id']='12345678-1234-4234-8234-123456789097'
        script="require $argv[1]; lead_analytics_collector()->record(json_decode($argv[2],true),'192.0.2.51','MATLAB',new DateTimeImmutable('-40 days'));"
        subprocess.run(['php','-r',script,str(self.web/'bootstrap.php'),json.dumps(body)],
                       env={**os.environ,'LEAD_ANALYTICS_CONFIG':str(self.config)},check=True,capture_output=True)
        config={'php':shutil.which('php'),'collector_dir':str(self.web),'collector_config':str(self.config),
                'private_dir':str(self.root/'operations'),'output':str(self.root/'operations'/'public.json')}
        original=ops.php_command
        def fail_export(config,*args):
            if args[0]=='export':raise RuntimeError('export failed')
            return original(config,*args)
        with patch.object(ops,'php_command',side_effect=fail_export):
            with self.assertRaises(RuntimeError):ops.run(config)
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute("SELECT COUNT(*) FROM events WHERE event_id=?",(body['event_id'],)).fetchone()[0],0)
