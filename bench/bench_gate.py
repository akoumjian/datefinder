#!/usr/bin/env python3
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
from typing import Iterable, List
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
    ref = datetime.now(timezone.utc)
    for line in lines:
        total += len(datefinder.extract(line, reference_dt=ref, stream=False))
    return total


def run_duckling_http(lines: Iterable[str], url: str) -> int:
    total = 0
    for line in lines:
        payload = parse.urlencode({"locale": "en_US", "text": line}).encode("utf-8")
        req = request.Request(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
        with request.urlopen(req, timeout=10) as resp:
            total += len(json.loads(resp.read().decode("utf-8")))
    return total


def median_runtime(fn, lines: List[str], iterations: int, *args) -> float:
    samples: List[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn(lines, *args)
        samples.append(time.perf_counter() - start)
    return statistics.median(samples)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--duckling-url", type=str, required=True)
    parser.add_argument("--iterations", type=int, default=10)
    parser.add_argument(
        "--required-ratio",
        type=float,
        default=0.95,
        help="Require: v2_median <= duckling_median * required_ratio",
    )
    args = parser.parse_args()

    lines = load_dataset(args.dataset)
    v2_median = median_runtime(run_v2, lines, args.iterations)
    duckling_median = median_runtime(run_duckling_http, lines, args.iterations, args.duckling_url)

    ratio = v2_median / duckling_median if duckling_median > 0 else float("inf")
    print(
        "v2_median={:.6f}s duckling_median={:.6f}s ratio={:.4f} required<={:.4f}".format(
            v2_median, duckling_median, ratio, args.required_ratio
        )
    )

    if ratio > args.required_ratio:
        raise SystemExit(
            "Benchmark gate failed: v2 is not sufficiently faster than Duckling "
            "(ratio {:.4f} > {:.4f})".format(ratio, args.required_ratio)
        )

    print("Benchmark gate passed.")


if __name__ == "__main__":
    main()

