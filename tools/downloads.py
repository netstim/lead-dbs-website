"""Offline historical download-request aggregation; no requests to the live site."""
import argparse
import collections
import datetime as dt
import hashlib
import ipaddress
import json
from pathlib import Path
import re
try:
    from . import usage
except ImportError:
    import usage

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = 1
RULES = 'download-address-artifact-day-v1'
ALL_KEYS = {'schema','rules','registry_version','from','to','observed_to','timezone','country_database',
        'total','categories','years','months','countries','program_countries','quality','high_frequency_threshold'}
QKEYS = {'rows','parsed','malformed','after_cutoff','collapsed','included','unknown_country',
         'unknown_artifact','high_frequency_groups','high_frequency_raw_requests'}


def registry(path=ROOT / 'analytics/artifacts.json'):
    data = json.loads(Path(path).read_text())
    assert data['schema'] == 1
    aliases = {}
    for category, names in data['aliases'].items():
        if category not in data['categories']:
            raise ValueError('Invalid artifact category')
        for name in names:
            if name in aliases:
                raise ValueError('Duplicate artifact alias')
            aliases[name] = category
    return data, aliases


def classify(artifact, aliases):
    if artifact in aliases:
        return aliases[artifact]
    if re.fullmatch(r'updates_?\d{2,6}[-_]\d{2,6}', artifact):
        return 'program_update'
    return 'unknown'


def parse(line):
    m = usage.LINE.fullmatch(line.strip())
    if not m:
        return None
    try:
        when = dt.datetime.strptime(m[1], '%Y-%m-%d %H:%M:%S')
        address = str(ipaddress.ip_address(m[2]))
    except ValueError:
        return None
    artifact = m[3].strip()
    if not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', artifact):
        return None
    return when.date(), address, artifact


def aggregate_all(lines, lookup, cutoff, database, artifact_registry=None, threshold=100):
    end = dt.date.fromisoformat(cutoff)
    if type(threshold) is not int or threshold < 2:
        raise ValueError('Invalid repetition threshold')
    catalog, aliases = artifact_registry or registry()
    q = dict.fromkeys(sorted(QKEYS), 0)
    groups = collections.Counter()
    first = observed = None
    for line in lines:
        q['rows'] += 1
        row = parse(line)
        if row is None:
            q['malformed'] += 1
            continue
        q['parsed'] += 1
        day, address, artifact = row
        observed = max(day, observed) if observed else day
        if day > end:
            q['after_cutoff'] += 1
            continue
        first = min(day, first) if first else day
        groups[(address, day.isoformat(), artifact)] += 1
    if not groups or end > observed:
        raise ValueError('No included data or cutoff beyond source coverage')
    counts = collections.Counter()
    years = collections.defaultdict(collections.Counter)
    months = collections.Counter()
    countries = collections.Counter()
    program_countries = collections.Counter()
    names, cache = {}, {}
    for (address, day, artifact), repeats in sorted(groups.items()):
        category = classify(artifact, aliases)
        counts[category] += 1
        years[day[:4]][category] += 1
        months[day[:7]] += 1
        q['collapsed'] += repeats - 1
        q['unknown_artifact'] += category == 'unknown'
        if repeats >= threshold:
            q['high_frequency_groups'] += 1
            q['high_frequency_raw_requests'] += repeats
        if address not in cache:
            cache[address] = lookup(address)
        country = cache[address]
        if country:
            code, name = country
            names[code] = name
            countries[code] += 1
            if category == 'program':
                program_countries[code] += 1
        else:
            q['unknown_country'] += 1
    q['included'] = len(groups)
    country_rows = lambda c: [[code, names[code], n] for code, n in sorted(c.items(), key=lambda x: (-x[1], x[0]))]
    out = {'schema':SCHEMA,'rules':RULES,'registry_version':catalog['version'],
           'from':first.isoformat(),'to':cutoff,'observed_to':observed.isoformat(),
           'timezone':'unverified_server_clock','country_database':dict(database),
           'total':len(groups),'categories':dict(sorted(counts.items())),
           'years':{y:dict(sorted(v.items())) for y,v in sorted(years.items())},
           'months':[[m,months.get(m)] for m in usage.month_range(first,end)],
           'countries':country_rows(countries),'program_countries':country_rows(program_countries),
           'quality':q,'high_frequency_threshold':threshold}
    validate_all(out, catalog['categories'])
    return out


