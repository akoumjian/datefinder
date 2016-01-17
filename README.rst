datefinder
==========

A module for locating dates inside text. Use this package to extract all sorts 
of date like strings from a document and turn them into datetime objects.

This module finds the likely datetime strings and then uses the excellent 
`dateparser <https://github.com/scrapinghub/dateparser>`_ package to convert 
to the datetime object.

Installation
------------

```
pip install datefinder


How to Use
----------

.. code-block:: python

    >>> import datefinder
    >>> matches = datefinder.find_dates(string_with_dates)

    >>> for match in matches:
        print match

    2016-01-13 11:00:00
    2016-01-05 00:00:00
    2014-01-02 00:00:00
    2014-01-02 00:00:00

