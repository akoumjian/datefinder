import pytest
import pytz
import datefinder
import dateparser
from datetime import datetime
from unittest import mock
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('date_string, expected_date_string, expected_timezone_string', [
    ['01/01/2015 cst', '01/01/2015 ', 'US/Central'],
    ['12/31/2015 pst', '12/31/2015 ', 'US/Pacific'],
    ['13/03/2015 mst', '13/03/2015 ', 'US/Mountain'],
    ['11/20/2015 est', '11/20/2015 ', 'US/Eastern'],
    ['est cst 11/20/2015 pst mst', '  11/20/2015  ', 'US/Pacific'], # edge cases
    ['01/01/2015', '01/01/2015', '']
])
def test_find_and_replace_timezones(date_string, expected_date_string, expected_timezone_string):
    finder = datefinder.DateFinder()
    actual_date_string, actual_timezone_string = finder._find_and_replace_timezones(date_string)
    assert actual_date_string == expected_date_string
    assert actual_timezone_string == expected_timezone_string
