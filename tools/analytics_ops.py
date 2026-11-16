"""Lab-operated collector maintenance. Local PHP only; no remote writes or deployment.

Run after lab activation: python3 tools/analytics_ops.py run /private/config.json
Monitor (hourly): python3 tools/analytics_ops.py check /private/config.json
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

CONFIG_KEYS = {'php', 'collector_dir', 'collector_config', 'private_dir', 'output'}
# Files inside private_dir that the job itself owns; a report may never replace one of them.
STATUS_FILE = 'status.json'
LOCK_FILE = 'run.lock'
ARCHIVE_FILE = 'aggregate-archive.sqlite'
SQLITE_SIDECARS = ('-journal', '-wal', '-shm')
BACKUP_DIR = 'backups'
REPORT_DIR = 'reports'
BACKUPS_KEPT = 7

# The daily run must have succeeded within this window.
STATUS_MAX_AGE = dt.timedelta(hours=30)
# Retention runs hourly from cron; this tolerates one late or failed run and alerts on the second.
RETENTION_MAX_AGE = dt.timedelta(hours=2)
COLLECTOR_STALE_DAYS = 2
# Alert at 90% of the configured database ceiling, before intake starts shedding at 100%.
STORAGE_WARNING_PERCENT = 90

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


def _resolved(path):
    return Path(path).resolve(strict=False)


def _collector_private_files(collector_config):
    """The database, key and country files the collector config names, when that config is readable."""
    try:
        settings = json.loads(Path(collector_config).read_text())
    except (OSError, ValueError):
        return []
    if not isinstance(settings, dict):
        return []
    files = []
    for key in ('database', 'key_file', 'country_database'):
        value = settings.get(key)
        if isinstance(value, str) and value:
            files.append(Path(value))
    database = settings.get('database')
    if isinstance(database, str) and database:
        files.extend(Path(database + suffix) for suffix in SQLITE_SIDECARS)
    return files


def report_path(config, operations_config=None):
    """Validate config['output'] without touching the filesystem.

    The report must be a regular file directly inside <private_dir>/reports/, reached without
    symlinks, and must not alias any file the job, collector or configuration depends on.
    """
    private = Path(config['private_dir'])
    if not private.is_absolute():
        raise ValueError('private_dir must be an absolute path')
    if _resolved(private).is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError('Operational state must be outside the repository')
    reports = private / REPORT_DIR
    output = Path(config['output'])
    if not output.is_absolute():
        raise ValueError('output must be an absolute path')

    # Lexical and resolved checks together: neither reports/ nor the report may be reached through a symlink.
    if Path(os.path.normpath(output)).parent != Path(os.path.normpath(reports)):
        raise ValueError('Operational output must be a file directly inside private_dir/reports')
    if reports.is_symlink() or output.is_symlink():
        raise ValueError('Operational output must not be a symlink or inside one')
    if reports.exists() and not reports.is_dir():
        raise ValueError('private_dir/reports must be a directory')
    if output.exists() and not output.is_file():
        raise ValueError('Operational output must be a regular file')
    resolved = _resolved(output)
    if resolved.parent != _resolved(reports):
        raise ValueError('Operational output must be a file directly inside private_dir/reports')

    reserved = [private / STATUS_FILE, private / LOCK_FILE, private / ARCHIVE_FILE]
    reserved += [private / (ARCHIVE_FILE + suffix) for suffix in SQLITE_SIDECARS]
    reserved.append(Path(config['collector_config']))
    reserved += _collector_private_files(config['collector_config'])
    if operations_config is not None:
        reserved.append(Path(operations_config))
    if any(resolved == _resolved(path) for path in reserved):
        raise ValueError('Operational output would replace a reserved file')
    if resolved.is_relative_to(_resolved(private / BACKUP_DIR)):
        raise ValueError('Operational output would replace a backup')
    return output


def run(config, now=None, operations_config=None):
    """Export closed days, run retention, archive, back up and write the report and status."""
    now = now or dt.datetime.now(dt.timezone.utc)
    # Everything is validated before the first subprocess call or filesystem change.
    output = report_path(config, operations_config)
    private = Path(config['private_dir'])
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    (private / REPORT_DIR).mkdir(mode=0o700, exist_ok=True)
    status_file = private / STATUS_FILE

    with (private / LOCK_FILE).open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            cutoff = (now.date() - dt.timedelta(days=1)).isoformat()
            try:
                batch = php_command(config, 'export', cutoff)
            finally:
                # Deletion is independent of export, validation, backup or report success.
                retention = php_command(config, 'retain')
            validate_batch(batch)

            archive = private / ARCHIVE_FILE
            public = ingest(archive, batch)
            # Aggregate-only backup, never a copy of the pseudonymous event DB.
            backups = private / BACKUP_DIR
            backups.mkdir(mode=0o700, exist_ok=True)
            backup_atomic(archive, backups / (now.strftime('%Y%m%dT%H%M%S') + '.sqlite'))
            usage.write_atomic(output, public)

            health = php_command(config, 'health')
            # Absence of events is visible, never asserted to mean no users.
            latest = health['last_event_day']
            stale = latest is None or (now.date() - dt.date.fromisoformat(latest)).days > COLLECTOR_STALE_DAYS
            status = {
                'schema': 1,
                'ok': True,
                'completed_at': now.isoformat(),
                'cutoff': cutoff,
                'collector_stale': stale,
                'last_event_day': latest,
                'retention': retention,
            }
            usage.write_atomic(status_file, status)
            for old in sorted(backups.glob('*.sqlite'))[:-BACKUPS_KEPT]:
                old.unlink()
            return status
        except Exception:
            failure = {
                'schema': 1,
                'ok': False,
                'completed_at': now.isoformat(),
                'error': 'maintenance_failed; inspect configuration and service health',
            }
            usage.write_atomic(status_file, failure)
            raise


def _age(timestamp, now):
    """Elapsed time since an ISO timestamp with offset; None when it is missing or invalid."""
    if not isinstance(timestamp, str):
        return None
    try:
        moment = dt.datetime.fromisoformat(timestamp)
    except ValueError:
        return None
    if moment.tzinfo is None:
        return None
    return now - moment


def _fresh(age, limit):
    return age is not None and dt.timedelta(0) <= age <= limit


def problems(config, now=None):
    """Fixed-text descriptions of everything that needs attention; empty when healthy."""
    now = now or dt.datetime.now(dt.timezone.utc)
    found = []

    try:
        status = json.loads((Path(config['private_dir']) / STATUS_FILE).read_text())
    except (OSError, ValueError):
        status = None
    if not isinstance(status, dict):
        found.append('No readable maintenance status')
    else:
        if status.get('ok') is not True:
            found.append('The last maintenance run failed')
        if not _fresh(_age(status.get('completed_at'), now), STATUS_MAX_AGE):
            found.append('The last maintenance run is older than 30 hours')
        if status.get('collector_stale', True):
            found.append(f'No collected event in the last {COLLECTOR_STALE_DAYS} days')

    # Live from the database, so a failing hourly retention job is noticed even when the daily run succeeds.
    try:
        health = php_command(config, 'health')
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError):
        health = None
    if not isinstance(health, dict):
        found.append('Collector health is unavailable')
        return found
    if not _fresh(_age(health.get('last_retention_at'), now), RETENTION_MAX_AGE):
        found.append('Retention has not completed in the last 2 hours')

    storage = health.get('storage')
    if not isinstance(storage, dict):
        found.append('Collector storage usage is unavailable')
        return found
    size = storage.get('database_bytes')
    ceiling = storage.get('max_database_bytes')
    free = storage.get('free_bytes')
    floor = storage.get('min_free_bytes')
    if type(size) is not int or type(ceiling) is not int or ceiling < 1:
        found.append('Collector database size is unavailable')
    elif size * 100 >= ceiling * STORAGE_WARNING_PERCENT:
        found.append('Collector database is at or above 90% of max_database_bytes')
    if type(free) is not int or type(floor) is not int:
        found.append('Free space is unavailable; collection is shedding')
    elif free < floor:
        found.append('Free space is below min_free_bytes; collection is shedding')
    return found


def check(config, now=None):
    return not problems(config, now)


def load_config(path):
    config = json.loads(Path(path).read_text())
    if not isinstance(config, dict) or set(config) != CONFIG_KEYS:
        raise ValueError('Invalid operational configuration')
    return config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'check'])
    parser.add_argument('config', type=Path)
    args = parser.parse_args()
    config = load_config(args.config)

    if args.command == 'run':
        result = run(config, operations_config=args.config)
        freshness = 'stale' if result['collector_stale'] else 'current'
        print('Maintenance completed; collector freshness: ' + freshness)
        return 0

    found = problems(config)
    if not found:
        print('Analytics healthy')
        return 0
    print('Analytics needs attention: ' + '; '.join(found))
    return 1


if __name__ == '__main__':
    os.umask(0o077)
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError):
        raise SystemExit('Analytics operation failed; inspect the private status file and configuration.') from None
