"""Bind a recorded consistency review to exact Standard revisions; never certify meaning."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

from sfe.standard_contract import validate


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _registries(baseline: bytes, candidate: bytes) -> tuple[dict, dict]:
    before, after = json.loads(baseline), json.loads(candidate)
    validate(before)
    validate(after)
    from sfe.terminology import KEY, validate_transition
    old_terms, new_terms = (r['reference_data'].get(KEY) for r in (before, after))
    if isinstance(old_terms, dict):
        validate_transition(old_terms, new_terms)
    return before, after


def _changes(before: dict, after: dict) -> list[dict]:
    old = {r['rule_id']: r for r in before['rules']}
    new = {r['rule_id']: r for r in after['rules']}
    ids = set(old) | set(new)
    references = {
        rid: set(re.findall(r'SF-RULE-[A-Z]+-[0-9]+',
                           old.get(rid, {}).get('normative_text', '') + '\n'
                           + new.get(rid, {}).get('normative_text', '')))
        for rid in ids
    }
    changes = []
    for rid in sorted(ids):
        # Activation is reviewed at section level, not repeated for all 89 rules.
        left = {k: v for k, v in old.get(rid, {}).items() if k != 'activation'}
        right = {k: v for k, v in new.get(rid, {}).items() if k != 'activation'}
        if left != right:
            related = references[rid] | {other for other in ids if rid in references[other]}
            changes.append({'target': 'rule:' + rid,
                            'related_rule_ids': sorted((related & ids) - {rid}),
                            'reason': '', 'impact': '', 'analysis': ''})
    for key in sorted((set(before) | set(after)) - {'rules'}):
        if before.get(key) != after.get(key):
            changes.append({'target': 'section:' + key, 'related_rule_ids': [],
                            'reason': '', 'impact': '', 'analysis': ''})
    common = set(old) & set(new)
    if ([r['rule_id'] for r in before['rules'] if r['rule_id'] in common]
            != [r['rule_id'] for r in after['rules'] if r['rule_id'] in common]):
        changes.append({'target': 'section:rules_order', 'related_rule_ids': [],
                        'reason': '', 'impact': '', 'analysis': ''})
    old_states = {rid: r.get('activation') for rid, r in old.items()}
    new_states = {rid: r.get('activation') for rid, r in new.items()}
    if any(old_states[rid] != new_states[rid] for rid in common):
        changes.append({'target': 'section:rule_activation', 'related_rule_ids': [],
                        'reason': '', 'impact': '', 'analysis': ''})
    return changes


def prepare_review(baseline: bytes, candidate: bytes) -> dict:
    before, after = _registries(baseline, candidate)
    return {'schema': 'suttaflow-standard-change-review-v1', 'status': 'DRAFT',
            'baseline_sha256': _sha(baseline), 'candidate_sha256': _sha(candidate),
            'reviewer': '', 'reviewed_at': '', 'decision_source': '',
            'global_analysis': '', 'changes': _changes(before, after),
            'resolved_conflicts': [], 'unresolved_conflicts': [], 'checks': []}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _text(obj: dict, key: str) -> bool:
    return isinstance(obj.get(key), str) and bool(obj[key].strip())


def validate_review(baseline: bytes, candidate: bytes, review: dict, root: Path) -> dict:
    before, after = _registries(baseline, candidate)
    expected = prepare_review(baseline, candidate)
    _require(isinstance(review, dict), 'review must be an object')
    _require(review.get('schema') == expected['schema'] and review.get('status') == 'REVIEWED',
             'completed consistency review required')
    _require(all(review.get(k) == expected[k] for k in ('baseline_sha256', 'candidate_sha256')),
             'stale review: baseline or candidate bytes differ')
    _require(all(_text(review, k) for k in
                 ('reviewer', 'reviewed_at', 'decision_source', 'global_analysis')),
             'review identity, date, source and global analysis required')
    date = datetime.fromisoformat(review['reviewed_at'])
    _require(date.utcoffset() is not None, 'review date requires timezone')
    _require(review.get('unresolved_conflicts') == [], 'unresolved conflicts block the change')
    if before.get('activation') == 'ACTIVE' and baseline != candidate:
        _require(before['version'] != after['version'], 'released version is immutable; create a new candidate')
    known = {r['rule_id'] for r in before['rules'] + after['rules']}
    candidate_ids = {r['rule_id'] for r in after['rules']}
    references = set(re.findall(r'SF-RULE-[A-Z]+-[0-9]+', json.dumps(after, ensure_ascii=False)))
    _require(not references - candidate_ids, 'unknown or removed RULE-ID referenced by candidate')
    items = review.get('changes')
    if not isinstance(items, list) or not all(isinstance(x, dict) for x in items):
        raise ValueError('change reviews must be a list of objects')
    targets = [x.get('target') for x in items]
    expected_targets = {x['target'] for x in expected['changes']}
    _require(all(isinstance(t, str) for t in targets) and len(set(targets)) == len(targets)
             and set(targets) == expected_targets, 'missing, duplicate or extra change review')
    by_target = {x['target']: x for x in expected['changes']}
    for item in items:
        related = item.get('related_rule_ids')
        if not isinstance(related, list):
            raise ValueError('related RULE-IDs must be a list')
        _require(all(isinstance(r, str) for r in related)
                 and len(set(related)) == len(related) and set(related) <= known,
                 'invalid related RULE-ID')
        _require(set(by_target[item['target']]['related_rule_ids']) <= set(related),
                 'referenced or referencing rule missing from related review')
        _require(all(_text(item, k) for k in ('reason', 'impact', 'analysis')),
                 'reason, impact and consistency analysis required for every change')
    conflicts = review.get('resolved_conflicts')
    if not isinstance(conflicts, list):
        raise ValueError('resolved conflicts must be a list')
    for conflict in conflicts:
        _require(isinstance(conflict, dict) and _text(conflict, 'description')
                 and _text(conflict, 'resolution'), 'conflict needs description and resolution')
        rules = conflict.get('rule_ids')
        _require(isinstance(rules, list) and bool(rules)
                 and all(isinstance(r, str) and r in known for r in rules),
                 'conflict needs known RULE-IDs')
    checks = review.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('record actual scoped checks')
    for check in checks:
        _require(isinstance(check, dict) and _text(check, 'path') and _text(check, 'scope')
                 and check.get('result') == 'OK', 'completed scoped check required')
        path = Path(check['path'])
        _require(not path.is_absolute() and (root / path).resolve().is_relative_to(root.resolve()),
                 'check artifact must remain inside review directory')
        raw = (root / path).read_bytes()
        _require(bool(raw) and _sha(raw) == check.get('sha256'), 'check artifact missing, empty or stale')
    return {'status': 'CONSISTENCY_REVIEW_RECORDED', 'reviewed_targets': len(items),
            'baseline_sha256': _sha(baseline), 'candidate_sha256': _sha(candidate),
            'reviewer': review['reviewer'], 'reviewed_at': review['reviewed_at'],
            'semantic_truth_verified': False, 'activation_performed': False}


def main() -> None:
    parser = argparse.ArgumentParser(description='Prepare an unreviewed Standard change checklist.')
    parser.add_argument('baseline', type=Path)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        draft = prepare_review(args.baseline.read_bytes(), args.candidate.read_bytes())
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(draft, ensure_ascii=False, indent=2) + '\n')
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'HOLD: {error}\n')
    print('DRAFT only: perform and record the review before building the changed Standard.')


if __name__ == '__main__':
    main()
