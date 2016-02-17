# import re
# import pytz
# from datetime import datetime
# import dateparser
# import pytest

# def expected_tz_conversion(datetime_obj, pytz_tzinfo_offset):
#     # keep the day and time, just give it tzinfo
#     return pytz_tzinfo_offset.localize(datetime_obj)

# @pytest.mark.parametrize('date_string, dateparser_expected_datetime, expected_datetime',[
#     [
#     '13/03/2014 MST',
#     datetime(2014, 3, 13, 7, 0), # assumes your /etc/localtime -> /usr/share/zoneinfo/America/Los_Angeles
#     datetime(2014, 3, 13, 0, 0).replace(tzinfo=pytz.timezone('MST'))
#     ]
# ])
# def test_dateparser_and_two_alternatives(date_string, dateparser_expected_datetime, expected_datetime):
#     '''
#     parsing a date string such as "13/03/2014 MST" has many potential meanings
#     '''

#     # the original default dateparser interpretation was to do a tzinfo shift plus a local conversion
#     # that changed in version 3.2 recently to do a UTC shift
#     # https://github.com/scrapinghub/dateparser/commit/6c6b3d93ac267901cbaaef534e2eb5c7d8c7deb8#diff-620d77b1f1bb42b71cf2181c8b7ce193L183
#     datetime_obj = dateparser.parse(date_string)
#     assert datetime_obj == dateparser_expected_datetime

#     # a more straightforward expectation might be to keep the day and time the same
#     # and just add the tzinfo to the datetime object if it is found
#     date_string_only, tzinfo_string = re.findall(r'[0-9\/]+',date_string)[0], re.findall(r'[a-zA-Z]+',date_string)[0]
#     datetime_obj = dateparser.parse(date_string_only)
#     assert expected_tz_conversion(datetime_obj, pytz.timezone(tzinfo_string)) == expected_datetime



