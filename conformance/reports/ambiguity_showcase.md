# Ambiguity and Multilingual Showcase

- Audited cases with preferred interpretation: 35
- Legacy aligned on audited cases: 10/35
- v2_compat aligned on audited cases: 25/35
- v2_typed aligned on audited cases: 3/35

| id | text | legacy | v2_compat | v2_typed | preferred | note | rationale |
|---|---|---|---|---|---|---|---|
| amb_001 | `01/02/03` | `['2003-01-02T00:00:00']` | `['2003-01-02T00:00:00']` | `['absolute:01/02/03']` | `both` | Ambiguous numeric date (MDY preference). | Ambiguous numeric date should follow caller 'first' preference; both agree. |
| amb_002 | `01/02/03` | `['2003-02-01T00:00:00']` | `['2003-02-01T00:00:00']` | `['absolute:01/02/03']` | `both` | Ambiguous numeric date (DMY preference). | Ambiguous numeric date should follow caller 'first' preference; both agree. |
| amb_003 | `01/02/03` | `['2001-02-03T00:00:00']` | `['2001-02-03T00:00:00']` | `['absolute:01/02/03']` | `both` | Ambiguous numeric date (YMD-like preference). | Ambiguous numeric date should follow caller 'first' preference; both agree. |
| amb_004 | `9.6 20:30` | `['2026-03-09T20:30:00']` | `[]` | `[]` | `` | Known ambiguity from open issue history. |  |
| amb_005 | `results = 3.8, 10` | `['2026-03-10T00:00:00']` | `[]` | `[]` | `v2_compat` | Strict-mode false-positive candidate. | `results = 3.8, 10` is typically not a date in strict extraction contexts. |
| amb_006 | `This is to inform you that an amount of Rs. 123.45 has been debited.` | `[]` | `[]` | `[]` | `both` | Money should usually not parse as a date. | Money should not parse as date in this sentence. |
| amb_007 | `French 75 is my favorite cocktail.` | `['2075-03-19T00:00:00']` | `[]` | `[]` | `v2_compat` | Number-containing phrase, not a date. | `French 75` should not infer year 2075. |
| amb_008 | `pre-qualification may proceed after review.` | `['2026-05-19T00:00:00']` | `[]` | `[]` | `v2_compat` | Month-name token inside non-date phrase. | `pre-qualification may` should not infer a month date. |
| amb_009 | `Date: Tue, 23 Apr 1996 13:28:27 -0400` | `['1996-04-23T17:28:27']` | `['1996-04-23T17:28:27']` | `['absolute:23 Apr 1996']` | `both` | RFC822-like timestamp. | RFC822-like timestamp should resolve with full time/offset context. |
| amb_010 | `2023-10-04 decision` | `['2023-10-04T00:00:00']` | `['2023-10-04T00:00:00']` | `['absolute:2023-10-04']` | `both` | ISO date followed by token. | ISO date adjacent to token should still parse. |
| amb_011 | `9/15/27 144A` | `[]` | `['2027-09-15T00:00:00']` | `['absolute:9/15/27']` | `v2_compat` | Date followed by alphanumeric token. | `9/15/27 144A` should still recover the date token. |
| amb_012 | `25/7//2023` | `[]` | `[]` | `[]` | `both` | Malformed separator case. | Malformed separators should not parse. |
| amb_013 | `tomorrow at noon` | `[]` | `['2026-03-19T12:00:00']` | `['relative:tomorrow']` | `v2_compat` | English relative expression. | Relative date phrase should be interpreted as relative datetime. |
| amb_014 | `in 2 weeks we launch` | `['2026-03-02T00:00:00']` | `['2026-04-01T12:00:00']` | `['relative:in 2 weeks']` | `v2_compat` | English relative by quantity. | `in 2 weeks` should be relative, not a month/day fallback. |
| amb_015 | `20 days ago` | `[]` | `['2026-02-26T12:00:00']` | `['relative:20 days ago']` | `v2_compat` | Relative offset expression. | `20 days ago` should resolve relative to reference date. |
| amb_016 | `we need a 20 day notice period` | `[]` | `[]` | `['duration:20 day']` | `v2_typed` | Duration extraction candidate. | Duration phrase is useful as duration object even if not legacy datetime. |
| amb_017 | `hoy cerramos el trimestre` | `[]` | `['2026-03-18T12:00:00']` | `['relative:hoy']` | `v2_compat` | Spanish relative keyword. | Spanish relative keyword should resolve as relative date. |
| amb_018 | `mañana enviaremos el contrato` | `[]` | `['2026-03-19T12:00:00']` | `['relative:mañana']` | `v2_compat` | Spanish tomorrow keyword. | Spanish tomorrow keyword should resolve as relative date. |
| amb_019 | `dans 2 jours on valide` | `['2026-03-02T00:00:00']` | `[]` | `['duration:2 jours']` | `v2_typed` | French relative phrase. | French `dans 2 jours` is best represented as relative or duration, not spurious absolute date. |
| amb_020 | `aujourd'hui est la date limite` | `[]` | `['2026-03-18T12:00:00']` | `["relative:aujourd'hui"]` | `v2_compat` | French today keyword. | French today keyword should resolve as relative date. |
| amb_021 | `heute ist der stichtag` | `[]` | `['2026-03-18T12:00:00']` | `['relative:heute']` | `v2_compat` | German today keyword. | German today keyword should resolve as relative date. |
| amb_022 | `morgen liefern wir` | `[]` | `['2026-03-19T12:00:00']` | `['relative:morgen']` | `v2_compat` | German tomorrow keyword. | German tomorrow keyword should resolve as relative date. |
| amb_023 | `hoje fechamos o trimestre` | `[]` | `['2026-03-18T12:00:00']` | `['relative:hoje']` | `v2_compat` | Portuguese today keyword. | Portuguese today keyword should resolve as relative date. |
| amb_024 | `amanhã revisaremos o relatório` | `[]` | `['2026-03-19T12:00:00']` | `['relative:amanhã']` | `v2_compat` | Portuguese tomorrow keyword. | Portuguese tomorrow keyword should resolve as relative date. |
| amb_025 | `oggi è la scadenza` | `[]` | `['2026-03-18T12:00:00']` | `['relative:oggi']` | `v2_compat` | Italian today keyword. | Italian today keyword should resolve as relative date. |
| amb_026 | `domani inviamo i documenti` | `[]` | `['2026-03-19T12:00:00']` | `['relative:domani']` | `v2_compat` | Italian tomorrow keyword. | Italian tomorrow keyword should resolve as relative date. |
| amb_027 | `20 marzo 2015` | `[]` | `['2015-03-20T00:00:00']` | `['absolute:20 marzo 2015']` | `v2_compat` | Day-first month-name date (Romance language). | Day-first Romance month-name date should parse. |
| amb_028 | `March 20, 2015` | `['2015-03-20T00:00:00']` | `['2015-03-20T00:00:00']` | `['absolute:March 20, 2015']` | `both` | English month-name date. | Canonical month-name date should parse. |
| amb_029 | `31/08/2012 to 30/08/2013` | `['2012-08-31T00:00:00', '2013-08-30T00:00:00']` | `['2012-08-31T00:00:00', '2013-08-30T00:00:00']` | `['absolute:31/08/2012', 'absolute:30/08/2013']` | `both` | Range-like text with day-first values. | Simple date range text should parse both endpoints. |
| amb_030 | `2017-02-03T09:04:08Z to 2017-02-03T09:04:09Z` | `['2017-02-03T09:04:08', '2017-02-03T09:04:09']` | `['2017-02-03T09:04:08', '2017-02-03T09:04:09']` | `['absolute:2017-02-03T09:04:08Z', 'absolute:2017-02-03T09:04:09Z']` | `both` | ISO timestamps with UTC suffix. | ISO UTC timestamps should parse with second precision. |
| amb_031 | `CR is 0 for the past 40 minutes` | `['2040-03-19T00:00:00']` | `[]` | `['duration:40 minutes']` | `v2_typed` | Numeric + duration phrase near known issue theme. | `40 minutes` should be duration signal; legacy 2040 date is misleading. |
| amb_032 | `1:00 pm is recognized but 1:00pm too` | `['2026-03-19T13:00:00', '2026-03-19T13:00:00']` | `[]` | `[]` | `` | Time formatting variants. |  |
| amb_033 | `June 2018` | `[]` | `[]` | `[]` | `both` | Incomplete date under strict mode. | Strict mode should reject incomplete month/year phrase. |
| amb_034 | `09/06/2018` | `['2018-09-06T00:00:00']` | `['2018-09-06T00:00:00']` | `['absolute:09/06/2018']` | `both` | Strict complete numeric date. | Strict complete numeric date should parse. |
| amb_035 | `19th day of May, 2015` | `['2015-05-19T00:00:00']` | `['2015-05-19T00:00:00']` | `['absolute:19th day of May, 2015']` | `both` | Ordinal day phrase under strict mode. | Strict ordinal day phrase should parse. |
| amb_036 | `On February 10, 2012, system event happened.` | `['2012-02-10T00:00:00']` | `['2012-02-10T00:00:00']` | `['absolute:February 10, 2012']` | `` | Mixed prose and valid date. |  |
| amb_037 | `report generated in 2004` | `[]` | `['2004-03-18T00:00:00']` | `['absolute:in 2004']` | `v2_compat` | Year-only parse behavior. | Year-only sentence can reasonably infer current month/day anchor if enabled. |
| amb_038 | `Wed Aug 05 12:00:00 EDT 2015` | `['2015-08-05T12:00:00']` | `[]` | `[]` | `` | Timezone abbreviation handling. |  |
| amb_039 | `11:59 PM PST` | `['2026-03-19T23:59:00']` | `[]` | `[]` | `` | Time + tz without explicit date. |  |
| amb_040 | `A unicode superscript like 12²/03/2020 appears in OCR.` | `['2020-03-19T00:00:00']` | `[]` | `[]` | `v2_compat` | Unicode-noise OCR style token. | OCR superscript noise should not force a legacy-style date hallucination. |
