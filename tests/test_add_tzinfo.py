import pytest
import pytz
import datefinder
import dateparser
from datetime import datetime
from unittest import mock
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('naive_datetime_obj, timezone_string', [
    [datetime(2015,3,13,0,0), 'US/Pacific'],
    [datetime(2015,3,13,23,59,59,1), 'US/Mountain'],
    [datetime(2015,3,13,15,20), 'US/Central'],
    [datetime(2015,3,13,20,25), 'US/Eastern']
])
def test_add_tzinfo(naive_datetime_obj, timezone_string):
    expected_datetime = naive_datetime_obj.replace(tzinfo=pytz.timezone(timezone_string))
    finder = datefinder.DateFinder()
    actual_datetime = finder._add_tzinfo(naive_datetime_obj,timezone_string)
    assert actual_datetime == expected_datetime
