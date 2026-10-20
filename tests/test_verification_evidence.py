import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from verification_evidence import compute_basis, owned_path, resolve_executable, sha256_file, validate_event


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('src.py', 'oracle.py'):
            (self.root / name).write_text(name, encoding='utf-8')
        self.check = {
            'id': 'unit', 'criteria': ['AC-1'], 'required': True,
            'rerun_policy': 'on_change',
            'command': [sys.executable, '-c', 'print(1)'],
            'basis_sources': {'implementation': ['src.py'], 'inputs': [], 'oracle': ['oracle.py']},
            'environment_keys': [],
        }
        (self.root / 'stdout.log').write_bytes(b'1\n')
        (self.root / 'stderr.log').write_bytes(b'')
        self.event = {
            'goal_id': 'goal', 'check_id': 'unit', 'checkpoint_id': 'cp-1',
            'basis': compute_basis(self.check, self.root), 'outcome': 'pass',
            'evidence_ref': 'receipt.json',
        }
        self.receipt = {
            'schema_version': 1, 'goal_id': 'goal', 'check_id': 'unit',
            'checkpoint_id': 'cp-1', 'basis': self.event['basis'],
            'command': self.check['command'], 'cwd': str(self.root.resolve()),
            'outcome': 'pass', 'exit_code': 0, 'timed_out': False,
            'source_changed': False, 'output_limited': False,
            'stdout_ref': 'stdout.log', 'stdout_sha256': sha256_file(self.root / 'stdout.log'),
            'stderr_ref': 'stderr.log', 'stderr_sha256': sha256_file(self.root / 'stderr.log'),
        }
        self.save_receipt()

    def save_receipt(self):
        (self.root / 'receipt.json').write_text(json.dumps(self.receipt), encoding='utf-8')
        self.event['evidence_sha256'] = sha256_file(self.root / 'receipt.json')

    def assert_rejected(self, phrase):
        valid, reason = validate_event(self.event, self.check, 'goal', self.root)
        self.assertFalse(valid, reason)
        self.assertIn(phrase, reason)

    def test_valid_pass_and_basis_change(self):
        self.assertTrue(validate_event(self.event, self.check, 'goal', self.root)[0])
        (self.root / 'src.py').write_text('changed', encoding='utf-8')
        self.assert_rejected('basis is stale')

    def test_contract_change_invalidates_basis(self):
        self.check['criteria'] = ['AC-2']
        self.assert_rejected('basis is stale')

    def test_missing_and_tampered_receipt_or_logs(self):
        del self.event['evidence_sha256']
        self.assert_rejected('evidence_sha256')
        self.event['evidence_sha256'] = 'a' * 64
        self.assert_rejected('evidence SHA-256 mismatch')
        self.save_receipt()
        (self.root / 'stdout.log').write_bytes(b'tampered')
        self.assert_rejected('stdout SHA-256 mismatch')

    def test_malformed_json_and_metadata_mismatch(self):
        (self.root / 'receipt.json').write_text('{broken', encoding='utf-8')
        self.event['evidence_sha256'] = sha256_file(self.root / 'receipt.json')
        self.assert_rejected('Expecting property name')
        self.receipt['check_id'] = 'other'
        self.save_receipt()
        self.assert_rejected('receipt check_id')
        self.receipt['check_id'] = 'unit'
        self.receipt['checkpoint_id'] = 'other'
        self.save_receipt()
        self.assert_rejected('receipt checkpoint_id')

    def test_missing_receipt_field_and_environment_change(self):
        del self.receipt['checkpoint_id']
        self.save_receipt()
        self.assert_rejected('missing required field: checkpoint_id')
        self.receipt['checkpoint_id'] = 'cp-1'
        self.save_receipt()
        self.check['environment_id'] = 'changed-environment'
        self.assert_rejected('basis is stale')

    def test_pass_requires_clean_integer_zero(self):
        for field, value, phrase in [
            ('exit_code', False, 'exit_code'), ('exit_code', 1, 'exit_code'),
            ('timed_out', True, 'pass cannot'),
            ('source_changed', True, 'pass cannot'),
            ('output_limited', True, 'pass cannot'),
        ]:
            with self.subTest(field=field):
                original = self.receipt[field]
                self.receipt[field] = value
                self.save_receipt()
                self.assert_rejected(phrase)
                self.receipt[field] = original

    def test_outcome_binding_prevents_nonpass_as_pass(self):
        self.receipt['outcome'] = 'fail'
        self.save_receipt()
        self.assert_rejected('receipt outcome')
        self.event['outcome'] = 'fail'
        self.assertTrue(validate_event(self.event, self.check, 'goal', self.root)[0])

    def test_path_escape_and_symlink(self):
        for value in ('../outside', '/tmp/outside'):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    owned_path(self.root, value, must_exist=False)
        outside = self.root.parent / (self.root.name + '-outside')
        outside.write_text('outside', encoding='utf-8')
        self.addCleanup(outside.unlink)
        (self.root / 'escape').symlink_to(outside)
        self.event['evidence_ref'] = 'escape'
        self.assert_rejected('escapes root')
        self.event['evidence_ref'] = 'receipt.json'
        self.check['basis_sources']['implementation'] = ['escape']
        with self.assertRaisesRegex(ValueError, 'escapes root'):
            compute_basis(self.check, self.root)

    def test_legacy_missing_root_and_oversize_files(self):
        self.assertFalse(validate_event(self.event, self.check, 'goal', None)[0])
        del self.event['evidence_sha256']
        self.assert_rejected('evidence_sha256')
        self.save_receipt()
        (self.root / 'stderr.log').write_bytes(b'x' * (2 * 1024 * 1024 + 1))
        self.assert_rejected('stderr exceeds')

    def test_owned_path_requires_regular_file(self):
        (self.root / 'directory').mkdir()
        with self.assertRaisesRegex(ValueError, 'regular file'):
            owned_path(self.root, 'directory')
        if hasattr(os, 'mkfifo'):
            os.mkfifo(self.root / 'pipe')
            with self.assertRaisesRegex(ValueError, 'regular file'):
                owned_path(self.root, 'pipe')

    def test_relative_executable_and_path_are_root_based(self):
        tools = self.root / 'tools'
        tools.mkdir()
        script = tools / 'check'
        script.write_text('#!/bin/sh\nexit 0\n', encoding='utf-8')
        script.chmod(0o755)
        self.assertEqual(resolve_executable(['tools/check'], self.root), script.resolve())
        self.assertEqual(resolve_executable(['./tools/check'], self.root), script.resolve())
        with patch.dict(os.environ, {'PATH': 'tools'}, clear=False):
            self.assertEqual(resolve_executable(['check'], self.root), script.resolve())
            self.check['command'] = ['check']
            self.assertEqual(len(compute_basis(self.check, self.root)['environment']), 64)
        with patch.dict(os.environ, {'PATH': 'other'}, clear=False):
            with self.assertRaisesRegex(ValueError, 'cannot be resolved'):
                resolve_executable(['check'], self.root)


if __name__ == '__main__':
    unittest.main()
