import pytest
import datefinder
import dateparser
from dateutil import tz
from datetime import datetime
try:
    from unittest import mock
except ImportError:
    import mock
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('date_string, expected_replace_string, expected_parse_arg, expected_captures, expected_date', [
    ## English Dates
    ('due on Tuesday Jul 22, 2014 eastern standard time',
     'tuesday jul 22 2014 est',
     'tuesday jul 22 2014',
     {'timezones': ['eastern']},
     datetime(2014, 7, 22).replace(tzinfo=tz.gettz('EST'))
    ),
    ('Friday pAcific stanDard time',
     'friday pst standard time',
     'friday',
     {'timezones':['pacific']},
     dateparser.parse('friday').replace(tzinfo=tz.gettz('PST'))
    ),

    # Numeric dates
    ('13/03/2014 Central Daylight Savings Time',
     '13/03/2014 cst daylight savings time',
     '13/03/2014',
     {'timezones':['central']},
     datetime(2014, 3, 13).replace(tzinfo=tz.gettz('CST'))
    ),
    (' on 12/24/2015 at 2pm ',
     'on 12/24/2015 at 2pm',
     '12/24/2015 at 2pm',
     {'timezones':[]},
     datetime(2015, 12, 24, 14, 0) # we're making sure it's naive
    ),
    (' on 11-20-2015 4pm IRST ', # test an abbreviation that tz.gettz will return None for
     'on 11-20-2015 4pm IRST',
     '11-20-2015 4pm irst',
     {'timezones':['CST']},
     datetime(2015, 11, 20, 14, 0) # we're making sure it's naive
    )
])
def test_parse_date_string_find_replace(date_string, expected_replace_string, expected_parse_arg, expected_captures, expected_date):
    dt = datefinder.DateFinder()
    with mock.patch.object(dateparser, 'parse', wraps=dateparser.parse) as spy:
        actual_datetime = dt.parse_date_string(date_string, expected_captures)
        spy.assert_called_with(expected_parse_arg)
        logger.debug("acutal={}  expected={}".format(actual_datetime, expected_date))
        assert actual_datetime == expected_date
