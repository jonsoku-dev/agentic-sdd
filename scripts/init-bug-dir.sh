#!/usr/bin/env bash
# Scaffold a Spec Kit bug directory (assess → fix → test).
# Prefer installed: specify extension / speckit.bug.* when available.
# Usage: init-bug-dir.sh <slug> [--project DIR]
# Example: init-bug-dir.sh login-crash --project /path/to/repo

set -euo pipefail

SLUG=""
PROJECT="."

while [ $# -gt 0 ]; do
  case "$1" in
    --project|-p)
      PROJECT="$2"
      shift 2
      ;;
    -*)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
    *)
      if [ -z "$SLUG" ]; then
        SLUG="$1"
      else
        echo "Unexpected argument: $1" >&2
        exit 1
      fi
      shift
      ;;
  esac
done

if [ -z "$SLUG" ]; then
  echo "Usage: $0 <slug> [--project DIR]" >&2
  exit 1
fi

# Safe slug: alnum, dash, underscore
if ! [[ "$SLUG" =~ ^[A-Za-z0-9_-]+$ ]]; then
  echo "Slug must be alphanumeric / dash / underscore: $SLUG" >&2
  exit 1
fi

PROJECT="$(cd "$PROJECT" && pwd)"
DIR="${PROJECT}/.specify/bugs/${SLUG}"
mkdir -p "$DIR"

cat > "$DIR/assessment.md" << EOF
# Bug Assessment: ${SLUG}

- **Verdict**: real | invalid | needs-clarification
- **Symptom**: 
- **Suspected paths**: 
- **Proposed remediation**: 
- **Scope**: 
EOF

cat > "$DIR/fix.md" << EOF
# Bug Fix: ${SLUG}

- **Status**: applied | partial | not-applied
- **Changes**:
  | File | Change |
  |------|--------|
- **Deviations from Assessment**: 
EOF

cat > "$DIR/test.md" << EOF
# Bug Test: ${SLUG}

- **Verdict**: verified | partial | failed
- **Reproduction result**: 
- **Tests run**: 
- **Evidence**: 
EOF

echo "Created bug directory: $DIR"
echo "Fill assessment.md first. Only the fix stage should edit source code."
