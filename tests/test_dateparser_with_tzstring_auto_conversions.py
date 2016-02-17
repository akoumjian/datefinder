# import re
# import pytz
# from datetime import datetime
# import dateparser
# from dateparser.timezone_parser import (
#     _tz_offsets,
#     local_tz_offset as my_local_os_tzoffset
# )
# import logging, sys
# logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
# logger = logging.getLogger(__name__)
# import pytest


# @pytest.mark.parametrize('date_string, expected_datetime',[
#     # assumes your /etc/localtime -> /usr/share/zoneinfo/America/Los_Angeles
#     ['13/03/2014 CST', datetime(2014, 3, 12, 22, 0),] # why?
# ])
# def test_parse_with_default_dateparser_conversion(date_string, expected_datetime):
#     '''
#     parsing a date string such as "13/03/2014 CST" has many potential meanings.
#     the default dateparser interpretation is do a tzinfo shift plus a local conversion
#     https://github.com/scrapinghub/dateparser/blob/master/dateparser/timezone_parser.py#L18-L19
#     '''
#     datetime_obj = dateparser.parse(date_string)
#     assert datetime_obj == expected_datetime
#
#     #
#     # how and why does dateparser.parse get that expected value?
#     #
#
#     # 1) parse the datestring separate from tzinfo string
#     # https://github.com/scrapinghub/dateparser/blob/35d4dbd7813df80f91f4f6997fda043f92c7f61c/dateparser/timezone_parser.py#L8-L15
#     datetime_midnight = dateparser.parse('13/03/2014')
#     central_tzoffset = [i for i in _tz_offsets if i[0]=='CST'][0][1]['offset']
#     assert datetime_midnight == datetime(2014, 3, 13, 0, 0)
#
#     # 2) factor in the tzinfo offset, we use subtraction operator
#     # https://github.com/scrapinghub/dateparser/blob/35d4dbd7813df80f91f4f6997fda043f92c7f61c/dateparser/timezone_parser.py#L19
#     datetime_central = datetime_midnight - central_tzoffset
#     assert datetime_central == datetime(2014, 3, 13, 6, 0)
#
#     # 3) then localize to the operating system's tzoffset
#     # https://github.com/scrapinghub/dateparser/blob/35d4dbd7813df80f91f4f6997fda043f92c7f61c/dateparser/timezone_parser.py#L19
#     datetime_local = datetime_central + my_local_os_tzoffset
#     assert datetime_local == datetime(2014, 3, 12, 22, 0)



# def expected_tz_conversion(datetime_obj, pytz_tzinfo_offset):
#     # keep the day and time, just give it tzinfo
#     return pytz_tzinfo_offset.localize(datetime_obj)

# @pytest.mark.parametrize('date_string, expected_datetime',[
#     ['13/03/2014 MST', datetime(2014, 3, 13, 0, 0).replace(tzinfo=pytz.timezone('MST')),]
# ])
# def test_parse_with_expected_conversion(date_string, expected_datetime):
#     '''
#     parsing a date string such as "13/03/2014 MST" has many potential meanings.
#     one reasonable expectation would be to keep the day and time the same
#     and just add the tzinfo to the datetime object
#     '''
#     date_string, tzinfo_string = re.findall(r'[0-9\/]+',date_string)[0], re.findall(r'[a-zA-Z]+',date_string)[0]
#     datetime_obj = dateparser.parse(date_string)
#     assert expected_tz_conversion(datetime_obj, pytz.timezone(tzinfo_string)) == expected_datetime




# def another_expected_tz_conversion(datetime_obj, pytz_tzinfo_offset):
#     # use the subtraction operator to calc the tzinfo offset
#     datetime_obj_as_gmt = pytz.timezone('GMT').localize(datetime_obj)
#     return datetime_obj_as_gmt.astimezone(pytz_tzinfo_offset)

# @pytest.mark.parametrize('date_string, expected_datetime',[
#     ['13/03/2014 MST', datetime(2014, 3, 12, 17, 0).replace(tzinfo=pytz.timezone('MST')),]
# ])
# def test_parse_with_another_expected_conversion(date_string, expected_datetime):
#     '''
#     parsing a date string such as "13/03/2014 MST" has many potential meanings.
#     another reasonable expectation would be to calculate only the tzinfo offset
#     '''
#     date_string, tzinfo_string = re.findall(r'[0-9\/]+',date_string)[0], re.findall(r'[a-zA-Z]+',date_string)[0]
#     datetime_obj = dateparser.parse(date_string)
#     assert another_expected_tz_conversion(datetime_obj, pytz.timezone(tzinfo_string)) == expected_datetime


