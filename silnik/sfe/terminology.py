"""Scoped terminology signals and recorded dispositions, never a semantic verdict."""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import unicodedata


KEY = 'Terminologia i zakresy zatwierdzeń'
STATUSES = {'ZATWIERDZONE', 'ZATWIERDZONE POŚREDNIO',
            'ZASTOSOWANE, ZATWIERDZONE POŚREDNIO', 'ZASTOSOWANE, NIEPOTWIERDZONE',
            'PROPOZYCJA', 'WYCOFANE'}
WORK_KINDS = {'NEW_TRANSLATION', 'REVISION', 'HISTORICAL'}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def _pattern(value: str) -> re.Pattern:
    try:
        pattern = re.compile(unicodedata.normalize('NFC', value), re.IGNORECASE)
    except (re.error, TypeError) as error:
        raise ValueError('invalid terminology pattern') from error
    _require(pattern.search('') is None, 'terminology pattern matches empty text')
    return pattern


def _overlap(left: dict, right: dict) -> bool:
    return all(not left[k] or not right[k] or bool(set(left[k]) & set(right[k]))
               for k in ('subjects', 'artifacts', 'work_kinds'))


def _scopes(entry: dict) -> list:
    value = entry.get('applies_to')
    return value if isinstance(value, list) else [value]


def validate_terms(data: dict) -> None:
    _require(isinstance(data, dict) and data.get('schema') == 'suttaflow-terminology-register-v1',
             'unknown terminology registry schema')
    entries = data.get('entries')
    _require(isinstance(entries, list) and bool(entries), 'terminology entries required')
    ids: set[str] = set()
    for e in entries:
        _require(isinstance(e, dict), 'term entry must be an object')
        for key in ('entry_id', 'pali', 'polish', 'sense_id', 'scope', 'meaning',
                    'exceptions', 'source_pattern', 'preferred_pattern'):
            _require(isinstance(e.get(key), str) and bool(e[key].strip()), 'missing term field: ' + key)
        _require(e['entry_id'] not in ids, 'duplicate term ID')
        ids.add(e['entry_id'])
        _require(e.get('status_raw') in STATUSES, 'unknown raw term status')
        _require(e.get('language') in ('PALI', 'EN_HH'), 'unknown term language')
        scopes = _scopes(e)
        _require(bool(scopes), 'at least one explicit machine scope required')
        for scope in scopes:
            _require(isinstance(scope, dict) and set(scope) == {'subjects', 'artifacts', 'work_kinds'},
                     'explicit machine scope required')
            for key, values in scope.items():
                _require(isinstance(values, list) and all(isinstance(v, str) and v.strip() for v in values)
                         and len(set(values)) == len(values), 'invalid scope: ' + key)
            _require(bool(scope['work_kinds']) and set(scope['work_kinds']) <= WORK_KINDS,
                     'explicit work kinds required')
            if 'POŚREDNIO' in e['status_raw']:
                _require(bool(scope['artifacts']), 'indirect approval requires exact artifacts')
        _require(isinstance(e.get('source_refs'), list) and bool(e['source_refs'])
                 and all(isinstance(v, str) and v.strip() for v in e['source_refs']), 'term provenance required')
        history = e.get('history')
        _require(isinstance(history, list) and bool(history) and all(
            isinstance(h, dict) and h.get('source') and isinstance(h.get('record'), dict) for h in history),
            'term history required')
        _require(history[-1]['record'] == {k: v for k, v in e.items() if k != 'history'},
                 'current term differs from last history record')
        _pattern(e['source_pattern'])
        _pattern(e['preferred_pattern'])
    binding = [e for e in entries if e['status_raw'] == 'ZATWIERDZONE' or 'POŚREDNIO' in e['status_raw']]
    for i, left in enumerate(binding):
        for right in binding[i + 1:]:
            if (left['language'], unicodedata.normalize('NFC', left['pali']).casefold(), left['sense_id']) == (
                    right['language'], unicodedata.normalize('NFC', right['pali']).casefold(), right['sense_id']):
                _require(not any(_overlap(l, r) for l in _scopes(left) for r in _scopes(right)),
                         'overlapping binding terms for the same sense')


def validate_transition(before: dict, after: dict) -> None:
    validate_terms(before)
    validate_terms(after)
    for key, value in before.get('legacy_history', {}).items():
        _require(after.get('legacy_history', {}).get(key) == value, 'raw legacy history removed or rewritten')
    imports = before.get('import_sources', [])
    _require(after.get('import_sources', [])[:len(imports)] == imports, 'import provenance removed or rewritten')
    current = {e['entry_id']: e for e in after['entries']}
    for entry in before['entries']:
        _require(entry['entry_id'] in current, 'term removed; retain a withdrawn record instead')
        history = current[entry['entry_id']]['history']
        _require(history[:len(entry['history'])] == entry['history'], 'term history removed or rewritten')


