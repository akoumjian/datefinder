# Changelog

## 1.0.0 - 2026-03-25

### Changed

- Promoted the `1.0.0rc3` release-candidate line to final `1.0.0`.
- `find_dates(...)` remains defaulted to the v2 compatibility engine, with legacy behavior available via `find_dates_legacy(...)` or `engine="legacy"`.

### Packaging

- Published final cross-platform wheels and source distribution for `1.0.0`.
- Kept source-build install path for platforms without a matching wheel (Rust toolchain required).

## 1.0.0rc3 - 2026-03-23

### Fixed

- Release packaging pipeline now filters unsupported PyPy wheel artifacts before publish.
- Publish checksum verification now excludes filtered artifacts so upload validation remains deterministic.

### Notes

- `1.0.0rc3` supersedes `1.0.0rc2` for release-candidate validation and installation guidance.

## 1.0.0rc2 - 2026-03-23

### Added

- Added compatibility flags for v2/default engine:
  - `allow_month_only` (default `True`)
  - `allow_compact_numeric` (default `False`)
  - `allow_multiline` (default `True`)
- Added matching CLI flags:
  - `--no-month-only`
  - `--compact-numeric`
  - `--no-multiline`
- Added expanded regression coverage for issue-driven edge cases and new flags.

### Changed

- Month-only parsing is now enabled by default in v2 compatibility mode and resolves to first day of month.
- Compact 8-digit numeric parsing (e.g. `20240315`) is now opt-in only.
- Multiline matching can now be disabled to force line-scoped extraction.

### Fixed

- Prevented false positives where `month + day` was incorrectly extracted from dotted time ranges (e.g. `April 09.00`).

## 1.0.0rc1 - 2026-03-19

### Breaking / Behavioral Changes

- `find_dates(...)` now defaults to the v2 compatibility engine.
- Added explicit legacy entrypoint: `find_dates_legacy(...)`.
- Added `engine` selector on `find_dates(...)` (`"v2"` default, `"legacy"` opt-in).
- Rust kernel is now mandatory for v2/default runtime execution (no Python parsing fallback).

### Added

- Added v2 typed extraction API with support for absolute, relative, and duration outputs.
- Integrated Rust kernel into `datefinder` package build/runtime.
- Added benchmark harness and Duckling comparison gate scripts.
- Added conformance corpus builder and differential legacy-v2 reporting.
- Added ambiguity/multilingual showcase with interpretation judgments.

### Improved

- Improved v2 parser behavior for:
  - ISO timestamps with `Z`/offset and fractional seconds
  - hyphen-delimited dates
  - strict ordinal date phrases
  - nearby time extraction for month-name dates
- Added behavior-change changelog generation from conformance scenarios.
