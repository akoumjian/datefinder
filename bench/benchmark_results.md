# Benchmark Results (2026-03-19 12:43:01Z)

| dataset | size | v2 median (s) | legacy median (s) | dateparser median (s) | duckling_http median (s) | v2 vs legacy | v2 vs dateparser | v2 vs duckling_http |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| core_corpus | 498 | 0.000267 | 0.003094 | 0.181080 | n/a | 11.59x | 678.35x | n/a |
| seattle_html_76k | 74838 | 0.020826 | 0.287495 | 0.750812 | n/a | 13.80x | 36.05x | n/a |
| test_data_560k | 552301 | 0.253541 | 2.875369 | n/a | n/a | 11.34x | n/a | n/a |

Notes:
- `v2` uses `datefinder.extract(...)`.
- `legacy` uses `datefinder.find_dates_legacy(...)`.
- `dateparser` uses `dateparser.search.search_dates` when installed.
- `duckling_http` uses `POST /parse` on the configured Duckling URL.
- `n/a` means the engine was unavailable or failed for that dataset in this run.
- Results are hardware/environment dependent; use as directional guidance.
