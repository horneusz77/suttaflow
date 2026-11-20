"""Separate editorial closure adapter (SF-RULE-QA-003/005, CORE-002, FMT-007).

It verifies a frozen evidence package; it never sends, publishes, activates a
Standard, or substitutes structural checks for a reviewer's actual reading.
Production use requires an authenticated intake and the original real reports.
"""
from __future__ import annotations
from urllib.parse import urlsplit, parse_qs
from . import release_evidence as RE
from . import status_axes as SA
from . import publication_inputs as PI
from . import publication_parts as PP
from . import claim_ledger as CL
from . import publication_metadata as PM
from . import native_product as NP

REQUIRED_GATES = {
    "sources": "SOURCE_READ_REVIEW", "coverage": "FULL_COVERAGE_REVIEW",
    "apparatus": "APPARAT_REVIEW", "ik": "APARAT_IK", "id": "APARAT_ID", "ir": "APARAT_IR",
    "format_native": "FORMAT_NATIVE", "format_pdf": "FORMAT_PDF",
    "translation_log": "TRANSLATION_LOG_READBACK",
}


def _permanent_uri(value):
    if not RE.nonempty(value):
        raise RE.EvidenceError('persistent PDF URI absent')
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise RE.EvidenceError('persistent PDF URI malformed') from exc
    if parsed.scheme != 'https' or not parsed.hostname or not parsed.path or parsed.username or parsed.password:
        raise RE.EvidenceError('PDF needs a persistent HTTPS location, not a session path')
    if any(k.lower() in {'expires', 'signature', 'token', 'se', 'sig'} or
           k.lower().startswith(('x-goog-', 'x-amz-')) for k in parse_qs(parsed.query)):
        raise RE.EvidenceError('a temporary signed download URL is not a persistent PDF reference')
    return value


def _native_text(doc):
    body = doc.get('body')
    if not isinstance(body, dict):
        tabs = doc.get('tabs')
        if not isinstance(tabs, list) or not tabs or not isinstance(tabs[0], dict):
            raise RE.EvidenceError('native log body absent')
        body = tabs[0].get('body')
        if not isinstance(body, dict):
            nested = tabs[0].get('documentTab')
            body = nested.get('body') if isinstance(nested, dict) else None
    if not isinstance(body, dict) or not isinstance(body.get('content'), list):
        raise RE.EvidenceError('native log content absent')
    pieces = []

    def walk(items):
        for item in items:
            if not isinstance(item, dict):
                raise RE.EvidenceError('native log element malformed')
            paragraph = item.get('paragraph', {})
            for element in paragraph.get('elements', []):
                content = element.get('textRun', {}).get('content', '')
                if not isinstance(content, str):
                    raise RE.EvidenceError('native log text malformed')
                pieces.append(content)
            for row in item.get('table', {}).get('tableRows', []):
                for cell in row.get('tableCells', []):
                    walk(cell.get('content', []))
    try:
        walk(body['content'])
    except (AttributeError, TypeError) as exc:
        raise RE.EvidenceError('native log structure malformed') from exc
    return ''.join(pieces)


def _log_readback(report, reports, root, subject):
    doc = RE.read_artifact(root, report.get('artifact'), json_object=True)
    for field, source in (('log_document_id', 'documentId'), ('log_document_revision_id', 'revisionId')):
        if not RE.nonempty(report.get(field)) or report[field] != doc.get(source):
            raise RE.EvidenceError('log readback identity or revision differs')
    text = _native_text(doc)
    entry = report.get('entry_text'); entry_id = report.get('entry_id')
    if not RE.nonempty(entry) or not RE.nonempty(entry_id) or text.count(entry) != 1 or text.count(entry_id) != 1:
        raise RE.EvidenceError('exact unique log entry was not read back')
    for token in (entry_id, subject['subject_id'], subject['revision_id'],
                  reports.get('format_native', {}).get('document_id'),
                  reports.get('format_native', {}).get('document_revision_id'),
                  reports.get('format_pdf', {}).get('permanent_uri')):
        if not RE.nonempty(token) or token not in entry:
            raise RE.EvidenceError('log does not identify the current candidate, native revision and persistent PDF')
    written = RE.timestamp(report.get('written_at'))
    if written > RE.timestamp(report['completed_at']):
        raise RE.EvidenceError('log readback precedes writing')
    dependencies = ('author', 'core', 'apparatus', 'ik', 'id', 'ir',
                    'sources', 'coverage', 'format_native', 'format_pdf', 'final_editor')
    if any(RE.timestamp(reports[key]['completed_at']) > written for key in dependencies if key in reports):
        raise RE.EvidenceError('log completion was written before its required review/FORMAT/notes gates')


