#!/usr/bin/env python3
"""One-time GitBook import of the Lead-DBS manual. Requires curl.

Usage (from the repository root):

    python3 tools/import_manual.py --plan [source-cache-directory]   # report only; writes nothing
    python3 tools/import_manual.py [source-cache-directory]          # import

The cache (default /tmp/lead-manual-source) keeps the public .md exports and index.json (title/URL pairs), so
a retry does not download them again. Every index URL must be a chapter below https://netstim.gitbook.io/leaddbs/,
and every image must be an https URL on a public host name.

The import is assembled in a staging folder and moved into content/manual, assets/manual and data/manual.json
only after every chapter and image was fetched, so a failed run changes nothing and can simply be retried.

Run it once: it refuses to start while content/manual or data/manual.json exists, so it never overwrites the
editorial changes made since the import (docs/manual.md).
"""
import argparse
import concurrent.futures
import hashlib
import html
import ipaddress
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://netstim.gitbook.io/leaddbs/'
DEFAULT_CACHE = Path('/tmp/lead-manual-source')
GROUPS = {'getting-started': 'Getting started', 'lead-dbs': 'Single-patient analysis',
          'lead-group': 'Group analysis', 'connectomics': 'Connectomics',
          'lead-or': 'Lead-OR', 'appendix': 'Reference'}
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}
# One folder of a chapter path below BASE. It cannot be empty, '.', '..' or hidden.
SEGMENT = re.compile(r'[A-Za-z0-9][A-Za-z0-9._-]*')


class ImportRefused(Exception):
    """The source or the repository is not in a state the import can safely run from."""


def fetch(url):
    """The body at url. curl refuses anything but https, on redirects too."""
    return subprocess.check_output(['curl', '-fLsS', '--proto', '=https', '--proto-redir', '=https',
                                    '--retry', '3', '--max-time', '120', url])


def contained(folder, relative):
    """folder/relative, refusing a relative path that would leave folder."""
    target = folder / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts \
            or not target.resolve().is_relative_to(folder.resolve()):
        raise ImportRefused(f'{relative!r} would leave {folder}')
    return target


def chapter_slug(url):
    """The path of a chapter URL below BASE, e.g. 'lead-dbs/step0-overview.md'. Refuses any other URL."""
    if not url.startswith(BASE) or not url.endswith('.md'):
        raise ImportRefused(f'not a chapter of {BASE}: {url}')
    slug = url.removeprefix(BASE)
    if not all(SEGMENT.fullmatch(part) for part in slug.removesuffix('.md').split('/')):
        raise ImportRefused(f'unexpected chapter path: {url}')
    return slug


def check_image_url(url):
    """Refuses an image URL that is not https on a public host name (no address, port or credentials)."""
    parts = urlsplit(url)
    host = parts.hostname or ''
    try:
        ipaddress.ip_address(host)
        is_address = True
    except ValueError:
        is_address = False
    if parts.scheme != 'https' or '.' not in host or is_address or parts.port or parts.username or parts.password:
        raise ImportRefused(f'image is not an https URL on a public host: {url}')


def read_index(cache, save):
    """The (title, URL) rows of the manual, from the cache or GitBook's llms.txt."""
    index = cache / 'index.json'
    if index.exists():
        rows = [tuple(row) for row in json.loads(index.read_text())]
    else:
        rows = re.findall(r'^- \[(.*?)\]\((.*?)\)', fetch(BASE + 'llms.txt').decode(), re.M)
    if not rows:
        raise ImportRefused('the index lists no chapters')
    for _, url in rows:
        chapter_slug(url)
    if save and not index.exists():
        cache.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps(rows))
    return rows


def read_chapter(cache, slug, url, save):
    cached = contained(cache, slug)
    if cached.exists():
        return cached.read_text(encoding='utf-8')
    body = fetch(url)
    if save:
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(body)
    return body.decode('utf-8')


