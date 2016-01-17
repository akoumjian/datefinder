import pytest
import datefinder
import dateparser
import pytz
from datetime import datetime
from unittest import mock
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

#TODO: many more TZINFO examples

@pytest.mark.parametrize('date_string, expected_match_date_string', [
    ['March 20, 2015 3:30 pm GMT ', 'March 20, 2015 3:30 pm GMT'],
    ['we need it back on Friday 2pm eastern standard time', 'on Friday 2pm eastern standard time'],
])
def test_extract_date_strings(date_string, expected_match_date_string):
    dt = datefinder.DateFinder()
    for actual_date_string, indexes, captures in dt.extract_date_strings(date_string):
        logger.debug("acutal={}  expected={}".format(actual_date_string, expected_match_date_string))
        assert actual_date_string == expected_match_date_string
        assert len(captures.get('timezones',[])) > 0
