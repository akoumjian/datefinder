datefinder - extract dates from text
====================================

.. image:: https://github.com/akoumjian/datefinder/actions/workflows/python-package.yml/badge.svg
    :target: https://github.com/akoumjian/datefinder
    :alt: Build Status

.. image:: https://img.shields.io/pypi/dm/datefinder.svg
    :target: https://pypi.python.org/pypi/datefinder/
    :alt: pypi downloads per day

.. image:: https://img.shields.io/pypi/v/datefinder.svg
    :target: https://pypi.python.org/pypi/datefinder
    :alt: pypi version


A python module for locating dates inside text. Use this package to extract date-like
strings from documents and turn them into useful datetime/temporal objects.

As of ``1.0.0``, ``find_dates(...)`` defaults to the v2 compatibility engine.
The original engine remains available as ``find_dates_legacy(...)``.


Installation
------------

Requires Python 3.9+.

**With pip**

.. code-block:: sh

    pip install datefinder

If a compatible prebuilt wheel is unavailable for your platform, pip will build
from source and requires a Rust toolchain.

**Note:  I do not publish the version on conda forge and cannot verify its integrity.**

What You Can Do With datefinder
-------------------------------

``datefinder`` is a Python date parser for extracting dates from unstructured text.
It is useful when your data is not already normalized, for example:

- emails, tickets, and support conversations
- contracts, policies, and legal text
- logs, reports, and markdown/wiki pages
- scraped HTML and mixed-format documents

You can use it to:

- parse explicit calendar dates like ``January 4th, 2017`` or ``2024-11-03 18:00``
- parse relative expressions like ``tomorrow``, ``yesterday``, and ``in 3 days``
- parse multiple date formats in one pass (month-name, slash, ISO, hyphen)
- anchor relative parsing to a reference/base date
- return either compatibility datetimes or typed structured match objects

In short: if you need to find and parse dates from text in Python, especially
inside large documents with mixed formatting, ``datefinder`` is designed for that.

Common workflows:

- migration from legacy date extraction code:
  use ``find_dates_legacy(...)`` for parity, then move to ``find_dates(...)``
- modern typed extraction:
  use ``extract(...)`` to get match kinds, spans, confidence, and structured values
- command line processing:
  use ``datefinder --engine extract --json`` in shell pipelines

Example (Python):

.. code-block:: python

    import datefinder
    from datetime import datetime, timezone

    text = "Meeting tomorrow; launch on 2024-11-03 18:00 UTC."
    ref = datetime(2026, 3, 19, 12, 0, tzinfo=timezone.utc)

    # Compatibility datetimes
    print(list(datefinder.find_dates(text, base_date=ref)))

    # Typed extraction
    for match in datefinder.extract(text, reference_dt=ref):
        print(match.kind, match.text, match.value)

Example (CLI):

.. code-block:: sh

    datefinder --reference "2026-03-19T12:00:00+00:00" --json \
      "Meeting tomorrow; launch on 2024-11-03 18:00 UTC."

How to Use
----------


.. code-block:: python

    In [1]: string_with_dates = """
       ...: ...
       ...: entries are due by January 4th, 2017 at 8:00pm
       ...: ...
       ...: created 01/15/2005 by ACME Inc. and associates.
       ...: ...
       ...: """

    In [2]: import datefinder

    In [3]: matches = datefinder.find_dates(string_with_dates)

    In [4]: for match in matches:
       ...:     print(match)
       ...:
    2017-01-04 20:00:00
    2005-01-15 00:00:00

CLI
---

The package now includes a CLI entrypoint:

.. code-block:: sh

    datefinder --json "tomorrow and 2024-12-10"

You can also run it as a module:

.. code-block:: sh

    python -m datefinder --engine extract --json --reference "2026-03-18T00:00:00+00:00" "in 3 days"

Engine options:

- ``default``: ``find_dates(...)`` (v2 compatibility default)
- ``legacy``: ``find_dates_legacy(...)``
- ``compat``: ``find_dates_compat(...)``
- ``extract``: typed ``extract(...)`` output

Common options:

- ``--reference <ISO8601>``: anchor for relative dates/times (equivalent to ``base_date``/``reference_dt``)
- ``--first {month,day,year}``: disambiguation for numeric dates
- ``--strict``: stricter matching
- ``--json`` / ``--pretty``: machine-readable output
- ``--source`` / ``--index``: include source span details (``default``/``legacy`` only)
- ``--locale <code>``: locale hint for ``extract`` (repeatable)
- ``--no-month-only``: disable month-only inference (``"May" -> YYYY-05-01``)
- ``--compact-numeric``: enable compact numeric parsing (e.g. ``20240315``)
- ``--no-multiline``: disable cross-line matching

Examples:

