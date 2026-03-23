from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Iterable, Iterator, List, Literal, Optional, Sequence, Tuple, Union
import re

try:
    from . import _kernel  # type: ignore
except Exception:
    _kernel = None


MatchKind = Literal["absolute", "relative", "duration", "interval"]
Grain = Literal["second", "minute", "hour", "day", "week", "month", "year"]


@dataclass(frozen=True)
class AbsoluteValue:
    datetime_value: datetime
    timezone_source: Optional[str] = None


@dataclass(frozen=True)
class RelativeValue:
    resolved_datetime: datetime
    delta_seconds: int
    anchor: str = "reference"


@dataclass(frozen=True)
class DurationValue:
    total_seconds: int
    components: Dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class IntervalValue:
    start: datetime
    end: datetime
    closed_open: str = "[)"


Value = Union[AbsoluteValue, RelativeValue, DurationValue, IntervalValue]


@dataclass(frozen=True)
class Match:
    kind: MatchKind
    text: str
    start: int
    end: int
    locale: str
    grain: Grain
    value: Value
    alternates: Tuple[Value, ...] = ()
    confidence: float = 1.0
    warnings: Tuple[str, ...] = ()


_MONTH_ALIASES = {
    # english
    "january": 1,
    "jan": 1,
    "february": 2,
    "feb": 2,
    "march": 3,
    "mar": 3,
    "april": 4,
    "apr": 4,
    "may": 5,
    "june": 6,
    "jun": 6,
    "july": 7,
    "jul": 7,
    "august": 8,
    "aug": 8,
    "september": 9,
    "sep": 9,
    "sept": 9,
    "october": 10,
    "oct": 10,
    "november": 11,
    "nov": 11,
    "december": 12,
    "dec": 12,
    # spanish
    "enero": 1,
    "febrero": 2,
    "marzo": 3,
    "abril": 4,
    "mayo": 5,
    "junio": 6,
    "julio": 7,
    "agosto": 8,
    "septiembre": 9,
    "setiembre": 9,
    "octubre": 10,
    "noviembre": 11,
    "diciembre": 12,
    # french
    "janvier": 1,
    "fevrier": 2,
    "février": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "aout": 8,
    "août": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "decembre": 12,
    "décembre": 12,
    # german
    "januar": 1,
    "februar": 2,
    "maerz": 3,
    "märz": 3,
    "april": 4,
    "mai": 5,
    "juni": 6,
    "juli": 7,
    "august": 8,
    "september": 9,
    "oktober": 10,
    "november": 11,
    "dezember": 12,
    # portuguese
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
    # italian
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}
_MONTH_PATTERN = "|".join(sorted(map(re.escape, _MONTH_ALIASES.keys()), key=len, reverse=True))

_ISO_RE = re.compile(
    r"\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"
    r"(?:[T\s](?P<h>\d{2}):(?P<min>\d{2})"
    r"(?::(?P<s>\d{2})(?:[\,\.](?P<us>\d{1,6}))?)?"
    r"(?P<tz>Z|[+\-]\d{2}:?\d{2})?)?\b",
    re.IGNORECASE,
)
_SLASH_RE = re.compile(r"\b(?P<a>\d{1,2})/(?P<b>\d{1,2})/(?P<c>\d{2,4})\b")
_HYPHEN_RE = re.compile(r"\b(?P<a>\d{1,2})-(?P<b>\d{1,2})-(?P<c>\d{2,4})\b")
_DOT_RE = re.compile(r"\b(?P<a>\d{1,4})\.(?P<b>\d{1,2})\.(?P<c>\d{1,4})\b")
_MONTH_FIRST_RE = re.compile(
    rf"\b(?P<month>{_MONTH_PATTERN})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+(?P<year>\d{{4}})\b",
    re.IGNORECASE,
)
_MONTH_FIRST_HYPHEN_RE = re.compile(
    rf"\b(?P<month>{_MONTH_PATTERN})-(?P<day>\d{{1,2}})(?:st|nd|rd|th)?-(?P<year>\d{{4}})\b",
    re.IGNORECASE,
)
_DAY_FIRST_RE = re.compile(
    rf"\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:\s+day\s+of|\s+de)?\s+(?P<month>{_MONTH_PATTERN})\.?(?:\s+de)?(?:,)?\s+(?P<year>\d{{4}})\b",
    re.IGNORECASE,
)
_YEAR_ONLY_RE = re.compile(r"\b(?:in|during|on)\s+(?P<year>19\d\d|20\d\d)\b", re.IGNORECASE)
_TIME_RE = re.compile(
    r"\b(?P<h>\d{1,2})\:(?P<min>\d{2})(?:\:(?P<s>\d{2}))?"
    r"(?:[\.,](?P<us>\d{1,6}))?\s*(?P<ampm>a\.?m\.?|p\.?m\.?)?"
    r"(?:\s*(?P<offset>Z|[+\-]\d{2}:?\d{2}))?\b",
    re.IGNORECASE,
)

