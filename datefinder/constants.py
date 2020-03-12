import regex as re

NUMBERS_PATTERN = r"first|second|third|fourth|fifth|sixth|seventh|eighth|nineth|tenth"
POSITIONNAL_TOKENS = r"next|last"
DIGITS_PATTERN = r"\d+"
DIGITS_SUFFIXES = r"st|th|rd|nd"
DAYS_PATTERN = "monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|tues|wed|thur|thurs|fri|sat|sun"
MONTHS_PATTERN = r"january|february|march|april|may|june|july|august|september|october|november|december|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre|jan\.?|ene\.?|feb\.?|mar\.?|apr\.?|abr\.?|may\.?|jun\.?|jul\.?|aug\.?|ago\.?|sep\.?|sept\.?|oct\.?|nov\.?|dec\.?|dic\.?"
TIMEZONES_PATTERN = "ACDT|ACST|ACT|ACWDT|ACWST|ADDT|ADMT|ADT|AEDT|AEST|AFT|AHDT|AHST|AKDT|AKST|AKTST|AKTT|ALMST|ALMT|AMST|AMT|ANAST|ANAT|ANT|APT|AQTST|AQTT|ARST|ART|ASHST|ASHT|AST|AWDT|AWST|AWT|AZOMT|AZOST|AZOT|AZST|AZT|BAKST|BAKT|BDST|BDT|BEAT|BEAUT|BIOT|BMT|BNT|BORT|BOST|BOT|BRST|BRT|BST|BTT|BURT|CANT|CAPT|CAST|CAT|CAWT|CCT|CDDT|CDT|CEDT|CEMT|CEST|CET|CGST|CGT|CHADT|CHAST|CHDT|CHOST|CHOT|CIST|CKHST|CKT|CLST|CLT|CMT|COST|COT|CPT|CST|CUT|CVST|CVT|CWT|CXT|ChST|DACT|DAVT|DDUT|DFT|DMT|DUSST|DUST|EASST|EAST|EAT|ECT|EDDT|EDT|EEDT|EEST|EET|EGST|EGT|EHDT|EMT|EPT|EST|ET|EWT|FET|FFMT|FJST|FJT|FKST|FKT|FMT|FNST|FNT|FORT|FRUST|FRUT|GALT|GAMT|GBGT|GEST|GET|GFT|GHST|GILT|GIT|GMT|GST|GYT|HAA|HAC|HADT|HAE|HAP|HAR|HAST|HAT|HAY|HDT|HKST|HKT|HLV|HMT|HNA|HNC|HNE|HNP|HNR|HNT|HNY|HOVST|HOVT|HST|ICT|IDDT|IDT|IHST|IMT|IOT|IRDT|IRKST|IRKT|IRST|ISST|IST|JAVT|JCST|JDT|JMT|JST|JWST|KART|KDT|KGST|KGT|KIZST|KIZT|KMT|KOST|KRAST|KRAT|KST|KUYST|KUYT|KWAT|LHDT|LHST|LINT|LKT|LMT|LMT|LMT|LMT|LRT|LST|MADMT|MADST|MADT|MAGST|MAGT|MALST|MALT|MART|MAWT|MDDT|MDST|MDT|MEST|MET|MHT|MIST|MIT|MMT|MOST|MOT|MPT|MSD|MSK|MSM|MST|MUST|MUT|MVT|MWT|MYT|NCST|NCT|NDDT|NDT|NEGT|NEST|NET|NFT|NMT|NOVST|NOVT|NPT|NRT|NST|NT|NUT|NWT|NZDT|NZMT|NZST|OMSST|OMST|ORAST|ORAT|PDDT|PDT|PEST|PET|PETST|PETT|PGT|PHOT|PHST|PHT|PKST|PKT|PLMT|PMDT|PMMT|PMST|PMT|PNT|PONT|PPMT|PPT|PST|PT|PWT|PYST|PYT|QMT|QYZST|QYZT|RET|RMT|ROTT|SAKST|SAKT|SAMT|SAST|SBT|SCT|SDMT|SDT|SET|SGT|SHEST|SHET|SJMT|SLT|SMT|SRET|SRT|SST|STAT|SVEST|SVET|SWAT|SYOT|TAHT|TASST|TAST|TBIST|TBIT|TBMT|TFT|THA|TJT|TKT|TLT|TMT|TOST|TOT|TRST|TRT|TSAT|TVT|ULAST|ULAT|URAST|URAT|UTC|UYHST|UYST|UYT|UZST|UZT|VET|VLAST|VLAT|VOLST|VOLT|VOST|VUST|VUT|WARST|WART|WAST|WAT|WDT|WEDT|WEMT|WEST|WET|WFT|WGST|WGT|WIB|WIT|WITA|WMT|WSDT|WSST|WST|WT|XJT|YAKST|YAKT|YAPT|YDDT|YDT|YEKST|YEKST|YEKT|YEKT|YERST|YERT|YPT|YST|YWT|zzz"
## explicit north american timezones that get replaced
NA_TIMEZONES_PATTERN = "pacific|eastern|mountain|central"
ALL_TIMEZONES_PATTERN = TIMEZONES_PATTERN + "|" + NA_TIMEZONES_PATTERN
DELIMITERS_PATTERN = r"[/\:\-\,\s\_\+\@]+"

