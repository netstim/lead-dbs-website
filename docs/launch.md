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
| every page of the site; old WordPress addresses (`/about/citing_leaddbs/`, `/lead-dbs-3-0-out-now/`, `/author/…`, `/category/…`) | the Hugo build (old addresses are redirect pages in it) |
| `/?na=…`: newsletter sign-up, confirmation, **unsubscribe links in emails already sent**, archive `/?na=view&id=…` | WordPress, which stays installed |
| `/?p=…`, `/?page_id=…`, `/?cat=…`, `/?author=…` | WordPress, which redirects them to the post's address (now a Hugo page) |
| `/wp-admin/`, `/wp-login.php`, `/wp-json/` | WordPress (needed to send newsletters) |
| `/release/`, `/docs/`, `/forms/`, `/wp-content/` (uploads linked from papers) | untouched, served as they are |
| `/?s=word` | redirect to `/search/?q=word` |
| `/feed/`, `/news/feed/`, `/comments/feed/` | redirect to the news feed `/news/index.xml` |
| `/xmlrpc.php` | 410 Gone |
| anything else | the site's 404 page with status 404 (no longer WordPress) |

WordPress is not removed, so the newsletter, its subscriber list and its unsubscribe links keep working.
Going back means taking the new files out again, which `tools/deploy.py rollback` does in seconds.

## Ready

- `tools/deploy.py package` builds the production site at one commit, checks it, and packs it with the
  `.htaccess`, a file list with checksums and the deploy tool itself. It refuses a checkout with uncommitted
  changes.
- `tools/deploy.py plan / deploy / rollback`:
  - `plan` changes nothing. It lists every file of the server it would replace.
  - `deploy` never touches `release/`, `docs/`, `forms/`, `wp-*`, `index.php` or `.well-known/`. It refuses
    when the build would overwrite one of those, or when a file is in the way.
  - It keeps every file it replaces in a state folder outside the web root. It records itself before
    changing anything, so even a deploy cut off halfway can be rolled back.
  - It puts the `.htaccess` in place last.
  - `rollback` puts the old `.htaccess` back first, then restores the web root byte for byte.
- `tools/check_launch.py` fails a build that:
  - is a preview (noindex, the banner, links to the preview)
  - has a robots.txt that shuts search engines out, or a sitemap off www.lead-dbs.org
  - shows TODO text
  - lacks its 404 page, feed or search index

  It also lists the server addresses the site depends on, so they can be checked after the switch.
- The contact and FOCUS forms (`server/forms/`, PR #36) are written but switched off. The page shows
  the email address until the forms are checked on the server.

## Blockers

### Andy (hosting)

1. **Access and method.** Does the package have SSH, and Python 3 on the server? If yes, run
   `deploy.py` there from the unpacked package. If not, use "By hand" below.
2. **The current `.htaccess`.** Any rule outside its `# BEGIN WordPress … # END WordPress` block (for
   `/release/`, PHP versions, old redirects) must be copied into `server/apache/htaccess` before the switch.
3. **Name clashes.** Run `deploy.py plan` against the real web root. It lists every file of the build that
   already exists there (e.g. `favicon.ico`, a `robots.txt`, a search-console proof file), and refuses on a
   clash it can't handle safely.
4. **Server setup.** Confirm that the web root's `.htaccess` is honoured (`AllowOverride`) with `mod_rewrite`
   and `mod_headers`, and that `DirectoryIndex` can be set there.
5. **HTTPS and www.** If STRATO's domain settings already redirect `lead-dbs.org` to `https://www.…`, delete
   those two rules from the `.htaccess`. DNS stays as it is; the mail records aren't touched.
6. **A full backup** of the web root and the WordPress database on the morning of the switch, besides
   `deploy`'s own.

### The lab (Andreas, with Richard)

1. **Privacy policy.** The current page is WordPress's default text about comments, Gravatar, logins and
   cookies the new site doesn't have. `docs/launch/privacy-draft.md` describes what the new site actually
   does. It needs the lab's (and possibly the institution's data-protection office's) review.
2. **Imprint.** It names a private US address. Who is the responsible provider, and is that address meant
   to stay? See the questions in the draft.
3. **Go/no-go.** The date, and who watches the site and the inbox on the first day.

## Should do before or right after the switch

- **A dress rehearsal on STRATO** (Andy). Copy the web root to a test subdomain (e.g. `new.lead-dbs.org`),
  run `plan`, `deploy`, the checks below and `rollback` once there.
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
| Philip | merge #36 and the launch PR, tag the deployed commit (`live-YYYY-MM-DD`), later deploys |
| Richard | content check, go/no-go, the first-day check list, Search Console |
| Andreas (with the institution) | privacy policy and imprint, form recipients |

## Switch day

Before, with the site still on WordPress:

1. `git checkout main && git pull && tools/deploy.py package`. It stops on any problem. Copy
   `dist/lead-dbs-site-<commit>.tar.gz` to the server, **outside** the web root, and unpack it.
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
   `/?s=atlas`, `/?p=1`.
6. `/no-such-page/` shows the site's 404 page, with status 404.
7. Search, the manual, the gallery and a video (click to load) work. The page source has no `noindex`.

## Rollback

    python3 lead-dbs-site-<commit>/deploy.py rollback <webroot> --state <outside>/lead-site-state

The old `.htaccess` goes back first, so WordPress answers again at once. Then every file of the build is
taken out and every file the deploy replaced is restored. Check that `https://www.lead-dbs.org/` shows
WordPress and a download button works. Andy's full backup is the second line of defence.

## By hand (no SSH)

1. Run `plan` on a downloaded copy of the web root (only the file names matter; empty files will do) to
   see what would be replaced. Download those files from the server and keep them.
2. Upload the contents of `site/` *except* `.htaccess` by SFTP.
3. Upload `site/.htaccess` last.

To roll back: upload the old `.htaccess` first, then delete the build's files. `MANIFEST.json` in the
package lists them. `index.html` and the build's top-level folders matter most, because the old rules
serve any file that exists.

## Not checked, because the live server is off limits

- the real web root's contents and `.htaccess`
- the PHP version
- whether `mod_rewrite` and `mod_headers` are allowed
- STRATO's domain and TLS settings
- the newsletter plugin's version and settings
- what changed on WordPress since the import
- which other files on the server are linked from elsewhere
