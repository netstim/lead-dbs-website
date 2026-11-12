# Access analytics

The website publishes recorded **access requests**, one per network address per
recorded clock hour. This metric is retained for continuity with earlier site
statistics. It is not a count of users, installations, sessions, completed
workflows, or clinical activity. The source logging calls are outside this repo;
verify them before describing a request as an application launch.

## Definitions and limitations

- Overall counts deduplicate `(canonical IP, calendar day, clock hour)`, across
  both `access.log.bak` and `access.log`. IPv6 alternate spellings normalize to
  the same address. IPv4-mapped IPv6 addresses remain distinct from bare IPv4
  addresses; rotating IPv6 privacy addresses also remain distinct. Backup overlap is included in the collapsed-row counter.
- Tool counts independently deduplicate `(IP, day, hour, tool)`. Tool values are
  allowlisted; everything else is `Other / unknown`. This category collapses
  unrecognized labels together. Tool totals and hourly charts cover the cutoff
  year to date; country totals cover the full reporting interval.
- Shared institutional addresses merge people; changing addresses split them.
  Deduplication is not bot detection. No bots are automatically excluded.
- Timestamp timezone is **unverified server clock**. Hourly charts do not claim
  UTC or Central European Time. Repeated DST clock hours are indistinguishable.
- Country lookup is offline using the named database build. Historical network
  assignments may differ. Unknown geography stays in overall totals and is
  reported separately. Codes not recognized by the country-name lookup (for
  example, `XK`) also count as unknown. Unknown geography is excluded from country tiles and country counts.
- First/last observed month and year are labelled partial when their date
  boundaries are incomplete. Missing months have `null` counts: no observations,
  not verified zero usage. No chart line bridges them. Even full calendar
  boundaries cannot establish uninterrupted logging. The previous-calendar-year
  headline is a recorded count, not an assertion of complete collection.
- All-time country totals include small counts. They indicate observed network
  locations, not verified adoption in that country. There are no country/time or
  country/tool cross-tables. Adding them requires a documented small-count policy.

## Public contract (schema 2)

`data/usage.json` contains only allowlisted aggregate fields. `rules` names the
counting method; `from` is the earliest included record date; `to` is the explicit
inclusive cutoff; `observed_to` is the latest valid date in the input. Database
name/date record the geography vintage. `quality` contains:

- `rows = parsed + malformed`
- `parsed = after_cutoff + collapsed + included`
- `included = total = sum(years) = sum(observed months)`
- `included = sum(country totals) + unknown_country`
- `tool_requests = sum(tools)` (cutoff year only; a different denominator)

There are no individual events, address identifiers, exact timestamps, network
names, source paths, or source fingerprints in the public artifact. The old
`launches` and `day` replay fields were removed. Source/database/parser checksums
and dependency versions live in a separate **private** run manifest. Its
`public_sha256` identifies the exact intended public JSON bytes. A manifest is
not proof that publication succeeded: if the public write fails, compare that
hash with the existing artifact before treating them as a matching pair.

## Refresh locally

Use a private copy of the logs and a locally obtained MaxMind-format country
database. Python 3.11+ is required. Do not put raw logs or the manifest in this
repository, public build directory, CI artifacts, or third-party analytics.
The script has no network calls. Initial dependency installation is separate.

```sh
python3 -m venv /tmp/ldbs-analytics-env
/tmp/ldbs-analytics-env/bin/pip install maxminddb==3.2.0 pycountry==26.2.16
/tmp/ldbs-analytics-env/bin/python tools/usage.py /private/path/to/logs /private/path/to/country.mmdb --cutoff YYYY-MM-DD --manifest /private/path/to/access-run-manifest.json
npm install --no-save pele@1.13.0
node scripts/usage.mjs
python3 -m unittest discover -s tests -v
node tests/test_usage_charts.mjs
hugo --gc --minify
```

Choose a cutoff known to precede completion of log export (usually the preceding
calendar day). A latest timestamp is not proof the source is complete. At least
one access log is required; the private manifest lists which files were used.
Review that both files are present when both are expected. The CLI refuses an
empty valid dataset or a cutoff later than the latest valid source record.

Public output is written atomically after validation, and sources are checked
for modification during the run. Failed runs preserve the previous JSON. Charts
must then be regenerated from the successful output before publishing. Review
changes to quality counters, gaps, geography coverage and unusual volume before
merging; the assigned maintainer owns this review and the refresh schedule.

CI uses synthetic fixtures and the public artifact only. It validates the data
contract and reconciliations without a country database. Chart tests cover no
data, one point, flat values and gaps. Automated live ingestion is not configured.

## Retention and follow-up

Keep access to raw logs restricted. The operator must choose and enforce a short
retention period for raw logs and their backups, and remove private processing
copies after validation according to that policy. `/tmp` is not a deletion
policy. This importer does not delete source files or the user's archive and does
not alter server retention. The private manifest contains source fingerprints;
retain it only in the restricted operational area under the same policy.

Phase 2 is separately defined download-request aggregation, after inventorying
artifact aliases and verifying the handler's semantics. Collection changes need
the PHP/MATLAB producer sources. Optional installation telemetry, consent UX,
retention enforcement and ingestion scheduling are not implemented by this
static-site branch. See [analytics-plan.md](analytics-plan.md).
