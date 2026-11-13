# Contact and FOCUS forms: not deployed

`send.php` takes the contact form (`/contact/`) and the FOCUS request form (the FOCUS atlas page) and emails
each submission to a fixed address. It has **not been deployed**, and nothing in this repository changes the
live server. The site keeps showing the email fallbacks until `formsEnabled = true` is set in `hugo.toml`, and
that should only happen at the switch, after Andy has put this folder on the server and it has passed the
checks below.

The newsletter form is not handled here. It keeps its News/RSS line until the newsletter service is decided.

## What it does

- Accepts only `POST` form submissions of at most 16 KB, from the origins listed in the config, for the
  forms `contact` and `downloadfocus`. Only the fields in `FormHandler::FORMS` are accepted (these must match
  `data/forms.yaml`, which `tests/test_forms_http.py` checks), with length limits and email-address checks.
- Sends a plain-text email to the address in the config, never to an address from the form. The sender's
  address goes in `Reply-To` after validation, so line breaks can't add headers.
- Bots: a hidden `website` field. A submission that fills it gets "sent" back, and nothing is sent.
  Each address may send `limit` submissions per `window` seconds. Only a keyed hash of the address is
  stored, the hash changes every day, and the files are deleted after two days.
- FOCUS: the academic-use box must be ticked. The newsletter box is optional, and the email only says
  "yes" or "no". Someone adds the person to the newsletter by hand. Nothing subscribes them automatically.
- Answers JSON to the page's script (`assets/js/main/forms.js`) or a small HTML page when the browser has no
  script. A success means the server accepted the email for delivery, not that it reached the inbox.
- Failures go to the PHP error log as one line naming the form, with no field values.

## Deploying (at the switch, with Andy)

1. Requirements: PHP 8.1+ with `mbstring`, and a working `mail()` on the hosting package. STRATO usually needs
   the sender to be an address of the domain (`from`) and the envelope sender set (`envelope_sender: true`).
2. Copy `send.php`, `FormHandler.php` and `.htaccess` to `forms/` in the web root, so the address is
   `https://www.lead-dbs.org/forms/send.php` (the site's forms post to `forms/send.php`). The `.htaccess` lets
   only `send.php` be fetched. Like `/release/` and `/docs/`, this folder isn't part of the Hugo build, so
   a site deploy that empties the web root must keep it.
3. Outside the web root, create a private folder with `config.json` (shaped like `config.example.json`) and a
   writable `rate/` folder. Set `LEAD_FORMS_CONFIG` to the config's absolute path. If the package can't set
   environment variables, `send.php` looks for `lead-forms/config.json` in the folder above the web root.
   It refuses to run if the config or the rate folder is inside the web root. Make `rate_key` a long random
   string generated on the server.
4. Before switching the site over, run the checks with a test recipient address in the config:
   - submit both forms; the emails arrive, `Reply-To` works, umlauts are right, they aren't marked as spam
   - a missing field, a bad address and an unticked academic box are refused
   - opening `forms/FormHandler.php` and `forms/.htaccess` in the browser is refused
   - with the default limit, the sixth submission within ten minutes is refused with "Too many messages"
   - the rate folder holds only 64-character hash names
   Then put the real recipient in the config.
5. Set `formsEnabled = true` in `hugo.toml` and deploy the site.

To try it locally without the server, set `"delivery": "outbox"` and an `outbox` folder. Each email is then
written there as a `.eml` file instead of being sent. See `tests/test_forms_http.py`.

## Still to be decided by the lab

- The recipients (now `mail@andreas-horn.de` for both forms in the example config) and a backup person.
- The privacy policy wording for these forms: what is collected, who receives it, how long it is kept.
  The current privacy page is WordPress's default text.
