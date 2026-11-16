"""The contact/FOCUS form handler (server/forms/) on a loopback PHP server. Mail goes into a temporary outbox
folder, never to a real address, and nothing talks to STRATO."""
import http.client
import json
import os
from pathlib import Path
import re
import shutil
import socket
import stat
import subprocess
import tempfile
import time
import unittest
from urllib.parse import urlencode

from prerequisites import needs

ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / 'server/forms'
KEY = 'test-key-0123456789abcdef0123456789abcdef'


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


@needs(shutil.which('php'), 'PHP CLI')
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
        # the usual umask, so that the files' modes come from the handler and not from the test
        previous = os.umask(0o022)
        try:
            cls.proc = subprocess.Popen(['php', '-S', f'127.0.0.1:{cls.port}', '-t', str(cls.web)],
                                        env={**os.environ, 'LEAD_FORMS_CONFIG': str(cls.config)},
                                        stdout=cls.log, stderr=cls.log)
        finally:
            os.umask(previous)
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
            'rate_dir': str(cls.root / 'rate'), 'rate_key': KEY, 'limit': 100, 'window': 600,
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

    def post(self, fields, json_reply=True, headers=None, method='POST', body=None, path='/forms/send.php',
             response=False):
        con = http.client.HTTPConnection('127.0.0.1', self.port, timeout=5)
        h = {'Content-Type': 'application/x-www-form-urlencoded', 'Origin': self.origin}
        if json_reply:
            h['Accept'] = 'application/json'
        h.update(headers or {})
        con.request(method, path, body=body if body is not None else urlencode(fields), headers=h)
        r = con.getresponse()
        data = r.read()
        con.close()
        reply = json.loads(data) if json_reply and data else data.decode()
        return (r.status, reply, r) if response else (r.status, reply)

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
        for fields in (self.contact, self.focus):
            with self.subTest(form=fields['form']):
                real = self.post(fields)
                trapped = self.post({**fields, 'website': 'http://spam.example'})
                self.assertEqual(trapped, real)     # a bot can't tell the difference
        self.assertEqual(len(self.outbox()), 2)

    def test_replies_say_what_happened(self):
        self.assertEqual(self.post(self.contact)[1]['message'], 'Message sent. We’ll reply by email.')
        self.assertEqual(self.post(self.focus)[1]['message'], 'Request sent. The team will email you the download link.')

    def test_a_refused_field_is_named_with_what_to_fix(self):
        cases = [
            ({**self.contact, 'name': ''}, 'name', 'Enter your name.'),
            ({**self.contact, 'email': ''}, 'email', 'Enter your email address.'),
            ({**self.contact, 'email': 'not-an-address'}, 'email', 'Enter a valid email address.'),
            ({**self.contact, 'message': '  '}, 'message', 'Enter your message.'),
            ({k: v for k, v in self.focus.items() if k != 'academic'}, 'academic',
             'Confirm that FOCUS will be used for academic research only.'),
            ({**self.contact, 'message': 'x' * 5001}, 'message', 'Check the required fields and email address, then send again.'),
        ]
        for fields, field, message in cases:
            with self.subTest(field=field, message=message):
                status, reply = self.post(fields)
                self.assertEqual((status, reply), (400, {'ok': False, 'message': message, 'field': field}))
        # a submission that is wrong as a whole names no field
        status, reply = self.post({**self.contact, 'extra': 'field'})
        self.assertEqual((status, reply), (400, {'ok': False, 'message': 'Check the required fields and email address, then send again.'}))
        status, page = self.post({**self.contact, 'email': ''}, json_reply=False)
        self.assertEqual(status, 400)
        self.assertIn('Enter your email address.', page)
        self.assertEqual(self.outbox(), [])

    def test_methods_types_sizes_and_origins(self):
        self.assertEqual(self.post({}, method='GET', body='')[0], 405)
        self.assertEqual(self.post({}, headers={'Content-Type': 'application/json'}, body='{}')[0], 415)
        self.assertEqual(self.post({**self.contact, 'message': 'x' * 140000})[0], 413)
        self.assertEqual(self.post(self.contact, headers={'Origin': 'https://evil.example'})[0], 403)
        self.assertEqual(self.outbox(), [])

    def test_rate_limit_without_storing_the_address(self):
        self.write_config(limit=2)
        self.assertEqual([self.post(self.contact)[0] for _ in range(2)], [200, 200])
        status, reply, r = self.post(self.contact, response=True)
        self.assertEqual((status, reply['message']), (429, 'Too many requests. Try again in 10 minutes.'))
        self.assertEqual(r.getheader('Retry-After'), '600')
        self.assertEqual(len(self.outbox()), 2)
        for f in (self.root / 'rate').iterdir():
            self.assertRegex(f.name, r'^[0-9a-f]{64}$')
            self.assertNotIn('127.0.0.1', f.read_text())
            self.assertEqual(stat.S_IMODE(f.stat().st_mode), 0o600, 'readable by others')
        self.write_config(limit=1, window=60)
        status, reply, r = self.post(self.contact, response=True)
        self.assertEqual((status, reply['message'], r.getheader('Retry-After')),
                         (429, 'Too many requests. Try again in a minute.', '60'))

    def test_an_unsafe_configuration_is_refused(self):
        cases = {
            'the example key': {'rate_key': 'replace with a long random string generated on the server'},
            'a short key': {'rate_key': 'short'},
            'no limit': {'limit': 0},
            'a limit as text': {'limit': '5'},
            'a window over a day': {'window': 2 * 86400},
            'a window under a minute': {'window': 10},
        }
        for why, change in cases.items():
            with self.subTest(why=why):
                self.write_config(**change)
                self.assertEqual(self.post(self.contact)[0], 503)
                self.assertEqual(self.outbox(), [])
        self.log.flush()
        self.assertNotIn('replace with a long', (self.root / 'php.log').read_text())

    def sweep(self, *args, config=None):
        return subprocess.run(['php', str(FORMS / 'sweep.php'), *args], capture_output=True, text=True,
                              env={**os.environ, 'LEAD_FORMS_CONFIG': str(config or self.config)})

    def test_the_scheduled_sweep_deletes_old_rate_files_without_any_traffic(self):
        rate = self.root / 'rate'
        old, recent = rate / ('a' * 64), rate / ('b' * 64)
        for f in (old, recent):
            f.write_text('1700000000\n')
        three_days_ago = time.time() - 3 * 86400
        os.utime(old, (three_days_ago, three_days_ago))
        (rate / 'notes.txt').write_text('not a rate file')
        r = self.sweep()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(old.exists())
        self.assertTrue(recent.exists())
        self.assertTrue((rate / 'notes.txt').exists())
        status = rate / 'sweep-status.json'
        self.assertEqual(json.loads(status.read_text())['removed'], 1)
        self.assertEqual(stat.S_IMODE(status.stat().st_mode), 0o600)
        self.assertEqual(self.sweep('check').returncode, 0)
        # monitoring: a sweep that hasn't run for hours, or never, needs attention
        data = json.loads(status.read_text())
        data['completed_at'] = time.strftime('%Y-%m-%dT%H:%M:%S+00:00', time.gmtime(time.time() - 3 * 3600))
        status.write_text(json.dumps(data))
        self.assertEqual(self.sweep('check').returncode, 1)
        status.unlink()
        self.assertEqual(self.sweep('check').returncode, 1)

    def test_a_sweep_that_fails_says_so(self):
        self.write_config(rate_key='short')
        r = self.sweep()
        self.assertEqual(r.returncode, 1)
        self.assertIn('rate_key', r.stderr)
        self.write_config()
        rate = self.root / 'rate'
        old = rate / ('c' * 64)
        old.write_text('1\n')
        os.utime(old, (0, 0))
        os.chmod(rate, 0o500)                  # the file can't be removed
        try:
            if os.access(rate, os.W_OK):
                self.skipTest('running as a user that ignores folder permissions')
            r = self.sweep()
        finally:
            os.chmod(rate, 0o700)
        self.assertEqual(r.returncode, 1)
        self.assertTrue(old.exists())
        self.assertNotEqual(self.sweep('check').returncode, 0)

    def test_the_sweep_is_not_a_web_address(self):
        status, _ = self.post({}, method='GET', body='', json_reply=False, path='/forms/sweep.php')
        self.assertEqual(status, 404)

    def test_long_messages_in_any_script_fit_without_script(self):
        # 5000 four-byte characters, percent-encoded as a form without script sends them: 60 000 bytes
        status, _ = self.post({**self.contact, 'message': '\U0001F9E0' * 5000})
        self.assertEqual(status, 200)
        status, _ = self.post({**self.contact, 'message': '界' * 5000}, json_reply=False)
        self.assertEqual(status, 200)

    def php(self, code, ulimit_zero=False):
        script = f'require "{FORMS}/FormHandler.php"; use LeadForms\\FormHandler; ' + code
        cmd = ['php', '-d', 'display_errors=stderr', '-r', script]
        if ulimit_zero:  # every write fails, as on a full disk or quota
            cmd = ['bash', '-c', "trap '' XFSZ; ulimit -f 0; exec \"$@\"", 'php'] + cmd
        return subprocess.run(cmd, capture_output=True, text=True)

    def test_rate_limit_counts_across_midnight(self):
        d = tempfile.mkdtemp(dir=self.root)
        out = self.php(f'$m = gmmktime(0, 0, 0, 1, 2, 2027); foreach ([$m - 2, $m - 1, $m + 1, $m + 2] as $t) '
                       f'echo FormHandler::overLimit("{d}", "k", "1.2.3.4", 2, 600, $t) ? "blocked " : "allowed ";').stdout
        self.assertEqual(out.split(), ['allowed', 'allowed', 'blocked', 'blocked'])
        # and outside the window it starts again
        out = self.php(f'echo FormHandler::overLimit("{d}", "k", "1.2.3.4", 2, 600, gmmktime(0, 11, 0, 1, 2, 2027)) ? "blocked" : "allowed";').stdout
        self.assertEqual(out, 'allowed')

    @unittest.skipUnless(shutil.which('bash'), 'bash required')
    def test_rate_limit_refuses_when_its_storage_cannot_be_written(self):
        d = tempfile.mkdtemp(dir=self.root)
        r = self.php(f'try {{ FormHandler::overLimit("{d}", "k", "1.2.3.4", 2, 600); echo "allowed"; }} '
                     f'catch (RuntimeException $e) {{ echo "refused"; }}', ulimit_zero=True)
        self.assertEqual(r.stdout, 'refused', r.stderr)

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
        self.assertIn('Message sent.', page)
        self.assertIn('href="/contact/"', page)
        status, page = self.post({**self.contact, 'email': 'bad', 'name': '<script>x</script>'}, json_reply=False)
        self.assertEqual(status, 400)
        self.assertNotIn('<script>', page)


if __name__ == '__main__':
    unittest.main()
