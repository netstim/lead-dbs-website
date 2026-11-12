# Historical download analytics and the approved globe

The homepage retains PR #24's month-by-month program-download globe and all
countries, without a minimum. Its data contract remains `countries` (numeric
country code/name/total rows), `months` (month and country-count dictionary),
`total`, `from`, `to`. Missing calendar months are explicit empty dictionaries,
so the animation does not compress a gap in source observations. A missing
month is not proof of zero usage. The first/last month can be partial.

`tools/downloads.py` extends the same importer; there is no second download
pipeline. It now validates timestamps/addresses, canonicalizes IPv6, requires a
cutoff, produces deterministic output and private checksummed provenance, and
reconciles parsed/malformed/after-cutoff/collapsed/included records.

## Two explicitly different series

1. **Globe/country-table series:** program requests plus hotfix, deduplicated by
   address, exact artifact alias and day, with the legacy #24 heuristics retained.
   Hosting/crawler-range heuristics and addresses with more than 50 selected
   requests across the entire interval are excluded. This is NOT a verified
   human count. It can omit legitimate cloud researchers and long-term users,
   and miss automation. Unknown geography is excluded from the map. Each
   exclusion count is published in `selection`; it reconciles with candidates.
2. **All-request series:** `all_requests` contains all categories before these
   exclusions, with unknown geography included in totals. `/usage/` shows yearly
   program, updates, other artifacts and total counts. Repeated raw records
   within an address/artifact/day group are counted as a quality diagnostic.
   A group with at least 100 raw rows is flagged, not silently removed. Backup
   overlap also contributes to raw repetition, so it is not proof of automation.

The globe preserves #24's selection exactly: latest, hotfix, lead, lead_dropbox,
lead_pcloud and names containing `standalone`. The broader all-request inventory
is separate and does not silently replace that historical metric. Its category
mapping is explicit, so an unlisted standalone name appears as unknown in that
breakdown even when the legacy globe selection includes it. IPv4-mapped IPv6
addresses receive the same network heuristic as their IPv4 form.

`analytics/artifacts.json` versions the category mapping and records source
evidence. Source `ea_checkinstall.m` identifies group2013, group2016, group2017
and PPMI variants as connectomes, fliplr as a transform/data resource, and
macroscalehc as an atlas. Unknown aliases are not guessed. Moving aliases such
as latest cannot recover the exact historical software version.

## Refresh

Use the same private source folder, country database and cutoff as access import:

```sh
python3 -m pip install --require-hashes -r tools/requirements.txt
python3 tools/downloads.py /private/logs /private/country.mmdb --cutoff YYYY-MM-DD --manifest /private/download-run-manifest.json
python3 -m unittest discover -s tests -v
```

The manifest is private and identifies source/parser/registry/database checksums
and exact intended output bytes. No real address or exclusion-list membership
is published. Inspect registry unknowns and changes to exclusion totals before
publishing. Geolocation uses the named contemporary offline database and may
misplace old addresses. Logs record requests, including update/probe activity;
without the actual handler code they cannot prove response or transfer success.

New UTC collector data remains a separate operational series until the lab
establishes a non-overlapping cutover and verifies the live producer integration.
Do not simply add it to historical counts or replace the approved globe shape.
