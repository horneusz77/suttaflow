"""Exact UTF-8 component / native UTF-16 binding, not visual or language QA.

The authenticated FORMAT report owns this map. Unsupported native structures
fail closed; a new K1 variant needs its own approved contract, not a relaxed flag.
"""
from __future__ import annotations

from . import release_evidence as RE

K1 = (
    ('TITLE', None, False, 'OTHER_PUBLIC'),
    ('SUBTITLE', None, False, 'OTHER_PUBLIC'),
    ('HEADING_2', 'Opis', False, 'DESCRIPTION'),
    ('HEADING_2', 'Interpretacja', False, 'INTERPRETATION'),
    ('HEADING_2', 'Przekład', False, 'CORE'),
    ('HEADING_2', 'Jak powstało to tłumaczenie', True, 'METHOD'),
    ('HEADING_3', 'Decyzje tłumaczeniowe', False, 'TRANSLATION_DECISIONS'),
    ('HEADING_2', 'Paralele kanoniczne', False, 'PARALLEL'),
    ('HEADING_2', 'Źródła', False, 'OTHER_PUBLIC'),
    ('HEADING_3', 'Metryka przekładu', True, 'METRICS'),
    ('HEADING_4', 'Dokumentacja pracy', False, 'METRICS'),
    ('HEADING_4', 'Historia rewizji', False, 'OTHER_PUBLIC'),
)


def _need(value, message):
    if not value:
        raise RE.EvidenceError('native product: ' + message)


def _record(value, keys):
    _need(isinstance(value, dict) and set(value) == set(keys), 'missing or unknown mapping fields')
    return value


def _pending(value):
    if isinstance(value, dict):
        return any((k.startswith('suggested') and bool(v)) or _pending(v) for k, v in value.items())
    return isinstance(value, list) and any(_pending(v) for v in value)


def _tab(doc, tab_id):
    tabs = {}

    def visit(items):
        _need(isinstance(items, list), 'malformed tabs')
        for item in items:
            _need(isinstance(item, dict), 'malformed tab')
            props = item.get('tabProperties', item)
            tab = item.get('documentTab', item)
            _need(isinstance(props, dict) and isinstance(tab, dict), 'malformed tab properties')
            tid = props.get('tabId')
            _need(RE.nonempty(tid) and tid not in tabs, 'absent or duplicate tab ID')
            tabs[tid] = tab
            if item.get('childTabs'):
                visit(item['childTabs'])

    if doc.get('tabs'):
        visit(doc['tabs'])
        _need(RE.nonempty(tab_id) and tab_id in tabs, 'exact mapped tab absent')
        return tabs[tab_id]
    _need(tab_id is None, 'legacy body cannot prove a named tab')
    return doc


