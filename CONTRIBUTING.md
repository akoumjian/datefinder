# Contributing

## Development Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install maturin pytest tox
python -m pip install -e .
```

Install Rust toolchain (required for `datefinder` runtime):

```bash
curl https://sh.rustup.rs -sSf | sh -s -- -y
source "$HOME/.cargo/env"
```

Build/install locally with maturin (alternative to `pip install -e .`):

```bash
maturin develop --release --manifest-path rust/datefinder-kernel/Cargo.toml
```

## Test Commands

```bash
pytest -q
tox -q
python scripts/build_conformance_corpus.py
python scripts/diff_legacy_v2.py
python bench/bench_core.py --dataset bench/corpus_core.txt --iterations 10
```

Optional Duckling speed gate:

```bash
python bench/bench_gate.py \
  --dataset bench/corpus_core.txt \
  --duckling-url http://localhost:8000/parse \
  --iterations 10 \
  --required-ratio 0.95
```

## Reports

Generated reports are under `conformance/reports/`:

- `legacy_v2_diff_report.md`
- `ambiguity_showcase.md`
- `behavior_change_changelog.md`

## Engine Selection

- Default: `datefinder.find_dates(...)` uses v2 compatibility engine.
- Legacy baseline: `datefinder.find_dates_legacy(...)`.
- Override default engine at runtime:
  - `find_dates(..., engine="legacy")`
  - `DATEFINDER_DEFAULT_ENGINE=legacy`
