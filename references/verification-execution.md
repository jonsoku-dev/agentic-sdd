# Verification execution

Use for repeatable, already admitted CLI checks where collecting real evidence
or preventing a redundant run matters. Python 3.10+ and standard library only;
the current runner is exercised on POSIX. It is not a sandbox or authorization
service. Review the command against repository policy before `--execute`.

## Declare the existing check

Keep a small execution snapshot alongside existing feature artifacts. The spec
and plan remain authority. No new requirements are admitted by this JSON.

```json
{
  "goal_id": "feature-004",
  "checkpoint_id": "implementation-batch-1",
  "proposed_check": "save",
  "checks": [{
    "id": "save", "criteria": ["AC-1"], "required": true,
    "rerun_policy": "on_change",
    "command": ["python3", "-B", "checks/save.py"],
    "basis_sources": {
      "implementation": ["src/store.py"],
      "inputs": ["fixtures/input.json", "specs/004-save/spec.md"],
      "oracle": ["checks/save.py"]
    },
    "environment_keys": ["APP_ENV"],
    "environment_id": "local-test-instance",
    "observation_json_key": "observation",
    "artifacts": ["proofs/save.json"]
  }],
  "history": []
}
```

Paths are relative to an explicit owned project root. Declare all relevant source,
lockfile/dependency, fixture, and oracle files; do not include self-updating state
or generated outputs in basis_sources. Declare required proof outputs in artifacts.
Environment values are hashed, not copied into the receipt. The actual executable,
cwd, Python/platform, declared environment, and harness version are fingerprinted.
Undeclared dependencies cannot be verified automatically.

`observation_json_key` selects a stable top-level field from stdout JSON. Exclude
timestamps, filenames, and incidental counters. If absent, the runner uses the
conservative outcome/exit-code pair; a recovery review must inspect the logs to
distinguish different failures. Do not build a custom reporter if an existing
structured reporter already supplies suitable facts.

## Preview, execute once, inspect

```sh
python scripts/verification_run.py --state progress.json --root /owned/project
python scripts/verification_run.py --state progress.json --root /owned/project --execute
```

`--check ID` selects another admitted check. Loading a state file never executes
its command by itself. `--execute` runs the approved argv with shell=False only
when the guard returns run_check. It is not permission to run untrusted repository
commands, external/production actions, or prohibited browser drivers. For GUI
verification, use the allowed host tools and an appropriate evidence adapter.

The runner holds a state-writer lock, captures stdout/stderr and exit status,
checks fingerprints before and after, snapshots declared proof outputs per run,
then publishes a receipt and an atomic
history update. The state reference is the commit: orphan receipts from a conflict
are not automatically imported or treated as accepted evidence. Other writers'
state changes are preserved. Do not delete a lock until its actual owner/state
is understood. Interrupted runs can leave a lock or orphan; diagnose rather than
launching duplicate work or discarding history.

Timeout defaults to 60 seconds (`--timeout` can set a justified bound). Combined
output defaults to 1 MiB and is capped at 2 MiB. Only the process group started by
this run is killed on timeout/output overflow. A timeout, malformed observation,
missing declared proof, source change during execution, or state conflict cannot
produce an accepted pass. Proof artifacts are bounded to 64 MiB each; use a
reviewed compact extract/reference for larger profiling data.

Exit codes: 0 pass/reuse/read-only plan, 1 failed/error check, 2 invalid input,
3 recovery/state action required, 4 state/lock conflict. A subprocess exit 0
with contradictory same-basis evidence returns recovery rather than an accepted pass. Parse the JSON;
0 from a read-only plan is not execution success. A `run_check` decision is permission under the guard, not a requirement to run
the entire matrix; select the affected check scope first using recovery.md. Keep
logical check IDs and command recipes stable across output-only changes.
Commands are not retried by
this helper. The primary's recovery loop chooses the next action.

## Reuse and legacy records

A reusable receipt must match actual file/log/artifact SHA-256, goal, check,
checkpoint, command, current source/environment/harness basis, and successful
process flags. A made-up path or missing SHA never counts as a pass. The guard
recomputes basis from declared files even when a stored snapshot is stale.

Legacy rows are preserved. An old always row without checkpoint_id cannot satisfy
a current checkpoint, but it does not prohibit a fresh run or block another check.
Name the CURRENT checkpoint from the actual planned execution before an always
check; do not invent old IDs. The collector appends a new verifiable record.

Checks still need meaningful assertions and an honest declared dependency scope.
Hash integrity detects missing/stale/changed material; it does not defend against
an actor who can rewrite the validator, oracle, state, and every hash together.
Production trust may require a separately controlled CI verifier. Do not label
this local helper as that security boundary or equate an empty required_gaps list with the
original product's acceptance/convergence.
