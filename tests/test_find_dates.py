import pytest
import datefinder
from datetime import datetime
import pytz
import sys
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)


@pytest.mark.parametrize('input_text, expected_date', [
    ## English Dates
    #('[Sept] 04, 2014.', datetime(2014, 9, 4)),
    ('Tuesday Jul 22, 2014', datetime(2014, 7, 22)),
    #('10:04am EDT', datetime(2012, 11, 13, 14, 4)),
    #('Friday', datetime(2012, 11, 9)),
    #('November 19, 2014 at noon', datetime(2014, 11, 19, 12, 0)),
    ('December 13, 2014 at midnight', datetime(2014, 12, 13, 0, 0)),
    #('Nov 25 2014 10:17 pm EST', datetime(2014, 11, 26, 3, 17)),
    #('Wed Aug 05 12:00:00 EDT 2015', datetime(2015, 8, 5, 16, 0)),
    #('April 9, 2013 at 6:11 a.m.', datetime(2013, 4, 9, 6, 11)),
    #('Aug. 9, 2012 at 2:57 p.m.', datetime(2012, 8, 9, 14, 57)),
    ('December 10, 2014, 11:02:21 pm', datetime(2014, 12, 10, 23, 2, 21)),
    #('8:25 a.m. Dec. 12, 2014', datetime(2014, 12, 12, 8, 25)),
    ('2:21 p.m., December 11, 2014', datetime(2014, 12, 11, 14, 21)),
    ('Fri, 12 Dec 2014 10:55:50', datetime(2014, 12, 12, 10, 55, 50)),
    #('20 Mar 2013 10h11', datetime(2013, 3, 20, 10, 11)),
    ('10:06am Dec 11, 2014', datetime(2014, 12, 11, 10, 6)),
    #('19 February 2013 year 09:10', datetime(2013, 2, 19, 9, 10)),

    # Numeric dates
    ('06-17-2014', datetime(2014, 6, 17)),
    ('13/03/2014', datetime(2014, 3, 13)),
    ('2016-02-04T20:16:26+00:00', datetime(2016, 2, 4, 20, 16, 26, tzinfo=pytz.utc)),
    #('11. 12. 2014, 08:45:39', datetime(2014, 11, 12, 8, 45, 39)),

    # dates from issue https://github.com/akoumjian/datefinder/issues/14
    #("i am looking for a date june 4th 1996 to july 3rd 2013",[]), # this is wrong, but make it pass to show the issue
    ("i am looking for a date june 4th 1996 so july 3rd 2013",[
        datetime(1996, 6, 4),
        datetime(2013, 7, 3)
    ]),
    ("october 27 1994 to be put into effect on june 1 1995",[
        datetime(1994, 10, 27),
        datetime(1995,  6,  1)
    ]),
    # Z dates with and without millis, from https://github.com/akoumjian/datefinder/issues/37
    ("2017-02-03T09:04:08.001Z", datetime(2017, 2, 3, 9, 4, 8, 1000, tzinfo=pytz.utc)),
    ("2017-02-03T09:04:08,00123Z", datetime(2017, 2, 3, 9, 4, 8, 1230, tzinfo=pytz.utc)),
    ("2017-02-03T09:04:08Z", datetime(2017, 2, 3, 9, 4, 8, tzinfo=pytz.utc)),
])
def test_find_date_strings(input_text, expected_date):
    if isinstance(expected_date,list):
        matches = list(datefinder.find_dates(input_text))
        assert matches == expected_date
    else:
        return_date = None
        for return_date in datefinder.find_dates(input_text):
            assert return_date == expected_date
        assert return_date is not None, 'Did not find date for test line: "{}"'.format(input_text) # handles dates that were never matched
