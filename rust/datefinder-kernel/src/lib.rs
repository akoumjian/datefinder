use aho_corasick::AhoCorasick;
use chrono::{
    DateTime, Datelike, Duration, FixedOffset, NaiveDate, NaiveDateTime, NaiveTime, TimeZone,
    Timelike, Utc,
};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use regex::Regex;
use std::cmp::Ordering;
use std::collections::HashMap;
use std::sync::OnceLock;

#[derive(Clone, Debug)]
enum RawValue {
    Absolute {
        datetime: String,
        timezone_source: Option<String>,
    },
    Relative {
        resolved_datetime: String,
        delta_seconds: i64,
        anchor: String,
    },
    Duration {
        total_seconds: i64,
        components: HashMap<String, i64>,
    },
}

#[derive(Clone, Debug)]
struct RawMatch {
    kind: &'static str,
    text: String,
    start: usize,
    end: usize,
    locale: String,
    grain: &'static str,
    value: RawValue,
    confidence: f64,
    warnings: Vec<String>,
}

fn iso_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(
            r"(?i)\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})(?:[T\s](?P<h>\d{2}):(?P<min>\d{2})(?::(?P<s>\d{2})(?:[\,\.](?P<us>\d{1,6}))?)?(?P<tz>Z|[+\-]\d{2}:?\d{2})?)?\b",
        )
        .expect("valid regex")
    })
}

fn slash_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?P<a>\d{1,4})/(?P<b>\d{1,2})/(?P<c>\d{1,4})").expect("valid regex")
    })
}

fn hyphen_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?P<a>\d{1,4})-(?P<b>\d{1,2})-(?P<c>\d{1,4})").expect("valid regex")
    })
}

fn dot_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?P<a>\d{1,4})\.(?P<b>\d{1,2})\.(?P<c>\d{1,4})").expect("valid regex")
    })
}

fn year_only_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\b(?:in|during|on)\s+(?P<year>19\d\d|20\d\d)\b").expect("valid regex")
    })
}

fn relative_word_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(
            r"(?i)\b(today|hoy|aujourd'hui|aujourdhui|heute|hoje|oggi|yesterday|ayer|hier|gestern|ontem|ieri|tomorrow|mañana|manana|demain|morgen|amanhã|amanha|domani)\b",
        )
        .expect("valid regex")
    })
}

fn relative_weekday_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\b(?P<dir>next|last)\s+(?P<weekday>monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b")
            .expect("valid regex")
    })
}

fn in_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\bin\s+(?P<num>\d+)\s+(?P<unit>[a-zà-ÿ]+)\b").expect("valid regex")
    })
}

fn ago_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\b(?P<num>\d+)\s+(?P<unit>[a-zà-ÿ]+)\s+ago\b").expect("valid regex")
    })
}

fn duration_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?i)\b(?P<num>\d+)\s*(?P<unit>[a-zà-ÿ]+)\b").expect("valid regex")
    })
}

fn month_aliases() -> &'static [(&'static str, u32)] {
    &[
        ("january", 1),
        ("jan", 1),
        ("february", 2),
        ("feb", 2),
        ("march", 3),
        ("mar", 3),
        ("april", 4),
        ("apr", 4),
        ("may", 5),
        ("june", 6),
        ("jun", 6),
        ("july", 7),
        ("jul", 7),
        ("august", 8),
        ("aug", 8),
        ("september", 9),
        ("septiembre", 9),
        ("sept", 9),
        ("sep", 9),
        ("october", 10),
        ("octubre", 10),
        ("oct", 10),
        ("november", 11),
        ("noviembre", 11),
        ("nov", 11),
        ("december", 12),
        ("diciembre", 12),
        ("dec", 12),
        ("enero", 1),
        ("febrero", 2),
        ("marzo", 3),
        ("abril", 4),
        ("mayo", 5),
        ("junio", 6),
        ("julio", 7),
        ("agosto", 8),
        ("setiembre", 9),
        ("janvier", 1),
        ("février", 2),
        ("fevrier", 2),
        ("mars", 3),
        ("avril", 4),
        ("mai", 5),
        ("juin", 6),
        ("juillet", 7),
        ("août", 8),
        ("aout", 8),
        ("septembre", 9),
        ("octobre", 10),
        ("novembre", 11),
        ("décembre", 12),
        ("decembre", 12),
        ("januar", 1),
        ("februar", 2),
        ("märz", 3),
        ("maerz", 3),
        ("mai", 5),
        ("juni", 6),
        ("juli", 7),
        ("oktober", 10),
        ("dezember", 12),
        ("janeiro", 1),
        ("fevereiro", 2),
        ("março", 3),
        ("marco", 3),
        ("junho", 6),
        ("julho", 7),
        ("setembro", 9),
        ("outubro", 10),
        ("novembro", 11),
        ("dezembro", 12),
        ("gennaio", 1),
        ("febbraio", 2),
        ("aprile", 4),
        ("maggio", 5),
        ("giugno", 6),
        ("luglio", 7),
        ("settembre", 9),
        ("ottobre", 10),
        ("dicembre", 12),
    ]
}

