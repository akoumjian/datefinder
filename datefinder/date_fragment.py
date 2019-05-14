'''
This class describes big chunks of text that may contain date strings
Each chunk includes of one of more tokens
Each token is build upon DATE_REGEX matches
'''


class DateFragment:
    def __init__(self):
        self.match_str = ''
        self.indices = (0, 0)
        self.captures = {}

    def __repr__(self):
        str_capt = ', '.join(['"{}": [{}]'.format(c, self.captures[c]) for c in self.captures])
        return '{} [{}, {}]\nCaptures: {}'.format(self.match_str, self.indices[0], self.indices[1], str_capt)

    def get_captures_count(self):
        return sum([len(self.captures[m]) for m in self.captures])