def render_terms(data: dict) -> str:
    validate_terms(data)
    lines = ['Widok generowany z rejestru Standardu. Status i zakres ograniczają każde użycie.', '',
             '| ID / hasło | Polski odpowiednik | Status | Zakres |', '| --- | --- | --- | --- |']
    def cell(s: str) -> str:
        return s.replace('|', '\\|').replace('\n', ' ')
    for e in data['entries']:
        lines.append('| ' + ' | '.join(cell(v) for v in (
            e['entry_id'] + ' · ' + e['pali'], e['polish'], e['status_raw'], e['scope'])) + ' |')
    for e in data['entries']:
        lines += ['', '#### ' + e['entry_id'], '', '**Znaczenie/kontekst:** ' + e['meaning'], '',
                  '**Wyjątki:** ' + e['exceptions'], '', '**Podstawa:** ' + '; '.join(e['source_refs']), '',
                  '**Historia (zachowane brzmienia, nie nowe zgody):**', '']
        for event in e['history']:
            r = event['record']
            lines += ['- ' + str(event.get('date') or 'Data nieodtworzona') + ': '
                      + r.get('polish', '') + '; ' + r.get('status_raw', '') + '; '
                      + r.get('scope', '') + '. Źródło: ' + event['source']]
    lines += ['', 'Pełne surowe rekordy historyczne i źródła importu: legacy_history w tym samym rejestrze.',
              'Wzorce są ograniczonym detektorem. Brak sygnału nie dowodzi zgodności znaczeniowej.', '']
    return '\n'.join(lines)


def _read_pin(pin: dict, root: Path) -> str:
    _require(isinstance(pin, dict) and isinstance(pin.get('path'), str) and bool(pin['path']), 'file pin required')
    raw = (root / pin['path']).read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == pin.get('sha256'), 'stale terminology file pin: ' + pin['path'])
    return raw.decode('utf-8')


def _span(unit: dict, key: str, text: str) -> str:
    span = unit.get(key)
    _require(isinstance(span, list) and len(span) == 2 and all(type(v) is int for v in span)
             and 0 <= span[0] < span[1] <= len(text), 'invalid or empty unit span: ' + key)
    actual = text[span[0]:span[1]]
    _require(unit.get(key.replace('_span', '_text')) == actual,
             'unit anchor differs from exact decoded bytes: ' + key)
    return actual


