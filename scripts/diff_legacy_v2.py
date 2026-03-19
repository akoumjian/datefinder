#!/usr/bin/env python3
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import datefinder
try:
    from dateutil.parser import UnknownTimezoneWarning
except Exception:  # pragma: no cover
    UnknownTimezoneWarning = None  # type: ignore

if UnknownTimezoneWarning is not None:
    warnings.filterwarnings("ignore", category=UnknownTimezoneWarning)


DEFAULT_CORPUS = ROOT / "conformance" / "legacy_parity_cases.jsonl"
DEFAULT_SHOWCASE = ROOT / "conformance" / "ambiguity_multilingual_cases.jsonl"
DEFAULT_JUDGMENTS = ROOT / "conformance" / "interpretation_judgments.jsonl"
DEFAULT_REPORT_JSON = ROOT / "conformance" / "reports" / "legacy_v2_diff_summary.json"
DEFAULT_REPORT_MD = ROOT / "conformance" / "reports" / "legacy_v2_diff_report.md"
DEFAULT_SHOWCASE_MD = ROOT / "conformance" / "reports" / "ambiguity_showcase.md"
DEFAULT_BEHAVIOR_CHANGE_MD = ROOT / "conformance" / "reports" / "behavior_change_changelog.md"


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_dt(dt: datetime) -> str:
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt.isoformat()


def run_legacy(case: Dict[str, Any]) -> List[str]:
    base_date = case.get("base_date")
    if base_date:
        base_dt = datetime.fromisoformat(base_date)
    else:
        base_dt = None
    out = list(
        datefinder.find_dates_legacy(
            case["text"],
            strict=bool(case.get("strict", False)),
            first=case.get("first", "month"),
            base_date=base_dt,
        )
    )
    return [normalize_dt(x) for x in out]


def run_v2_compat(case: Dict[str, Any]) -> List[str]:
    ref_raw = case.get("reference_dt") or case.get("base_date")
    if ref_raw:
        ref_dt = datetime.fromisoformat(ref_raw)
    else:
        ref_dt = None
    out = list(
        datefinder.find_dates_compat(
            case["text"],
            strict=bool(case.get("strict", False)),
            first=case.get("first", "month"),
            reference_dt=ref_dt,
        )
    )
    return [normalize_dt(x) for x in out]


def run_v2_typed(case: Dict[str, Any]) -> List[str]:
    ref_raw = case.get("reference_dt") or case.get("base_date")
    if ref_raw:
        ref_dt = datetime.fromisoformat(ref_raw)
    else:
        ref_dt = None
    out = datefinder.extract(
        case["text"],
        strict=bool(case.get("strict", False)),
        first=case.get("first", "month"),
        reference_dt=ref_dt,
        stream=False,
    )
    summary = []
    for m in out:
        summary.append(f"{m.kind}:{m.text}")
    return summary


def mismatch_reason(expected: List[str], actual: List[str]) -> str:
    if len(expected) != len(actual):
        return "count_mismatch"
    if expected != actual:
        return "value_mismatch"
    return "match"


