"""Lab-operated collector maintenance. Local PHP only; no remote writes or deployment.

Run after lab activation: python3 tools/analytics_ops.py run /private/config.json
Monitor: python3 tools/analytics_ops.py check /private/config.json
"""
import argparse
import collections
from contextlib import closing
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import tempfile
try:
    from . import usage
except ImportError:
    import usage

SERIES = {'access': {'day','country','n'}, 'tools': {'day','item','n'},
          'download_requests': {'day','item','country','n'}, 'outcomes': {'day','kind','outcome','traffic','n'}}


def validate_batch(batch):
    if set(batch) != {'schema','timezone','cutoff','series'} or batch['schema'] != 1 or batch['timezone'] != 'UTC':
        raise ValueError('Invalid collector export')
    cutoff = dt.date.fromisoformat(batch['cutoff'])
    if set(batch['series']) != set(SERIES):
        raise ValueError('Unexpected export series')
    seen = set()
    for name, rows in batch['series'].items():
        for row in rows:
            if set(row) != SERIES[name] or type(row['n']) is not int or row['n'] < 1:
                raise ValueError('Invalid aggregate row')
            if dt.date.fromisoformat(row['day']) > cutoff:
                raise ValueError('Unclosed day in export')
            if 'country' in row and not re.fullmatch(r'[A-Z]{2}', row['country']):
                raise ValueError('Invalid country')
            if 'item' in row and not re.fullmatch(r'[A-Za-z0-9_.-]{1,100}', row['item']):
                raise ValueError('Invalid artifact')
            if name == 'tools' and row['item'] not in {'dbs','group','connectome','anatomy','other'}:
                raise ValueError('Invalid tool')
            if name == 'outcomes' and (row['kind'] not in {'access','download'} or row['outcome'] not in {'request','redirect','file_response','not_found'} or row['traffic'] not in {'unclassified','declared_automation'}):
                raise ValueError('Invalid outcome')
            key = (name, tuple(sorted((k,v) for k,v in row.items() if k != 'n')))
            if key in seen:
                raise ValueError('Duplicate aggregate dimension')
            seen.add(key)


def ingest(archive, batch):
    """Replace closed-day snapshots atomically; replays do not add counts twice."""
    validate_batch(batch)
    days = {}
    for name, rows in batch['series'].items():
        for row in rows:
            day = row['day']
            days.setdefault(day, {s: [] for s in SERIES})[name].append(row)
    with closing(sqlite3.connect(archive)) as db:
        db.execute('CREATE TABLE IF NOT EXISTS days(day TEXT PRIMARY KEY, payload TEXT NOT NULL)')
        with db:
            for day, values in sorted(days.items()):
                db.execute('INSERT INTO days VALUES(?,?) ON CONFLICT(day) DO UPDATE SET payload=excluded.payload',
                           (day,json.dumps(values,sort_keys=True,separators=(',',':'))))
        stored = db.execute('SELECT day,payload FROM days ORDER BY day').fetchall()
    return summarize(stored, batch['cutoff'])


def summarize(stored, cutoff):
    access,downloads,tools,countries = (collections.Counter() for _ in range(4))
    unknown = 0
    days = []
    for day,payload in stored:
        if day > cutoff:
            continue
        days.append(day)
        series = json.loads(payload)
        validate_batch({'schema':1,'timezone':'UTC','cutoff':cutoff,'series':series})
        for row in series['access']:
            access[day[:7]] += row['n']
            if row['country'] == 'ZZ': unknown += row['n']
            else: countries[row['country']] += row['n']
        for row in series['download_requests']: downloads[day[:7]] += row['n']
        for row in series['tools']: tools[row['item']] += row['n']
    return {'schema':1,'timezone':'UTC','from':min(days) if days else None,'to':cutoff,
            'access':{'total':sum(access.values()),'months':dict(sorted(access.items())),
                      'countries':dict(sorted(countries.items())),'unknown_country':unknown,'tools':dict(sorted(tools.items()))},
            'download_requests':{'total':sum(downloads.values()),'months':dict(sorted(downloads.items()))}}


