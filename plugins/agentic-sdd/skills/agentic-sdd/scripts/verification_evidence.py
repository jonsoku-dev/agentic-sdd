"""Local receipt integrity for bounded verification checks.

This ties a receipt to declared source files, command, environment, and logs.
It is not a sandbox or an attestation: a writer authorized to change this
validator and its state can forge evidence, and undeclared dependencies remain
outside the basis.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import stat
import sys
from pathlib import Path
from typing import Any

BASIS_FIELDS = ('implementation', 'inputs', 'environment', 'oracle')
SHA256_RE = re.compile(r'[0-9a-f]{64}\Z')
RECEIPT_LIMIT = 1024 * 1024
LOG_LIMIT = 2 * 1024 * 1024


def owned_path(root: Path, value: str, must_exist: bool = True) -> Path:
    """Resolve a root-relative regular file without permitting root escape."""
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('evidence root must be an existing directory')
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('file reference must be a non-empty root-relative path')
    relative = Path(value)
    if relative.is_absolute() or '..' in relative.parts or relative == Path('.'):
        raise ValueError(f'file reference must stay inside root: {value}')
    target = (root / relative).resolve(strict=must_exist)
    if not target.is_relative_to(root):
        raise ValueError(f'file reference escapes root: {value}')
    if must_exist or target.exists():
        if not target.is_file() or not stat.S_ISREG(target.stat().st_mode):
            raise ValueError(f'file reference must be a regular file: {value}')
    return target


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def _digest(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
                         allow_nan=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def _sources(check: dict[str, Any], root: Path, field: str) -> list[dict[str, str]]:
    groups = check.get('basis_sources')
    if not isinstance(groups, dict):
        raise ValueError('basis_sources must be an object')
    names = groups.get(field)
    if not isinstance(names, list) or (field != 'inputs' and not names):
        raise ValueError(f'basis_sources.{field} must be a non-empty file list' if field != 'inputs'
                         else 'basis_sources.inputs must be a file list')
    if any(not isinstance(name, str) for name in names) or len(names) != len(set(names)):
        raise ValueError(f'basis_sources.{field} contains invalid or duplicate paths')
    return [{'path': name, 'sha256': sha256_file(owned_path(root, name))}
            for name in sorted(names)]


def _command(check: dict[str, Any]) -> list[str]:
    command = check.get('command')
    if not isinstance(command, list) or not command or any(
            not isinstance(part, str) or not part for part in command):
        raise ValueError('command must be a non-empty argv list of non-empty strings')
    return command


def resolve_executable(command: list[str], root: Path) -> Path:
    """Resolve argv[0] as it would run with cwd=root, including relative PATH."""
    if not isinstance(command, list) or not command or not isinstance(command[0], str) or not command[0]:
        raise ValueError('command must have a non-empty executable')
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('evidence root must be an existing directory')
    executable = command[0]
    if Path(executable).is_absolute():
        resolved = Path(executable)
    elif '/' in executable:
        resolved = root / executable
    else:
        search_path = os.pathsep.join(
            str(Path(entry) if Path(entry).is_absolute() else root / entry)
            for entry in os.environ.get('PATH', os.defpath).split(os.pathsep))
        found = shutil.which(executable, path=search_path)
        if not found:
            raise ValueError(f'command executable cannot be resolved: {executable}')
        resolved = Path(found)
    try:
        resolved = resolved.resolve(strict=True)
    except OSError as exc:
        raise ValueError(f'command executable cannot be resolved: {executable}') from exc
    if not resolved.is_file() or not os.access(resolved, os.X_OK):
        raise ValueError(f'command executable is not an executable file: {executable}')
    return resolved


def compute_basis(check: dict[str, Any], root: Path) -> dict[str, str]:
    """Hash caller-declared files and the current command/environment contract."""
    if not isinstance(check, dict):
        raise ValueError('check must be an object')
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('evidence root must be an existing directory')
    command = _command(check)
    executable_path = resolve_executable(command, root)
    keys = check.get('environment_keys', [])
    if not isinstance(keys, list) or any(not isinstance(key, str) or not key for key in keys):
        raise ValueError('environment_keys must be a list of non-empty strings')
    if len(keys) != len(set(keys)):
        raise ValueError('environment_keys contains duplicate keys')
    environment_id = check.get('environment_id')
    if environment_id is not None and not isinstance(environment_id, str):
        raise ValueError('environment_id must be a string')
    files = {field: _sources(check, root, field) for field in ('implementation', 'inputs', 'oracle')}
    contract = {key: check.get(key) for key in
                ('id', 'criteria', 'required', 'rerun_policy', 'command', 'basis_sources',
                 'environment_keys', 'environment_id', 'observation_json_key', 'artifacts')}
    return {
        'implementation': _digest({'files': files['implementation'], 'command': command}),
        'inputs': _digest({'files': files['inputs'], 'command': command}),
        'environment': _digest({
            'root': str(root), 'cwd': str(root),
            'executable': str(executable_path), 'executable_sha256': sha256_file(executable_path),
            'python': sys.version, 'platform': platform.platform(),
            'environment': {key: _digest(os.environ.get(key)) for key in sorted(keys)},
            'environment_id': environment_id,
            'harness': {name: sha256_file(Path(__file__).with_name(name))
                        for name in ('verification_evidence.py', 'verification_guard.py', 'verification_run.py')
                        if Path(__file__).with_name(name).is_file()},
        }),
        'oracle': _digest({'files': files['oracle'], 'contract': contract}),
    }


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f'duplicate receipt JSON key: {key}')
        value[key] = item
    return value


def _checked_file(root: Path, reference: Any, expected_sha: Any, limit: int, label: str) -> Path:
    if not isinstance(reference, str) or not reference:
        raise ValueError(f'{label}_ref is missing or invalid')
    if not isinstance(expected_sha, str) or not SHA256_RE.fullmatch(expected_sha):
        raise ValueError(f'{label}_sha256 is missing or malformed')
    path = owned_path(root, reference)
    if path.stat().st_size > limit:
        raise ValueError(f'{label} exceeds {limit} bytes')
    if sha256_file(path) != expected_sha:
        raise ValueError(f'{label} SHA-256 mismatch')
    return path


def capture_artifacts(check: dict, root: Path) -> list[dict[str, Any]]:
    """Hash only explicitly declared proof outputs; never discover arbitrary files."""
    names = check.get('artifacts', [])
    if not isinstance(names, list) or any(not isinstance(name, str) for name in names) or len(names) != len(set(names)):
        raise ValueError('artifacts must be a unique list of relative file paths')
    result = []
    for name in names:
        path = owned_path(root, name)
        if path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('proof artifact exceeds 64 MiB; use a bounded declared proof extract')
        result.append({'path': name, 'sha256': sha256_file(path), 'bytes': path.stat().st_size})
    return result


def validate_event(event: dict, check: dict, goal_id: str,
                   root: Path | None, *, require_current: bool = True) -> tuple[bool, str]:
    """Validate an existing receipt and logs without executing its command."""
    try:
        if root is None:
            raise ValueError('evidence root is required to validate receipts')
        if not isinstance(event, dict) or not isinstance(check, dict):
            raise ValueError('event and check must be objects')
        if not isinstance(goal_id, str) or not goal_id:
            raise ValueError('goal_id is required')
        root = Path(root).resolve(strict=True)
        receipt_path = _checked_file(root, event.get('evidence_ref'),
                                     event.get('evidence_sha256'), RECEIPT_LIMIT, 'evidence')
        receipt = json.loads(receipt_path.read_text(encoding='utf-8'),
                             object_pairs_hook=_unique_object)
        if not isinstance(receipt, dict) or type(receipt.get('schema_version')) is not int or receipt['schema_version'] != 1:
            raise ValueError('receipt schema_version must be 1')
        required = ('goal_id', 'check_id', 'checkpoint_id', 'basis', 'command', 'cwd',
                    'outcome', 'exit_code', 'timed_out', 'source_changed',
                    'output_limited', 'stdout_ref', 'stdout_sha256', 'stderr_ref',
                    'stderr_sha256')
        missing = [field for field in required if field not in receipt]
        if missing:
            raise ValueError(f'receipt missing required field: {missing[0]}')
        for field, expected in (('goal_id', goal_id), ('check_id', check.get('id')),
                                ('checkpoint_id', event.get('checkpoint_id')),
                                ('basis', event.get('basis')),
                                ('outcome', event.get('outcome')),
                                ('command', _command(check)), ('cwd', str(root))):
            if receipt.get(field) != expected:
                raise ValueError(f'receipt {field} does not match current event/check')
        if event.get('goal_id') != goal_id or event.get('check_id') != check.get('id'):
            raise ValueError('event goal_id/check_id does not match current check')
        if require_current and event.get('basis') != compute_basis(check, root):
            raise ValueError('event basis is stale or differs from current files/contract')
        if event.get('outcome') not in ('pass', 'fail', 'error', 'blocked', 'skipped'):
            raise ValueError('event outcome is invalid')
        for label in ('stdout', 'stderr'):
            _checked_file(root, receipt.get(f'{label}_ref'),
                          receipt.get(f'{label}_sha256'), LOG_LIMIT, label)
        artifacts = receipt.get('artifacts', [])
        if not isinstance(artifacts, list) or any(not isinstance(item, dict) for item in artifacts):
            raise ValueError('artifact manifest must be a list of objects')
        if [item.get('path') for item in artifacts] != check.get('artifacts', []):
            raise ValueError('artifact manifest does not match declared outputs')
        for item in artifacts:
            snapshot = _checked_file(root, item.get('snapshot_ref'), item.get('sha256'), 64 * 1024 * 1024, 'artifact_snapshot')
            if type(item.get('bytes')) is not int or snapshot.stat().st_size != item['bytes']:
                raise ValueError('artifact snapshot size mismatch')
        if require_current and [{k: item.get(k) for k in ('path', 'sha256', 'bytes')} for item in artifacts] != capture_artifacts(check, root):
            raise ValueError('declared proof artifacts are missing, changed, or mismatched')
        if type(receipt.get('exit_code')) is not int and receipt.get('exit_code') is not None:
            raise ValueError('receipt exit_code must be an integer or null')
        for flag in ('timed_out', 'source_changed', 'output_limited'):
            if type(receipt.get(flag)) is not bool:
                raise ValueError(f'receipt {flag} must be boolean')
        if event['outcome'] == 'pass':
            if receipt.get('exit_code') != 0 or type(receipt.get('exit_code')) is not int:
                raise ValueError('pass requires exact integer exit_code 0')
            if any(receipt[flag] for flag in ('timed_out', 'source_changed', 'output_limited')):
                raise ValueError('pass cannot be timed out, source changed, or output limited')
        return True, 'receipt and logs match current check basis'
    except (ValueError, TypeError, OSError, UnicodeError, RuntimeError) as exc:
        return False, str(exc)