def _tokens(tab):
    _need(not _pending(tab), 'unresolved suggestions')
    _need(tab.get('documentStyle', {}).get('documentFormat', {}).get('documentMode') == 'PAGES',
          'native PAGES mode not proved')
    _need(not tab.get('inlineObjects') and not tab.get('positionedObjects'),
          'unsupported native media/positioned objects')
    for field in ('headers', 'footers'):
        surfaces = tab.get(field, {})
        if surfaces is None:
            surfaces = {}
        _need(isinstance(surfaces, dict), 'malformed header/footer collection')
        for surface in surfaces.values():
            for item in surface.get('content', []):
                _need(isinstance(item.get('paragraph'), dict), 'unsupported header/footer content')
                for element in item['paragraph'].get('elements', []):
                    _need((set(element) <= {'startIndex', 'endIndex', 'textRun'} and
                           element.get('textRun', {}).get('content') in ('\n', ' ')) or
                          (set(element) <= {'startIndex', 'endIndex', 'autoText'} and
                           element.get('autoText', {}).get('type') == 'PAGE_NUMBER'),
                          'unreviewed header/footer text or object')
    named = {}
    for style in tab.get('namedStyles', {}).get('styles', []):
        role = style.get('namedStyleType')
        _need(RE.nonempty(role) and role not in named, 'invalid or duplicate named style')
        named[role] = style.get('paragraphStyle', {})
    tokens, references = {}, {}
    headings: list[tuple[str, str]] = []

    def paragraphs(content, segment, initial):
        _need(isinstance(content, list) and content, 'empty native segment')
        position, region = initial, 'FOOTNOTE' if segment is not None else 'OTHER_PUBLIC'
        for item in content:
            _need(isinstance(item, dict), 'malformed native content')
            if 'sectionBreak' in item:
                _need(segment is None and position == 0 and item.get('endIndex') == 1,
                      'unsupported section break')
                position = 1
                continue
            para = item.get('paragraph')
            _need(isinstance(para, dict), 'unsupported native element (not a paragraph)')
            _need(not para.get('positionedObjectIds'), 'unsupported positioned object anchor')
            _need(set(item) <= {'startIndex', 'endIndex', 'paragraph'} and
                  type(item.get('startIndex', 0)) is int and item.get('startIndex', 0) == position,
                  'paragraph index gap, overlap or order')
            style = para.get('paragraphStyle', {})
            _need(isinstance(style, dict), 'malformed paragraph style')
            role = style.get('namedStyleType', 'NORMAL_TEXT')
            fixed = False
            if segment is None and role != 'NORMAL_TEXT':
                _need(len(headings) < len(K1), 'extra heading')
                expected, label, page_break, region = K1[len(headings)]
                _need(role == expected, 'K1 heading role/order differs')
                effective = style.get('pageBreakBefore', named.get(role, {}).get('pageBreakBefore', False))
                _need(type(effective) is bool and effective == page_break, 'K1 pageBreakBefore differs')
                text = ''.join(e.get('textRun', {}).get('content', '') for e in para.get('elements', []))
                _need(text.endswith('\n') and (text[:-1] == label if label else bool(text[:-1].strip())),
                      'K1 heading label absent or changed')
                headings.append((role, text[:-1]))
                fixed = label is not None
            elif segment is not None:
                _need(role == 'NORMAL_TEXT', 'a footnote cannot contain K1 headings')
            elements = para.get('elements')
            _need(isinstance(elements, list) and elements, 'empty native paragraph')
            for element in elements:
                _need(isinstance(element, dict) and type(element.get('startIndex', position)) is int and
                      element.get('startIndex', position) == position,
                      'element indices differ')
                kinds = [k for k in ('textRun', 'footnoteReference', 'dateElement', 'richLink') if k in element]
                _need(len(kinds) == 1 and set(element) <= {'startIndex', 'endIndex', *kinds},
                      'unsupported or ambiguous native inline element')
                _need(not fixed or kinds == ['textRun'], 'fixed K1 heading has an inline object')
                kind = kinds[0]
                value = element[kind]
                _need(isinstance(value, dict), 'malformed inline value')
                if kind == 'textRun':
                    text = value.get('content')
                    _need(isinstance(text, str) and bool(text), 'empty native text run')
                    for char in text:
                        end = position + len(char.encode('utf-16-le')) // 2
                        tokens[(segment, position, end)] = (char, region, fixed)
                        position = end
                else:
                    end = position + 1
                    if kind == 'footnoteReference':
                        fid = value.get('footnoteId')
                        _need(segment is None and RE.nonempty(fid), 'invalid or nested footnote reference')
                        _need(fid not in references, 'duplicate footnote reference')
                        references[fid] = (segment, position, end)
                        text = ''
                    elif kind == 'dateElement':
                        props = value.get('dateElementProperties', {})
                        _need(RE.nonempty(value.get('dateId')), 'date identity absent')
                        text = props.get('displayText')
                    else:
                        text = value.get('richLinkProperties', {}).get('title')
                    _need(isinstance(text, str) and (kind == 'footnoteReference' or bool(text)),
                          'inline display text absent')
                    tokens[(segment, position, end)] = (text, region, fixed)
                    position = end
                _need(type(element.get('endIndex', position)) is int and
                      element.get('endIndex', position) == position, 'inline UTF-16 length differs')
            _need(type(item.get('endIndex')) is int and item['endIndex'] == position,
                  'paragraph UTF-16 length differs')
            _need(tokens.get((segment, position - 1, position), (None,))[0] == '\n',
                  'paragraph terminator absent')

    body = tab.get('body')
    _need(isinstance(body, dict), 'native body absent')
    paragraphs(body.get('content'), None, 0 if body.get('content', [{}])[0].get('startIndex', 0) == 0 else 1)
    _need(len(headings) == len(K1), 'incomplete K1 structure')
    notes = tab.get('footnotes', {})
    if notes is None:
        notes = {}
    _need(isinstance(notes, dict) and len(references) == len(set(references)) and
          set(references) == set(notes), 'missing, unused or duplicate footnote/reference')
    for fid, note in notes.items():
        _need(isinstance(note, dict) and note.get('footnoteId') == fid, 'footnote ID differs')
        paragraphs(note.get('content'), fid, 0)
    return tokens, headings, references