def evaluate_parity(cases: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    rows = []
    counts = {
        "total": 0,
        "legacy_matches_expected": 0,
        "v2_matches_expected": 0,
        "v2_matches_legacy": 0,
        "legacy_expected_mismatches": 0,
        "v2_expected_mismatches": 0,
        "v2_legacy_mismatches": 0,
    }
    mismatch_samples = []

    for case in cases:
        counts["total"] += 1
        expected = case.get("expected_iso", [])
        legacy = run_legacy(case)
        v2 = run_v2_compat(case)

        legacy_reason = mismatch_reason(expected, legacy)
        v2_reason = mismatch_reason(expected, v2)
        v2_legacy_reason = mismatch_reason(legacy, v2)

        if legacy_reason == "match":
            counts["legacy_matches_expected"] += 1
        else:
            counts["legacy_expected_mismatches"] += 1

        if v2_reason == "match":
            counts["v2_matches_expected"] += 1
        else:
            counts["v2_expected_mismatches"] += 1

        if v2_legacy_reason == "match":
            counts["v2_matches_legacy"] += 1
        else:
            counts["v2_legacy_mismatches"] += 1

        row = {
            "id": case["id"],
            "text": case["text"],
            "first": case.get("first", "month"),
            "strict": bool(case.get("strict", False)),
            "expected_iso": expected,
            "legacy_iso": legacy,
            "v2_iso": v2,
            "legacy_reason": legacy_reason,
            "v2_reason": v2_reason,
            "v2_legacy_reason": v2_legacy_reason,
        }
        rows.append(row)
        if v2_legacy_reason != "match" and len(mismatch_samples) < 30:
            mismatch_samples.append(row)

    return {"counts": counts, "rows": rows, "mismatch_samples": mismatch_samples}


def build_markdown_report(summary: Dict[str, Any], out_path: Path) -> None:
    counts = summary["counts"]
    mismatches = summary["mismatch_samples"]
    lines = []
    lines.append("# Legacy vs v2 Differential Report")
    lines.append("")
    lines.append(f"- Total cases: {counts['total']}")
    lines.append(f"- Legacy matches expected: {counts['legacy_matches_expected']}")
    lines.append(f"- v2 matches expected: {counts['v2_matches_expected']}")
    lines.append(f"- v2 matches legacy: {counts['v2_matches_legacy']}")
    lines.append(f"- Legacy↔expected mismatches: {counts['legacy_expected_mismatches']}")
    lines.append(f"- v2↔expected mismatches: {counts['v2_expected_mismatches']}")
    lines.append(f"- v2↔legacy mismatches: {counts['v2_legacy_mismatches']}")
    lines.append("")
    lines.append("## Mismatch Samples")
    lines.append("")
    if not mismatches:
        lines.append("No mismatch samples.")
    else:
        for item in mismatches:
            lines.append(f"### {item['id']}")
            lines.append(f"- Text: `{item['text']}`")
            lines.append(f"- first=`{item['first']}` strict=`{item['strict']}`")
            lines.append(f"- Expected: `{item['expected_iso']}`")
            lines.append(f"- Legacy: `{item['legacy_iso']}`")
            lines.append(f"- v2: `{item['v2_iso']}`")
            lines.append(f"- Reason: `{item['v2_legacy_reason']}`")
            lines.append("")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_showcase(
    showcase_cases: Iterable[Dict[str, Any]],
    out_path: Path,
    judgments: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
    judgments = judgments or {}
    lines = []
    lines.append("# Ambiguity and Multilingual Showcase")
    lines.append("")
    lines.append("| id | text | legacy | v2_compat | v2_typed | preferred | note | rationale |")
    lines.append("|---|---|---|---|---|---|---|---|")

    audited_total = 0
    legacy_aligned = 0
    v2_compat_aligned = 0
    v2_typed_aligned = 0

    for case in showcase_cases:
        legacy = run_legacy(case)
        v2 = run_v2_compat(case)
        typed = run_v2_typed(case)
        decision = judgments.get(case["id"], {})
        preferred = decision.get("preferred", "")
        rationale = str(decision.get("rationale", "")).replace("|", "\\|")
        if preferred:
            audited_total += 1
            if preferred in {"legacy", "both"} and legacy:
                legacy_aligned += 1
            if preferred in {"v2_compat", "both"} and v2:
                v2_compat_aligned += 1
            if preferred == "v2_typed" and typed:
                v2_typed_aligned += 1

        text = case["text"].replace("|", "\\|")
        note = str(case.get("note", "")).replace("|", "\\|")
        lines.append(
            f"| {case['id']} | `{text}` | `{legacy}` | `{v2}` | `{typed}` | `{preferred}` | {note} | {rationale} |"
        )

    lines.insert(2, f"- Audited cases with preferred interpretation: {audited_total}")
    lines.insert(3, f"- Legacy aligned on audited cases: {legacy_aligned}/{audited_total or 1}")
    lines.insert(4, f"- v2_compat aligned on audited cases: {v2_compat_aligned}/{audited_total or 1}")
    lines.insert(5, f"- v2_typed aligned on audited cases: {v2_typed_aligned}/{audited_total or 1}")
    lines.insert(6, "")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_behavior_change_changelog(
    showcase_cases: Iterable[Dict[str, Any]],
    out_path: Path,
    judgments: Optional[Dict[str, Dict[str, Any]]] = None,
) -> None:
    judgments = judgments or {}
    lines: List[str] = []
    lines.append("# Behavior Change Changelog")
    lines.append("")
    lines.append("This document is generated from ambiguity scenarios plus interpretation judgments.")
    lines.append("")

    improvements: List[str] = []
    typed_additions: List[str] = []
    both_consistent: List[str] = []

    for case in showcase_cases:
        case_id = case["id"]
        legacy = run_legacy(case)
        v2 = run_v2_compat(case)
        typed = run_v2_typed(case)
        decision = judgments.get(case_id, {})
        preferred = decision.get("preferred", "")
        rationale = decision.get("rationale", "")
        note = case.get("note", "")
        text = case["text"]

        if preferred == "v2_compat":
            improvements.append(
                "\n".join(
                    [
                        f"## {case_id}",
                        f"- Text: `{text}`",
                        f"- Legacy: `{legacy}`",
                        f"- v2_compat: `{v2}`",
                        f"- Why: {rationale or note}",
                        "",
                    ]
                )
            )
        elif preferred == "v2_typed":
            typed_additions.append(
                "\n".join(
                    [
                        f"## {case_id}",
                        f"- Text: `{text}`",
                        f"- Legacy: `{legacy}`",
                        f"- v2_typed: `{typed}`",
                        f"- Why: {rationale or note}",
                        "",
                    ]
                )
            )
        elif preferred == "both":
            if legacy == v2:
                both_consistent.append(
                    f"- `{case_id}` `{text}` -> `{legacy}` ({rationale or note})"
                )

    lines.append("## v2 Compatibility Improvements Over Legacy")
    lines.append("")
    if not improvements:
        lines.append("No judged compatibility improvements.")
        lines.append("")
    else:
        lines.extend(improvements)

    lines.append("## v2 Typed Semantic Additions")
    lines.append("")
    if not typed_additions:
        lines.append("No judged typed-only additions.")
        lines.append("")
    else:
        lines.extend(typed_additions)

    lines.append("## Stable Behaviors (Both)")
    lines.append("")
    if not both_consistent:
        lines.append("No judged stable-behavior rows.")
    else:
        lines.extend(both_consistent[:30])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    parser.add_argument("--showcase", type=Path, default=DEFAULT_SHOWCASE)
    parser.add_argument("--judgments", type=Path, default=DEFAULT_JUDGMENTS)
    parser.add_argument("--out-json", type=Path, default=DEFAULT_REPORT_JSON)
    parser.add_argument("--out-md", type=Path, default=DEFAULT_REPORT_MD)
    parser.add_argument("--showcase-out-md", type=Path, default=DEFAULT_SHOWCASE_MD)
    parser.add_argument("--behavior-change-out-md", type=Path, default=DEFAULT_BEHAVIOR_CHANGE_MD)
    parser.add_argument(
        "--min-v2-legacy-ratio",
        type=float,
        default=0.0,
        help="Optional gate. Fail if (v2_matches_legacy / total) is below this ratio.",
    )
    args = parser.parse_args()

    corpus = load_jsonl(args.corpus)
    summary = evaluate_parity(corpus)
    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(json.dumps(summary["counts"], indent=2) + "\n", encoding="utf-8")
    build_markdown_report(summary, args.out_md)

    showcase = load_jsonl(args.showcase)
    judgments = {}
    if args.judgments.exists():
        judgments = {row["id"]: row for row in load_jsonl(args.judgments)}
    build_showcase(showcase, args.showcase_out_md, judgments=judgments)
    build_behavior_change_changelog(showcase, args.behavior_change_out_md, judgments=judgments)

    print(f"Parity corpus: {len(corpus)} cases")
    print(f"Wrote summary JSON: {args.out_json}")
    print(f"Wrote parity report: {args.out_md}")
    print(f"Wrote ambiguity showcase: {args.showcase_out_md}")
    print(f"Wrote behavior changelog: {args.behavior_change_out_md}")

    total = summary["counts"]["total"]
    ratio = (summary["counts"]["v2_matches_legacy"] / total) if total else 0.0
    print(f"v2_matches_legacy_ratio={ratio:.4f}")
    if ratio < args.min_v2_legacy_ratio:
        raise SystemExit(
            "Parity gate failed: v2 legacy-match ratio {:.4f} < {:.4f}".format(
                ratio, args.min_v2_legacy_ratio
            )
        )


if __name__ == "__main__":
    main()