def _bound_source_case(report, root, subject):
    case = RE.read_artifact(root, report.get('source_case'), json_object=True)
    RE.binding(case, subject)
    return case


def _source_reads(report, root, subject, evidence, owner, method_axis, case):
    """Recheck the collection contract, never trust a chosen required-ID list.

    Actual book-reading attestations remain admissible without a full capture.
    Summary states and declared extra requirements can only constrain the gate;
    they cannot relax the requirements of the versioned source contract.
    """
    from . import source_contract as SC
    index = RE.read_artifact(root, report.get('source_evidence_index'), json_object=True)
    RE.binding(case, subject)
    if case.get('intended_publication') is not True:
        raise RE.EvidenceError('finalization requires source evidence for the actual intended public use')
    trusted = owner.get('source_contract_decisions', {}) if isinstance(owner, dict) else {}
    result = SC.validate(case, index, root=root, evidence=evidence, trusted_decisions=trusted,
                         method_axis=method_axis)
    if result['status'] != SC.READY:
        raise RE.EvidenceError('collection source contract is ' + result['status'] + ': ' +
                               '; '.join(p['requirement_id'] + ' ' + p['message'] for p in result['reasons']))
    states = {s['source_id']: 'READ' if s['read_state'] == 'READ' else s['availability_status']
              for s in case['sources']}
    if report.get('read_states', states) != states:
        raise RE.EvidenceError('source summary differs from the actual collection evidence')
    required = report.get('required_source_ids', [])
    if required:
        required = RE.scope(required)
        if any(states.get(sid) != 'READ' for sid in required):
            raise RE.EvidenceError('a declared additional mandatory source has not been read')
    elif not isinstance(required, list):
        raise RE.EvidenceError('additional required source IDs malformed')
    exceptions = report.get('source_exceptions', [])
    if not isinstance(exceptions, list):
        raise RE.EvidenceError('source exceptions malformed')
    notes = {i['id'] for i in report['findings'] if i['status'] == 'ACCEPTED_NONBLOCKING'}
    accounted = set()
    for exc in exceptions:
        if not isinstance(exc, dict) or not RE.nonempty(exc.get('source_id')):
            raise RE.EvidenceError('source exception identity absent')
        sid = exc['source_id']
        if sid in accounted or sid in required or states.get(sid) not in SC.ABSENT or exc.get('finding_id') not in notes:
            raise RE.EvidenceError('optional source exception lacks an individual nonblocking assessment')
        query = RE.read_artifact(root, exc.get('query_evidence'), json_object=True)
        if query.get('source_id') != sid or query.get('result') != states[sid]:
            raise RE.EvidenceError('source search evidence differs')
        RE.timestamp(query.get('performed_at'))
        attempts = query.get('attempts')
        if not isinstance(attempts, list) or not attempts or not all(isinstance(a, dict) and RE.nonempty(a.get('uri')) and RE.nonempty(a.get('outcome')) for a in attempts):
            raise RE.EvidenceError('actual search attempts absent')
        accounted.add(sid)
    if accounted != {sid for sid, state in states.items() if state != 'READ'}:
        raise RE.EvidenceError('CAPTURED, unchecked, or unexplained missing source cannot pass')
    return case


