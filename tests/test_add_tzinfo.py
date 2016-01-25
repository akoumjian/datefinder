import pytest
from dateutil import tz
import datefinder
from datetime import datetime
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('naive_datetime_obj, timezone_string', [
    [datetime(2015,3,13,0,0), 'PST'],
    [datetime(2015,3,13,23,59,59,1), 'MST'],
    [datetime(2015,3,13,15,20), 'CST'],
    [datetime(2015,3,13,20,25), 'EST']
])
def test_add_tzinfo(naive_datetime_obj, timezone_string):
    expected_datetime = naive_datetime_obj.replace(tzinfo=tz.gettz(timezone_string))
    finder = datefinder.DateFinder()
    actual_datetime = finder._add_tzinfo(naive_datetime_obj,timezone_string)
    assert actual_datetime == expected_datetime
