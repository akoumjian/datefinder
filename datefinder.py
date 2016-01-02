import dateparser
import re

## The idea of the regex is to liberally match any natural language datetime phrases from beginning to end.
COMBINED_REG = """
(
    (
        ## Grab any digits
        \d+
        |
        monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun
        |
        january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec
        |
        \sACDT|\sACST|\sACT|\sACWDT|\sACWST|\sADDT|\sADMT|\sADT|\sAEDT|\sAEST|\sAFT|\sAHDT|\sAHST|\sAKDT|\sAKST|\sAKTST|\sAKTT|\sALMST|\sALMT|\sAMST|\sAMT|\sANAST|\sANAT|\sANT|\sAPT|\sAQTST|\sAQTT|\sARST|\sART|\sASHST|\sASHT|\sAST|\sAWDT|\sAWST|\sAWT|\sAZOMT|\sAZOST|\sAZOT|\sAZST|\sAZT|\sBAKST|\sBAKT|\sBDST|\sBDT|\sBEAT|\sBEAUT|\sBIOT|\sBMT|\sBNT|\sBORT|\sBOST|\sBOT|\sBRST|\sBRT|\sBST|\sBTT|\sBURT|\sCANT|\sCAPT|\sCAST|\sCAT|\sCAWT|\sCCT|\sCDDT|\sCDT|\sCEDT|\sCEMT|\sCEST|\sCET|\sCGST|\sCGT|\sCHADT|\sCHAST|\sCHDT|\sCHOST|\sCHOT|\sCIST|\sCKHST|\sCKT|\sCLST|\sCLT|\sCMT|\sCOST|\sCOT|\sCPT|\sCST|\sCUT|\sCVST|\sCVT|\sCWT|\sCXT|\sChST|\sDACT|\sDAVT|\sDDUT|\sDFT|\sDMT|\sDUSST|\sDUST|\sEASST|\sEAST|\sEAT|\sECT|\sEDDT|\sEDT|\sEEDT|\sEEST|\sEET|\sEGST|\sEGT|\sEHDT|\sEMT|\sEPT|\sEST|\sET|\sEWT|\sFET|\sFFMT|\sFJST|\sFJT|\sFKST|\sFKT|\sFMT|\sFNST|\sFNT|\sFORT|\sFRUST|\sFRUT|\sGALT|\sGAMT|\sGBGT|\sGEST|\sGET|\sGFT|\sGHST|\sGILT|\sGIT|\sGMT|\sGST|\sGYT|\sHAA|\sHAC|\sHADT|\sHAE|\sHAP|\sHAR|\sHAST|\sHAT|\sHAY|\sHDT|\sHKST|\sHKT|\sHLV|\sHMT|\sHNA|\sHNC|\sHNE|\sHNP|\sHNR|\sHNT|\sHNY|\sHOVST|\sHOVT|\sHST|\sICT|\sIDDT|\sIDT|\sIHST|\sIMT|\sIOT|\sIRDT|\sIRKST|\sIRKT|\sIRST|\sISST|\sIST|\sJAVT|\sJCST|\sJDT|\sJMT|\sJST|\sJWST|\sKART|\sKDT|\sKGST|\sKGT|\sKIZST|\sKIZT|\sKMT|\sKOST|\sKRAST|\sKRAT|\sKST|\sKUYST|\sKUYT|\sKWAT|\sLHDT|\sLHST|\sLINT|\sLKT|\sLMT|\sLMT|\sLMT|\sLMT|\sLRT|\sLST|\sMADMT|\sMADST|\sMADT|\sMAGST|\sMAGT|\sMALST|\sMALT|\sMART|\sMAWT|\sMDDT|\sMDST|\sMDT|\sMEST|\sMET|\sMHT|\sMIST|\sMIT|\sMMT|\sMOST|\sMOT|\sMPT|\sMSD|\sMSK|\sMSM|\sMST|\sMUST|\sMUT|\sMVT|\sMWT|\sMYT|\sNCST|\sNCT|\sNDDT|\sNDT|\sNEGT|\sNEST|\sNET|\sNFT|\sNMT|\sNOVST|\sNOVT|\sNPT|\sNRT|\sNST|\sNT|\sNUT|\sNWT|\sNZDT|\sNZMT|\sNZST|\sOMSST|\sOMST|\sORAST|\sORAT|\sPDDT|\sPDT|\sPEST|\sPET|\sPETST|\sPETT|\sPGT|\sPHOT|\sPHST|\sPHT|\sPKST|\sPKT|\sPLMT|\sPMDT|\sPMMT|\sPMST|\sPMT|\sPNT|\sPONT|\sPPMT|\sPPT|\sPST|\sPT|\sPWT|\sPYST|\sPYT|\sQMT|\sQYZST|\sQYZT|\sRET|\sRMT|\sROTT|\sSAKST|\sSAKT|\sSAMT|\sSAST|\sSBT|\sSCT|\sSDMT|\sSDT|\sSET|\sSGT|\sSHEST|\sSHET|\sSJMT|\sSLT|\sSMT|\sSRET|\sSRT|\sSST|\sSTAT|\sSVEST|\sSVET|\sSWAT|\sSYOT|\sTAHT|\sTASST|\sTAST|\sTBIST|\sTBIT|\sTBMT|\sTFT|\sTHA|\sTJT|\sTKT|\sTLT|\sTMT|\sTOST|\sTOT|\sTRST|\sTRT|\sTSAT|\sTVT|\sULAST|\sULAT|\sURAST|\sURAT|\sUTC|\sUYHST|\sUYST|\sUYT|\sUZST|\sUZT|\sVET|\sVLAST|\sVLAT|\sVOLST|\sVOLT|\sVOST|\sVUST|\sVUT|\sWARST|\sWART|\sWAST|\sWAT|\sWDT|\sWEDT|\sWEMT|\sWEST|\sWET|\sWFT|\sWGST|\sWGT|\sWIB|\sWIT|\sWITA|\sWMT|\sWSDT|\sWSST|\sWST|\sWT|\sXJT|\sYAKST|\sYAKT|\sYAPT|\sYDDT|\sYDT|\sYEKST|\sYEKST|\sYEKT|\sYEKT|\sYERST|\sYERT|\sYPT|\sYST|\sYWT|\szzz
        |
        ## Delimiters, ie Tuesday, July 18 or 6/17/2008
        ## as well as whitespace
        [/\:\.\-\,\s\_\+\@]+
        |
        a\.m\.|am|p\.m\.|pm
        |
        ## These characters could be in phrases that dateparser does not yet recognize
        ## (US centric, making assumptions)
        due|by|on|pacific|eastern|mountain|central|standard|daylight|savings|time|date
    ## We need at least three items to match for minimal datetime parsing
    ## ie 10pm
    ){3,}
)
"""

