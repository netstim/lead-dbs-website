# Whole-system analytics acceptance

The user requested the whole analytics setup, not just the access-reporting
slice. Completion requires evidence for each item below. The coordinating session has
clarified that STRATO access is read-only and live activation is the lab’s call.
This branch must prepare and test the implementation and handoff, never deploy it. A code review cannot
substitute for deployment, a successful scheduled run, or client-release testing.

| Area | Required evidence | Status |
| --- | --- | --- |
| Historical access | Validated aggregate import, honest definitions, tests and CI | Implemented in 32add7a |
| Historical downloads | Versioned inventory, categories, deduplication, diagnostics, public report, approved globe contract | Implemented, locally tested and approved by Opus 5.5 medium at 017791c (2026-11-13) |
| Actual producers | Audit deployed PHP and public MATLAB build call sites and response semantics | Public MATLAB source inspected; live PHP access pending |
| Structured collection | Schema validation, bounded inputs, UTC, explicit event/outcome, privacy-safe identity, no patient/path/free-text collection | PHP implementation and loopback tests pass; lab activation pending |
| Compatibility | Existing download redirects/file delivery unchanged; opted-out clients send no optional analytics | Internal hook and default-off MATLAB helpers prepared; deployed handler audit and MATLAB runtime/release test remain lab dependencies |
| Privacy controls | Private storage, minimal identifiers, retention, opt-in telemetry, offline lookup | Local tests pass; production webserver log and backup retention are unverified |
| Ingestion and reporting | Idempotent ingestion, atomic aggregate report, backup/restore, quality checks | Local PHP-to-Python end-to-end test passes; report is a separate UTC series, not automatically merged into legacy globe |
| Monitoring | Health/freshness checks, successful scheduled run and actionable failure state | Script, failure/age tests and inactive cron example prepared; lab schedule and monitoring activation pending |
| Deployment | Host prerequisites, backup/rollback, live end-to-end smoke tests | Handoff bundle and activation/rollback guide prepared. Server writes prohibited in this session; lab must execute/verify |
| Independent review | Opus 5.5 medium reviews this whole checklist and implementation; findings addressed | Completed 2026-11-13 at 017791c: code and local handoff ready; no code blockers. Production dependencies remain open. |

## Audit evidence

- The current public `netstim/leaddbs` file `ea_firstrun_public.m` (blob
  `e90ed0939f5248d687caa3b224ce5d6af4d433c6`) calls
  `/release/stats.php?id=<tool>&ver=<MATLAB release>` before its first-run
  preferences guard. A failed webread triggers a urlread retry; there is no
  event id, explicit opt-in gate, app version or installation id in this call.
- The local `ea_firstrun.m` has that tracking block commented out. Coverage
  depends on build packaging; do not describe logs as all installations.
- `ea_update.m` uses `download.php` for full and incremental updates and also
  probes `updates_data` using a response-code request. Historical download
  log entries cannot establish completed downloads or a human action.
- The website is a static Hugo deployment; it cannot run PHP collectors itself.
  Existing server paths must remain reachable when the new site is deployed. No
  server writes, probes that create events, or scheduled remote jobs are authorized.
- STRATO SFTP host/account are known, but a fresh credential prompt timed out.
  Shell access was previously unavailable. No live changes have been made.

## Boundaries

No speculative cloud-provider/country blocking. Network location is not a
person's location. No historical unique-user or installation estimate. No
rewriting app builds or activating new user telemetry without an opt-in path.
Any unavailable credential, hosting feature or release-test environment remains
an explicit open dependency; it is not marked complete by narrowing the scope.

## Local evidence (2026-11-13)

- 46 Python tests pass, including loopback HTTP collection and an actual local
  PHP export → Python archive/report → retention run, repeated idempotently.
- PHP collector tests cover validation, opt-in, event retry, independent tool
  deduplication, response outcomes, declared automation, rates, daily token
  rotation, private file permissions and retention.
- Direct hook/HTTP tests use locked MaxMind reader 1.14.0 with its upstream
  offline fixture. Invalid versions, aliases, HEAD/DNT/GPC and missing inventory
  are covered. A failed real export still deletes expired rows.
- A freshly unpacked handoff installs locked dependencies and passes the PHP
  checks and all 16 bundled Python tests. Backups use atomic replacement;
  private output paths are enforced.
- The globe retains exactly 39,403 requests, identical monthly totals and
  country counts to #24; only equal-count country ordering is deterministic.
  Homepage wording describes recorded requests rather than completed transfers;
  the user approved preserving #24’s selection and using “download requests”.
- Desktop/mobile browser checks preserve monthly progression, pause/play/drag,
  all-country anchor opening and the added download tables without overflow.
- This branch does not claim the whole production analytics setup is finished.
  The coordinating session explicitly reserves deployment for the lab. A full
  production completion verdict requires their activation and client-release
  evidence; independent code review must not waive those dependencies.

## Independent review outcome (2026-11-13)

Opus 5.5 medium reviewed commit `017791c829472980d164a4158815d53aed80021b`
and independently reran the Python, PHP, chart, Hugo and site checks. Two
handoff bundle builds were byte-identical; a fresh unpack installed the locked
dependencies and passed all 16 included Python tests plus the PHP tests, with
none skipped. Verdict: code and local handoff ready, with no remaining code
blockers. This document update records that verdict; it does not certify live
activation.

Optional follow-ups from the review: decouple retention from GeoIP database
loading; reject operational output paths that collide with internal state files;
expose hourly retention failures independently of daily status. These are
hardening opportunities, not prerequisites for this reviewed handoff. The lab
must still verify every pending production item in the table above.
