import dateparser
# import re
import regex as re
from dateutil import tz


class DateFinder():
    """
    Locates dates in a text
    """

    DIGITS_MODIFIER_PATTERN = '\d+st|\d+th|\d+rd|first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth|next|last'
    DIGITS_PATTERN = '\d+'
    DAYS_PATTERN = 'monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun'
    MONTHS_PATTERN = 'january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec'
    TIMEZONES_PATTERN = '\sACDT|\sACST|\sACT|\sACWDT|\sACWST|\sADDT|\sADMT|\sADT|\sAEDT|\sAEST|\sAFT|\sAHDT|\sAHST|\sAKDT|\sAKST|\sAKTST|\sAKTT|\sALMST|\sALMT|\sAMST|\sAMT|\sANAST|\sANAT|\sANT|\sAPT|\sAQTST|\sAQTT|\sARST|\sART|\sASHST|\sASHT|\sAST|\sAWDT|\sAWST|\sAWT|\sAZOMT|\sAZOST|\sAZOT|\sAZST|\sAZT|\sBAKST|\sBAKT|\sBDST|\sBDT|\sBEAT|\sBEAUT|\sBIOT|\sBMT|\sBNT|\sBORT|\sBOST|\sBOT|\sBRST|\sBRT|\sBST|\sBTT|\sBURT|\sCANT|\sCAPT|\sCAST|\sCAT|\sCAWT|\sCCT|\sCDDT|\sCDT|\sCEDT|\sCEMT|\sCEST|\sCET|\sCGST|\sCGT|\sCHADT|\sCHAST|\sCHDT|\sCHOST|\sCHOT|\sCIST|\sCKHST|\sCKT|\sCLST|\sCLT|\sCMT|\sCOST|\sCOT|\sCPT|\sCST|\sCUT|\sCVST|\sCVT|\sCWT|\sCXT|\sChST|\sDACT|\sDAVT|\sDDUT|\sDFT|\sDMT|\sDUSST|\sDUST|\sEASST|\sEAST|\sEAT|\sECT|\sEDDT|\sEDT|\sEEDT|\sEEST|\sEET|\sEGST|\sEGT|\sEHDT|\sEMT|\sEPT|\sEST|\sET|\sEWT|\sFET|\sFFMT|\sFJST|\sFJT|\sFKST|\sFKT|\sFMT|\sFNST|\sFNT|\sFORT|\sFRUST|\sFRUT|\sGALT|\sGAMT|\sGBGT|\sGEST|\sGET|\sGFT|\sGHST|\sGILT|\sGIT|\sGMT|\sGST|\sGYT|\sHAA|\sHAC|\sHADT|\sHAE|\sHAP|\sHAR|\sHAST|\sHAT|\sHAY|\sHDT|\sHKST|\sHKT|\sHLV|\sHMT|\sHNA|\sHNC|\sHNE|\sHNP|\sHNR|\sHNT|\sHNY|\sHOVST|\sHOVT|\sHST|\sICT|\sIDDT|\sIDT|\sIHST|\sIMT|\sIOT|\sIRDT|\sIRKST|\sIRKT|\sIRST|\sISST|\sIST|\sJAVT|\sJCST|\sJDT|\sJMT|\sJST|\sJWST|\sKART|\sKDT|\sKGST|\sKGT|\sKIZST|\sKIZT|\sKMT|\sKOST|\sKRAST|\sKRAT|\sKST|\sKUYST|\sKUYT|\sKWAT|\sLHDT|\sLHST|\sLINT|\sLKT|\sLMT|\sLMT|\sLMT|\sLMT|\sLRT|\sLST|\sMADMT|\sMADST|\sMADT|\sMAGST|\sMAGT|\sMALST|\sMALT|\sMART|\sMAWT|\sMDDT|\sMDST|\sMDT|\sMEST|\sMET|\sMHT|\sMIST|\sMIT|\sMMT|\sMOST|\sMOT|\sMPT|\sMSD|\sMSK|\sMSM|\sMST|\sMUST|\sMUT|\sMVT|\sMWT|\sMYT|\sNCST|\sNCT|\sNDDT|\sNDT|\sNEGT|\sNEST|\sNET|\sNFT|\sNMT|\sNOVST|\sNOVT|\sNPT|\sNRT|\sNST|\sNT|\sNUT|\sNWT|\sNZDT|\sNZMT|\sNZST|\sOMSST|\sOMST|\sORAST|\sORAT|\sPDDT|\sPDT|\sPEST|\sPET|\sPETST|\sPETT|\sPGT|\sPHOT|\sPHST|\sPHT|\sPKST|\sPKT|\sPLMT|\sPMDT|\sPMMT|\sPMST|\sPMT|\sPNT|\sPONT|\sPPMT|\sPPT|\sPST|\sPT|\sPWT|\sPYST|\sPYT|\sQMT|\sQYZST|\sQYZT|\sRET|\sRMT|\sROTT|\sSAKST|\sSAKT|\sSAMT|\sSAST|\sSBT|\sSCT|\sSDMT|\sSDT|\sSET|\sSGT|\sSHEST|\sSHET|\sSJMT|\sSLT|\sSMT|\sSRET|\sSRT|\sSST|\sSTAT|\sSVEST|\sSVET|\sSWAT|\sSYOT|\sTAHT|\sTASST|\sTAST|\sTBIST|\sTBIT|\sTBMT|\sTFT|\sTHA|\sTJT|\sTKT|\sTLT|\sTMT|\sTOST|\sTOT|\sTRST|\sTRT|\sTSAT|\sTVT|\sULAST|\sULAT|\sURAST|\sURAT|\sUTC|\sUYHST|\sUYST|\sUYT|\sUZST|\sUZT|\sVET|\sVLAST|\sVLAT|\sVOLST|\sVOLT|\sVOST|\sVUST|\sVUT|\sWARST|\sWART|\sWAST|\sWAT|\sWDT|\sWEDT|\sWEMT|\sWEST|\sWET|\sWFT|\sWGST|\sWGT|\sWIB|\sWIT|\sWITA|\sWMT|\sWSDT|\sWSST|\sWST|\sWT|\sXJT|\sYAKST|\sYAKT|\sYAPT|\sYDDT|\sYDT|\sYEKST|\sYEKST|\sYEKT|\sYEKT|\sYERST|\sYERT|\sYPT|\sYST|\sYWT|\szzz'
    ## explicit north american timezones that get replaced
    NA_TIMEZONES_PATTERN = 'pacific|eastern|mountain|central'
    ALL_TIMEZONES_PATTERN = TIMEZONES_PATTERN + '|' + NA_TIMEZONES_PATTERN
    DELIMITERS_PATTERN = '[/\:\-\,\s\_\+\@]+'
    TIME_PERIOD_PATTERN = 'a\.m\.|am|p\.m\.|pm'
    ## can be in date strings but not recognized by dateparser
    EXTRA_TOKENS_PATTERN = 'due|by|on|standard|daylight|savings|time|date|year|of|to|until|z|at'

    ## Time pattern is used independently, so specified here.
    TIME_PATTERN = """
    (?P<time>
        (
            (?P<hours>\d{{1,2}})
            \:
            (?P<minutes>\d{{1,2}})
            (\:(?<seconds>\d{{1,2}}))?
            \s*
            (?P<time_periods>{time_periods})?
            \s*
            (?P<timezones>{timezones})?
        )
        |
        (
            (?P<hours>\d{{1,2}})
            \s*
            (?P<time_periods>{time_periods})
            \s*
            (?P<timezones>{timezones})*
        )
    )
    """.format(
        time_periods=TIME_PERIOD_PATTERN,
        timezones=ALL_TIMEZONES_PATTERN
    )

    DATES_PATTERN = """
    (
        (
            {time}
            |
            ## Grab any digits
            (?P<digits_modifier>{digits_modifier})
            |
            (?P<digits>{digits})
            |
            (?P<days>{days})
            |
            (?P<months>{months})
            |
            ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
            ## as well as whitespace
            (?P<delimiters>{delimiters})
            |
            ## These tokens could be in phrases that dateparser does not yet recognize
            ## Some are US Centric
            (?P<extra_tokens>{extra_tokens})
        ## We need at least three items to match for minimal datetime parsing
        ## ie 10pm
        ){{3,}}
    )
    """

    DATES_PATTERN = DATES_PATTERN.format(
        time=TIME_PATTERN,
        digits=DIGITS_PATTERN,
        digits_modifier=DIGITS_MODIFIER_PATTERN,
        days=DAYS_PATTERN,
        months=MONTHS_PATTERN,
        delimiters=DELIMITERS_PATTERN,
        extra_tokens=EXTRA_TOKENS_PATTERN
    )

    DATE_REGEX = re.compile(DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

    TIME_REGEX = re.compile(TIME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

    ## These tokens can be in original text but dateparser
    ## won't handle them without modification
    REPLACEMENTS = {
        "standard": "",
        "daylight": "",
        "savings": "",
        "time": "",
        "date": "",
        "by": "",
        "due": "",
        "on": "",
        ",": "",
    }

    TIMEZONE_REPLACEMENTS = {
        "pacific": "PST",
        "eastern": "EST",
        "mountain": "MST",
        "central": "CST",
    }

    ## Characters that can be removed from ends of matched strings
    STRIP_CHARS = ' \n\t:-.,_'

    def find_dates(self, text, source=False, index=False, strict=False):

        for date_string, indices, captures in self.extract_date_strings(text, strict=strict):

            as_dt = self.parse_date_string(date_string,captures)
            if as_dt is None:
                ## Dateparser couldn't make heads or tails of it
                ## move on to next
                continue

            returnables = (as_dt,)
            if source:
                returnables = returnables + (date_string,)
            if index:
                returnables = returnables + (indices,)

            if len(returnables) == 1:
                returnables = returnables[0]
            yield returnables

    def _find_and_replace(self, date_string, captures):
        """
        replace strings which helped us do matching but dateparser can't read.
        also replace captured timezones and return tz_string separately
        so that dateparser.parse doesn't do weirdo auto tzoffset conversions
        https://github.com/scrapinghub/dateparser/blob/master/dateparser/timezone_parser.py#L19

        :warning: when multiple tz matches exist the last sorted capture will trump
        :param date_string:
        :return: date_string, tz_string
        """

        # add timezones to replace
        for tz_string in captures.get('timezones',[]):
            self.REPLACEMENTS.update({tz_string:''})

        date_string = date_string.lower()
        for key, replacement in self.REPLACEMENTS.items():
            date_string = date_string.replace(key, replacement)

        return date_string, self._pop_tz_string(sorted(captures.get('timezones',[])))


    def _pop_tz_string(self, list_of_timezones):
        try:
            tz_string = list_of_timezones.pop()
            # make sure it's not a timezone we
            # want replaced with better abbreviation
            return self.TIMEZONE_REPLACEMENTS.get(tz_string, tz_string)
        except IndexError:
            return ''

    def _add_tzinfo(self, datetime_obj, tz_string):
        """
        take a naive datetime and add dateutil.tz.tzinfo object

        :param datetime_obj: naive datetime object
        :return: datetime object with tzinfo
        """
        if datetime_obj is None:
            return None

        tzinfo_match = tz.gettz(tz_string)
        return datetime_obj.replace(tzinfo=tzinfo_match)


    def parse_date_string(self, date_string, captures):
        # replace tokens that are problematic for dateparser
        date_string, tz_string = self._find_and_replace(date_string, captures)

        ## One last sweep after removing
        date_string = date_string.strip(self.STRIP_CHARS)
        ## Match strings must be at least 3 characters long
        ## < 3 tends to be garbage
        if len(date_string) < 3:
            return None

        as_dt = dateparser.parse(date_string)
        if tz_string:
            as_dt = self._add_tzinfo(as_dt,tz_string)
        return as_dt

    def extract_date_strings(self, text, strict=False):
        """
        Scans text for possible datetime strings and extracts them

        source: also return the original date string
        index: also return the indices of the date string in the text
        strict: Strict mode will only return dates sourced with day, month, and year
        """
        for match in self.DATE_REGEX.finditer(text):
            match_str = match.group(0)
            indices = match.span(0)

            ## If strict, only match input strings that

            # if strict:
                # complete = False

                ## Get individual group matches
            captures = match.capturesdict()
            time = captures.get('time')
            digits = captures.get('digits')
            digits_modifiers = captures.get('digits_modifiers')
            days = captures.get('days')
            months = captures.get('months')
            timezones = captures.get('timezones')
            delimiters = captures.get('delimiters')
            time = captures.get('time)')
            time_periods = captures.get('time_periods')
            extra_tokens = captures.get('extra_tokens')

            if strict:
                complete = False
                ## 12-05-2015
                if len(digits) == 3:
                    complete = True
                ## 19 February 2013 year 09:10
                elif (len(months) == 1) and (len(digits) == 2):
                    complete = True

                if not complete:
                    continue

            ## sanitize date string
            ## replace unhelpful whitespace characters with single whitespace
            match_str = re.sub('[\n\t\s\xa0]+', ' ', match_str)
            match_str = match_str.strip(self.STRIP_CHARS)

            ## Save sanitized source string
            yield match_str, indices, captures


def find_dates(text, source=False, index=False, strict=False):
    """
    Create a top level function to for basic API accessibility
    """
    date_finder = DateFinder()
    return date_finder.find_dates(text, source=source, index=index, strict=strict)
