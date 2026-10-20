#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from criterion_gate import decide, extract, questions

SPEC = """
### User Story 1

**Acceptance Scenarios**:

1. **Given** a listed share, **When** history is requested, **Then** sixty days of prices return.
2. **Given** the source is down, **When** history is requested, **Then** the run fails and no order is written.

---

### User Story 2

**Acceptance Scenarios**:

1. **Given** a buy signal, **When** evaluation runs, **Then** one paper buy is recorded.
"""


class CriterionGateTests(unittest.TestCase):
    def test_extract_keeps_each_given_when_then(self) -> None:
        rows = extract(SPEC)
        self.assertEqual([row["id"] for row in rows], ["c1", "c2", "c3"])
        self.assertIn("sixty days", rows[0]["text"])
        self.assertIn("paper buy", rows[2]["text"])

    def test_one_check_per_scenario(self) -> None:
        payload = questions(extract(SPEC))
        self.assertEqual([item["id"] for item in payload["questions"]], ["c1", "c2", "c3"])

    def test_one_miss_holds_the_next_spec(self) -> None:
        rows = extract(SPEC)
        result = decide(rows, {"c1": {"noul": 0.91}, "c2": {"noul": 0.69}, "c3": {"noul": 0.8}})
        self.assertFalse(result["advance"])
        self.assertEqual(result["advisory_review"][0]["id"], "c2")
        self.assertEqual(result["met"], 0)

    def test_high_scores_alone_never_advance(self) -> None:
        rows = extract(SPEC)
        result = decide(rows, {"c1": {"noul": 0.7}, "c2": {"noul": 0.71}, "c3": {"noul": 0.99}})
        self.assertFalse(result["advance"])
        self.assertEqual(result["advisory_review"], [])
        self.assertEqual(len(result["unmet"]), 3)


if __name__ == "__main__":
    unittest.main()