def _coverage(report, source_case, root, subject, core_subject):
    from . import source_contract as SC
    if report.get("technical_verdict") != "TECHNICAL_EVIDENCE_READY" or report.get("ready_for_publication") is not False:
        raise RE.EvidenceError("technical readiness is absent or improperly claims publication")
    material_pali = source_case is None or SC.is_pali(source_case['basis']['language']) or any(
        decision.get('material') is True for decision in source_case['lexical_decisions'])
    allowed_dpd = {'VERIFIED'} if material_pali else {'NOT_APPLICABLE', 'VERIFIED'}
    if not isinstance(report.get('dpd_status'), str) or report["dpd_status"] not in allowed_dpd:
        raise RE.EvidenceError("required DPD verification absent")
    source = RE.scope(report.get("source_units")); target = RE.scope(report.get("target_units"))
    if source != subject['scope'] or source_case is None or source != source_case['scope']:
        raise RE.EvidenceError('coverage source denominator differs from the independently bound full task scope')
    if target != PI.target_units(root, subject, core_subject):
        raise RE.EvidenceError('coverage target denominator differs from the complete CORE byte manifest')
    pairs = report.get("pairs")
    if not isinstance(pairs, list) or not pairs:
        raise RE.EvidenceError("coverage relations absent")
    left, right = [], []
    resolved_ids = {i['id'] for i in report.get('findings', [])
                    if i.get('status') in {'RESOLVED', 'REJECTED_WITH_EVIDENCE', 'ACCEPTED_NONBLOCKING'}}
    for pair in pairs:
        if not isinstance(pair, dict) or pair.get("status") not in ("OK", "OK_NOTE", "MINOR", "VARIANT"):
            raise RE.EvidenceError("unknown or unresolved alignment state")
        if pair["status"] != "OK" and (not RE.nonempty(pair.get("resolved_issue_id")) or pair["resolved_issue_id"] not in resolved_ids):
            raise RE.EvidenceError("non-OK relation lacks the current resolved issue record")
        left.extend(RE.scope(pair.get("pali"))); right.extend(RE.scope(pair.get("pl")))
    if set(left) != set(source) or set(right) != set(target) or len(left) != len(set(left)) or len(right) != len(set(right)):
        raise RE.EvidenceError("unmapped, unknown, or multiply mapped units")


def _method_axis_compatibility(case, axes):
    """Check the bound method claim even when its full source gate will fail.

    This diagnostic does not make the case source-verified. Coverage and public
    finalization still receive it only after the complete collection contract.
    """
    basis = case.get('basis')
    if not isinstance(basis, dict) or not RE.nonempty(basis.get('method')):
        raise RE.EvidenceError('source-case method record absent or malformed')
    method = basis['method']
    expected = {'PALI_FIRST': {'PALI_FIRST_UDOKUMENTOWANY', 'PALI_FIRST_DEKLAROWANY'},
                'EN_PL_HH': {'EN_PL_HH'}, 'EN_PL_OTHER': {'EN_PL_INNY'},
                'SOURCE_FIRST_OTHER': {'NIEUSTALONE'}}
    if method == 'INDIRECT_SOURCE_FIRST':
        sources = case.get('sources')
        if not isinstance(sources, list) or not RE.nonempty(basis.get('intermediary_source_id')):
            raise RE.EvidenceError('indirect method does not identify its source/intermediary')
        candidates = [s for s in sources if isinstance(s, dict) and
                      s.get('source_id') == basis['intermediary_source_id']]
        if len(candidates) != 1 or not RE.nonempty(candidates[0].get('language')):
            raise RE.EvidenceError('indirect method intermediary is absent, ambiguous or lacks its language')
        expected[method] = {'NIEUSTALONE'}
    if method not in expected:
        raise RE.EvidenceError('source-case method is unknown')
    if axes['B']['value'] not in expected[method]:
        raise RE.EvidenceError('axis B contradicts the bound source-case method and source/intermediary')


