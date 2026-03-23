from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from typing import Iterable, List, Optional, Sequence, Tuple

from . import (
    __version__,
    find_dates,
    find_dates_compat,
    find_dates_legacy,
    extract,
    AbsoluteValue,
    RelativeValue,
    DurationValue,
    IntervalValue,
    Match,
)


def _parse_reference(value: Optional[str]) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError as exc:
        raise SystemExit(f"Invalid --reference value '{value}': {exc}")


def _get_text(text_parts: Sequence[str]) -> str:
    if text_parts:
        return " ".join(text_parts)
    piped = sys.stdin.read()
    if piped:
        return piped
    raise SystemExit("No input text provided. Pass text as args or pipe via stdin.")


def _serialize_value(value):
    if isinstance(value, AbsoluteValue):
        return {
            "datetime": value.datetime_value.isoformat(),
            "timezone_source": value.timezone_source,
        }
    if isinstance(value, RelativeValue):
        return {
            "resolved_datetime": value.resolved_datetime.isoformat(),
            "delta_seconds": value.delta_seconds,
            "anchor": value.anchor,
        }
    if isinstance(value, DurationValue):
        return {
            "total_seconds": value.total_seconds,
            "components": dict(value.components),
        }
    if isinstance(value, IntervalValue):
        return {
            "start": value.start.isoformat(),
            "end": value.end.isoformat(),
            "closed_open": value.closed_open,
        }
    return str(value)


def _serialize_extract(matches: Iterable[Match]) -> List[dict]:
    rows = []
    for match in matches:
        rows.append(
            {
                "kind": match.kind,
                "text": match.text,
                "start": match.start,
                "end": match.end,
                "locale": match.locale,
                "grain": match.grain,
                "value": _serialize_value(match.value),
                "alternates": [_serialize_value(v) for v in match.alternates],
                "confidence": match.confidence,
                "warnings": list(match.warnings),
            }
        )
    return rows


def _unpack_find_dates_item(item, source: bool, index: bool) -> Tuple[datetime, Optional[str], Optional[Tuple[int, int]]]:
    if not source and not index:
        return item, None, None
    if source and index:
        return item[0], item[1], item[2]
    if source:
        return item[0], item[1], None
    return item[0], None, item[1]


def _serialize_find_dates(rows, source: bool, index: bool) -> List[dict]:
    out = []
    for item in rows:
        dt, text, loc = _unpack_find_dates_item(item, source=source, index=index)
        record = {"datetime": dt.isoformat()}
        if text is not None:
            record["text"] = text
        if loc is not None:
            record["index"] = [loc[0], loc[1]]
        out.append(record)
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract dates from natural language text.")
    parser.add_argument("text", nargs="*", help="Input text. If omitted, read from stdin.")
    parser.add_argument(
        "--engine",
        choices=("default", "legacy", "compat", "extract"),
        default="default",
        help="Extraction engine. default uses datefinder.find_dates(...).",
    )
    parser.add_argument(
        "--reference",
        help="ISO8601 reference datetime (for relative expressions).",
    )
    parser.add_argument(
        "--first",
        choices=("month", "day", "year"),
        default="month",
        help="Disambiguation strategy for numeric dates.",
    )
    parser.add_argument(
        "--no-month-only",
        action="store_true",
        help="Disable month-only parsing (e.g. 'July' -> YYYY-07-01).",
    )
    parser.add_argument(
        "--compact-numeric",
        action="store_true",
        help="Enable opt-in compact numeric parsing (e.g. 08082018).",
    )
    parser.add_argument(
        "--no-multiline",
        action="store_true",
        help="Disable cross-line matching; parse each line independently.",
    )
    parser.add_argument("--strict", action="store_true", help="Enable strict date matching.")
    parser.add_argument("--source", action="store_true", help="Include source substring (default/legacy only).")
    parser.add_argument("--index", action="store_true", help="Include match indices (default/legacy only).")
    parser.add_argument("--locale", action="append", default=[], help="Locale for extract engine (repeatable).")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    parser.add_argument("--version", action="version", version=f"datefinder {__version__}")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.engine in {"compat", "extract"} and (args.source or args.index):
        parser.error("--source/--index are only supported for default or legacy engines.")
    if args.engine != "extract" and args.locale:
        parser.error("--locale is only supported with --engine extract.")

    text = _get_text(args.text)
    reference = _parse_reference(args.reference)

    if args.engine == "legacy":
        rows = list(
            find_dates_legacy(
                text,
                source=args.source,
                index=args.index,
                strict=args.strict,
                base_date=reference,
                first=args.first,
            )
        )
        if args.json:
            payload = _serialize_find_dates(rows, source=args.source, index=args.index)
            json.dump(payload, sys.stdout, indent=2 if args.pretty else None)
            sys.stdout.write("\n")
            return 0
        for item in rows:
            dt, src, loc = _unpack_find_dates_item(item, source=args.source, index=args.index)
            line = dt.isoformat()
            if src is not None:
                line += f"\t{src}"
            if loc is not None:
                line += f"\t{loc[0]}:{loc[1]}"
            print(line)
        return 0

    if args.engine == "compat":
        rows = list(
            find_dates_compat(
                text,
                reference_dt=reference,
                strict=args.strict,
                first=args.first,
                allow_month_only=not args.no_month_only,
                allow_compact_numeric=args.compact_numeric,
                allow_multiline=not args.no_multiline,
            )
        )
        if args.json:
            json.dump([{"datetime": dt.isoformat()} for dt in rows], sys.stdout, indent=2 if args.pretty else None)
            sys.stdout.write("\n")
            return 0
        for dt in rows:
            print(dt.isoformat())
        return 0

    if args.engine == "extract":
        matches = list(
            extract(
                text,
                reference_dt=reference,
                locales=tuple(args.locale) if args.locale else None,
                strict=args.strict,
                first=args.first,
                allow_month_only=not args.no_month_only,
                allow_compact_numeric=args.compact_numeric,
                allow_multiline=not args.no_multiline,
                stream=False,
            )
        )
        if args.json:
            json.dump(_serialize_extract(matches), sys.stdout, indent=2 if args.pretty else None)
            sys.stdout.write("\n")
            return 0
        for match in matches:
            print(f"{match.kind}\t{match.text}\t{_serialize_value(match.value)}")
        return 0

    rows = list(
        find_dates(
            text,
            source=args.source,
            index=args.index,
            strict=args.strict,
            base_date=reference,
            first=args.first,
            allow_month_only=not args.no_month_only,
            allow_compact_numeric=args.compact_numeric,
            allow_multiline=not args.no_multiline,
        )
    )
    if args.json:
        payload = _serialize_find_dates(rows, source=args.source, index=args.index)
        json.dump(payload, sys.stdout, indent=2 if args.pretty else None)
        sys.stdout.write("\n")
        return 0
    for item in rows:
        dt, src, loc = _unpack_find_dates_item(item, source=args.source, index=args.index)
        line = dt.isoformat()
        if src is not None:
            line += f"\t{src}"
        if loc is not None:
            line += f"\t{loc[0]}:{loc[1]}"
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
