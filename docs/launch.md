# Taking the new site live on www.lead-dbs.org

The new site replaces the WordPress pages on the same STRATO web space and the same domain. **Nothing here has
been done on the server.** Every step that touches it is Andy's, on a day Richard, Andy and Philip agree on.
Everything marked *ready* has been rehearsed on this repository's side: a local Apache serving a fake copy of the
web root (`tests/test_launch_server.py`).

## How the switch works

The Hugo build is copied **into the web root beside WordPress**, and a new `.htaccess`
(`server/apache/htaccess`) decides who answers:

| Address | Answered by |
|---|---|
| every page of the site; old WordPress addresses (`/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`, `/category/…`) | the Hugo build (old addresses are redirect pages in it) |
| `/forums/…` (the retired forum), `/author/…` | HTTP 301 to `/helpsupport/forum/` and `/about/team/` (the build keeps redirect pages for the same addresses, for a host without these rules) |
| `/?na=…`: newsletter sign-up, confirmation, **unsubscribe links in emails already sent**, archive `/?na=view&id=…` | WordPress, which stays installed |
| `/?p=…`, `/?page_id=…`, `/?cat=…`, `/?author=…` | WordPress, which redirects them to the post's address (now a Hugo page) |
| `/wp-admin/`, `/wp-login.php`, `/wp-json/` | WordPress (needed to send newsletters) |
| `/release/`, `/docs/`, `/forms/`, `/wp-content/` (uploads linked from papers) | untouched, served as they are |
| `/?s=word` | redirect to `/search/?q=word` |
| `/feed/`, `/news/feed/`, `/comments/feed/` | redirect to the news feed `/news/index.xml` |
| `/xmlrpc.php` | 410 Gone |
| private files in any folder: dot-files (except `/.well-known/`), `composer.json`, `vendor/`, `logs/`, `backups/`, `*.log`, `*.bak`, `*.sql`, `*.sqlite`, config and editor copies, PHP in `/wp-content/uploads/` | 403, whatever a folder's own `.htaccess` says |
| anything else | the site's 404 page with status 404 (no longer WordPress) |

WordPress is not removed, so the newsletter, its subscriber list and its unsubscribe links keep working.
Going back to WordPress means taking the new files out again, which `tools/deploy.py rollback` does in
seconds. Going back to an earlier version of the new site means deploying that version's package again (keep
the last two packages, unpacked, outside the web root).

## Ready

