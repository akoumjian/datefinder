import pytest
import datefinder
from datetime import datetime
import pytz
import sys
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

today = datetime.today()


@pytest.mark.parametrize(
    ("input_text", "expected_date", "first"),
    [
        ## English Dates
        ("Tuesday Jul 22, 2014", datetime(2014, 7, 22), "month"),
        ("April 9, 2013 at 6:11 a.m.", datetime(2013, 4, 9, 6, 11), "month"),
        ("Aug. 9, 2012 at 2:57 p.m.", datetime(2012, 8, 9, 14, 57), "month"),
        ("December 10, 2014, 11:02:21 pm", datetime(2014, 12, 10, 23, 2, 21), "month"),
        ("8:25 a.m. Dec. 12, 2014", datetime(2014, 12, 12, 8, 25), "month"),
        ("2:21 p.m., December 11, 2014", datetime(2014, 12, 11, 14, 21), "month"),
        ("Fri, 12 Dec 2014 10:55:50", datetime(2014, 12, 12, 10, 55, 50), "month"),
        ("10:06am Dec 11, 2014", datetime(2014, 12, 11, 10, 6), "month"),
        ("September 2nd, 1998", datetime(1998, 9, 2), "month"),
        (
            "May 5, 2010 to July 10, 2011",
            [datetime(2010, 5, 5), datetime(2011, 7, 10)],
            "month",
        ),
        # Numeric dates
        ("06-17-2014", datetime(2014, 6, 17), "month"),
        ("13/03/2014", datetime(2014, 3, 13), "month"),
        (
            "2016-02-04T20:16:26+00:00",
            datetime(2016, 2, 4, 20, 16, 26, tzinfo=pytz.utc),
            "month",
        ),
        (
            "2017-02-03T09:04:08Z to 2017-02-03T09:04:09Z",
            [
                datetime(2017, 2, 3, 9, 4, 8, tzinfo=pytz.utc),
                datetime(2017, 2, 3, 9, 4, 9, tzinfo=pytz.utc),
            ],
            "month",
        ),
        # dates from issue https://github.com/akoumjian/datefinder/issues/14
        (
            "i am looking for a date june 4th 1996 to july 3rd 2013",
            [datetime(1996, 6, 4), datetime(2013, 7, 3)],
            "month",
        ),
        (
            "october 27 1994 to be put into effect on june 1 1995",
            [datetime(1994, 10, 27), datetime(1995, 6, 1)],
            "month",
        ),
        # Simple date range
        (
            "31/08/2012 to 30/08/2013",
            [datetime(2012, 8, 31), datetime(2013, 8, 30)],
            "month",
        ),
        # Z dates with and without millis, from https://github.com/akoumjian/datefinder/issues/37
        (
            "2017-02-03T09:04:08.001Z",
            datetime(2017, 2, 3, 9, 4, 8, 1000, tzinfo=pytz.utc),
            "month",
        ),
        (
            "2017-02-03T09:04:08,00123Z",
            datetime(2017, 2, 3, 9, 4, 8, 1230, tzinfo=pytz.utc),
            "month",
        ),
        (
            "2017-02-03T09:04:08Z",
            datetime(2017, 2, 3, 9, 4, 8, tzinfo=pytz.utc),
            "month",
        ),
        # Year only strings, from https://github.com/akoumjian/datefinder/issues/96
        (
            "Dutta is the recipient of Femina Miss India Universe title in 2004.",
            datetime(2004, today.month, today.day),
            "month",
        ),
        (
            'she said that she hit depression after being traumatized on the sets of "Horn OK" in 2008.',
            datetime(2008, today.month, today.day),
            "month",
        ),
        # https://github.com/akoumjian/datefinder/issues/63
        ("12th day of December, 2001", datetime(2001, 12, 12), "month"),
        ("01/02/03", datetime(2003, 1, 2, 0, 0, 0, 0), "month"),
        ("01/02/03", datetime(2003, 2, 1, 0, 0, 0, 0), "day"),
        ("01/02/03", datetime(2001, 2, 3, 0, 0, 0, 0), "year"),
        ("02/05/2020", datetime(2020, 2, 5, 0, 0, 0, 0), "month"),
        ("02/05/2020", datetime(2020, 5, 2, 0, 0, 0, 0), "day"),
    ],
)
def test_find_date_strings(input_text, expected_date, first):
    if isinstance(expected_date, list):
        matches = list(datefinder.find_dates(input_text, first=first))
        assert matches == expected_date
    else:
        return_date = None
        for return_date in datefinder.find_dates(input_text, first=first):
            assert return_date == expected_date
        assert return_date is not None, 'Did not find date for test line: "{}"'.format(
            input_text
        )  # handles dates that were never matched
