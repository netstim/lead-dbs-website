import copy
from contextlib import closing
import datetime as dt
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
from tools import analytics_ops as ops

BATCH={'schema':1,'timezone':'UTC','cutoff':'2026-01-02','series':{
'access':[{'day':'2026-01-02','country':'DE','n':2}],
'tools':[{'day':'2026-01-02','item':'dbs','n':2}],
'download_requests':[{'day':'2026-01-02','item':'latest','country':'DE','n':1}],
'outcomes':[{'day':'2026-01-02','kind':'access','outcome':'request','traffic':'unclassified','n':3}]}}

class OperationsTests(unittest.TestCase):
    def test_idempotent_archive_and_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=Path(tmp)/'archive.sqlite'
            first=ops.ingest(archive,BATCH)
            self.assertEqual(first,ops.ingest(archive,BATCH))
            self.assertEqual(first['access']['total'],2)
            backup=Path(tmp)/'backup.sqlite'
            with closing(sqlite3.connect(archive)) as db,closing(sqlite3.connect(backup)) as dst:db.backup(dst)
            self.assertEqual(first,ops.ingest(backup,BATCH))
    def test_private_fields_and_future_dates_rejected(self):
        for field,value in [('ip','192.0.2.1'),('subject','token'),('day','2026-01-03')]:
            batch=copy.deepcopy(BATCH);batch['series']['access'][0][field]=value
            with self.assertRaises(ValueError):ops.validate_batch(batch)
    def test_run_exports_before_retention_and_records_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'private_dir':tmp,'output':str(Path(tmp)/'public.json')}
            calls=[]
            def command(c,*args):
                calls.append(args[0])
                return {'export':BATCH,'retain':{'events':0},'health':{'last_event_day':'2026-01-02'}}[args[0]]
            now=dt.datetime(2026,1,3,tzinfo=dt.timezone.utc)
            with patch.object(ops,'php_command',side_effect=command):ops.run(config,now)
            self.assertEqual(calls,['export','retain','health'])
            self.assertTrue(ops.check(config,now))
            self.assertFalse(ops.check(config,now+dt.timedelta(hours=31)))
            before=Path(config['output']).read_bytes()
            with patch.object(ops,'php_command',side_effect=RuntimeError('fixture')):
                with self.assertRaises(RuntimeError):ops.run(config,now)
            self.assertEqual(before,Path(config['output']).read_bytes())
            self.assertFalse(ops.check(config,now))

    def test_failed_export_still_deletes_expired_rows(self):
        with tempfile.TemporaryDirectory() as tmp:
            config={'private_dir':tmp,'output':str(Path(tmp)/'report.json')}
            calls=[]
            def command(c,*args):
                calls.append(args[0])
                if args[0]=='export':raise RuntimeError('export failed')
                return {'events':2}
            with patch.object(ops,'php_command',side_effect=command):
                with self.assertRaises(RuntimeError):ops.run(config)
            self.assertEqual(calls,['export','retain'])
            self.assertFalse(ops.check(config))

    def test_output_must_stay_private(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                ops.run({'private_dir':str(Path(tmp)/'private'),'output':str(Path(tmp)/'public.json')})
            self.assertFalse((Path(tmp)/'public.json').exists())

    def test_failed_backup_keeps_previous_and_removes_temporary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);archive=root/'archive.sqlite';backup=root/'backup.sqlite'
            ops.ingest(archive,BATCH);ops.backup_atomic(archive,backup)
            previous=backup.read_bytes()
            with patch.object(ops.os,'replace',side_effect=OSError('failure')):
                with self.assertRaises(OSError):ops.backup_atomic(archive,backup)
            self.assertEqual(backup.read_bytes(),previous)
            self.assertEqual(list(root.glob('.backup-*')),[])
