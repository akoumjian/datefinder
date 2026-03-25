# Release Checklist

Release target in this cycle: `v1.0.0`

## 1. Validate Code and Parser Behavior

```bash
pytest -q
python scripts/build_conformance_corpus.py
python scripts/diff_legacy_v2.py --min-v2-legacy-ratio 1.0
```

Confirm:

- `conformance/reports/legacy_v2_diff_summary.json`
- `conformance/reports/behavior_change_changelog.md`
- `conformance/reports/ambiguity_showcase.md`

## 2. Validate API Contracts

```bash
python - <<'PY'
import datefinder
print("version:", datefinder.__version__)
print("default:", list(datefinder.find_dates("tomorrow and 2024-12-10")))
print("legacy:", list(datefinder.find_dates("June 2018", engine="legacy")))
print("legacy-explicit:", list(datefinder.find_dates_legacy("June 2018")))
PY
```

## 3. Validate Performance

Run local benchmark:

```bash
python bench/bench_core.py --dataset bench/corpus_core.txt --iterations 20
```

Optional Duckling gate:

```bash
python bench/bench_gate.py \
  --dataset bench/corpus_core.txt \
  --duckling-url http://localhost:8000/parse \
  --iterations 20 \
  --required-ratio 0.95
```

## 4. Build Distribution Artifacts

Build package wheel and sdist with Rust kernel integrated:

```bash
python -m pip install --upgrade maturin
maturin build --release --manifest-path rust/datefinder-kernel/Cargo.toml --out dist
maturin sdist --manifest-path rust/datefinder-kernel/Cargo.toml --out dist
```

## 5. Validate Installability (Local Smoke)

```bash
python -m venv /tmp/datefinder-ga-smoke
. /tmp/datefinder-ga-smoke/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/datefinder-1.0.0*.whl
python - <<'PY'
import datefinder
print(list(datefinder.find_dates("tomorrow and 2024-12-10")))
PY
deactivate
```

Source-build smoke (requires Rust toolchain):

```bash
. /tmp/datefinder-ga-smoke/bin/activate
python -m pip uninstall -y datefinder
python -m pip install dist/datefinder-1.0.0.tar.gz
python - <<'PY'
import datefinder
print(list(datefinder.find_dates("created 01/15/2005 by ACME")))
PY
deactivate
```

## 6. Prepare Release Notes

- Summarize parser behavior changes from `behavior_change_changelog.md`.
- Include conformance and benchmark numbers.
- Document known limitations and planned follow-ups.
- Update `docs/releases/1.0.0.md`.

## 7. Publish

- Preflight publish to TestPyPI before final PyPI release:
  - Set repo secret: `TEST_PYPI_API_TOKEN`
  - Run workflow: `Upload Python Package (TestPyPI)` via `workflow_dispatch`
  - Confirm package and wheels at `https://test.pypi.org/project/datefinder/`
  - Validate install on clean machine:
    ```bash
    python -m pip install -U pip
    python -m pip install \
      --index-url https://test.pypi.org/simple/ \
      --extra-index-url https://pypi.org/simple \
      --only-binary=datefinder \
      datefinder==1.0.0
    ```
- Tag release (`v1.0.0`).
- Create GitHub release.
- Ensure workflows complete:
  - Python tests + conformance artifacts
  - benchmark gate
  - rust wheel artifact build target matrix:
    - manylinux2014: `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`
    - musllinux_1_2: `x86_64-unknown-linux-musl`, `aarch64-unknown-linux-musl`
    - macOS: `x86_64-apple-darwin`, `aarch64-apple-darwin`
    - Windows: `x86_64-pc-windows-msvc`
  - artifact inspection + smoke checks:
    - Linux: `auditwheel show`
    - macOS: `delocate-listdeps`
    - Windows: `delvewheel show`
    - wheel install smoke (`--only-binary=:all:`), including Linux target-container runtime smoke (QEMU for `aarch64`)
    - sdist source-build smoke (`--no-binary=datefinder`)
  - PyPI publish job

Before final publish, run `Release Candidate Validation` with `workflow_dispatch` to execute full wheel target validation matrix.

## 8. RC Portability Notes (for release body)

- Rust wheels are platform-specific.
- ABI3 lowers Python-version-specific wheel churn, but OS/arch wheel variants are still needed.
- If no matching wheel is available, installation falls back to source build and needs Rust tooling.
