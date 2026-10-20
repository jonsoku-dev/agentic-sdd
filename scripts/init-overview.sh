#!/usr/bin/env bash
# Create overview spec under the project's canonical Spec Kit root.
# Usage: init-overview.sh [--project DIR] [--root specs|.specify/specs]

set -euo pipefail

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
    *)
      echo "Usage: $0 [--project DIR] [--root specs|.specify/specs]" >&2
      exit 1
      ;;
  esac
done

PROJECT="$(cd "$PROJECT" && pwd)"

if [ -z "$SPEC_ROOT" ]; then
  if [ -d "${PROJECT}/.specify/specs" ] && [ ! -d "${PROJECT}/specs" ]; then
    SPEC_ROOT=".specify/specs"
  else
    SPEC_ROOT="specs"
  fi
fi

DIR="${PROJECT}/${SPEC_ROOT}/000-overview"
mkdir -p "$DIR"

if [ ! -f "$DIR/spec.md" ]; then
  cat > "$DIR/spec.md" << 'EOF'
# Project Overview

## Overall Goal
[1–2 sentences describing the overall Final Goal]

## Child Specs
<!-- Link numbered features as they are created -->
- 

## Current Status
See root progress.md Overall line.

## Notes
- Shared Spec Kit authority: one `.specify/` + one canonical spec root.
EOF
  echo "Created $DIR/spec.md"
else
  echo "Overview already exists at $DIR/spec.md"
fi
