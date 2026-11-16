"""Loopback-only endpoint and maintenance CLI integration with the locked MaxMind reader and upstream test
database; never calls STRATO."""
from contextlib import closing, contextmanager
import http.client
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

from prerequisites import needs
from tools import analytics_ops as ops

ROOT = Path(__file__).resolve().parents[1]
COLLECTOR = ROOT / 'collector' if (ROOT / 'collector').is_dir() else ROOT / 'server/analytics'
GEOIP_FIXTURE = ROOT / 'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb'
HAS_PHP = shutil.which('php') is not None
HAS_VENDOR = (COLLECTOR / 'vendor/autoload.php').exists()


def access_event(event_id='12345678-1234-4234-8234-123456789012'):
    return {'schema': 1, 'event_id': event_id, 'kind': 'access', 'item': 'dbs', 'outcome': 'request', 'consent': True}


def count_events(database):
    with closing(sqlite3.connect(database)) as db:
        return db.execute('SELECT COUNT(*) FROM events').fetchone()[0]


@contextmanager
def write_lock(database):
    """Another connection holding the SQLite write lock (RESERVED) until the block ends."""
    with closing(sqlite3.connect(database, isolation_level=None)) as db:
        db.execute('BEGIN IMMEDIATE')
        try:
            yield
        finally:
            db.execute('ROLLBACK')


