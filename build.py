#!/usr/bin/env python3
"""Aggregate AltStore Classic feeds without downloading application binaries."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_BYTES = 16 * 1024 * 1024
APP_KEYS = {'name', 'bundleIdentifier', 'developerName', 'localizedDescription', 'iconURL',
            'subtitle', 'tintColor', 'category', 'screenshots', 'versions', 'appPermissions', 'patreon'}
VERSION_KEYS = {'version', 'buildVersion', 'marketingVersion', 'date', 'downloadURL', 'size',
                'minOSVersion', 'maxOSVersion', 'localizedDescription'}


def http_url(value):
    if not isinstance(value, str):
        return False
    try:
        url = urlparse(value)
        return url.scheme in {'https', 'http'} and bool(url.hostname) and not url.username and not url.password
    except ValueError:
        return False


def fetch_json(url, timeout=15):
    if not http_url(url):
        raise ValueError('Source must be an HTTP(S) URL without credentials')
    request = Request(url, headers={'User-Agent': 'MegaSource/1.0', 'Accept': 'application/json'})
    with urlopen(request, timeout=timeout) as response:
        if not http_url(response.geturl()):
            raise ValueError('Unsupported redirect')
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError('Source exceeds 16 MiB')
    data = json.loads(body.decode('utf-8-sig'))
    if not isinstance(data, dict) or not isinstance(data.get('apps'), list):
        raise ValueError('Source must contain an apps array')
    return data


def normalize_app(raw):
    if not isinstance(raw, dict):
        raise ValueError('App is not an object')
    for field in ('name', 'bundleIdentifier', 'developerName', 'localizedDescription'):
        if not isinstance(raw.get(field), str) or not raw[field].strip():
            raise ValueError('Missing app ' + field)
    if not http_url(raw.get('iconURL')):
        raise ValueError('Invalid app iconURL')
    versions = raw.get('versions')
    if versions is None and raw.get('version'):
        versions = [{key: raw[key] for key in VERSION_KEYS if key in raw}]
    if not isinstance(versions, list) or not versions:
        raise ValueError('Missing versions')
    valid, seen = [], set()
    for value in versions:
        if not isinstance(value, dict):
            raise ValueError('Invalid version object')
        if not isinstance(value.get('version'), str) or not value['version']:
            raise ValueError('Missing version number')
        if not isinstance(value.get('date'), str):
            raise ValueError('Missing version date')
        datetime.fromisoformat(value['date'].replace('Z', '+00:00'))
        if not http_url(value.get('downloadURL')) or type(value.get('size')) is not int or value['size'] < 0:
            raise ValueError('Invalid download URL or size')
        key = (value['version'], str(value.get('buildVersion', '')))
        if key not in seen:
            valid.append({key: deepcopy(item) for key, item in value.items() if key in VERSION_KEYS})
            seen.add(key)
    result = {key: deepcopy(value) for key, value in raw.items() if key in APP_KEYS}
    result['versions'] = valid
    # Never fabricate permissions; AltStore checks these against each IPA.
    if not isinstance(result.get('appPermissions'), dict):
        raise ValueError('Missing appPermissions; upstream must declare permissions')
    return result


def build_payload(urls, *, loader=fetch_json, allow_partial=False):
    urls = list(dict.fromkeys(url.strip() for url in urls if url.strip() and not url.lstrip().startswith('#')))
    if not urls:
        raise ValueError('No sources configured')

    def load(url):
        try:
            data = loader(url)
            if not isinstance(data, dict) or not isinstance(data.get('apps'), list):
                raise ValueError('Missing apps array')
            return data, None
        except Exception as exc:
            return None, str(exc)

    apps, report = {}, []
    with ThreadPoolExecutor(max_workers=5) as pool:
        # map preserves source priority, regardless of download completion order.
        for url, (data, error) in zip(urls, pool.map(load, urls)):
            entry = {'url': url, 'accepted': 0, 'duplicates': 0, 'rejected': 0, 'rejectionReasons': {}}
            if error:
                entry['error'] = error
                report.append(entry)
                continue
            for raw in data['apps']:
                try:
                    app = normalize_app(raw)
                except (TypeError, ValueError) as exc:
                    entry['rejected'] += 1
                    reason = str(exc)
                    entry['rejectionReasons'][reason] = entry['rejectionReasons'].get(reason, 0) + 1
                    continue
                identifier = app['bundleIdentifier']
                if identifier in apps:
                    entry['duplicates'] += 1
                else:
                    apps[identifier] = app
                    entry['accepted'] += 1
            report.append(entry)
    if not apps:
        raise ValueError('No valid applications; previous output preserved')
    if not allow_partial and any(entry.get('error') or entry['rejected'] for entry in report):
        raise ValueError('Incomplete source data; review sources or use --allow-partial explicitly. ' + json.dumps(report))
    return {'name': 'MegaSource', 'identifier': 'megasource.toninomontana',
            'subtitle': 'Fuentes agregadas de AltStore Classic',
            'website': 'https://github.com/M264921/MegaSource',
            'apps': list(apps.values()), 'news': []}, report


def write_json(path, data):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, prefix=path.name + '.', suffix='.tmp',
                                         encoding='utf-8', newline='\n', delete=False) as handle:
            temp = Path(handle.name)
            json.dump(data, handle, indent=2, ensure_ascii=False)
            handle.write('\n')
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path(__file__).with_name('sources.txt'))
    parser.add_argument('-o', '--output', type=Path, default=Path(__file__).with_name('MegaSource.json'))
    parser.add_argument('--report', type=Path, default=Path(__file__).with_name('build-report.json'))
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    payload, report = build_payload(args.sources.read_text(encoding='utf-8-sig').splitlines(), allow_partial=args.allow_partial)
    if args.dry_run:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        write_json(args.output, payload)
        write_json(args.report, report)
        print(f'Wrote {len(payload["apps"])} apps; source details: {args.report}')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
