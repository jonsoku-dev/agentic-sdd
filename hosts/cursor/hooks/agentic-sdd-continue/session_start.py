#!/usr/bin/env python3
"""sessionStart: remember ask mode and background agents."""

from __future__ import annotations

import sys

from common import handle_session_start, read_payload


def main() -> int:
    try:
        handle_session_start(read_payload())
    except Exception:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
