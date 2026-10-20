#!/usr/bin/env python3
"""stop: follow up only while an armed agentic-sdd goal is still running."""

from __future__ import annotations

import json
import sys

from common import handle_stop, read_payload


def main() -> int:
    try:
        message = handle_stop(read_payload())
    except Exception:
        return 0
    if not message:
        return 0
    sys.stdout.write(json.dumps({"followup_message": message}, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
