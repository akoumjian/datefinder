# Core Benchmark Harness

This benchmark compares the new v2 extractor core against a Duckling baseline.
The primary gate is **in-process parser performance**.

For direct old-vs-new comparisons, use `bench_readme_compare.py` which compares:

- `v2`: `datefinder.extract(...)`
- `legacy`: `datefinder.find_dates_legacy(...)`

## Usage

```bash
python bench/bench_core.py --dataset bench/corpus_core.txt --iterations 20
```

To include Duckling:

```bash
python bench/bench_core.py --dataset bench/corpus_core.txt --iterations 20 --duckling-url http://localhost:8000/parse
```

Or compare with an in-process Python Duckling binding:

```bash
python bench/bench_core.py --dataset bench/corpus_core.txt --iterations 20 --duckling-python
```

## Notes

- The benchmark requires the Rust kernel; build/install must provide `datefinder._kernel`.
- Duckling comparison is optional in local runs but required in CI release gating.

## Benchmark Gate

To enforce a speed gate against Duckling:

```bash
python bench/bench_gate.py \
  --dataset bench/corpus_core.txt \
  --duckling-url http://localhost:8000/parse \
  --iterations 10 \
  --required-ratio 0.95
```

Gate condition: `v2_median <= duckling_median * required_ratio`.

## README Comparison Snapshot

Generate benchmark output intended for README updates:

```bash
python bench/bench_readme_compare.py \
  --iterations-small 12 \
  --iterations-large 2
```

Output files:

- `bench/benchmark_results.json`
- `bench/benchmark_results.md`
