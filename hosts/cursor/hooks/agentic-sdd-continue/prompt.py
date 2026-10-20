#!/usr/bin/env python3
"""beforeSubmitPrompt: arm, hold, or recognize an sdd-continue follow-up."""

from __future__ import annotations

import json
import sys

from common import handle_prompt, read_payload


def main() -> int:
    try:
        result = handle_prompt(read_payload())
    except Exception:
        result = {"continue": True}
    sys.stdout.write(json.dumps(result, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