def validate_all(data, categories=None):
    def require(condition, message):
        if not condition:
            raise ValueError(message)
    require(set(data)==ALL_KEYS and data['schema']==SCHEMA and data['rules']==RULES, 'Invalid download schema')
    require(data['timezone']=='unverified_server_clock','Invalid legacy timezone')
    for field in ['from','to','observed_to']:
        dt.date.fromisoformat(data[field])
    require(data['from']<=data['to']<=data['observed_to'],'Invalid coverage')
    require(set(data['country_database'])=={'name','date'},'Invalid geography metadata')
    dt.date.fromisoformat(data['country_database']['date'])
    count=lambda n:type(n) is int and n>=0
    q=data['quality'];require(set(q)==QKEYS and all(count(n) for n in q.values()),'Invalid quality counters')
    require(q['rows']==q['parsed']+q['malformed'],'Rows do not reconcile')
    require(q['parsed']==q['after_cutoff']+q['collapsed']+q['included'],'Records do not reconcile')
    require(count(data['total']) and data['total']==q['included'],'Total mismatch')
    allowed=set(categories or registry()[0]['categories'])
    require(set(data['categories'])<=allowed and all(count(v) for v in data['categories'].values()),'Invalid categories')
    require(sum(data['categories'].values())==data['total'],'Category total mismatch')
    require(data['categories'].get('unknown',0)==q['unknown_artifact'],'Unknown count mismatch')
    combined=collections.Counter()
    for year, values in data['years'].items():
        require(re.fullmatch(r'\d{4}',year) and set(values)<=allowed and all(count(n) for n in values.values()),'Invalid year')
        combined.update(values)
    require(dict(combined)==data['categories'],'Year categories mismatch')
    require([m for m,n in data['months']]==list(usage.month_range(dt.date.fromisoformat(data['from']),dt.date.fromisoformat(data['to']))),'Invalid month series')
    require(all(n is None or count(n) for m,n in data['months']) and sum(n or 0 for m,n in data['months'])==data['total'],'Month total mismatch')
    for field in ['countries','program_countries']:
        seen=set()
        for code,name,n in data[field]:
            require(isinstance(code,str) and re.fullmatch(r'\d{3}',code) and code not in seen,'Invalid country')
            require(isinstance(name,str) and 0<len(name)<100 and count(n) and n>0,'Invalid country count')
            seen.add(code)
    require(sum(c[2] for c in data['countries'])+q['unknown_country']==data['total'],'Country total mismatch')
    require(sum(c[2] for c in data['program_countries'])<=data['categories'].get('program',0),'Program geography mismatch')
    totals={c:n for c,name,n in data['countries']}
    require(all(n<=totals.get(c,0) for c,name,n in data['program_countries']),'Program country exceeds total')
    require(type(data['high_frequency_threshold']) is int and data['high_frequency_threshold']>=2,'Invalid frequency threshold')
    require(q['high_frequency_groups']<=data['total'] and q['high_frequency_raw_requests']<=q['parsed']-q['after_cutoff'],'Invalid repetition diagnostic')
    require(q['high_frequency_raw_requests']>=q['high_frequency_groups']*data['high_frequency_threshold'],'Repetition count mismatch')
    def inspect(value):
        if isinstance(value,str):
            try: ipaddress.ip_address(value)
            except ValueError: return
            raise ValueError('Address found in public data')
        if isinstance(value,dict):
            for k,v in value.items():inspect(k);inspect(v)
        if isinstance(value,list):
            for v in value:inspect(v)
    inspect(data)


# Retain PR #24's historical selection for continuity, but name its limitations.
# These are heuristic network ranges, NOT verified crawler identities.
NETWORK_PREFIXES = ('66.249', '40.77', '157.55', '207.46', '52.167', '47.128',
    '65.21', '136.243', '116.202', '88.198', '5.9', '148.251', '95.216',
    '135.181', '138.201', '144.76', '78.46')
HEAVY = 50
GLOBE_KEYS = {'schema','rule','rules','from','to','total','countries','months','selection','all_requests'}


def network_flag(address):
    parsed = ipaddress.ip_address(address)
    address = str(getattr(parsed, 'ipv4_mapped', None) or parsed)
    return ('.'.join(address.split('.')[:2]) in NETWORK_PREFIXES or
            address.split('.')[0] in ('13','20') or address.startswith('2a01:4f8:'))


def aggregate(lines, lookup, cutoff, database, artifact_registry=None, threshold=100):
    lines = list(lines)
    catalog, aliases = artifact_registry or registry()
    all_requests = aggregate_all(lines, lookup, cutoff, database, (catalog,aliases), threshold)
    # Preserve #24's approved artifact selection; the wider inventory is
    # available separately in all_requests.
    selected = set()
    for line in lines:
        row = parse(line)
        if row and row[0].isoformat() <= cutoff:
            day,address,artifact = row
            if artifact in {'latest','hotfix','lead','lead_dropbox','lead_pcloud'} or 'standalone' in artifact:
                selected.add((day.isoformat(),address,artifact))
    frequency = collections.Counter(address for day,address,item in selected)
    dropped = {'network_heuristic':0,'high_lifetime_frequency':0,'unknown_country':0}
    months = collections.defaultdict(collections.Counter)
    totals,names,cache = collections.Counter(),{},{}
    for day,address,item in sorted(selected):
        if network_flag(address):
            dropped['network_heuristic'] += 1
            continue
        if frequency[address] > HEAVY:
            dropped['high_lifetime_frequency'] += 1
            continue
        if address not in cache: cache[address] = lookup(address)
        country = cache[address]
        if not country:
            dropped['unknown_country'] += 1
            continue
        code,name = country
        totals[code] += 1
        months[day[:7]][code] += 1
        names[code] = name
    first = min((day for day,address,item in selected), default=all_requests['from'])
    data = {'schema':1,'rules':RULES,'rule':'one address + artifact + day; program and hotfix requests; legacy heuristic exclusions, not verified humans',
      'from':first,'to':cutoff,'total':sum(totals.values()),
      'countries':[[c,names[c],n] for c,n in sorted(totals.items(),key=lambda x:(-x[1],x[0]))],
      'months':[[m,dict(sorted(months[m].items()))] for m in usage.month_range(dt.date.fromisoformat(first),dt.date.fromisoformat(cutoff))],
      'selection':{'version':'globe-legacy-heuristics-v1','candidate_requests':len(selected),'excluded':dropped,
        'lifetime_threshold':HEAVY,'country_minimum':1,
        'limitations':'Hosting ranges and more than 50 requests across the entire reporting period are imperfect heuristics. They can exclude legitimate users and miss automation. All-request counts remain available separately.'},
      'all_requests':all_requests}
    validate(data)
    return data


