"""Structural F018 checks for an actually divided CORE review package.

N1 30.3/30.4, SF-RULE-CORE-004. All source/read/reviewer intake is externally
authenticated. This module reads pinned artifacts and never certifies a reading,
philology, reviewer independence, publication consent, or Standard activation.
The caller supplies the independently verified global source scope and source
reference, complete CORE/target manifest, reviewer report and freeze reference.
"""
from __future__ import annotations
import json
from typing import Any
from . import publication_inputs as PI
from . import release_evidence as RE

READY = 'PARTS_EVIDENCE_READY'
BOUND = {'subject_id', 'revision_id', 'content_sha256', 'scope'}
GLOBAL_CHECKS = {'argument_continuity', 'full_polish_reading', 'source_scope', 'repetition_inventory'}
LOGICAL_KINDS = {'SENTENCE', 'STANZA', 'FORMULA', 'PARAGRAPH'}


def _need(condition, message):
    if not condition:
        raise RE.EvidenceError(message)


def _record(value, required, optional=()):
    _need(isinstance(value, dict), 'record must be an object')
    _need(set(required) <= set(value) and not set(value) - set(required) - set(optional),
          'missing or unknown record fields')
    return value


def _records(value, *, empty=False):
    _need(isinstance(value, list) and (empty or bool(value)) and
          all(isinstance(x, dict) for x in value), 'record array absent or malformed')
    return value


def _ids(value, *, empty=False):
    if empty and value == []:
        return []
    return RE.scope(value)


def _canonical(value):
    try:
        return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode('utf-8')
    except UnicodeError as exc:
        raise RE.EvidenceError('record contains text that cannot be encoded as UTF-8') from exc


def _range(value, raw, *, previous=0):
    _need(isinstance(value, list) and len(value) == 2 and all(type(n) is int for n in value),
          'byte range must contain two integer offsets')
    a, b = value
    _need(previous <= a < b <= len(raw), 'byte range overlaps, is empty or exceeds the bound unit')
    return a, b


def _utf8(raw):
    try:
        return raw.decode('utf-8')
    except UnicodeError as exc:
        raise RE.EvidenceError('text or range boundary is not valid UTF-8') from exc


def _json_source_units(raw):
    """Complete flat unit object with exact string-token offsets and unique IDs."""
    text = _utf8(raw); offsets = [0]
    for char in text:
        offsets.append(offsets[-1] + len(char.encode('utf-8')))
    decoder = json.JSONDecoder(); entries = []; seen = set()

    def space(index):
        while index < len(text) and text[index] in ' \r\n\t':
            index += 1
        return index

    try:
        cursor = space(0)
        _need(cursor < len(text) and text[cursor] == '{', 'source must be a flat JSON unit object')
        cursor = space(cursor + 1)
        while True:
            uid, cursor = decoder.raw_decode(text, cursor)
            _need(RE.nonempty(uid) and uid not in seen, 'source unit ID is invalid or duplicated')
            seen.add(uid); cursor = space(cursor)
            _need(cursor < len(text) and text[cursor] == ':', 'source unit colon absent')
            begin = space(cursor + 1); value, end = decoder.raw_decode(text, begin)
            _need(RE.nonempty(value), 'source unit is not nonempty text')
            try:
                value.encode('utf-8')
            except UnicodeError as exc:
                raise RE.EvidenceError('decoded source unit is not valid UTF-8 text') from exc
            entries.append({'id': uid, 'byte_range': [offsets[begin], offsets[end]],
                            'representation': 'JSON_STRING'})
            cursor = space(end)
            if cursor < len(text) and text[cursor] == '}':
                _need(space(cursor + 1) == len(text), 'source has trailing unaccounted material')
                break
            _need(cursor < len(text) and text[cursor] == ',', 'source unit separator absent')
            cursor = space(cursor + 1)
    except json.JSONDecodeError as exc:
        raise RE.EvidenceError('source JSON unit structure is malformed') from exc
    return entries