def php_command(config, *args):
    proc = subprocess.run([config['php'],str(Path(config['collector_dir'])/'maintenance.php'),*args],
        env={**os.environ,'LEAD_ANALYTICS_CONFIG':config['collector_config']},capture_output=True,text=True,timeout=120)
    if proc.returncode:
        raise RuntimeError('Collector maintenance failed')
    return json.loads(proc.stdout)


def backup_atomic(archive, backup):
    """Only complete SQLite backups are eligible for rotation."""
    fd, name = tempfile.mkstemp(dir=backup.parent, prefix='.backup-', suffix='.tmp')
    os.close(fd)
    temporary = Path(name)
    try:
        with closing(sqlite3.connect(archive)) as source, closing(sqlite3.connect(temporary)) as destination:
            source.backup(destination)
            if destination.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise RuntimeError('Aggregate backup failed validation')
        os.replace(temporary, backup)
    finally:
        temporary.unlink(missing_ok=True)


def run(config, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    private = Path(config['private_dir'])
    private.mkdir(mode=0o700,parents=True,exist_ok=True)
    if private.resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError('Operational state must be outside the repository')
    output = Path(config['output']).resolve()
    if not output.is_relative_to(private.resolve()):
        raise ValueError('Operational output must be inside private_dir')
    status_file = private/'status.json'
    with (private/'run.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            cutoff = (now.date()-dt.timedelta(days=1)).isoformat()
            try:
                batch = php_command(config,'export',cutoff)
            finally:
                # Deletion is independent of export, validation, backup or report success.
                retention = php_command(config,'retain')
            validate_batch(batch)
            archive = private/'aggregate-archive.sqlite'
            public = ingest(archive,batch)
            # Aggregate-only backup, never a copy of the pseudonymous event DB.
            backups = private/'backups';backups.mkdir(mode=0o700,exist_ok=True)
            backup = backups/(now.strftime('%Y%m%dT%H%M%S')+'.sqlite')
            backup_atomic(archive, backup)
            usage.write_atomic(config['output'],public)
            health = php_command(config,'health')
            # Absence of events is visible, never asserted to mean no users.
            latest = health['last_event_day']
            stale = latest is None or (now.date()-dt.date.fromisoformat(latest)).days > 2
            status = {'schema':1,'ok':True,'completed_at':now.isoformat(),'cutoff':cutoff,
                      'collector_stale':stale,'last_event_day':latest,'retention':retention}
            usage.write_atomic(status_file,status)
            for old in sorted(backups.glob('*.sqlite'))[:-7]: old.unlink()
            return status
        except Exception:
            usage.write_atomic(status_file,{'schema':1,'ok':False,'completed_at':now.isoformat(),
                                            'error':'maintenance_failed; inspect configuration and service health'})
            raise


def check(config, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    status = json.loads((Path(config['private_dir'])/'status.json').read_text())
    elapsed = now-dt.datetime.fromisoformat(status['completed_at'])
    return status.get('ok') is True and not status.get('collector_stale',True) and dt.timedelta(0)<=elapsed<=dt.timedelta(hours=30)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','check'])
    parser.add_argument('config',type=Path)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if set(config)!={'php','collector_dir','collector_config','private_dir','output'}:
        raise ValueError('Invalid operational configuration')
    if args.command=='run':
        result=run(config)
        print('Maintenance completed; collector freshness: '+('stale' if result['collector_stale'] else 'current'))
    else:
        ok=check(config);print('Analytics healthy' if ok else 'Analytics needs attention');return 0 if ok else 1
    return 0


if __name__=='__main__':
    os.umask(0o077)
    try:raise SystemExit(main())
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError):
        raise SystemExit('Analytics operation failed; inspect the private status file and configuration.') from None
