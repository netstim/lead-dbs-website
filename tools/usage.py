"""Usage figures for the site, from the launch log of lead-dbs.org: data/usage.json.

    python3 tools/usage.py <log directory> <country database .mmdb> [last day, YYYY-MM-DD]

The log directory holds access.log (and access.log.bak): one line per start of Lead-DBS, with the time,
the IP address, the tool started and the MATLAB release. The country database is a free IP-to-country
file in MaxMind format (for example DB-IP "IP to Country Lite"); the lookup runs on this computer.
Needs: pip install maxminddb pycountry.

What is counted: a launch is one start of Lead-DBS; the same address counts once an hour, so a script
that restarts Lead-DBS in a loop does not weigh more than a person. What leaves this script: totals by
country, year, month, hour and tool, and for the last full day of the log the time (to the minute) and
country of each launch. No IP address, city or network name is written.

Afterwards: node scripts/usage.mjs (redraws the charts of /usage/ from data/usage.json).
"""
import collections
import datetime
import json
import os
import re
import sys

import maxminddb
import pycountry

LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}) (\d\d):(\d\d):\d\d, .*?IP: ([0-9a-fA-F:.]+),?\s*([^,]*)')
TOOLS = {'dbs': 'Lead-DBS', 'group': 'Lead Group', 'connectome': 'Lead Connectome', 'anatomy': 'Lead Anatomy'}


def main(logdir, db, last=None):
    reader = maxminddb.open_database(db)
    cache = {}

    def country(ip):
        if ip not in cache:
            rec = reader.get(ip)
            code = rec['country']['iso_code'] if rec and 'country' in rec else None
            c = pycountry.countries.get(alpha_2=code) if code else None
            cache[ip] = (c.numeric, getattr(c, 'common_name', None) or c.name) if c else (None, None)
        return cache[ip]

    rows = []
    seen = set()
    for name in ('access.log.bak', 'access.log'):
        path = os.path.join(logdir, name)
        if not os.path.exists(path):
            continue
        with open(path, errors='replace') as fh:
            for line in fh:
                m = LINE.match(line)
                if not m:
                    continue
                day, hh, mm, ip, tool = m.groups()
                if (ip, day, hh) in seen:
                    continue
                seen.add((ip, day, hh))
                rows.append((day, int(hh), int(mm), ip, tool.strip()))
    if not rows:
        sys.exit('no launches found in ' + logdir)

    # the last full day of the log, unless one is named
    last = last or (datetime.date.fromisoformat(max(r[0] for r in rows)) - datetime.timedelta(days=1)).isoformat()
    rows = [r for r in rows if r[0] <= last]
    this_year = last[:4]
    full_year = str(int(this_year) - 1)

    years = collections.Counter()
    months = collections.Counter()
    by_country = collections.Counter()
    names = {}
    hours = collections.Counter()
    tools = collections.Counter()
    launches = []
    for day, hh, mm, ip, tool in rows:
        years[day[:4]] += 1
        months[day[:7]] += 1
        num, cname = country(ip)
        if num:
            by_country[num] += 1
            names[num] = cname
        if day[:4] == this_year:
            hours[hh] += 1
            if tool in TOOLS:
                tools[TOOLS[tool]] += 1
        if day == last and num:
            launches.append([hh * 60 + mm, num])
    launches.sort()

    # months: complete ones only
    end = datetime.date.fromisoformat(last)
    complete = (end + datetime.timedelta(days=1)).day == 1
    month_rows = [[k, v] for k, v in sorted(months.items()) if k < last[:7] or complete]

    out = {
        'to': last,
        'year': full_year,
        'launches_year': years[full_year],
        'total': sum(years.values()),
        'countries': [[k, names[k], v] for k, v in by_country.most_common()],
        'years': dict(sorted(years.items())),
        'months': month_rows,
        'hours_year': this_year,
        'hours': [hours[h] for h in range(24)],
        'tools': dict(tools.most_common()),
        'day': last,
        'launches': launches,
    }
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'usage.json')
    with open(dest, 'w') as fh:
        json.dump(out, fh, separators=(',', ':'), ensure_ascii=False)
        fh.write('\n')
    print(f"{dest}: {len(out['countries'])} countries, {out['launches_year']:,} launches in {full_year}, "
          f"{out['total']:,} since {min(years)}, {len(launches)} on {last}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:4])
