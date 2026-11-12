"""Offline access-log aggregation. See docs/analytics.md for refresh instructions.

Only the CLI needs maxminddb and pycountry. Importing/testing this module is stdlib-only.
"""
import argparse
import collections
import datetime as dt
import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import tempfile

SCHEMA = 2
RULES = 'access-address-hour-v2'
TOOLS = {'dbs': 'Lead-DBS', 'group': 'Lead Group', 'connectome': 'Lead Connectome', 'anatomy': 'Lead Anatomy'}
LINE = re.compile(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}), (?:.*?,\s*)?IP:\s*([^,\s]+),?\s*(.*)$')
PUBLIC_KEYS = {'schema', 'rules', 'metric', 'timezone', 'from', 'to', 'observed_to', 'country_database',
               'year', 'requests_year', 'total', 'countries', 'years', 'months', 'partial_years',
               'partial_months', 'hours_year', 'hours', 'tools', 'quality'}
QUALITY_KEYS = {'rows', 'parsed', 'malformed', 'after_cutoff', 'collapsed', 'included',
                'unknown_country', 'tool_requests', 'unknown_tool_requests'}


def parse(line):
    """Return timestamp, canonical address, known tool (or Other); never echo input."""
    m = LINE.fullmatch(line.strip())
    if not m:
        return None
    try:
        when = dt.datetime.strptime(m[1], '%Y-%m-%d %H:%M:%S')
        address = str(ipaddress.ip_address(m[2]))
    except ValueError:
        return None
    tool = m[3].split(',')[0].strip()
    return when, address, TOOLS.get(tool, 'Other / unknown')


def month_range(start, end):
    month = start.replace(day=1)
    while month <= end:
        yield month.strftime('%Y-%m')
        month = (month.replace(day=28) + dt.timedelta(days=4)).replace(day=1)


def aggregate(lines, lookup, cutoff, database):
    """Count address/hours and separately address/hour/tools. No row-level output."""
    cutoff = dt.date.fromisoformat(cutoff)
    q = dict.fromkeys(sorted(QUALITY_KEYS), 0)
    seen, tool_seen = set(), set()
    first = last = observed = None
    for line in lines:
        q['rows'] += 1
        row = parse(line)
        if row is None:
            q['malformed'] += 1
            continue
        q['parsed'] += 1
        when, address, tool = row
        day = when.date()
        observed = max(observed, day) if observed else day
        if day > cutoff:
            q['after_cutoff'] += 1
            continue
        first = min(first, day) if first else day
        last = max(last, day) if last else day
        key = (address, day.isoformat(), when.hour)
        if key in seen:
            q['collapsed'] += 1
        seen.add(key)
        tool_seen.add((*key, tool))
    if not seen:
        raise ValueError('No valid access records on or before the cutoff; output unchanged.')
    if cutoff > observed:
        raise ValueError('Cutoff exceeds the latest valid source date; output unchanged.')
    years, months, countries, hours, tools = (collections.Counter() for _ in range(5))
    names, cache = {}, {}
    for address, day, hour in sorted(seen):
        years[day[:4]] += 1
        months[day[:7]] += 1
        if day[:4] == str(cutoff.year):
            hours[hour] += 1
        if address not in cache:
            cache[address] = lookup(address)
        country = cache[address]
        if country:
            code, name = country
            countries[code] += 1
            names[code] = name
        else:
            q['unknown_country'] += 1
    for address, day, hour, tool in sorted(tool_seen):
        if day[:4] == str(cutoff.year):
            tools[tool] += 1
    q['included'] = len(seen)
    q['tool_requests'] = sum(tools.values())
    q['unknown_tool_requests'] = tools['Other / unknown']
    # Null means no recorded observations, not verified zero usage.
    month_rows = [[m, months.get(m)] for m in month_range(first, cutoff)]
    partial_months = set()
    if first.day != 1:
        partial_months.add(first.strftime('%Y-%m'))
    if (last + dt.timedelta(days=1)).day != 1:
        partial_months.add(last.strftime('%Y-%m'))
    partial_years = set()
    if (first.month, first.day) != (1, 1):
        partial_years.add(str(first.year))
    if (last.month, last.day) != (12, 31):
        partial_years.add(str(last.year))
    out = {
        'schema': SCHEMA, 'rules': RULES, 'metric': 'access_requests_per_address_hour',
        'timezone': 'unverified_server_clock', 'from': first.isoformat(),
        'to': cutoff.isoformat(), 'observed_to': observed.isoformat(),
        'country_database': dict(database), 'year': str(cutoff.year - 1),
        'requests_year': years[str(cutoff.year - 1)], 'total': len(seen),
        'countries': [[c, names[c], n] for c, n in sorted(countries.items(), key=lambda kv: (-kv[1], kv[0]))],
        'years': dict(sorted(years.items())), 'months': month_rows,
        'partial_years': sorted(partial_years), 'partial_months': sorted(partial_months),
        'hours_year': str(cutoff.year), 'hours': [hours[h] for h in range(24)],
        'tools': dict(sorted(tools.items())), 'quality': q,
    }
    validate(out)
    return out


