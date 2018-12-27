from dateutil import tz
import sys, logging

from datefinder.constants import NA_TIMEZONES_PATTERN, TIMEZONES_PATTERN, TIMEZONE_REPLACEMENTS

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

def test_tz_gettz_for_all_patterns():
    """
    determine which pattern matching tz_strings
    dateutil.tz.gettz will not handle

    :warning: currently tz.gettz only matches 14 of regex timezones of our ~400
    [ GOOD MATCHES ]: ['PST', 'EST', 'MST', 'CET', 'EET', 'EST', 'GMT', 'HST', 'MET', 'MST', 'PDT', 'PST', 'UTC', 'WET']
    """
    bad_tz_strings = []
    good_tz_strings = []
    test_tz_strings = NA_TIMEZONES_PATTERN.split('|') + TIMEZONES_PATTERN.split(r'|\s')
    for tz_string in test_tz_strings:
        if tz_string in TIMEZONE_REPLACEMENTS.keys():
            tz_string = TIMEZONE_REPLACEMENTS[tz_string]
        tz_object = tz.gettz(tz_string.replace(r'\s',''))
        if tz_object is None:
            bad_tz_strings.append(tz_string)
        else:
            good_tz_strings.append(tz_string)
    logger.debug("[ BAD TZINFO ]: {}".format(bad_tz_strings))
    logger.debug("[ GOOD TZINFO ]: {}".format(good_tz_strings))
    #assert len(bad_tz_strings) == 0


