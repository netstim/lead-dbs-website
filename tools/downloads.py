"""Download figures for the home page globe, from the download log of lead-dbs.org: data/downloads.json.

    python3 tools/downloads.py <log directory> <country database .mmdb> [last day, YYYY-MM-DD]

The log directory holds download.log (and download.log.bak): one line per download from lead-dbs.org,
with the time, the IP address and the item fetched (Lead-DBS itself, a standalone build, a data pack, an
atlas ...). The country database is a free IP-to-country file in MaxMind format (for example DB-IP "IP to
Country Lite"); the lookup runs on this computer, with today's database, so an old address may be placed
in the wrong country now and then. Needs maxminddb and pycountry, at the versions in
tools/requirements.txt:
    python3 -m pip install --require-hashes -r tools/requirements.txt

What is counted:
- A download is one IP address fetching one item on one day: the same address fetching the same item
  twice in a day (a retry, a broken connection) counts once.
- Only Lead-DBS itself is counted: the items latest, hotfix, lead, lead_dropbox and lead_pcloud, and the
  standalone builds (any item with "standalone" in its name). Data packs and atlases are left out; many of
  their downloads come from servers, not people.
- Bots are left out: addresses in blocks of known crawlers and cloud servers (Google, Bing and Microsoft,
  Azure, Alibaba Cloud, Hetzner; see BOT_BLOCKS), and any address with more than 50 downloads of Lead-DBS
  (HEAVY), which no person needs.
The log runs to the last full day, unless a last day is named.

What leaves this script: downloads by country and month, and the countries' names. No IP address, city
or network name is written.
"""
import collections
import datetime
import json
import os
import re
import sys

import maxminddb
import pycountry

LINE = re.compile(r'^(\d{4}-\d{2}-\d{2}) [\d:]+, .*?IP: ([0-9a-fA-F:.]+),\s*(\S*)')
SOFTWARE = ('latest', 'hotfix', 'lead', 'lead_dropbox', 'lead_pcloud')
# the first two parts of an IPv4 address (crawlers, cloud and hosting servers)
BOT_BLOCKS = ('66.249', '40.77', '157.55', '207.46', '52.167', '47.128', '65.21', '136.243', '116.202', '88.198',
              '5.9', '148.251', '95.216', '135.181', '138.201', '144.76', '78.46')
BOT_FIRST = ('20', '13')  # Microsoft Azure
BOT_V6 = ('2a01:4f8:',)  # Hetzner
HEAVY = 50


def is_software(item):
    return item in SOFTWARE or 'standalone' in item


def is_bot(ip):
    parts = ip.split('.')
    return '.'.join(parts[:2]) in BOT_BLOCKS or parts[0] in BOT_FIRST or ip.startswith(BOT_V6)


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

    # every download of Lead-DBS, once per address, item and day
    seen = set()
    for name in ('download.log.bak', 'download.log'):
        path = os.path.join(logdir, name)
        if not os.path.exists(path):
            continue
        with open(path, errors='replace') as fh:
            for line in fh:
                m = LINE.match(line)
                if m and is_software(m.group(3)):
                    day, ip, item = m.groups()
                    seen.add((day, ip, item))
    if not seen:
        sys.exit('no downloads found in ' + logdir)

    last = last or (datetime.date.fromisoformat(max(k[0] for k in seen)) - datetime.timedelta(days=1)).isoformat()
    rows = [k for k in seen if k[0] <= last]
    per_ip = collections.Counter(ip for _, ip, _ in rows)

    months = collections.defaultdict(collections.Counter)
    names = {}
    dropped = collections.Counter()
    for day, ip, _ in rows:
        if is_bot(ip):
            dropped['bot blocks'] += 1
            continue
        if per_ip[ip] > HEAVY:
            dropped[f'over {HEAVY} a person'] += 1
            continue
        num, cname = country(ip)
        if not num:
            dropped['no country'] += 1
            continue
        months[day[:7]][num] += 1
        names[num] = cname

    totals = collections.Counter()
    for c in months.values():
        totals.update(c)
    out = {
        'rule': 'one IP address + one item + one day = one download; Lead-DBS itself only; bots left out',
        'from': min(k[0] for k in rows),
        'to': last,
        'total': sum(totals.values()),
        'countries': [[k, names[k], v] for k, v in totals.most_common()],
        'months': [[m, dict(c.most_common())] for m, c in sorted(months.items())],
    }
    dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'downloads.json')
    with open(dest, 'w') as fh:
        json.dump(out, fh, separators=(',', ':'), ensure_ascii=False)
        fh.write('\n')
    print(f"{dest}: {out['total']:,} downloads from {len(totals)} countries, {out['from']} to {last}; "
          f"left out: {', '.join(f'{k} {v:,}' for k, v in dropped.items())}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(*sys.argv[1:4])