def check(data: dict, task: dict, root: Path, *, resolutions: dict | None = None,
          registry_sha256: str | None = None) -> dict:
    validate_terms(data)
    _require(isinstance(task, dict) and task.get('schema') == 'suttaflow-terminology-task-v1', 'unknown task schema')
    _require(task.get('work_kind') in WORK_KINDS and task.get('language') in ('PALI', 'EN_HH'), 'invalid task context')
    _require(all(isinstance(task.get(k), str) and task[k].strip() for k in ('subject_id', 'artifact_id')),
             'subject and exact artifact required')
    source, polish = (_read_pin(task[k], root) for k in ('source', 'candidate'))
    units = task.get('units')
    _require(isinstance(units, list) and bool(units), 'declare actual units; empty scan is not a check')
    registry_pin = registry_sha256 or _digest(data)
    scan_pin = _digest({'registry_sha256': registry_pin, 'task': task})
    findings = []
    ids: set[str] = set()
    for unit in units:
        _require(isinstance(unit, dict) and all(isinstance(unit.get(k), str) and unit[k].strip()
                 for k in ('id', 'locator', 'section')), 'incomplete terminology unit')
        _require(unit['id'] not in ids, 'duplicate terminology unit')
        ids.add(unit['id'])
        src = unicodedata.normalize('NFC', _span(unit, 'source_span', source))
        pl = unicodedata.normalize('NFC', _span(unit, 'candidate_span', polish))
        for e in data['entries']:
            if e['language'] != task['language']:
                continue
            applies = any((not scope['subjects'] or task['subject_id'] in scope['subjects']) and (
                not scope['artifacts'] or task['artifact_id'] in scope['artifacts']) and task['work_kind'] in scope['work_kinds']
                for scope in _scopes(e))
            binding = applies and (e['status_raw'] == 'ZATWIERDZONE' or 'POŚREDNIO' in e['status_raw'])
            for match in _pattern(e['source_pattern']).finditer(src):
                _require(match.end() > match.start(), 'zero-width term occurrence')
                findings.append({'finding_id': 'TERM-' + _digest([scan_pin, unit['id'], e['entry_id'], match.span()])[:24],
                                 'entry_id': e['entry_id'], 'unit_id': unit['id'], 'locator': unit['locator'],
                                 'section': unit['section'], 'source_span': unit['source_span'],
                                 'candidate_span': unit['candidate_span'], 'match_nfc_span': list(match.span()),
                                 'source_form': match.group(), 'source_excerpt': src, 'polish_excerpt': pl,
                                 'status_raw': e['status_raw'], 'scope': e['scope'],
                                 'authority': 'BINDING_IN_SCOPE' if binding else 'REFERENCE_ONLY',
                                 'in_scope': applies,
                                 'signal': 'PREFERRED_FORM_PRESENT' if _pattern(e['preferred_pattern']).search(pl)
                                 else 'PREFERRED_FORM_NOT_FOUND', 'resolution': None})
    stale = False
    if resolutions is not None:
        _require(isinstance(resolutions, dict), 'resolutions must be an object')
        stale = resolutions.get('scan_sha256') != scan_pin
        if not stale:
            pending = {f['finding_id']: f for f in findings if f['authority'] == 'BINDING_IN_SCOPE'}
            items = resolutions.get('items')
            _require(isinstance(items, list), 'resolution items required')
            seen: set[str] = set()
            for item in items:
                _require(isinstance(item, dict) and item.get('finding_id') in pending
                         and item['finding_id'] not in seen, 'unknown, informational or duplicate disposition')
                _require(item.get('decision') in ('CONFORMS', 'JUSTIFIED_EXCEPTION', 'NOT_APPLICABLE'), 'unknown disposition')
                _require(all(isinstance(item.get(k), str) and item[k].strip()
                             for k in ('reason', 'evidence', 'performer', 'recorded_at')), 'actual disposition evidence required')
                _require(datetime.fromisoformat(item['recorded_at']).utcoffset() is not None, 'disposition date requires timezone')
                seen.add(item['finding_id'])
                pending[item['finding_id']]['resolution'] = item
    open_count = sum(f['authority'] == 'BINDING_IN_SCOPE' and f['resolution'] is None for f in findings)
    status = ('STALE_TERMINOLOGY_RESOLUTIONS' if stale else 'REQUIRES_TERMINOLOGY_REVIEW' if open_count
              else 'TECHNICAL_TERMINOLOGY_RECORDED' if any(f['resolution'] for f in findings)
              else 'REFERENCE_SIGNALS_ONLY' if findings else 'NO_MATCHES_NOT_SEMANTIC_CLEARANCE')
    return {'schema': 'suttaflow-terminology-check-v1', 'status': status, 'scan_sha256': scan_pin,
            'registry_sha256': registry_pin, 'subject_id': task['subject_id'], 'artifact_id': task['artifact_id'],
            'source': task['source'], 'candidate': task['candidate'], 'units_checked': len(units),
            'scope': 'declared spans only; no claim of whole-file semantic coverage',
            'open_findings': open_count, 'findings': findings, 'semantic_correctness_verified': False,
            'approval_authenticity_verified': False, 'publication_approved': False,
            'limits': 'bounded source forms; context, morphology, exceptions and unmatched forms require actual review'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('list', 'check'))
    parser.add_argument('registry', type=Path)
    parser.add_argument('--task', type=Path)
    parser.add_argument('--resolutions', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    try:
        raw = args.registry.read_bytes()
        registry = json.loads(raw)
        from sfe.standard_contract import validate
        validate(registry)
        data = registry['reference_data'][KEY]
        protected = [args.registry]
        exit_code = 0
        if args.command == 'list':
            text = (f'# Rejestr terminologii — SuttaFlow {registry["version"]}\n\n'
                    f'Stan Standardu: {registry["activation"]}. Widok, nie osobne źródło reguł.\n\n'
                    + render_terms(data))
        else:
            _require(args.task is not None, '--task required')
            protected.append(args.task)
            task = json.loads(args.task.read_bytes())
            protected.extend(args.task.parent / task[k]['path'] for k in ('source', 'candidate'))
            resolutions = None
            if args.resolutions:
                protected.append(args.resolutions)
                resolutions = json.loads(args.resolutions.read_bytes())
            result = check(data, task, args.task.parent, resolutions=resolutions,
                           registry_sha256=hashlib.sha256(raw).hexdigest())
            result['standard_version'] = registry['version']
            result['standard_activation'] = registry['activation']
            result['task_sha256'] = hashlib.sha256(args.task.read_bytes()).hexdigest()
            text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
            exit_code = 2 if result['open_findings'] or result['status'] == 'STALE_TERMINOLOGY_RESOLUTIONS' else 0
        _require(args.output.resolve() not in {p.resolve() for p in protected}, 'output collides with an input')
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(text)
    except (ValueError, OSError, KeyError, TypeError, AttributeError) as error:
        parser.exit(1, f'HOLD: {error}\n')
    parser.exit(exit_code)


if __name__ == '__main__':
    main()
