import pytest
import datefinder
import copy
import sys, logging

from datefinder.constants import REPLACEMENTS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

@pytest.mark.parametrize('date_string, expected_replaced_string, captures, expected_tz_string', [
    ('due on Tuesday Jul 22, 2014 eastern standard time',
    ' tuesday jul 22, 2014 eastern ',
     {'timezones':['EST']},
     'EST',
    )
])
def test_find_and_replace(date_string, expected_replaced_string, captures, expected_tz_string):
    dt = datefinder.DateFinder()
    expected_replacements = copy.copy(REPLACEMENTS)
    actual_date_string, actual_tz_string = dt._find_and_replace(date_string, captures)

    # assert that dt._find_and_replace did not mutate dt.REPLACEMENTS
    assert REPLACEMENTS == expected_replacements

    # assert the return values of dt._find_and_replace
    assert actual_date_string == expected_replaced_string
    assert actual_tz_string == expected_tz_string
