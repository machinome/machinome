"""A chapter's narration and the anchors made from it.

An anchor is symbolic: a phrase of the narration, the end of a phrase, or
the end of the whole narration, each with an optional offset in seconds.
The renderer resolves it against the recorded speech; nothing here reads
speech.
"""

import math
import re

from .names import MovieError, number
from .text import count_phrase


class Narration:
    """A chapter's lines, spoken as one continuous take."""

    def __init__(self, text):
        if not isinstance(text, str) or not text.split():
            raise MovieError('A Narration needs its lines as text')
        # Whitespace runs fold to one space, so a triple-quoted paragraph and
        # a concatenated one are the same narration.
        self.text = ' '.join(text.split())

    def spoken(self, phrase, plus=0):
        """The instant the narrator begins `phrase`."""
        return Anchor('spoken', phrase, plus, self)

    def spoken_end(self, phrase, plus=0):
        """The instant the narrator finishes `phrase`."""
        return Anchor('spokenEnd', phrase, plus, self)

    def end(self, plus=0):
        """The instant the narrator finishes the whole narration."""
        return Anchor('end', None, plus, self)

    def count(self, phrase):
        """How many times `phrase` occurs, overlapping occurrences included."""
        return count_phrase(self.text, phrase)

    def tail(self):
        """The shortest run of the last words that occurs exactly once,
        edge punctuation removed: the phrase whose end is the narration's."""
        starts = [match.start() for match in re.finditer(r'\S+', self.text)]
        for start in reversed(starts):
            phrase = re.sub(r'^\W+|\W+$', '', self.text[start:])
            if phrase and self.count(phrase) == 1:
                return phrase
        raise MovieError(f"The narration {self.text!r} has no ending that occurs "
                         f"once, so its end cannot be named")


class Anchor:
    """A named instant of a chapter's narration."""

    def __init__(self, kind, phrase, plus, narration):
        if kind != 'end' and (not isinstance(phrase, str) or not phrase.strip()):
            raise MovieError(f'An anchor needs a phrase of the narration, not {phrase!r}')
        if (isinstance(plus, bool) or not isinstance(plus, (int, float))
                or not math.isfinite(plus)):
            raise MovieError(f'plus={plus!r} is not a number of seconds')
        self.kind, self.phrase, self.plus, self.narration = kind, phrase, plus, narration

    def _key(self):
        return (self.kind, self.phrase, self.plus, id(self.narration))

    def __eq__(self, other):
        return isinstance(other, Anchor) and self._key() == other._key()

    def __hash__(self):
        return hash(self._key())

    def shifted(self, seconds):
        return Anchor(self.kind, self.phrase, self.plus + seconds, self.narration)

    def written(self):
        name = {'spoken': 'spoken', 'spokenEnd': 'spoken_end', 'end': 'end'}[self.kind]
        arguments = [] if self.phrase is None else [repr(self.phrase)]
        if self.plus:
            arguments.append(f'plus={self.plus!r}')
        return f"lines.{name}({', '.join(arguments)})"

    def check(self, narration, where):
        """Refuse an anchor of another narration, and a phrase absent from
        or repeated in this one."""
        if self.narration is not narration:
            raise MovieError(f"{where}: {self.written()} is an anchor of another "
                             f"narration, not of this chapter's")
        if self.kind == 'end':
            self.narration.tail()
            return
        found = narration.count(self.phrase)
        if found == 0:
            raise MovieError(f"{where}: the phrase '{self.phrase}' is absent from the "
                             f"chapter's narration")
        if found > 1:
            raise MovieError(f"{where}: the phrase '{self.phrase}' is ambiguous in the "
                             f"chapter's narration: it occurs {found} times, and an anchor "
                             f"names one instant, so write a longer phrase")

    def document(self):
        if self.kind == 'end':
            written = {'spokenEnd': self.narration.tail()}
        else:
            written = {self.kind: self.phrase}
        if self.plus:
            written['plus'] = self.plus
        return written


def time_value(value, where):
    """A shot-local time: seconds as written, or an anchor."""
    if isinstance(value, Anchor):
        return value
    return number(value, where)


def time_document(value):
    return value.document() if isinstance(value, Anchor) else value


def is_zero(value):
    return not isinstance(value, Anchor) and value == 0