.. code-block:: sh

    # default engine (v2 compatibility), anchored relative parsing
    datefinder --reference "2026-03-19T12:00:00+00:00" --json "tomorrow and 2024-12-10"

    # explicit legacy behavior, include source text and indices
    datefinder --engine legacy --source --index --json "created 01/15/2005 by ACME"

    # typed extract output with locale hints
    datefinder --engine extract --locale en --locale fr --pretty --json "in 3 days and demain"

    # read long input from stdin
    cat document.txt | datefinder --engine extract --json

Relative and duration values:

- ``default`` / ``legacy`` / ``compat`` engines emit datetimes.
- ``extract`` emits typed values:
  - ``relative`` includes both ``resolved_datetime`` and ``delta_seconds``.
  - ``duration`` includes ``total_seconds`` and normalized components.


V2 Typed API
------------

This repository includes a v2 extraction API with typed match objects and
first-class support for relative expressions and durations.

.. code-block:: python

    import datefinder
    from datetime import datetime, timezone

    matches = datefinder.extract(
        "in 3 days we deploy on 2024-11-03 18:00",
        reference_dt=datetime.now(timezone.utc),
    )
    for m in matches:
        print(m.kind, m.text, m.value)

There is also a compatibility helper for migrating existing code:

.. code-block:: python

    for dt in datefinder.find_dates_compat("tomorrow and 2024-12-10"):
        print(dt)

If you need the original parser behavior exactly:

.. code-block:: python

    for dt in datefinder.find_dates_legacy("April 9, 2013 at 6:11 a.m."):
        print(dt)

Rust kernel source is under ``rust/datefinder-kernel`` and is required for v2/default
runtime behavior.

Rust Portability
----------------

- Compiled Rust extensions are platform-specific, they do not run on every system by default.
- Release wheel targets:
  - Linux glibc: ``x86_64`` and ``aarch64`` (manylinux2014)
  - Linux musl: ``x86_64`` and ``aarch64`` (musllinux_1_2)
  - macOS: ``x86_64`` and ``arm64``
  - Windows: ``x86_64``
- If no compatible wheel is available, ``pip`` builds from source and requires a Rust toolchain.


Conformance and Ambiguity Reports
---------------------------------

Build a reproducible corpus from legacy tests and generate differential reports
between legacy behavior and ``find_dates_compat``:

.. code-block:: sh

    python scripts/build_conformance_corpus.py
    python scripts/diff_legacy_v2.py

This writes:

- ``conformance/legacy_parity_cases.jsonl``
- ``conformance/reports/legacy_v2_diff_report.md``
- ``conformance/reports/ambiguity_showcase.md``
- ``conformance/reports/behavior_change_changelog.md``

The ambiguity showcase also supports interpretation judgments in
``conformance/interpretation_judgments.jsonl`` to assess whether legacy
behavior is semantically preferable for ambiguous real-world cases.

See also:

- ``CONTRIBUTING.md`` for developer setup and validation commands.
- ``RELEASE.md`` for release checklist.


Benchmark Snapshot
------------------

The command below generates a local benchmark snapshot comparing:

- ``v2``: ``datefinder.extract(...)``
- ``legacy``: ``datefinder.find_dates_legacy(...)``
- ``dateparser``: ``dateparser.search.search_dates``
- ``duckling_http``: Duckling ``POST /parse``

Run:

.. code-block:: sh

    # optional: run duckling locally
    docker run --rm -p 8000:8000 rasa/duckling:latest

    python bench/bench_readme_compare.py \
      --iterations-small 12 \
      --iterations-large 2

Latest local snapshot (2026-03-19 UTC):

+------------------+--------+---------------+-------------------+----------------------+-------------------------+---------------+------------------+----------------------+
| dataset          | size   | v2 median (s) | legacy median (s) | dateparser median (s)| duckling_http median (s)| v2 vs legacy  | v2 vs dateparser | v2 vs duckling_http  |
+==================+========+===============+===================+======================+=========================+===============+==================+======================+
| core_corpus      | 498    | 0.000236      | 0.003042          | 0.180596             | 0.050266                | 12.91x        | 766.74x          | 213.41x              |
+------------------+--------+---------------+-------------------+----------------------+-------------------------+---------------+------------------+----------------------+
| seattle_html_76k | 74838  | 0.037436      | 0.281466          | 0.771712             | 25.353595               | 7.52x         | 20.61x           | 677.24x              |
+------------------+--------+---------------+-------------------+----------------------+-------------------------+---------------+------------------+----------------------+
| test_data_560k   | 552301 | 0.239391      | 2.840845          | n/a                  | n/a                     | 11.87x        | n/a              | n/a                  |
+------------------+--------+---------------+-------------------+----------------------+-------------------------+---------------+------------------+----------------------+

Notes:

- ``n/a`` means unavailable/failed for that dataset in this run.
- ``dateparser``/``duckling_http`` are skipped by default for documents larger than 200k bytes unless forced.
- Match counts differ across engines because behavior targets differ (e.g. relative/duration support and false-positive tolerance).
- Results are hardware/environment dependent and should be treated as directional.

Release Notes
-------------

- ``docs/releases/1.0.0.md`` documents GA scope, behavior changes, and migration.