@needs(HAS_PHP and HAS_VENDOR, 'PHP CLI and composer install required for collector integration')
class CollectorHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='lead-collector-http-')
        cls.root = Path(cls.tmp.name)
        cls.web = cls.root / 'web'
        shutil.copytree(COLLECTOR, cls.web)
        cls.db = cls.root / 'events.sqlite'
        (cls.root / 'key').write_bytes(os.urandom(32))
        shutil.copyfile(GEOIP_FIXTURE, cls.root / 'country.mmdb')
        cls.settings = {'database': str(cls.db), 'key_file': str(cls.root / 'key'),
                        'country_database': str(cls.root / 'country.mmdb')}
        cls.config = cls.root / 'config.json'
        cls.config.write_text(json.dumps(cls.settings))
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.log = (cls.root / 'php.log').open('w+')
        cls.proc = subprocess.Popen(['php', '-S', f'127.0.0.1:{cls.port}', '-t', str(cls.web)],
                                    env={**os.environ, 'LEAD_ANALYTICS_CONFIG': str(cls.config)},
                                    stdout=cls.log, stderr=cls.log)
        for _ in range(50):
            try:
                with socket.create_connection(('127.0.0.1', cls.port), timeout=.1):
                    break
            except OSError:
                time.sleep(.02)
        else:
            raise RuntimeError('Local PHP fixture did not start')

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.log.close()
        cls.tmp.cleanup()

    @contextmanager
    def settings_changed(self, **changes):
        self.config.write_text(json.dumps({**self.settings, **changes}))
        try:
            yield
        finally:
            self.config.write_text(json.dumps(self.settings))

    def request(self, body=None, method='POST', headers=None):
        con = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        con.request(method, '/collect.php', body=body, headers=headers or {'Content-Type': 'application/json'})
        response = con.getresponse()
        data = response.read()
        con.close()
        self.last_headers = response.headers
        return response.status, data

    def test_accepted_and_idempotent_no_raw_address(self):
        body = json.dumps(access_event())
        self.assertEqual(self.request(body)[0], 204)
        self.assertEqual(self.request(body)[0], 204)
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM events WHERE event_id=?',
                                        (access_event()['event_id'],)).fetchone()[0], 1)
        self.assertNotIn(b'127.0.0.1', self.db.read_bytes())

    def test_consent_and_payload_bounds(self):
        body = access_event()
        body['consent'] = False
        self.assertEqual(self.request(json.dumps(body))[0], 400)
        body = access_event()
        body['patient'] = 'sensitive'
        self.assertEqual(self.request(json.dumps(body))[0], 400)
        self.assertEqual(self.request('x' * 4097)[0], 413)
        self.assertEqual(self.request('{}', headers={'Content-Type': 'text/plain'})[0], 415)
        self.assertEqual(self.request(method='GET')[0], 405)

    def test_privacy_signals_and_server_only_outcomes(self):
        for header in ['DNT', 'Sec-GPC']:
            self.assertEqual(self.request('{}', headers={'Content-Type': 'application/json', header: '1'})[0], 204)
        body = access_event()
        body['kind'] = 'download'
        body['item'] = 'latest'
        body['outcome'] = 'redirect'
        self.assertEqual(self.request(json.dumps(body))[0], 400)

    def test_private_storage_must_be_outside_document_root(self):
        with self.settings_changed(database=str(self.web / 'exposed.sqlite')):
            self.assertEqual(self.request(json.dumps(access_event()))[0], 503)
        self.assertFalse((self.web / 'exposed.sqlite').exists())

    def test_storage_ceiling_sheds_with_503(self):
        self.assertEqual(self.request(json.dumps(access_event('12345678-1234-4234-8234-000000000301')))[0], 204)
        before = count_events(self.db)
        body = json.dumps(access_event('12345678-1234-4234-8234-000000000302'))
        missing_country_database = str(self.root / 'missing.mmdb')
        for ceiling in [{'max_database_bytes': 1}, {'min_free_bytes': 2 ** 62},
                        {'max_database_bytes': 1, 'country_database': missing_country_database}]:
            # The last case shows that shed requests never open the country database.
            with self.subTest(**ceiling), self.settings_changed(**ceiling):
                self.assertEqual(self.request(body)[0], 503)
                self.assertEqual(self.last_headers['Retry-After'], '3600')
        self.assertEqual(count_events(self.db), before)
        self.assertEqual(self.request(body)[0], 204)

    def test_invalid_limits_and_unknown_settings_are_refused(self):
        body = json.dumps(access_event('12345678-1234-4234-8234-000000000303'))
        for change in [{'max_database_bytes': 0}, {'hook_busy_timeout_ms': '200'}, {'min_free_bytes': 1.5},
                       {'max_database_byte': 10}]:
            with self.subTest(**change), self.settings_changed(**change):
                self.assertEqual(self.request(body)[0], 503)
                self.assertIsNone(self.last_headers['Retry-After'])

    def test_concurrent_writers(self):
        """Several PHP processes record distinct events at the same moment through the real bootstrap."""
        database = self.root / 'concurrent.sqlite'
        config = self.root / 'concurrent.json'
        config.write_text(json.dumps({**self.settings, 'database': str(database)}))
        script = r'''
            require $argv[1];
            $worker = (int) $argv[3];
            time_sleep_until((float) $argv[2]);
            $collector = lead_analytics_collector('collect');
            $results = [];
            for ($i = 0; $i < 25; $i++) {
                $event = ['schema' => 1, 'event_id' => sprintf('12345678-1234-4234-8%03x-%012x', $worker, $i),
                          'kind' => 'access', 'item' => 'dbs', 'outcome' => 'request', 'consent' => true];
                $results[] = $collector->record($event, '198.51.100.' . $worker, 'MATLAB');
            }
            echo json_encode(array_count_values($results));
        '''
        start = time.time() + 1
        env = {**os.environ, 'LEAD_ANALYTICS_CONFIG': str(config)}
        workers = [subprocess.Popen(['php', '-r', script, str(self.web / 'bootstrap.php'), str(start), str(worker)],
                                    env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                   for worker in range(1, 9)]
        for worker in workers:
            out, err = worker.communicate(timeout=60)
            self.assertEqual((worker.returncode, err), (0, ''))
            self.assertEqual(json.loads(out), {'accepted': 25})
        with closing(sqlite3.connect(database)) as db:
            self.assertEqual(db.execute('SELECT COUNT(DISTINCT event_id) FROM events').fetchone()[0], 200)
            self.assertEqual(db.execute('SELECT COUNT(DISTINCT subject) FROM events').fetchone()[0], 8)
            counters = dict(db.execute('SELECT name, SUM(n) FROM metrics GROUP BY name').fetchall())
            self.assertEqual(db.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        self.assertEqual(counters, {'received': 200, 'accepted': 200})

    def test_z_maintenance_end_to_end(self):
        # Actual PHP CLI -> private archive -> minimized report -> retention.
        script = ("require $argv[1]; $c=lead_analytics_collector(); $e=json_decode($argv[2],true); "
                  "$c->record($e,'192.0.2.50','MATLAB',new DateTimeImmutable('yesterday')); "
                  "$e['event_id']='12345678-1234-4234-8234-123456789099'; "
                  "$c->record($e,'192.0.2.50','MATLAB',new DateTimeImmutable('-40 days'));")
        body = access_event('12345678-1234-4234-8234-123456789098')
        subprocess.run(['php', '-r', script, str(self.web / 'bootstrap.php'), json.dumps(body)],
                       env={**os.environ, 'LEAD_ANALYTICS_CONFIG': str(self.config)}, check=True, capture_output=True)
        config = self.operations_config()
        status = ops.run(config)
        self.assertTrue(status['ok'])
        first = Path(config['output']).read_bytes()
        self.assertEqual(json.loads(first)['access']['total'], 2)
        self.assertNotIn(b'subject', first)
        self.assertGreater(status['retention']['events'], 0)
        ops.run(config)
        self.assertEqual(first, Path(config['output']).read_bytes())
        # The live health check sees the retention the run just completed.
        self.assertNotIn('Retention has not completed in the last 2 hours', ops.problems(config))

    def test_zz_failed_export_still_runs_real_retention(self):
        body = access_event('12345678-1234-4234-8234-123456789097')
        script = ("require $argv[1]; lead_analytics_collector()->record(json_decode($argv[2],true),"
                  "'192.0.2.51','MATLAB',new DateTimeImmutable('-40 days'));")
        subprocess.run(['php', '-r', script, str(self.web / 'bootstrap.php'), json.dumps(body)],
                       env={**os.environ, 'LEAD_ANALYTICS_CONFIG': str(self.config)}, check=True, capture_output=True)
        original = ops.php_command

        def fail_export(config, *args):
            if args[0] == 'export':
                raise RuntimeError('export failed')
            return original(config, *args)

        with patch.object(ops, 'php_command', side_effect=fail_export):
            with self.assertRaises(RuntimeError):
                ops.run(self.operations_config())
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM events WHERE event_id=?',
                                        (body['event_id'],)).fetchone()[0], 0)

    def operations_config(self):
        private = self.root / 'operations'
        return {'php': shutil.which('php'), 'collector_dir': str(self.web), 'collector_config': str(self.config),
                'private_dir': str(private), 'output': str(private / 'reports' / 'public.json')}


