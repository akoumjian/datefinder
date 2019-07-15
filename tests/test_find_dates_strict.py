import pytest
import datefinder
from datetime import datetime
import pytz
import sys
import logging
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
logger = logging.getLogger(__name__)

today = datetime.today()


@pytest.mark.parametrize('input_text, expected_date', [

    ('June 2018', []),
    ('09/06/18',  datetime(2018, 9, 6)),
    ('09/06/2018', datetime(2018, 9, 6))
    
])
def test_find_date_strings_strict(input_text, expected_date):
    if isinstance(expected_date,list):
        matches = list(datefinder.find_dates(input_text, strict=True))
        assert matches == expected_date

    else:
        return_date = None
        for return_date in datefinder.find_dates(input_text, strict=True):
            assert return_date == expected_date
        assert return_date is not None, 'Did not find date for test line: "{}"'.format(input_text) # handles dates 