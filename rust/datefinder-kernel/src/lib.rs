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
            r"(?i)\b(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})(?:[T\s](?P<h>\d{2}):(?P<min>\d{2})(?::(?P<s>\d{2})(?:[\,\.](?P<us>\d{1,6}))?)?(?:\s*(?P<tz>Z|[+\-]\d{2}:?\d{2}))?(?:\s+(?P<tzabbr>[A-Za-z]{2,5}))?)?\b",
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

fn double_slash_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(r"(?P<a>\d{1,2})/(?P<b>\d{1,2})//(?P<c>\d{2,4})").expect("valid regex")
    })
}

fn compact_numeric_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"\b(?P<compact>\d{8})\b").expect("valid regex"))
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

fn month_day_re() -> &'static Regex {
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
            r"(?i)\b(?P<month>{})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn month_first_hyphen_re() -> &'static Regex {
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
            r"(?i)\b(?P<month>{})-(?P<day>\d{{1,2}})(?:st|nd|rd|th)?-(?P<year>\d{{4}})\b",
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
            r"(?i)\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:\s+day\s+of|\s+de|\s+of)?\s+(?P<month>{})\.?(?:\s+de)?(?:,)?\s+(?P<year>\d{{4}})\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn month_year_re() -> &'static Regex {
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
        let pattern = format!(r"(?i)\b(?:through|during|in|on)?\s*(?P<month>{})\.?(?:\s+de)?(?:,)?\s+(?P<year>\d{{4}})\b", escaped);
        Regex::new(&pattern).expect("valid regex")
    })
}

fn month_only_context_re() -> &'static Regex {
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
            r"(?i)\b(?:from|in|during|through|on)\s+(?P<month>{})\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn month_only_standalone_re() -> &'static Regex {
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
        let pattern = format!(r"(?i)^\s*(?P<month>{})\s*$", escaped);
        Regex::new(&pattern).expect("valid regex")
    })
}

fn leading_year_tail_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| Regex::new(r"(?i)^\s*,?\s*\d{4}\b").expect("valid regex"))
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

fn day_word_month_year_words_re() -> &'static Regex {
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
            r"(?i)\b(?P<day_word>[a-z\-]+)\s+day\s+of\s+(?P<month>{})\.?(?:,)?\s+(?P<year_words>[a-z\s\-]+)\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn lower_char_boundary(text: &str, mut idx: usize) -> usize {
    idx = idx.min(text.len());
    while idx > 0 && !text.is_char_boundary(idx) {
        idx -= 1;
    }
    idx
}

fn parse_day_word(token: &str) -> Option<u32> {
    match token.to_lowercase().replace('-', " ").as_str() {
        "first" => Some(1),
        "second" => Some(2),
        "third" => Some(3),
        "fourth" => Some(4),
        "fifth" => Some(5),
        "sixth" => Some(6),
        "seventh" => Some(7),
        "eighth" => Some(8),
        "ninth" => Some(9),
        "tenth" => Some(10),
        "eleventh" => Some(11),
        "twelfth" => Some(12),
        "thirteenth" => Some(13),
        "fourteenth" => Some(14),
        "fifteenth" => Some(15),
        "sixteenth" => Some(16),
        "seventeenth" => Some(17),
        "eighteenth" => Some(18),
        "nineteenth" => Some(19),
        "twentieth" => Some(20),
        "twenty first" => Some(21),
        "twenty second" => Some(22),
        "twenty third" => Some(23),
        "twenty fourth" => Some(24),
        "twenty fifth" => Some(25),
        "twenty sixth" => Some(26),
        "twenty seventh" => Some(27),
        "twenty eighth" => Some(28),
        "twenty ninth" => Some(29),
        "thirtieth" => Some(30),
        "thirty first" => Some(31),
        _ => None,
    }
}

fn number_word_value(token: &str) -> Option<i32> {
    match token {
        "zero" => Some(0),
        "one" => Some(1),
        "two" => Some(2),
        "three" => Some(3),
        "four" => Some(4),
        "five" => Some(5),
        "six" => Some(6),
        "seven" => Some(7),
        "eight" => Some(8),
        "nine" => Some(9),
        "ten" => Some(10),
        "eleven" => Some(11),
        "twelve" => Some(12),
        "thirteen" => Some(13),
        "fourteen" => Some(14),
        "fifteen" => Some(15),
        "sixteen" => Some(16),
        "seventeen" => Some(17),
        "eighteen" => Some(18),
        "nineteen" => Some(19),
        "twenty" => Some(20),
        "thirty" => Some(30),
        "forty" => Some(40),
        "fifty" => Some(50),
        "sixty" => Some(60),
        "seventy" => Some(70),
        "eighty" => Some(80),
        "ninety" => Some(90),
        _ => None,
    }
}