def _reading(root, ref, unit, source, subject):
    """Scoped book/direct reading is admitted without a full carrier capture."""
    proof = RE.read_artifact(root, ref, json_object=True)
    _need(proof.get('kind') == 'SOURCE_READ_ATTESTATION' and
          isinstance(proof.get('read_mode'), str) and
          proof.get('read_mode') in {'BOOK_READING', 'DIRECT_SOURCE_READING'},
          'uncaptured source requires actual scoped book/direct reading evidence')
    _need(all(proof.get(k) == subject[k] for k in ('subject_id', 'revision_id')) and
          proof.get('source_id') == source['source_id'], 'source reading identity differs')
    scope = RE.scope(proof.get('scope'))
    _need(unit['id'] in scope and set(scope) <= set(subject['scope']), 'source reading scope differs')
    _need(proof.get('locator') == unit['locator'] and all(RE.nonempty(proof.get(k)) for k in
          ('actor_id', 'context_id', 'evidence_text')), 'actual scoped reading details absent')
    auth = proof.get('authenticated_source')
    _need(isinstance(auth, dict) and auth.get('actor_id') == proof['actor_id'] and
          all(RE.nonempty(auth.get(k)) for k in ('uri', 'record_id')), 'reading source record absent')
    RE.timestamp(proof.get('at'))
    return proof['at']


def _sources(root, index, source_ref, subject):
    _need(index['source'] == source_ref, 'parts source differs from the independently supplied source')
    raw = RE.read_artifact(root, source_ref)
    entries = _records(index['source_units'])
    _need(_ids([u.get('id') for u in entries]) == subject['scope'],
          'source unit inventory omits, duplicates or reorders the full task scope')
    units = {}; events = []
    book = any('reading_ref' in unit for unit in entries)
    if book:
        try:
            source = json.loads(_utf8(raw))
        except ValueError as exc:
            raise RE.EvidenceError('source scope manifest is not valid JSON') from exc
        _record(source, {'schema', 'subject_id', 'revision_id', 'source_id', 'scope', 'units'})
        _need(source['schema'] == 'suttaflow-core-source-scope-v2' and RE.nonempty(source['source_id']),
              'source scope manifest schema or source identity absent')
        _need(all(source[k] == subject[k] for k in ('subject_id', 'revision_id', 'scope')) and
              source['units'] == entries, 'source scope manifest does not pin these exact units')
    else:
        representations = [unit.get('representation') for unit in entries]
        _need(all(r == representations[0] for r in representations), 'mixed source representations are unsupported')
        if representations[0] == 'JSON_STRING':
            _need(entries == _json_source_units(raw),
                  'source IDs, text-token ranges or full JSON unit inventory differ')
    end = 0
    for unit in entries:
        uid = unit['id']
        if book:
            _record(unit, {'id', 'locator', 'reading_ref'})
            _need(RE.nonempty(unit['locator']), 'book unit locator absent')
            events.append(_reading(root, unit['reading_ref'], unit, source, subject))
            units[uid] = dict(unit)
        else:
            _record(unit, {'id', 'byte_range', 'representation'})
            previous = end
            a, end = _range(unit['byte_range'], raw, previous=previous)
            text = _utf8(raw[a:end])
            _need(unit['representation'] in ('UTF8_TEXT', 'JSON_STRING'), 'unknown source representation')
            if unit['representation'] == 'UTF8_TEXT':
                _need(not _utf8(raw[previous:a]).strip(), 'source unit inventory silently omits text')
            if unit['representation'] == 'JSON_STRING':
                try:
                    text = json.loads(text)
                except ValueError as exc:
                    raise RE.EvidenceError('source range is not one complete JSON string') from exc
            _need(RE.nonempty(text), 'source unit text absent')
            units[uid] = {'id': uid, 'text': text}
    if not book and entries[0]['representation'] == 'UTF8_TEXT':
        _need(not _utf8(raw[end:]).strip(), 'source unit inventory omits final source text')
    return units, events


def _targets(root, index, subject, core_subject, bundle):
    ids = PI.target_units(root, subject, core_subject)
    _need(index['target_unit_manifest'] == bundle.get('target_unit_manifest'),
          'parts target manifest differs from the complete global CORE inventory')
    manifest = RE.read_artifact(root, index['target_unit_manifest'], json_object=True)
    raw = RE.read_artifact(root, core_subject['content'])
    units = {u['id']: {'id': u['id'], 'text': _utf8(raw[u['byte_range'][0]:u['byte_range'][1]])}
             for u in manifest['units']}
    return ids, units