# Allows for straightforward datestamps e.g 2017, 201712, 20171223. Created with:
#  YYYYMM_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'|20\d\d'+'{:0>2}'.format(mon) for mon in range(1, 13)])
#  YYYYMMDD_PATTERN = '|'.join(['19\d\d'+'{:0>2}'.format(mon)+'[0123]\d|20\d\d'+'{:0>2}'.format(mon)+'[0123]\d' for mon in range(1, 13)])
YYYY_PATTERN = r"19\d\d|20\d\d"
YYYYMM_PATTERN = r"19\d\d01|20\d\d01|19\d\d02|20\d\d02|19\d\d03|20\d\d03|19\d\d04|20\d\d04|19\d\d05|20\d\d05|19\d\d06|20\d\d06|19\d\d07|20\d\d07|19\d\d08|20\d\d08|19\d\d09|20\d\d09|19\d\d10|20\d\d10|19\d\d11|20\d\d11|19\d\d12|20\d\d12"
YYYYMMDD_PATTERN = r"19\d\d01[0123]\d|20\d\d01[0123]\d|19\d\d02[0123]\d|20\d\d02[0123]\d|19\d\d03[0123]\d|20\d\d03[0123]\d|19\d\d04[0123]\d|20\d\d04[0123]\d|19\d\d05[0123]\d|20\d\d05[0123]\d|19\d\d06[0123]\d|20\d\d06[0123]\d|19\d\d07[0123]\d|20\d\d07[0123]\d|19\d\d08[0123]\d|20\d\d08[0123]\d|19\d\d09[0123]\d|20\d\d09[0123]\d|19\d\d10[0123]\d|20\d\d10[0123]\d|19\d\d11[0123]\d|20\d\d11[0123]\d|19\d\d12[0123]\d|20\d\d12[0123]\d"
YYYYMMDDHHMMSS_PATTERN = "|".join(
    [
        r"19\d\d"
        + "{:0>2}".format(mon)
        + r"[0-3]\d[0-5]\d[0-5]\d[0-5]\d|20\d\d"
        + "{:0>2}".format(mon)
        + r"[0-3]\d[0-5]\d[0-5]\d[0-5]\d"
        for mon in range(1, 13)
    ]
)
ISO8601_PATTERN = r"(?P<years>-?(\:[1-9][0-9]*)?[0-9]{4})\-(?P<months>1[0-2]|0[1-9])\-(?P<days>3[01]|0[1-9]|[12][0-9])T(?P<hours>2[0-3]|[01][0-9])\:(?P<minutes>[0-5][0-9]):(?P<seconds>[0-5][0-9])(?:[\.,]+(?P<microseconds>[0-9]+))?(?P<offset>(?:Z|[+-](?:2[0-3]|[01][0-9])\:[0-5][0-9]))?"
UNDELIMITED_STAMPS_PATTERN = "|".join(
    [YYYYMMDDHHMMSS_PATTERN, YYYYMMDD_PATTERN, YYYYMM_PATTERN, ISO8601_PATTERN]
)
DELIMITERS_PATTERN = r"[/\:\-\,\.\s\_\+\@]+"
TIME_PERIOD_PATTERN = r"a\.m\.|am|p\.m\.|pm"
## can be in date strings but not recognized by dateutils
EXTRA_TOKENS_PATTERN = r"due|by|on|during|standard|daylight|savings|time|date|dated|of|to|through|between|until|at|day"