fn month_automaton() -> &'static AhoCorasick {
    static AC: OnceLock<AhoCorasick> = OnceLock::new();
    AC.get_or_init(|| {
        let patterns: Vec<&str> = month_aliases().iter().map(|(alias, _)| *alias).collect();
        AhoCorasick::new(patterns).expect("valid month automaton")
    })
}

fn month_lookup() -> &'static HashMap<&'static str, u32> {
    static MAP: OnceLock<HashMap<&'static str, u32>> = OnceLock::new();
    MAP.get_or_init(|| month_aliases().iter().copied().collect())
}

fn month_first_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        let mut aliases: Vec<&str> = month_aliases().iter().map(|(m, _)| *m).collect();
        aliases.sort_by_key(|m| std::cmp::Reverse(m.len()));
        aliases.dedup();
        let escaped = aliases
            .into_iter()
            .map(regex::escape)
            .collect::<Vec<String>>()
            .join("|");
        let pattern = format!(
            r"(?i)\b(?P<month>{})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+(?P<year>\d{{4}})\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn day_first_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        let mut aliases: Vec<&str> = month_aliases().iter().map(|(m, _)| *m).collect();
        aliases.sort_by_key(|m| std::cmp::Reverse(m.len()));
        aliases.dedup();
        let escaped = aliases
            .into_iter()
            .map(regex::escape)
            .collect::<Vec<String>>()
            .join("|");
        let pattern = format!(
            r"(?i)\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:\s+day\s+of|\s+de|\s+of)?\s+(?P<month>{})\.?(?:,)?\s+(?P<year>\d{{4}})\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn year_day_month_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        let mut aliases: Vec<&str> = month_aliases().iter().map(|(m, _)| *m).collect();
        aliases.sort_by_key(|m| std::cmp::Reverse(m.len()));
        aliases.dedup();
        let escaped = aliases
            .into_iter()
            .map(regex::escape)
            .collect::<Vec<String>>()
            .join("|");
        let pattern = format!(
            r"(?i)(?P<year>\d{{4}})\s*[,/\-]\s*(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s*[,/\-]\s*(?P<month>{})\.?",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn weekday_month_day_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        let mut aliases: Vec<&str> = month_aliases().iter().map(|(m, _)| *m).collect();
        aliases.sort_by_key(|m| std::cmp::Reverse(m.len()));
        aliases.dedup();
        let escaped = aliases
            .into_iter()
            .map(regex::escape)
            .collect::<Vec<String>>()
            .join("|");
        let pattern = format!(
            r"(?i)\b(?P<weekday>monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s*,?\s*(?P<month>{})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn time_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(
            r"(?i)\b(?P<h>\d{1,2})\:(?P<min>\d{2})(?:\:(?P<s>\d{2}))?(?:[\,\.](?P<us>\d{1,6}))?\s*(?P<ampm>a\.?m\.?|p\.?m\.?)?(?:\s*(?P<offset>Z|[+\-]\d{2}:?\d{2}))?\b",
        )
        .expect("valid regex")
    })
}

fn relative_word_days(token: &str) -> Option<i64> {
    match token.to_lowercase().as_str() {
        "today" | "hoy" | "aujourd'hui" | "aujourdhui" | "heute" | "hoje" | "oggi" => Some(0),
        "yesterday" | "ayer" | "hier" | "gestern" | "ontem" | "ieri" => Some(-1),
        "tomorrow" | "mañana" | "manana" | "demain" | "morgen" | "amanhã" | "amanha" | "domani" => {
            Some(1)
        }
        _ => None,
    }
}

