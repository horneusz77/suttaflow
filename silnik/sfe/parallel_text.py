"""Render checked translation/source pairs; never infer alignment from punctuation."""
from __future__ import annotations

import argparse
import hashlib
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import unicodedata

from sfe.markdown_product import compact


def compose_pali_chars(chars: list[dict]) -> list[dict]:
    """Join zero-advance marks before geometry sorting can place them before their base."""
    result = []
    for char in chars:
        text = char['text']
        if len(text) == 1 and unicodedata.combining(text) and 'ChivoMono' in char['fontname']:
            if (not result or result[-1]['fontname'] != char['fontname']
                    or abs(char['width']) > .01
                    or abs(result[-1]['top'] - char['top']) > .5
                    or not result[-1]['x0'] - 1 <= char['x0'] <= result[-1]['x1'] + 1):
                raise ValueError('unattached Pali combining mark')
            result[-1] = {**result[-1], 'text': unicodedata.normalize('NFC', result[-1]['text'] + text)}
        else:
            result.append(char)
    return result


def read_mapping(path: Path, root: Path) -> tuple[dict, str, str]:
    mapping = json.loads(path.read_text(encoding='utf-8'))
    texts = []
    for key in ('source', 'candidate'):
        pin = mapping[key]
        raw = (root / pin['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest() != pin['sha256']:
            raise ValueError('stale parallel input: ' + key)
        texts.append(raw.decode('utf-8'))
    units = mapping['units']
    if not units or len({u['id'] for u in units}) != len(units):
        raise ValueError('empty or duplicate parallel scope')
    ends = [0, 0]
    for unit in units:
        for i, key in enumerate(('source', 'candidate')):
            start, end = unit[key + '_span']
            if (not isinstance(start, int) or not isinstance(end, int)
                    or not 0 <= ends[i] <= start < end <= len(texts[i])
                    or not unit[key + '_text'].strip()
                    or texts[i][start:end] != unit[key + '_text']):
                raise ValueError('invalid parallel anchor: ' + unit['id'])
            if i == 0 and texts[0][ends[0]:start].strip():
                raise ValueError('invalid parallel anchor; unmapped source before: ' + unit['id'])
            ends[i] = end
    if texts[0][ends[0]:].strip():
        raise ValueError('unmapped source tail')
    return mapping, texts[0], texts[1]


def render(mapping: dict, markdown: str) -> str:
    start = markdown.index('\n', markdown.index('## Przekład')) + 1
    stops = [markdown.find(marker, start) for marker in ('\n[^', '\n## Jak powstało')]
    end = min((stop for stop in stops if stop >= 0), default=len(markdown))
    cursor, blocks = start, []
    for unit in mapping['units']:
        a, b = unit['candidate_span']
        if a < cursor or b > end or markdown[cursor:a].strip():
            raise ValueError('unmapped translation or overlapping note: ' + unit['id'])
        # Calls immediately following a clause belong to that Polish clause.
        calls = re.match(r'(?:\[\^[^\]\n]+\])*', markdown[b:]).group()
        polish = markdown[a:b] + calls
        pali = escape(unit['source_text'].strip())
        identifier = escape(unit['id'], quote=True)
        blocks.append(f'<div class="parallel-unit" data-source-id="{identifier}">\n\n'
                      f'{polish}\n\n<p class="pali-source" lang="pi">{pali}</p>\n\n</div>')
        cursor = b + len(calls)
    if markdown[cursor:end].strip():
        raise ValueError('unmapped translation tail')
    return markdown[:start] + '\n' + '\n\n'.join(blocks) + '\n' + markdown[end:]


class Pairs(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pairs = []
        self.depth = 0
        self.current = None
        self.pali_depth = None
        self.ignore_depth = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'br', 'hr', 'meta', 'link', 'wbr', 'input'}:
            return
        self.depth += 1
        if 'parallel-unit' in attrs.get('class', '').split():
            if self.current or tag != 'div' or not attrs.get('data-source-id'):
                raise ValueError('invalid parallel wrapper')
            self.current = {'id': attrs['data-source-id'], 'pl': [], 'pali': [], 'depth': self.depth}
        if 'pali-source' in attrs.get('class', '').split():
            if (not self.current or self.current['pali'] or tag != 'p' or attrs.get('lang') != 'pi'
                    or not ''.join(self.current['pl']).strip()):
                raise ValueError('invalid or duplicate Pali block')
            self.pali_depth = self.depth
        if self.current and attrs.get('role') == 'doc-noteref':
            self.ignore_depth = self.depth

    def handle_data(self, text):
        if self.current and self.ignore_depth is None:
            if self.pali_depth is None and self.current['pali'] and text.strip():
                raise ValueError('Polish text after the Pali block')
            self.current['pali' if self.pali_depth is not None else 'pl'].append(text)

    def handle_endtag(self, tag):
        if self.pali_depth == self.depth:
            self.pali_depth = None
        if self.ignore_depth == self.depth:
            self.ignore_depth = None
        if self.current and self.current['depth'] == self.depth:
            pair = self.current
            if not ''.join(pair['pl']).strip() or not ''.join(pair['pali']).strip():
                raise ValueError('incomplete language pair')
            self.pairs.append({k: ''.join(pair[k]).strip() if k != 'id' else pair[k]
                               for k in ('id', 'pl', 'pali')})
            self.current = None
        self.depth -= 1


def plain_polish(text: str) -> str:
    text = re.sub(r'\[\^[^]]+\]', '', text)
    text = re.sub(r'<[^>]+>', '', text)
    return text.replace('*', '')


def check_pairs(html: str, mapping: dict) -> list[dict]:
    parser = Pairs()
    parser.feed(html)
    if parser.current is not None:
        raise ValueError('unclosed parallel pair')
    pairs = parser.pairs
    if [p['id'] for p in pairs] != [u['id'] for u in mapping['units']]:
        raise ValueError('parallel scope/order differs')
    for pair, unit in zip(pairs, mapping['units']):
        if (compact(pair['pali']) != compact(unit['source_text'])
                or compact(pair['pl']) != compact(plain_polish(unit['candidate_text']))):
            raise ValueError('parallel text differs: ' + pair['id'])
    return pairs


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('mapping', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    mapping, _, markdown = read_mapping(args.mapping, root)
    if args.source.resolve() != (root / mapping['candidate']['path']).resolve():
        raise ValueError('mapping belongs to another translation')
    result = render(mapping, markdown)
    with args.output.open('xb') as output:
        output.write(result.encode('utf-8'))