_RELATIVE_WORDS = {
    "today": 0,
    "hoy": 0,
    "aujourd'hui": 0,
    "aujourdhui": 0,
    "heute": 0,
    "hoje": 0,
    "oggi": 0,
    "yesterday": -1,
    "ayer": -1,
    "hier": -1,
    "gestern": -1,
    "ontem": -1,
    "ieri": -1,
    "tomorrow": 1,
    "mañana": 1,
    "manana": 1,
    "demain": 1,
    "morgen": 1,
    "amanhã": 1,
    "amanha": 1,
    "domani": 1,
}
_RELATIVE_WORD_RE = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, _RELATIVE_WORDS.keys()), key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)

_UNITS = {
    "second": 1,
    "seconds": 1,
    "sec": 1,
    "minute": 60,
    "minutes": 60,
    "hour": 3600,
    "hours": 3600,
    "day": 86400,
    "days": 86400,
    "week": 7 * 86400,
    "weeks": 7 * 86400,
    "month": 30 * 86400,
    "months": 30 * 86400,
    "year": 365 * 86400,
    "years": 365 * 86400,
    # es
    "segundo": 1,
    "segundos": 1,
    "minuto": 60,
    "minutos": 60,
    "hora": 3600,
    "horas": 3600,
    "dia": 86400,
    "dias": 86400,
    "día": 86400,
    "días": 86400,
    "semana": 7 * 86400,
    "semanas": 7 * 86400,
    "mes": 30 * 86400,
    "meses": 30 * 86400,
    "año": 365 * 86400,
    "años": 365 * 86400,
    # fr
    "seconde": 1,
    "secondes": 1,
    "minute": 60,
    "minutes": 60,
    "heure": 3600,
    "heures": 3600,
    "jour": 86400,
    "jours": 86400,
    "semaine": 7 * 86400,
    "semaines": 7 * 86400,
    "mois": 30 * 86400,
    "an": 365 * 86400,
    "ans": 365 * 86400,
    "année": 365 * 86400,
    "années": 365 * 86400,
    # de
    "sekunde": 1,
    "sekunden": 1,
    "stunde": 3600,
    "stunden": 3600,
    "tag": 86400,
    "tage": 86400,
    "woche": 7 * 86400,
    "wochen": 7 * 86400,
    "monat": 30 * 86400,
    "monate": 30 * 86400,
    "jahr": 365 * 86400,
    "jahre": 365 * 86400,
    # pt
    "segundo": 1,
    "segundos": 1,
    "minuto": 60,
    "minutos": 60,
    "hora": 3600,
    "horas": 3600,
    "dia": 86400,
    "dias": 86400,
    "semana": 7 * 86400,
    "semanas": 7 * 86400,
    "mes": 30 * 86400,
    "meses": 30 * 86400,
    "ano": 365 * 86400,
    "anos": 365 * 86400,
    # it
    "secondo": 1,
    "secondi": 1,
    "minuto": 60,
    "minuti": 60,
    "ora": 3600,
    "ore": 3600,
    "giorno": 86400,
    "giorni": 86400,
    "settimana": 7 * 86400,
    "settimane": 7 * 86400,
    "mese": 30 * 86400,
    "mesi": 30 * 86400,
    "anno": 365 * 86400,
    "anni": 365 * 86400,
}
_UNIT_PATTERN = "|".join(sorted(map(re.escape, _UNITS.keys()), key=len, reverse=True))
_IN_PATTERN = re.compile(rf"\b(in)\s+(?P<num>\d+)\s+(?P<unit>{_UNIT_PATTERN})\b", re.IGNORECASE)
_AGO_PATTERN = re.compile(rf"\b(?P<num>\d+)\s+(?P<unit>{_UNIT_PATTERN})\s+(ago)\b", re.IGNORECASE)
_DURATION_PATTERN = re.compile(rf"\b(?P<num>\d+)\s*(?P<unit>{_UNIT_PATTERN})\b", re.IGNORECASE)