def _logical_units(index, sources, targets, source_ids, target_ids):
    logical = _records(index['logical_units'])
    ids = _ids([u.get('id') for u in logical])
    source_order = []; target_order = []; leaves = {}
    for unit in logical:
        _record(unit, {'id', 'kind', 'source_ids', 'candidate_ids'}, {'repeat_key'})
        _need(unit['kind'] in LOGICAL_KINDS if isinstance(unit['kind'], str) else False,
              'unknown logical boundary type')
        left = _ids(unit['source_ids']); right = _ids(unit['candidate_ids'])
        _need(set(left) <= set(sources) and set(right) <= set(targets), 'logical unit maps unknown IDs')
        if 'repeat_key' in unit:
            _need(RE.nonempty(unit['repeat_key']), 'repeat group identity absent')
        source_order.extend(left); target_order.extend(right)
        leaves[unit['id']] = {'id': unit['id'], 'source': [sources[i] for i in left],
                              'candidate': [targets[i] for i in right]}
    _need(source_order == source_ids and target_order == target_ids,
          'logical unit map omits, duplicates or reorders global source/target units')
    return logical, ids, leaves


def _split_children(mapping, parent, reserved_ids, source_fragment_ids, target_fragment_ids):
    children = _records(mapping['children'])
    child_ids = _ids([c.get('id') for c in children])
    _need(len(children) >= 2 and not set(child_ids) & reserved_ids, 'split child IDs reused or absent')
    reserved_ids.update(child_ids)
    output = {}
    for child in children:
        _record(child, {'id', 'source', 'candidate'})
        output[child['id']] = {'id': child['id'], 'source': [], 'candidate': []}
    for side, seen in [('source', source_fragment_ids), ('candidate', target_fragment_ids)]:
        originals = {u['id']: u for u in parent[side]}
        _need(all('text' in u for u in originals.values()),
              'within-unit split needs exact scoped text; a book locator alone cannot prove byte partitions')
        positions = {uid: 0 for uid in originals}; visits = []
        for child in children:
            fragments = _records(child[side])
            for fragment in fragments:
                _record(fragment, {'id', 'parent_id', 'byte_range'})
                uid, pid = fragment['id'], fragment['parent_id']
                _need(RE.nonempty(uid) and uid not in seen and RE.nonempty(pid) and pid in originals,
                      'split fragment identity is duplicated, unknown or outside the parent')
                seen.add(uid); visits.append(pid)
                raw = originals[pid]['text'].encode('utf-8')
                a, b = _range(fragment['byte_range'], raw, previous=positions[pid])
                _need(a == positions[pid], 'controlled split silently omits bytes')
                text = _utf8(raw[a:b]); _need(RE.nonempty(text), 'empty controlled subunit')
                positions[pid] = b
                output[child['id']][side].append(dict(fragment) | {'text': text})
        order = list(originals)
        _need(visits == sorted(visits, key=order.index) and
              all(positions[uid] == len(u['text'].encode('utf-8')) for uid, u in originals.items()),
              'split fragments reorder parent units or omit their remaining bytes')
    return child_ids, output


def _splits(root, index, logical_ids, leaves, core_subject, source_ids, target_ids):
    records = _records(index['splits'], empty=True)
    replacements = {}; reserved = set(logical_ids); events = []
    source_fragments = set(source_ids); target_fragments = set(target_ids)
    for record in records:
        _record(record, {'mapping', 'evidence'})
        mapping = RE.read_artifact(root, record['mapping'], json_object=True)
        _record(mapping, BOUND | {'schema', 'parent_unit_id', 'children'})
        RE.binding(mapping, core_subject)
        _need(mapping['schema'] == 'suttaflow-controlled-core-split-v2' and
              RE.nonempty(mapping['parent_unit_id']), 'controlled split mapping schema absent')
        pid = mapping['parent_unit_id']
        _need(pid in logical_ids and pid not in replacements, 'split parent is unknown or split twice')
        _need(len(_canonical(leaves[pid])) > index['max_part_bytes'],
              'controlled within-unit split has no recorded over-limit logical unit')
        proof = RE.read_artifact(root, record['evidence'], json_object=True)
        _record(proof, BOUND | {'kind', 'parent_unit_id', 'mapping', 'reason', 'actor_id', 'at'})
        RE.binding(proof, core_subject)
        _need(proof['kind'] == 'CONTROLLED_CORE_SPLIT' and proof['parent_unit_id'] == pid and
              proof['mapping'] == record['mapping'] and RE.nonempty(proof['reason']) and
              RE.nonempty(proof['actor_id']), 'split evidence does not attest this exact new map')
        RE.timestamp(proof['at']); events.append(proof['at'])
        ids, children = _split_children(mapping, leaves[pid], reserved, source_fragments, target_fragments)
        replacements[pid] = ids; leaves.update(children)
    for uid in logical_ids:
        _need(uid in replacements or len(_canonical(leaves[uid])) <= index['max_part_bytes'],
              'over-limit logical unit needs an explicit controlled split and new map')
    ordered = [child for uid in logical_ids for child in replacements.get(uid, [uid])]
    return ordered, events