- `tools/deploy.py package` builds the production site from a fresh clone of the repository at the current
  commit, so nothing untracked or ignored can enter it, checks it, and packs it with the `.htaccess`, the deploy
  tool itself and `MANIFEST.json` (the commit and every file's sha256). It refuses a checkout with uncommitted
  changes and prints the full commit and the manifest's sha256: note both in the switch-day record.
- `tools/deploy.py plan / deploy / rollback`:
  - `plan` changes nothing. It lists every file of the server it would replace. With `--inventory FILE` it
    also writes the lists a deploy by hand needs (below).
  - `plan` and `deploy` refuse a `site/` folder that differs from its `MANIFEST.json` in any way: a changed,
    missing or extra file, or a symbolic link.
  - `deploy` never touches `release/`, `docs/`, `forms/`, `wp-*`, `index.php` or `.well-known/`. It refuses
    when the build would overwrite one of those, when a file or a symbolic link is in the way, and when the
    package, the web root and the state folder overlap.
  - It keeps every file it replaces in a state folder outside the web root. It records itself (with the web
    root it belongs to) before changing anything, so even a deploy cut off halfway can be rolled back; a new
    deploy refuses until that rollback is done. Used with another web root, the state is refused.
  - One deploy or rollback at a time: a second one, from another terminal, is refused while the first holds
    the state folder's lock.
  - It puts files in first, then the pages that use them, and the `.htaccess` last. Each file is written under
    a temporary name and renamed into place, so nobody gets half a file.
  - Fingerprinted files that a new deploy no longer has (old stylesheets, scripts, processed images) stay for
    7 days (`--grace-days`), so pages that were open before the deploy still find them.
  - `rollback` puts the old `.htaccess` back first, then the pages and the rest, and restores the web root
    byte for byte (WordPress as it was before the first deploy).
- `tools/check_launch.py` fails a build that:
  - is a preview (noindex, the banner, links to the preview)
  - has a robots.txt that shuts search engines out, or a sitemap off www.lead-dbs.org
  - shows TODO text
  - lacks its 404 page, feed or search index

  It also lists the server addresses the site depends on, so they can be checked after the switch.
- The contact and FOCUS forms (`server/forms/`, PR #36) are written but switched off. The page shows
  the email address until the forms are checked on the server.
- `server/apache/htaccess` on a local Apache (`tests/test_launch_server.py`): the routes in the table above,
  private files refused, gzip with `Vary: Accept-Encoding` for text, a year's caching for fingerprinted files and
  revalidation for pages, the MIME type of every kind of file the build has, byte ranges for videos, and the
  security headers below. `tests/test_csp_browser.mjs` loads every page with the Content Security Policy
  enforced and fails on any violation.
- CI: `.github/workflows/backend.yml` runs every server-side test with none skipped, checks the PHP version
  and extensions, and audits the locked Composer packages (also weekly). The Pages workflow checks the static
  site only.

## Security headers

The `.htaccess` sends `nosniff`, a referrer policy, `X-Frame-Options: SAMEORIGIN` and a permissions policy on
every answer, and two headers that are rolled out in steps:

- **Content Security Policy, report-only.** On the build's pages only (WordPress and the PHP folders send
  their own): scripts from the site itself plus the sha256 of each inline script of the build (filled in by
  `deploy.py package`, which refuses a page with an inline event handler), styles from the site and inline,
  pictures from the site and `data:`, players only from `www.youtube-nocookie.com` and `player.vimeo.com`, no
  plugins (`object-src 'none'`), `base-uri 'self'`, `form-action 'self'`, `frame-ancestors 'self'`. It has no
  report address: collecting reports would be a new processing of visitors' data. Instead
  `tests/test_csp_browser.mjs` runs every page with it enforced on each pull request. To enforce it: after two
  weeks live with no problems reported, rename the header to `Content-Security-Policy` in
  `server/apache/htaccess`, run the tests, deploy.
- **HSTS** (`Strict-Transport-Security`), only on HTTPS answers: `max-age=86400` (a day) at the switch. After
  two weeks without certificate or HTTPS problems raise it to `max-age=31536000`. Add `includeSubDomains`
  only once every subdomain of lead-dbs.org is known to answer on HTTPS, and never `preload` without the lab's
  decision: both are hard to undo.

## Blockers

### Andy (hosting)

1. **Access and method.** Does the package have SSH, and Python 3 on the server? If yes, run
   `deploy.py` there from the unpacked package. If not, use "By hand" below.
2. **The current `.htaccess`.** Any rule outside its `# BEGIN WordPress … # END WordPress` block (for
   `/release/`, PHP versions, old redirects) must be copied into `server/apache/htaccess` before the switch.
3. **Name clashes.** Run `deploy.py plan` against the real web root. It lists every file of the build that
   already exists there (e.g. `favicon.ico`, a `robots.txt`, a search-console proof file), and refuses on a
   clash it can't handle safely.
4. **Server setup.** Confirm that Apache is 2.4 (the `.htaccess` uses `<If>`), that the web root's
   `.htaccess` is honoured in full (`AllowOverride All`), and that `mod_rewrite`, `mod_headers`, `mod_mime`
   and `mod_deflate` are on. Every block for an optional module is wrapped in `<IfModule>`, so a missing
   module loses its rules silently: the acceptance checks below are what proves them. Find out which file
   holds the release downloads' log, so the switch-day checks can confirm it is refused.
5. **HTTPS and www.** If STRATO's domain settings already redirect `lead-dbs.org` to `https://www.…`, delete
   those two rules from the `.htaccess`. Does STRATO end TLS in a proxy in front of Apache? If not, delete the
   `X-Forwarded-Proto` line (it then only lets a visitor skip the redirect to HTTPS). DNS stays as it is; the
   mail records aren't touched.
6. **A full backup** of the web root and the WordPress database on the morning of the switch, besides
   `deploy`'s own.

### The lab (Andreas, with Richard)

1. **Privacy notice: a launch gate.** The site does not go live until an institution-approved privacy notice
   and imprint are published. `content/privacy-policy/index.md` describes only what the repository can confirm;
   `docs/launch/privacy-draft.md` is the fuller draft. Still open, each needing an answer from the named person
   or the data-protection office:
   - the controller and provider (Andreas personally, the institute or the clinic), its postal address, and
     whether a data-protection officer is named;
   - the legal basis for server logs, download logs and statistics, and the software's optional usage
     statistics (legitimate interests may not be open to a public body);
   - STRATO's data-processing agreement and server location;
   - how long raw server logs, release download logs, the form inbox and backups are kept;
   - the newsletter: double opt-in and who can see the list;
   - the supervisory authority that fits the controller.
   The forms and the new analytics collector stay off until the notice covers them.
2. **Imprint.** It names a private US address. Who is the responsible provider, and is that address meant
   to stay? See the questions in the draft.
3. **Go/no-go.** The date, and who watches the site and the inbox on the first day.

## Should do before or right after the switch

- **A dress rehearsal on STRATO** (Andy). Copy the web root to a test subdomain (e.g. `new.lead-dbs.org`),
  run `plan`, `deploy`, the acceptance checks below, the switch-day checks and `rollback` once there.
- **Acceptance of the server's answers** (Andy, on the rehearsal host; `HOST` is its address). Each line must
  print what its comment says:

      curl -s -D - -o /dev/null --compressed https://HOST/ | grep -iE '^(content-encoding|vary|cache-control|strict-transport|content-security-policy-report-only):'
      # content-encoding: gzip, vary: Accept-Encoding, cache-control: no-cache, strict-transport-security: max-age=86400, the policy
      curl -sI https://HOST/css/$(ls site/css | head -1) | grep -i '^cache-control'       # public, max-age=31536000, immutable
      curl -sI https://HOST/sitemap.xml | grep -i '^content-type'                           # application/xml; charset=utf-8
      curl -s -o /dev/null -w '%{http_code}\n' -r 0-99 https://HOST/media/hero-lead-stn-1280.mp4   # 206
      curl -s -o /dev/null -w '%{http_code}\n' https://HOST/.htaccess                       # 403
      curl -s -o /dev/null -w '%{http_code}\n' https://HOST/<the release log's path>        # 403
      curl -s -o /dev/null -w '%{http_code} %{redirect_url}\n' https://HOST/forums/topic/x/   # 301 …/helpsupport/forum/
      curl -s -o /dev/null -w '%{http_code}\n' https://HOST/.well-known/acme-challenge/x    # 404, not 403

  On the rehearsal host the redirects point to that host; on the live one, to www.lead-dbs.org.
- **Content check** (Richard). Look at what changed on WordPress since the import of 10 November and copy
  it over by hand; don't rerun the importer, which overwrites edits. Other things to check:
  - The Cologne workshop (`data/events.yaml`, `hands-on-workshop-2027`) has no registration link yet.
  - The release data (`data/release.yaml`: 3.2.1) should still be current on the day.
- **Rebuilds** (Philip, Andy). The site's dates (the next event, countdowns) are fixed at build time. The
  preview rebuilds nightly; STRATO doesn't. Deploy again after every merge and at least weekly, or agree
  on a scheduled job that runs `package` and `deploy`.
- **Search Console** (Richard or Andreas). Confirm ownership, submit `https://www.lead-dbs.org/sitemap.xml`,
  and watch the coverage report and 404s for two weeks.
- **Monitoring** (Andy). Uptime and certificate expiry for the domain, and an alert if
  `/release/download.php` fails. Don't use probes that start downloads or send forms: they skew the
  download statistics and the inbox.

## Later

- **Forms.** Switch them on after their own checks on the server (`server/forms/README.md`): recipients, a
  test address, then `formsEnabled = true` and a new deploy.
- **Newsletter sign-up on the new site.** The subscribers stay in WordPress. The new site's newsletter form
  could post to the plugin (`/?na=s`) once someone with WordPress access confirms the plugin's settings and
  double opt-in. Until then the page points to News and RSS.
- **The analytics collector** (`server/analytics/`) is a separate project and not needed for the switch.

## Who does what

| Who | What |
|---|---|
| Andy | access and method, the current `.htaccess`, `plan` on the server, backups, the switch and any rollback, monitoring |
| Philip | merge #36 and the launch PR, tag the deployed commit (`live-YYYY-MM-DD`), later deploys; branch protection for `main` requiring the checks `checks`, `browser` (Checks) and `backend` (Backend) |
| Richard | content check, go/no-go, the first-day check list, Search Console |
| Andreas (with the institution) | privacy policy and imprint, form recipients |

## Switch day

Before, with the site still on WordPress:

1. `git checkout main && git pull && tools/deploy.py package`. It stops on any problem. Note the commit and
   the `MANIFEST.json` sha256 it prints. Copy `dist/lead-dbs-site-<commit>.tar.gz` to the server, **outside**
   the web root, and unpack it. Keep the previous package's folder there too.
2. `python3 lead-dbs-site-<commit>/deploy.py plan lead-dbs-site-<commit>/site <webroot> --state <outside>/lead-site-state`,
   and read what it would replace.

The switch, which takes about a minute:

3. The same command with `deploy` instead of `plan`.

Check at once, in a private browser window and then on a phone. **If any of 1–4 fails, roll back first and
investigate afterwards.**

1. `https://www.lead-dbs.org/` shows the new home page, without the "under construction" banner.
2. A **download button** works: `/release/download.php?id=…` starts the download, and the release log grows.
3. `/?na=view&id=33` shows the newsletter, and `/wp-admin/` logs in.
4. A PDF under `/docs/` and one under `/wp-content/uploads/` open.
5. Old addresses work: `/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`, `/author/andreashorn/`, `/feed/`,
   `/?s=atlas`, `/?p=1`, `/forums/topic/anything/` (301 to the forum page).
6. `/no-such-page/` shows the site's 404 page, with status 404.
7. Search, the manual, the gallery and a video (click to load) work. The page source has no `noindex`.
8. The release log is refused: its address answers 403.

## Rollback

    python3 lead-dbs-site-<commit>/deploy.py rollback <webroot> --state <outside>/lead-site-state

The old `.htaccess` goes back first, so the old rules apply again. Until the build's files are out, an
address that is still a file of the build (the home page among them: the old rules serve any file that
exists) still shows the new site; that takes seconds. Then every file of the build is taken out and every
file the deploy replaced is restored. Check that `https://www.lead-dbs.org/` shows WordPress and a download
button works. Andy's full backup is the second line of defence.

This goes back to WordPress. To go back to the previous version of the new site instead, deploy its package
again: `python3 <previous package>/deploy.py deploy <previous package>/site <webroot> --state <the same state>`.
`deployed.json` in the state folder lists the commits deployed (`history`).

## By hand (no SSH)

`tests/test_launch_server.py` rehearses exactly these steps.

1. Make a copy of the web root's file names (empty files will do, but every name must be there), and run
   `plan` on it with `--inventory inventory.json`. The inventory lists `upload` (every file, in order),
   `add` (files that are new), `replace` (files already there that the build replaces, the `.htaccess`
   among them) and `new_folders`.
2. Download every file in `replace` from the server into a folder `originals/`, keeping the paths. Record
   their checksums: `cd originals && find . -type f -exec sha256sum {} + > ../originals.sha256`.
3. Upload the files of `upload` by SFTP in that order: the `.htaccess` comes last.

To roll back by hand:

1. Upload `originals/.htaccess` first.
2. Upload every other file of `originals/` to its place: these are the files the build replaced.
3. Delete every file in `add`, and nothing else.
4. Delete the folders in `new_folders`, deepest first; each is empty by then.
5. Download the replaced files again and check them against `originals.sha256` (`sha256sum -c`), then check
   that the home page shows WordPress and a download button works.

Until step 3 is done, addresses that are still files of the build show the new site (the old rules serve any
file that exists).

## Not checked, because the live server is off limits

- the real web root's contents and `.htaccess`
- the PHP version
- whether `mod_rewrite` and `mod_headers` are allowed
- STRATO's domain and TLS settings
- the newsletter plugin's version and settings
- what changed on WordPress since the import
- which other files on the server are linked from elsewhere
