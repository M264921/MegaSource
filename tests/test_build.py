from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('builder', Path(__file__).resolve().parents[1] / 'build.py')
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def app(identifier='test.app', version='1'):
    return {'name': 'Fixture', 'bundleIdentifier': identifier, 'developerName': 'Fixture',
            'localizedDescription': 'Controlled test app', 'iconURL': 'https://example.org/icon.png',
            'appPermissions': {'entitlements': [], 'privacy': {}},
            'versions': [{'version': version, 'date': '2026-10-15', 'downloadURL': 'https://example.org/test.ipa', 'size': 42}]}


class BuildTests(unittest.TestCase):
    def test_two_sources_and_first_source_priority(self):
        first = app()
        first['versions'] += [deepcopy(first['versions'][0]), {**first['versions'][0], 'version': '0.9'}]
        sources = {'one': {'apps': [first]}, 'two': {'apps': [app(version='2'), app('other.app')]}}
        payload, report = builder.build_payload(['one', 'two'], loader=sources.__getitem__)
        self.assertEqual(len(payload['apps']), 2)
        self.assertEqual([v['version'] for v in payload['apps'][0]['versions']], ['1', '0.9'])
        self.assertEqual(report[1]['duplicates'], 1)
        self.assertNotIn('sources', payload)

    def test_legacy_version_is_normalized_without_fabricating_permissions(self):
        raw = app()
        raw.update(raw.pop('versions')[0])
        self.assertEqual(builder.normalize_app(raw)['versions'][0]['size'], 42)
        raw.pop('appPermissions')
        with self.assertRaisesRegex(ValueError, 'appPermissions'):
            builder.normalize_app(raw)

    def test_failed_sources_require_explicit_partial_and_all_failed_never_publish(self):
        def load(url):
            if url == 'bad':
                raise OSError('unavailable')
            return {'apps': [app()]}
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            builder.build_payload(['ok', 'bad'], loader=load)
        payload, report = builder.build_payload(['ok', 'bad'], loader=load, allow_partial=True)
        self.assertEqual(len(payload['apps']), 1)
        self.assertEqual(report[1]['error'], 'unavailable')
        with self.assertRaisesRegex(ValueError, 'No valid'):
            builder.build_payload(['bad'], loader=load, allow_partial=True)

    def test_invalid_dates_download_schemes_and_sizes_rejected(self):
        for key, value in [('date', 'bad'), ('downloadURL', 'file:///private'), ('size', True), ('size', -1)]:
            raw = app()
            raw['versions'][0][key] = value
            with self.assertRaises(ValueError):
                builder.normalize_app(raw)

    def test_write_preserves_original_if_serialization_fails(self):
        with tempfile.TemporaryDirectory(prefix='megasource-test-') as temp:
            output = Path(temp) / 'feed.json'
            output.write_text('original')
            with self.assertRaises(TypeError):
                builder.write_json(output, {'bad': object()})
            self.assertEqual(output.read_text(), 'original')
            self.assertEqual(list(Path(temp).glob('*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
