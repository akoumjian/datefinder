#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import statistics
import time
from typing import Callable, Dict, Iterable, List, Optional, Tuple
from urllib import parse, request

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import datefinder  # noqa: E402

try:
    from dateparser.search import search_dates  # type: ignore
except Exception:
    search_dates = None


def _load_docs() -> List[Tuple[str, str]]:
    core_lines = [
        x.strip()
        for x in (ROOT / "bench" / "corpus_core.txt").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    core_text = "\n".join(core_lines)
    seattle = (ROOT / "tests" / "seattle_weekly.html").read_text(errors="ignore")
    test_data = (ROOT / "tests" / "test_data.txt").read_text(errors="ignore")
    return [
        ("core_corpus", core_text),
        ("seattle_html_76k", seattle),
        ("test_data_560k", test_data),
    ]


def _bench(fn: Callable[[str], int], text: str, iterations: int) -> Tuple[float, int]:
    times: List[float] = []
    count = 0
    for _ in range(iterations):
        start = time.perf_counter()
        count = fn(text)
        times.append(time.perf_counter() - start)
    return statistics.median(times), count


def _v2_count(text: str) -> int:
    ref = datetime(2026, 3, 18, 12, 0, tzinfo=timezone.utc)
    return len(datefinder.extract(text, reference_dt=ref))


def _legacy_count(text: str) -> int:
    return len(list(datefinder.find_dates_legacy(text)))


def _dateparser_count(text: str) -> int:
    if search_dates is None:
        return -1
    out = search_dates(text)
    return len(out or [])


def _duckling_http_count(text: str, url: str) -> int:
    payload = parse.urlencode({"locale": "en_US", "text": text}).encode("utf-8")
    req = request.Request(url, data=payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    with request.urlopen(req, timeout=180) as resp:
        return len(json.loads(resp.read().decode("utf-8")))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations-small", type=int, default=20)
    parser.add_argument("--iterations-large", type=int, default=2)
    parser.add_argument("--duckling-url", type=str, default="http://localhost:8000/parse")
    parser.add_argument(
        "--alt-max-bytes",
        type=int,
        default=200000,
        help="Skip dateparser/duckling for docs larger than this unless --force-all-alternatives is used.",
    )
    parser.add_argument("--force-all-alternatives", action="store_true")
    parser.add_argument("--out-json", type=Path, default=ROOT / "bench" / "benchmark_results.json")
    parser.add_argument("--out-md", type=Path, default=ROOT / "bench" / "benchmark_results.md")
    args = parser.parse_args()

    docs = _load_docs()
    rows: List[Dict[str, object]] = []
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")

    for name, text in docs:
        iterations = args.iterations_small if name == "core_corpus" else args.iterations_large
        size = len(text)

        v2_median, v2_count = _bench(_v2_count, text, iterations)
        legacy_median, legacy_count = _bench(_legacy_count, text, iterations)

        run_alts = args.force_all_alternatives or size <= args.alt_max_bytes

        dateparser_median = None
        dateparser_count = None
        if search_dates is not None and run_alts:
            try:
                dateparser_median, dateparser_count = _bench(_dateparser_count, text, iterations)
            except Exception:
                dateparser_median, dateparser_count = None, None

        duckling_median = None
        duckling_count = None
        if run_alts:
            try:
                duckling_median, duckling_count = _bench(lambda t: _duckling_http_count(t, args.duckling_url), text, iterations)
            except Exception:
                duckling_median, duckling_count = None, None

        rows.append(
            {
                "dataset": name,
                "size_bytes": size,
                "iterations": iterations,
                "v2_median_s": v2_median,
                "v2_matches": v2_count,
                "legacy_median_s": legacy_median,
                "legacy_matches": legacy_count,
                "dateparser_median_s": dateparser_median,
                "dateparser_matches": dateparser_count,
                "duckling_http_median_s": duckling_median,
                "duckling_http_matches": duckling_count,
            }
        )

    args.out_json.write_text(json.dumps({"timestamp_utc": stamp, "rows": rows}, indent=2) + "\n", encoding="utf-8")

    md: List[str] = []
    md.append(f"# Benchmark Results ({stamp})")
    md.append("")
    md.append("| dataset | size | v2 median (s) | legacy median (s) | dateparser median (s) | duckling_http median (s) | v2 vs legacy | v2 vs dateparser | v2 vs duckling_http |")
    md.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")

    for r in rows:
        def _fmt(v: Optional[float]) -> str:
            return f"{v:.6f}" if isinstance(v, float) else "n/a"

        v2 = r["v2_median_s"]
        legacy = r["legacy_median_s"]
        dp = r["dateparser_median_s"]
        dk = r["duckling_http_median_s"]
        assert isinstance(v2, float)
        assert isinstance(legacy, float)
        v2_vs_legacy = legacy / v2 if v2 > 0 else float("inf")
        v2_vs_dp = (dp / v2) if isinstance(dp, float) and v2 > 0 else None
        v2_vs_dk = (dk / v2) if isinstance(dk, float) and v2 > 0 else None
        md.append(
            "| {dataset} | {size} | {v2} | {legacy} | {dp} | {dk} | {v2l:.2f}x | {v2d} | {v2k} |".format(
                dataset=r["dataset"],
                size=r["size_bytes"],
                v2=_fmt(v2),
                legacy=_fmt(legacy),
                dp=_fmt(dp),
                dk=_fmt(dk),
                v2l=v2_vs_legacy,
                v2d=(f"{v2_vs_dp:.2f}x" if v2_vs_dp is not None else "n/a"),
                v2k=(f"{v2_vs_dk:.2f}x" if v2_vs_dk is not None else "n/a"),
            )
        )

    md.append("")
    md.append("Notes:")
    md.append("- `v2` uses `datefinder.extract(...)`.")
    md.append("- `legacy` uses `datefinder.find_dates_legacy(...)`.")
    md.append("- `dateparser` uses `dateparser.search.search_dates` when installed.")
    md.append("- `duckling_http` uses `POST /parse` on the configured Duckling URL.")
    md.append("- `n/a` means the engine was unavailable or failed for that dataset in this run.")
    md.append("- Results are hardware/environment dependent; use as directional guidance.")

    args.out_md.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")


if __name__ == "__main__":
    main()