fn unit_seconds(unit: &str) -> Option<i64> {
    match unit.to_lowercase().as_str() {
        "second" | "seconds" | "sec" | "segundo" | "segundos" | "seconde" | "secondes"
        | "sekunde" | "sekunden" | "secondo" | "secondi" => Some(1),
        "minute" | "minutes" | "minuto" | "minutos" | "minuti" => Some(60),
        "hour" | "hours" | "hora" | "horas" | "heure" | "heures" | "stunde" | "stunden" | "ora"
        | "ore" => Some(3600),
        "day" | "days" | "dia" | "dias" | "día" | "días" | "jour" | "jours" | "tag" | "tage"
        | "giorno" | "giorni" => Some(86_400),
        "week" | "weeks" | "semana" | "semanas" | "semaine" | "semaines" | "woche" | "wochen"
        | "settimana" | "settimane" => Some(604_800),
        "month" | "months" | "mes" | "meses" | "mois" | "monat" | "monate" | "mese" | "mesi" => {
            Some(2_592_000)
        }
        "year" | "years" | "año" | "años" | "an" | "ans" | "année" | "années" | "jahr"
        | "jahre" | "ano" | "anos" | "anno" | "anni" => Some(31_536_000),
        _ => None,
    }
}

fn parse_reference(reference_dt: Option<&str>) -> DateTime<FixedOffset> {
    if let Some(raw) = reference_dt {
        if let Ok(dt) = DateTime::parse_from_rfc3339(raw) {
            return dt;
        }
    }
    Utc::now().fixed_offset()
}

fn coerce_year(year: i32) -> i32 {
    if year < 100 {
        if year <= 68 {
            2000 + year
        } else {
            1900 + year
        }
    } else {
        year
    }
}

fn parse_slash_candidates(a: i32, b: i32, c: i32, first: &str) -> Vec<(i32, u32, u32)> {
    let mut out = Vec::new();
    let preferred = match first {
        "day" => (coerce_year(c), b as u32, a as u32),
        "year" => (coerce_year(a), b as u32, c as u32),
        _ => (coerce_year(c), a as u32, b as u32),
    };
    out.push(preferred);
    for fallback in [
        (coerce_year(c), b as u32, a as u32), // DMY
        (coerce_year(c), a as u32, b as u32), // MDY
        (coerce_year(a), b as u32, c as u32), // YMD-ish legacy
    ] {
        if !out.contains(&fallback) {
            out.push(fallback);
        }
    }
    out
}

fn absolute_grain(has_time: bool, has_seconds: bool) -> &'static str {
    if !has_time {
        return "day";
    }
    if has_seconds {
        "second"
    } else {
        "minute"
    }
}

fn parse_tz_offset(offset: &str) -> Option<FixedOffset> {
    let raw = offset.trim().to_uppercase();
    if raw == "Z" {
        return FixedOffset::east_opt(0);
    }
    let clean = raw.replace(':', "");
    if clean.len() != 5 {
        return None;
    }
    let sign = match &clean[0..1] {
        "+" => 1,
        "-" => -1,
        _ => return None,
    };
    let hours: i32 = clean[1..3].parse().ok()?;
    let minutes: i32 = clean[3..5].parse().ok()?;
    FixedOffset::east_opt(sign * (hours * 3600 + minutes * 60))
}

fn normalize_microseconds(raw: &str) -> u32 {
    let mut s = raw.to_string();
    if s.len() < 6 {
        s.push_str(&"0".repeat(6 - s.len()));
    } else if s.len() > 6 {
        s.truncate(6);
    }
    s.parse().unwrap_or(0)
}

fn parse_time_capture(
    caps: &regex::Captures<'_>,
) -> Option<(u32, u32, u32, u32, Option<FixedOffset>)> {
    let mut hour: u32 = caps.name("h")?.as_str().parse().ok()?;
    let minute: u32 = caps.name("min")?.as_str().parse().ok()?;
    let second: u32 = caps
        .name("s")
        .and_then(|m| m.as_str().parse().ok())
        .unwrap_or(0);
    let micro: u32 = caps
        .name("us")
        .map(|m| normalize_microseconds(m.as_str()))
        .unwrap_or(0);
    let ampm = caps
        .name("ampm")
        .map(|m| m.as_str().to_ascii_lowercase().replace('.', ""))
        .unwrap_or_default();
    if ampm == "pm" && hour < 12 {
        hour += 12;
    } else if ampm == "am" && hour == 12 {
        hour = 0;
    }
    let offset = caps
        .name("offset")
        .and_then(|m| parse_tz_offset(m.as_str()));
    Some((hour, minute, second, micro, offset))
}