def validate(data):
    if set(data)!=GLOBE_KEYS or data['schema']!=1 or data['rules']!=RULES:
        raise ValueError('Invalid globe-compatible download schema')
    validate_all(data['all_requests'])
    if data['to'] != data['all_requests']['to'] or not data['all_requests']['from']<=data['from']<=data['to']:
        raise ValueError('Invalid globe coverage')
    expected=list(usage.month_range(dt.date.fromisoformat(data['from']),dt.date.fromisoformat(data['to'])))
    if [m for m,by in data['months']]!=expected:raise ValueError('Invalid globe months')
    totals=collections.Counter()
    for month,by in data['months']:
        for code,n in by.items():
            if not re.fullmatch(r'\d{3}',code) or type(n) is not int or n<=0:raise ValueError('Invalid globe count')
        totals.update(by)
    rows={}
    for code,name,n in data['countries']:
        if code in rows or not isinstance(name,str) or type(n) is not int or n<=0:raise ValueError('Invalid globe country')
        rows[code]=n
    if dict(totals)!=rows or sum(totals.values())!=data['total']:raise ValueError('Globe totals mismatch')
    selection=data['selection']
    if set(selection)!={'version','candidate_requests','excluded','lifetime_threshold','country_minimum','limitations'}:raise ValueError('Invalid selection metadata')
    if set(selection['excluded'])!={'network_heuristic','high_lifetime_frequency','unknown_country'}:raise ValueError('Invalid exclusion reasons')
    if any(type(n) is not int or n<0 for n in selection['excluded'].values()):raise ValueError('Invalid exclusions')
    if selection['candidate_requests']!=data['total']+sum(selection['excluded'].values()) or selection['country_minimum']!=1:raise ValueError('Selection does not reconcile')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('logdir',type=Path);p.add_argument('database',type=Path)
    p.add_argument('--cutoff',required=True);p.add_argument('--manifest',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'data/downloads.json')
    args=p.parse_args()
    sources=[args.logdir/n for n in ['download.log.bak','download.log'] if (args.logdir/n).is_file()]
    if not sources or args.manifest.resolve().is_relative_to(ROOT):p.error('Logs and a private manifest outside this repository are required')
    protected={p.resolve() for p in [*sources,args.database]}
    if args.output.resolve() in protected or args.manifest.resolve() in protected or args.output.resolve()==args.manifest.resolve():p.error('Inputs and outputs must be distinct')
    import maxminddb,pycountry
    def sha(path):
        with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
    hashes={p.name:sha(p) for p in sources}; db_hash=sha(args.database)
    with maxminddb.open_database(str(args.database)) as reader:
        meta=reader.metadata();db={'name':meta.database_type,'date':dt.datetime.fromtimestamp(meta.build_epoch,dt.timezone.utc).date().isoformat()}
        def lookup(ip):
            code=(reader.get(ip) or {}).get('country',{}).get('iso_code')
            c=pycountry.countries.get(alpha_2=code) if code else None
            return (c.numeric,getattr(c,'common_name',None) or c.name) if c else None
        def lines():
            for source in sources:
                with source.open(encoding='utf-8',errors='replace') as f:yield from f
        data=aggregate(lines(),lookup,args.cutoff,db)
    if hashes!={p.name:sha(p) for p in sources} or db_hash!=sha(args.database):raise ValueError('Inputs changed during import')
    usage.write_atomic(args.manifest,{'schema':1,'rules':RULES,'sources_sha256':hashes,'database_sha256':db_hash,'registry_sha256':sha(ROOT/'analytics/artifacts.json'),'parser_sha256':sha(Path(__file__)),'cutoff':args.cutoff,'public_sha256':hashlib.sha256(usage.public_bytes(data)).hexdigest(),'quality':data['all_requests']['quality']})
    usage.write_atomic(args.output,data)
    print('Published download-request aggregates; raw addresses remain private.')


if __name__=='__main__':
    try:main()
    except (ValueError,OSError):raise SystemExit('Download import failed; check inputs, cutoff and permissions. Public data unchanged.') from None
