import json
from pathlib import Path
import random
import unittest
from tools import downloads

DB={'name':'Synthetic','date':'2026-01-01'}
def line(day='2026-01-02',ip='192.0.2.1',item='latest'):
    return f'{day} 12:00:00, Country: , ORG: VIP: Test, IP: {ip}, {item}'
def lookup(ip):return ('276','Germany') if ip=='192.0.2.1' else None

class DownloadTests(unittest.TestCase):
    def test_aliases_have_evidence_based_categories(self):
        catalog,aliases=downloads.registry()
        for artifact,category in [('group2017','connectome'),('fliplr','data'),('allengenetics','data'),('macroscalehc','atlas'),('latest','program'),('updates_32-321','program_update'),('standalone_mystery','unknown')]:
            self.assertEqual(downloads.classify(artifact,aliases),category)
    def test_globe_contract_and_all_categories(self):
        d=downloads.aggregate([line(),line(),line(item='data'),line(item='group2017')],lookup,'2026-01-02',DB)
        self.assertEqual(d['total'],1)
        self.assertEqual(d['months'],[['2026-01',{'276':1}]])
        self.assertEqual(d['all_requests']['total'],3)
        self.assertEqual(d['all_requests']['quality']['collapsed'],1)
    def test_legacy_exclusions_are_auditable(self):
        d=downloads.aggregate([line(ip='13.0.0.1'),line(ip='2001:db8::1'),line()],lookup,'2026-01-02',DB)
        self.assertEqual(d['selection']['excluded'],{'network_heuristic':1,'high_lifetime_frequency':0,'unknown_country':1})
        self.assertEqual(d['selection']['candidate_requests'],3)
        self.assertEqual(d['total'],1)
    def test_all_countries_no_minimum(self):
        d=downloads.aggregate([line()],lookup,'2026-01-02',DB)
        self.assertEqual(d['countries'],[['276','Germany',1]])
    def test_order_and_repetition(self):
        rows=[line()]*101+[line(item='data'),line(day='2026-01-03')]
        a=downloads.aggregate(rows,lookup,'2026-01-02',DB)
        random.Random(10).shuffle(rows)
        self.assertEqual(a,downloads.aggregate(rows,lookup,'2026-01-02',DB))
        self.assertEqual(a['all_requests']['quality']['high_frequency_groups'],1)
        self.assertEqual(a['all_requests']['quality']['after_cutoff'],1)
    def test_validation_and_gaps(self):
        rows=[line(day='2026-01-02'),line(day='2026-03-02'),line(ip='999.0.0.1'),line(item='bad name')]
        d=downloads.aggregate(rows,lookup,'2026-03-02',DB)
        self.assertEqual(d['all_requests']['quality']['malformed'],2)
        self.assertEqual(d['months'][1],['2026-02',{}])
        self.assertEqual(d['all_requests']['months'][1],['2026-02',None])
        d['total']+=1
        with self.assertRaises(ValueError):downloads.validate(d)
    def test_no_program_or_geography_is_valid_empty_globe(self):
        d=downloads.aggregate([line(item='data')],lookup,'2026-01-02',DB)
        self.assertEqual(d['countries'],[])
        self.assertEqual(d['total'],0)
    def test_public_data(self):
        downloads.validate(json.loads((Path(__file__).resolve().parents[1]/'data/downloads.json').read_text()))

    def test_mapped_ipv6_uses_same_network_filter(self):
        self.assertTrue(downloads.network_flag('::ffff:13.0.0.1'))
        self.assertTrue(downloads.network_flag('::ffff:66.249.0.1'))
        self.assertFalse(downloads.network_flag('::ffff:192.0.2.1'))
    def test_globe_retains_approved_artifact_selection(self):
        d=downloads.aggregate([line(item='leaddbs'),line(item='standalone_mystery'),line()],lookup,'2026-01-02',DB)
        self.assertEqual(d['total'],2)
        self.assertEqual(d['all_requests']['total'],3)
