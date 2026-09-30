"""The refusal type, the naming rule and the small vocabularies every
declaration shares: easing curves, times, entrances and exits."""

import math
import os
import re
import sys


class MovieError(Exception):
    """A movie that cannot be filmed as declared. The message names what is
    wrong and where: the movie or chapter, the shot, the field."""


_ATTRIBUTE = re.compile(r'[a-z0-9][a-z0-9_]*')

EASES = ('linear', 'smooth', 'in', 'out', 'in-out')


def slug(attribute, where, what):
    """The document name of the declaration held by `attribute`: the
    attribute itself with underscores as hyphens."""
    if not _ATTRIBUTE.fullmatch(attribute):
        raise MovieError(
            f"{where}: '{attribute}' cannot name a {what}; the attribute holding "
            f"a declaration is its name in the document, so it is written in "
            f"lower-case letters, digits and underscores")
    return attribute.replace('_', '-')


def ease(name, where):
    if name not in EASES:
        raise MovieError(f"Unknown easing: {name}; use linear, smooth, in, out or "
                         f"in-out ({where})")
    return name


def number(value, where, *, positive=False):
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < 0 or (positive and value == 0)):
        kind = 'a positive number' if positive else 'a number of seconds, zero or more'
        raise MovieError(f"{where}: {value!r} is not {kind}")
    return value


def pair(value, where):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                       and math.isfinite(v) for v in value)):
        raise MovieError(f"{where}: {value!r} is not a pair of numbers (x, y)")
    return list(value)


def entrance(value, where, kinds):
    """An entrance or exit: a number is a fade of that many seconds; a tuple
    is `(kind, duration)` or `(kind, duration, ease)`."""
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        value = ('fade', value)
    if not isinstance(value, tuple) or len(value) not in (2, 3):
        raise MovieError(f"{where}: {value!r} is not a duration or (kind, duration[, ease])")
    kind, duration = value[0], value[1]
    if kind not in kinds:
        raise MovieError(f"{where}: kind {kind!r} must be {' or '.join(kinds)}")
    written = {'kind': kind, 'duration': number(duration, where, positive=True)}
    if len(value) == 3:
        written['ease'] = ease(value[2], where)
    return written


def module_directory(klass):
    """The directory of the file a class is written in: the base every path
    that class declares is relative to."""
    module = sys.modules.get(klass.__module__)
    path = getattr(module, '__file__', None)
    if not path:
        raise MovieError(f"{klass.__qualname__} is not written in a file, so the paths "
                         f"it declares have nothing to be relative to")
    return os.path.dirname(os.path.abspath(path))


def declaring_class(klass, attribute):
    """The class in `klass`'s MRO whose own body assigns `attribute`."""
    for candidate in klass.__mro__:
        if attribute in vars(candidate):
            return candidate
    return None
