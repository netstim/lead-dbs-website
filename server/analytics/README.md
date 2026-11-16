# Collector package — lab activation required

This code has not been deployed to STRATO. Access for this task is read-only.
The lab owns server changes, retention policy, operational monitoring and client
release decisions. A successful local test is not proof of production activation.

From the website source checkout, build a reproducible source handoff with
`python3 tools/package_analytics.py --output /private/lead-analytics-handoff.tar.gz`.
The bundle includes the exact artifact inventory, Composer lock and MATLAB
helpers; it contains no logs, keys, private config or country database. Unpack
under `/srv/lead-analytics` on the lab-selected staging host (or adjust all
example paths together). The bundle contains its PHP and Python tests and the
offline MaxMind fixture. Install dependencies in `collector/`.

## Requirements and private configuration

PHP 8.2+, PDO SQLite with SQLite 3.35+ (RETURNING support), a secure writable
filesystem, PHP CLI for maintenance, an offline country MMDB and a private
32-byte random HMAC key. Collection needs all of these; maintenance (`health`,
`retain`, `export`) needs only PHP and the private database. Install locked
dependencies with:

```sh
composer install --no-dev --no-plugins --no-scripts --prefer-dist
```

Set `LEAD_ANALYTICS_CONFIG` to a private JSON file shaped like
`collector/config.example.json` from the bundle root. The operations example
uses `/private/lead-analytics/collector-config.json`; copy the operations config
to `/private/lead-analytics/operations.json`. Its file, DB, key and country database must all be outside
the HTTP document root; bootstrap refuses public storage. Collection refuses
unknown settings; maintenance validates only the database path (and, for
`health`, the two storage limits), so a broken key, country database or vendor
folder disables collection without stopping retention. Restrict the private
directory to its service account. Generate the key locally on that host; do not
place it in source control, an HTTP-readable file or a shared chat. Do not trust
forwarded-IP headers: the collector uses `REMOTE_ADDR` only. A reverse-proxy
installation needs an explicit, reviewed trusted-proxy configuration.

The `.htaccess` file allows only collect.php through HTTP and disables directory
listings, but Apache must be configured to honor it. Nginx needs an equivalent
rule. The only public route should be collect.php; keep code/config/vendor and
maintenance files otherwise private. Verify that a non-PHP static sentinel in
the private storage cannot be fetched before activation. Do not rely on a file
extension to protect the SQLite database.

## Resource limits

These optional positive-integer settings bound what analytics can take from the
shared host; the values in `config.example.json` are the defaults:

| Setting | Default | Effect |
| --- | --- | --- |
| `max_database_bytes` | 268435456 (256 MiB) | Shed collection once the database with its journal or WAL file reaches this size |
| `min_free_bytes` | 536870912 (512 MiB) | Shed collection while the database folder has less free space |
| `collect_busy_timeout_ms` | 1000 | How long `collect.php` waits for the SQLite write lock |
| `hook_busy_timeout_ms` | 200 | How long the download hook waits for it, so a busy database barely delays a download |

Both ceilings are checked with `stat` and `disk_free_space` before the country
lookup and before any SQLite lock. `disk_free_space` reports free space on the
filesystem, not a hosting quota: set `max_database_bytes` below the package's
quota. Where PHP cannot report free space (for example, the function is
disabled), collection sheds and `check` fails, so find this out on staging.
Each stored event takes up to about 430 bytes with its rate bucket and index, so
the default ceiling holds roughly 600,000 events: about 20,000 a day over the
31-day retention. Measure real volume on staging and adjust. A new database
uses SQLite incremental auto-vacuum, and each retention run returns the pages it
freed to the filesystem, so intake resumes once retention brings the size back
under the ceiling. Maintenance waits up to 3 s for the write lock.

## Routes and schema

`collect.php`: POST JSON, at most 4096 bytes. Schema 1 requires a UUID-v4
`event_id`, `kind: access`, allowlisted `item`, `outcome: request`, and
`consent: true`. Optional app and runtime versions use bounded version syntax.
Unknown fields are rejected. No client timestamp or persistent installation ID
is accepted. The server supplies UTC day/hour. DNT and GPC requests are ignored.
No CORS access is enabled. It returns 204 for accepted or duplicate events, 400
for invalid payloads, 413/415 for size/type, 429 with `Retry-After: 60` for
rate limiting, 503 with `Retry-After: 3600` at the storage ceiling, and 503
without `Retry-After` for service failure. IDs are caller-generated and cannot
establish human identity.

Each address may make 60 requests per UTC minute. Once it has, further requests
in that minute are rejected after a plain read of the rate bucket: no country
lookup, no write lock and no write. A request turned away at the storage
ceiling is not written either. Neither is counted in the `metrics` table
(`received` counts only requests that reached the write transaction); the web
server's access log shows those 429 and 503 responses. Requests that pass the
read concurrently are recounted under the write lock, so the limit still holds.

The stored subject is HMAC(key, UTC day + packed IP). It rotates by day and
supports hourly/daily deduplication, but is pseudonymous data, not anonymous.
Raw IPs and user agents are not stored by this collector. Webserver/access/error
logs are a separate retention surface that the lab must configure and verify.
A user-agent bot declaration is a diagnostic, not verified crawler identity.

