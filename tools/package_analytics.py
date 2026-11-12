"""Build a lab handoff bundle from an explicit source allowlist; never deploy."""
import argparse
import gzip
import io
from pathlib import Path
import tarfile
import tempfile
import os

ROOT=Path(__file__).resolve().parents[1]
FILES={
    'collector/Collector.php':'server/analytics/Collector.php',
    'collector/bootstrap.php':'server/analytics/bootstrap.php',
    'collector/collect.php':'server/analytics/collect.php',
    'collector/download-hook.php':'server/analytics/download-hook.php',
    'collector/maintenance.php':'server/analytics/maintenance.php',
    'collector/.htaccess':'server/analytics/.htaccess',
    'collector/composer.json':'server/analytics/composer.json',
    'collector/composer.lock':'server/analytics/composer.lock',
    'collector/artifacts.json':'analytics/artifacts.json',
    'collector/config.example.json':'server/analytics/config.example.json',
    'README.md':'server/analytics/README.md',
    'tools/analytics_ops.py':'tools/analytics_ops.py',
    'tools/usage.py':'tools/usage.py',
    'tools/requirements.txt':'tools/requirements.txt',
    'tests/php/collector.php':'tests/php/collector.php',
    'tests/test_analytics_ops.py':'tests/test_analytics_ops.py',
    'tests/test_collector_http.py':'tests/test_collector_http.py',
    'tests/test_download_hook.py':'tests/test_download_hook.py',
    'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb':'tests/fixtures/geoip/GeoIP2-Country-Test.mmdb',
    'tests/fixtures/geoip/README.md':'tests/fixtures/geoip/README.md',
    'tests/fixtures/geoip/LICENSE-APACHE':'tests/fixtures/geoip/LICENSE-APACHE',
    'tests/fixtures/geoip/LICENSE-MIT':'tests/fixtures/geoip/LICENSE-MIT',
    'operations.example.json':'analytics/operations.example.json',
    'crontab.example':'analytics/crontab.example',
    'matlab/ea_analytics.m':'integrations/matlab/ea_analytics.m',
    'matlab/ea_analytics_consent.m':'integrations/matlab/ea_analytics_consent.m',
    'matlab/README.md':'integrations/matlab/README.md',
}


def package(output):
    output=Path(output).resolve()
    if output.is_relative_to(ROOT):raise ValueError('Bundle output must be outside the repository')
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent,delete=False) as handle:
            tmp=Path(handle.name)
            with gzip.GzipFile(fileobj=handle,mode='wb',filename='',mtime=0) as gz, tarfile.open(fileobj=gz,mode='w') as tar:
                for dest,source in sorted(FILES.items()):
                    data=(ROOT/source).read_bytes()
                    info=tarfile.TarInfo(dest);info.size=len(data);info.mode=0o644;info.mtime=0
                    tar.addfile(info,io.BytesIO(data))
        os.replace(tmp,output)
    finally:
        if tmp and tmp.exists():tmp.unlink()


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);args=p.parse_args()
    package(args.output)
    print('Lab handoff bundle created. Install locked Composer dependencies before activation; no deployment performed.')
