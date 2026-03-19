#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Iterable, List
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "conformance" / "legacy_parity_cases.jsonl"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import tests.test_find_dates as test_find_dates
import tests.test_find_dates_strict as test_find_dates_strict


def _iter_param_cases(func) -> Iterable[tuple]:
    for mark in getattr(func, "pytestmark", []):
        if mark.name != "parametrize":
            continue
        for case in mark.args[1]:
            yield case


def _normalize_expected(value) -> List[str]:
    if isinstance(value, list):
        return [v.isoformat() for v in value]
    if isinstance(value, datetime):
        return [value.isoformat()]
    return []


def build() -> None:
    rows = []
    idx = 0

    for input_text, expected_date, first in _iter_param_cases(test_find_dates.test_find_date_strings):
        idx += 1
        rows.append(
            {
                "id": f"legacy_find_{idx:03d}",
                "text": input_text,
                "first": first,
                "strict": False,
                "base_date": None,
                "expected_iso": _normalize_expected(expected_date),
                "source": "tests/test_find_dates.py",
            }
        )

    for input_text, expected_date in _iter_param_cases(test_find_dates_strict.test_find_date_strings_strict):
        idx += 1
        rows.append(
            {
                "id": f"legacy_strict_{idx:03d}",
                "text": input_text,
                "first": "month",
                "strict": True,
                "base_date": None,
                "expected_iso": _normalize_expected(expected_date),
                "source": "tests/test_find_dates_strict.py",
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} cases to {OUT}")


if __name__ == "__main__":
    build()