def _method_disclosure(case, source_report, axes, evidence, root):
    index = RE.read_artifact(root, source_report['source_evidence_index'], json_object=True)
    key = case['public_sources'][-1]['disclosure_evidence_ref']
    disclosure = RE.read_artifact(root, index[key], json_object=True)
    if 'method_axis' in disclosure and disclosure['method_axis'] != axes['B']['value']:
        raise RE.EvidenceError('public method declaration contradicts verified axis B')
    human = {'BRAK': 'NO_HUMAN_REVIEW', 'ODSTĄPIONO': 'NO_HUMAN_REVIEW',
             'CZĘŚCIOWA': 'PARTIAL_HUMAN_REVIEW', 'PEŁNA': 'FULL_HUMAN_REVIEW'}[axes['D']['value']]
    if disclosure['human_review_status'] != human:
        raise RE.EvidenceError('public human review declaration contradicts verified axis D')
    if evidence.get('human_review') and axes['D']['value'] in {'BRAK', 'ODSTĄPIONO'}:
        raise RE.EvidenceError('supplied human review must be reconciled with axis D and the public declaration')


def _parts_declared(core, pair):
    """A revealed partition cannot become optional by omitting its manifest."""
    mode = core.get('review_mode', 'WHOLE')
    if not isinstance(mode, str) or mode not in {'WHOLE', 'PARTS'}:
        raise RE.EvidenceError('CORE review_mode must be WHOLE or PARTS')
    if 'split' in core and type(core['split']) is not bool:
        raise RE.EvidenceError('CORE split declaration must be boolean')
    markers = {'parts_manifest', 'parts_review', 'parts', 'part_ids'}
    return (mode == 'PARTS' or core.get('split') is True or bool(markers & set(core)) or
            any('parts_review' in report for report in pair or ()))


def _parts_source(root, source_report, case, subject, core_subject):
    """Select the actual source before inspecting the parts manifest.

    Captured input is selected by the verified edition's capture identity. A
    book/direct original may instead use a SOURCE_READ_REVIEW.core_source_scope
    already present in its external evidence index. Every such original reading
    binds RAW CORE and must equal a validated bundle reading in every other
    field. This preserves the actual actor, context, time, scope and metadata
    without the bundle -> parts -> reading -> bundle hash cycle.
    """
    index = RE.read_artifact(root, source_report['source_evidence_index'], json_object=True)
    basis = case['basis']
    sid = basis['intermediary_source_id'] if basis['indirect'] else basis['source_id']
    source = next(s for s in case['sources'] if s['source_id'] == sid)
    if source.get('read_state') != 'READ' or source.get('used') is not True or set(source['read_scope']) != set(subject['scope']):
        raise RE.EvidenceError('parts require the actually read full CORE source scope')
    if source['capture_state'] == 'CAPTURED':
        refs = [r for r in index.values() if isinstance(r, dict) and
                r.get('path') == source['capture_path'] and r.get('sha256') == source['capture_sha256']]
        if not refs or any(r != refs[0] for r in refs):
            raise RE.EvidenceError('actual CORE capture lacks an unambiguous verified source reference')
        RE.read_artifact(root, refs[0])
        return refs[0]

    ref = source_report.get('core_source_scope')
    if not isinstance(ref, dict) or ref not in index.values():
        raise RE.EvidenceError('uncaptured CORE source needs its independently indexed source-scope artifact')
    scoped = RE.read_artifact(root, ref, json_object=True)
    if (scoped.get('schema') != 'suttaflow-core-source-scope-v2' or scoped.get('source_id') != sid or
            any(scoped.get(k) != subject[k] for k in ('subject_id', 'revision_id', 'scope'))):
        raise RE.EvidenceError('indexed source scope differs from the actual CORE source or full task')
    units = scoped.get('units')
    if not isinstance(units, list) or not all(isinstance(u, dict) for u in units) or RE.scope([u.get('id') for u in units]) != subject['scope']:
        raise RE.EvidenceError('indexed book/direct units do not cover the complete ordered source scope')
    verified = [RE.read_artifact(root, index[event['evidence_ref']], json_object=True)
                for event in source['read_events']]
    for unit in units:
        original_ref = unit.get('reading_ref')
        if not isinstance(original_ref, dict) or original_ref not in index.values():
            raise RE.EvidenceError('original scoped reading is absent from the verified source evidence index')
        original = RE.read_artifact(root, original_ref, json_object=True)
        RE.binding(original, core_subject, partial=True)
        if (original.get('kind') != 'SOURCE_READ_ATTESTATION' or
                not isinstance(original.get('read_mode'), str) or
                original['read_mode'] not in {'BOOK_READING', 'DIRECT_SOURCE_READING'} or
                original.get('source_id') != sid or unit['id'] not in original['scope'] or
                original.get('locator') != unit.get('locator')):
            raise RE.EvidenceError('original reading does not identify this CORE source unit and locator')
        identity = {k: v for k, v in original.items() if k != 'content_sha256'}
        if not any(identity == {k: v for k, v in current.items() if k != 'content_sha256'} for current in verified):
            raise RE.EvidenceError('original book/direct reading differs from the actual validated source attestation')
    return ref


