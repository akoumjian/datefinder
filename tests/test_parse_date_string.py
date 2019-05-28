import pytest
import warnings
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


@pytest.mark.parametrize('date_string, expected_parse_args, expected_parse_kwargs, expected_captures, is_day_first, expected_date', [
    (
        'due on Tuesday Jul 22, 2014 eastern standard time',
        ['tuesday jul 22, 2014',],
        {'default': None, 'dayfirst': False},
        { 'timezones': ['eastern'] },
        False,
        datetime(2014, 7, 22).replace(tzinfo=tz.gettz('EST'))
    ),
    (
        'Friday pAcific stanDard time',
        ['friday',],
        {'default': None, 'dayfirst': False},
        { 'timezones': ['pacific'] },
        False,
        parser.parse('friday').replace(tzinfo=tz.gettz('PST'))
    ),
    (
        '13/03/2014 Central Daylight Savings Time',
        ['13/03/2014',],
        {'default': None, 'dayfirst': False},
        { 'timezones': ['central'] },
        False,
        datetime(2014, 3, 13).replace(tzinfo=tz.gettz('CST'))
    ),
    # assert dateutil.parse successfully
    # handles tz-naive date strings
    # and returns naive datetime objects
    (
        '12/24/2015 at 2pm',
        ['12/24/2015 at 2pm',],
        {'default': None, 'dayfirst': False},
        { 'timezones': [] },
        False,
        datetime(2015, 12, 24, 14, 0)
    ),
    (
        '12/01/2015 at 2pm',
        ['12/01/2015 at 2pm',],
        {'default': None, 'dayfirst': True},
        { 'timezones': [] },
        True,
        datetime(2015, 1, 12, 14, 0)
    ),
])
def test_parse_date_string_find_replace(date_string, expected_parse_args, expected_parse_kwargs, expected_captures, is_day_first, expected_date):
    dt = datefinder.DateFinder()
    with mock.patch.object(parser, 'parse', wraps=parser.parse) as spy:
        actual_datetime = dt.parse_date_string(date_string, expected_captures, is_day_first)
        spy.assert_called_with(*expected_parse_args, **expected_parse_kwargs)
        logger.debug("actual={}  expected={}".format(actual_datetime, expected_date))
        assert actual_datetime == expected_date

@pytest.mark.parametrize('date_string, expected_parse_arg, expected_captures, expected_date', [
    # test a tz abbreviation that
    # dateutil.tz.gettz cannot find
    # and will return None for
    (
        ' on 11-20-2015 6pm CST ',
        '11-20-2015 6pm',
        { 'timezones': ['CST'] },
        datetime(2015, 11, 20, 18, 0)
    ),
    # test a tz abbreviation that
    # dateutil.tz.gettz cannot find
    # and will return None for
    (
        ' on 11-20-2015 6am IRST ',
        '11-20-2015 6am',
        { 'timezones': ['IRST'] },
        datetime(2015, 11, 20, 6, 0)
    )
])
def test_parse_date_string_find_replace_nonexistent_tzinfo(date_string, expected_parse_arg, expected_captures, expected_date):
    '''
    mimic what happens when dateutil tries
    to find a non-existent tzinfo string
    because some operating systems might resolve 'CST' and 'IRST' this should raise a warning.

    :param date_string:
    :param expected_parse_arg:
    :param expected_captures:
    :param expected_date:
    :return:
    '''
    with pytest.warns(parser.UnknownTimezoneWarning):
        warnings.simplefilter('always')
        dt = datefinder.DateFinder()
        actual_datetime = dt.parse_date_string(date_string, expected_captures)
        logger.debug("actual={}  expected={}".format(actual_datetime, expected_date))
        assert actual_datetime == expected_date

# @pytest.mark.parametrize('date_string, expected_exception', [
#     # assert dateutil.parser.parse
#     # throws ValueError on bad date string input
#     (
#         'to barf',
#         ValueError
#     ),
# ])
# def test_dateutil_parse_throws_value_error(date_string, expected_exception):
#     dt = datefinder.DateFinder()
#     pytest.raises(expected_exception, dt.parse_date_string, *[date_string], **{'captures':{}})
