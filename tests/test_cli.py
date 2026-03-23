import json
import subprocess
import sys


def _run_cli(*args, input_text=None):
    cmd = [sys.executable, "-m", "datefinder", *args]
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_default_json():
    result = _run_cli(
        "--json",
        "--reference",
        "2026-03-18T00:00:00+00:00",
        "tomorrow and 2024-12-10",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert isinstance(payload, list)
    assert len(payload) >= 2
    assert any(item["datetime"].startswith("2024-12-10") for item in payload)


def test_cli_legacy_source_index_json():
    result = _run_cli(
        "--engine",
        "legacy",
        "--source",
        "--index",
        "--json",
        "created 01/15/2005 by ACME",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload
    first = payload[0]
    assert first["datetime"].startswith("2005-01-15")
    assert "text" in first
    assert "index" in first
    assert first["index"][0] < first["index"][1]


def test_cli_extract_json():
    result = _run_cli(
        "--engine",
        "extract",
        "--json",
        "--reference",
        "2026-03-18T00:00:00+00:00",
        "in 3 days",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload
    assert payload[0]["kind"] == "relative"
    assert payload[0]["value"]["delta_seconds"] == 3 * 86400


def test_cli_invalid_source_for_extract():
    result = _run_cli("--engine", "extract", "--source", "today")
    assert result.returncode != 0
    assert "--source/--index are only supported" in result.stderr


def test_cli_no_month_only():
    result = _run_cli(
        "--json",
        "--no-month-only",
        "--reference",
        "2026-03-18T00:00:00+00:00",
        "in May",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == []


def test_cli_compact_numeric_opt_in():
    result = _run_cli(
        "--json",
        "--compact-numeric",
        "--first",
        "year",
        "--reference",
        "2026-03-18T00:00:00+00:00",
        "invoice 20240315 generated",
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload
    assert payload[0]["datetime"].startswith("2024-03-15")