def _workflow_order(reports, evidence, owner, axes, root, subject, case):
    """completed_at means the actual completed check, not later file recording.

Source reading/query/lexical events precede coverage; the source report may be
recorded later to check the final bibliography/disclosures before FORMAT.
Parallel IK/ID/IR work is allowed after the general APARAT review.
"""
    edges = [('coverage', 'author'), ('author', 'core'), ('core', 'apparatus'),
             ('apparatus', 'ik'), ('apparatus', 'id'), ('apparatus', 'ir'),
             ('sources', 'format_native'), ('ik', 'format_native'),
             ('id', 'format_native'), ('ir', 'format_native'), ('format_native', 'format_pdf')]
    for before, after in edges:
        if before in reports and after in reports and RE.timestamp(reports[before]['completed_at']) > RE.timestamp(reports[after]['completed_at']):
            raise RE.EvidenceError(before + ' was completed after ' + after)
    for key in ('ik', 'id', 'ir'):
        if key in reports and 'apparatus' in reports and RE.timestamp(reports[key]['disclosed_at']) < RE.timestamp(reports['apparatus']['completed_at']):
            raise RE.EvidenceError('interpretation review was disclosed before completed general APARAT')
    if case is not None and 'coverage' in reports and 'sources' in reports:
        index = RE.read_artifact(root, reports['sources']['source_evidence_index'], json_object=True)
        operations = [e['at'] for s in case['sources'] for e in s['read_events']]
        operations += [q['at'] for q in case['queries']]
        for name in ('lexical_decisions', 'parallel_queries'):
            for rec in case[name]:
                refs = rec['evidence_refs'] if name == 'lexical_decisions' else [rec['evidence_ref']]
                operations += [RE.read_artifact(root, index[k], json_object=True)['at'] for k in refs]
        if any(RE.timestamp(t) > RE.timestamp(reports['coverage']['completed_at']) for t in operations):
            raise RE.EvidenceError('coverage predates actual reading, source queries or lexical decisions')
    if 'translation_log' in reports:
        consent_ids = [axes['E'].get('decision')] + axes['E'].get('also', [])
        for key in consent_ids:
            d = RE.consent(owner, key, 'PUBLICATION_CONSENT', subject, root)
            if RE.timestamp(d['issued_at']) < RE.timestamp(reports['translation_log']['completed_at']):
                raise RE.EvidenceError('owner publication consent precedes the completed final log readback')