def _as_utc(dt: Optional[datetime]) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _coerce_year(year: int) -> int:
    if year < 100:
        return 2000 + year
    return year


def _resolve_slash_candidates(a: int, b: int, c: int, first: str) -> List[Tuple[int, int, int]]:
    preferred: List[Tuple[int, int, int]] = []
    if first == "day":
        preferred.append((_coerce_year(c), b, a))
    elif first == "year":
        preferred.append((_coerce_year(a), b, c))
    else:
        preferred.append((_coerce_year(c), a, b))

    # Fallback attempts prevent obvious misses like 31/08/2012 with month-first default.
    fallbacks = [
        (_coerce_year(c), b, a),  # DMY
        (_coerce_year(c), a, b),  # MDY
        (_coerce_year(a), b, c),  # YMD-ish 2-digit legacy
    ]
    for cand in fallbacks:
        if cand not in preferred:
            preferred.append(cand)
    return preferred


def _grain_from_time(has_time: bool, has_seconds: bool) -> Grain:
    if not has_time:
        return "day"
    if has_seconds:
        return "second"
    return "minute"


def _parse_offset(offset: Optional[str]):
    if not offset:
        return None
    raw = offset.upper()
    if raw == "Z":
        return timezone.utc
    clean = raw.replace(":", "")
    sign = 1 if clean[0] == "+" else -1
    hours = int(clean[1:3])
    minutes = int(clean[3:5])
    delta = timedelta(hours=hours, minutes=minutes) * sign
    return timezone(delta)


def _coerce_time(match: re.Match) -> Tuple[int, int, int, int, Optional[timezone]]:
    hour = int(match.group("h"))
    minute = int(match.group("min"))
    second = int(match.group("s")) if match.group("s") else 0
    micro = int((match.group("us") or "0").ljust(6, "0"))
    ampm = (match.group("ampm") or "").lower().replace(".", "")
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return hour, minute, second, micro, _parse_offset(match.group("offset"))


def _find_nearby_time(text: str, start: int, end: int) -> Optional[Tuple[int, int, int, int, Optional[timezone]]]:
    window_start = max(0, start - 20)
    window_end = min(len(text), end + 30)
    window = text[window_start:window_end]
    best = None
    best_distance = 10**9
    for mt in _TIME_RE.finditer(window):
        global_start = window_start + mt.start()
        global_end = window_start + mt.end()
        if global_end < start - 20 or global_start > end + 30:
            continue
        distance = min(abs(global_start - end), abs(start - global_end))
        if distance < best_distance:
            best_distance = distance
            best = _coerce_time(mt)
    return best


