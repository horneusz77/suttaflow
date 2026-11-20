"""Structural, byte-bound claim evidence (N1 34.1–34.9 / APP-001 / INT-002).

This adapter checks the complete apparatus and interpretation bytes, recorded
source reading and three separate claim reviews. It cannot determine sentence
semantics, authenticate a reader or certify philological truth. The caller must
pass the actual dictionaries already verified by release_evidence.report and
the source case verified by source_contract. No result authorizes publication.
"""
from __future__ import annotations
import json
from typing import Any
from . import release_evidence as RE

READY = 'CLAIM_EVIDENCE_READY'
COMPONENTS = ('core', 'apparatus', 'interpretation')
GATES = {'ik': 'APARAT_IK', 'id': 'APARAT_ID', 'ir': 'APARAT_IR'}
PROVENANCE = {'K', 'P', 'W', 'T', 'H'}
REGIONS = {'DESCRIPTION', 'INTERPRETATION', 'FOOTNOTE', 'PARALLEL',
           'METHOD', 'TRANSLATION_DECISIONS', 'METRICS', 'OTHER_PUBLIC'}
PROCESS_REGIONS = {'METHOD', 'TRANSLATION_DECISIONS', 'METRICS'}
PROCESS_TYPES = {'METHOD', 'OWNER_DECISION', 'READING', 'REVIEW'}
HEADINGS = {
    'DESCRIPTION': {'Opis'}, 'INTERPRETATION': {'Interpretacja'},
    'FOOTNOTE': {'Przypisy'}, 'PARALLEL': {'Paralele kanoniczne'},
    'METHOD': {'Jak powstało to tłumaczenie'},
    'TRANSLATION_DECISIONS': {'Decyzje tłumaczeniowe'},
    'METRICS': {'Metryka przekładu'},
    'OTHER_PUBLIC': {'Źródła', 'Historia rewizji'},
}
LABELS = {'Autor', 'Data', 'Wersja', 'Rewizja', 'Zakres', 'Podstawa', 'Metoda',
          'Źródło', 'Recenzja', 'Status'}
INVENTORY_CHECKS = {'sentence_inventory', 'subclaim_inventory', 'role_assignment'}
CHECKS = {
    'ik': {'claim_type', 'canonical_locus_context', 'subject_quantifiers',
           'causality_conditions_negation', 'terms_variants',
           'translation_consistency', 'support_scope'},
    'id': {'claim_type', 'provenance', 'attribution_actual_reading',
           'direct_vs_indirect', 'alternatives_uncertainty', 'support_scope',
           'process_record_truth'},
    'ir': {'claim_type', 'full_polish_reading', 'description_neutrality',
           'interpretation_clarity', 'titles_terms_style',
           'preserved_meaning_attribution_uncertainty', 'hidden_claims'},
}
CONFIDENCE = {'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN'}


