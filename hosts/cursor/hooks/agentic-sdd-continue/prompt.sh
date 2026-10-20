#!/bin/sh
export PATH="/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin:${PATH}"
DIR="$(CDPATH= cd -- "$(dirname "$0")" && pwd)"
SCRIPT="$DIR/prompt.py"
if [ ! -f "$SCRIPT" ]; then
  { command -p cat 2>/dev/null || cat; } >/dev/null 2>&1 || :
  printf '%s\n' '{"continue":true}'
  exit 0
fi
exec /usr/bin/python3 "$SCRIPT"
