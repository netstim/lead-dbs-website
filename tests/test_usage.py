import importlib.util
import json
import hashlib
from pathlib import Path
import random
import types
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location('usage', Path(__file__).resolve().parents[1] / 'tools/usage.py')
usage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(usage)
DB = {'name': 'Synthetic country database', 'date': '2026-01-01'}


def line(day='2026-01-02', hour='12:00:00', address='192.0.2.1', tool='dbs'):
    return f'{day} {hour}, Country: , Region: , City: , ORG: , IP: {address}, {tool}, R2024b\n'


def lookup(address):
    return ('276', 'Germany') if address == '192.0.2.1' else None


def aggregate(lines, cutoff='2026-01-02'):
    return usage.aggregate(lines, lookup, cutoff, DB)


class UsageTests(unittest.TestCase):
    def test_invalid_input_is_not_echoed(self):
        for raw in ['garbage', line(address='999.0.0.1'), line(day='2026-02-30'), line(hour='24:00:00')]:
            self.assertIsNone(usage.parse(raw))

    def test_ip_marker_inside_network_name(self):
        row = line().replace('ORG: ,', 'ORG: VIP: Net,')
        self.assertEqual(usage.parse(row)[1], '192.0.2.1')
        self.assertEqual(aggregate([row])['quality']['malformed'], 0)

    def test_tool_total_cannot_be_lower_than_overall_activity(self):
        data = aggregate([line()])
        data['tools'] = {}
        data['quality']['tool_requests'] = 0
        with self.assertRaisesRegex(ValueError, 'Tool requests cannot be fewer'):
            usage.validate(data)

    def test_ipv6_is_canonical(self):
        self.assertEqual(usage.parse(line(address='2001:0db8::1'))[1], '2001:db8::1')

    def test_backup_overlap_and_different_tools(self):
        rows = [line(), line(), line(tool='group'), line(hour='13:00:00')]
        d = aggregate(rows)
        self.assertEqual(d['total'], 2)
        self.assertEqual(d['quality']['collapsed'], 2)
        self.assertEqual(d['tools'], {'Lead-DBS': 2, 'Lead Group': 1})

    def test_order_independence(self):
        rows = [line(tool='group'), line(), line(address='2001:db8::1'), line(tool='unknown'), line(hour='14:30:00')]
        expected = aggregate(rows)
        for seed in range(10):
            random.Random(seed).shuffle(rows)
            self.assertEqual(aggregate(rows), expected)

    def test_hour_and_day_boundaries(self):
        d = aggregate([line(day='2026-01-01', hour='23:59:59'), line(hour='00:00:00'), line(hour='00:59:59'), line(hour='01:00:00')])
        self.assertEqual(d['total'], 3)

    def test_cutoff_and_quality_reconcile(self):
        d = aggregate([line(), line(), 'bad record', line(day='2026-01-03')])
        self.assertEqual(d['quality']['rows'], 4)
        self.assertEqual(d['quality']['parsed'], 3)
        self.assertEqual(d['quality']['malformed'], 1)
        self.assertEqual(d['quality']['after_cutoff'], 1)
        self.assertEqual(d['quality']['included'], 1)
        self.assertEqual(d['observed_to'], '2026-01-03')

    def test_empty_and_future_cutoff_rejected(self):
        for rows, cutoff in [([], '2026-01-02'), ([line()], '2027-01-01'), ([line()], '2025-01-01')]:
            with self.assertRaises(ValueError):
                aggregate(rows, cutoff)

    def test_unknown_country_and_tool_are_visible(self):
        d = aggregate([line(address='2001:db8::1', tool='unrecognized')])
        self.assertEqual(d['countries'], [])
        self.assertEqual(d['quality']['unknown_country'], 1)
        self.assertEqual(d['tools'], {'Other / unknown': 1})

    def test_missing_month_is_unknown(self):
        d = aggregate([line(day='2026-01-02'), line(day='2026-03-05')], '2026-03-05')
        self.assertEqual(d['months'], [['2026-01', 1], ['2026-02', None], ['2026-03', 1]])
        self.assertEqual(d['partial_months'], ['2026-01', '2026-03'])
        self.assertEqual(d['partial_years'], ['2026'])

    def test_full_boundary_month_and_leap_year(self):
        d = aggregate([line(day='2024-02-01'), line(day='2024-02-29')], '2024-02-29')
        self.assertEqual(d['partial_months'], [])

    def test_empty_reporting_year_has_no_tools(self):
        d = aggregate([line(day='2025-12-31'), line(day='2026-02-01')], '2026-01-02')
        self.assertEqual(d['tools'], {})
        self.assertEqual(sum(d['hours']), 0)
        self.assertEqual(d['months'][-1], ['2026-01', None])

    def test_public_contract_blocks_extra_fields_and_ips(self):
        for mutate in [lambda d: d.update(launches=[[120, '276']]),
                       lambda d: d['countries'][0].__setitem__(1, '192.0.2.1'),
                       lambda d: d['country_database'].update(path='/private/logs'),
                       lambda d: d['tools'].update({'2001:db8::1': 1})]:
            d = aggregate([line()])
            mutate(d)
            with self.assertRaises(ValueError):
                usage.validate(d)

    def test_total_tampering_rejected(self):
        d = aggregate([line()])
        d['total'] += 1
        with self.assertRaises(ValueError):
            usage.validate(d)

    def test_atomic_write_preserves_existing_file_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'usage.json'
            path.write_text('original')
            with patch.object(usage.os, 'replace', side_effect=OSError('test')):
                with self.assertRaises(OSError):
                    usage.write_atomic(path, aggregate([line()]))
            self.assertEqual(path.read_text(), 'original')
            self.assertEqual(len(list(Path(tmp).iterdir())), 1)

    def test_output_bytes_are_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'usage.json'
            rows = [line(), line(tool='group')]
            usage.write_atomic(path, aggregate(rows))
            first = path.read_bytes()
            usage.write_atomic(path, aggregate(reversed(rows)))
            self.assertEqual(first, path.read_bytes())
            self.assertNotIn(b'192.0.2.1', first)

    def test_cli_writes_public_data_and_private_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / 'access.log').write_text(line())
            db = directory / 'test.mmdb'
            db.write_bytes(b'synthetic')
            output, manifest = directory / 'public.json', directory / 'private.json'
            reader = unittest.mock.MagicMock()
            reader.__enter__.return_value = reader
            reader.metadata.return_value = types.SimpleNamespace(database_type='Synthetic', build_epoch=1767225600)
            reader.get.return_value = {'country': {'iso_code': 'DE'}}
            country = types.SimpleNamespace(numeric='276', name='Germany')
            modules = {'maxminddb': types.SimpleNamespace(open_database=lambda _: reader),
                       'pycountry': types.SimpleNamespace(countries=types.SimpleNamespace(get=lambda **_: country))}
            argv = ['usage.py', str(directory), str(db), '--cutoff', '2026-01-02', '--output', str(output), '--manifest', str(manifest)]
            with patch.dict(sys.modules, modules), patch.object(sys, 'argv', argv), patch('importlib.metadata.version', return_value='test'), patch('sys.stdout'):
                usage.main()
                first = output.read_bytes()
                usage.main()
                self.assertEqual(first, output.read_bytes())
                self.assertEqual(json.loads(manifest.read_text())['public_sha256'], hashlib.sha256(first).hexdigest())
                # A failed publication leaves the old artifact intact, and the
                # new manifest cannot be mistaken for its provenance.
                (directory / 'access.log').write_text(line() + line(hour='13:00:00'))
                replace = usage.os.replace
                def fail_public(source, target):
                    if Path(target) == output:
                        raise OSError('synthetic publication failure')
                    return replace(source, target)
                with patch.object(usage.os, 'replace', side_effect=fail_public):
                    with self.assertRaises(OSError):
                        usage.main()
                self.assertEqual(first, output.read_bytes())
                self.assertNotEqual(json.loads(manifest.read_text())['public_sha256'], hashlib.sha256(first).hexdigest())
            data = json.loads(first)
            usage.validate(data)
            self.assertEqual(data['total'], 1)
            self.assertIn('sources_sha256', json.loads(manifest.read_text()))
            self.assertNotIn('sources_sha256', data)

    def test_cli_requires_cutoff_before_loading_dependencies(self):
        with patch.object(sys, 'argv', ['usage.py', '/unused', '/unused.mmdb']), patch('sys.stderr'):
            with self.assertRaises(SystemExit) as error:
                usage.main()
            self.assertEqual(error.exception.code, 2)

    def test_checked_in_data_contract(self):
        usage.validate(json.loads((Path(__file__).resolve().parents[1] / 'data/usage.json').read_text()))


if __name__ == '__main__':
    unittest.main()