`download-hook.php`: internal function only. Call
`lead_analytics_download($artifact, $outcome, $version)` after the existing
handler has determined its response. Outcomes are request, redirect,
file_response, not_found. HEAD probes are ignored. It returns false when
analytics fails, including at the storage ceiling and when the database stays
locked beyond `hook_busy_timeout_ms`; the handler must deliver the download
either way. A file_response does **not** prove the recipient completed a download. The live handler has not been read
or patched; audit its actual branches before integrating this hook. Copy the
versioned `analytics/artifacts.json` inventory beside this hook before activation (already included beside the hook in the bundle). Invalid
version strings become `unknown`, preserving the event.

Old clients using stats.php do not explicitly opt in. The lab must decide how
to retire the old collector; do not silently treat old requests as new consented
telemetry. The prepared MATLAB helpers replace the legacy call and default off.

## Maintenance and verification

`maintenance.php` is CLI-only and supports health, export YYYY-MM-DD, and retain.
It opens only the private database: no Composer dependencies, HMAC key or
country database. `health` reports the last event day, retained event count,
`last_retention_at`, daily counters and, under `storage`, `database_bytes`,
`free_bytes`, `max_database_bytes` and `min_free_bytes`. Exports contain daily aggregates only; they are private
operational inputs, not the public website artifact. Run `tools/analytics_ops.py`
with the example private operations config. It locks against concurrent runs,
exports closed UTC days, attempts retention even if export fails, then upserts
aggregate snapshots idempotently, backs up the aggregate archive and writes a
minimized report atomically.

The report (`output`) must be a file directly inside `<private_dir>/reports/`,
which the job creates with mode 0700. Neither `reports/` nor the report may be
a symlink, and the report may not resolve to the job's own files
(`status.json`, `run.lock`, `aggregate-archive.sqlite` and its `-journal`,
`-wal` and `-shm` files, anything under `backups/`), the operations or collector
config, or the database, key or country database the collector config names.
All of this is checked before any collector command runs or any file changes.

Retention deletes event-state days older than 31 days, rate-limit bucket days
older than 2 days, and health-counter days older than 90 days. Boundaries use
UTC dates, not an exact elapsed-hour lifetime. Each successful run stores its
UTC completion time in the database in the same transaction, and `health`
reports it as `last_retention_at`; a failed run (for example, a locked or
read-only database) exits nonzero and records nothing. Install the
**independent hourly PHP-only retain job** from `crontab.example` as well: it
does not depend on Python, export, backup, the key, the country database or the
vendor folder. Retention cannot run when no job is installed or the host is
down. Verify the schedule and failure monitoring before enabling collection or
releasing the consent UI.

The job keeps seven aggregate-only backups and never backs up pseudonymous
collector rows. Restore an aggregate backup by stopping the job and replacing
aggregate-archive.sqlite with the selected backup, then rerun (idempotent).

Exports and reports name the deduplicated response-request series
`download_requests`: only `redirect` and `file_response`, excluding user agents
that declare automation. `request` and `not_found` do not enter this series.
The export separately preserves raw outcome/traffic counts for diagnostics;
these counts are not deduplicated and need not sum to the response series.
Even a file response is not evidence of a completed transfer or a human user.

Run the check command hourly, after the retain job (see `crontab.example`). It
reads the daily status file and runs `maintenance.php health`, and exits
nonzero, naming each problem, when:

- the last daily run failed or is older than 30 hours;
- the last observed event is older than two days (an alert, not a claim that no users exist);
- health is unavailable, or the last retention completed more than 2 hours ago
  (one late or failed hourly run is tolerated; the second raises the alert);
- the database is at or above 90% of `max_database_bytes`, or free space is
  below `min_free_bytes` or unknown (collection is then shedding).

Route the exit code into the lab's existing monitoring; no emails or Slack
messages are sent by this package. Rotate the maintenance and retention logs
separately (they contain fixed status messages only).

Do not mix UTC structured counts into legacy server-clock figures without an
explicit cutover date and non-overlap check. The operations output is a separate
series for review, not an automatic replacement of the approved historical globe.

## Lab activation and rollback checklist

1. Audit actual download.php/stats.php source, deployment version, timezone,
   redirect/file-delivery branches, current logging and backup retention.
2. Verify host supports PHP/SQLite, a private directory, CLI scheduling and log
   controls. Existing SFTP access does not establish these capabilities.
3. Back up the existing handler code (restricted access); install the collector
   in staging. Verify denied private paths, synthetic requests, export, restore,
   rate limiting, malformed bodies, failure isolation and retention.
4. Integrate the download hook without altering redirects or file delivery. Gate
   the new opt-in client endpoint behind the approved app release. Record a
   cutover date and inspect two closed-day reports before publication.
5. Before enabling collection, install the independent retention job and the
   export/check jobs after successful manual runs. Assign an owner and verify
   real scheduled runs and deliberately failed-run alerts, including retention.
6. Roll back by restoring the handlers and disabling collection/export. Keep
   the retention job running until all pseudonymous state has expired; then
   remove the unused private event DB/key and stop that job. Keep consented
   clients non-blocking if the endpoint disappears. Do not restore expired
   pseudonymous backups or resurrect previously deleted data.

From the unpacked bundle root, run `php tests/php/collector.php` (PHP with
PDO SQLite only) and, after Composer install,
`python3 -m unittest discover -s tests -v` (including loopback HTTP tests and
the maintenance command with a missing key, country database and vendor folder). No test
contacts STRATO or sends the real logs to any external service.

Python 3.10+ is required for the operations job and its tests; they use only the
standard library. `tools/requirements.txt` supplies the hash-pinned packages for
legacy offline GeoIP import, if needed; they are not required by operations.
Do not publish the bundle or its operational output as the website document root.
