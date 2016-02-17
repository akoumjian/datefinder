import pytest
import datefinder
from dateutil import tz, parser
from datetime import datetime
try:
    from unittest import mock
except ImportError:
    import mock
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('date_string, expected_parse_arg, expected_captures, expected_date', [
    (
        'due on Tuesday Jul 22, 2014 eastern standard time',
        'tuesday jul 22 2014',
        { 'timezones': ['eastern'] },
        datetime(2014, 7, 22).replace(tzinfo=tz.gettz('EST'))
    ),
    (
        'Friday pAcific stanDard time',
        'friday',
        { 'timezones': ['pacific'] },
        parser.parse('friday').replace(tzinfo=tz.gettz('PST'))
    ),
    (
        '13/03/2014 Central Daylight Savings Time',
        '13/03/2014',
        { 'timezones': ['central'] },
        datetime(2014, 3, 13).replace(tzinfo=tz.gettz('CST'))
    ),
    # assert dateutil.parse successfully
    # handles tz-naive date strings
    # and returns naive datetime objects
    (
        ' on 12/24/2015 at 2pm ',
        '12/24/2015 at 2pm',
        { 'timezones': [] },
        datetime(2015, 12, 24, 14, 0)
    ),
    # test a tz abbreviation that
    # dateutil.tz.gettz cannot find on ANY operating system
    # and will return None for
    (
        ' on 11-20-2015 6pm NATZABBRV ', # stands for 'not a timezone abbreviation'
        '11-20-2015 6pm',
        { 'timezones': ['NATZABBRV'] },
        datetime(2015, 11, 20, 18, 0)
    ),
    # test a tz abbreviation that
    # dateutil.tz.gettz cannot find on ANY operating system
    # and will return None for
    (
        ' on 11-20-2015 6am NATZABBRV ', # stands for 'not a timezone abbreviation'
        '11-20-2015 6am',
        { 'timezones': ['NATZABBRV'] },
        datetime(2015, 11, 20, 6, 0)
    )
])
def test_parse_date_string_find_replace(date_string, expected_parse_arg, expected_captures, expected_date):
    dt = datefinder.DateFinder()
    with mock.patch.object(parser, 'parse', wraps=parser.parse) as spy:
        actual_datetime = dt.parse_date_string(date_string, expected_captures)
        spy.assert_called_with(expected_parse_arg)
        logger.debug("acutal={}  expected={}".format(actual_datetime, expected_date))
        assert actual_datetime == expected_date