## TODO: Get english numbers?
## http://www.rexegg.com/regex-trick-numbers-in-english.html

RELATIVE_PATTERN = "before|after|next|last|ago"
TIME_SHORTHAND_PATTERN = "noon|midnight|today|yesterday"
UNIT_PATTERN = "second|minute|hour|day|week|month|year"

## Time pattern is used independently, so specified here.
TIME_PATTERN = r"""
(?P<time>
    ## Captures in format XX:YY(:ZZ) (PM) (EST)
    (
        (?P<hours>\d{{1,2}})
        \:
        (?P<minutes>\d{{1,2}})
        (\:(?<seconds>\d{{1,2}}))?
        ([\.\,](?<microseconds>\d{{1,6}}))?
        \s*
        (?P<time_periods>{time_periods})?
        \s*
        (?P<timezones>{timezones})?
    )
    |
    ## Captures in format 11 AM (EST)
    ## Note with single digit capture requires time period
    (
        (?P<hours>\d{{1,2}})
        \s*
        (?P<time_periods>{time_periods})
        \s*
        (?P<timezones>{timezones})*
    )
)
""".format(
    time_periods=TIME_PERIOD_PATTERN, timezones=ALL_TIMEZONES_PATTERN
)

DATES_PATTERN = """
(
    ## Undelimited datestamps (treated independently)
    (?P<undelimited_stamps>{undelimited_stamps})
    |
    (
        {time}
        |
        ## Grab any four digit years
        (?P<years>{years})
        |
        ## Numbers
        (?P<numbers>{numbers})
        ## Grab any digits
        |
        (?P<digits>{digits})(?P<digits_suffixes>{digits_suffixes})?
        |
        (?P<days>{days})
        |
        (?P<months>{months})
        |
        ## Delimiters, ie Tuesday[,] July 18 or 6[/]17[/]2008
        ## as well as whitespace
        (?P<delimiters>{delimiters})
        |
        (?P<positionnal_tokens>{positionnal_tokens})
        |
        ## These tokens could be in phrases that dateutil does not yet recognize
        ## Some are US Centric
        (?P<extra_tokens>{extra_tokens})
    ## We need at least three items to match for minimal datetime parsing
    ## ie 10pm
    ){{1,1}}
)
"""

DATES_PATTERN = DATES_PATTERN.format(
    time=TIME_PATTERN,
    undelimited_stamps=UNDELIMITED_STAMPS_PATTERN,
    years=YYYY_PATTERN,
    numbers=NUMBERS_PATTERN,
    digits=DIGITS_PATTERN,
    digits_suffixes=DIGITS_SUFFIXES,
    days=DAYS_PATTERN,
    months=MONTHS_PATTERN,
    delimiters=DELIMITERS_PATTERN,
    positionnal_tokens=POSITIONNAL_TOKENS,
    extra_tokens=EXTRA_TOKENS_PATTERN,
)

ALL_GROUPS = ['time', 'years', 'numbers', 'digits', 'digits_suffixes', 'days',
              'months', 'delimiters', 'positionnal_tokens', 'extra_tokens',
              'undelimited_stamps', 'hours', 'minutes', 'seconds', 'microseconds',
              'time_periods', 'timezones']

DATE_REGEX = re.compile(
    DATES_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE
)

TIME_REGEX = re.compile(
    TIME_PATTERN, re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL | re.VERBOSE
)

## These tokens can be in original text but dateutil
## won't handle them without modification
REPLACEMENTS = {
    "standard": " ",
    "daylight": " ",
    "savings": " ",
    "time": " ",
    "date": " ",
    "by": " ",
    "due": " ",
    "on": " ",
    "to": " ",
    "day": " ",
}

TIMEZONE_REPLACEMENTS = {
    "pacific": "PST",
    "eastern": "EST",
    "mountain": "MST",
    "central": "CST",
}

## Characters that can be removed from ends of matched strings
STRIP_CHARS = " \n\t:-.,_"

# split ranges
RANGE_SPLIT_PATTERN = r'\Wto\W|\Wthrough\W'

RANGE_SPLIT_REGEX =  re.compile(RANGE_SPLIT_PATTERN,
    re.IGNORECASE | re.MULTILINE | re.UNICODE | re.DOTALL)
