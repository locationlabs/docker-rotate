"""
Contains functions used in implementing image name filtering.
"""
import re


def regex_positive_match(pattern, value):
    """
    Return False if the regex is "positive" and is NOT a complete match for
    the supplied value, True otherwise.
    """
    if pattern[0] == '~':
        # this is a negative regex, ignore
        return True
    return re.match(pattern + '\Z', value)


def regex_negative_match(pattern, value):
    """
    Return False if the regex is "negative" and is a complete match for the
    supplied value, True otherwise.
    """
    if pattern[0] != '~':
        # this is a positive regex, ignore
        return True
    return not re.match(pattern[1:] + '\Z', value)
