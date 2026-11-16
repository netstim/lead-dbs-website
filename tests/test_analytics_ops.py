import copy
from contextlib import closing
import datetime as dt
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import unittest
from unittest.mock import Mock, patch

from tools import analytics_ops as ops

BATCH = {'schema': 1, 'timezone': 'UTC', 'cutoff': '2026-01-02', 'series': {
    'access': [{'day': '2026-01-02', 'country': 'DE', 'n': 2}],
    'tools': [{'day': '2026-01-02', 'item': 'dbs', 'n': 2}],
    'download_requests': [{'day': '2026-01-02', 'item': 'latest', 'country': 'DE', 'n': 1}],
    'outcomes': [{'day': '2026-01-02', 'kind': 'access', 'outcome': 'request', 'traffic': 'unclassified', 'n': 3}]}}

NOW = dt.datetime(2026, 1, 3, 4, 0, tzinfo=dt.timezone.utc)
MIB = 1024 * 1024


def health(now=NOW, **overrides):
    """A healthy `maintenance.php health` result as of `now`."""
    result = {
        'schema': 1,
        'last_event_day': '2026-01-02',
        'events_retained': 3,
        'last_retention_at': (now - dt.timedelta(minutes=30)).isoformat(),
        'storage': {'database_bytes': 10 * MIB, 'free_bytes': 4096 * MIB,
                    'max_database_bytes': 256 * MIB, 'min_free_bytes': 512 * MIB},
        'counters': [],
    }
    result.update(overrides)
    return result


def fake_collector(calls=None, now=NOW, **health_overrides):
    """A php_command replacement that records the maintenance commands it receives."""
    def command(config, *args):
        if calls is not None:
            calls.append(args[0])
        if args[0] == 'export':
            return copy.deepcopy(BATCH)
        if args[0] == 'retain':
            return {'events': 0, 'buckets': 0, 'metrics': 0, 'completed_at': now.isoformat()}
        return health(now, **health_overrides)
    return command


def make_config(root):
    """Operations config whose collector config names its private files inside reports/,
    so only the reserved-path comparison can keep a report off them."""
    private = root / 'private'
    reports = private / 'reports'
    collector_config = reports / 'collector.json'
    reports.mkdir(parents=True)
    collector_config.write_text(json.dumps({
        'database': str(reports / 'events.sqlite'),
        'key_file': str(reports / 'hmac.key'),
        'country_database': str(reports / 'country.mmdb'),
    }))
    return {
        'php': '/nonexistent/php',
        'collector_dir': str(root / 'collector'),
        'collector_config': str(collector_config),
        'private_dir': str(private),
        'output': str(reports / 'usage.json'),
    }


class OperationsTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.config = make_config(self.root)
        self.private = Path(self.config['private_dir'])

    def test_idempotent_archive_and_restore(self):
        archive = self.root / 'archive.sqlite'
        first = ops.ingest(archive, BATCH)
        self.assertEqual(first, ops.ingest(archive, BATCH))
        self.assertEqual(first['access']['total'], 2)
        backup = self.root / 'backup.sqlite'
        with closing(sqlite3.connect(archive)) as db, closing(sqlite3.connect(backup)) as destination:
            db.backup(destination)
        self.assertEqual(first, ops.ingest(backup, BATCH))

    def test_private_fields_and_future_dates_rejected(self):
        for field, value in [('ip', '192.0.2.1'), ('subject', 'token'), ('day', '2026-01-03')]:
            batch = copy.deepcopy(BATCH)
            batch['series']['access'][0][field] = value
            with self.assertRaises(ValueError):
                ops.validate_batch(batch)

    def test_run_exports_before_retention_and_records_failure(self):
        calls = []
        with patch.object(ops, 'php_command', side_effect=fake_collector(calls)):
            ops.run(self.config, NOW)
            self.assertEqual(calls, ['export', 'retain', 'health'])
            self.assertTrue(ops.check(self.config, NOW))
            self.assertFalse(ops.check(self.config, NOW + dt.timedelta(hours=31)))
        before = Path(self.config['output']).read_bytes()
        with patch.object(ops, 'php_command', side_effect=RuntimeError('fixture')):
            with self.assertRaises(RuntimeError):
                ops.run(self.config, NOW)
        self.assertEqual(before, Path(self.config['output']).read_bytes())
        with patch.object(ops, 'php_command', side_effect=fake_collector()):
            self.assertFalse(ops.check(self.config, NOW))

    def test_failed_export_still_deletes_expired_rows(self):
        calls = []

        def command(config, *args):
            calls.append(args[0])
            if args[0] == 'export':
                raise RuntimeError('export failed')
            return {'events': 2}

        with patch.object(ops, 'php_command', side_effect=command):
            with self.assertRaises(RuntimeError):
                ops.run(self.config)
        self.assertEqual(calls, ['export', 'retain'])
        with patch.object(ops, 'php_command', side_effect=fake_collector()):
            self.assertFalse(ops.check(self.config))

    def test_output_must_stay_private(self):
        config = dict(self.config, private_dir=str(self.root / 'elsewhere'), output=str(self.root / 'public.json'))
        with patch.object(ops, 'php_command') as command:
            with self.assertRaises(ValueError):
                ops.run(config)
        command.assert_not_called()
        self.assertFalse((self.root / 'public.json').exists())
        self.assertFalse((self.root / 'elsewhere').exists())

    def test_failed_backup_keeps_previous_and_removes_temporary(self):
        archive = self.root / 'archive.sqlite'
        backup = self.root / 'backup.sqlite'
        ops.ingest(archive, BATCH)
        ops.backup_atomic(archive, backup)
        previous = backup.read_bytes()
        with patch.object(ops.os, 'replace', side_effect=OSError('failure')):
            with self.assertRaises(OSError):
                ops.backup_atomic(archive, backup)
        self.assertEqual(backup.read_bytes(), previous)
        self.assertEqual(list(self.root.glob('.backup-*')), [])