class ClaimError(RE.EvidenceError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def _need(ok, message, code='CLAIM_MANIFEST_INVALID'):
    if not ok:
        raise ClaimError(code, message)


def _object(value, required, optional=(), *, label='record'):
    _need(isinstance(value, dict), label + ' must be an object')
    required = set(required)
    _need(required <= set(value) <= required | set(optional),
          label + ' has missing or unknown fields')
    return value


def _array(value, *, empty=False, label='array'):
    _need(isinstance(value, list) and (empty or bool(value)), label + ' is absent or malformed')
    return value


def _ids(value, *, empty=False, label='IDs'):
    _array(value, empty=empty, label=label)
    _need(all(RE.nonempty(x) for x in value), label + ' must contain nonempty strings')
    _need(len(value) == len(set(value)), label + ' contains duplicates')
    return value


def _enum(value, choices, label):
    _need(isinstance(value, str) and value in choices, label + ' is unknown')
    return value


def _actor(value):
    _object(value, {'id', 'model', 'context_id'}, label='actor')
    _need(all(RE.nonempty(value[k]) for k in value), 'actor identity/model/context absent')
    return value


def _span(span, raw, low=0, high=None):
    high = len(raw) if high is None else high
    _need(isinstance(span, list) and len(span) == 2 and all(type(n) is int for n in span),
          'byte range must contain two integers', 'CLAIM_INVENTORY_INCOMPLETE')
    a, b = span
    _need(low <= a < b <= high, 'byte range outside parent or reversed', 'CLAIM_INVENTORY_INCOMPLETE')
    try:
        text = raw[a:b].decode('utf-8')
    except UnicodeError as exc:
        raise ClaimError('CLAIM_INVENTORY_INCOMPLETE', 'range splits a UTF-8 character') from exc
    _need(bool(text.strip()), 'empty/whitespace-only inventory item', 'CLAIM_INVENTORY_INCOMPLETE')
    return a, b, text


def _partition(raw, entries, low=0, high=None):
    """Independently account for actual bytes, not a declared ID denominator."""
    high = len(raw) if high is None else high
    end = low
    for item in _array(entries, label='byte inventory'):
        _need(isinstance(item, dict), 'inventory item must be an object')
        a, b, text = _span(item.get('byte_range'), raw, end, high)
        try:
            gap = raw[end:a].decode('utf-8')
        except UnicodeError as exc:
            raise ClaimError('CLAIM_INVENTORY_INCOMPLETE', 'inventory gap splits UTF-8') from exc
        _need(not gap.strip(), 'inventory omits non-whitespace bytes', 'CLAIM_INVENTORY_INCOMPLETE')
        _need(item.get('text') == text, 'quoted text differs from current bytes', 'CLAIM_INVENTORY_INCOMPLETE')
        end = b
    try:
        tail = raw[end:high].decode('utf-8')
    except UnicodeError as exc:
        raise ClaimError('CLAIM_INVENTORY_INCOMPLETE', 'inventory tail splits UTF-8') from exc
    _need(not tail.strip(), 'inventory omits final text', 'CLAIM_INVENTORY_INCOMPLETE')


def _inventory(inventory, raw):
    units, sentences, region_ids = {}, set(), set()
    by_component: dict[str, list[dict[str, Any]]] = {k: [] for k in ('apparatus', 'interpretation')}
    for region in _array(inventory, label='full component inventory'):
        _object(region, {'id', 'component', 'role', 'byte_range', 'text', 'sentences'}, label='region')
        _need(RE.nonempty(region['id']) and region['id'] not in region_ids, 'region ID absent or duplicate')
        region_ids.add(region['id'])
        component = _enum(region['component'], by_component, 'region component')
        role = _enum(region['role'], REGIONS, 'region role')
        _need(role != 'DESCRIPTION' or component == 'apparatus', 'Opis must belong to apparatus')
        _need(role != 'INTERPRETATION' or component == 'interpretation', 'Interpretacja component differs')
        by_component[component].append(region)
        data = raw[component]
        a, b, _ = _span(region['byte_range'], data)
        _partition(data, region['sentences'], a, b)
        for sentence in region['sentences']:
            _object(sentence, {'id', 'byte_range', 'text', 'units'}, label='sentence')
            sid = sentence['id']
            _need(RE.nonempty(sid) and sid not in sentences, 'sentence ID absent or duplicate')
            sentences.add(sid)
            x, y, _ = _span(sentence['byte_range'], data, a, b)
            _partition(data, sentence['units'], x, y)
            for unit in sentence['units']:
                _object(unit, {'id', 'kind', 'byte_range', 'text'}, {'role'}, label='subclaim/unit')
                uid = unit['id']
                _need(RE.nonempty(uid) and uid not in units, 'subclaim/unit ID absent or duplicate')
                kind = _enum(unit['kind'], {'CLAIM', 'NON_CLAIM'}, 'unit kind')
                if kind == 'NON_CLAIM':
                    technical = _enum(unit.get('role'), {'HEADING', 'FIELD_LABEL'}, 'non-claim role')
                    label = unit['text'].strip().removesuffix(':')
                    allowed = HEADINGS[role] if technical == 'HEADING' else LABELS
                    _need(label in allowed, 'ordinary text cannot be excluded as a technical heading/label',
                          'CLAIM_INVENTORY_INCOMPLETE')
                else:
                    _need('role' not in unit, 'a claim cannot also declare a non-claim role')
                units[uid] = {**unit, 'sentence_id': sid, 'component': component, 'region_role': role}
    for component, regions in by_component.items():
        _partition(raw[component], regions)
    _need(any(r['role'] == 'DESCRIPTION' for r in inventory), 'complete Opis region absent')
    _need(any(r['role'] == 'INTERPRETATION' for r in inventory), 'complete Interpretacja region absent')
    return units, len(sentences)


def _scope(value, subject, *, label):
    _ids(value, label=label)
    _need(set(value) <= set(subject['scope']), label + ' exceeds current subject', 'CLAIM_BINDING_INVALID')
    return value


def _checks(value, names, *, allow_na=()):
    _object(value, names, label='dimension checks')
    for key, item in value.items():
        _object(item, {'status', 'evidence'}, label='dimension assessment')
        _need(RE.nonempty(item['evidence']), 'dimension assessment needs its own explanation', 'CLAIM_REVIEW_INVALID')
        allowed = {'REVIEWED', 'NOT_APPLICABLE'} if key in allow_na else {'REVIEWED'}
        _need(isinstance(item['status'], str) and item['status'] in allowed,
              'missing actual assessment of dimension ' + key, 'CLAIM_REVIEW_INVALID')


def _envelope(report, kind, subject):
    _need(isinstance(report, dict), 'verified ' + kind + ' report absent', 'CLAIM_REVIEW_INVALID')
    RE.binding(report, subject)
    _need(report.get('kind') == kind and report.get('result') in ('PASS', 'PASS_WITH_NOTES'),
          'completed ' + kind + ' report absent', 'CLAIM_REVIEW_INVALID')
    _actor(report.get('actor'))
    RE.timestamp(report.get('completed_at'))
    _array(report.get('findings'), empty=True, label='report findings')


def _sources(root, case, reports, subject):
    _need(isinstance(case, dict), 'verified source case absent', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    RE.binding(case, subject)
    source_report = reports.get('sources')
    _envelope(source_report, 'SOURCE_READ_REVIEW', subject)
    recorded = RE.read_artifact(root, source_report.get('source_case'), json_object=True)
    _need(recorded == case, 'source case differs from the actual verified report artifact', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    index = RE.read_artifact(root, source_report.get('source_evidence_index'), json_object=True)
    sources = {}
    for source in _array(case.get('sources'), label='actual sources'):
        _need(isinstance(source, dict) and RE.nonempty(source.get('source_id')), 'source identity absent')
        _need(source['source_id'] not in sources, 'duplicate source ID')
        sources[source['source_id']] = source
    return sources, index


def _source_reference(root, ref, claim, sources, index, subject, prepared_at):
    _object(ref, {'id', 'kind', 'source_id', 'edition', 'locus', 'scope', 'attribution', 'read_event_ref'},
            {'capture', 'excerpt'}, label='source reference')
    sid = ref['source_id']
    _need(RE.nonempty(sid) and sid in sources, 'claim cites an unknown source', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    source = sources[sid]
    _need(source.get('read_state') == 'READ' and source.get('used') is True,
          'claim cites a source without actual READ/use', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    _need(ref['edition'] == source.get('edition') and ref['attribution'] == source.get('author_or_editor'),
          'claim edition or attribution differs from actual source', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    _need(RE.nonempty(ref['locus']) and RE.nonempty(ref['read_event_ref']), 'source locus/read event absent')
    used_scope = _scope(ref['scope'], subject, label='citation scope')
    _need(set(used_scope) <= set(RE.scope(source.get('read_scope'))),
          'citation exceeds actually read source scope', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    events = [e for e in _array(source.get('read_events'), label='read events')
              if isinstance(e, dict) and e.get('evidence_ref') == ref['read_event_ref']]
    _need(len(events) == 1, 'exact source read event absent or duplicate', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    event = events[0]
    _need(set(used_scope) <= set(RE.scope(event.get('scope'))),
          'citation exceeds this reading event', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    proof = RE.read_artifact(root, index.get(ref['read_event_ref']), json_object=True)
    RE.binding(proof, subject, partial=True)
    _need(proof.get('kind') == 'SOURCE_READ_ATTESTATION' and proof.get('source_id') == sid,
          'actual read artifact identifies another source or kind', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    for key in ('actor_id', 'context_id', 'at', 'scope', 'locator'):
        _need(proof.get(key) == event.get(key), 'source read event differs from its artifact: ' + key,
              'CLAIM_SOURCE_EVIDENCE_INVALID')
    _need(RE.timestamp(proof.get('at')) <= prepared_at, 'claim manifest predates the cited source reading',
          'CLAIM_SOURCE_EVIDENCE_INVALID')
    metadata = proof.get('source_metadata')
    _need(isinstance(metadata, dict) and all(metadata.get(k) == source.get(k) for k in
          ('title', 'author_or_editor', 'edition', 'actual_carrier', 'evidence_kind', 'language', 'profile_role')),
          'read artifact source metadata differs', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    auth = proof.get('authenticated_source')
    _need(isinstance(auth, dict) and auth.get('actor_id') == event.get('actor_id') and
          all(RE.nonempty(auth.get(k)) for k in ('uri', 'record_id')) and RE.nonempty(proof.get('evidence_text')),
          'recorded reading has no attributed source record', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    if proof.get('read_mode') == 'CAPTURE_READING':
        _need(ref.get('capture') == proof.get('capture_ref'), 'citation capture differs from actual read capture',
              'CLAIM_SOURCE_EVIDENCE_INVALID')
        capture = RE.read_artifact(root, ref['capture'])
        _need(source.get('capture_path') == ref['capture']['path'] and
              source.get('capture_sha256') == ref['capture']['sha256'],
              'source case capture differs', 'CLAIM_SOURCE_EVIDENCE_INVALID')
        excerpt = _object(ref.get('excerpt'), {'byte_range', 'text'}, label='source excerpt')
        a, b, text = _span(excerpt['byte_range'], capture)
        _need(excerpt['text'] == text, 'source excerpt differs from actual capture bytes', 'CLAIM_SOURCE_EVIDENCE_INVALID')
        ranges = _array(proof.get('read_byte_ranges'), label='actual source read ranges')
        covered = []
        for span in ranges:
            x, y, _ = _span(span, capture)
            covered.append((x, y))
        end = a
        for x, y in sorted(covered):
            if x <= end < y:
                end = y
        _need(end >= b, 'claim excerpt includes unread capture bytes', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    else:
        _need(isinstance(proof.get('read_mode'), str) and proof['read_mode'] in {'BOOK_READING', 'DIRECT_SOURCE_READING'}
              and 'capture' not in ref and 'excerpt' not in ref,
              'source reading mode not documented', 'CLAIM_SOURCE_EVIDENCE_INVALID')
        _need(ref['locus'] == event.get('locator'), 'uncaptured claim locus is outside the recorded precise reading locus',
              'CLAIM_SOURCE_EVIDENCE_INVALID')
    return set(used_scope)


def _pointer(obj, pointer):
    _need(RE.nonempty(pointer) and pointer.startswith('/'), 'process assertion needs a JSON pointer')
    for part in pointer[1:].split('/'):
        # RFC 6901 escaping, without accepting malformed escape spellings.
        rest = part.replace('~0', '').replace('~1', '')
        _need('~' not in rest, 'invalid JSON pointer escape')
        key = part.replace('~1', '/').replace('~0', '~')
        if isinstance(obj, dict) and key in obj:
            obj = obj[key]
        elif isinstance(obj, list) and key.isascii() and key.isdecimal() and str(int(key)) == key and int(key) < len(obj):
            obj = obj[int(key)]
        else:
            raise ClaimError('CLAIM_PROCESS_EVIDENCE_INVALID', 'process assertion locator absent: ' + pointer)
    return obj


def _same_json(left, right):
    # Python considers True == 1; factual normalized assertions must not.
    return json.dumps(left, sort_keys=True, ensure_ascii=False, allow_nan=False) == json.dumps(
        right, sort_keys=True, ensure_ascii=False, allow_nan=False)


def _process_reference(root, ref, claim, proof, sources, index, subject, reports):
    _object(ref, {'id', 'kind', 'record_id', 'id_pointer', 'record_kind', 'locus', 'attribution', 'assertions'},
            label='process reference')
    _need(all(RE.nonempty(ref[k]) for k in ('record_id', 'record_kind', 'locus', 'attribution')),
          'process identity/locus/attribution absent')
    _object(proof, {'reference_id', 'artifact', 'reader_id', 'context_id', 'read_at', 'byte_range'},
            label='external process read proof')
    report = reports['id']
    _need(proof['reader_id'] == report['actor']['id'] and proof['context_id'] == report['actor']['context_id'],
          'process record was not read in the independent ID context', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    read_at = RE.timestamp(proof['read_at'])
    _need(RE.timestamp(report['disclosed_at']) <= read_at <= RE.timestamp(report['completed_at']),
          'process read date is outside the actual ID review', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    raw = RE.read_artifact(root, proof['artifact'])
    record = RE.read_artifact(root, proof['artifact'], json_object=True)
    _need(proof['byte_range'] == [0, len(raw)], 'process record was not read in full', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    RE.binding(record, subject, partial=True)
    _need(set(claim['scope']) <= set(record['scope']), 'process record does not cover the claim scope', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    _need(record.get('kind') == ref['record_kind'] and _pointer(record, ref['id_pointer']) == ref['record_id'],
          'process record identity or kind differs', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    _pointer(record, ref['locus'])
    assertions = _array(ref['assertions'], label='process assertions')
    pointers = []
    for assertion in assertions:
        _object(assertion, {'pointer', 'value'}, label='process assertion')
        pointer = assertion['pointer']; pointers.append(pointer)
        _need(_same_json(_pointer(record, pointer), assertion['value']), 'public process assertion contradicts the actual record',
              'CLAIM_PROCESS_EVIDENCE_INVALID')
    _ids(pointers, label='process assertion locators')
    kind = claim['process_type']
    if kind in {'METHOD', 'READING'}:
        _need(record.get('kind') == 'SOURCE_READ_ATTESTATION', 'process claim lacks actual source read record',
              'CLAIM_PROCESS_EVIDENCE_INVALID')
        sid = record.get('source_id')
        _need(RE.nonempty(sid) and sid in sources, 'process reading source absent', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        _need(sources[sid].get('read_state') == 'READ', 'process source was not actually read', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        events = [e for e in sources[sid].get('read_events', []) if index.get(e.get('evidence_ref')) == proof['artifact']]
        _need(len(events) == 1 and all(record.get(k) == events[0].get(k) for k in ('actor_id', 'context_id', 'at', 'scope', 'locator')),
              'process claim does not identify an actual indexed source reading', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        required = {'/actor_id', '/at', '/source_id'} if kind == 'READING' else {'/method'}
        _need(required <= set(pointers), 'public process claim lacks its substantive normalized facts', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        if kind == 'METHOD':
            case = RE.read_artifact(root, reports['sources']['source_case'], json_object=True)
            _need(sid == case['basis']['source_id'] and record.get('method') == case['basis'],
                  'declared public method differs from verified basis', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        occurred = RE.timestamp(record.get('at'))
        attributed = record.get('actor_id')
    elif kind == 'OWNER_DECISION':
        _need(record.get('kind') in {'EDITORIAL_DECISION', 'PUBLICATION_CONSENT', 'HUMAN_REVIEW_WAIVER'} and
              record.get('status') == 'APPROVED' and RE.nonempty(record.get('verbatim')),
              'public decision claim lacks a matching approved decision source record', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        _need({'/owner_id', '/status', '/issued_at', '/kind'} <= set(pointers),
              'decision claim does not specify owner, purpose, status and date', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        occurred = RE.timestamp(record.get('issued_at')); attributed = record.get('owner_id')
    else:
        _need(any(record == r for r in reports.values()), 'process review is not an actual verified report', 'CLAIM_PROCESS_EVIDENCE_INVALID')
        _need({'/actor', '/result', '/completed_at'} <= set(pointers), 'public review assertion lacks exact reviewer/result/date',
              'CLAIM_PROCESS_EVIDENCE_INVALID')
        occurred = RE.timestamp(record.get('completed_at')); attributed = record.get('actor', {}).get('id')
    _need(occurred <= read_at and ref['attribution'] == attributed and claim['attribution'] == attributed,
          'public process date/attribution differs', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    if kind != 'REVIEW':
        auth = record.get('authenticated_source')
        _need(isinstance(auth, dict) and auth.get('actor_id') == attributed and
              all(RE.nonempty(auth.get(k)) for k in ('uri', 'record_id')),
              'process source attribution absent', 'CLAIM_PROCESS_EVIDENCE_INVALID')


def _reviews(root, manifest_ref, manifest, units, claims, reports, subject):
    expected_claims = set(claims)
    expected_nonclaims = {uid for uid, u in units.items() if u['kind'] == 'NON_CLAIM'}
    contexts = {manifest['author']['context_id']}
    for name in ('author', 'core', 'apparatus'):
        if name in reports:
            context = reports[name].get('actor', {}).get('context_id')
            _need(RE.nonempty(context), 'prior report context absent', 'CLAIM_INDEPENDENCE_INVALID')
            contexts.add(context)
    process_proofs, reviewed = {}, {}
    for gate, kind in GATES.items():
        report = reports.get(gate)
        _envelope(report, kind, subject)
        context = report['actor']['context_id']
        independence = report.get('independence')
        _need(context not in contexts and isinstance(independence, dict) and
              independence.get('author_context_available') is False and independence.get('prior_exposure') == 'NONE',
              'claim controls need separate clean recorded reviewer contexts', 'CLAIM_INDEPENDENCE_INVALID')
        contexts.add(context)
        review = _object(report.get('claim_review'), {'schema', 'manifest', 'components', 'inventory',
                         'inventory_method', 'inventory_read_at', 'inventory_checks', 'claims', 'non_claims',
                         'process_records'}, label=gate + ' claim review')
        _need(review['schema'] == 'suttaflow-claim-review-v2' and review['manifest'] == manifest_ref,
              gate + ' report does not pin the current full claim manifest', 'CLAIM_REVIEW_INVALID')
        _need(review['components'] == manifest['components'], 'review component references differ', 'CLAIM_REVIEW_INVALID')
        _need(review['inventory_method'] == 'FULL_COMPONENT_READING' and review['inventory'] == manifest['inventory'],
              gate + ' lacks its full independently recorded sentence/subclaim inventory', 'CLAIM_REVIEW_INVALID')
        _checks(review['inventory_checks'], INVENTORY_CHECKS)
        _need(RE.timestamp(manifest['prepared_at']) <= RE.timestamp(report.get('disclosed_at')) <=
              RE.timestamp(review['inventory_read_at']) <= RE.timestamp(report['completed_at']),
              'claim inventory review chronology differs', 'CLAIM_REVIEW_INVALID')
        nonclaims = {}
        for row in _array(review['non_claims'], empty=True, label='reviewed non-claims'):
            _object(row, {'unit_id', 'role', 'text', 'reason'}, label='non-claim assessment')
            uid = row['unit_id']
            _need(RE.nonempty(uid) and uid in expected_nonclaims and uid not in nonclaims,
                  'orphan/duplicate reviewed non-claim', 'CLAIM_REVIEW_INVALID')
            _need(row['role'] == units[uid]['role'] and row['text'] == units[uid]['text'] and RE.nonempty(row['reason']),
                  'non-claim role was not specifically assessed', 'CLAIM_REVIEW_INVALID')
            nonclaims[uid] = row
        _need(set(nonclaims) == expected_nonclaims, 'technical exclusions lack separate role review', 'CLAIM_REVIEW_INVALID')
        rows, finding_links = {}, {}
        for row in _array(review['claims'], label='per-claim review'):
            _object(row, {'claim_id', 'sentence_id', 'text', 'scope', 'kind', 'provenance', 'reference_ids',
                          'checks', 'result', 'confidence', 'finding_ids'}, label='claim assessment')
            uid = row['claim_id']
            _need(RE.nonempty(uid) and uid in expected_claims and uid not in rows,
                  'orphan/duplicate claim assessment', 'CLAIM_REVIEW_INVALID')
            claim = claims[uid]; unit = units[uid]
            _need(all(row[k] == claim[k] for k in ('scope', 'kind', 'provenance')) and
                  row['sentence_id'] == unit['sentence_id'] and row['text'] == unit['text'],
                  'claim assessment text/scope/type differs', 'CLAIM_REVIEW_INVALID')
            _need(_ids(row['reference_ids'], label='review reference IDs') == [r['id'] for r in claim['references']],
                  'claim assessment source/locus references differ', 'CLAIM_REVIEW_INVALID')
            _need(row['result'] in ('PASS', 'PASS_WITH_NOTES'), 'claim review is unperformed or unresolved', 'CLAIM_REVIEW_INVALID')
            _enum(row['confidence'], CONFIDENCE, 'assessment confidence')
            allow_na = set()
            if gate == 'ik' and claim['kind'] == 'PROCESS':
                allow_na = CHECKS['ik'] - {'claim_type', 'support_scope'}
            elif gate == 'id':
                allow_na = {'process_record_truth'} if claim['kind'] == 'CONTENT' else {'direct_vs_indirect', 'alternatives_uncertainty'}
            elif gate == 'ir':
                allow_na = ({'description_neutrality'} if unit['region_role'] != 'DESCRIPTION' else set()) | (
                            {'interpretation_clarity'} if unit['region_role'] != 'INTERPRETATION' else set())
            _checks(row['checks'], CHECKS[gate], allow_na=allow_na)
            for fid in _ids(row['finding_ids'], empty=True, label='claim finding IDs'):
                _need(fid not in finding_links, 'finding assigned more than once', 'CLAIM_FINDING_INVALID')
                finding_links[fid] = uid
            rows[uid] = row
        _need(set(rows) == expected_claims, gate + ' has omitted claims/subclaims', 'CLAIM_REVIEW_INVALID')
        findings = report['findings']
        _need(set(_ids([f.get('id') if isinstance(f, dict) else None for f in findings], empty=True,
                       label='report finding IDs')) == set(finding_links),
              'report has unassigned or missing findings', 'CLAIM_FINDING_INVALID')
        for finding in findings:
            uid = finding_links[finding['id']]; row = rows[uid]
            RE.issue_closed(finding, subject, root, closed_at=report['completed_at'], allow_notes=report['result'] == 'PASS_WITH_NOTES')
            _need(finding.get('claim_id') == uid and finding.get('sentence_id') == row['sentence_id'] and
                  finding.get('quote') == row['text'] and finding.get('actor') == report['actor'] and
                  finding.get('source_loci') == [{'reference_id': r['id'], 'locus': r['locus']} for r in claims[uid]['references']],
                  'finding lacks its exact current claim, source locus or executor', 'CLAIM_FINDING_INVALID')
            _need(all(RE.nonempty(finding.get(k)) for k in ('defect_type', 'proposal')) and
                  finding.get('confidence') in CONFIDENCE,
                  'finding type/proposal/confidence absent', 'CLAIM_FINDING_INVALID')
            _need(RE.timestamp(report['disclosed_at']) <= RE.timestamp(finding.get('assessed_at')) <= RE.timestamp(report['completed_at']),
                  'finding assessment date outside review', 'CLAIM_FINDING_INVALID')
        for uid, row in rows.items():
            notes = [f for f in findings if f['id'] in row['finding_ids'] and f['status'] == 'ACCEPTED_NONBLOCKING']
            _need((row['result'] == 'PASS_WITH_NOTES') == bool(notes), 'per-claim note result differs from finding ledger', 'CLAIM_FINDING_INVALID')
        records = _array(review['process_records'], empty=True, label='external process records')
        _need(gate == 'id' or not records, 'process artifact intake belongs to ID; other gates cite the same manifest references')
        if gate == 'id':
            for proof in records:
                _need(isinstance(proof, dict) and RE.nonempty(proof.get('reference_id')),
                      'process read proof ID absent', 'CLAIM_PROCESS_EVIDENCE_INVALID')
                _need(proof['reference_id'] not in process_proofs, 'duplicate process read proof', 'CLAIM_PROCESS_EVIDENCE_INVALID')
                process_proofs[proof['reference_id']] = proof
        reviewed[gate] = sorted(rows)
    return process_proofs, reviewed


def _validate(root, manifest_ref, subject, bundle, source_case, reports):
    _need(isinstance(subject, dict) and isinstance(bundle, dict) and isinstance(reports, dict),
          'verified subject, bundle and reports must be objects', 'CLAIM_INPUT_INVALID')
    _need(all(RE.nonempty(subject.get(k)) for k in ('subject_id', 'revision_id')),
          'verified subject identity/revision absent', 'CLAIM_INPUT_INVALID')
    RE.scope(subject.get('scope'))
    _need(bundle == RE.read_artifact(root, subject.get('content'), json_object=True),
          'bundle differs from the current subject bytes', 'CLAIM_BINDING_INVALID')
    _need(bundle.get('schema') == 'suttaflow-publication-bundle-v2' and
          all(bundle.get(k) == subject.get(k) for k in ('subject_id', 'revision_id', 'scope')),
          'bundle subject/revision/scope differs', 'CLAIM_BINDING_INVALID')
    _need(bundle.get('claim_ledger') == manifest_ref,
          'bundle does not pin this claim manifest', 'CLAIM_BINDING_INVALID')
    manifest = RE.read_artifact(root, manifest_ref, json_object=True)
    _object(manifest, {'schema', 'subject_id', 'revision_id', 'scope', 'components', 'basis',
                       'author', 'prepared_at', 'inventory', 'claims'}, label='claim manifest')
    _need(manifest['schema'] == 'suttaflow-claim-ledger-v2' and
          all(manifest[k] == subject.get(k) for k in ('subject_id', 'revision_id', 'scope')),
          'claim manifest identity/revision/scope differs', 'CLAIM_BINDING_INVALID')
    _actor(manifest['author']); prepared = RE.timestamp(manifest['prepared_at'])
    components = _object(manifest['components'], COMPONENTS, label='claim components')
    raw = {}
    for name in COMPONENTS:
        _need(components[name] == bundle.get(name), 'manifest component reference differs: ' + name, 'CLAIM_BINDING_INVALID')
        raw[name] = RE.read_artifact(root, bundle[name])
        if name != 'core':
            try:
                raw[name].decode('utf-8')
            except UnicodeError as exc:
                raise ClaimError('CLAIM_INVENTORY_INCOMPLETE', 'claim components must be full UTF-8 text') from exc
    units, sentence_count = _inventory(manifest['inventory'], raw)
    sources, index = _sources(root, source_case, reports, subject)
    basis = _object(manifest['basis'], {'source_id', 'edition', 'language'}, label='frozen source basis')
    sid = basis['source_id']
    _need(RE.nonempty(sid) and sid in sources and sid == source_case.get('basis', {}).get('source_id') and
          all(basis[k] == sources[sid].get(k) for k in ('edition', 'language')),
          'frozen source basis/edition differs', 'CLAIM_SOURCE_EVIDENCE_INVALID')
    claims, all_references, process_refs = {}, set(), {}
    for claim in _array(manifest['claims'], label='claim ledger'):
        _object(claim, {'id', 'kind', 'provenance', 'scope', 'attribution', 'uncertainty', 'dependencies', 'references'},
                {'process_type'}, label='claim')
        uid = claim['id']
        _need(RE.nonempty(uid) and uid in units and units[uid]['kind'] == 'CLAIM' and uid not in claims,
              'claim has no matching unique inventory unit', 'CLAIM_INVENTORY_INCOMPLETE')
        _scope(claim['scope'], subject, label='claim scope')
        _need(RE.nonempty(claim['attribution']) and RE.nonempty(claim['uncertainty']), 'claim attribution/uncertainty absent')
        _ids(claim['dependencies'], empty=True, label='claim dependencies')
        kind = _enum(claim['kind'], {'CONTENT', 'PROCESS'}, 'claim kind')
        if kind == 'CONTENT':
            _enum(claim['provenance'], PROVENANCE, 'K/P/W/T/H provenance')
            _need('process_type' not in claim, 'content claim cannot bypass canon review as process')
        else:
            _need(claim['provenance'] is None and units[uid]['region_role'] in PROCESS_REGIONS,
                  'doctrinal/Opis/Interpretacja claim cannot be exempted as PROCESS', 'CLAIM_PROCESS_EVIDENCE_INVALID')
            _enum(claim.get('process_type'), PROCESS_TYPES, 'process claim type')
        coverage = set(); canonical_scope = set()
        attribution_scopes: dict[str, set[str]] = {}
        for ref in _array(claim['references'], label='claim source/locus references'):
            _need(isinstance(ref, dict) and RE.nonempty(ref.get('id')) and ref['id'] not in all_references,
                  'reference identity absent or duplicated')
            all_references.add(ref['id'])
            _need(ref.get('kind') == ('SOURCE' if kind == 'CONTENT' else 'PROCESS'), 'reference kind differs from claim type')
            if kind == 'CONTENT':
                cited_scope = _source_reference(root, ref, claim, sources, index, subject, prepared)
                coverage |= cited_scope
                if ref['source_id'] == sid or sources[ref['source_id']].get('evidence_kind') in {'SOURCE_TEXT', 'PARALLEL'}:
                    canonical_scope |= cited_scope
                attribution_scopes.setdefault(ref['attribution'], set()).update(cited_scope)
            else:
                process_refs[ref['id']] = (ref, claim)
        if kind == 'CONTENT':
            _need(set(claim['scope']) <= coverage and set(claim['scope']) <= canonical_scope,
                  'claim lacks read canonical context for its whole declared scope', 'CLAIM_SOURCE_EVIDENCE_INVALID')
            if claim['provenance'] in {'K', 'P', 'T'}:
                _need(set(claim['scope']) <= attribution_scopes.get(claim['attribution'], set()),
                      'attributed position does not cover the claim scope in its own cited source readings',
                      'CLAIM_SOURCE_EVIDENCE_INVALID')
            else:
                _need(claim['attribution'] == manifest['author']['id'], 'W/H must disclose the actual inference/hypothesis author')
        claims[uid] = claim
    _need(set(claims) == {uid for uid, u in units.items() if u['kind'] == 'CLAIM'},
          'sentence/subclaim inventory contains omitted claims', 'CLAIM_INVENTORY_INCOMPLETE')
    for uid, claim in claims.items():
        _need(uid not in claim['dependencies'] and set(claim['dependencies']) <= set(claims),
              'claim dependency is self-referential or orphaned')
    proofs, reviewed = _reviews(root, manifest_ref, manifest, units, claims, reports, subject)
    _need(set(proofs) == set(process_refs), 'process claims have missing/orphan external record evidence', 'CLAIM_PROCESS_EVIDENCE_INVALID')
    for rid, (ref, claim) in process_refs.items():
        _process_reference(root, ref, claim, proofs[rid], sources, index, subject, reports)
    return {'sentences': sentence_count, 'claims': len(claims),
            'non_claim_units': len(units) - len(claims), 'reviewed_claim_ids': reviewed,
            'component_bytes': {name: len(raw[name]) for name in ('apparatus', 'interpretation')}}


def validate(root, manifest_ref, *, subject, bundle, source_case, reports):
    """Return CLAIM_EVIDENCE_READY/HOLD; publication readiness is always false.

The bundle pins the manifest. The manifest pins components, never itself, the
bundle hash or later reports. Each verified external IK/ID/IR report pins the
bundle and manifest. Source/read/process artifacts are resolved externally.
"""
    result: dict[str, Any] = {'schema': 'suttaflow-claim-evidence-result-v2', 'status': 'HOLD',
              'ready_for_publication': False, 'verification_level': 'STRUCTURAL_EVIDENCE_ONLY',
              'reasons': [], 'summary': None}
    try:
        result['summary'] = _validate(root, manifest_ref, subject, bundle, source_case, reports)
    except ClaimError as exc:
        result['reasons'].append({'code': exc.code, 'message': str(exc)})
    except RE.EvidenceError as exc:
        result['reasons'].append({'code': 'CLAIM_ARTIFACT_OR_BINDING_INVALID', 'message': str(exc)})
    except (TypeError, KeyError, AttributeError, ValueError, OverflowError) as exc:
        result['reasons'].append({'code': 'CLAIM_INPUT_INVALID', 'message': type(exc).__name__ + ': ' + str(exc)})
    else:
        result['status'] = READY
    return result
