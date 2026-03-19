# Behavior Change Changelog

This document is generated from ambiguity scenarios plus interpretation judgments.

## v2 Compatibility Improvements Over Legacy

## amb_005
- Text: `results = 3.8, 10`
- Legacy: `['2026-03-10T00:00:00']`
- v2_compat: `[]`
- Why: `results = 3.8, 10` is typically not a date in strict extraction contexts.

## amb_007
- Text: `French 75 is my favorite cocktail.`
- Legacy: `['2075-03-19T00:00:00']`
- v2_compat: `[]`
- Why: `French 75` should not infer year 2075.

## amb_008
- Text: `pre-qualification may proceed after review.`
- Legacy: `['2026-05-19T00:00:00']`
- v2_compat: `[]`
- Why: `pre-qualification may` should not infer a month date.

## amb_011
- Text: `9/15/27 144A`
- Legacy: `[]`
- v2_compat: `['2027-09-15T00:00:00']`
- Why: `9/15/27 144A` should still recover the date token.

## amb_013
- Text: `tomorrow at noon`
- Legacy: `[]`
- v2_compat: `['2026-03-19T12:00:00']`
- Why: Relative date phrase should be interpreted as relative datetime.

## amb_014
- Text: `in 2 weeks we launch`
- Legacy: `['2026-03-02T00:00:00']`
- v2_compat: `['2026-04-01T12:00:00']`
- Why: `in 2 weeks` should be relative, not a month/day fallback.

## amb_015
- Text: `20 days ago`
- Legacy: `[]`
- v2_compat: `['2026-02-26T12:00:00']`
- Why: `20 days ago` should resolve relative to reference date.

## amb_017
- Text: `hoy cerramos el trimestre`
- Legacy: `[]`
- v2_compat: `['2026-03-18T12:00:00']`
- Why: Spanish relative keyword should resolve as relative date.

## amb_018
- Text: `mañana enviaremos el contrato`
- Legacy: `[]`
- v2_compat: `['2026-03-19T12:00:00']`
- Why: Spanish tomorrow keyword should resolve as relative date.

## amb_020
- Text: `aujourd'hui est la date limite`
- Legacy: `[]`
- v2_compat: `['2026-03-18T12:00:00']`
- Why: French today keyword should resolve as relative date.

## amb_021
- Text: `heute ist der stichtag`
- Legacy: `[]`
- v2_compat: `['2026-03-18T12:00:00']`
- Why: German today keyword should resolve as relative date.

## amb_022
- Text: `morgen liefern wir`
- Legacy: `[]`
- v2_compat: `['2026-03-19T12:00:00']`
- Why: German tomorrow keyword should resolve as relative date.

## amb_023
- Text: `hoje fechamos o trimestre`
- Legacy: `[]`
- v2_compat: `['2026-03-18T12:00:00']`
- Why: Portuguese today keyword should resolve as relative date.

## amb_024
- Text: `amanhã revisaremos o relatório`
- Legacy: `[]`
- v2_compat: `['2026-03-19T12:00:00']`
- Why: Portuguese tomorrow keyword should resolve as relative date.

## amb_025
- Text: `oggi è la scadenza`
- Legacy: `[]`
- v2_compat: `['2026-03-18T12:00:00']`
- Why: Italian today keyword should resolve as relative date.

## amb_026
- Text: `domani inviamo i documenti`
- Legacy: `[]`
- v2_compat: `['2026-03-19T12:00:00']`
- Why: Italian tomorrow keyword should resolve as relative date.

## amb_027
- Text: `20 marzo 2015`
- Legacy: `[]`
- v2_compat: `['2015-03-20T00:00:00']`
- Why: Day-first Romance month-name date should parse.

## amb_037
- Text: `report generated in 2004`
- Legacy: `[]`
- v2_compat: `['2004-03-18T00:00:00']`
- Why: Year-only sentence can reasonably infer current month/day anchor if enabled.

## amb_040
- Text: `A unicode superscript like 12²/03/2020 appears in OCR.`
- Legacy: `['2020-03-19T00:00:00']`
- v2_compat: `[]`
- Why: OCR superscript noise should not force a legacy-style date hallucination.

## v2 Typed Semantic Additions

## amb_016
- Text: `we need a 20 day notice period`
- Legacy: `[]`
- v2_typed: `['duration:20 day']`
- Why: Duration phrase is useful as duration object even if not legacy datetime.

## amb_019
- Text: `dans 2 jours on valide`
- Legacy: `['2026-03-02T00:00:00']`
- v2_typed: `['duration:2 jours']`
- Why: French `dans 2 jours` is best represented as relative or duration, not spurious absolute date.

## amb_031
- Text: `CR is 0 for the past 40 minutes`
- Legacy: `['2040-03-19T00:00:00']`
- v2_typed: `['duration:40 minutes']`
- Why: `40 minutes` should be duration signal; legacy 2040 date is misleading.

## Stable Behaviors (Both)

- `amb_001` `01/02/03` -> `['2003-01-02T00:00:00']` (Ambiguous numeric date should follow caller 'first' preference; both agree.)
- `amb_002` `01/02/03` -> `['2003-02-01T00:00:00']` (Ambiguous numeric date should follow caller 'first' preference; both agree.)
- `amb_003` `01/02/03` -> `['2001-02-03T00:00:00']` (Ambiguous numeric date should follow caller 'first' preference; both agree.)
- `amb_006` `This is to inform you that an amount of Rs. 123.45 has been debited.` -> `[]` (Money should not parse as date in this sentence.)
- `amb_009` `Date: Tue, 23 Apr 1996 13:28:27 -0400` -> `['1996-04-23T17:28:27']` (RFC822-like timestamp should resolve with full time/offset context.)
- `amb_010` `2023-10-04 decision` -> `['2023-10-04T00:00:00']` (ISO date adjacent to token should still parse.)
- `amb_012` `25/7//2023` -> `[]` (Malformed separators should not parse.)
- `amb_028` `March 20, 2015` -> `['2015-03-20T00:00:00']` (Canonical month-name date should parse.)
- `amb_029` `31/08/2012 to 30/08/2013` -> `['2012-08-31T00:00:00', '2013-08-30T00:00:00']` (Simple date range text should parse both endpoints.)
- `amb_030` `2017-02-03T09:04:08Z to 2017-02-03T09:04:09Z` -> `['2017-02-03T09:04:08', '2017-02-03T09:04:09']` (ISO UTC timestamps should parse with second precision.)
- `amb_033` `June 2018` -> `[]` (Strict mode should reject incomplete month/year phrase.)
- `amb_034` `09/06/2018` -> `['2018-09-06T00:00:00']` (Strict complete numeric date should parse.)
- `amb_035` `19th day of May, 2015` -> `['2015-05-19T00:00:00']` (Strict ordinal day phrase should parse.)
