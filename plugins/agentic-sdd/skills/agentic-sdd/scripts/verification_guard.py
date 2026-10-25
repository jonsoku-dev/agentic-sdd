#!/usr/bin/env python3
"""Detect redundant verification from a bounded snapshot of existing receipts.

Read --state FILE and print a JSON recommendation; never run commands, edit files,
waive required checks, or declare the goal complete. Exit 0 on a valid report,
2 on invalid input. Observation/basis identities must come from actual evidence.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from verification_evidence import compute_basis, validate_event

BASIS_FIELDS = ('implementation', 'inputs', 'environment', 'oracle')
OUTCOMES = {'pass', 'fail', 'error', 'blocked', 'skipped'}


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be a non-empty string')
    return value


def basis(value: Any) -> tuple[str, ...]:
    if not isinstance(value, dict):
        raise ValueError('basis must identify implementation, inputs, environment, and oracle')
    return tuple(text(value.get(key), f'basis.{key}') for key in BASIS_FIELDS)


def assess(state: Any, threshold: int = 2, evidence_root: Path | None = None) -> dict[str, Any]:
    if not isinstance(state, dict):
        raise ValueError('state must be an object')
    if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
        raise ValueError('threshold must be a positive integer')
    goal = text(state.get('goal_id'), 'goal_id')
    proposal = text(state.get('proposed_check'), 'proposed_check')
    checkpoint = text(state['checkpoint_id'], 'checkpoint_id') if 'checkpoint_id' in state else None
    rows, history = state.get('checks'), state.get('history')
    if not isinstance(rows, list) or not rows or not isinstance(history, list):
        raise ValueError('checks must be a non-empty list and history must be a list')
    checks: dict[str, dict[str, Any]] = {}
    basis_issues: dict[str, str] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each check must be an object')
        key = text(row.get('id'), 'check.id')
        if key in checks:
            raise ValueError(f'duplicate check id: {key}')
        if type(row.get('required')) is not bool:
            raise ValueError(f'{key}.required must be boolean')
        if row.get('rerun_policy') not in ('on_change', 'always'):
            raise ValueError(f'{key}.rerun_policy must be on_change or always')
        criteria = row.get('criteria')
        if not isinstance(criteria, list) or not criteria:
            raise ValueError(f'{key} must map to at least one acceptance criterion')
        for criterion in criteria:
            text(criterion, 'criterion')
        row = dict(row)
        if 'basis_sources' in row:
            try:
                if evidence_root is None:
                    raise ValueError('evidence_root is required for current source fingerprints')
                row['basis'] = compute_basis(row, evidence_root)
            except (ValueError, OSError) as exc:
                basis_issues[key] = str(exc)
                row.setdefault('basis', {field: 'unavailable' for field in BASIS_FIELDS})
        basis(row.get('basis'))
        checks[key] = row
    if proposal not in checks:
        raise ValueError('proposed_check is outside the admitted check list')

    seen_observations: set[tuple[str, str, str]] = set()
    seen_passes: set[tuple[str, tuple[str, ...], str | None]] = set()
    latest: dict[str, dict[str, Any]] = {}
    outcomes_by_basis: dict[tuple[str, tuple[str, ...]], set[str]] = {}
    current_checkpoint: dict[str, dict[str, Any]] = {}
    streaks = {key: 0 for key in checks}
    evidence_issues: dict[str, str] = {}
    trusted: dict[int, bool] = {}
    legacy_unscoped: list[int] = []
    streak, last_sequence = 0, 0
    for event in history:
        if not isinstance(event, dict):
            raise ValueError('each history event must be an object')
        sequence = event.get('sequence')
        if type(sequence) is not int or sequence != last_sequence + 1:
            raise ValueError('history sequence must start at 1 and be contiguous; do not discard prior attempts')
        last_sequence = sequence
        if event.get('goal_id') != goal:
            raise ValueError('history belongs to a different goal')
        key = event.get('check_id')
        if not isinstance(key, str) or key not in checks:
            raise ValueError('history contains an unrecognized check_id')
        outcome = event.get('outcome')
        if not isinstance(outcome, str) or outcome not in OUTCOMES:
            raise ValueError('unsupported check outcome')
        identity = basis(event.get('basis'))
        event_checkpoint = text(event['checkpoint_id'], 'history.checkpoint_id') if event.get('checkpoint_id') is not None else None
        if checks[key]['rerun_policy'] == 'always' and event_checkpoint is None:
            legacy_unscoped.append(sequence)
        observation = text(event.get('observation_id'), 'observation_id')
        text(event.get('evidence_ref'), 'evidence_ref')
        signature = (key, outcome, observation)
        proof = (key, identity)
        pass_identity = (*proof, event_checkpoint if checks[key]['rerun_policy'] == 'always' else None)
        verified, evidence_reason = validate_event(event, checks[key], goal, evidence_root, require_current=False)
        trusted[sequence] = verified and key not in basis_issues
        if not trusted[sequence]:
            evidence_issues[str(sequence)] = basis_issues.get(key, evidence_reason)
        # Unverified legacy passes never establish progress or fresh acceptance.
        changed = ((outcome == 'pass' and trusted[sequence] and pass_identity not in seen_passes) or
                   (outcome in {'fail', 'error', 'blocked'} and trusted[sequence]
                    and signature not in seen_observations))
        if trusted[sequence]:
            outcomes_by_basis.setdefault(proof, set()).add(outcome)
        streak = 0 if changed else streak + 1
        streaks[key] = 0 if changed else streaks[key] + 1
        seen_observations.add(signature)
        if outcome == 'pass' and trusted[sequence]:
            seen_passes.add(pass_identity)
        # A later failure/skip on the same basis supersedes an earlier pass.
        if identity == basis(checks[key]['basis']):
            latest[key] = event
            if checkpoint is not None and event_checkpoint == checkpoint:
                current_checkpoint[key] = event

    def unstable_check(key: str) -> bool:
        return {'pass', 'fail'} <= outcomes_by_basis.get((key, basis(checks[key]['basis'])), set())

    def receipt(key: str) -> dict[str, Any] | None:
        return (current_checkpoint if checks[key]['rerun_policy'] == 'always' else latest).get(key)

    def passed(key: str) -> bool:
        item = receipt(key)
        if not item or item['outcome'] != 'pass' or not trusted.get(item['sequence']) or unstable_check(key):
            return False
        valid, reason = validate_event(item, checks[key], goal, evidence_root)
        if not valid:
            evidence_issues[str(item['sequence'])] = reason
        return valid

    gaps = [key for key, row in checks.items() if row['required'] and not passed(key)]
    selected = checks[proposal]
    previous = receipt(proposal)
    unstable = unstable_check(proposal)
    can_reuse = passed(proposal)
    if proposal in basis_issues:
        decision, reason = 'repair_state', 'current_basis_unavailable'
    elif selected['rerun_policy'] == 'always' and checkpoint is None:
        decision, reason = 'repair_state', 'current_checkpoint_identity_missing'
    elif unstable:
        decision, reason = 'recover', 'conflicting_behavior_on_same_basis'
    elif can_reuse:
        decision = 'reuse_pass'
        reason = ('already_passed_current_checkpoint' if selected['rerun_policy'] == 'always'
                  else 'same_relevant_basis_already_passed')
    elif previous is None:
        # Prior failures cannot prohibit the first observation after a real change
        # or make an unrelated, not-yet-run check wait for another diagnosis.
        decision = 'run_check'
        reason = 'current_basis_or_checkpoint_not_yet_checked'
    elif previous['outcome'] == 'pass' and not can_reuse:
        decision, reason = 'run_check', 'recorded_pass_has_no_verified_evidence'
    elif streaks[proposal] >= threshold:
        decision, reason = 'recover', 'selected_check_repeats_without_new_observation'
    else:
        decision, reason = 'run_check', 'current_required_or_discriminating_evidence_needed'
    return {
        'goal_id': goal, 'proposed_check': proposal,
        'decision': decision, 'reason': reason,
        'no_progress_streak': streak, 'threshold': threshold,
        'selected_check_no_progress_streak': streaks[proposal],
        'no_progress_by_check': streaks,
        'checkpoint_id': checkpoint,
        'required_gaps': gaps,
        'reusable_evidence': previous['evidence_ref'] if can_reuse else None,
        'completion_decided': False,
        'evidence_status': 'receipt_integrity_checked_not_a_security_attestation',
        'evidence_issues': evidence_issues,
        'basis_issues': basis_issues,
        'legacy_unscoped_history': legacy_unscoped,
    }


def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state', required=True, help='snapshot derived from existing feature checks/receipts; see recovery.md')
    parser.add_argument('--evidence-root', type=Path, help='owned project root for receipt/source/log verification; no pass is reusable without it')
    parser.add_argument('--threshold', type=int, default=2, help='no-progress attempts before a recovery checkpoint (default: 2)')
    args = parser.parse_args()
    try:
        state = json.loads(Path(args.state).read_text(), object_pairs_hook=unique_object)
        print(json.dumps(assess(state, args.threshold, args.evidence_root), ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, OSError) as exc:
        parser.exit(2, f'verification_guard: {exc}\n')


if __name__ == '__main__':
    sys.exit(main())
