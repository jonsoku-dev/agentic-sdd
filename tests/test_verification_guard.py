import copy
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verification_guard import assess as real_assess


def assess(value, threshold=2):
    # Isolate decision rules; test_verification_evidence/run cover real I/O without mocks.
    with mock.patch('verification_guard.validate_event', return_value=(True, 'control-flow fixture')):
        return real_assess(value, threshold)

BASIS = {'implementation': 'code-1', 'inputs': 'fixture-1', 'environment': 'env-1', 'oracle': 'test-1'}


def state(outcomes=()):
    return {'goal_id': 'feature-1', 'proposed_check': 'save',
            'checks': [{'id': 'save', 'criteria': ['AC-1'], 'required': True,
                        'rerun_policy': 'on_change', 'basis': dict(BASIS)}],
            'history': [event(i + 1, outcome) for i, outcome in enumerate(outcomes)]}


def event(sequence, outcome, observation=None):
    return {'sequence': sequence, 'goal_id': 'feature-1', 'check_id': 'save',
            'basis': dict(BASIS), 'outcome': outcome,
            'observation_id': observation or outcome + '-facts',
            'evidence_ref': f'run-{sequence}.json'}


class VerificationGuardTests(unittest.TestCase):
    def test_untrusted_distinct_failures_do_not_reset_progress(self):
        value = state()
        value['history'] = [event(i, 'fail', f'new-name-{i}') for i in range(1, 5)]
        with mock.patch('verification_guard.validate_event', return_value=(False, 'missing receipt')):
            result = real_assess(value)
        self.assertEqual(result['selected_check_no_progress_streak'], 4)
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(len(result['evidence_issues']), 4)

    def test_missing_required_result_runs_and_is_not_complete(self):
        result = assess(state())
        self.assertEqual(result['decision'], 'run_check')
        self.assertEqual(result['required_gaps'], ['save'])
        self.assertFalse(result['completion_decided'])

    def test_valid_pass_is_reused_without_requiring_two_more_runs(self):
        result = assess(state(['pass']))
        self.assertEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['reusable_evidence'], 'run-1.json')

    def test_renamed_files_and_models_do_not_create_progress(self):
        value = state(['fail', 'fail', 'fail'])
        for i, row in enumerate(value['history']):
            row['model'] = f'model-{i}'
            row['evidence_ref'] = f'new-report-{i}.json'
        result = assess(value)
        self.assertEqual(result['no_progress_streak'], 2)
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_repeated_green_reuses_evidence_and_does_not_finish_goal(self):
        result = assess(state(['pass', 'pass', 'pass']))
        self.assertEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['no_progress_streak'], 2)
        self.assertFalse(result['completion_decided'])

    def test_new_pass_report_metadata_is_not_progress(self):
        value = state(['pass', 'pass', 'pass'])
        for i, row in enumerate(value['history']):
            row['observation_id'] = f'new-report-format-{i}'
        self.assertEqual(assess(value)['no_progress_streak'], 2)

    def test_conflicting_pass_fail_same_basis_is_not_reused(self):
        result = assess(state(['pass', 'fail', 'pass']))
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(result['reason'], 'conflicting_behavior_on_same_basis')
        self.assertEqual(result['required_gaps'], ['save'])
        self.assertIsNone(result['reusable_evidence'])

    def test_truncated_history_cannot_reset_counter(self):
        value = state(['fail'])
        value['history'][0]['sequence'] = 10
        with self.assertRaises(ValueError):assess(value)

    def test_shared_change_invalidates_prior_pass(self):
        for field in BASIS:
            with self.subTest(field=field):
                value = state(['pass'])
                value['checks'][0]['basis'][field] = 'changed'
                result = assess(value)
                self.assertEqual(result['decision'], 'run_check')
                self.assertEqual(result['required_gaps'], ['save'])

    def test_new_findings_are_progress_even_if_all_checks_fail(self):
        value = state()
        value['history'] = [event(i, 'fail', f'new-defect-{i}') for i in range(1, 5)]
        result = assess(value)
        self.assertEqual(result['no_progress_streak'], 0)
        self.assertEqual(result['decision'], 'run_check')

    def test_code_churn_with_same_failure_is_not_progress(self):
        value = state(['fail', 'fail', 'fail'])
        for i, row in enumerate(value['history']):
            row['basis']['implementation'] = f'code-{i}'
        value['checks'][0]['basis']['implementation'] = 'code-2'
        result = assess(value)
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(result['no_progress_streak'], 2)

    def test_later_failure_invalidates_same_basis_pass(self):
        result = assess(state(['pass', 'fail']))
        self.assertNotEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_skipped_required_check_is_not_a_pass_or_progress(self):
        result = assess(state(['skipped', 'skipped']))
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_required_per_run_policy_cannot_be_waived(self):
        value = state(['pass', 'pass', 'pass'])
        value['checks'][0]['rerun_policy'] = 'always'
        value['checkpoint_id'] = 'current'
        for row in value['history']: row['checkpoint_id'] = 'previous'
        self.assertEqual(assess(value)['decision'], 'run_check')

    def test_optional_check_cannot_hide_another_required_failure(self):
        value = state(['fail'])
        other = copy.deepcopy(value['checks'][0])
        other.update(id='optional', required=False)
        value['checks'].append(other)
        row = event(2, 'pass');row['check_id'] = 'optional'
        value['history'].append(row);value['proposed_check'] = 'optional'
        result = assess(value)
        self.assertEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_repair_then_new_pass_resets_streak(self):
        value = state(['fail', 'fail', 'fail', 'pass'])
        value['checks'][0]['basis']['implementation'] = 'repaired-code'
        value['history'][-1]['basis']['implementation'] = 'repaired-code'
        self.assertEqual(assess(value)['no_progress_streak'], 0)
        self.assertEqual(assess(value)['required_gaps'], [])

    def test_bad_schema_and_mixed_goal_rejected(self):
        values = []
        value = state(['fail']);value['history'][0]['goal_id'] = 'other';values.append(value)
        value = state(['fail', 'fail']);value['history'][1]['sequence'] = 1;values.append(value)
        value = state(['fail']);del value['history'][0]['evidence_ref'];values.append(value)
        value = state();value['checks'][0]['required'] = 'true';values.append(value)
        value = state();value['checks'][0]['basis']['environment'] = '';values.append(value)
        value = state();value['proposed_check'] = 'unknown';values.append(value)
        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):assess(value)

    def test_loop_in_one_check_does_not_block_a_fresh_independent_check(self):
        value = state(['fail', 'fail', 'fail'])
        other = copy.deepcopy(value['checks'][0])
        other.update(id='independent', criteria=['AC-2'])
        value['checks'].append(other)
        value['proposed_check'] = 'independent'
        result = assess(value)
        self.assertEqual(result['decision'], 'run_check')
        self.assertEqual(result['required_gaps'], ['save', 'independent'])

    def test_first_run_after_real_repair_is_not_blocked_by_old_failures(self):
        value = state(['fail', 'fail', 'fail'])
        value['checks'][0]['basis']['implementation'] = 'repaired-code'
        self.assertEqual(assess(value)['decision'], 'run_check')
        # The changed basis allows an observation, not an endless unchanged retry.
        row = event(4, 'fail')
        row['basis']['implementation'] = 'repaired-code'
        value['history'].append(row)
        self.assertEqual(assess(value)['decision'], 'recover')

    def test_other_check_progress_does_not_mask_a_selected_loop(self):
        value = state(['fail', 'fail'])
        other = copy.deepcopy(value['checks'][0])
        other.update(id='other', criteria=['AC-2'])
        value['checks'].append(other)
        row = event(3, 'pass'); row['check_id'] = 'other'
        value['history'].extend([row, event(4, 'fail')])
        self.assertEqual(assess(value)['decision'], 'recover')

    def test_always_check_past_pass_remains_gap_in_new_checkpoint(self):
        value = state(['pass'])
        value['checks'][0]['rerun_policy'] = 'always'
        value['checkpoint_id'] = 'release-2'
        value['history'][0]['checkpoint_id'] = 'release-1'
        other = copy.deepcopy(value['checks'][0])
        other.update(id='other', criteria=['AC-2'], rerun_policy='on_change')
        value['checks'].append(other)
        row = event(2, 'pass'); row['check_id'] = 'other'
        value['history'].append(row); value['proposed_check'] = 'other'
        result = assess(value)
        self.assertEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_always_pass_is_reused_once_within_current_checkpoint(self):
        value = state(['pass'])
        value['checks'][0]['rerun_policy'] = 'always'
        value['checkpoint_id'] = 'release-1'
        value['history'][0]['checkpoint_id'] = 'release-1'
        result = assess(value)
        self.assertEqual(result['decision'], 'reuse_pass')
        self.assertEqual(result['required_gaps'], [])
        value['checkpoint_id'] = 'release-2'
        result = assess(value)
        self.assertEqual(result['decision'], 'run_check')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_missing_checkpoint_requests_input_repair_instead_of_endless_runs(self):
        value = state(['pass'])
        value['checks'][0]['rerun_policy'] = 'always'
        self.assertEqual(assess(value)['decision'], 'repair_state')
        value['checkpoint_id'] = 'current'
        result = assess(value)
        self.assertEqual(result['decision'], 'run_check')
        self.assertEqual(result['required_gaps'], ['save'])
        self.assertEqual(result['legacy_unscoped_history'], [1])

    def test_checkpoint_change_cannot_hide_same_basis_conflict(self):
        value = state(['pass', 'fail'])
        value['checks'][0]['rerun_policy'] = 'always'
        value['checkpoint_id'] = 'release-2'
        for row in value['history']: row['checkpoint_id'] = 'release-1'
        result = assess(value)
        self.assertEqual(result['decision'], 'recover')
        self.assertEqual(result['required_gaps'], ['save'])

    def test_invalid_checkpoint_identity_rejected(self):
        for empty in ['', None, 1, False]:
            value = state(['pass']); value['checkpoint_id'] = empty
            with self.assertRaises(ValueError): assess(value)
            if empty is not None:
                value = state(['pass']); value['history'][0]['checkpoint_id'] = empty
                with self.assertRaises(ValueError): assess(value)

    def test_unscoped_optional_history_does_not_block_other_check(self):
        value = state(['fail'])
        other = copy.deepcopy(value['checks'][0]);other.update(id='old', required=False, rerun_policy='always')
        value['checks'].append(other)
        row = event(2, 'pass');row['check_id'] = 'old'
        value['history'].append(row)
        self.assertEqual(assess(value)['decision'], 'run_check')
        self.assertEqual(assess(value)['required_gaps'], ['save'])

    def test_missing_file_no_longer_reuses_self_reported_pass(self):
        value = state(['pass'])
        result = real_assess(value)
        self.assertEqual(result['decision'], 'run_check')
        self.assertEqual(result['required_gaps'], ['save'])
        self.assertIn('1', result['evidence_issues'])

    def test_threshold_must_be_positive_integer(self):
        for threshold in [True, 0, -1, 1.5]:
            with self.assertRaises(ValueError):assess(state(), threshold)

    def test_cli_read_only_json_and_input_error(self):
        script = Path(__file__).resolve().parents[1] / 'scripts/verification_guard.py'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'state.json';p.write_text(json.dumps(state(['fail', 'fail', 'fail'])))
            before = p.read_bytes()
            result = subprocess.run([sys.executable, str(script), '--state', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['decision'], 'recover')
            self.assertEqual(p.read_bytes(), before)
            p.write_text('{"goal_id":"one","goal_id":"two"}')
            result = subprocess.run([sys.executable, str(script), '--state', str(p)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn('duplicate JSON key', result.stderr)


if __name__ == '__main__':unittest.main()
