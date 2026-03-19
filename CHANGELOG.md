# Changelog

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
