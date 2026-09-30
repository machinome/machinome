"""Counting a phrase in a narration, words in a phrase and tokens in a
source excerpt: the three rules an anchor and an emphasis are checked by.

Both character classes are ASCII so that the Node side, whose regular
expressions are ASCII, counts exactly as this does.
"""

import re

#: What a source token is: an identifier, dots included, so that
#: `feed.pawl.turn` is one token.
TOKEN = re.compile(r'[A-Za-z_][A-Za-z0-9_.]*')

_WORD = '[A-Za-z0-9_]'
_IDENTIFIER = '[A-Za-z0-9_.]'


def count_phrase(text, phrase):
    """How many times `phrase` occurs in `text`, overlapping occurrences
    included: the rule a spoken anchor is checked by."""
    found, start = 0, 0
    while True:
        start = text.find(phrase, start)
        if start < 0:
            return found
        found, start = found + 1, start + 1


def count_words(phrase, words):
    """How many times `words` occur in `phrase`, word-bounded: not preceded
    or followed by a letter, a digit or an underscore."""
    return len(re.findall(rf'(?<!{_WORD}){re.escape(words)}(?!{_WORD})', phrase))


def count_token(text, token):
    """How many times `token` occurs in `text`, identifier-bounded: not
    preceded or followed by a letter, a digit, an underscore or a dot, so a
    segment of a dotted path is not the token."""
    return len(re.findall(rf'(?<!{_IDENTIFIER}){re.escape(token)}(?!{_IDENTIFIER})', text))