def validate(data):
    """Validate the public contract and reconcile independent totals."""
    def require(ok, message):
        if not ok:
            raise ValueError(message)
    require(set(data) == PUBLIC_KEYS and data['schema'] == SCHEMA, 'Unexpected public schema.')
    require(data['rules'] == RULES and data['metric'] == 'access_requests_per_address_hour', 'Unexpected metric.')
    require(data['timezone'] == 'unverified_server_clock', 'Unexpected timezone.')
    for key in ('from', 'to', 'observed_to'):
        dt.date.fromisoformat(data[key])
    require(data['from'] <= data['to'] <= data['observed_to'], 'Invalid coverage dates.')
    require(set(data['country_database']) == {'name', 'date'}, 'Unexpected database metadata.')
    dt.date.fromisoformat(data['country_database']['date'])
    require(set(data['quality']) == QUALITY_KEYS, 'Unexpected quality fields.')
    def count(n):
        return type(n) is int and n >= 0
    q = data['quality']
    require(all(count(n) for n in q.values()), 'Invalid quality count.')
    require(q['rows'] == q['parsed'] + q['malformed'], 'Row reconciliation failed.')
    require(q['parsed'] == q['after_cutoff'] + q['collapsed'] + q['included'], 'Dedup reconciliation failed.')
    require(count(data['total']) and data['total'] == q['included'], 'Total mismatch.')
    require(all(re.fullmatch(r'\d{4}', y) and count(n) for y, n in data['years'].items()), 'Invalid year series.')
    require(sum(data['years'].values()) == data['total'], 'Year reconciliation failed.')
    require(data['year'] == str(int(data['to'][:4]) - 1), 'Invalid summary year.')
    require(data['requests_year'] == data['years'].get(data['year'], 0), 'Summary mismatch.')
    require(data['hours_year'] == data['to'][:4], 'Invalid hours year.')
    require(len(data['hours']) == 24 and all(count(n) for n in data['hours']), 'Invalid hours.')
    require(sum(data['hours']) == data['years'].get(data['hours_year'], 0), 'Hour reconciliation failed.')
    require(set(data['tools']) <= set(TOOLS.values()) | {'Other / unknown'}, 'Unexpected tool label.')
    require(all(count(n) for n in data['tools'].values()) and sum(data['tools'].values()) == q['tool_requests'], 'Tool reconciliation failed.')
    require(q['tool_requests'] >= sum(data['hours']), 'Tool requests cannot be fewer than address-hour requests.')
    require(data['tools'].get('Other / unknown', 0) == q['unknown_tool_requests'], 'Unknown tools mismatch.')
    codes = set()
    for row in data['countries']:
        require(isinstance(row, list) and len(row) == 3, 'Invalid country row.')
        code, name, n = row
        require(isinstance(code, str) and re.fullmatch(r'\d{3}', code) and code not in codes, 'Invalid country code.')
        require(isinstance(name, str) and 0 < len(name) < 100 and count(n) and n > 0, 'Invalid country aggregate.')
        codes.add(code)
    require(sum(r[2] for r in data['countries']) + q['unknown_country'] == data['total'], 'Country reconciliation failed.')
    expected = list(month_range(dt.date.fromisoformat(data['from']), dt.date.fromisoformat(data['to'])))
    require([r[0] for r in data['months']] == expected, 'Month sequence mismatch.')
    require(all(n is None or count(n) for _, n in data['months']), 'Invalid month count.')
    require(sum(n or 0 for _, n in data['months']) == data['total'], 'Month reconciliation failed.')
    require(set(data['partial_months']) <= set(expected), 'Invalid partial months.')
    require(set(data['partial_years']) <= set(data['years']), 'Invalid partial years.')
    def inspect(value):
        if isinstance(value, str):
            try:
                ipaddress.ip_address(value)
            except ValueError:
                return
            raise ValueError('Address found in public data.')
        if isinstance(value, dict):
            for k, v in value.items():
                inspect(k)
                inspect(v)
        if isinstance(value, list):
            for v in value:
                inspect(v)
    inspect(data)


