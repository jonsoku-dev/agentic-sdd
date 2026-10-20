from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from criterion_gate import decide, extract, questions, read_json

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
class AcceptanceGateRegressionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [{'id': 'c1', 'text': 'A valid acceptance condition'}]

    def test_invalid_probability_never_advances(self):
        for value in [float('nan'), float('inf'), -float('inf'), -0.1, 1.1, True, False,
                      'NaN', 'Infinity', '0.8', None, [], {}, 10**400]:
            with self.subTest(value=str(value)[:30]):
                self.assertFalse(decide(self.rows, {'c1': {'noul': value}})['advance'])

    def test_missing_answer_never_advances(self):
        self.assertFalse(decide(self.rows, {})['advance'])

    def test_unknown_answer_id_rejects_stale_coverage(self):
        self.assertFalse(decide(self.rows, {'c1': {'noul': 1}, 'c2': {'noul': 1}})['advance'])

    def test_duplicate_criteria_rejected(self):
        with self.assertRaises(ValueError):
            decide(self.rows * 2, {'c1': {'noul': 1}})

    def test_duplicate_answer_json_rejected(self):
        with self.assertRaises(ValueError):
            read_json('{"c1":{"noul":0.1},"c1":{"noul":1}}')

    def test_all_65_criteria_survive_and_last_failure_holds(self):
        spec = '\n'.join(f'{i}. **Given** item {i}, **When** run, **Then** pass.' for i in range(1, 66))
        rows = extract(spec)
        self.assertEqual(len(rows), 65)
        with self.assertRaises(ValueError):
            questions(rows)
        ids = [q['id'] for batch in (1, 2) for q in questions(rows, batch)['questions']]
        self.assertEqual(ids, [r['id'] for r in rows])
        answers = {r['id']: {'noul': 1} for r in rows}
        answers['c65']['noul'] = 0.1
        self.assertFalse(decide(rows, answers)['advance'])
        self.assertEqual(decide(rows, answers)['advisory_review'][0]['id'], 'c65')

    def test_multiline_plain_and_bold_scenarios(self):
        rows = extract('1. Given one\nWhen called\nThen done\n\n## Next\n- **Given** two, **When** run, **Then** done')
        self.assertEqual(len(rows), 2)
        self.assertNotIn('Next', rows[0]['text'])

    def test_incomplete_scenario_is_not_silently_scored(self):
        with self.assertRaises(ValueError):
            extract('1. **Given** data, **Then** done')

    def test_documented_examples_inside_code_do_not_become_acceptance(self):
        self.assertEqual(extract('```\n1. Given a, When b, Then c\n```'), [])

    def test_explicit_non_english_criteria(self):
        rows = [{'id': 'AC-저장', 'text': '저장 후 새로고침해도 값이 남는다'}]
        self.assertEqual(questions(rows)['questions'][0]['id'], 'AC-저장')
        self.assertFalse(decide(rows, {'AC-저장': {'noul': 0.9}})['advance'])

    def test_cli_exit_contract_and_file_input(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root/'spec.md').write_text('1. Given data, When saved, Then persists')
            for probability, exit_code in [(0.1, 1), (0.9, 1)]:
                (root/'answers.json').write_text(json.dumps({'answers': {'c1': {'noul': probability}}}))
                run = subprocess.run([sys.executable, str(SCRIPTS/'criterion_gate.py'), 'decide',
                    '--spec', str(root/'spec.md'), '--answers-file', str(root/'answers.json')], capture_output=True, text=True)
                self.assertEqual(run.returncode, exit_code, run.stderr)
                self.assertEqual(json.loads(run.stdout)['advance'], exit_code == 0)
            (root/'spec.md').write_text('No recognized acceptance scenarios')
            run = subprocess.run([sys.executable, str(SCRIPTS/'criterion_gate.py'), 'questions',
                                  '--spec', str(root/'spec.md')], capture_output=True, text=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, '')


if __name__ == '__main__':
    unittest.main()
