"""Byte checks for editorial inputs; no language or visual certification.

The target manifest accounts for every non-whitespace UTF-8 byte of CORE.
PDF inspection supports unencrypted exports with classic cross-reference tables
and explicit page objects (including classic incremental updates). Unsupported
PDF structures require another verified export and return HOLD, never PASS.
The original native/PDF reviewer reports remain separately mandatory.
"""
from __future__ import annotations
import re
from . import release_evidence as RE


def target_units(root, subject, core_subject):
    bundle = RE.read_artifact(root, subject['content'], json_object=True)
    m = RE.read_artifact(root, bundle.get('target_unit_manifest'), json_object=True)
    if m.get('schema') != 'suttaflow-target-units-v2' or m.get('encoding') != 'UTF-8':
        raise RE.EvidenceError('versioned target unit manifest absent')
    if any(m.get(k) != subject[k] for k in ('subject_id', 'revision_id')) or m.get('content') != core_subject['content']:
        raise RE.EvidenceError('target unit manifest identifies another CORE or revision')
    raw = RE.read_artifact(root, m['content'])
    entries = m.get('units')
    if not isinstance(entries, list) or not entries or not all(isinstance(u, dict) for u in entries):
        raise RE.EvidenceError('target units absent')
    ids = RE.scope([u.get('id') for u in entries])
    end = 0
    try:
        raw.decode('utf-8')
        for unit in entries:
            span = unit.get('byte_range')
            if not isinstance(span, list) or len(span) != 2 or any(type(n) is not int for n in span):
                raise RE.EvidenceError('target unit byte range malformed')
            start, stop = span
            if not end <= start < stop <= len(raw):
                raise RE.EvidenceError('target unit ranges overlap, are reversed or exceed CORE')
            if raw[end:start].decode('utf-8').strip() or not raw[start:stop].decode('utf-8').strip():
                raise RE.EvidenceError('target manifest omits text or contains an empty unit')
            end = stop
        if raw[end:].decode('utf-8').strip():
            raise RE.EvidenceError('target manifest omits final CORE text')
    except UnicodeError as exc:
        raise RE.EvidenceError('CORE or target range boundary is not valid UTF-8') from exc
    return ids


def pdf_page_count(raw):
    try:
        return _classic_pdf_page_count(raw)
    except RE.EvidenceError:
        raise
    except (ValueError, OverflowError) as exc:
        raise RE.EvidenceError('PDF numeric field is invalid or exceeds the supported reader limit') from exc


def _classic_pdf_page_count(raw):
    """Check the export's xref, catalog and page tree; return actual page count.

This is a deliberately bounded structural reader, not a full PDF renderer or
syntax certification. Object streams, encrypted documents and xref streams
are unsupported here and fail closed with an actionable diagnostic.
"""
    if not isinstance(raw, bytes) or re.match(rb'%PDF-(?:1\.[0-9]|2\.0)[\r\n]', raw) is None:
        raise RE.EvidenceError('artifact does not have a valid PDF header')
    trailer_end = re.search(rb'startxref\s+(\d+)\s+%%EOF\s*\Z', raw)
    if trailer_end is None:
        raise RE.EvidenceError('PDF is truncated or lacks a final startxref/EOF')
    objects = {}; visited = set(); root_ref = None
    offset: int | None = int(trailer_end.group(1))
    while offset is not None:
        if offset in visited or not 0 <= offset < len(raw):
            raise RE.EvidenceError('PDF cross-reference offset invalid or cyclic')
        visited.add(offset)
        if not raw[offset:].startswith(b'xref'):
            raise RE.EvidenceError('PDF needs a supported classic-xref export; xref streams are not verified')
        tail = raw[offset + 4:]
        marker = re.search(rb'\btrailer\s*<<(.*?)>>', tail, re.S)
        if marker is None:
            raise RE.EvidenceError('PDF cross-reference trailer absent')
        table = tail[:marker.start()].strip().splitlines(); i = 0
        while i < len(table):
            header = re.fullmatch(rb'\s*(\d+)\s+(\d+)\s*', table[i]); i += 1
            if header is None:
                raise RE.EvidenceError('PDF cross-reference subsection malformed')
            first, count = map(int, header.groups())
            if count > len(table) - i:
                raise RE.EvidenceError('PDF cross-reference subsection is truncated')
            for number, line in enumerate(table[i:i + count], first):
                entry = re.fullmatch(rb'\s*(\d{10})\s+(\d{5})\s+([nf])\s*', line)
                if entry is None:
                    raise RE.EvidenceError('PDF cross-reference entry malformed')
                pos, gen = int(entry.group(1)), int(entry.group(2))
                if number not in objects:
                    objects[number] = (pos, gen) if entry.group(3) == b'n' else None
            i += count
        trailer = marker.group(1)
        if re.search(rb'/Encrypt\b|/XRefStm\b', trailer):
            raise RE.EvidenceError('encrypted or hybrid PDF export is not supported by this structural gate')
        ref = re.search(rb'/Root\s+(\d+)\s+(\d+)\s+R\b', trailer)
        if root_ref is None and ref:
            root_ref = tuple(map(int, ref.groups()))
        previous = re.search(rb'/Prev\s+(\d+)\b', trailer)
        offset = int(previous.group(1)) if previous else None

    def object_body(reference):
        number, generation = reference
        entry = objects.get(number)
        if entry is None or entry[1] != generation or not 0 < entry[0] < len(raw):
            raise RE.EvidenceError('PDF object reference is absent or has an invalid generation/offset')
        header = rb'\s*' + str(number).encode() + rb'\s+' + str(generation).encode() + rb'\s+obj\b(.*?)\bendobj\b'
        obj = re.match(header, raw[entry[0]:], re.S)
        if obj is None:
            raise RE.EvidenceError('PDF cross-reference does not identify an actual complete object')
        return obj.group(1)

    for number, object_entry in objects.items():
        if object_entry is not None:
            object_body((number, object_entry[1]))
    if root_ref is None:
        raise RE.EvidenceError('PDF catalog reference absent')
    catalog = object_body(root_ref)
    pages = re.search(rb'/Pages\s+(\d+)\s+(\d+)\s+R\b', catalog)
    if re.search(rb'/Type\s*/Catalog\b', catalog) is None or pages is None:
        raise RE.EvidenceError('PDF catalog/page tree absent')
    seen = set()

    def count_pages(reference):
        if reference in seen:
            raise RE.EvidenceError('PDF page tree is cyclic or repeats a page')
        seen.add(reference); body = object_body(reference)
        if re.search(rb'/Type\s*/Page\b', body):
            return 1
        kids = re.search(rb'/Kids\s*\[(.*?)\]', body, re.S)
        count = re.search(rb'/Count\s+(\d+)\b', body)
        if re.search(rb'/Type\s*/Pages\b', body) is None or kids is None or count is None:
            raise RE.EvidenceError('PDF page node or child references absent')
        refs = re.findall(rb'(\d+)\s+(\d+)\s+R\b', kids.group(1))
        if not refs or re.sub(rb'\d+\s+\d+\s+R\b', b'', kids.group(1)).strip():
            raise RE.EvidenceError('PDF page child array malformed or empty')
        total = sum(count_pages(tuple(map(int, r))) for r in refs)
        if total != int(count.group(1)):
            raise RE.EvidenceError('PDF page tree count contradicts actual pages')
        return total

    try:
        return count_pages(tuple(map(int, pages.groups())))
    except RecursionError as exc:
        raise RE.EvidenceError('PDF page tree nesting exceeds the supported reader limit') from exc
