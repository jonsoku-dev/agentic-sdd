#!/usr/bin/env python3
"""Run one explicitly approved verification command with checked evidence.

Default is read-only planning. --execute runs the declared argv without a shell
only when the guard permits it. This is not a sandbox or permission grant.
Exit: 0 pass/reuse/plan, 1 check failed/error, 2 bad input, 3 recovery/state action required,
4 concurrent state/lock conflict. No automatic retry, code fix, or goal completion.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from verification_evidence import capture_artifacts, compute_basis, owned_path, resolve_executable, sha256_file
from verification_guard import assess, unique_object


class StateConflict(Exception):
    pass


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode()


def stamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def capture(argv: list[str], root: Path, timeout: float, limit: int) -> dict[str, Any]:
    """Bound output/time; terminate only the process group this invocation creates."""
    started = time.monotonic()
    proc = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            start_new_session=os.name == 'posix')
    chunks = {'stdout': bytearray(), 'stderr': bytearray()}
    timed_out = limited = False
    selector = selectors.DefaultSelector()
    for name in chunks:
        selector.register(getattr(proc, name), selectors.EVENT_READ, name)
    try:
        while selector.get_map():
            remaining = timeout - (time.monotonic() - started)
            if remaining <= 0:
                timed_out = True
                break
            for key, _ in selector.select(min(remaining, 0.1)):
                block = os.read(key.fileobj.fileno(), 65536)
                if not block:
                    selector.unregister(key.fileobj)
                    continue
                available = limit - sum(len(value) for value in chunks.values())
                chunks[key.data].extend(block[:available])
                if len(block) > available:
                    limited = True
                    break
            if limited:
                break
        if timed_out or limited:
            try:
                if os.name == 'posix': os.killpg(proc.pid, signal.SIGKILL)
                else: proc.kill()
            except ProcessLookupError:
                pass
        try:
            returncode = proc.wait(timeout=max(0.1, timeout - (time.monotonic() - started)))
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                if os.name == 'posix': os.killpg(proc.pid, signal.SIGKILL)
                else: proc.kill()
            except ProcessLookupError:
                pass
            returncode = proc.wait(timeout=2)
    finally:
        selector.close()
        for name in chunks: getattr(proc, name).close()
    return {'exit_code': returncode, 'timed_out': timed_out, 'output_limited': limited,
            **{name: bytes(data) for name, data in chunks.items()}}


def write_new(root: Path, reference: str, data: bytes) -> Path:
    target = owned_path(root, reference, must_exist=False)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open('xb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    return target


def run_check(state_path: Path, root: Path, *, execute: bool = False,
              timeout: float = 60, output_limit: int = 1024 * 1024,
              evidence_dir: str = '.sdd-evidence', check_id: str | None = None) -> tuple[dict, int]:
    root = root.resolve(strict=True)
    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError('timeout must be finite and positive')
    if type(output_limit) is not int or not 1 <= output_limit <= 2 * 1024 * 1024:
        raise ValueError('output limit must be 1..2097152 bytes')
    relative = str(state_path.relative_to(root)) if state_path.is_absolute() else str(state_path)
    state_path = owned_path(root, relative)
    # Validate storage path before any command runs.
    owned_path(root, f'{evidence_dir}/probe.json', must_exist=False)
    lock_path = state_path.with_name(state_path.name + '.verification.lock')
    locked = False
    lock_identity = None

    def lock_intact() -> bool:
        try:
            if lock_path.resolve(strict=True) != lock_path or lock_path.is_symlink(): return False
            info = lock_path.stat()
            return (info.st_dev, info.st_ino) == lock_identity
        except OSError:
            return False
    try:
        if execute:
            try:
                with lock_path.open('x') as lock:
                    lock.write(json.dumps({'pid': os.getpid(), 'started_at': stamp()}))
                    info = os.fstat(lock.fileno())
                    lock_identity = (info.st_dev, info.st_ino)
                locked = True
            except FileExistsError as exc:
                raise StateConflict('state is locked; inspect the existing owner, do not launch a second writer') from exc
        original = state_path.read_bytes()

        def unchanged() -> bool:
            try:
                return (lock_intact() and state_path.resolve(strict=True) == state_path
                        and not state_path.is_symlink() and state_path.read_bytes() == original)
            except OSError:
                return False

        state = json.loads(original, object_pairs_hook=unique_object)
        state = copy.deepcopy(state)
        if check_id is not None: state['proposed_check'] = check_id
        decision = assess(state, evidence_root=root)
        if not execute or decision['decision'] != 'run_check':
            return {'executed': False, 'guard': decision}, (0 if not execute or decision['decision'] == 'reuse_pass' else 3)
        check = next(row for row in state['checks'] if row['id'] == state['proposed_check'])
        before = compute_basis(check, root)
        command = check['command']
        executable = resolve_executable(command, root)
        started_at = stamp()
        result = capture([str(executable), *command[1:]], root, timeout, output_limit)
        fingerprint_error = None
        try:
            after = compute_basis(check, root)
        except (ValueError, OSError) as exc:
            after = None
            fingerprint_error = str(exc)
        source_changed = before != after
        outcome = ('error' if result['timed_out'] or result['output_limited'] or source_changed
                   else 'pass' if result['exit_code'] == 0 else 'fail')
        observation_error = None
        observation: Any = {'outcome': outcome, 'exit_code': result['exit_code']}
        key = check.get('observation_json_key')
        if key is not None and outcome not in ('error',):
            try:
                if not isinstance(key, str) or not key: raise ValueError('observation_json_key must be a non-empty string')
                payload = json.loads(result['stdout'], object_pairs_hook=unique_object)
                if not isinstance(payload, dict) or key not in payload: raise ValueError('structured observation is missing')
                observation = {'outcome': outcome, 'facts': payload[key]}
                encoded(observation)
            except (ValueError, UnicodeError, TypeError) as exc:
                observation_error = str(exc)
                outcome = 'error'
                observation = {'outcome': outcome, 'reason': 'invalid_structured_observation'}
        artifact_error = None
        try:
            artifacts = capture_artifacts(check, root)
        except (ValueError, OSError) as exc:
            artifacts = []
            artifact_error = str(exc)
            if outcome == 'pass': outcome = 'error'
        run_id = uuid.uuid4().hex
        prefix = f'{evidence_dir}/{run_id}'
        stdout_ref, stderr_ref, receipt_ref = prefix + '.stdout', prefix + '.stderr', prefix + '.json'
        for index, artifact in enumerate(artifacts):
            artifact['snapshot_ref'] = prefix + f'.artifact-{index}'
            source = owned_path(root, artifact['path'])
            data = source.read_bytes()
            if len(data) != artifact['bytes'] or digest(data) != artifact['sha256']:
                outcome = 'error'
                artifact_error = 'proof output changed while being captured'
            write_new(root, artifact['snapshot_ref'], data)
        stdout_path = write_new(root, stdout_ref, result['stdout'])
        stderr_path = write_new(root, stderr_ref, result['stderr'])
        receipt = {'schema_version': 1, 'run_id': run_id, 'goal_id': state['goal_id'],
                   'check_id': check['id'], 'checkpoint_id': state.get('checkpoint_id'),
                   'basis': before, 'command': command, 'cwd': str(root),
                   'resolved_executable': str(executable), 'outcome': outcome,
                   'exit_code': result['exit_code'], 'timed_out': result['timed_out'],
                   'output_limited': result['output_limited'], 'source_changed': source_changed,
                   'started_at': started_at, 'finished_at': stamp(),
                   'stdout_ref': stdout_ref, 'stdout_sha256': sha256_file(stdout_path),
                   'stderr_ref': stderr_ref, 'stderr_sha256': sha256_file(stderr_path),
                   'observation_error': observation_error, 'fingerprint_error': fingerprint_error,
                   'artifacts': artifacts, 'artifact_error': artifact_error}
        receipt_path = write_new(root, receipt_ref, encoded(receipt))
        if not unchanged():
            # Receipt is an unreferenced orphan; history publication is the commit.
            return {'executed': True, 'state_committed': False, 'status': 'state_conflict',
                    'orphan_receipt': receipt_ref, 'outcome': outcome}, 4
        check['basis'] = after or before
        event = {'sequence': len(state['history']) + 1, 'goal_id': state['goal_id'],
                 'check_id': check['id'], 'basis': before, 'outcome': outcome,
                 'observation_id': digest(encoded(observation)),
                 'evidence_ref': receipt_ref, 'evidence_sha256': sha256_file(receipt_path)}
        if state.get('checkpoint_id') is not None: event['checkpoint_id'] = state['checkpoint_id']
        state['history'].append(event)
        fd, temporary = tempfile.mkstemp(prefix='.verification-state-', dir=state_path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(encoded(state)); stream.flush(); os.fsync(stream.fileno())
            os.chmod(temporary, state_path.stat().st_mode & 0o777)
            if not unchanged():
                return {'executed': True, 'state_committed': False, 'status': 'state_conflict',
                        'orphan_receipt': receipt_ref, 'outcome': outcome}, 4
            os.replace(temporary, state_path)
        finally:
            if os.path.exists(temporary): os.unlink(temporary)
        current = assess(state, evidence_root=root)
        accepted = outcome == 'pass' and current['decision'] == 'reuse_pass'
        return {'executed': True, 'state_committed': True, 'run_id': run_id,
                'outcome': outcome, 'accepted_check': accepted, 'receipt': receipt_ref, 'guard': current}, (0 if accepted else 3 if outcome == 'pass' else 1)
    finally:
        if locked and lock_intact(): lock_path.unlink()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--check', help='admitted check id; defaults to state proposed_check')
    parser.add_argument('--execute', action='store_true', help='execute the reviewed argv; loading a state file alone never grants authority')
    parser.add_argument('--timeout', type=float, default=60)
    parser.add_argument('--max-output-bytes', type=int, default=1024 * 1024)
    parser.add_argument('--evidence-dir', default='.sdd-evidence')
    args = parser.parse_args()
    try:
        result, code = run_check(args.state, args.root, execute=args.execute, timeout=args.timeout,
                                 output_limit=args.max_output_bytes, evidence_dir=args.evidence_dir,
                                 check_id=args.check)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return code
    except StateConflict as exc:
        print(json.dumps({'executed': False, 'status': 'state_locked', 'error': str(exc)}))
        return 4
    except (ValueError, OSError, TypeError, KeyError) as exc:
        parser.exit(2, f'verification_run: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