def convert(rows, cache, save):
    """The chapters as [(page URL, Markdown document)], the navigation entries and the images {URL: file name}."""
    mapping = {url: '/manual/' + ('' if url == BASE+'readme.md' else url.removeprefix(BASE).removesuffix('.md')+'/') for _, url in rows}
    assets = {}

    def image_url(url):
        url = html.unescape(url).replace('\\&', '&')
        ext = Path(unquote(urlsplit(url).path)).suffix.lower()
        if ext not in IMAGE_TYPES:
            raise ValueError('Unknown image format: '+url)
        check_image_url(url)
        name = hashlib.sha256(url.encode()).hexdigest()[:16]+ext
        assets[url] = name
        return 'manual/'+name

    def link(url, source):
        url = html.unescape(url).replace('\\_', '_')
        if url.startswith('#'): return url
        full = urljoin(source, url)
        bits = urlsplit(full)
        key = bits._replace(fragment='', query='').geturl().rstrip('/')
        if key == BASE.rstrip('/'): key = BASE+'readme.md'
        if not key.endswith('.md'): key += '.md'
        target = mapping.get(key)
        return target + ('#'+bits.fragment if bits.fragment else '') if target else url

    chapters, pages = [], []
    for order, (title, source) in enumerate(rows):
        slug = chapter_slug(source)
        text = read_chapter(cache, slug, source, save)
        text = re.sub(r'^> For the complete documentation index.*\n', '', text)
        text = re.sub(r'^# .*\n', '', text, count=1, flags=re.M).strip()
        text = text.replace('&#x20;', ' ').replace('&#x26;', '&')
        text = re.sub(r'<mark[^>]*>(.*?)</mark>', r'\1', text, flags=re.S)
        text = re.sub(r'{% hint style="(.*?)" %}', r'{{% manual-note "\1" %}}', text)
        text = text.replace('{% endhint %}', '{{% /manual-note %}}')

        # Convert figures to Markdown so Hugo handles responsive images, captions and zoom links.
        def figure(m):
            block = m.group(0)
            src = re.search(r'src="([^"]+)"', block)
            alt = re.search(r'alt="([^"]*)"', block)
            caption = re.search(r'<figcaption>(.*?)</figcaption>', block, re.S)
            cap = html.unescape(re.sub('<[^>]+>', '', caption[1])).strip() if caption else ''
            desc = html.unescape(alt[1]) if alt and alt[1] else cap or title+' — screenshot'
            desc = desc.replace('[', '').replace(']', '')
            caption_text = ' "'+cap.replace('"', '&quot;')+'"' if cap else ''
            return '\n\n!['+desc+']('+image_url(src[1])+caption_text+')\n\n'

        text = re.sub(r'<figure>.*?</figure>', figure, text, flags=re.S)
        text = re.sub(r'<img\b[^>]*>', figure, text)
        text = re.sub(r'<div(?:\s[^>]*)?>|</div>', '', text)
        text = re.sub(r'!\[([^\]]*)\]\((https?://[^\s)]+)\)', lambda m: '!['+(m[1] or title+' — screenshot')+']('+image_url(m[2])+')', text)
        text = re.sub(r'(?<!!)\[([^\]]*)\]\(([^\s)]+)\)', lambda m: '['+m[1]+']('+link(m[2], source)+')', text)
        text = re.sub(r'href="([^"]+)"', lambda m: 'href="'+link(m[1], source)+'"', text)
        group = slug.split('/')[0] if '/' in slug else 'getting-started'
        dest = mapping[source]
        # Branch bundles preserve nested chapter URLs; images are shared Hugo assets.
        front = {'title': 'Manual' if slug == 'readme.md' else title, 'linkTitle': 'Manual' if slug == 'readme.md' else title,
                 'layout': 'manual', 'weight': order+1, 'manual_group': group,
                 'description': 'Lead-DBS user guide: '+title+'.', 'source_url': source.removesuffix('.md'),
                 'manual_title': title}
        chapters.append((dest, '---\n'+json.dumps(front, ensure_ascii=False, indent=2)+'\n---\n\n'+text+'\n'))
        pages.append({'title': title, 'page': dest, 'group': group, 'depth': max(0, slug.count('/')-1)})
    return chapters, pages, assets


