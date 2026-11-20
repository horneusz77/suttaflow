"""Verify a bounded K1 build. Run with the installed PDF Python runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import pdfplumber
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from sfe.markdown_product import inspect_html, check_text, check_k1, check_build_manifest, compact  # noqa: E402
from sfe.parallel_text import read_mapping, check_pairs, compose_pali_chars  # noqa: E402


def verify(build_path, style_path):
    build = json.loads(build_path.read_text(encoding='utf-8-sig'))
    check_build_manifest(build, Path(__file__).resolve().parent)
    html = Path(build['html']).read_text(encoding='utf-8')
    if '[^' in html:
        raise ValueError('unresolved Markdown footnote')
    data = inspect_html(html)
    check_k1(data)
    pairs = []
    if 'pali_map' in build:
        mapping, _, _ = read_mapping(Path(build['pali_map']), Path(__file__).resolve().parents[2])
        pairs = check_pairs(html, mapping)
    elif 'pali-source' in html:
        raise ValueError('parallel product has no pinned source map')
    for number, call in enumerate(data['calls'], 1):
        if call['id'] != f'fnref{number}' or call['target'] != f'fn{number}':
            raise ValueError('HTML footnote edge differs from VFM numbering')
    if data['note_ids'] != [f'fn{i}' for i in range(1, len(data['calls']) + 1)]:
        raise ValueError('footnotes missing, duplicated or reordered')
    if data['backlinks'] != [{'id': f'fn{i}', 'target': f'fnref{i}'} for i in range(1, len(data['calls']) + 1)]:
        raise ValueError('HTML backlink edges differ from their note/call identities')
    style = json.loads(style_path.read_text(encoding='utf-8'))
    pdf = Path(build['pdf'])
    reader = PdfReader(pdf)
    urls, fonts, destinations = set(), set(), set()
    calls = []
    backlinks = []
    for page_no, page in enumerate(reader.pages):
        for ref in page.get('/Annots', []):
            annotation = ref.get_object()
            if annotation.get('/Dest'):
                destination = str(annotation['/Dest'])
                if destination not in reader.named_destinations:
                    raise ValueError('broken PDF destination: ' + destination)
                destinations.add(destination.rsplit(':0023', 1)[-1])
                if re.search(r':0023fn\d+$', destination):
                    calls.append({'page': page_no, 'rect': [float(v) for v in annotation['/Rect']],
                                  'target': destination.rsplit(':0023', 1)[-1], 'destination': destination})
                if re.search(r':0023fnref\d+$', destination):
                    backlinks.append({'page': page_no, 'rect': [float(v) for v in annotation['/Rect']],
                                      'target': destination.rsplit(':0023', 1)[-1], 'destination': destination})
            uri = annotation.get('/A', {}).get('/URI')
            if uri:
                urls.add(str(uri))
        for ref in page['/Resources']['/Font'].values():
            font = ref.get_object()
            desc = font.get('/DescendantFonts', [font])[0].get_object().get('/FontDescriptor', {})
            if font['/Subtype'] == '/Type3' or '/ToUnicode' not in font or not ('/FontFile2' in desc or '/FontFile3' in desc):
                raise ValueError('font not embedded with Unicode map')
            fonts.add(str(font['/BaseFont']))
    if urls != set(data['urls']):
        raise ValueError('PDF links differ from converted source')
    if not {x for x in data['internal_targets'] if x.startswith(('fn', 'fnref'))} <= destinations:
        raise ValueError('missing PDF footnote link')
    calls.sort(key=lambda x: (x['page'], -x['rect'][3], x['rect'][0]))
    if [c['target'] for c in calls] != [c['target'] for c in data['calls']]:
        raise ValueError('PDF footnote edges differ from source call order')
    backlinks.sort(key=lambda x: (x['page'], -x['rect'][3], x['rect'][0]))
    if [c['target'] for c in backlinks] != [c['target'] for c in data['backlinks']]:
        raise ValueError('PDF backlink edges differ from source notes')
    with pdfplumber.open(pdf) as document:
        for links in (calls, backlinks):
            for number, link in enumerate(links, 1):
                page = document.pages[link['page']]
                x0, y0, x1, y1 = link['rect']
                glyphs = [c for c in page.chars if c['size'] < 10
                          and x0 <= (c['x0'] + c['x1']) / 2 <= x1
                          and y0 <= page.height - (c['top'] + c['bottom']) / 2 <= y1]
                if ''.join(c['text'] for c in sorted(glyphs, key=lambda c: c['x0'])).strip() != str(number):
                    raise ValueError('link rectangle misses the actual footnote number')
        for forward, backward in zip(calls, backlinks):
            for link, target in ((forward, backward), (backward, forward)):
                dest = reader.named_destinations[link['destination']]
                if (reader.get_destination_page_number(dest) != target['page']
                        or abs(float(dest.left) - target['rect'][0]) > 2
                        or abs(float(dest.top) - target['rect'][3]) > 3):
                    raise ValueError('named destination differs from corresponding note/call geometry')
        body, notes, all_text, page_texts = [], [], [], []
        body_chars = []
        for page in document.pages:
            if abs(page.width - 595.276) > 1 or abs(page.height - 841.89) > 1:
                raise ValueError('page is not A4')
            content_bottom = page.height - 56.2
            crop = page.crop((0, 50, page.width, content_bottom))
            chars = crop.chars
            if any(c['x0'] < 55 or c['x1'] > 540 or c['bottom'] > content_bottom for c in chars):
                raise ValueError('content outside K1 text box')
            page_texts.append(pdfplumber.utils.extract_text(compose_pali_chars(chars)) or '')
            all_text.append(page_texts[-1])
            current_body = [c for c in chars if c['size'] >= 9.99 and c['text'] != '●']
            body_chars.append(current_body)
            body.append(pdfplumber.utils.extract_text(compose_pali_chars(current_body)) or '')
            notes.append(crop.filter(lambda x: x.get('object_type') == 'char' and abs(x.get('size', 0) - 9.5) <= .04).extract_text() or '')
            footer = [c for c in page.chars if c['top'] > 780 and abs(c['size'] - 10.5) < .04]
            if ''.join(c['text'] for c in footer).strip() != str(page.page_number):
                raise ValueError('incorrect page footer')
        check_text(data['body'], ''.join(body))
        # Notes may span pages; their complete ordered text is still required.
        check_text(data['notes'], ''.join(notes))
        for expected, call in zip(data['calls'], calls):
            page_no = call['page']
            top = document.pages[page_no].height - call['rect'][3]
            before = ''.join(body[:page_no]) + ''.join(c['text'] for c in body_chars[page_no]
                if c['top'] + 9 < top or abs(c['top'] - top) <= 9 and c['x1'] <= call['rect'][0] + .5)
            if len(compact(before)) != expected['offset']:
                raise ValueError('footnote anchor moved within source text: ' + call['target'])
            dest = reader.named_destinations[call['destination']]
            dest_page = reader.get_destination_page_number(dest)
            note_top = document.pages[dest_page].height - float(dest.top)
            prefix = compact(document.pages[dest_page].filter(lambda c: c.get('object_type') == 'char'
                             and abs(c.get('size', 0) - 9.5) < .04
                             and c['top'] >= note_top - 2).extract_text() or '')
            note = data['notes'][int(call['target'][2:]) - 1]
            if not prefix.startswith(compact(note)[:60]):
                raise ValueError('footnote destination points to wrong note: ' + call['target'])
        for heading in ['Jak powstało to tłumaczenie', 'Metryka przekładu']:
            hits = [i for i, text in enumerate(page_texts) if compact(heading) in compact(text)]
            if len(hits) != 1 or not compact(page_texts[hits[0]]).startswith(compact(heading)):
                raise ValueError('required new page absent: ' + heading)
        for term in style['pali_terms']:
            pattern = r'(?i)(?<![^\W\d_])' + re.escape(term).replace(r'\ ', r'\s+') + r'(?!\w)'
            expected = sum(len(re.findall(pattern, block)) for block in data['body'] + data['notes'])
            expected -= sum(len(re.findall(pattern, pair['pali'])) for pair in pairs)
            hits = [hit for page in document.pages for hit in page.search(pattern)
                    if not all('ChivoMono' in c['fontname'] for c in hit['chars'] if c['text'].strip())]
            if not expected or len(hits) != expected or any('Italic' not in c['fontname'] for hit in hits for c in hit['chars'] if c['text'].strip()):
                raise ValueError('Pali occurrence missing or not italic: ' + term)
        for probe in style['roman_probes']:
            hits = [hit for page in document.pages for hit in page.search(re.escape(probe))]
            if not hits or any('Italic' in c['fontname'] for hit in hits for c in hit['chars'] if c['text'].strip()):
                raise ValueError('Polish explanation is not roman: ' + probe)
        if pairs:
            pali_chars = [c for page in document.pages for c in page.chars if 'ChivoMono' in c['fontname']]
            check_text([pair['pali'] for pair in pairs], ''.join(c['text'] for c in pali_chars))
            if not pali_chars or any(abs(c['size'] - 10.5) > .04 for c in pali_chars):
                raise ValueError('Pali font/size differs from bilingual layout')
    return {'status': 'TECHNICAL_ONLY_VISUAL_REVIEW_REQUIRED', 'pages': len(reader.pages),
            'body_blocks': len(data['body']), 'notes': len(data['notes']), 'urls': len(urls),
            'fonts': sorted(fonts), 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'build_sha256': hashlib.sha256(build_path.read_bytes()).hexdigest(),
            'style_checks_sha256': hashlib.sha256(style_path.read_bytes()).hexdigest(),
            'parallel_pairs': len(pairs),
            'limits': ['Converted HTML versus PDF; source conversion still requires author readback.',
                       'Curated term list is not a universal Pali detector.',
                       'No semantic review, delivery or publication approval.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('build', type=Path)
    parser.add_argument('style_checks', type=Path)
    args = parser.parse_args()
    result = verify(args.build, args.style_checks)
    args.build.with_suffix('.verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