DATE_REGEX = re.compile(COMBINED_REG, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE)

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
    # "\n": " ",
    # "\t": " ",
    # "  ": " ",
}

STRIP_CHARS = ' \n\t:-.,_'


def compare_date_tuples(first, second):
    first_length = len(first[0])
    second_length = len(second[0])
    if first_length > second_length:
        return 1
    elif first_length < second_length:
        return -1
    return 0


def prioritize(dates):
    """
    Sort dates according to most likely to be correct

    Currently that just amounts to the largest original matching string,
    since it theoretically has the most information.
    """
    return sorted(dates, cmp=compare_date_tuples, reverse=True)


def find_dates(text):
    """
    Scans text for possible datetime strings and extracts them
    """
    ## note, remove newlines on matches before testing parse
    dates = []
    for match in DATE_REGEX.finditer(text):
        match_str = match.group(0)

        ## sanitize date string
        match_str = match_str.lower()
        ## replace unhelpful whitespace characters with single whitespace
        match_str = re.sub('[\n\t\s\xa0]+', ' ', match_str)
        match_str = match_str.strip(STRIP_CHARS)

        ## save it here for original comparison
        full = match_str

        ## replace strings which are allowable to help us match but for which dateparser can't read
        for key, replacement in REPLACEMENTS.items():
            match_str = match_str.replace(key, replacement)

        ## One last sweep after removing
        match_str = match_str.strip(STRIP_CHARS)

        if len(match_str) > 3:
            as_dt = dateparser.parse(match_str)
            if as_dt is not None:
                dates.append((full, as_dt))

    dates = prioritize(dates)
    return dates