def public_bytes(data):
    return (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')


def write_atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, delete=False) as fh:
            tmp = fh.name
            fh.write(public_bytes(data))
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        if tmp and os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('logdir', type=Path)
    parser.add_argument('database', type=Path)
    parser.add_argument('--cutoff', required=True, help='Inclusive YYYY-MM-DD in the recorded server clock')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'data/usage.json')
    parser.add_argument('--manifest', type=Path, required=True, help='Private run manifest outside the repository')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    if args.manifest.resolve().is_relative_to(root):
        parser.error('The private manifest must be outside the repository.')
    if args.manifest.resolve() == args.output.resolve():
        parser.error('Manifest and public output must be separate.')
    sources = [args.logdir / n for n in ('access.log.bak', 'access.log') if (args.logdir / n).is_file()]
    if not sources:
        parser.error('No access logs found.')
    protected = {p.resolve() for p in [*sources, args.database]}
    if args.output.resolve() in protected or args.manifest.resolve() in protected:
        parser.error('Output cannot overwrite an input.')
    import maxminddb
    import pycountry
    def digest(path):
        with path.open('rb') as fh:
            return hashlib.file_digest(fh, 'sha256').hexdigest()
    # Private provenance only; do not publish fingerprints of personal-data sources.
    before = {p.name: digest(p) for p in sources}
    db_hash = digest(args.database)
    with maxminddb.open_database(str(args.database)) as reader:
        metadata = reader.metadata()
        database = {'name': metadata.database_type, 'date': dt.datetime.fromtimestamp(metadata.build_epoch, dt.timezone.utc).date().isoformat()}
        def lookup(address):
            rec = reader.get(address) or {}
            code = rec.get('country', {}).get('iso_code')
            country = pycountry.countries.get(alpha_2=code) if code else None
            return (country.numeric, getattr(country, 'common_name', None) or country.name) if country else None
        def lines():
            for path in sources:
                with path.open(encoding='utf-8', errors='replace') as fh:
                    yield from fh
        data = aggregate(lines(), lookup, args.cutoff, database)
    if before != {p.name: digest(p) for p in sources} or db_hash != digest(args.database):
        raise ValueError('Inputs changed during aggregation; output unchanged.')
    manifest = {'schema': SCHEMA, 'rules': RULES, 'sources_sha256': before, 'database_sha256': db_hash,
                'public_sha256': hashlib.sha256(public_bytes(data)).hexdigest(),
                'parser_sha256': digest(Path(__file__)), 'cutoff': args.cutoff, 'quality': data['quality'],
                'dependencies': {'maxminddb': __import__('importlib.metadata', fromlist=['version']).version('maxminddb'),
                                 'pycountry': __import__('importlib.metadata', fromlist=['version']).version('pycountry')}}
    # The manifest identifies the intended bytes, not a successful publication.
    # If output replacement fails, its hash will not match the previous artifact.
    write_atomic(args.manifest, manifest)
    write_atomic(args.output, data)
    print(f"Published {data['total']:,} address-hour access requests through {args.cutoff}; {data['quality']['malformed']} malformed rows.")


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as exc:
        # Do not echo raw parser/database errors or sensitive paths.
        raise SystemExit('Aggregation failed; check inputs, cutoff, and output permissions. Public data was not refreshed.') from None
