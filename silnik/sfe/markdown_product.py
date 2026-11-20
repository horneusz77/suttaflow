"""Bounded K1 HTML/text checks. They do not perform semantic or visual review."""
from __future__ import annotations

from html.parser import HTMLParser
import hashlib
from pathlib import Path
import re
import unicodedata


def compact(text: str) -> str:
    return ''.join(unicodedata.normalize('NFKC', text).replace('\u00ad', '').split())


def check_text(blocks: list[str], actual: str) -> None:
    expected = compact(''.join(blocks))
    if expected != compact(actual).replace('●', ''):
        raise ValueError('text differs: missing, added, truncated or reordered content')


def check_build_manifest(build: dict, assets: Path) -> None:
    required = [Path(build.get(k, '')) for k in ('source', 'html', 'pdf')]
    required += [assets / 'suttaflow.css'] + [assets / 'fonts' / name for name in (
        'Merriweather-Regular.ttf', 'Merriweather-Italic.ttf', 'Merriweather-Bold.ttf',
        'Merriweather-BoldItalic.ttf', 'OFL.txt')]
    if 'stylesheet' in build:
        if not isinstance(build['stylesheet'], str) or not build['stylesheet']:
            raise ValueError('invalid build stylesheet')
        required.append(Path(build['stylesheet']))
        if Path(build['stylesheet']).name == 'polski-pali-v2.css':
            required += [assets/name for name in ('polski-pali.css', 'odstepy-r4.css',
                         'fonts/ChivoMono-Regular.ttf', 'fonts/OFL-ChivoMono.txt')]
    if 'pali_map' in build:
        if any(not isinstance(build.get(key), str) or not build[key]
               for key in ('pali_map', 'translation_source')):
            raise ValueError('incomplete parallel build manifest')
        required += [Path(build[key]) for key in ('pali_map', 'translation_source')]
        required += [assets / name for name in ('polski-pali.css', 'odstepy-r4.css',
                                               'fonts/ChivoMono-Regular.ttf', 'fonts/OFL-ChivoMono.txt')]
    pins = build.get('hashes')
    if (not isinstance(pins, dict) or len(required) < 8
            or any(not isinstance(build.get(k), str) or not build[k] for k in ('source', 'html', 'pdf'))):
        raise ValueError('incomplete build manifest')
    normalized = {Path(file).resolve(): pin for file, pin in pins.items()}
    for path in required:
        pin = normalized.get(path.resolve())
        if not isinstance(pin, str) or not re.fullmatch('[0-9a-f]{64}', pin):
            raise ValueError('required build pin absent: ' + str(path))
        if not path.is_file() or not path.stat().st_size or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('changed or missing build input/output: ' + str(path))
    for path, pin in normalized.items():
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('declared build pin differs: ' + str(path))


class _Content(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.body: list[str] = []
        self.notes: list[str] = []
        self.ids: set[str] = set()
        self.targets: list[str] = []
        self.urls: set[str] = set()
        self.stack: list[tuple[str, bool]] = []
        self.parts: list[str] | None = None
        self.note = False
        self.in_body = False
        self.backlink = False
        self.noteref = False
        self.headings: list[tuple[str, str]] = []
        self.subtitles = 0
        self.calls: list[dict] = []
        self.note_ids: list[str] = []
        self.backlinks: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag in {'script', 'iframe', 'object', 'img', 'table', 'math', 'style'}:
            raise ValueError('unsupported element requires a separate proof: ' + tag)
        if tag == 'body':
            self.in_body = True
        if not self.in_body:
            return
        if attributes.get('id'):
            identifier = str(attributes['id'])
            if identifier in self.ids:
                raise ValueError('duplicate HTML anchor: ' + identifier)
            self.ids.add(identifier)
        href = attributes.get('href') or ''
        if href.startswith('#'):
            self.targets.append(href[1:])
        elif href.startswith(('https://', 'http://')):
            self.urls.add(href)
        if attributes.get('role') == 'doc-footnote':
            self.note = True
            self.note_ids.append(str(attributes.get('id') or ''))
        if attributes.get('role') == 'doc-backlink':
            self.backlink = True
            self.backlinks.append({'id': self.note_ids[-1] if self.note_ids else None, 'target': href[1:]})
        if attributes.get('role') == 'doc-noteref':
            self.noteref = True
            self.calls.append({'id': attributes.get('id'), 'target': href[1:],
                               'offset': len(compact(''.join(self.body) + ''.join(self.parts or [])))})
        if tag == 'p' and 'subtitle' in (attributes.get('class') or '').split():
            self.subtitles += 1
        is_block = (tag in {'h1', 'h2', 'h3', 'h4', 'p', 'li'}
                    or attributes.get('role') == 'doc-footnote') and self.parts is None
        if is_block:
            self.parts = []
        if tag == 'br' and self.parts is not None:
            self.parts.append(' ')
        if tag not in {'br', 'hr', 'meta', 'link', 'wbr', 'input'}:
            self.stack.append((tag, is_block))

    def handle_endtag(self, tag: str) -> None:
        if tag == 'body':
            self.in_body = False
        if not self.stack:
            return
        start, is_block = self.stack.pop()
        if start != tag:
            raise ValueError('unbalanced converted HTML: ' + tag)
        if is_block and self.parts is not None:
            text = ''.join(self.parts).strip()
            if text:
                (self.notes if self.note else self.body).append(text)
                if tag in {'h1', 'h2', 'h3', 'h4'}:
                    self.headings.append((tag, text))
            self.parts = None
        if tag == 'aside':
            self.note = False
        if tag == 'a':
            self.backlink = False
            self.noteref = False

    def handle_data(self, data: str) -> None:
        if self.backlink or self.noteref:
            return
        if self.parts is not None:
            self.parts.append(data)
        elif self.in_body and data.strip():
            raise ValueError('text outside supported blocks: ' + data[:80])


def inspect_html(text: str) -> dict:
    parser = _Content()
    parser.feed(text)
    parser.close()
    if (not parser.body or parser.parts is not None or parser.stack or parser.in_body
            or set(parser.targets) - parser.ids):
        raise ValueError('empty product, unclosed block or unresolved anchor')
    return {'body': parser.body, 'notes': parser.notes, 'urls': sorted(parser.urls),
            'internal_targets': parser.targets, 'headings': parser.headings, 'subtitles': parser.subtitles,
            'calls': parser.calls, 'note_ids': parser.note_ids, 'backlinks': parser.backlinks}


def check_k1(data: dict) -> None:
    required = ['Opis', 'Interpretacja', 'Przekład', 'Jak powstało to tłumaczenie',
                'Paralele kanoniczne', 'Źródła']
    headings = data['headings']
    if ([text for tag, text in headings if tag == 'h2'] != required
            or sum(tag == 'h1' for tag, _ in headings) != 1
            or data['subtitles'] != 1
            or ('h3', 'Decyzje tłumaczeniowe') not in headings
            or ('h3', 'Metryka przekładu') not in headings):
        raise ValueError('K1 semantic heading/subtitle roles differ')