class CheckTests(unittest.TestCase):
    """check combines the daily status file with live collector health."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.config = make_config(Path(tmp.name))
        with patch.object(ops, 'php_command', side_effect=fake_collector()):
            ops.run(self.config, NOW)

    def problems(self, now=NOW, **health_overrides):
        with patch.object(ops, 'php_command', side_effect=fake_collector(now=now, **health_overrides)) as command:
            found = ops.problems(self.config, now)
        command.assert_called_with(self.config, 'health')
        return found

    def test_healthy(self):
        self.assertEqual(self.problems(), [])

    def test_retention_must_be_recent(self):
        two_hours_ago = (NOW - dt.timedelta(hours=2)).isoformat()
        self.assertEqual(self.problems(last_retention_at=two_hours_ago), [])
        for stale in [(NOW - dt.timedelta(hours=2, minutes=1)).isoformat(), None, 'not a time',
                      '2026-01-03T03:30:00', (NOW + dt.timedelta(hours=1)).isoformat()]:
            with self.subTest(last_retention_at=stale):
                self.assertEqual(self.problems(last_retention_at=stale),
                                 ['Retention has not completed in the last 2 hours'])

    def test_retention_staleness_fails_even_after_a_successful_daily_run(self):
        later = NOW + dt.timedelta(hours=5)
        stale = (NOW - dt.timedelta(minutes=30)).isoformat()
        with patch.object(ops, 'php_command', side_effect=fake_collector(now=later, last_retention_at=stale)):
            self.assertFalse(ops.check(self.config, later))

    def test_database_size_against_ceiling(self):
        ceiling = 1000 * MIB
        below = {'database_bytes': 900 * MIB - 1, 'free_bytes': 4096 * MIB,
                 'max_database_bytes': ceiling, 'min_free_bytes': 512 * MIB}
        self.assertEqual(self.problems(storage=below), [])
        for size in [900 * MIB, ceiling, ceiling * 2]:
            with self.subTest(size=size):
                self.assertEqual(self.problems(storage=dict(below, database_bytes=size)),
                                 ['Collector database is at or above 90% of max_database_bytes'])

    def test_free_space_floor(self):
        storage = health()['storage']
        self.assertEqual(self.problems(storage=dict(storage, free_bytes=512 * MIB)), [])
        self.assertEqual(self.problems(storage=dict(storage, free_bytes=512 * MIB - 1)),
                         ['Free space is below min_free_bytes; collection is shedding'])
        self.assertEqual(self.problems(storage=dict(storage, free_bytes=None)),
                         ['Free space is unavailable; collection is shedding'])

    def test_unavailable_health_fails(self):
        with patch.object(ops, 'php_command', side_effect=RuntimeError('Collector maintenance failed')):
            self.assertEqual(ops.problems(self.config, NOW), ['Collector health is unavailable'])

    def test_missing_status_fails_and_still_checks_health(self):
        (Path(self.config['private_dir']) / 'status.json').unlink()
        self.assertEqual(self.problems(), ['No readable maintenance status'])


class ReportPathTests(unittest.TestCase):
    """The report may only be written to its own file in private_dir/reports (BE-03)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.config = make_config(self.root)
        self.private = Path(self.config['private_dir'])
        self.reports = self.private / 'reports'
        self.operations_config = self.reports / 'operations.json'
        self.operations_config.write_text(json.dumps(self.config))

    def assert_rejected(self, output, target=None):
        """run() refuses `output` before any collector call and leaves `target` byte-for-byte unchanged."""
        target = Path(target or output)
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'original contents')
        before = target.read_bytes()
        state_before = sorted(path.name for path in self.private.iterdir())
        config = dict(self.config, output=str(output))
        with patch.object(ops, 'php_command') as command:
            with self.assertRaises(ValueError):
                ops.run(config, NOW, operations_config=self.operations_config)
        command.assert_not_called()
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in self.private.iterdir()), state_before)

    def test_status_file(self):
        self.assert_rejected(self.private / 'status.json')

    def test_lock_file(self):
        self.assert_rejected(self.private / 'run.lock')

    def test_aggregate_archive(self):
        self.assert_rejected(self.private / 'aggregate-archive.sqlite')

    def test_aggregate_archive_sidecars(self):
        for suffix in ['-journal', '-wal', '-shm']:
            with self.subTest(suffix=suffix):
                self.assert_rejected(self.private / ('aggregate-archive.sqlite' + suffix))

    def test_backups(self):
        self.assert_rejected(self.private / 'backups' / '20260102T040000.sqlite')

    def test_backups_reached_through_reports(self):
        (self.private / 'backups').symlink_to(self.reports, target_is_directory=True)
        self.assert_rejected(self.reports / '20260102T040000.sqlite')

    def test_operations_config(self):
        self.assert_rejected(self.operations_config)

    def test_collector_config(self):
        self.assert_rejected(self.config['collector_config'])

    def test_collector_database_and_sidecars(self):
        for name in ['events.sqlite', 'events.sqlite-journal', 'events.sqlite-wal', 'events.sqlite-shm']:
            with self.subTest(name=name):
                self.assert_rejected(self.reports / name)

    def test_collector_key(self):
        self.assert_rejected(self.reports / 'hmac.key')

    def test_country_database(self):
        self.assert_rejected(self.reports / 'country.mmdb')

    def test_output_symlink_to_reserved_file(self):
        archive = self.private / 'aggregate-archive.sqlite'
        archive.write_bytes(b'archive')
        alias = self.reports / 'usage.json'
        alias.symlink_to(archive)
        self.assert_rejected(alias, target=archive)

    def test_reports_directory_symlink(self):
        status = self.private / 'status.json'
        status.write_bytes(b'status')
        real_reports = self.private / 'real-reports'
        self.reports.rename(real_reports)
        self.reports.symlink_to(self.private, target_is_directory=True)
        self.config['collector_config'] = str(real_reports / 'collector.json')
        self.assert_rejected(self.reports / 'status.json', target=status)

    def test_reports_directory_symlink_outside_private_dir(self):
        public = self.root / 'public'
        public.mkdir()
        self.reports.rename(self.private / 'real-reports')
        self.config['collector_config'] = str(self.private / 'real-reports' / 'collector.json')
        self.reports.symlink_to(public, target_is_directory=True)
        self.assert_rejected(self.reports / 'usage.json', target=public / 'usage.json')

    def test_report_reached_through_another_symlinked_directory(self):
        alias_dir = self.root / 'alias'
        alias_dir.symlink_to(self.reports, target_is_directory=True)
        self.assert_rejected(alias_dir / 'usage.json', target=self.reports / 'usage.json')

    def test_output_outside_reports(self):
        self.assert_rejected(self.private / 'usage.json')
        self.assert_rejected(self.reports / 'nested' / 'usage.json')

    def test_happy_path_creates_private_reports_directory(self):
        self.reports.joinpath('collector.json').rename(self.root / 'collector.json')
        self.operations_config.unlink()
        self.reports.rmdir()
        self.config['collector_config'] = str(self.root / 'collector.json')
        with patch.object(ops, 'php_command', side_effect=fake_collector()):
            status = ops.run(self.config, NOW, operations_config=self.root / 'operations.json')
        self.assertTrue(status['ok'])
        self.assertEqual(stat.S_IMODE(os.stat(self.reports).st_mode), 0o700)
        self.assertEqual(json.loads(Path(self.config['output']).read_text())['access']['total'], 2)
        with closing(sqlite3.connect(self.private / 'aggregate-archive.sqlite')) as db:
            self.assertEqual(db.execute('PRAGMA quick_check').fetchone()[0], 'ok')
        self.assertTrue(json.loads((self.private / 'status.json').read_text())['ok'])
        self.assertEqual(len(list((self.private / 'backups').glob('*.sqlite'))), 1)


if __name__ == '__main__':
    unittest.main()