def navigation(pages):
    """data/manual.json: the chapters grouped and nested as the manual's sidebar shows them."""
    nodes = {e['page']: dict(e, children=[]) for e in pages}
    groups = []
    for key, title in GROUPS.items():
        group = {'id': key, 'title': title, 'chapters': []}
        for entry in pages:
            if entry['group'] != key: continue
            parent = entry['page'].rstrip('/').rsplit('/', 1)[0]+'/'
            if parent in nodes and parent != '/manual/':
                nodes[parent]['children'].append(nodes[entry['page']])
            else:
                group['chapters'].append(nodes[entry['page']])
        groups.append(group)
    return {'groups': groups, 'pages': pages}


def stage_import(stage, root, chapters, pages, assets):
    """Writes the complete import below stage: content/manual, the images missing from assets/manual, manual.json."""
    for dest, document in chapters:
        folder = contained(stage / 'content', dest.strip('/'))
        folder.mkdir(parents=True, exist_ok=True)
        (folder / '_index.md').write_text(document)
    images = stage / 'assets'
    images.mkdir()
    missing = {url: name for url, name in assets.items() if not (root / 'assets' / 'manual' / name).exists()}

    def download(item):
        url, name = item
        contained(images, name).write_bytes(fetch(url))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(download, missing.items()))
    for url, name in missing.items():
        if (images / name).stat().st_size == 0:
            raise ImportRefused(f'empty image: {url}')
    (stage / 'manual.json').write_text(json.dumps(navigation(pages), ensure_ascii=False, indent=2)+'\n')


def publish(stage, root):
    """Moves a complete staged import into the repository."""
    (root / 'assets' / 'manual').mkdir(parents=True, exist_ok=True)
    for image in (stage / 'assets').iterdir():
        image.replace(root / 'assets' / 'manual' / image.name)
    (root / 'content').mkdir(exist_ok=True)
    (stage / 'content' / 'manual').rename(root / 'content' / 'manual')
    (root / 'data').mkdir(exist_ok=True)
    (stage / 'manual.json').rename(root / 'data' / 'manual.json')


def import_manual(root, cache, plan=False):
    """Imports the manual into root (the repository), or with plan=True only reports what it would import."""
    for existing in (root / 'content' / 'manual', root / 'data' / 'manual.json'):
        if existing.exists():
            raise ImportRefused(f'{existing.relative_to(root)} already exists; refusing to overwrite editorial changes.')
    rows = read_index(cache, save=not plan)
    chapters, pages, assets = convert(rows, cache, save=not plan)
    if plan:
        for dest, _ in chapters:
            print(f'would write content{dest}_index.md')
        missing = [name for name in assets.values() if not (root / 'assets' / 'manual' / name).exists()]
        print(f'would download {len(missing)} of {len(assets)} images into assets/manual and write data/manual.json')
        return
    # Staged next to its destination, so that publishing is a rename on the same file system.
    stage = Path(tempfile.mkdtemp(prefix='.manual-import-', dir=root))
    try:
        stage_import(stage, root, chapters, pages, assets)
        publish(stage, root)
    finally:
        shutil.rmtree(stage, ignore_errors=True)
    print(f'Imported {len(pages)} chapters and {len(assets)} images.')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('cache', nargs='?', type=Path, default=DEFAULT_CACHE,
                        help=f'source cache directory (default {DEFAULT_CACHE})')
    parser.add_argument('--plan', action='store_true', help='report what would be imported; write nothing')
    args = parser.parse_args(argv)
    try:
        import_manual(ROOT, args.cache, plan=args.plan)
    except ImportRefused as error:
        raise SystemExit(f'refused: {error}')


if __name__ == '__main__': main()