fn is_digit_bounded(text: &str, start: usize, end: usize) -> bool {
    let prev_is_digit = text[..start]
        .chars()
        .next_back()
        .map(|c| c.is_ascii_digit())
        .unwrap_or(false);
    let next_is_digit = text[end..]
        .chars()
        .next()
        .map(|c| c.is_ascii_digit())
        .unwrap_or(false);
    !prev_is_digit && !next_is_digit
}

fn weekday_index(token: &str) -> Option<u32> {
    match token.to_lowercase().as_str() {
        "monday" => Some(0),
        "tuesday" => Some(1),
        "wednesday" => Some(2),
        "thursday" => Some(3),
        "friday" => Some(4),
        "saturday" => Some(5),
        "sunday" => Some(6),
        _ => None,
    }
}

fn find_nearby_time(
    text: &str,
    start: usize,
    end: usize,
) -> Option<(u32, u32, u32, u32, Option<FixedOffset>)> {
    let window_start = start.saturating_sub(20);
    let window_end = (end + 30).min(text.len());
    let window = &text[window_start..window_end];
    let mut best: Option<(u32, u32, u32, u32, Option<FixedOffset>)> = None;
    let mut best_distance = usize::MAX;
    for caps in time_re().captures_iter(window) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        let global_start = window_start + all.start();
        let global_end = window_start + all.end();
        let distance = global_start.abs_diff(end).min(start.abs_diff(global_end));
        if distance < best_distance {
            if let Some(parsed) = parse_time_capture(&caps) {
                best_distance = distance;
                best = Some(parsed);
            }
        }
    }
    best
}

fn build_datetime(
    offset: FixedOffset,
    y: i32,
    m: u32,
    d: u32,
    h: u32,
    min: u32,
    s: u32,
    micro: u32,
) -> Option<DateTime<FixedOffset>> {
    let date = NaiveDate::from_ymd_opt(y, m, d)?;
    let time = NaiveTime::from_hms_micro_opt(h, min, s, micro)?;
    let ndt = NaiveDateTime::new(date, time);
    offset.from_local_datetime(&ndt).single()
}

