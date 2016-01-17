import dateparser
from dateparser.timezone_parser import (
    _tz_offsets,
    local_tz_offset as my_local_os_tzoffset
)
import pytz
from datetime import datetime
import logging, sys
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)
import pytest

#
#  different semantic conversion meanings
#  for parsing a datetime_obj with tzinfo
#
from dateparser.timezone_parser import (
    # datetime_obj + timezone_offset - local_tz_offset
    convert_to_local_tz as default_convert_to_local_tz
)

def relative_day_convert_to_local_tz(datetime_obj, datetime_timedelta_offset):
    # move the day if the offset falls within calculation
    return datetime_obj + datetime_timedelta_offset

def current_day_convert_to_local_tz(datetime_obj, datetime_timedelta_offset):
    # don't move day, just hours
    return datetime_obj - datetime_timedelta_offset

def expected_convert_to_local_tz(datetime_obj, pytz_tzinfo_offset):
    # keep the day and time, just give it tzinfo dammit
    return pytz_tzinfo_offset.localize(datetime_obj)



@pytest.mark.parametrize('date_string, expected_datetime',[
    ['13/03/2014 cst', datetime(2014, 3, 12, 22, 0),]
])
def test_parse_with_default_convert(date_string, expected_datetime):
    datetime_obj = dateparser.parse(date_string)
    logger.debug("actual={} expected={}".format(datetime_obj,expected_datetime))

    assert datetime_obj == expected_datetime
    #
    # How and Why does dateparser.parse get that expected value?
    #
    # highlevel overview:
    # 1) get the datetime object for parsed date without tzinfo, so midnight
    # 2) then apply tzoffset which shifts it the correct tzoffset. though, which operator (sub,add) we use is important
    # https://github.com/scrapinghub/dateparser/blob/master/dateparser/date_parser.py#L182-L183
    # 3) then localize
    # https://github.com/scrapinghub/dateparser/blob/master/dateparser/timezone_parser.py#L18-L19
    #
    # step-by-step overview:
    # parse the datestring without tzinfo, so midnight is returned
    # step 1)
    datetime_midnight = dateparser.parse('13/03/2014')
    assert datetime_midnight == datetime(2014, 3, 13, 0, 0)
    # add the central tzoffset, we use subtraction operator
    # so we cancel out the -1 day offset
    # but subtract the hours from midnight of that same day 03/13/2014
    # so 24 - offset(18) gives us 6 hours
    # step 2)
    central_tzoffset = [i for i in _tz_offsets if i[0]=='CST'][0][1]['offset']
    datetime_central = datetime_midnight - central_tzoffset
    assert datetime_central == datetime(2014, 3, 13, 6, 0)
    # then localize to the operating system's tzoffset
    # here we use addition operator
    # so we end up subtracting the day but
    # adding the hours 03/12/2014
    # so 06:00 + 16:00 give us 22:00
    # step 3)
    datetime_local = datetime_central + my_local_os_tzoffset
    assert datetime_local == datetime(2014, 3, 12, 22, 0)
