#!/usr/bin/env bash
# Check whether a Spec Kit feature spec is too large and should be split.
# Usage: check-spec-size.sh [path-to-spec.md] [--project DIR]
# Default: checks all specs under specs/ and .specify/specs/

set -euo pipefail

PROJECT="."
TARGET=""

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
      TARGET="$1"
      shift
      ;;
  esac
done

PROJECT="$(cd "$PROJECT" && pwd)"

check_one() {
  local file="$1"
  if [ ! -f "$file" ]; then
    echo "Missing: $file"
    return
  fi

  local lines ac_count status
  lines=$(wc -l < "$file" | tr -d ' ')
  ac_count=$(grep -cE '^[0-9]+\. ' "$file" || true)

  status="OK"
  if [ "$lines" -gt 120 ] || [ "$ac_count" -gt 7 ]; then
    status="SPLIT"
  fi

  printf "%-50s lines=%-4s ac≈%-3s %s\n" "$file" "$lines" "$ac_count" "$status"
}

if [ -n "$TARGET" ]; then
  if [[ "$TARGET" = /* ]]; then
    check_one "$TARGET"
  else
    check_one "${PROJECT}/${TARGET}"
  fi
  exit 0
fi

shopt -s nullglob
found=0
for root in "${PROJECT}/specs" "${PROJECT}/.specify/specs"; do
  for f in "${root}"/*/spec.md; do
    case "$f" in
      */000-overview/spec.md|*/overview/spec.md) continue ;;
    esac
    check_one "$f"
    found=1
  done
done

if [ "$found" -eq 0 ]; then
  echo "No specs found under ${PROJECT}/specs or ${PROJECT}/.specify/specs"
fi