fn parse_raw(
    text: &str,
    reference: DateTime<FixedOffset>,
    first: &str,
    strict: bool,
) -> Vec<RawMatch> {
    let mut out: Vec<RawMatch> = Vec::new();
    let reference_offset = *reference.offset();

    for caps in iso_re().captures_iter(text) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        let year: i32 = caps["y"].parse().unwrap_or_default();
        let month: u32 = caps["m"].parse().unwrap_or_default();
        let day: u32 = caps["d"].parse().unwrap_or_default();
        let hour: u32 = caps
            .name("h")
            .map(|x| x.as_str().parse().unwrap_or(0))
            .unwrap_or(0);
        let minute: u32 = caps
            .name("min")
            .map(|x| x.as_str().parse().unwrap_or(0))
            .unwrap_or(0);
        let second: u32 = caps
            .name("s")
            .map(|x| x.as_str().parse().unwrap_or(0))
            .unwrap_or(0);
        let micro: u32 = caps
            .name("us")
            .map(|x| normalize_microseconds(x.as_str()))
            .unwrap_or(0);
        let offset = caps
            .name("tz")
            .and_then(|x| parse_tz_offset(x.as_str()))
            .unwrap_or(reference_offset);
        let Some(dt) = build_datetime(offset, year, month, day, hour, minute, second, micro) else {
            continue;
        };
        out.push(RawMatch {
            kind: "absolute",
            text: all.as_str().to_string(),
            start: all.start(),
            end: all.end(),
            locale: "und".to_string(),
            grain: absolute_grain(caps.name("h").is_some(), caps.name("s").is_some()),
            value: RawValue::Absolute {
                datetime: dt.to_rfc3339(),
                timezone_source: caps.name("tz").map(|_| "explicit".to_string()),
            },
            confidence: 0.99,
            warnings: vec![],
        });
    }

    for re in [slash_re(), hyphen_re(), dot_re()] {
        for caps in re.captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            if !is_digit_bounded(text, all.start(), all.end()) {
                continue;
            }
            let a: i32 = caps["a"].parse().unwrap_or_default();
            let b: i32 = caps["b"].parse().unwrap_or_default();
            let c: i32 = caps["c"].parse().unwrap_or_default();
            let mut dt = None;
            for (y, m, d) in parse_slash_candidates(a, b, c, first) {
                dt = build_datetime(reference_offset, y, m, d, 0, 0, 0, 0);
                if dt.is_some() {
                    break;
                }
            }
            let Some(mut dt) = dt else {
                continue;
            };

            if let Some((h, mi, s, us, offset)) = find_nearby_time(text, all.start(), all.end()) {
                let tz = offset.unwrap_or(reference_offset);
                if let Some(with_time) =
                    build_datetime(tz, dt.year(), dt.month(), dt.day(), h, mi, s, us)
                {
                    dt = with_time;
                }
            }

            out.push(RawMatch {
                kind: "absolute",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: if dt.time().second() > 0 {
                    "second"
                } else if dt.time().hour() > 0 || dt.time().minute() > 0 {
                    "minute"
                } else {
                    "day"
                },
                value: RawValue::Absolute {
                    datetime: dt.to_rfc3339(),
                    timezone_source: None,
                },
                confidence: 0.95,
                warnings: vec![],
            });
        }
    }

    // Month-name based dates with automata-backed lexicon prebuilt.
    let _ = month_automaton();
    for re in [month_first_re(), day_first_re()] {
        for caps in re.captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            let month_token = match caps.name("month") {
                Some(m) => m.as_str().to_lowercase().trim_end_matches('.').to_string(),
                None => continue,
            };
            let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
                continue;
            };
            let day: u32 = caps["day"].parse().unwrap_or_default();
            let year: i32 = caps["year"].parse().unwrap_or_default();
            let mut dt = match build_datetime(reference_offset, year, month, day, 0, 0, 0, 0) {
                Some(x) => x,
                None => continue,
            };
            if let Some((h, mi, s, us, offset)) = find_nearby_time(text, all.start(), all.end()) {
                let tz = offset.unwrap_or(reference_offset);
                if let Some(with_time) = build_datetime(tz, year, month, day, h, mi, s, us) {
                    dt = with_time;
                }
            }
            out.push(RawMatch {
                kind: "absolute",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: if dt.time().second() > 0 {
                    "second"
                } else if dt.time().hour() > 0 || dt.time().minute() > 0 {
                    "minute"
                } else {
                    "day"
                },
                value: RawValue::Absolute {
                    datetime: dt.to_rfc3339(),
                    timezone_source: None,
                },
                confidence: 0.96,
                warnings: vec![],
            });
        }
    }

    // Year-day-month name variants like "2020,31,August".
    for caps in year_day_month_re().captures_iter(text) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        if !is_digit_bounded(text, all.start(), all.end()) {
            continue;
        }
        let month_token = match caps.name("month") {
            Some(m) => m.as_str().to_lowercase().trim_end_matches('.').to_string(),
            None => continue,
        };
        let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
            continue;
        };
        let day: u32 = caps["day"].parse().unwrap_or_default();
        let year: i32 = caps["year"].parse().unwrap_or_default();
        let mut dt = match build_datetime(reference_offset, year, month, day, 0, 0, 0, 0) {
            Some(x) => x,
            None => continue,
        };
        if let Some((h, mi, s, us, offset)) = find_nearby_time(text, all.start(), all.end()) {
            let tz = offset.unwrap_or(reference_offset);
            if let Some(with_time) = build_datetime(tz, year, month, day, h, mi, s, us) {
                dt = with_time;
            }
        }
        out.push(RawMatch {
            kind: "absolute",
            text: all.as_str().to_string(),
            start: all.start(),
            end: all.end(),
            locale: "und".to_string(),
            grain: if dt.time().second() > 0 {
                "second"
            } else if dt.time().hour() > 0 || dt.time().minute() > 0 {
                "minute"
            } else {
                "day"
            },
            value: RawValue::Absolute {
                datetime: dt.to_rfc3339(),
                timezone_source: None,
            },
            confidence: 0.94,
            warnings: vec![],
        });
    }

    // Weekday + month/day without year, infer reference year.
    for caps in weekday_month_day_re().captures_iter(text) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        let month_token = match caps.name("month") {
            Some(m) => m.as_str().to_lowercase().trim_end_matches('.').to_string(),
            None => continue,
        };
        let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
            continue;
        };
        let day: u32 = caps["day"].parse().unwrap_or_default();
        let year: i32 = reference.year();
        let mut dt = match build_datetime(reference_offset, year, month, day, 0, 0, 0, 0) {
            Some(x) => x,
            None => continue,
        };
        if let Some((h, mi, s, us, offset)) = find_nearby_time(text, all.start(), all.end()) {
            let tz = offset.unwrap_or(reference_offset);
            if let Some(with_time) = build_datetime(tz, year, month, day, h, mi, s, us) {
                dt = with_time;
            }
        }
        out.push(RawMatch {
            kind: "absolute",
            text: all.as_str().to_string(),
            start: all.start(),
            end: all.end(),
            locale: "und".to_string(),
            grain: if dt.time().second() > 0 {
                "second"
            } else if dt.time().hour() > 0 || dt.time().minute() > 0 {
                "minute"
            } else {
                "day"
            },
            value: RawValue::Absolute {
                datetime: dt.to_rfc3339(),
                timezone_source: None,
            },
            confidence: 0.84,
            warnings: vec!["inferred_year".to_string()],
        });
    }

    if !strict {
        for caps in year_only_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            if out
                .iter()
                .any(|m| m.kind == "absolute" && all.start() < m.end && all.end() > m.start)
            {
                continue;
            }
            let year: i32 = caps["year"].parse().unwrap_or_default();
            let month = reference.month();
            let day = reference.day();
            let Some(dt) = build_datetime(reference_offset, year, month, day, 0, 0, 0, 0) else {
                continue;
            };
            out.push(RawMatch {
                kind: "absolute",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: "day",
                value: RawValue::Absolute {
                    datetime: dt.to_rfc3339(),
                    timezone_source: None,
                },
                confidence: 0.72,
                warnings: vec!["year_only_inference".to_string()],
            });
        }
    }

    if strict {
        out.retain(|m| m.kind == "absolute");
    }

    let mut consumed: Vec<(usize, usize)> = Vec::new();

    if !strict {
        for caps in relative_word_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            let Some(days) = relative_word_days(all.as_str()) else {
                continue;
            };
            let resolved = reference + Duration::days(days);
            out.push(RawMatch {
                kind: "relative",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: "day",
                value: RawValue::Relative {
                    resolved_datetime: resolved.to_rfc3339(),
                    delta_seconds: days * 86_400,
                    anchor: "reference".to_string(),
                },
                confidence: 0.92,
                warnings: vec![],
            });
            consumed.push((all.start(), all.end()));
        }

        for caps in relative_weekday_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            let direction = caps
                .name("dir")
                .map(|m| m.as_str().to_lowercase())
                .unwrap_or_default();
            let weekday_token = match caps.name("weekday") {
                Some(m) => m.as_str(),
                None => continue,
            };
            let Some(target_wd) = weekday_index(weekday_token) else {
                continue;
            };
            let current_wd = reference.weekday().num_days_from_monday();
            let delta_days = if direction == "next" {
                let mut d = (target_wd as i64 - current_wd as i64).rem_euclid(7);
                if d == 0 {
                    d = 7;
                }
                d
            } else {
                let mut d = (current_wd as i64 - target_wd as i64).rem_euclid(7);
                if d == 0 {
                    d = 7;
                }
                -d
            };
            let resolved = reference + Duration::days(delta_days);
            out.push(RawMatch {
                kind: "relative",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: "day",
                value: RawValue::Relative {
                    resolved_datetime: resolved.to_rfc3339(),
                    delta_seconds: delta_days * 86_400,
                    anchor: "reference".to_string(),
                },
                confidence: 0.90,
                warnings: vec![],
            });
            consumed.push((all.start(), all.end()));
        }

        for caps in in_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            let num: i64 = caps["num"].parse().unwrap_or_default();
            let Some(unit_s) = unit_seconds(&caps["unit"]) else {
                continue;
            };
            let delta = num * unit_s;
            let resolved = reference + Duration::seconds(delta);
            out.push(RawMatch {
                kind: "relative",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: if unit_s < 60 { "second" } else { "day" },
                value: RawValue::Relative {
                    resolved_datetime: resolved.to_rfc3339(),
                    delta_seconds: delta,
                    anchor: "reference".to_string(),
                },
                confidence: 0.90,
                warnings: vec![],
            });
            consumed.push((all.start(), all.end()));
        }

        for caps in ago_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            let num: i64 = caps["num"].parse().unwrap_or_default();
            let Some(unit_s) = unit_seconds(&caps["unit"]) else {
                continue;
            };
            let delta = -(num * unit_s);
            let resolved = reference + Duration::seconds(delta);
            out.push(RawMatch {
                kind: "relative",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: if unit_s < 60 { "second" } else { "day" },
                value: RawValue::Relative {
                    resolved_datetime: resolved.to_rfc3339(),
                    delta_seconds: delta,
                    anchor: "reference".to_string(),
                },
                confidence: 0.90,
                warnings: vec![],
            });
            consumed.push((all.start(), all.end()));
        }

        for caps in duration_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            if consumed
                .iter()
                .any(|(s, e)| all.start() >= *s && all.end() <= *e)
            {
                continue;
            }
            let num: i64 = caps["num"].parse().unwrap_or_default();
            let Some(unit_s) = unit_seconds(&caps["unit"]) else {
                continue;
            };
            let total = num * unit_s;
            let mut components = HashMap::new();
            components.insert(caps["unit"].to_lowercase(), num);
            out.push(RawMatch {
                kind: "duration",
                text: all.as_str().to_string(),
                start: all.start(),
                end: all.end(),
                locale: "und".to_string(),
                grain: if unit_s < 60 { "second" } else { "day" },
                value: RawValue::Duration {
                    total_seconds: total,
                    components,
                },
                confidence: 0.86,
                warnings: vec![],
            });
        }
    }

    out.sort_by(|a, b| {
        let s = a.start.cmp(&b.start);
        if s != Ordering::Equal {
            return s;
        }
        let e = a.end.cmp(&b.end);
        if e != Ordering::Equal {
            return e;
        }
        a.kind.cmp(b.kind)
    });

    out.dedup_by(|a, b| {
        a.kind == b.kind && a.start == b.start && a.end == b.end && a.text == b.text
    });
    out
}

