import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from sfe.parallel_text import render, read_mapping, check_pairs, compose_pali_chars


class ParallelTextTests(unittest.TestCase):
    def test_combining_mark_is_composed_without_changing_its_base(self):
        base = {'text': 'm', 'fontname': 'ABC+ChivoMono-Regular', 'x0': 10, 'x1': 16, 'top': 20, 'width': 6}
        mark = {**base, 'text': '\u0307', 'x0': 9.99, 'x1': 9.99, 'width': 0}
        self.assertEqual(compose_pali_chars([base, mark])[0]['text'], 'ṁ')
        self.assertEqual(base['text'], 'm')
        with self.assertRaisesRegex(ValueError, 'unattached'):
            compose_pali_chars([mark])
        with self.assertRaisesRegex(ValueError, 'unattached'):
            compose_pali_chars([base, {**mark, 'x0': 50}])

    def setUp(self):
        self.md = '## Przekład ##\n\nTak słyszałem.[^n]\n\nPięć pasm.\n\n[^n]: Nota.\n'
        self.mapping = {'units': []}
        for i, (pl, pali) in enumerate([('Tak słyszałem.', 'Evaṁ me sutaṁ—'),
                                         ('Pięć pasm.', 'Pañca kāmaguṇā.')], 1):
            a = self.md.index(pl)
            self.mapping['units'].append({'id': f'test:{i}', 'candidate_span': [a, a+len(pl)],
                                           'candidate_text': pl, 'source_text': pali})

    def test_render_keeps_calls_on_polish_and_escapes_source(self):
        self.mapping['units'][0]['source_text'] = 'Evaṁ <test> & sutaṁ'
        result = render(self.mapping, self.md)
        self.assertIn('Tak słyszałem.[^n]\n\n<p class="pali-source"', result)
        self.assertIn('Evaṁ &lt;test&gt; &amp; sutaṁ', result)
        self.assertTrue(result.endswith('[^n]: Nota.\n'))

    def test_unmapped_text_and_overlapping_calls_fail(self):
        for position in [0, 1]:
            mapping = copy.deepcopy(self.mapping)
            mapping['units'].pop(position)
            with self.assertRaisesRegex(ValueError, 'unmapped'):
                render(mapping, self.md)

    def test_no_footnotes_does_not_consume_method_section(self):
        md = self.md.split('\n[^n]:')[0] + '\n## Jak powstało to tłumaczenie ##\n\nMetoda.\n'
        result = render(self.mapping, md)
        self.assertEqual(result.count('class="parallel-unit"'), 2)
        self.assertTrue(result.endswith('## Jak powstało to tłumaczenie ##\n\nMetoda.\n'))

    def test_pin_anchor_and_order_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'pl.md').write_bytes(self.md.encode())
            pali = 'Evaṁ me sutaṁ—\nPañca kāmaguṇā.'
            (root/'pali.txt').write_bytes(pali.encode())
            mapping = copy.deepcopy(self.mapping)
            for key, file in [('source', 'pali.txt'), ('candidate', 'pl.md')]:
                mapping[key] = {'path': file, 'sha256': hashlib.sha256((root/file).read_bytes()).hexdigest()}
            for unit in mapping['units']:
                a = pali.index(unit['source_text'])
                unit['source_span'] = [a, a+len(unit['source_text'])]
            path = root/'map.json'
            path.write_text(json.dumps(mapping), encoding='utf-8')
            self.assertEqual(read_mapping(path, root)[2], self.md)
            mapping['units'].reverse()
            path.write_text(json.dumps(mapping), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'anchor'):
                read_mapping(path, root)
            (root/'pl.md').write_text('changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'stale'):
                read_mapping(path, root)

    def test_html_pairs_require_both_languages_and_correct_scope(self):
        html = '<body>' + ''.join(
            f'<div class="parallel-unit" data-source-id="{u["id"]}">'
            f'<p>{u["candidate_text"]}</p><p class="pali-source" lang="pi">{u["source_text"]}</p></div>'
            for u in self.mapping['units']) + '</body>'
        self.assertEqual(len(check_pairs(html, self.mapping)), 2)
        for wrong in [html.replace('Evaṁ', 'Wrong'), html.replace('test:2', 'test:1'),
                      html.replace('lang="pi"', 'lang="pl"'), html.replace('Tak słyszałem.', '')]:
            with self.subTest(wrong=wrong), self.assertRaises(ValueError):
                check_pairs(wrong, self.mapping)

    def test_source_coverage_rejects_nonwhite_gaps_and_allows_whitespace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'pl.md').write_bytes(self.md.encode())
            for before, between, after in [('Pominięte.', '\n', ''), ('', 'Luka.', ''),
                                           ('', '\n', 'Koniec.'), (' \r\n', '\t\r\n', '\n')]:
                with self.subTest(before=before, between=between, after=after):
                    mapping = copy.deepcopy(self.mapping)
                    pali = before + mapping['units'][0]['source_text'] + between + mapping['units'][1]['source_text'] + after
                    (root/'pali.txt').write_bytes(pali.encode())
                    for key, file in [('source', 'pali.txt'), ('candidate', 'pl.md')]:
                        mapping[key] = {'path': file, 'sha256': hashlib.sha256((root/file).read_bytes()).hexdigest()}
                    for unit in mapping['units']:
                        a = pali.index(unit['source_text'])
                        unit['source_span'] = [a, a+len(unit['source_text'])]
                    path = root/'map.json'
                    path.write_text(json.dumps(mapping), encoding='utf-8')
                    if any(x.strip() for x in (before, between, after)):
                        with self.assertRaisesRegex(ValueError, 'unmapped source'):
                            read_mapping(path, root)
                    else:
                        self.assertEqual(read_mapping(path, root)[1], pali)

    def test_whole_stanza_can_be_an_explicit_pair(self):
        md = '## Przekład ##\n\n<div class="gatha keep">\n\nPierwszy.  \nDrugi.\n\n</div>\n\n[^n]: Nota.\n'
        pl = md[md.index('<div'):md.index('</div>')+6]
        result = render({'units': [{'id': 'v1', 'candidate_span': [md.index(pl), md.index(pl)+len(pl)],
                                    'candidate_text': pl, 'source_text': 'Pāda1\nPāda2'}]}, md)
        self.assertIn('class="gatha keep"', result)
        self.assertIn('Pāda1\nPāda2', result)


if __name__ == '__main__':
    unittest.main()
