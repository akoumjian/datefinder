import dateparser
import re


class DateFinder():
    """
    Locates dates in a text
    """

    ## The idea of the regex is to liberally match any natural language datetime phrases from beginning to end.
    DATES_PATTERN = """
    (
        (
            ## Grab any digits
            \d+
            |
            monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun
            |
            january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec
            |
            ## Timezones
            \sACDT|\sACST|\sACT|\sACWDT|\sACWST|\sADDT|\sADMT|\sADT|\sAEDT|\sAEST|\sAFT|\sAHDT|\sAHST|\sAKDT|\sAKST|\sAKTST|\sAKTT|\sALMST|\sALMT|\sAMST|\sAMT|\sANAST|\sANAT|\sANT|\sAPT|\sAQTST|\sAQTT|\sARST|\sART|\sASHST|\sASHT|\sAST|\sAWDT|\sAWST|\sAWT|\sAZOMT|\sAZOST|\sAZOT|\sAZST|\sAZT|\sBAKST|\sBAKT|\sBDST|\sBDT|\sBEAT|\sBEAUT|\sBIOT|\sBMT|\sBNT|\sBORT|\sBOST|\sBOT|\sBRST|\sBRT|\sBST|\sBTT|\sBURT|\sCANT|\sCAPT|\sCAST|\sCAT|\sCAWT|\sCCT|\sCDDT|\sCDT|\sCEDT|\sCEMT|\sCEST|\sCET|\sCGST|\sCGT|\sCHADT|\sCHAST|\sCHDT|\sCHOST|\sCHOT|\sCIST|\sCKHST|\sCKT|\sCLST|\sCLT|\sCMT|\sCOST|\sCOT|\sCPT|\sCST|\sCUT|\sCVST|\sCVT|\sCWT|\sCXT|\sChST|\sDACT|\sDAVT|\sDDUT|\sDFT|\sDMT|\sDUSST|\sDUST|\sEASST|\sEAST|\sEAT|\sECT|\sEDDT|\sEDT|\sEEDT|\sEEST|\sEET|\sEGST|\sEGT|\sEHDT|\sEMT|\sEPT|\sEST|\sET|\sEWT|\sFET|\sFFMT|\sFJST|\sFJT|\sFKST|\sFKT|\sFMT|\sFNST|\sFNT|\sFORT|\sFRUST|\sFRUT|\sGALT|\sGAMT|\sGBGT|\sGEST|\sGET|\sGFT|\sGHST|\sGILT|\sGIT|\sGMT|\sGST|\sGYT|\sHAA|\sHAC|\sHADT|\sHAE|\sHAP|\sHAR|\sHAST|\sHAT|\sHAY|\sHDT|\sHKST|\sHKT|\sHLV|\sHMT|\sHNA|\sHNC|\sHNE|\sHNP|\sHNR|\sHNT|\sHNY|\sHOVST|\sHOVT|\sHST|\sICT|\sIDDT|\sIDT|\sIHST|\sIMT|\sIOT|\sIRDT|\sIRKST|\sIRKT|\sIRST|\sISST|\sIST|\sJAVT|\sJCST|\sJDT|\sJMT|\sJST|\sJWST|\sKART|\sKDT|\sKGST|\sKGT|\sKIZST|\sKIZT|\sKMT|\sKOST|\sKRAST|\sKRAT|\sKST|\sKUYST|\sKUYT|\sKWAT|\sLHDT|\sLHST|\sLINT|\sLKT|\sLMT|\sLMT|\sLMT|\sLMT|\sLRT|\sLST|\sMADMT|\sMADST|\sMADT|\sMAGST|\sMAGT|\sMALST|\sMALT|\sMART|\sMAWT|\sMDDT|\sMDST|\sMDT|\sMEST|\sMET|\sMHT|\sMIST|\sMIT|\sMMT|\sMOST|\sMOT|\sMPT|\sMSD|\sMSK|\sMSM|\sMST|\sMUST|\sMUT|\sMVT|\sMWT|\sMYT|\sNCST|\sNCT|\sNDDT|\sNDT|\sNEGT|\sNEST|\sNET|\sNFT|\sNMT|\sNOVST|\sNOVT|\sNPT|\sNRT|\sNST|\sNT|\sNUT|\sNWT|\sNZDT|\sNZMT|\sNZST|\sOMSST|\sOMST|\sORAST|\sORAT|\sPDDT|\sPDT|\sPEST|\sPET|\sPETST|\sPETT|\sPGT|\sPHOT|\sPHST|\sPHT|\sPKST|\sPKT|\sPLMT|\sPMDT|\sPMMT|\sPMST|\sPMT|\sPNT|\sPONT|\sPPMT|\sPPT|\sPST|\sPT|\sPWT|\sPYST|\sPYT|\sQMT|\sQYZST|\sQYZT|\sRET|\sRMT|\sROTT|\sSAKST|\sSAKT|\sSAMT|\sSAST|\sSBT|\sSCT|\sSDMT|\sSDT|\sSET|\sSGT|\sSHEST|\sSHET|\sSJMT|\sSLT|\sSMT|\sSRET|\sSRT|\sSST|\sSTAT|\sSVEST|\sSVET|\sSWAT|\sSYOT|\sTAHT|\sTASST|\sTAST|\sTBIST|\sTBIT|\sTBMT|\sTFT|\sTHA|\sTJT|\sTKT|\sTLT|\sTMT|\sTOST|\sTOT|\sTRST|\sTRT|\sTSAT|\sTVT|\sULAST|\sULAT|\sURAST|\sURAT|\sUTC|\sUYHST|\sUYST|\sUYT|\sUZST|\sUZT|\sVET|\sVLAST|\sVLAT|\sVOLST|\sVOLT|\sVOST|\sVUST|\sVUT|\sWARST|\sWART|\sWAST|\sWAT|\sWDT|\sWEDT|\sWEMT|\sWEST|\sWET|\sWFT|\sWGST|\sWGT|\sWIB|\sWIT|\sWITA|\sWMT|\sWSDT|\sWSST|\sWST|\sWT|\sXJT|\sYAKST|\sYAKT|\sYAPT|\sYDDT|\sYDT|\sYEKST|\sYEKST|\sYEKT|\sYEKT|\sYERST|\sYERT|\sYPT|\sYST|\sYWT|\szzz
            |
            ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
            ## as well as whitespace
            [/\:\.\-\,\s\_\+\@]+
            |
            ## descriptions of time
            a\.m\.|am|p\.m\.|pm
            |
            ## These tokens could be in phrases that dateparser does not yet recognize
            ## Some are US Centric
            due|by|on|pacific|eastern|mountain|central|standard|daylight|savings|time|date
        ## We need at least three items to match for minimal datetime parsing
        ## ie 10pm
        ){3,}
    )
    """

    DATE_REGEX = re.compile(DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

    ## These tokens can be in original text but dateparser
    ## won't handle them without modification
    REPLACEMENTS = {
        "pacific": "pst",
        "eastern": "est",
        "mountain": "mst",
        "central": "cst",
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

    ## Characters that can be removed from ends of matched strings
    STRIP_CHARS = ' \n\t:-.,_'

    def find_dates(self, text, source=False, index=False):

        for date_string, indices in self.extract_date_strings(text):

            as_dt = self.parse_date_string(date_string)
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

    def parse_date_string(self, date_string):
            ## replace strings which are allowable to help us match but for which dateparser can't read
            date_string = date_string.lower()
            for key, replacement in self.REPLACEMENTS.items():
                date_string = date_string.replace(key, replacement)

            ## One last sweep after removing
            date_string = date_string.strip(self.STRIP_CHARS)
            ## Match strings must be at least 3 characters long
            ## < 3 tends to be garbage
            if len(date_string) > 3:
                as_dt = dateparser.parse(date_string)
                return as_dt
            return None

    def extract_date_strings(self, text):
        """
        Scans text for possible datetime strings and extracts them

        source: also return the original date string
        index: also return the indices of the date string in the text
        """
        for match in self.DATE_REGEX.finditer(text):
            match_str = match.group(0)
            indices = match.span(0)

            ## sanitize date string
            ## replace unhelpful whitespace characters with single whitespace
            match_str = re.sub('[\n\t\s\xa0]+', ' ', match_str)
            match_str = match_str.strip(self.STRIP_CHARS)

            ## Save sanitized source string
            yield match_str, indices


def find_dates(text, source=False, index=False):
    """
    Create a top level function to for basic API accessibility
    """
    date_finder = DateFinder()
    return date_finder.find_dates(text, source=source, index=index)