def finalize(root, axes, owner, evidence):
    errors: list[dict] = []
    reports: dict[str, dict] = {}
    source_case = None

    def check(code, fn):
        try:
            return fn()
        except RE.EvidenceError as exc:
            errors.append({"code": code, "message": str(exc)})

    def outcome():
        has_notes = any(r.get("result") == "PASS_WITH_NOTES" for r in reports.values())
        return {"schema": "suttaflow-editorial-finalization-v2",
                "verdict": "HOLD" if errors else ("PASS_WITH_NOTES" if has_notes else "PASS"),
                "ready_for_publication": not errors and source_case is not None and source_case['is_synthetic'] is False,
                "is_synthetic": source_case.get('is_synthetic') if source_case is not None else None,
                "standard_activated": False, "errors": errors,
                "completed_gates": sorted(reports),
                "scope": evidence.get("subject", {}).get("scope", []) if isinstance(evidence, dict) and isinstance(evidence.get("subject"), dict) else []}

    if not isinstance(axes, dict) or any(not isinstance(axes.get(k), dict) for k in "ABCDE"):
        errors.append({"code": "FINALIZER_INPUT_INVALID", "message": "axes and each axis must be objects"})
        return outcome()
    subject = check("FINALIZER_SUBJECT_INVALID", lambda: RE.subject_from(
        evidence, root, subject_id=axes.get("sutta"), revision_id=axes.get("version")))
    if subject is None:
        return outcome()
    core_subject = check("FINALIZER_COMPONENTS_INVALID", lambda: RE.core_view(evidence, subject, root))
    if core_subject is None:
        return outcome()
    errors.extend(SA.validate(axes, owner, True, "NOT_INFERRED", root=root, evidence=evidence))
    if any(e.get('code') in {'STATUS_AXIS_INVALID_STRUCTURE', 'STATUS_AXIS_INVALID_VALUE'} for e in errors):
        return outcome()
    if axes.get("C", {}).get("value") != "PEŁNA_AI":
        errors.append({"code": "FINALIZER_FULL_REVIEW_REQUIRED", "message": "full executed review is required"})
    if axes.get("E", {}).get("value") not in {"DOPUSZCZONE_JAKO_OPRACOWANIE_AI", "DOPUSZCZONE_PO_RECENZJI"}:
        errors.append({"code": "FINALIZER_OWNER_CONSENT_REQUIRED", "message": "separate publication consent absent"})
    pair = check("FINALIZER_CORE_REVIEW_INVALID", lambda: RE.full_ai(evidence, subject, root))
    if pair:
        reports["author"], reports["core"] = pair

    def freeze():
        core = evidence["core"]
        rec = RE.read_artifact(root, core.get("freeze_record"), json_object=True)
        RE.binding(rec, core_subject)
        frozen_at = RE.timestamp(core.get("frozen_at"))
        ref = evidence.get("reviewer_report")
        if not isinstance(ref, dict) or rec.get("kind") != "CORE_FREEZE" or rec.get("frozen_at") != core.get("frozen_at") or rec.get("report_sha256") != ref.get("sha256"):
            raise RE.EvidenceError("CORE freeze does not pin the original report")
        if pair and any(RE.timestamp(r["completed_at"]) > frozen_at for r in pair):
            raise RE.EvidenceError("CORE report was not completed before freezing")
        return frozen_at

    frozen_at = check("FINALIZER_CORE_FREEZE_INVALID", freeze)
    gates = evidence.get("gates")
    if not isinstance(gates, dict):
        errors.append({"code": "FINALIZER_GATES_INVALID", "message": "required report references absent"})
        gates = {}
    elif set(gates) - set(REQUIRED_GATES):
        errors.append({"code": "FINALIZER_GATES_INVALID", "message": "unknown gate references"})
    for key, kind in REQUIRED_GATES.items():
        r = check("FINALIZER_" + key.upper() + "_INVALID", lambda key=key, kind=kind: RE.report(root, gates.get(key), kind, subject))
        if r is not None:
            reports[key] = r

    for key in ("apparatus", "ik", "id", "ir"):
        if key in reports:
            def disclosure(key=key):
                r = reports[key]
                disclosed = RE.timestamp(r.get("disclosed_at"))
                if frozen_at is None or disclosed <= frozen_at or disclosed > RE.timestamp(r["completed_at"]):
                    raise RE.EvidenceError("APARAT was disclosed before the frozen CORE report")
            check("FINALIZER_DISCLOSURE_ORDER_INVALID", disclosure)
    if pair and 'apparatus' in reports:
        if any(reports['apparatus']['actor'].get(field) != pair[1]['actor'].get(field)
               for field in ('id', 'model', 'context_id')):
            errors.append({'code': 'FINALIZER_APPARATUS_REVIEWER_INVALID',
                           'message': 'general APARAT must continue with the same fresh CORE reviewer'})
    if all(k in reports for k in ("ik", "id", "ir")):
        contexts = [reports[k]["actor"]["context_id"] for k in ("ik", "id", "ir")]
        prior_contexts = {r['actor']['context_id'] for r in pair} if pair else set()
        if len(set(contexts)) != 3 or set(contexts) & prior_contexts:
            errors.append({"code": "FINALIZER_INTERPRETATION_INDEPENDENCE_INVALID", "message": "IK/ID/IR need separate reviewer contexts"})
        for key in ("ik", "id", "ir"):
            ind = reports[key].get("independence", {})
            if not isinstance(ind, dict) or ind.get("author_context_available") is not False or ind.get("prior_exposure") != "NONE":
                errors.append({"code": "FINALIZER_INTERPRETATION_INDEPENDENCE_INVALID", "message": "clean interpretation review context not evidenced"})
    if "sources" in reports:
        bound_case = check('FINALIZER_SOURCE_READS_INVALID', lambda: _bound_source_case(
            reports['sources'], root, subject))
        if bound_case is not None:
            check('FINALIZER_METHOD_DISCLOSURE_INVALID', lambda: _method_axis_compatibility(bound_case, axes))
            source_case = check('FINALIZER_SOURCE_READS_INVALID', lambda: _source_reads(
                reports['sources'], root, subject, evidence, owner, axes['B'], bound_case))
            if source_case is not None:
                check('FINALIZER_METHOD_DISCLOSURE_INVALID', lambda: _method_disclosure(source_case, reports['sources'], axes, evidence, root))
    if "coverage" in reports:
        check("FINALIZER_COVERAGE_INVALID", lambda: _coverage(reports["coverage"], source_case, root, subject, core_subject))

    bundle = check('FINALIZER_COMPONENTS_INVALID', lambda: RE.read_artifact(root, subject['content'], json_object=True))
    if bundle is None:
        return outcome()
    divided = check('FINALIZER_PARTS_DECLARATION_INVALID', lambda: _parts_declared(evidence['core'], pair))
    if divided and 'parts_manifest' not in bundle:
        errors.append({'code': 'FINALIZER_PARTS_MANIFEST_REQUIRED',
                       'message': 'the declared divided CORE review has no parts_manifest'})
    elif 'parts_manifest' in bundle:
        def parts():
            if source_case is None or pair is None or frozen_at is None:
                raise RE.EvidenceError('verified sources, original full CORE review and freeze are required before parts')
            source_ref = _parts_source(root, reports['sources'], source_case, subject, core_subject)
            result = PP.validate(root, bundle['parts_manifest'], subject=subject, core_subject=core_subject,
                                 source_ref=source_ref, global_report_ref=evidence['reviewer_report'],
                                 core_freeze_ref=evidence['core']['freeze_record'])
            if result['status'] != PP.READY:
                raise RE.EvidenceError('; '.join(e['code'] + ': ' + e['message'] for e in result['errors']))
            return result
        parts_result = check('FINALIZER_PARTS_INVALID', parts)
        if parts_result is not None:
            reports['parts'] = parts_result

    if 'claim_ledger' not in bundle:
        errors.append({'code': 'FINALIZER_CLAIMS_REQUIRED',
                       'message': 'the full apparatus/interpretation claim manifest is required'})
    else:
        def claims():
            if source_case is None or any(k not in reports for k in ('author', 'core', 'apparatus', 'ik', 'id', 'ir')):
                raise RE.EvidenceError('verified source case and actual CORE/APARAT/IK/ID/IR reports are required')
            result = CL.validate(root, bundle['claim_ledger'], subject=subject, bundle=bundle,
                                 source_case=source_case, reports=reports)
            if result['status'] != CL.READY:
                raise RE.EvidenceError('; '.join(e['code'] + ': ' + e['message'] for e in result['reasons']))
            return result
        claim_result = check('FINALIZER_CLAIMS_INVALID', claims)
        if claim_result is not None:
            reports['claims'] = claim_result

    if "format_native" in reports:
        def native():
            r = reports["format_native"]
            doc = RE.read_artifact(root, r.get("artifact"), json_object=True)
            if not RE.nonempty(r.get("document_id")) or not RE.nonempty(r.get("document_revision_id")) or doc.get("documentId") != r["document_id"] or doc.get("revisionId") != r["document_revision_id"]:
                raise RE.EvidenceError("native document identity or revision differs")
            if not _native_text(doc).strip():
                raise RE.EvidenceError('native content is absent or empty; metadata is not a native document')
            return NP.validate(root, r, bundle)
        check("FINALIZER_NATIVE_ARTIFACT_INVALID", native)
    if "format_pdf" in reports:
        def pdf():
            r = reports["format_pdf"]
            raw = RE.read_artifact(root, r.get("artifact"))
            _permanent_uri(r.get('permanent_uri'))
            pages = r.get('pages_viewed')
            if type(r.get("page_count")) is not int or r["page_count"] <= 0 or not isinstance(pages, list) or any(type(n) is not int for n in pages) or pages != list(range(1, r["page_count"] + 1)):
                raise RE.EvidenceError("not every exported PDF page was reviewed")
            if PI.pdf_page_count(raw) != r['page_count']:
                raise RE.EvidenceError('reviewed page count differs from the actual PDF page tree')
            if r.get("exported_from_document_revision_id") != reports.get("format_native", {}).get("document_revision_id"):
                raise RE.EvidenceError("PDF export and reviewed native revision differ")
        check("FINALIZER_PDF_ARTIFACT_INVALID", pdf)

    if 'publication_metadata' not in bundle:
        errors.append({'code': 'FINALIZER_PUBLICATION_METADATA_REQUIRED',
                       'message': 'the actual completion/revision dates and full public bibliography manifest are required'})
    else:
        def metadata():
            if source_case is None or any(k not in reports for k in ('format_native', 'format_pdf', 'translation_log')):
                raise RE.EvidenceError('verified source case and current native/PDF/LOG reports are required')
            pdf_report = reports['format_pdf']
            recorded = pdf_report.get('publication_metadata')
            if not isinstance(recorded, dict) or recorded.get('source_evidence_index') != reports['sources']['source_evidence_index']:
                raise RE.EvidenceError('metadata source index is not the exact independently verified SOURCE_READ_REVIEW index')
            result = PM.validate(root, bundle['publication_metadata'], subject=subject, source_case=source_case,
                                 native_ref=reports['format_native']['artifact'], pdf_report=pdf_report,
                                 log_ref=gates['translation_log'], requested_channels=bundle.get('requested_channels', []))
            if result['status'] != PM.READY:
                raise RE.EvidenceError('; '.join(e['code'] + ': ' + e['message'] for e in result['errors']))
            return result
        metadata_result = check('FINALIZER_PUBLICATION_METADATA_INVALID', metadata)
        if metadata_result is not None:
            reports['publication_metadata'] = metadata_result

    notes = [i for r in reports.values() for i in r.get("findings", []) if i.get("status") == "ACCEPTED_NONBLOCKING"]
    if notes:
        def accept_notes():
            r = RE.report(root, evidence.get("final_editor_acceptance"), "FINAL_EDITOR_ACCEPTANCE", subject)
            ids = [i["id"] for i in notes]
            if len(ids) != len(set(ids)) or r.get("accepted_note_ids") != sorted(ids):
                raise RE.EvidenceError("final editor must assess every note individually")
            if any(RE.timestamp(r["completed_at"]) < RE.timestamp(reports[k]["completed_at"]) for k in ("format_native", "format_pdf") if k in reports):
                raise RE.EvidenceError("final acceptance precedes FORMAT")
            return r
        accepted = check("FINALIZER_NOTES_ACCEPTANCE_INVALID", accept_notes)
        if accepted:
            reports["final_editor"] = accepted
    if 'translation_log' in reports:
        check('FINALIZER_LOG_READBACK_INVALID', lambda: _log_readback(reports['translation_log'], reports, root, subject))
    # Run only on records already structurally verified by their own gates.
    if not errors:
        check('FINALIZER_WORKFLOW_ORDER_INVALID', lambda: _workflow_order(reports, evidence, owner, axes, root, subject, source_case))
    return outcome()
