import pytest
import datefinder
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

#TODO: many more TZINFO examples

@pytest.mark.parametrize('date_string, expected_match_date_string', [
    ['March 20, 2015 3:30 pm GMT ', 'March 20, 2015 3:30 pm GMT'],
    ['March 20, 2015 3:30 pm ACWDT in the parking lot', 'March 20, 2015 3:30 pm ACWDT'],
    ['blah blah March 20, 2015 3pm MADMT for some thing', 'March 20, 2015 3pm MADMT'],
    ['we need it back on Friday 2p.m. central standard time', 'on Friday 2p.m. central standard time'],
    ['the big fight at 2p.m. mountain standard time on ufc.com', 'at 2p.m. mountain standard time on']
])
def test_extract_date_strings(date_string, expected_match_date_string):
    dt = datefinder.DateFinder()
    for actual_date_string, indexes, captures in dt.extract_date_strings(date_string):
        logger.debug("acutal={}  expected={}".format(actual_date_string, expected_match_date_string))
        assert actual_date_string == expected_match_date_string
        assert len(captures.get('timezones',[])) > 0
