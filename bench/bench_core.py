#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
from typing import Iterable, List, Tuple
from urllib import parse, request

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import datefinder  # noqa: E402


def load_dataset(path: Path) -> List[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_v2(lines: Iterable[str]) -> int:
    total = 0
    for line in lines:
        total += len(datefinder.extract(line, reference_dt=datetime.now(timezone.utc), stream=False))
    return total


def run_duckling_http(lines: Iterable[str], url: str) -> int:
    total = 0
    for line in lines:
        payload = parse.urlencode({"locale": "en_US", "text": line}).encode("utf-8")
        req = request.Request(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body)
            total += len(parsed)
    return total


def run_duckling_python(lines: Iterable[str]) -> int:
    try:
        import duckling  # type: ignore
    except Exception as exc:
        raise RuntimeError("duckling python module is not available") from exc

    parser = duckling.Duckling()
    if hasattr(parser, "load"):
        parser.load()

    total = 0
    ref_time = int(datetime.now(timezone.utc).timestamp() * 1000)
    for line in lines:
        # pyduckling and pyduckling-native vary slightly; keep common args only.
        parsed = parser.parse(line, dim_filter=["time"], reference_time=ref_time)
        total += len(parsed)
    return total


def timed(fn, *args) -> Tuple[float, int]:
    start = time.perf_counter()
    count = fn(*args)
    elapsed = time.perf_counter() - start
    return elapsed, count


def summarize(name: str, times: List[float], total_chars: int, total_matches: int) -> str:
    med = statistics.median(times)
    p95 = sorted(times)[max(0, int(len(times) * 0.95) - 1)]
    chars_sec = total_chars / med if med > 0 else 0.0
    docs = max(1, total_chars // 100)
    docs_sec = docs / med if med > 0 else 0.0
    return (
        f"{name}: median={med:.6f}s p95={p95:.6f}s chars/sec={chars_sec:.2f} "
        f"approx_docs/sec={docs_sec:.2f} matches={total_matches}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--duckling-url", type=str, default=None)
    parser.add_argument("--duckling-python", action="store_true")
    args = parser.parse_args()

    lines = load_dataset(args.dataset)
    total_chars = sum(len(x) for x in lines)

    v2_times: List[float] = []
    v2_matches = 0
    for _ in range(args.iterations):
        elapsed, matches = timed(run_v2, lines)
        v2_times.append(elapsed)
        v2_matches = matches
    print(summarize("datefinder_v2", v2_times, total_chars, v2_matches))

    if args.duckling_url:
        dk_times: List[float] = []
        dk_matches = 0
        for _ in range(args.iterations):
            elapsed, matches = timed(run_duckling_http, lines, args.duckling_url)
            dk_times.append(elapsed)
            dk_matches = matches
        print(summarize("duckling_http", dk_times, total_chars, dk_matches))
    elif args.duckling_python:
        dk_times = []
        dk_matches = 0
        for _ in range(args.iterations):
            elapsed, matches = timed(run_duckling_python, lines)
            dk_times.append(elapsed)
            dk_matches = matches
        print(summarize("duckling_python", dk_times, total_chars, dk_matches))


if __name__ == "__main__":
    main()
