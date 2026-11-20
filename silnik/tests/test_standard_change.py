"""Synthetic change reviews test the gate, never attest a real semantic review."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from sfe.standard_change import prepare_review, validate_review
from sfe.standard_contract import build, render


ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / 'docs/standards/2.0.0/RULE_REGISTRY.json'


class StandardChangeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.before = {
            'schema': 'suttaflow-standard-registry-v2', 'version': '2.0.0',
            'activation': 'CANDIDATE',
            'stages': [{'id': 'start', 'title': 'Start', 'instruction': 'Read.'}],
            'rules': [
                {'rule_id': 'SF-RULE-GOV-001', 'stage': 'start', 'title': 'First',
                 'normative_text': 'Read the whole source.', 'scope': ['SUTTA'],
                 'source_refs': ['SYNTHETIC']},
                {'rule_id': 'SF-RULE-GOV-002', 'stage': 'start', 'title': 'Second',
                 'normative_text': 'Use SF-RULE-GOV-001.', 'scope': ['SUTTA'],
                 'source_refs': ['SYNTHETIC']},
            ],
            'reference_data': {'terms': 'Synthetic glossary'},
            'baseline_rule_ids': ['SF-RULE-GOV-001', 'SF-RULE-GOV-002'],
        }
        self.after = copy.deepcopy(self.before)
        self.after['version'] = '2.0.1'
        self.after['rules'][0]['normative_text'] = 'Read and record the whole source.'

    def raw(self, obj):
        return (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode()

    def review(self, before=None, after=None):
        base = self.raw(self.before if before is None else before)
        candidate = self.raw(self.after if after is None else after)
        review = prepare_review(base, candidate)
        review.update(status='REVIEWED', reviewer='SYNTHETIC reviewer',
                      reviewed_at='2026-10-21T12:00:00+02:00',
                      decision_source='SYNTHETIC test request',
                      global_analysis='SYNTHETIC: compared source, output and review duties.')
        for item in review['changes']:
            item.update(reason='SYNTHETIC clarification', impact='SYNTHETIC test only',
                        analysis='SYNTHETIC: related duties remain compatible.')
        proof = self.root / 'check.log'
        proof.write_text('SYNTHETIC check OK\n', encoding='utf-8')
        review['checks'] = [{'path': 'check.log',
                             'sha256': hashlib.sha256(proof.read_bytes()).hexdigest(),
                             'result': 'OK', 'scope': 'SYNTHETIC fixture check'}]
        return base, candidate, review

    def test_draft_lists_rule_and_non_rule_changes_and_reverse_reference(self):
        draft = prepare_review(self.raw(self.before), self.raw(self.after))
        self.assertEqual(draft['status'], 'DRAFT')
        self.assertEqual([x['target'] for x in draft['changes']],
                         ['rule:SF-RULE-GOV-001', 'section:version'])
        self.assertEqual(draft['changes'][0]['related_rule_ids'], ['SF-RULE-GOV-002'])
        self.assertEqual(draft['reviewer'], '')

    def test_complete_review_records_scope_without_claiming_authentication(self):
        base, candidate, review = self.review()
        result = validate_review(base, candidate, review, self.root)
        self.assertEqual(result['status'], 'CONSISTENCY_REVIEW_RECORDED')
        self.assertEqual(result['reviewed_targets'], 2)
        self.assertIs(result['semantic_truth_verified'], False)

    def test_incomplete_draft_or_identity_cannot_unlock_change(self):
        for field, value in [('status', 'DRAFT'), ('reviewer', ''),
                             ('reviewed_at', '2026-10-21'), ('decision_source', ''),
                             ('global_analysis', '')]:
            with self.subTest(field=field):
                base, candidate, review = self.review()
                review[field] = value
                with self.assertRaises(ValueError):
                    validate_review(base, candidate, review, self.root)

    def test_review_for_previous_bytes_is_rejected(self):
        base, candidate, review = self.review()
        for old, new in [(base, base + b' '), (candidate, candidate + b' ')]:
            with self.subTest(changed='base' if old is base else 'candidate'):
                with self.assertRaises(ValueError):
                    validate_review(new if old is base else base,
                                    new if old is candidate else candidate, review, self.root)

    def test_each_rule_and_reference_data_change_requires_exact_coverage(self):
        self.after['reference_data']['terms'] = 'Changed glossary'
        base, candidate, review = self.review()
        for mutation in ('missing', 'extra', 'duplicate'):
            with self.subTest(mutation=mutation):
                broken = copy.deepcopy(review)
                if mutation == 'missing':
                    broken['changes'].pop()
                elif mutation == 'extra':
                    broken['changes'].append({**broken['changes'][0], 'target': 'section:absent'})
                else:
                    broken['changes'].append(copy.deepcopy(broken['changes'][0]))
                with self.assertRaises(ValueError):
                    validate_review(base, candidate, broken, self.root)

    def test_workflow_stage_and_rule_order_changes_are_included(self):
        self.after['workflow'] = ['SYNTHETIC new workflow']
        self.after['stages'][0]['instruction'] = 'SYNTHETIC changed instruction'
        self.after['rules'].reverse()
        draft = prepare_review(self.raw(self.before), self.raw(self.after))
        self.assertEqual({x['target'] for x in draft['changes']},
                         {'rule:SF-RULE-GOV-001', 'section:version', 'section:workflow',
                          'section:stages', 'section:rules_order'})

    def test_missing_related_rule_or_unknown_rule_is_rejected(self):
        for ids in ([], ['SF-RULE-GOV-999']):
            base, candidate, review = self.review()
            review['changes'][0]['related_rule_ids'] = ids
            with self.assertRaises(ValueError):
                validate_review(base, candidate, review, self.root)

    def test_unknown_rule_reference_and_open_conflict_are_rejected(self):
        base, candidate, review = self.review()
        review['unresolved_conflicts'] = ['SYNTHETIC conflict still open']
        with self.assertRaises(ValueError):
            validate_review(base, candidate, review, self.root)
        for unknown in ('SF-RULE-GOV-999', 'SF-RULE-GOV-0010'):
            self.after['rules'][0]['normative_text'] = 'Use ' + unknown + '.'
            base, candidate, review = self.review()
            with self.assertRaises(ValueError):
                validate_review(base, candidate, review, self.root)

    def test_resolved_conflict_needs_description_resolution_and_known_rules(self):
        base, candidate, review = self.review()
        review['resolved_conflicts'] = [{'rule_ids': ['SF-RULE-GOV-001', 'SF-RULE-GOV-002'],
                                         'description': 'SYNTHETIC ambiguity',
                                         'resolution': 'SYNTHETIC scope clarified'}]
        validate_review(base, candidate, review, self.root)
        review['resolved_conflicts'][0]['resolution'] = ''
        with self.assertRaises(ValueError):
            validate_review(base, candidate, review, self.root)

    def test_missing_stale_or_outside_check_artifact_is_rejected(self):
        for mutation in ('missing', 'stale', 'outside', 'empty_checks'):
            with self.subTest(mutation=mutation):
                base, candidate, review = self.review()
                if mutation == 'missing':
                    review['checks'][0]['path'] = 'absent.log'
                elif mutation == 'stale':
                    (self.root / 'check.log').write_text('Changed result', encoding='utf-8')
                elif mutation == 'outside':
                    review['checks'][0]['path'] = '../outside.log'
                else:
                    review['checks'] = []
                with self.assertRaises((ValueError, OSError)):
                    validate_review(base, candidate, review, self.root)

    def test_changed_registry_without_review_writes_nothing(self):
        path = self.root / 'RULE_REGISTRY.json'
        path.write_bytes(self.raw(self.after))
        output = self.root / 'SUTTAFLOW_2_0.md'
        output.write_text('Preserve existing view', encoding='utf-8')
        with self.assertRaises(ValueError):
            build(path)
        self.assertEqual(output.read_text('utf-8'), 'Preserve existing view')
        self.assertFalse((self.root / 'CONTRACT_BUILD.json').exists())

    def test_renderer_change_cannot_rewrite_released_view(self):
        path = self.root / 'RULE_REGISTRY.json'; path.write_bytes(RELEASE.read_bytes())
        output = self.root / 'SUTTAFLOW_2_0.md'
        output.write_bytes(b'Preserve previous output')
        # Simulate a changed pure renderer; exercise the real pre-write hash guard.
        with patch('sfe.standard_contract.render', return_value='Changed renderer output'):
            with self.assertRaises(ValueError):
                build(path)
        self.assertEqual(output.read_bytes(), b'Preserve previous output')

    def released_candidate(self):
        before = json.loads(RELEASE.read_bytes())
        after = copy.deepcopy(before)
        after.update(version='2.0.1', activation='CANDIDATE')
        after['owner_scope']['activation_approved'] = False
        after['owner_scope'].pop('approval_record')
        for rule in after['rules']:
            rule['activation'] = 'CANDIDATE'
        _, candidate, review = self.review(before, after)
        review['baseline_sha256'] = hashlib.sha256(RELEASE.read_bytes()).hexdigest()
        return candidate, review

    def test_alternate_registry_cannot_overwrite_released_outputs(self):
        candidate, review = self.released_candidate()
        manifest_path = self.root / 'wydania/2.0.0/RELEASE_MANIFEST.json'
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_bytes((ROOT / 'wydania/2.0.0/RELEASE_MANIFEST.json').read_bytes())
        directory = self.root / 'docs/standards/2.0.0'
        directory.mkdir(parents=True)
        baseline = directory / 'RULE_REGISTRY.json'
        baseline.write_bytes(RELEASE.read_bytes())
        path = directory / 'ALTERNATE.json'; path.write_bytes(candidate)
        proof = self.root / 'REVIEW.json'; proof.write_bytes(self.raw(review))
        outputs = [directory / 'SUTTAFLOW_2_0.md', directory / 'CONTRACT_BUILD.json']
        for output in outputs:
            output.write_bytes(b'Preserve released output')
        with patch('sfe.standard_contract.__file__', str(self.root / 'sfe/standard_contract.py')):
            with self.assertRaises(ValueError):
                build(path, baseline_path=baseline, review_path=proof)
        for output in outputs:
            self.assertEqual(output.read_bytes(), b'Preserve released output')

    def test_build_outputs_cannot_replace_inputs_or_review_checks(self):
        for filename in ('SUTTAFLOW_2_0.md', 'CONTRACT_BUILD.json'):
            for role in ('candidate', 'baseline', 'review', 'check'):
                with self.subTest(filename=filename, role=role):
                    candidate, review = self.released_candidate()
                    path = self.root / 'RULE_REGISTRY.json'; path.write_bytes(candidate)
                    baseline = self.root / 'BASE.json'; baseline.write_bytes(RELEASE.read_bytes())
                    output = self.root / filename
                    output.write_bytes(b'Preserve collision input')
                    proof = self.root / 'REVIEW.json'
                    if role == 'candidate':
                        output.write_bytes(candidate); path = output
                    elif role == 'baseline':
                        output.write_bytes(RELEASE.read_bytes()); baseline = output
                    elif role == 'review':
                        proof = output
                    else:
                        review['checks'][0].update(path=filename,
                            sha256=hashlib.sha256(output.read_bytes()).hexdigest())
                    proof.write_bytes(self.raw(review))
                    saved = output.read_bytes()
                    with self.assertRaises(ValueError):
                        build(path, baseline_path=baseline, review_path=proof)
                    self.assertEqual(output.read_bytes(), saved)

    def test_hardlink_output_cannot_rewrite_a_released_file(self):
        base, candidate, review = self.review()
        repo = self.root / 'synthetic-repo'
        released = repo / 'docs/standards/2.0.0'
        released.mkdir(parents=True)
        baseline = released / 'RULE_REGISTRY.json'; baseline.write_bytes(base)
        view = released / 'SUTTAFLOW_2_0.md'; view.write_bytes(render(json.loads(base)).encode())
        saved = view.read_bytes()
        manifest = repo / 'wydania/2.0.0/RELEASE_MANIFEST.json'
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes(self.raw({'active_contract': {
            'registry': {'path': str(baseline.relative_to(repo)), 'sha256': hashlib.sha256(base).hexdigest()},
            'view': {'path': str(view.relative_to(repo)), 'sha256': hashlib.sha256(saved).hexdigest()}}}))
        path = repo / 'candidate/RULE_REGISTRY.json'; path.parent.mkdir(); path.write_bytes(candidate)
        os.link(view, path.parent / 'SUTTAFLOW_2_0.md')
        proof = self.root / 'REVIEW.json'; proof.write_bytes(self.raw(review))
        with patch('sfe.standard_contract.__file__', str(repo / 'sfe/standard_contract.py')):
            with self.assertRaises(ValueError): build(path, baseline_path=baseline, review_path=proof)
        self.assertEqual(view.read_bytes(), saved)

    def test_unchanged_release_cannot_overwrite_another_protected_file_role(self):
        raw = RELEASE.read_bytes()
        directory = self.root / 'docs/standards/2.0.0'
        directory.mkdir(parents=True)
        protected = [directory / name for name in
                     ('RULE_REGISTRY.json', 'SUTTAFLOW_2_0.md', 'CONTRACT_BUILD.json')]
        contents = [raw, render(json.loads(raw)).encode(), b'Preserve build record']
        for path, content in zip(protected, contents):
            path.write_bytes(content)
        manifest = self.root / 'wydania/2.0.0/RELEASE_MANIFEST.json'
        manifest.parent.mkdir(parents=True)
        manifest.write_bytes((ROOT / 'wydania/2.0.0/RELEASE_MANIFEST.json').read_bytes())
        for index, source in enumerate(protected):
            for output_name in ('SUTTAFLOW_2_0.md', 'CONTRACT_BUILD.json'):
                if source.name == output_name:
                    continue
                with self.subTest(source=source.name, output=output_name):
                    restore = self.root / f'restore-{index}-{output_name}'
                    restore.mkdir()
                    registry = restore / 'RULE_REGISTRY.json'; registry.write_bytes(raw)
                    os.link(source, restore / output_name)
                    with patch('sfe.standard_contract.__file__', str(self.root / 'sfe/standard_contract.py')):
                        with self.assertRaises(ValueError): build(registry)
                    self.assertEqual(source.read_bytes(), contents[index])

    def test_reviewed_candidate_builds_from_released_base_and_stale_review_stops_rebuild(self):
        before = json.loads(RELEASE.read_bytes())
        after = copy.deepcopy(before)
        after.update(version='2.0.1', activation='CANDIDATE')
        after['owner_scope']['activation_approved'] = False
        after['owner_scope'].pop('approval_record')
        for rule in after['rules']:
            rule['activation'] = 'CANDIDATE'
        after['rules'][0]['normative_text'] += ' SYNTHETIC test only.'
        _, candidate, review = self.review(before, after)
        # Use the literal released bytes, not a reserialized approximation of the base.
        review['baseline_sha256'] = hashlib.sha256(RELEASE.read_bytes()).hexdigest()
        path = self.root / 'RULE_REGISTRY.json'; path.write_bytes(candidate)
        proof = self.root / 'REVIEW.json'; proof.write_bytes(self.raw(review))
        result = build(path, baseline_path=RELEASE, review_path=proof)
        self.assertEqual(result['change_control']['status'], 'CONSISTENCY_REVIEW_RECORDED')
        self.assertIn('SuttaFlow 2.0.1', (self.root / 'SUTTAFLOW_2_0.md').read_text('utf-8'))
        saved = (self.root / 'SUTTAFLOW_2_0.md').read_bytes()
        path.write_bytes(candidate + b' ')
        with self.assertRaises(ValueError):
            build(path, baseline_path=RELEASE, review_path=proof)
        self.assertEqual((self.root / 'SUTTAFLOW_2_0.md').read_bytes(), saved)

    def test_self_baseline_and_edit_of_released_version_are_rejected(self):
        before = json.loads(RELEASE.read_bytes()); after = copy.deepcopy(before)
        after['rules'][0]['normative_text'] += ' SYNTHETIC change.'
        _, candidate, review = self.review(before, after)
        review['baseline_sha256'] = hashlib.sha256(RELEASE.read_bytes()).hexdigest()
        path = self.root / 'RULE_REGISTRY.json'; path.write_bytes(candidate)
        proof = self.root / 'REVIEW.json'; proof.write_bytes(self.raw(review))
        for baseline in (RELEASE, path):
            with self.subTest(baseline=str(baseline)):
                with self.assertRaises(ValueError):
                    build(path, baseline_path=baseline, review_path=proof)

    def test_cli_draft_is_not_a_review_and_existing_draft_is_not_overwritten(self):
        candidate = self.root / 'RULE_REGISTRY.json'
        candidate.write_bytes(self.raw(self.after))
        before = self.root / 'BEFORE.json'; before.write_bytes(self.raw(self.before))
        draft = self.root / 'REVIEW.json'
        command = [sys.executable, '-m', 'sfe.standard_change', str(before), str(candidate),
                   '--output', str(draft)]
        first = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        saved = draft.read_bytes()
        self.assertEqual(json.loads(saved)['status'], 'DRAFT')
        second = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertEqual(draft.read_bytes(), saved)
        denied = subprocess.run([sys.executable, '-m', 'sfe.standard_contract', str(candidate)],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(denied.returncode, 1)
        self.assertIn('HOLD:', denied.stderr)
        self.assertFalse((self.root / 'SUTTAFLOW_2_0.md').exists())


if __name__ == '__main__':
    unittest.main()
