from datetime import datetime, timezone

import datefinder
from datefinder.v2 import AbsoluteValue, DurationValue, RelativeValue


def test_v2_absolute_iso():
    ref = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out = datefinder.extract("deploy at 2024-11-03 18:00", reference_dt=ref)
    assert len(out) >= 1
    assert out[0].kind == "absolute"
    assert isinstance(out[0].value, AbsoluteValue)
    assert out[0].value.datetime_value.year == 2024
    assert out[0].value.datetime_value.month == 11
    assert out[0].value.datetime_value.day == 3


def test_v2_relative_and_duration():
    ref = datetime(2024, 1, 10, tzinfo=timezone.utc)
    out = datefinder.extract("in 3 days and 20 days", reference_dt=ref)
    kinds = [m.kind for m in out]
    assert "relative" in kinds
    assert "duration" in kinds
    rel = next(m for m in out if m.kind == "relative")
    dur = next(m for m in out if m.kind == "duration")
    assert isinstance(rel.value, RelativeValue)
    assert isinstance(dur.value, DurationValue)
    assert rel.value.resolved_datetime.date().isoformat() == "2024-01-13"
    assert dur.value.total_seconds == 20 * 24 * 60 * 60


def test_v2_stream_mode():
    ref = datetime(2024, 1, 1, tzinfo=timezone.utc)
    stream = datefinder.extract("today 2024-05-01", reference_dt=ref, stream=True)
    collected = list(stream)
    assert len(collected) >= 2


def test_find_dates_compat():
    ref = datetime(2024, 1, 1, tzinfo=timezone.utc)
    out = list(datefinder.find_dates_compat("tomorrow and 2024-12-10", reference_dt=ref))
    assert len(out) >= 2
    assert all(isinstance(x, datetime) for x in out)


def test_v2_month_name_with_time():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates_compat("April 9, 2013 at 6:11 a.m.", reference_dt=ref))
    assert out[0] == datetime(2013, 4, 9, 6, 11, tzinfo=timezone.utc)


def test_v2_iso_with_z_and_fractional():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates_compat("2017-02-03T09:04:08.001Z", reference_dt=ref))
    assert out == [datetime(2017, 2, 3, 9, 4, 8, 1000, tzinfo=timezone.utc)]


def test_v2_hyphen_date():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates_compat("06-17-2014", reference_dt=ref))
    assert out == [datetime(2014, 6, 17, tzinfo=timezone.utc)]


def test_v2_strict_ordinal():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates_compat("19th day of May, 2015", reference_dt=ref, strict=True))
    assert out == [datetime(2015, 5, 19, tzinfo=timezone.utc)]


def test_find_dates_defaults_to_v2_engine():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("tomorrow and 2024-12-10", base_date=ref))
    assert len(out) >= 2
    assert out[0].tzinfo is not None


def test_find_dates_legacy_engine_opt_in():
    out = list(datefinder.find_dates("June 2018", engine="legacy"))
    assert out
    assert out[0].year == 2018


def test_find_dates_source_and_index_in_v2_default():
    ref = datetime(2026, 3, 18, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("ship by 2024-12-10", base_date=ref, source=True, index=True))
    assert out
    dt, text, idx = out[0]
    assert dt.year == 2024
    assert text == "2024-12-10"
    assert idx == (8, 18)


def test_issue_59_ymd_slash_with_time():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("handpunched on 2017/08/27 @ 7:24 AM", base_date=ref))
    assert out == [datetime(2017, 8, 27, 7, 24, tzinfo=timezone.utc)]


def test_issue_202_weekday_month_day_without_year():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("Tuesday, April 30, Wednesday, May 1", base_date=ref))
    assert len(out) == 2
    assert (out[0].month, out[0].day) == (4, 30)
    assert (out[1].month, out[1].day) == (5, 1)


def test_issue_179_dot_dates_in_filename():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("07.11.2022_-_11.11.2022.pdf", base_date=ref, first="day"))
    assert out == [
        datetime(2022, 11, 7, tzinfo=timezone.utc),
        datetime(2022, 11, 11, tzinfo=timezone.utc),
    ]


def test_issue_176_year_day_month_name():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("2020,31,August", base_date=ref, first="year"))
    assert out == [datetime(2020, 8, 31, tzinfo=timezone.utc)]


def test_issue_160_day_of_month_name_phrase():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)
    out = list(datefinder.find_dates("At 13:14 on the 23 of october 2020", base_date=ref))
    assert out == [datetime(2020, 10, 23, 13, 14, tzinfo=timezone.utc)]


def test_issue_170_next_weekday_relative():
    ref = datetime(2026, 3, 20, tzinfo=timezone.utc)  # Friday
    out = list(datefinder.find_dates("next Friday", base_date=ref))
    assert out == [datetime(2026, 3, 27, tzinfo=timezone.utc)]
