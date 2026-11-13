"""The contact/FOCUS form handler (server/forms/) on a loopback PHP server. Mail goes into a temporary outbox
folder, never to a real address, and nothing talks to STRATO."""
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
from urllib.parse import urlencode

ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / 'server/forms'


def yaml_fields():
    """form id -> field names of data/forms.yaml (top-level keys and their `- {name: ...}` lines)."""
    forms, current = {}, None
    for line in (ROOT / 'data/forms.yaml').read_text().splitlines():
        if m := re.match(r'^([a-z]\w*):\s*$', line):
            current = forms.setdefault(m[1], {'fields': [], 'action': None})
        elif current is not None and (m := re.match(r'^\s+- \{name: (\w+)', line)):
            current['fields'].append(m[1])
        elif current is not None and (m := re.match(r'^\s+action:\s*(\S+)', line)):
            current['action'] = m[1]
    return forms


@unittest.skipUnless(shutil.which('php'), 'PHP CLI required')
class FormHandlerHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix='lead-forms-')
        cls.root = Path(cls.tmp.name)
        cls.web = cls.root / 'web'
        shutil.copytree(FORMS, cls.web / 'forms')
        for d in ('rate', 'outbox'):
            (cls.root / d).mkdir()
        with socket.socket() as sock:
            sock.bind(('127.0.0.1', 0))
            cls.port = sock.getsockname()[1]
        cls.origin = f'http://127.0.0.1:{cls.port}'
        cls.config = cls.root / 'config.json'
        cls.write_config()
        cls.log = (cls.root / 'php.log').open('w+')
        cls.proc = subprocess.Popen(['php', '-S', f'127.0.0.1:{cls.port}', '-t', str(cls.web)],
                                    env={**os.environ, 'LEAD_FORMS_CONFIG': str(cls.config)}, stdout=cls.log, stderr=cls.log)
        for _ in range(100):
            try:
                with socket.create_connection(('127.0.0.1', cls.port), timeout=.1):
                    break
            except OSError:
                time.sleep(.02)
        else:
            raise RuntimeError('Local PHP server did not start')

    @classmethod
    def write_config(cls, **changes):
        config = {
            'recipients': {'contact': 'team@example.org', 'downloadfocus': 'focus@example.org'},
            'from': 'website@example.org', 'site': 'www.example.org', 'origins': [cls.origin],
            'pages': {'contact': '/contact/', 'downloadfocus': '/focus/'},
            'rate_dir': str(cls.root / 'rate'), 'rate_key': 'test-key', 'limit': 1000, 'window': 600,
            'delivery': 'outbox', 'outbox': str(cls.root / 'outbox'),
        }
        config.update(changes)
        cls.config.write_text(json.dumps(config))

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait(timeout=5)
        cls.log.close()
        cls.tmp.cleanup()

    def setUp(self):
        self.write_config()
        for d in ('rate', 'outbox'):
            for f in (self.root / d).iterdir():
                f.unlink()

    def post(self, fields, json_reply=True, headers=None, method='POST', body=None):
        con = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        h = {'Content-Type': 'application/x-www-form-urlencoded', 'Origin': self.origin}
        if json_reply:
            h['Accept'] = 'application/json'
        h.update(headers or {})
        con.request(method, '/forms/send.php', body=body if body is not None else urlencode(fields), headers=h)
        r = con.getresponse()
        data = r.read()
        con.close()
        return r.status, (json.loads(data) if json_reply and data else data.decode())

    def outbox(self):
        return [p.read_bytes().decode() for p in sorted((self.root / 'outbox').iterdir())]

    contact = {'form': 'contact', 'website': '', 'name': 'Ada Lovelace', 'email': 'ada@example.org',
               'message': 'Hello,\nhow do I cite Lead-DBS?'}
    focus = {'form': 'downloadfocus', 'website': '', 'first_name': 'Jürgen', 'last_name': 'Müller',
             'institution': 'Charité', 'email': 'jm@example.org', 'academic': 'yes'}

    def test_fields_match_data_forms_yaml(self):
        php = subprocess.run(['php', '-r', f'require "{FORMS}/FormHandler.php"; echo json_encode(LeadForms\\FormHandler::FORMS);'],
                             capture_output=True, text=True, check=True)
        server = json.loads(php.stdout)
        site = yaml_fields()
        for form, spec in server.items():
            self.assertEqual(site[form]['fields'], list(spec['fields']), form)
            self.assertEqual(site[form]['action'], 'forms/send.php', form)
        # a form with an action that the server does not know would be refused on every submission
        for form, spec in site.items():
            if spec['action']:
                self.assertIn(form, server)

    def test_contact_is_sent_to_the_fixed_address(self):
        status, reply = self.post(self.contact)
        self.assertEqual((status, reply['ok']), (200, True))
        [mail] = self.outbox()
        self.assertIn('To: team@example.org\r\n', mail)
        self.assertIn('Reply-To: ada@example.org\r\n', mail)
        self.assertIn('From: Lead-DBS website <website@example.org>\r\n', mail)
        self.assertIn('Subject: Contact form: Ada Lovelace\r\n', mail)
        self.assertIn('Hello,\r\nhow do I cite Lead-DBS?', mail)
        self.assertNotIn('127.0.0.1', mail)

    def test_focus_request_records_the_choices(self):
        status, reply = self.post(self.focus)
        self.assertEqual(status, 200)
        self.assertIn('download link', reply['message'])
        [mail] = self.outbox()
        self.assertIn('To: focus@example.org\r\n', mail)
        self.assertIn('Subject: FOCUS request form: =?UTF-8?Q?J=C3=BCrgen', mail)  # the umlauts are encoded
        self.assertIn('Institution: Charité', mail)
        self.assertIn('Academic research only: yes', mail)
        self.assertIn('Also wants the newsletter: no', mail)
        self.post({**self.focus, 'newsletter': 'yes'})
        self.assertEqual(sum('Also wants the newsletter: yes' in m for m in self.outbox()), 1)

    def test_focus_needs_the_academic_terms(self):
        status, reply = self.post({k: v for k, v in self.focus.items() if k != 'academic'})
        self.assertEqual((status, reply['ok']), (400, False))
        self.assertEqual(self.outbox(), [])

    def test_invalid_submissions_are_refused(self):
        cases = [
            {**self.contact, 'email': 'not-an-address'},
            {**self.contact, 'email': 'a@example.org\r\nBcc: victim@example.org'},
            {**self.contact, 'message': ''},
            {**self.contact, 'message': 'x' * 5001},
            {**self.contact, 'extra': 'field'},
            {**self.contact, 'form': 'newsletter'},
            {**self.contact, 'form': 'unknown'},
            {**self.focus, 'academic': 'maybe'},
        ]
        for fields in cases:
            with self.subTest(fields=list(fields)):
                self.assertEqual(self.post(fields)[0], 400)
        self.assertEqual(self.outbox(), [])

    def test_header_injection_through_the_name_stays_in_the_subject(self):
        self.assertEqual(self.post({**self.contact, 'name': 'Eve\r\nBcc: victim@example.org'})[0], 200)
        [mail] = self.outbox()
        headers = mail.split('\r\n\r\n', 1)[0]
        self.assertNotRegex(headers, r'(?m)^Bcc:')
        self.assertIn('Subject: Contact form: Eve Bcc: victim@example.org\r\n', headers)

    def test_trap_field_answers_success_and_sends_nothing(self):
        status, reply = self.post({**self.contact, 'website': 'http://spam.example'})
        self.assertEqual((status, reply['ok']), (200, True))
        self.assertEqual(self.outbox(), [])

    def test_methods_types_sizes_and_origins(self):
        self.assertEqual(self.post({}, method='GET', body='')[0], 405)
        self.assertEqual(self.post({}, headers={'Content-Type': 'application/json'}, body='{}')[0], 415)
        self.assertEqual(self.post({**self.contact, 'message': 'x' * 20000})[0], 413)
        self.assertEqual(self.post(self.contact, headers={'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.outbox(), [])

    def test_rate_limit_without_storing_the_address(self):
        self.write_config(limit=2)
        self.assertEqual([self.post(self.contact)[0] for _ in range(3)], [200, 200, 429])
        self.assertEqual(len(self.outbox()), 2)
        for f in (self.root / 'rate').iterdir():
            self.assertRegex(f.name, r'^[0-9a-f]{64}$')
            self.assertNotIn('127.0.0.1', f.read_text())

    def test_delivery_failure_is_reported_and_logged_without_contents(self):
        self.write_config(outbox=str(self.root / 'outbox' / 'missing'))
        status, reply = self.post(self.contact)
        self.assertEqual((status, reply['ok']), (503, False))
        (self.root / 'outbox' / 'missing').mkdir()
        self.write_config(outbox=str(self.root / 'outbox' / 'missing'))
        os.chmod(self.root / 'outbox' / 'missing', 0o500)
        try:
            self.assertEqual(self.post(self.contact)[0], 503)
        finally:
            os.chmod(self.root / 'outbox' / 'missing', 0o700)
            (self.root / 'outbox' / 'missing').rmdir()
        self.log.flush()
        log = (self.root / 'php.log').read_text()
        self.assertNotIn('ada@example.org', log)
        self.assertNotIn('cite Lead-DBS', log)

    def test_private_files_inside_the_web_root_are_refused(self):
        inside = self.web / 'rate'
        inside.mkdir(exist_ok=True)
        self.write_config(rate_dir=str(inside))
        self.assertEqual(self.post(self.contact)[0], 503)
        self.assertEqual(self.outbox(), [])

    def test_without_script_the_reply_is_a_page_with_a_way_back(self):
        status, page = self.post(self.contact, json_reply=False)
        self.assertEqual(status, 200)
        self.assertIn('your message is sent', page)
        self.assertIn('href="/contact/"', page)
        status, page = self.post({**self.contact, 'email': 'bad', 'name': '<script>x</script>'}, json_reply=False)
        self.assertEqual(status, 400)
        self.assertNotIn('<script>', page)


if __name__ == '__main__':
    unittest.main()
