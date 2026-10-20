import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from criterion_gate import criteria_digest, decide


class AcceptanceReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'source.py').write_text('implementation')
        (self.root / 'test-result.json').write_text('{"status":"pass"}')
        self.criteria = [{'id': 'AC-1', 'text': 'Save persists after reload'}]
        def ref(name):
            return {'path': name, 'sha256': hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
        self.review = {'criteria_digest': criteria_digest(self.criteria), 'reviewer': 'primary',
                       'decisions': [{'id': 'AC-1', 'status': 'met',
                           'reason': 'The current reload test observes the same saved value.',
                           'basis': [ref('source.py')], 'evidence': [ref('test-result.json')]}]}

    def test_low_or_unavailable_score_does_not_override_reviewed_evidence(self):
        for answers in [{}, {'AC-1': {'noul': 0.2}}, {'AC-1': {'noul': 0.99}}]:
            self.assertTrue(decide(self.criteria, answers, self.review, self.root)['advance'])

    def test_concrete_failure_blocks_even_with_high_score(self):
        self.review['decisions'][0].update(status='unmet', reason='Reload loses saved value')
        self.assertFalse(decide(self.criteria, {'AC-1': {'noul': 0.99}}, self.review, self.root)['advance'])

    def test_stale_unknown_score_id_cannot_hide_behind_valid_review(self):
        result = decide(self.criteria, {'old-criterion': {'noul': 0.99}}, self.review, self.root)
        self.assertFalse(result['advance'])
        self.assertEqual(result['errors'], ['unknown answer id: old-criterion'])

    def test_stale_basis_or_missing_receipt_fails_closed(self):
        (self.root / 'source.py').write_text('changed implementation')
        with self.assertRaisesRegex(ValueError, 'stale'):
            decide(self.criteria, {}, self.review, self.root)
        (self.root / 'source.py').write_text('implementation')
        (self.root / 'test-result.json').unlink()
        with self.assertRaises(OSError):
            decide(self.criteria, {}, self.review, self.root)

    def test_missing_duplicate_unknown_or_changed_criteria_rejected(self):
        for rows in [[], self.review['decisions'] * 2, [dict(self.review['decisions'][0], id='unknown')]]:
            with self.assertRaises(ValueError):
                decide(self.criteria, {}, dict(self.review, decisions=rows), self.root)
        with self.assertRaises(ValueError):
            decide([dict(self.criteria[0], text='Different acceptance')], {}, self.review, self.root)

    def test_source_symlink_escape_rejected(self):
        with tempfile.TemporaryDirectory() as outside:
            target = Path(outside) / 'source'; target.write_text('implementation')
            (self.root / 'source.py').unlink(); (self.root / 'source.py').symlink_to(target)
            with self.assertRaisesRegex(ValueError, 'escapes'):
                decide(self.criteria, {}, self.review, self.root)

    def test_unrelated_file_change_keeps_evidence_valid(self):
        (self.root / 'notes.md').write_text('Documentation only')
        self.assertTrue(decide(self.criteria, {}, self.review, self.root)['advance'])

    def test_cli_review_without_answers_and_invalidated_receipt(self):
        (self.root / 'criteria.json').write_text(json.dumps(self.criteria))
        (self.root / 'review.json').write_text(json.dumps(self.review))
        script = Path(__file__).resolve().parents[1] / 'scripts/criterion_gate.py'
        command = [sys.executable, '-B', str(script), 'decide', '--criteria-file', str(self.root/'criteria.json'),
                   '--review-file', str(self.root/'review.json'), '--evidence-root', str(self.root)]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['completion_decided'])
        (self.root / 'test-result.json').write_text('changed')
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
