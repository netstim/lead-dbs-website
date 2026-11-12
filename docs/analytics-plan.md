# Analytics improvement plan

Status: implemented and reviewed by Opus 5.5 (medium reasoning); review fixes validated.
Branch: `improve-analytics`, based on `review-fixes`. Preserve all unrelated
pre-existing edits; do not stage or commit them with analytics work.

## This branch: existing access analytics

1. Refactor the offline importer into parse, aggregate, validate, and atomic
   write operations. Require a cutoff; validate addresses and timestamps;
   report parsed/malformed, after-cutoff, collapsed, and included counts.
   Inject country lookup for dependency-free synthetic tests.
2. Preserve the historical one-address-per-hour access metric, with accurate
   wording. Count tools independently per address/hour/tool, including unknown
   tools in the denominator. Record unknown geography. Do not label these
   counts people, sessions, installations, or bot-filtered activity.
3. Publish schema 2 aggregates only: remove minute/country event pairs and the
   homepage replay. Retain the rotating country-shaded globe. Migrate importer,
   charts, templates, globe, homepage text, and refresh docs together; reject
   incompatible data schemas during the build.
4. Mark boundary periods partial. Represent months without observations as
   null (unknown), not inferred zeros; do not draw across gaps. Keep the hour
   chart but label its timezone as unverified server clock. Handle flat,
   empty, and small chart datasets, including an empty tool denominator.
5. Keep input/database/parser checksums in a private manifest. Publish only
   database name/date, metric version, coverage, and aggregate quality counts.
   Regenerate from local logs using the available local country database;
   describe historical geolocation as an estimate. Do not commit raw logs.
6. Add synthetic parser/aggregation/privacy tests and CI schema checks. Run
   chart edge-case checks and relevant existing Hugo/site checks. Document a
   repeatable local refresh and private-data retention responsibilities.
7. Request a fresh Opus 5.5 medium review of the completed work: scope adherence,
   missing work, defects, and next steps. Resolve concrete findings and rerun
   affected checks before reporting completion.

## Decisions from review

- Downloads are phase 2, after documenting log formats and artifact aliases.
- No speculative crawler exclusions: address ownership and repeat requests do
  not prove a bot. No exclusion framework in this first slice.
- A directory importer suffices; ZIP support is not needed for recurring refresh.
- All-time country totals remain published, including small counts; the headline
  explicitly says requests were recorded from those countries. This is not a
  verified adoption count. No country/month or country/tool cross-tables are
  introduced. A future cross-table requires an explicit small-count policy.
- File hashes belong in private provenance, not the public data artifact.
- Missing months stay unknown, rather than filling them with misleading zeros.

## Later work

Separate download aggregation; a producer audit and event contract for PHP and
MATLAB; optional app telemetry and consent UX; private ingestion scheduling.
Those producers are not present in this static-site repository. This branch
makes no claims to change live collection, deploy a backend, or measure users.

## Acceptance criteria

- Same inputs, rules, lookup and cutoff yield identical aggregates.
- Source rows reconcile with aggregate quality counters; unknowns stay visible.
- Public data has an allowlisted schema and no individual-event replay or IPs.
- Tool counts do not depend on input order or whichever tool appeared first.
- Site labels explain the metric, reporting period, geography and timezone limits.
- Synthetic tests, data validation and relevant website checks pass.
- Analytics work preserves unrelated changes and includes the final review.

## Completion review

Opus confirmed scope adherence and found no blocking issue. Fixed its five
small findings: placeholder documentation, unknown-tool colour, delimited IP
field parsing, stale comments, and manifest/public-output hash matching. Added
chart freshness CI, tool-total reconciliation and quiet CLI tests. Tool colours
also remain stable when preceding categories are absent. Future work remains
outside this branch as listed above.

Validation: 20 synthetic Python tests, chart edge cases, Hugo production/preview
builds, link/copy/design/unused-CSS checks, and targeted Chrome desktop/mobile
checks of usage content and globe pause/play/drag. Raw inputs stayed local;
no deployment or server collection changes were performed.
