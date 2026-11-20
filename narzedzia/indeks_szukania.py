"""Build versioned search files alongside the reader's static catalogue."""
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path


def build_indexes(assets, catalog):
    groups = defaultdict(list)
    for entry in catalog:
        groups[entry['collection']].append(entry)
    for collection, entries in groups.items():
        polish, extra = {}, {}
        for entry in entries:
            slug = entry['slug']
            doc = json.loads((assets / 'teksty' / (slug + '.json')).read_bytes())
            if (doc['slug'], doc['collection']) != (slug, collection):
                raise ValueError('Niezgodny tekst w katalogu: ' + slug)
            polish[slug] = [[u['id'], u['pl']] for u in doc['units']]
            extra[slug] = {'pali': [u['pi'] for u in doc['units']], 'notes': doc['notes']}
        files = []
        for kind, data in [('pl', polish), ('extra', extra)]:
            raw = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode()
            name = f'idx-{collection.lower()}-{kind}-{sha256(raw).hexdigest()[:16]}.json'
            (assets / name).write_bytes(raw)
            files.append(name)
        for entry in entries:
            entry['searchFiles'] = files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets', type=Path)
    assets = parser.parse_args().assets
    path = assets / 'katalog.json'
    catalog = json.loads(path.read_bytes())
    build_indexes(assets, catalog)
    path.write_bytes(json.dumps(catalog, ensure_ascii=False).encode())
