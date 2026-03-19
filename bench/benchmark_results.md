# Benchmark Results (2026-03-19 17:48:32Z)

| dataset | size | v2 median (s) | legacy median (s) | dateparser median (s) | duckling_http median (s) | v2 vs legacy | v2 vs dateparser | v2 vs duckling_http |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core_corpus | 498 | 0.000236 | 0.003042 | 0.180596 | 0.050266 | 12.91x | 766.74x | 213.41x |
| seattle_html_76k | 74838 | 0.037436 | 0.281466 | 0.771712 | 25.353595 | 7.52x | 20.61x | 677.24x |
| test_data_560k | 552301 | 0.239391 | 2.840845 | n/a | n/a | 11.87x | n/a | n/a |

Notes:
- `v2` uses `datefinder.extract(...)`.
- `legacy` uses `datefinder.find_dates_legacy(...)`.
- `dateparser` uses `dateparser.search.search_dates` when installed.
- `duckling_http` uses `POST /parse` on the configured Duckling URL.
- `n/a` means the engine was unavailable or failed for that dataset in this run.
- Results are hardware/environment dependent; use as directional guidance.