def _parts(root, index, leaf_ids, leaves, core_subject):
    records = _records(index['parts'])
    _need(len(records) >= 2, 'a divided package needs at least two actual parts')
    ids = _ids([p.get('id') for p in records]); ordered: list[str] = []; contexts = 0
    for number, part in enumerate(records, 1):
        _record(part, {'id', 'order', 'unit_ids', 'source_ids', 'candidate_ids',
                       'context_before', 'context_after', 'artifact'})
        _need(type(part['order']) is int and part['order'] == number, 'part index is out of order')
        body = _ids(part['unit_ids'])
        _need(set(body) <= set(leaf_ids), 'unknown part unit')
        start, end = len(ordered), len(ordered) + len(body)
        _need(body == leaf_ids[start:end], 'part units omitted, duplicated or out of order')
        ordered.extend(body)
        before = _ids(part['context_before'], empty=True); after = _ids(part['context_after'], empty=True)
        _need(len(before) <= start and before == leaf_ids[start-len(before):start] and
              after == leaf_ids[end:end+len(after)], 'KONTEKST must contain adjacent external units only')
        _need(_ids(part['source_ids']) == [s['id'] for uid in body for s in leaves[uid]['source']] and
              _ids(part['candidate_ids']) == [s['id'] for uid in body for s in leaves[uid]['candidate']],
              'part source/target IDs differ from body units; context never contributes coverage')
        raw = RE.read_artifact(root, part['artifact'])
        _need(len(raw) <= index['max_part_bytes'], 'actual part file exceeds its recorded byte limit')
        payload = RE.read_artifact(root, part['artifact'], json_object=True)
        expected = {'schema': 'suttaflow-core-part-v2', 'subject_id': core_subject['subject_id'],
            'revision_id': core_subject['revision_id'], 'part_id': part['id'], 'order': number,
            'units': [leaves[uid] for uid in body],
            'KONTEKST': {'before': [leaves[uid] for uid in before], 'after': [leaves[uid] for uid in after]}}
        _need(payload == expected, 'part bytes contain different text, scope, context, revision or extra material')
        contexts += len(before) + len(after)
    _need(ordered == leaf_ids, 'parts do not cover all logical units')
    return ids, contexts


def _completed(record):
    _need(isinstance(record, dict) and record.get('status') == 'COMPLETED' and
          RE.nonempty(record.get('evidence')), 'actual complete global reading/check is absent or NOT_RUN')


def _global_review(root, manifest, index_ref, part_ids, target_ids, logical, core_subject,
                   global_report_ref, core_freeze_ref, events):
    _need(manifest['global_report'] == global_report_ref and manifest['global_freeze'] == core_freeze_ref,
          'manifest global report/freeze differs from the real CORE workflow')
    report = RE.report(root, global_report_ref, 'INDEPENDENT_REVIEW', core_subject)
    review = report.get('parts_review')
    _record(review, {'index', 'part_ids', 'candidate_ids', 'part_checks', 'transitions',
                     'repetitions', 'global_checks'})
    _need(review['index'] == index_ref and review['part_ids'] == part_ids and
          review['candidate_ids'] == target_ids, 'global review does not cover this entire parts index')
    checks = _records(review['part_checks'])
    _need([c.get('part_id') for c in checks] == part_ids, 'global report omits or duplicates a part check')
    for check in checks:
        _record(check, {'part_id', 'status', 'evidence'}); _completed(check)
    transitions = _records(review['transitions'])
    _need([(r.get('from'), r.get('to')) for r in transitions] == list(zip(part_ids, part_ids[1:])),
          'global report omits or reorders a transition between parts')
    for transition in transitions:
        _record(transition, {'from', 'to', 'status', 'evidence'}); _completed(transition)
    repeats = _records(review['repetitions'], empty=True)
    _need([r.get('unit_id') for r in repeats] == [u['id'] for u in logical if 'repeat_key' in u],
          'global report does not account for every declared repeated occurrence')
    for repeat in repeats:
        _record(repeat, {'unit_id', 'status', 'evidence'}); _completed(repeat)
    _record(review['global_checks'], GLOBAL_CHECKS)
    for check in review['global_checks'].values():
        _record(check, {'status', 'evidence'}); _completed(check)
    completed = RE.timestamp(report['completed_at'])
    _need(all(RE.timestamp(at) <= completed for at in events), 'global review predates reading or controlled remapping')
    freeze = RE.read_artifact(root, core_freeze_ref, json_object=True)
    RE.binding(freeze, core_subject)
    _need(freeze.get('kind') == 'CORE_FREEZE' and freeze.get('report_sha256') == global_report_ref['sha256'],
          'CORE freeze does not pin the complete original global report')
    _need(RE.timestamp(freeze.get('frozen_at')) >= completed, 'CORE froze before completion of global review')