def _serialize_matches(matches: List[dict]) -> List[dict]:
    grain_score = {
        "year": 1,
        "month": 2,
        "week": 3,
        "day": 4,
        "hour": 5,
        "minute": 6,
        "second": 7,
    }

    def score(item: dict) -> float:
        base = float(item.get("confidence", 0.0))
        base += 0.05 * grain_score.get(item.get("grain", "day"), 0)
        value = item.get("value", {})
        if isinstance(value, dict):
            text_value = value.get("datetime", "")
            if isinstance(text_value, str) and "T" in text_value:
                base += 0.1
            if isinstance(text_value, str) and ("+" in text_value or text_value.endswith("Z")):
                base += 0.05
        return base

    best_by_key: Dict[Tuple[str, int, int, str], dict] = {}
    for item in sorted(matches, key=lambda x: (x["start"], x["end"], x["kind"])):
        key = (item["kind"], item["start"], item["end"], item["text"])
        existing = best_by_key.get(key)
        if existing is None or score(item) > score(existing):
            best_by_key[key] = item

    deduped = list(best_by_key.values())
    ranked = sorted(deduped, key=lambda x: (-score(x), -(x["end"] - x["start"]), x["start"]))
    kept: List[dict] = []

    def _value_sig(item: dict) -> str:
        value = item.get("value", {})
        if isinstance(value, dict):
            if "datetime" in value:
                return str(value["datetime"])
            if "resolved_datetime" in value:
                return str(value["resolved_datetime"])
            if "total_seconds" in value:
                return str(value["total_seconds"])
        return ""

    def _subsumed(item: dict, keeper: dict) -> bool:
        if item["kind"] != keeper["kind"]:
            return False
        overlaps = not (item["end"] <= keeper["start"] or item["start"] >= keeper["end"])
        if not overlaps:
            return False
        same_value = _value_sig(item) == _value_sig(keeper)
        if same_value:
            return True
        if item["kind"] == "absolute":
            return keeper["start"] <= item["start"] and keeper["end"] >= item["end"]
        return False

    for item in ranked:
        if any(_subsumed(item, k) for k in kept):
            continue
        kept.append(item)

    return sorted(kept, key=lambda x: (x["start"], x["end"], x["kind"]))


def _strict_keep(item: dict) -> bool:
    if item.get("kind") != "absolute":
        return False
    text = item.get("text", "")
    if _ISO_RE.search(text):
        return True
    if _SLASH_RE.search(text) or _HYPHEN_RE.search(text) or _DOT_RE.search(text):
        return True
    if _MONTH_FIRST_RE.search(text) or _MONTH_FIRST_HYPHEN_RE.search(text) or _DAY_FIRST_RE.search(text):
        return True
    return False


def _value_from_raw(raw_value: dict) -> Value:
    kind = raw_value.get("type")
    if kind == "absolute":
        dt = datetime.fromisoformat(raw_value["datetime"])
        return AbsoluteValue(datetime_value=dt, timezone_source=raw_value.get("timezone_source"))
    if kind == "relative":
        dt = datetime.fromisoformat(raw_value["resolved_datetime"])
        return RelativeValue(
            resolved_datetime=dt,
            delta_seconds=int(raw_value["delta_seconds"]),
            anchor=str(raw_value.get("anchor", "reference")),
        )
    if kind == "duration":
        return DurationValue(
            total_seconds=int(raw_value["total_seconds"]),
            components=dict(raw_value.get("components", {})),
        )
    if kind == "interval":
        start = datetime.fromisoformat(raw_value["start"])
        end = datetime.fromisoformat(raw_value["end"])
        return IntervalValue(start=start, end=end, closed_open=str(raw_value.get("closed_open", "[)")))
    raise ValueError("unknown value type: {}".format(kind))