def validate(root, report, bundle):
    """Check the pinned native product after the caller verifies its reviews."""
    try:
        return _validate(root, report, bundle)
    except RE.EvidenceError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError, IndexError, RecursionError) as exc:
        raise RE.EvidenceError('native product: malformed mapping or native resource: ' + str(exc)) from exc


def _validate(root, report, bundle):
    """Raise EvidenceError for any gap; reports/claim ledger are verified by caller."""
    binding = _record(report.get('native_product'), ('schema', 'artifact', 'tab_id', 'components',
                                                    'claim_ledger', 'pieces', 'footnote_anchors'))
    _need(binding['schema'] == 'suttaflow-native-product-v1', 'unknown binding schema')
    _need(binding['artifact'] == report.get('artifact'), 'map pins another native artifact')
    components = {key: bundle.get(key) for key in ('core', 'apparatus', 'interpretation')}
    _need(binding['components'] == components and binding['claim_ledger'] == bundle.get('claim_ledger'),
          'map pins other reviewed components or claim ledger')
    raw = {key: RE.read_artifact(root, ref) for key, ref in components.items()}
    ledger = RE.read_artifact(root, binding['claim_ledger'], json_object=True)
    _need(ledger.get('components') == components, 'claim inventory components differ')
    inventory = ledger.get('inventory')
    _need(isinstance(inventory, list) and all(isinstance(r, dict) for r in inventory), 'claim inventory absent')
    metadata = RE.read_artifact(root, bundle.get('publication_metadata'), json_object=True)
    _need(metadata.get('native', {}).get('tab_id') == binding['tab_id'], 'metadata and map select different tabs')
    doc = RE.read_artifact(root, report['artifact'], json_object=True)
    _need(doc.get('documentId') == report.get('document_id') and
          doc.get('revisionId') == report.get('document_revision_id'), 'native identity/revision differs')
    tokens, headings, notes = _tokens(_tab(doc, binding['tab_id']))
    anchors = binding['footnote_anchors']
    _need(isinstance(anchors, list), 'footnote anchor map absent')
    expected_anchors = {}
    for anchor in anchors:
        _record(anchor, ('footnote_id', 'component', 'byte_offset'))
        fid, component, offset = anchor['footnote_id'], anchor['component'], anchor['byte_offset']
        _need(RE.nonempty(fid) and fid in notes and fid not in expected_anchors and
              isinstance(component, str) and component in raw and type(offset) is int and
              0 <= offset <= len(raw[component]), 'invalid or duplicate footnote anchor')
        expected_anchors[fid] = (component, offset)
    anchor_keys = {key: fid for fid, key in notes.items()}
    observed_anchors = {}
    segments: dict[str | None, list] = {}
    for key, value in tokens.items():
        segments.setdefault(key[0], []).append((key, value))
    starts = {segment: {key[1]: i for i, (key, _) in enumerate(values)}
              for segment, values in segments.items()}
    ends = {segment: {key[2]: i + 1 for i, (key, _) in enumerate(values)}
            for segment, values in segments.items()}
    pieces = binding['pieces']
    _need(isinstance(pieces, list) and pieces, 'component map absent')
    source_ranges: dict[str, list[tuple[int, int]]] = {key: [] for key in components}
    used = set()
    placements: dict[tuple, list] = {}
    for piece in pieces:
        _record(piece, ('component', 'byte_range', 'native_ranges'))
        component = piece['component']
        _need(isinstance(component, str) and component in raw, 'unknown component')
        interval = piece['byte_range']
        _need(isinstance(interval, list) and len(interval) == 2 and all(type(n) is int for n in interval),
              'invalid UTF-8 interval')
        a, b = interval
        _need(0 <= a < b <= len(raw[component]), 'source interval out of bounds')
        expected = raw[component][a:b].decode('utf-8')
        source_ranges[component].append((a, b))
        if component == 'core':
            role = 'CORE'
            region_id = ('core', 0, len(raw[component]))
        else:
            regions = [r for r in inventory if r.get('component') == component and
                       r.get('byte_range', [b, a])[0] <= a and b <= r.get('byte_range', [b, a])[1]]
            _need(len(regions) == 1, 'piece crosses or omits a reviewed claim region')
            role = regions[0].get('role')
            region_id = (component, *regions[0]['byte_range'])
        ranges = piece['native_ranges']
        _need(isinstance(ranges, list) and ranges, 'native intervals absent')
        actual: list[str] = []
        placement = []
        for span in ranges:
            _record(span, ('segment_id', 'range'))
            segment, interval = span['segment_id'], span['range']
            _need(segment is None or isinstance(segment, str), 'invalid native segment')
            _need(isinstance(interval, list) and len(interval) == 2 and all(type(n) is int for n in interval),
                  'invalid UTF-16 interval')
            start, end = interval
            _need(segment in segments and start in starts[segment] and end in ends[segment],
                  'native interval absent or splits a UTF-16 unit')
            selected = segments[segment][starts[segment][start]:ends[segment][end]]
            _need(selected and selected[0][0][1] == start and selected[-1][0][2] == end and
                  all(left[0][2] == right[0][1] for left, right in zip(selected, selected[1:])),
                  'native interval absent, discontinuous or splits a UTF-16 unit')
            placement.append((segment, start, end))
            for key, (text, region, fixed) in selected:
                _need(key not in used, 'native text mapped more than once')
                _need(not fixed or component != 'core', 'CORE cannot be supplied by structural headings')
                _need(region == role or not text.strip(), 'text is in the wrong native section')
                if key in anchor_keys:
                    observed_anchors[anchor_keys[key]] = (component, a + len(''.join(actual).encode('utf-8')))
                used.add(key)
                actual.append(text)
        _need(''.join(actual) == expected, 'actual native text differs from reviewed bytes')
        placements.setdefault(region_id, []).append((a, placement))
    for component, intervals in source_ranges.items():
        end = 0
        for a, b in sorted(intervals):
            _need(a == end, 'source bytes missing, duplicated or overlapping')
            end = b
        _need(end == len(raw[component]), 'reviewed component not completely mapped')
    for region_pieces in placements.values():
        ordered = [span for _, spans in sorted(region_pieces) for span in spans]
        _need(all(left[0] == right[0] and left[2] <= right[1]
                  for left, right in zip(ordered, ordered[1:])),
              'reviewed text order differs within a native region')
    _need(all(key in used or fixed or text in ('', '\n') for key, (text, _, fixed) in tokens.items()),
          'native text is absent from the reviewed components')
    _need(set(notes) == set(expected_anchors) and expected_anchors == observed_anchors,
          'footnote reference differs from reviewed component anchor')
    _need(set(notes) == {key[0] for key in used if key[0] is not None and tokens[key][0].strip()},
          'footnote has no reviewed nonempty content')
    return {'schema': binding['schema'], 'tab_id': binding['tab_id'], 'headings': len(headings),
            'footnotes': len(notes), 'pieces': len(pieces), 'structural_only': True}