def validate(root, manifest_ref, *, subject, core_subject, source_ref,
             global_report_ref, core_freeze_ref):
    """Check optional ``bundle.parts_manifest`` on the divided-review path only.

    ``source_ref`` is independently selected by the caller after source-contract
    validation: actual captured source bytes OR a pinned complete source-scope
    index with scoped BOOK_READING/DIRECT_SOURCE_READING references. Neither the
    source denominator nor the global reviewer/freeze pins is chosen by parts.
    """
    stage = 'MANIFEST'
    result: dict[str, Any] = {'schema': 'suttaflow-publication-parts-validation-v2', 'status': 'HOLD',
              'errors': [], 'coverage': None, 'ready_for_publication': False,
              'structural_only': True}
    try:
        for view in (subject, core_subject):
            _need(isinstance(view, dict) and all(RE.nonempty(view.get(k)) for k in ('subject_id', 'revision_id'))
                  and isinstance(view.get('content'), dict), 'complete independently bound subject absent')
            RE.scope(view.get('scope'))
        _need(all(core_subject[k] == subject[k] for k in ('subject_id', 'revision_id', 'scope')),
              'global CORE/source identity or scope differs')
        bundle = RE.read_artifact(root, subject['content'], json_object=True)
        _need(bundle.get('schema') == 'suttaflow-publication-bundle-v2' and
              bundle.get('parts_manifest') == manifest_ref and bundle.get('core') == core_subject['content'] and
              all(bundle.get(k) == subject[k] for k in ('subject_id', 'revision_id', 'scope')),
              'publication bundle does not bind this parts manifest and entire CORE')
        manifest = RE.read_artifact(root, manifest_ref, json_object=True)
        _record(manifest, BOUND | {'schema', 'index', 'global_report', 'global_freeze'})
        RE.binding(manifest, core_subject)
        _need(manifest['schema'] == 'suttaflow-publication-parts-v2', 'unknown parts manifest schema')
        stage = 'INDEX'
        index = RE.read_artifact(root, manifest['index'], json_object=True)
        _record(index, BOUND | {'schema', 'source', 'source_units', 'target_unit_manifest',
                               'max_part_bytes', 'logical_units', 'splits', 'parts'})
        RE.binding(index, core_subject)
        _need(index['schema'] == 'suttaflow-publication-parts-index-v2', 'unknown parts index schema')
        _need(type(index['max_part_bytes']) is int and index['max_part_bytes'] > 0,
              'per-request practical byte limit must be a positive integer')
        sources, events = _sources(root, index, source_ref, subject)
        target_ids, targets = _targets(root, index, subject, core_subject, bundle)
        logical, logical_ids, leaves = _logical_units(index, sources, targets, subject['scope'], target_ids)
        stage = 'SPLIT'
        leaf_ids, split_events = _splits(root, index, logical_ids, leaves, core_subject, subject['scope'], target_ids)
        stage = 'CONTENT'
        part_ids, contexts = _parts(root, index, leaf_ids, leaves, core_subject)
        stage = 'GLOBAL_REVIEW'
        _global_review(root, manifest, manifest['index'], part_ids, target_ids, logical, core_subject,
                       global_report_ref, core_freeze_ref, events + split_events)
        result.update(status=READY, coverage={'source_ids': list(subject['scope']), 'candidate_ids': target_ids,
            'part_ids': part_ids, 'leaf_unit_count': len(leaf_ids), 'context_occurrences': contexts,
            'controlled_splits': len(index['splits'])})
    except RE.EvidenceError as exc:
        result['errors'].append({'code': 'PARTS_' + stage + '_INVALID', 'message': str(exc)})
    return result