fn parse_english_year_words(raw: &str) -> Option<i32> {
    let mut total = 0i32;
    let mut current = 0i32;
    let mut seen = false;
    for token in raw.to_lowercase().replace('-', " ").split_whitespace() {
        if token == "and" {
            continue;
        }
        if let Some(v) = number_word_value(token) {
            current += v;
            seen = true;
            continue;
        }
        if token == "hundred" {
            if current == 0 {
                current = 1;
            }
            current *= 100;
            seen = true;
            continue;
        }
        if token == "thousand" {
            if current == 0 {
                current = 1;
            }
            total += current * 1000;
            current = 0;
            seen = true;
            continue;
        }
        return None;
    }
    if !seen {
        return None;
    }
    total += current;
    if (1..=9999).contains(&total) {
        Some(total)
    } else {
        None
    }
}

fn upper_char_boundary(text: &str, mut idx: usize) -> usize {
    idx = idx.min(text.len());
    while idx < text.len() && !text.is_char_boundary(idx) {
        idx += 1;
    }
    idx
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

fn weekday_day_month_re() -> &'static Regex {
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
            r"(?i)\b(?P<weekday>monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<month>{})\.?\b",
            escaped
        );
        Regex::new(&pattern).expect("valid regex")
    })
}

fn time_re() -> &'static Regex {
    static RE: OnceLock<Regex> = OnceLock::new();
    RE.get_or_init(|| {
        Regex::new(
            r"(?i)\b(?P<h>\d{1,2})(?P<sep>[:\.])(?P<min>\d{2})(?:[:\.](?P<s>\d{2}))?(?:[\,\.](?P<us>\d{1,6}))?\s*(?P<ampm>a\.?m\.?|p\.?m\.?)?(?:\s*(?P<offset>Z|[+\-]\d{2}:?\d{2}))?\b",
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

fn coerce_year(year: i32, two_digit_year_pivot: u8) -> i32 {
    if year < 100 {
        if year <= i32::from(two_digit_year_pivot) {
            2000 + year
        } else {
            1900 + year
        }
    } else {
        year
    }
}

fn parse_slash_candidates(
    a: i32,
    b: i32,
    c: i32,
    first: &str,
    two_digit_year_pivot: u8,
) -> Vec<(i32, u32, u32)> {
    let mut out = Vec::new();
    let preferred = match first {
        "day" => (coerce_year(c, two_digit_year_pivot), b as u32, a as u32),
        "year" => (coerce_year(a, two_digit_year_pivot), b as u32, c as u32),
        _ => (coerce_year(c, two_digit_year_pivot), a as u32, b as u32),
    };
    out.push(preferred);
    for fallback in [
        (coerce_year(c, two_digit_year_pivot), b as u32, a as u32), // DMY
        (coerce_year(c, two_digit_year_pivot), a as u32, b as u32), // MDY
        (coerce_year(a, two_digit_year_pivot), b as u32, c as u32), // YMD-ish legacy
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

fn parse_tz_abbrev(token: &str) -> Option<FixedOffset> {
    match token.trim().to_uppercase().as_str() {
        "UTC" | "GMT" | "Z" => FixedOffset::east_opt(0),
        "CET" => FixedOffset::east_opt(3600),
        "CEST" => FixedOffset::east_opt(7200),
        "EET" => FixedOffset::east_opt(7200),
        "EEST" => FixedOffset::east_opt(10_800),
        "MSK" => FixedOffset::east_opt(10_800),
        "PST" => FixedOffset::east_opt(-8 * 3600),
        "PDT" => FixedOffset::east_opt(-7 * 3600),
        "MST" => FixedOffset::east_opt(-7 * 3600),
        "MDT" => FixedOffset::east_opt(-6 * 3600),
        "CST" => FixedOffset::east_opt(-6 * 3600),
        "CDT" => FixedOffset::east_opt(-5 * 3600),
        "EST" => FixedOffset::east_opt(-5 * 3600),
        "EDT" => FixedOffset::east_opt(-4 * 3600),
        _ => None,
    }
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
    let sep = caps.name("sep").map(|m| m.as_str()).unwrap_or(":");
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
    if sep == "." && ampm.is_empty() && hour <= 12 && (1..=12).contains(&minute) {
        return None;
    }
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
    if !text.is_char_boundary(start) || !text.is_char_boundary(end) {
        return false;
    }
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

fn is_alnum_bounded(text: &str, start: usize, end: usize) -> bool {
    if !text.is_char_boundary(start) || !text.is_char_boundary(end) {
        return false;
    }
    let prev_is_alnum = text[..start]
        .chars()
        .next_back()
        .map(|c| c.is_ascii_alphanumeric())
        .unwrap_or(false);
    let next_is_alnum = text[end..]
        .chars()
        .next()
        .map(|c| c.is_ascii_alphanumeric())
        .unwrap_or(false);
    !prev_is_alnum && !next_is_alnum
}

fn has_dot_digit_tail(text: &str, idx: usize) -> bool {
    let bytes = text.as_bytes();
    idx + 1 < bytes.len() && bytes[idx] == b'.' && bytes[idx + 1].is_ascii_digit()
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
    let window_start = lower_char_boundary(text, start.saturating_sub(20));
    let window_end = upper_char_boundary(text, (end + 30).min(text.len()));
    let window = &text[window_start..window_end];
    let mut best_after: Option<(u32, u32, u32, u32, Option<FixedOffset>)> = None;
    let mut best_after_distance = usize::MAX;
    let mut best_before: Option<(u32, u32, u32, u32, Option<FixedOffset>)> = None;
    let mut best_before_distance = usize::MAX;
    for caps in time_re().captures_iter(window) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        let global_start = window_start + all.start();
        let global_end = window_start + all.end();
        // Do not treat fragments inside a detected date token as nearby time.
        if global_start < end && global_end > start {
            continue;
        }
        if let Some(parsed) = parse_time_capture(&caps) {
            if global_start >= end {
                let distance = global_start - end;
                if distance < best_after_distance {
                    best_after_distance = distance;
                    best_after = Some(parsed);
                }
            } else if global_end <= start {
                let distance = start - global_end;
                if distance < best_before_distance {
                    best_before_distance = distance;
                    best_before = Some(parsed);
                }
            }
        }
    }
    best_after.or(best_before)
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
    two_digit_year_pivot: u8,
    allow_month_only: bool,
    allow_compact_numeric: bool,
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
        let numeric_offset = caps.name("tz").and_then(|x| parse_tz_offset(x.as_str()));
        let abbrev_offset = caps
            .name("tzabbr")
            .and_then(|x| parse_tz_abbrev(x.as_str()));
        let offset = numeric_offset.or(abbrev_offset).unwrap_or(reference_offset);
        let mut warnings = Vec::new();
        if let (Some(explicit), Some(abbrev)) = (numeric_offset, abbrev_offset) {
            if explicit != abbrev {
                warnings.push("tz_abbrev_mismatch_ignored".to_string());
            }
        }
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
                timezone_source: if caps.name("tz").is_some() {
                    Some("explicit".to_string())
                } else if caps.name("tzabbr").is_some() {
                    Some("abbreviation".to_string())
                } else {
                    None
                },
            },
            confidence: 0.99,
            warnings,
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
            for (y, m, d) in parse_slash_candidates(a, b, c, first, two_digit_year_pivot) {
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

    if allow_compact_numeric {
        for caps in compact_numeric_re().captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            if !is_digit_bounded(text, all.start(), all.end()) {
                continue;
            }
            let raw = caps["compact"].to_string();
            if raw.len() != 8 {
                continue;
            }
            let (y, m, d) = match first {
                "day" => (
                    raw[4..8].parse().unwrap_or_default(),
                    raw[2..4].parse().unwrap_or_default(),
                    raw[0..2].parse().unwrap_or_default(),
                ),
                "year" => (
                    raw[0..4].parse().unwrap_or_default(),
                    raw[4..6].parse().unwrap_or_default(),
                    raw[6..8].parse().unwrap_or_default(),
                ),
                _ => (
                    raw[4..8].parse().unwrap_or_default(),
                    raw[0..2].parse().unwrap_or_default(),
                    raw[2..4].parse().unwrap_or_default(),
                ),
            };
            let Some(dt) = build_datetime(reference_offset, y, m, d, 0, 0, 0, 0) else {
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
                confidence: 0.83,
                warnings: vec!["compact_numeric_opt_in".to_string()],
            });
        }
    }

    // Allow light recovery for malformed dates with double slash, but only on token boundaries.
    for caps in double_slash_re().captures_iter(text) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        if !is_alnum_bounded(text, all.start(), all.end()) {
            continue;
        }
        if !is_digit_bounded(text, all.start(), all.end()) {
            continue;
        }
        let a: i32 = caps["a"].parse().unwrap_or_default();
        let b: i32 = caps["b"].parse().unwrap_or_default();
        let c: i32 = caps["c"].parse().unwrap_or_default();
        let mut dt = None;
        for (y, m, d) in parse_slash_candidates(a, b, c, first, two_digit_year_pivot) {
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
            confidence: 0.88,
            warnings: vec!["malformed_separator_recovery".to_string()],
        });
    }

    // Month-name based dates with automata-backed lexicon prebuilt.
    let _ = month_automaton();
    for re in [
        month_first_re(),
        month_first_hyphen_re(),
        day_first_re(),
        month_day_re(),
    ] {
        for caps in re.captures_iter(text) {
            let all = match caps.get(0) {
                Some(m) => m,
                None => continue,
            };
            if std::ptr::eq(re, month_day_re())
                && leading_year_tail_re().is_match(&text[all.end()..])
            {
                continue;
            }
            if std::ptr::eq(re, month_day_re()) && has_dot_digit_tail(text, all.end()) {
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
            let year: i32 = caps
                .name("year")
                .map(|m| m.as_str().parse().unwrap_or_default())
                .unwrap_or(reference.year());
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

    for caps in month_year_re().captures_iter(text) {
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
        let month_token = match caps.name("month") {
            Some(m) => m.as_str().to_lowercase().trim_end_matches('.').to_string(),
            None => continue,
        };
        let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
            continue;
        };
        let year: i32 = caps["year"].parse().unwrap_or_default();
        let Some(dt) = build_datetime(reference_offset, year, month, 1, 0, 0, 0, 0) else {
            continue;
        };
        out.push(RawMatch {
            kind: "absolute",
            text: all.as_str().to_string(),
            start: all.start(),
            end: all.end(),
            locale: "und".to_string(),
            grain: "month",
            value: RawValue::Absolute {
                datetime: dt.to_rfc3339(),
                timezone_source: None,
            },
            confidence: 0.79,
            warnings: vec!["inferred_day".to_string()],
        });
    }

    if allow_month_only {
        for re in [month_only_context_re(), month_only_standalone_re()] {
            for caps in re.captures_iter(text) {
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
                let month_token = match caps.name("month") {
                    Some(m) => m.as_str().to_lowercase(),
                    None => continue,
                };
                let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
                    continue;
                };
                let Some(dt) =
                    build_datetime(reference_offset, reference.year(), month, 1, 0, 0, 0, 0)
                else {
                    continue;
                };
                out.push(RawMatch {
                    kind: "absolute",
                    text: all.as_str().to_string(),
                    start: all.start(),
                    end: all.end(),
                    locale: "und".to_string(),
                    grain: "month",
                    value: RawValue::Absolute {
                        datetime: dt.to_rfc3339(),
                        timezone_source: None,
                    },
                    confidence: 0.72,
                    warnings: vec![
                        "month_only_inference".to_string(),
                        "inferred_day".to_string(),
                    ],
                });
            }
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

    // Worded forms like "twentieth day of august, one thousand nine hundred and five".
    for caps in day_word_month_year_words_re().captures_iter(text) {
        let all = match caps.get(0) {
            Some(m) => m,
            None => continue,
        };
        let day_word = match caps.name("day_word") {
            Some(m) => m.as_str(),
            None => continue,
        };
        let Some(day) = parse_day_word(day_word) else {
            continue;
        };
        let month_token = match caps.name("month") {
            Some(m) => m.as_str().to_lowercase().trim_end_matches('.').to_string(),
            None => continue,
        };
        let Some(month) = month_lookup().get(month_token.as_str()).copied() else {
            continue;
        };
        let year_words = match caps.name("year_words") {
            Some(m) => m.as_str(),
            None => continue,
        };
        let Some(year) = parse_english_year_words(year_words) else {
            continue;
        };
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
            confidence: 0.78,
            warnings: vec!["worded_date_parse".to_string()],
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

    // Weekday + day/month without year, infer reference year.
    for caps in weekday_day_month_re().captures_iter(text) {
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
#[pyo3(signature = (text, reference_dt=None, locales=None, strict=false, first="month", two_digit_year_pivot=None, allow_month_only=true, allow_compact_numeric=false))]
fn extract(
    py: Python<'_>,
    text: &str,
    reference_dt: Option<&str>,
    locales: Option<Vec<String>>,
    strict: bool,
    first: &str,
    two_digit_year_pivot: Option<u8>,
    allow_month_only: bool,
    allow_compact_numeric: bool,
) -> PyResult<PyObject> {
    let _ = locales;
    let ref_dt = parse_reference(reference_dt);
    let parsed = parse_raw(
        text,
        ref_dt,
        first,
        strict,
        two_digit_year_pivot.unwrap_or(68),
        allow_month_only,
        allow_compact_numeric,
    );
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
