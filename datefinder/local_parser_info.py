import calendar
from dateutil import parser
    
class LocaleParserInfo(parser.parserinfo):
    WEEKDAYS = list(zip(calendar.day_abbr, calendar.day_name))
    MONTHS = list(zip(calendar.month_abbr, calendar.month_name))[1:]