SEED_EXPIRED_EVENT = r'''
    require $argv[1];
    $collector = new LeadAnalytics\Collector(new LeadAnalytics\Storage($argv[2]), str_repeat('k', 32), fn($ip) => 'DE');
    $event = ['schema' => 1, 'event_id' => '12345678-1234-4234-8234-000000000001', 'kind' => 'access',
              'item' => 'dbs', 'outcome' => 'request', 'consent' => true];
    echo $collector->record($event, '192.0.2.60', 'MATLAB', new DateTimeImmutable('-40 days'));
'''


@needs(HAS_PHP, 'PHP CLI required for the maintenance command')
class RetentionCLITests(unittest.TestCase):
    """`php maintenance.php retain` needs only the private database (BE-01)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix='lead-retention-')
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.web = self.root / 'web'
        shutil.copytree(COLLECTOR, self.web)
        private = self.root / 'private'
        private.mkdir(mode=0o700)
        self.db = private / 'events.sqlite'
        self.key = private / 'hmac.key'
        self.key.write_bytes(os.urandom(32))
        self.country = private / 'country.mmdb'
        shutil.copyfile(GEOIP_FIXTURE, self.country)
        self.config = private / 'config.json'
        self.config.write_text(json.dumps({'database': str(self.db), 'key_file': str(self.key),
                                           'country_database': str(self.country)}))
        seeded = subprocess.run(['php', '-r', SEED_EXPIRED_EVENT, str(self.web / 'Collector.php'), str(self.db)],
                                capture_output=True, text=True, check=True)
        self.assertEqual(seeded.stdout, 'accepted')

    def maintenance(self, *args, cwd=None):
        return subprocess.run(['php', str(self.web / 'maintenance.php'), *args],
                              env={**os.environ, 'LEAD_ANALYTICS_CONFIG': str(self.config)},
                              cwd=cwd or self.web, capture_output=True, text=True, timeout=60)

    def last_retention(self):
        with closing(sqlite3.connect(self.db)) as db:
            row = db.execute("SELECT value FROM state WHERE name='last_retention_at'").fetchone()
        return row and row[0]

    def assert_retention_succeeds(self, cwd=None):
        result = self.maintenance('retain', cwd=cwd)
        self.assertEqual((result.returncode, result.stderr), (0, ''))
        retained = json.loads(result.stdout)
        self.assertEqual(retained['events'], 1)
        self.assertEqual(count_events(self.db), 0)
        self.assertEqual(self.last_retention(), retained['completed_at'])
        health = self.maintenance('health', cwd=cwd)
        self.assertEqual(health.returncode, 0)
        self.assertEqual(json.loads(health.stdout)['last_retention_at'], retained['completed_at'])

    def assert_retention_fails(self):
        result = self.maintenance('retain')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertEqual(count_events(self.db), 1)
        self.assertIsNone(self.last_retention())

    def test_without_country_database(self):
        self.country.unlink()
        self.assert_retention_succeeds()

    def test_with_corrupt_country_database(self):
        self.country.write_bytes(b'not a MaxMind database')
        self.assert_retention_succeeds()

    def test_without_key_file(self):
        self.key.unlink()
        self.assert_retention_succeeds()

    def test_without_vendor_folder(self):
        shutil.rmtree(self.web / 'vendor', ignore_errors=True)
        self.assert_retention_succeeds()
        health = json.loads(self.maintenance('health').stdout)
        self.assertEqual(health['storage']['database_bytes'], self.db.stat().st_size)
        self.assertEqual(self.maintenance('export', '2026-01-02').returncode, 0)

    def test_from_a_working_directory_that_contains_the_private_files(self):
        # The CLI has no document root; the working directory must not be mistaken for one.
        self.assert_retention_succeeds(cwd=self.root)

    def test_fails_while_another_writer_holds_the_lock(self):
        started = time.monotonic()
        with write_lock(self.db):
            self.assert_retention_fails()
        # It waited for the lock (the 3 s busy timeout) before giving up.
        self.assertGreaterEqual(time.monotonic() - started, 2.5)
        self.assert_retention_succeeds()

    def test_fails_on_a_read_only_database(self):
        if os.geteuid() == 0:
            self.skipTest('root ignores file permissions')
        self.db.chmod(0o400)
        try:
            self.assert_retention_fails()
        finally:
            self.db.chmod(0o600)
        self.assert_retention_succeeds()


if __name__ == '__main__':
    unittest.main()
