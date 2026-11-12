#!/usr/bin/env python3
"""One-time GitBook import. Requires curl. Refuses to overwrite edited content.

Usage: python3 tools/import_manual.py [source-cache-directory]
The cache may contain the public .md exports and index.json (title/URL pairs).
"""
import concurrent.futures
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://netstim.gitbook.io/leaddbs/'
CACHE = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/lead-manual-source')
OUT = ROOT / 'content/manual'
GROUPS = {'getting-started': 'Getting started', 'lead-dbs': 'Single-patient analysis',
          'lead-group': 'Group analysis', 'connectomics': 'Connectomics',
          'lead-or': 'Lead-OR', 'appendix': 'Reference'}

def fetch(url):
    return subprocess.check_output(['curl', '-fLsS', '--retry', '3', '--max-time', '120', url])

def main():
    if OUT.exists():
        raise SystemExit('content/manual already exists; refusing to overwrite editorial changes.')
    CACHE.mkdir(parents=True, exist_ok=True)
    index = CACHE / 'index.json'
    if not index.exists():
        index.write_text(json.dumps(re.findall(r'^- \[(.*?)\]\((.*?)\)', fetch(BASE+'llms.txt').decode(), re.M)))
    rows = json.loads(index.read_text())
    mapping = {url: '/manual/' + ('' if url == BASE+'readme.md' else url.removeprefix(BASE).removesuffix('.md')+'/') for _, url in rows}
    assets = {}
    def image_url(url):
        url = html.unescape(url).replace('\\&', '&')
        ext = Path(unquote(urlsplit(url).path)).suffix.lower()
        if ext not in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp'}:
            raise ValueError('Unknown image format: '+url)
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
    pages = []
    for order, (title, source) in enumerate(rows):
        slug = source.removeprefix(BASE)
        cached = CACHE / slug
        if not cached.exists():
            cached.parent.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(fetch(source))
        text = cached.read_text()
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
        folder = ROOT / 'content' / dest.strip('/')
        folder.mkdir(parents=True, exist_ok=True)
        # Branch bundles preserve nested chapter URLs; images are shared Hugo assets.
        front = {'title': 'Manual' if slug == 'readme.md' else title, 'linkTitle': 'Manual' if slug == 'readme.md' else title,
                 'layout': 'manual', 'weight': order+1, 'manual_group': group,
                 'description': 'Lead-DBS user guide: '+title+'.', 'source_url': source.removesuffix('.md'),
                 'manual_title': title}
        (folder/'_index.md').write_text('---\n'+json.dumps(front, ensure_ascii=False, indent=2)+'\n---\n\n'+text+'\n')
        pages.append({'title': title, 'page': dest, 'group': group, 'depth': max(0, slug.count('/')-1)})
    def download(item):
        url, name = item
        p = ROOT/'assets/manual'/name
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists(): p.write_bytes(fetch(url))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(download, assets.items()))
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
    (ROOT/'data/manual.json').write_text(json.dumps({'groups': groups, 'pages': pages}, ensure_ascii=False, indent=2)+'\n')
    print(f'Imported {len(pages)} chapters and {len(assets)} images.')

if __name__ == '__main__': main()
