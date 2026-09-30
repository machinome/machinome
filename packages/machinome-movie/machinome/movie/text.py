"""Counting a phrase in a narration, words in a phrase and tokens in a
source excerpt: the three rules an anchor and an emphasis are checked by.

Both character classes are ASCII so that the Node side, whose regular
expressions are ASCII, counts exactly as this does.
"""

import re

#: What a source token is: an identifier, or a dotted path of identifiers,
#: so that `waterwheel` and `feed.pawl.turn` are both tokens.
TOKEN = re.compile(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*')

_WORD = '[A-Za-z0-9_]'


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
    """How many times `token` occurs in `text`, word-bounded: not preceded
    or followed by a letter, a digit or an underscore. A dot is a boundary,
    so `waterwheel` occurs in `water_drive.waterwheel.spin` and `feed.pawl`
    in `feed.pawl.turn`, while `pawl` does not occur in `pawl_mount`."""
    return len(re.findall(rf'(?<!{_WORD}){re.escape(token)}(?!{_WORD})', text))


def excerpt_line(text, first, line):
    """The text of `line` (a file line number) in an excerpt whose first
    line is `first`, or None when the line is outside the excerpt."""
    lines = text.split('\n')
    index = line - first
    return lines[index] if 0 <= index < len(lines) else None
