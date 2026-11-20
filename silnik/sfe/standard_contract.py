"""Build a readable registry view; never authenticate approval or activate a release."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


def _same_file(left: Path, right: Path) -> bool:
    return left == right or (left.exists() and right.exists() and left.samefile(right))


def validate(registry: dict) -> None:
    if registry.get('schema') != 'suttaflow-standard-registry-v2':
        raise ValueError('unknown standard registry schema')
    if registry.get('activation') not in ('CANDIDATE', 'ACTIVE'):
        raise ValueError('unknown declared activation state')
    stages = registry.get('stages', [])
    stage_ids = [stage['id'] for stage in stages]
    if not stages or len(set(stage_ids)) != len(stage_ids):
        raise ValueError('stages absent or duplicated')
    rules = registry.get('rules', [])
    ids = [rule['rule_id'] for rule in rules]
    if not rules or len(set(ids)) != len(ids):
        raise ValueError('rules absent or duplicated')
    if registry['activation'] == 'ACTIVE':
        owner = registry.get('owner_scope')
        if (registry.get('release_mode') != 'SINGLE_OPERATOR'
                or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', registry.get('version', ''))
                or not isinstance(owner, dict) or owner.get('activation_approved') is not True
                or not isinstance(owner.get('approval_record'), str) or not owner['approval_record'].strip()
                or any(rule.get('activation') != 'ACTIVE' for rule in rules)):
            raise ValueError('inconsistent active metadata; actual approval must be verified by the operator')
    if not set(registry.get('baseline_rule_ids', [])) <= set(ids):
        raise ValueError('baseline rule missing without a disposition')
    for rule in rules:
        scope = rule.get('scope')
        if (not re.fullmatch(r'SF-RULE-[A-Z]+-\d{3}', rule['rule_id'])
                or rule.get('stage') not in stage_ids
                or not isinstance(rule.get('normative_text'), str)
                or not rule['normative_text'].strip()
                or not isinstance(scope, list) or not scope
                or not all(isinstance(item, str) and item.strip() for item in scope)
                or not rule.get('source_refs')):
            raise ValueError(f'incomplete rule: {rule.get("rule_id")}')
    if not registry.get('reference_data'):
        raise ValueError('reference data absent')
    from sfe.terminology import KEY, validate_terms
    terms = registry['reference_data'].get(KEY)
    if isinstance(terms, dict):
        validate_terms(terms)


def render(registry: dict) -> str:
    validate(registry)
    notice = ('Kandydat do wydania. Aktywacja wymaga dokładnej akceptacji i manifestu wydania.'
              if registry['activation'] == 'CANDIDATE' else
              'Aktywna wersja Standardu. Zapis zgody: ' + registry['owner_scope']['approval_record'] + '.')
    lines = [f'# SuttaFlow {registry["version"]} — proces tłumaczenia', '',
             notice, '',
             'Ten dokument powstaje z RULE_REGISTRY.json. Zmiany wprowadza się w rejestrze; '
             'nie utrzymuje się osobnych ręcznie redagowanych instrukcji.', '']
    if registry.get('workflow'):
        lines += ['## Przebieg w skrócie', '', *[
            f'{i}. {step}' for i, step in enumerate(registry['workflow'], 1)], '']
    for stage in registry['stages']:
        lines += [f'## {stage["title"]}', '', stage['instruction'], '']
        for field, label in [('responsible', 'Odpowiedzialność'), ('inputs', 'Wejście'),
                             ('outputs', 'Produkt i zakończenie'), ('stop', 'Zatrzymanie'), ('resume', 'Wznowienie')]:
            if stage.get(field):
                lines += [f'**{label}:** {stage[field]}', '']
        for rule in registry['rules']:
            if rule['stage'] == stage['id']:
                lines += [f'### {rule["rule_id"]} — {rule["title"]}', '',
                          'Zakres: ' + ', '.join(rule['scope']) + '.', '',
                          rule['normative_text'], '']
    lines += ['## Dane referencyjne dla właściwego zakresu', '']
    for title, value in registry['reference_data'].items():
        lines += [f'### {title}', '']
        if isinstance(value, str):
            lines += [value, '']
        elif title == 'Terminologia i zakresy zatwierdzeń':
            from sfe.terminology import render_terms
            lines += [render_terms(value), '']
        else:
            lines += ['```json', json.dumps(value, ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(lines)


def build(registry_path: Path, *, baseline_path: Path | None = None,
          review_path: Path | None = None) -> dict:
    raw = registry_path.read_bytes()
    registry = json.loads(raw)
    text = render(registry).encode('utf-8')
    released = {}
    protected = {}
    target = registry_path.parent / 'SUTTAFLOW_2_0.md'
    record_path = registry_path.parent / 'CONTRACT_BUILD.json'
    outputs = {target.resolve(), record_path.resolve()}
    inputs = {p.resolve() for p in (registry_path, baseline_path, review_path) if p is not None}
    incompatible_outputs = [(target.resolve(), record_path.resolve())]
    root = Path(__file__).resolve().parents[1]
    for manifest_path in (root / 'wydania').glob('*/RELEASE_MANIFEST.json'):
        manifest = json.loads(manifest_path.read_bytes())
        contract = manifest['active_contract']
        released[contract['registry']['sha256']] = contract['view']['sha256']
        view_path = root / contract['view']['path']
        inputs.add((root / contract['registry']['path']).resolve())
        incompatible_outputs.extend(((record_path.resolve(), view_path.resolve()),
                                     (target.resolve(), (view_path.parent / 'CONTRACT_BUILD.json').resolve())))
        for path in (root / contract['registry']['path'], view_path,
                     view_path.parent / 'CONTRACT_BUILD.json'):
            protected[path.resolve()] = contract['registry']['sha256']
    digest = hashlib.sha256(raw).hexdigest()
    if any(pin != digest and _same_file(path, target)
           for path in {registry_path.resolve()} | outputs for target, pin in protected.items()):
        raise ValueError('released registry and outputs are immutable; prepare a new candidate')
    control = None
    if digest in released:
        if hashlib.sha256(text).hexdigest() != released[digest]:
            raise ValueError('generated view differs from released manifest; prepare a new candidate')
        if baseline_path is not None or review_path is not None:
            raise ValueError('unchanged released registry needs no new change review')
    else:
        if baseline_path is None or review_path is None:
            raise ValueError('changed Standard requires --baseline and --review')
        baseline = baseline_path.read_bytes()
        if hashlib.sha256(baseline).hexdigest() not in released:
            raise ValueError('baseline must match a released manifest')
        from sfe.standard_change import validate_review
        review_raw = review_path.read_bytes()
        review = json.loads(review_raw)
        control = validate_review(baseline, raw, review, review_path.parent)
        inputs.update((review_path.parent / check['path']).resolve()
                      for check in review['checks'])
        control['review_sha256'] = hashlib.sha256(review_raw).hexdigest()
    if (any(_same_file(output, source) for output in outputs for source in inputs)
            or any(_same_file(left, right) for left, right in incompatible_outputs)):
        raise ValueError('build outputs must not alias each other, inputs, evidence or a different released file role')
    target.write_bytes(text)
    result = {'status': 'STRUCTURAL_BUILD_ONLY', 'version': registry['version'],
              'rules': len(registry['rules']),
              'registry_sha256': hashlib.sha256(raw).hexdigest(),
              'document_sha256': hashlib.sha256(text).hexdigest(),
              'semantic_review': 'REQUIRES_ACTUAL_REVIEW', 'activation_performed': False}
    if control is not None:
        result['change_control'] = control
    record_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('registry', type=Path)
    parser.add_argument('--baseline', type=Path)
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    try:
        result = build(args.registry, baseline_path=args.baseline, review_path=args.review)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'HOLD: {error}\n')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