def _matches_from_raw(raw_matches: Iterable[dict]) -> Iterator[Match]:
    for item in raw_matches:
        value = _value_from_raw(item["value"])
        alternates = tuple(_value_from_raw(v) for v in item.get("alternates", []))
        warnings = tuple(item.get("warnings", []))
        yield Match(
            kind=item["kind"],
            text=item["text"],
            start=int(item["start"]),
            end=int(item["end"]),
            locale=item.get("locale", "und"),
            grain=item.get("grain", "day"),
            value=value,
            alternates=alternates,
            confidence=float(item.get("confidence", 1.0)),
            warnings=warnings,
        )


def _extract_raw(
    text: str,
    reference_dt: datetime,
    locales: Sequence[str],
    strict: bool,
    first: str,
    two_digit_year_pivot: Optional[int],
    allow_month_only: bool,
    allow_compact_numeric: bool,
    allow_multiline: bool,
) -> List[dict]:
    if _kernel is None:
        raise RuntimeError(
            "datefinder Rust kernel is unavailable. Install a compatible wheel or build from source "
            "with Rust toolchain support."
        )
    def _kernel_extract(chunk: str) -> List[dict]:
        return _kernel.extract(
            text=chunk,
            reference_dt=reference_dt.isoformat(),
            locales=list(locales),
            strict=bool(strict),
            first=first,
            two_digit_year_pivot=two_digit_year_pivot,
            allow_month_only=allow_month_only,
            allow_compact_numeric=allow_compact_numeric,
        )

    if allow_multiline:
        kernel_raw = _kernel_extract(text)
    else:
        kernel_raw = []
        offset = 0
        for line in text.splitlines(keepends=True):
            content = line.rstrip("\r\n")
            if content:
                line_raw = _kernel_extract(content)
                for item in line_raw:
                    item["start"] = int(item["start"]) + offset
                    item["end"] = int(item["end"]) + offset
                kernel_raw.extend(line_raw)
            offset += len(line)

    merged = _serialize_matches(kernel_raw)
    if strict:
        merged = [item for item in merged if _strict_keep(item)]
    return merged


def extract(
    text: str,
    *,
    reference_dt: Optional[datetime] = None,
    locales: Optional[Sequence[str]] = None,
    timezone_name: Optional[str] = None,
    strict: bool = False,
    first: Literal["month", "day", "year"] = "month",
    two_digit_year_pivot: Optional[int] = None,
    allow_month_only: bool = True,
    allow_compact_numeric: bool = False,
    allow_multiline: bool = True,
    stream: bool = False,
) -> Union[List[Match], Iterator[Match]]:
    del timezone_name  # reserved for timezone database integration
    ref = _as_utc(reference_dt)
    requested_locales = tuple(locales or ("en", "es", "fr", "de", "pt", "it"))
    raw = _extract_raw(
        text,
        ref,
        requested_locales,
        strict,
        first,
        two_digit_year_pivot,
        allow_month_only,
        allow_compact_numeric,
        allow_multiline,
    )
    iterator = _matches_from_raw(raw)
    if stream:
        return iterator
    return list(iterator)


def find_dates_compat(
    text: str,
    *,
    reference_dt: Optional[datetime] = None,
    strict: bool = False,
    first: Literal["month", "day", "year"] = "month",
    two_digit_year_pivot: Optional[int] = None,
    allow_month_only: bool = True,
    allow_compact_numeric: bool = False,
    allow_multiline: bool = True,
) -> Iterator[datetime]:
    matches = extract(
        text,
        reference_dt=reference_dt,
        strict=strict,
        first=first,
        two_digit_year_pivot=two_digit_year_pivot,
        allow_month_only=allow_month_only,
        allow_compact_numeric=allow_compact_numeric,
        allow_multiline=allow_multiline,
        stream=True,
    )
    for match in matches:
        if match.kind == "absolute":
            assert isinstance(match.value, AbsoluteValue)
            yield match.value.datetime_value
        elif match.kind == "relative":
            assert isinstance(match.value, RelativeValue)
            yield match.value.resolved_datetime
        elif match.kind == "interval":
            assert isinstance(match.value, IntervalValue)
            yield match.value.start