fn to_py_dict<'py>(py: Python<'py>, m: &RawMatch) -> PyResult<Bound<'py, PyDict>> {
    let out = PyDict::new_bound(py);
    out.set_item("kind", m.kind)?;
    out.set_item("text", &m.text)?;
    out.set_item("start", m.start)?;
    out.set_item("end", m.end)?;
    out.set_item("locale", &m.locale)?;
    out.set_item("grain", m.grain)?;
    out.set_item("confidence", m.confidence)?;
    out.set_item("warnings", m.warnings.clone())?;

    let value = PyDict::new_bound(py);
    match &m.value {
        RawValue::Absolute {
            datetime,
            timezone_source,
        } => {
            value.set_item("type", "absolute")?;
            value.set_item("datetime", datetime)?;
            value.set_item("timezone_source", timezone_source.clone())?;
        }
        RawValue::Relative {
            resolved_datetime,
            delta_seconds,
            anchor,
        } => {
            value.set_item("type", "relative")?;
            value.set_item("resolved_datetime", resolved_datetime)?;
            value.set_item("delta_seconds", *delta_seconds)?;
            value.set_item("anchor", anchor)?;
        }
        RawValue::Duration {
            total_seconds,
            components,
        } => {
            value.set_item("type", "duration")?;
            value.set_item("total_seconds", *total_seconds)?;
            value.set_item("components", components.clone())?;
        }
    }
    out.set_item("value", value)?;
    out.set_item("alternates", PyList::empty_bound(py))?;
    Ok(out)
}

#[pyfunction]
#[pyo3(signature = (text, reference_dt=None, locales=None, strict=false, first="month"))]
fn extract(
    py: Python<'_>,
    text: &str,
    reference_dt: Option<&str>,
    locales: Option<Vec<String>>,
    strict: bool,
    first: &str,
) -> PyResult<PyObject> {
    let _ = locales;
    let ref_dt = parse_reference(reference_dt);
    let parsed = parse_raw(text, ref_dt, first, strict);
    let py_list = PyList::empty_bound(py);
    for m in parsed.iter() {
        py_list.append(to_py_dict(py, m)?)?;
    }
    Ok(py_list.into_any().unbind())
}

#[pymodule]
fn _kernel(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract, m)?)?;
    Ok(())
}
