import pytest
import datefinder
from datetime import datetime
import sys
import logging

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

today = datetime.today()

@pytest.mark.parametrize(
    ("input_text", "expected_date", "first"),
    [
        ("Tuesday Jul 22, 2014", datetime(2014, 7, 22), "month"),
        ("30/10/2015", datetime(2015, 10, 30), "day"),
        ("12/15/18", datetime(2018, 12, 15), "day"),
        ("qwe 15/01/2020 asd", datetime(2020, 1, 15), "day"),
        ("At December 31, 2017", datetime(2017, 12, 31), "day"),
        ("Mär 13 2000", datetime(2000, 3, 13), "day"),
        ("Jan. 1, 2018 1", datetime(2018, 1, 1), "day"),
        ("Jan. 1", datetime(2021, 1, 1), "day"),

        ("2.81", None, "day"),
        ("12.81", None, "day"),
        ("123.81", None, "day"),
        ("2,81", None, "day"),
        ("12,81", None, "day"),
        ("123,81", None, "day"),
        ("12,383", None, "day"),

        ("80,108", None, "day"),
        ("(12)", None, "day"),

        #("asfoj 10/9/2015 asfete 30/10/2015", [datetime(2015, 9, 10),datetime(2015, 10, 30)], "day"),
        #("asfoj 12.4 asfete 3.11", [], "day"),
        #("12/31/2017 31/12/2019", [datetime(2017, 12, 31), datetime(2019, 12, 31)], "day"),
    ]

)
def test_dnl_date_strings(input_text, expected_date, first):
    if isinstance(expected_date, list):
        matches = list(datefinder.find_dates(input_text, first=first, strict=False))
        assert matches == expected_date
    else:
        for return_date in datefinder.find_dates(input_text, first=first, strict=True):
            assert return_date == expected_date