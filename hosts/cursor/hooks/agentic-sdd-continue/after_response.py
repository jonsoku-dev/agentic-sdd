#!/usr/bin/env python3
"""afterAgentResponse: keep the front of the last assistant message."""

from __future__ import annotations

import sys

from common import handle_after_response, read_payload


def main() -> int:
    try:
        handle_after_response(read_payload())
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
