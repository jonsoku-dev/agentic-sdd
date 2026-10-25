#!/usr/bin/env bash
# Scaffold a numbered Spec Kit feature directory when the CLI surface is unavailable.
# Prefer installed Spec Kit specify/plan/tasks commands when present.
# Usage: init-spec-dir.sh <number> <short-name> [--project DIR] [--root specs|.specify/specs]
# Example: init-spec-dir.sh 001 user-auth --project .

set -euo pipefail

NUM=""
NAME=""
PROJECT="."
SPEC_ROOT=""

while [ $# -gt 0 ]; do
  case "$1" in
    --project|-p)
      PROJECT="$2"
      shift 2
      ;;
    --root)
      SPEC_ROOT="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      if [ -z "$NUM" ]; then
        NUM="$1"
      elif [ -z "$NAME" ]; then
        NAME="$1"
      else
        echo "Unexpected argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [ -z "$NUM" ] || [ -z "$NAME" ]; then
  echo "Usage: $0 <number> <short-name> [--project DIR] [--root specs|.specify/specs]" >&2
  exit 1
fi

if ! [[ "$NUM" =~ ^[0-9]{3,}$ ]]; then
  echo "Number should be zero-padded digits (e.g. 001): $NUM" >&2
  exit 1
fi
if ! [[ "$NAME" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "Name must be alphanumeric / dash / underscore: $NAME" >&2
  exit 1
fi

PROJECT="$(cd "$PROJECT" && pwd)"

if [ -z "$SPEC_ROOT" ]; then
  if [ -d "${PROJECT}/.specify/specs" ] && [ ! -d "${PROJECT}/specs" ]; then
    SPEC_ROOT=".specify/specs"
  else
    SPEC_ROOT="specs"
  fi
fi

DIR="${PROJECT}/${SPEC_ROOT}/${NUM}-${NAME}"
mkdir -p "$DIR"

if [ -f "$DIR/spec.md" ]; then
  echo "Already exists: $DIR" >&2
  exit 1
fi

cat > "$DIR/spec.md" << 'EOF'
# [Feature Name]

## Goal
One or two sentences describing the user-facing outcome.

## User Stories
- As a [role], I want [capability] so that [benefit].

## Acceptance Scenarios
1. **Given** [state], **When** [action], **Then** [observable result]
2. **Given** [state], **When** [action], **Then** [observable result]
3. **Given** [state], **When** [action], **Then** [observable result]

## Out of Scope
- 

## Notes
- 
EOF

cat > "$DIR/plan.md" << 'EOF'
# Plan

## Approach
[High-level technical approach]

## Verification contract
| Acceptance ID | Check / repro | Required result | Evidence class |
|---------------|---------------|-----------------|----------------|
| AC1 | | | test |

## Key Decisions
- 

## Risks
- 
EOF

cat > "$DIR/tasks.md" << 'EOF'
# Tasks

## Implement
- [ ] T1: 
- [ ] T2: 
EOF

if [ ! -f "${PROJECT}/progress.md" ]; then
  cat > "${PROJECT}/progress.md" << 'EOF'
# Progress

## Overall
Not started.

## Scope for this session
[Active feature / phase]

## Current outputs
- 

## Completed
- 

## Decisions
- 

## Open issues
- 

## Next action
[One concrete Spec Kit phase step]

## Last updated
EOF
fi

echo "Created $DIR with spec.md, plan.md, tasks.md"
echo "Root progress.md ensured at ${PROJECT}/progress.md"
echo "Prefer Spec Kit phase commands when the project has them installed."
