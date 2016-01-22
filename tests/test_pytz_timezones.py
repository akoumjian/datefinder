import pytest
import datefinder
import dateparser
from datetime import datetime
from unittest import mock
from dateutil import tz
import pytz
import sys, logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

def test_pytz_get_timezone_for_all_patterns():
    """
    determine which pattern matching tz_strings
    pytz.timezone will not handle

    :warning: currently tz.gettz only matches 14 of regex timezones of our ~400
    [ GOOD MATCHES ]: ['PST', 'EST', 'MST', 'CET', 'EET', 'EST', 'GMT', 'HST', 'MET', 'MST', 'PDT', 'PST', 'UTC', 'WET']
    """
    bad_tz_strings = []
    good_tz_strings = []
    finder = datefinder.DateFinder()
    test_tz_strings = finder.NA_TIMEZONES_PATTERN.split('|') + finder.TIMEZONES_PATTERN.split('|\s')
    for tz_string in test_tz_strings:
        if tz_string in finder.TIMEZONE_REPLACEMENTS.keys():
            tz_string = finder.TIMEZONE_REPLACEMENTS[tz_string]
        try:
            tz_object = pytz.timezone(tz_string.replace('\s',''))
        except pytz.UnknownTimeZoneError:
            bad_tz_strings.append(tz_string)
            continue

        good_tz_strings.append(tz_string)
    logger.debug("[ BAD TZINFO ]: {}".format(bad_tz_strings))
    logger.debug("[ GOOD TZINFO ]: {}".format(good_tz_strings))
    #assert len(bad_tz_strings) == 0


