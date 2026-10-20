import copy
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verification_evidence import compute_basis
from verification_guard import assess
from verification_run import run_check, StateConflict


class VerificationRunTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.app = self.root/'app.py'
        self.app.write_text('def total():\n    return 3\n')
        self.oracle = self.root/'check.py'
        self.oracle.write_text('''import json
from pathlib import Path
from app import total
counter = Path('executions.txt')
with counter.open('a') as stream: stream.write('run\\n')
actual = total()
print(json.dumps({'observation': {'expected': 2, 'actual': actual}}))
raise SystemExit(0 if actual == 2 else 1)
''')
        self.check = {'id': 'total', 'criteria': ['AC-total'], 'required': True,
                      'rerun_policy': 'on_change', 'command': [sys.executable, '-B', 'check.py'],
                      'basis_sources': {'implementation': ['app.py'], 'inputs': [], 'oracle': ['check.py']},
                      'observation_json_key': 'observation'}
        self.state = {'goal_id': 'correct-total', 'proposed_check': 'total',
                      'checks': [self.check], 'history': []}
        self.path = self.root/'progress.json'
        self.save()

    def save(self):
        self.path.write_text(json.dumps(self.state))

    def read(self):
        return json.loads(self.path.read_text())

    def run_one(self, **kwargs):
        return run_check(self.path, self.root, execute=True, **kwargs)

    def test_real_failure_recovery_repair_pass_and_no_duplicate_execution(self):
        for _ in range(3):
            result, code = self.run_one()
            self.assertEqual(code, 1)
            self.assertEqual(result['outcome'], 'fail')
        result, code = self.run_one()
        self.assertEqual(code, 3)
        self.assertFalse(result['executed'])
        self.assertEqual(result['guard']['decision'], 'recover')
        self.assertEqual((self.root/'executions.txt').read_text().count('run'), 3)
        self.app.write_text('def total():\n    return 2\n')
        result, code = self.run_one()
        self.assertEqual(code, 0)
        self.assertTrue(result['state_committed'])
        self.assertEqual(result['guard']['required_gaps'], [])
        self.assertEqual(result['guard']['decision'], 'reuse_pass')
        final, code = self.run_one()
        self.assertEqual(code, 0)
        self.assertFalse(final['executed'])
        self.assertEqual(len(self.read()['history']), 4)
        self.assertEqual((self.root/'executions.txt').read_text().count('run'), 4)

    def test_cli_entrypoint_plans_executes_and_reuses(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/verification_run.py'
        command = [sys.executable, str(script), '--state', str(self.path), '--root', str(self.root)]
        plan = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(plan.returncode, 0, plan.stderr)
        self.assertFalse(json.loads(plan.stdout)['executed'])
        failed = subprocess.run([*command, '--execute'], capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1, failed.stderr)
        self.assertEqual(json.loads(failed.stdout)['outcome'], 'fail')
        self.app.write_text('def total():\n    return 2\n')
        passed = subprocess.run([*command, '--execute'], capture_output=True, text=True)
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertTrue(json.loads(passed.stdout)['accepted_check'])
        reused = subprocess.run([*command, '--execute'], capture_output=True, text=True)
        self.assertEqual(reused.returncode, 0, reused.stderr)
        self.assertFalse(json.loads(reused.stdout)['executed'])
        self.assertEqual((self.root/'executions.txt').read_text().count('run'), 2)

    def test_plan_does_not_execute_or_mutate_state(self):
        before = self.path.read_bytes()
        result, code = run_check(self.path, self.root)
        self.assertEqual(code, 0)
        self.assertFalse(result['executed'])
        self.assertEqual(before, self.path.read_bytes())
        self.assertFalse((self.root/'executions.txt').exists())

    def test_missing_or_tampered_log_invalidates_real_pass(self):
        self.app.write_text('def total():\n    return 2\n')
        result, _ = self.run_one()
        receipt = json.loads((self.root/result['receipt']).read_text())
        log = self.root/receipt['stdout_ref']
        log.write_text('forged output')
        current = assess(self.read(), evidence_root=self.root)
        self.assertEqual(current['decision'], 'run_check')
        self.assertEqual(current['required_gaps'], ['total'])
        log.unlink()
        self.assertEqual(assess(self.read(), evidence_root=self.root)['required_gaps'], ['total'])

    def test_real_source_change_is_detected_without_state_edit(self):
        self.app.write_text('def total():\n    return 2\n')
        self.run_one()
        self.app.write_text('def total():\n    return 99\n')
        current = assess(self.read(), evidence_root=self.root)
        self.assertEqual(current['decision'], 'run_check')
        self.assertEqual(current['required_gaps'], ['total'])

    def test_process_exit_zero_during_source_change_is_not_success(self):
        self.oracle.write_text("from pathlib import Path\nPath('app.py').write_text('def total(): return 2')\n")
        result, code = self.run_one()
        self.assertEqual(code, 1)
        self.assertEqual(result['outcome'], 'error')
        receipt = json.loads((self.root/result['receipt']).read_text())
        self.assertTrue(receipt['source_changed'])
        self.assertEqual(receipt['exit_code'], 0)
        self.assertEqual(result['guard']['required_gaps'], ['total'])

    def test_bad_structured_observation_is_not_success(self):
        self.oracle.write_text("print('not json')\n")
        result, code = self.run_one()
        self.assertEqual(code, 1)
        self.assertEqual(result['outcome'], 'error')

    def test_timeout_is_recorded_and_cannot_pass(self):
        self.oracle.write_text('import time\ntime.sleep(10)\n')
        result, code = self.run_one(timeout=0.15)
        self.assertEqual(code, 1)
        receipt = json.loads((self.root/result['receipt']).read_text())
        self.assertTrue(receipt['timed_out'])
        self.assertEqual(result['outcome'], 'error')

    def test_output_limit_stops_process_and_cannot_pass(self):
        self.oracle.write_text("import os\nos.write(1, b'x'*1000000)\n")
        result, code = self.run_one(output_limit=128)
        self.assertEqual(code, 1)
        receipt = json.loads((self.root/result['receipt']).read_text())
        self.assertTrue(receipt['output_limited'])
        self.assertLessEqual((self.root/receipt['stdout_ref']).stat().st_size, 128)

    def test_concurrent_state_change_preserves_external_work_and_no_commit(self):
        self.oracle.write_text("from pathlib import Path\nPath('progress.json').write_text('external change')\n")
        result, code = self.run_one()
        self.assertEqual(code, 4)
        self.assertFalse(result['state_committed'])
        self.assertEqual(self.path.read_text(), 'external change')
        self.assertIn('orphan_receipt', result)

    def test_existing_lock_prevents_execution(self):
        self.path.with_name(self.path.name+'.verification.lock').write_text('other writer')
        with self.assertRaises(StateConflict): self.run_one()
        self.assertFalse((self.root/'executions.txt').exists())

    def test_deleted_declared_proof_artifact_invalidates_pass(self):
        self.app.write_text('def total():\n    return 2\n')
        self.oracle.write_text(self.oracle.read_text().replace("actual = total()", "Path('proof.txt').write_text('observed total')\nactual = total()"))
        self.check['artifacts'] = ['proof.txt']; self.save()
        result, code = self.run_one()
        self.assertEqual(code, 0)
        (self.root/'proof.txt').unlink()
        self.assertEqual(assess(self.read(), evidence_root=self.root)['required_gaps'], ['total'])

    def test_overwritten_output_cannot_erase_prior_failure_conflict(self):
        self.check['artifacts'] = ['proof.txt']
        self.oracle.write_text("""import json
from pathlib import Path
marker=Path('flaky-count')
count=int(marker.read_text())+1 if marker.exists() else 1
marker.write_text(str(count))
Path('proof.txt').write_text('observed-'+str(count))
print(json.dumps({'observation': {'accepted': count > 1}}))
raise SystemExit(0 if count > 1 else 1)
""")
        self.save()
        first, code = self.run_one(); self.assertEqual(code, 1)
        second, code = self.run_one(); self.assertEqual(code, 3)
        self.assertFalse(second['accepted_check'])
        report = second['guard']
        self.assertEqual(report['decision'], 'recover')
        self.assertEqual(report['required_gaps'], ['total'])
        first_receipt = json.loads((self.root/first['receipt']).read_text())
        snapshot = self.root/first_receipt['artifacts'][0]['snapshot_ref']
        self.assertEqual(snapshot.read_text(), 'observed-1')

    def test_missing_declared_proof_output_cannot_pass(self):
        self.app.write_text('def total():\n    return 2\n')
        self.check['artifacts'] = ['never-created.txt']; self.save()
        result, code = self.run_one()
        self.assertEqual(code, 1)
        self.assertEqual(result['outcome'], 'error')

    def test_removed_state_is_conflict_not_false_success(self):
        self.oracle.write_text("from pathlib import Path\nPath('progress.json').unlink()\n")
        result, code = self.run_one()
        self.assertEqual(code, 4)
        self.assertFalse(result['state_committed'])
        self.assertFalse(self.path.exists())

    def test_evidence_path_escape_rejected_before_execution(self):
        with self.assertRaises(ValueError): self.run_one(evidence_dir='../outside')
        self.assertFalse((self.root/'executions.txt').exists())

    def test_legacy_unscoped_always_record_survives_and_new_run_satisfies(self):
        self.app.write_text('def total():\n    return 2\n')
        self.check['rerun_policy'] = 'always'
        self.state['checkpoint_id'] = 'release-2'
        old = {'sequence': 1, 'goal_id': self.state['goal_id'], 'check_id': 'total',
               'basis': compute_basis(self.check, self.root), 'outcome': 'pass',
               'observation_id': 'legacy-pass', 'evidence_ref': 'unavailable-legacy-proof.json'}
        self.state['history'] = [copy.deepcopy(old)]
        self.save()
        report = assess(self.read(), evidence_root=self.root)
        self.assertEqual(report['decision'], 'run_check')
        result, code = self.run_one()
        self.assertEqual(code, 0)
        self.assertEqual(result['guard']['required_gaps'], [])
        self.assertEqual(self.read()['history'][0], old)
        self.assertEqual(len(self.read()['history']), 2)
        self.assertEqual(self.read()['history'][1]['checkpoint_id'], 'release-2')

    def test_incomplete_optional_legacy_record_cannot_block_required_run(self):
        self.app.write_text('def total():\n    return 2\n')
        other = copy.deepcopy(self.check);other.update(id='old-diagnostic', required=False, rerun_policy='always')
        self.state['checks'].append(other)
        self.state['history'] = [{'sequence': 1, 'goal_id': self.state['goal_id'], 'check_id': other['id'],
                                 'basis': compute_basis(other, self.root), 'outcome': 'pass',
                                 'observation_id': 'old', 'evidence_ref': 'lost.json'}]
        self.save()
        result, code = self.run_one()
        self.assertEqual(code, 0)
        self.assertEqual(result['guard']['required_gaps'], [])
        self.assertEqual(len(self.read()['history']), 2)


if __name__ == '__main__':unittest.main()
