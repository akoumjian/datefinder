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


A python module for locating dates inside text. Use this package to extract all sorts 
of date like strings from a document and turn them into datetime objects.

This module finds the likely datetime strings and then uses  
`dateutil` to convert to the datetime object.


Installation
------------

**With pip**

.. code-block:: sh

    pip install datefinder

**Note:  I do not publish the version on conda forge and cannot verify its integrity.**

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

    In [3]: matches = datefinder.find_dates(string_with_dates, locale="en_US")

    In [4]: for match in matches:
       ...:     print match
       ...:
    2017-01-04 20:00:00
    2005-01-15 00:00:00

**Note: The `locale` parameter is optional. If you do not specify a locale, the default is `en_US`.**

Demo
----

-  🎞️ `Video demo`_ by Calmcode.io. :star: 

.. _Video demo: https://calmcode.io/shorts/datefinder.py.html

