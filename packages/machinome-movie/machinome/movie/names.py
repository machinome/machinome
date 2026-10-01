"""The refusal type, the naming rule and the small vocabularies every
declaration shares: easing curves, times, entrances and exits."""

import math
import os
import re
import sys
from fractions import Fraction


class MovieError(Exception):
    """A movie that cannot be filmed as declared. The message names what is
    wrong and where: the movie or chapter, the shot, the field."""


_ATTRIBUTE = re.compile(r'[a-z0-9][a-z0-9_]*')

#: Every id, kind, key and slot name in the document.
SLUG = re.compile(r'[a-z][a-z0-9-]*')

EASES = ('linear', 'smooth', 'in', 'out', 'in-out')

#: What a stage module may be.
MODULE_SUFFIXES = ('.ts', '.tsx', '.js', '.jsx')


def slug(attribute, where, what):
    """The document name of the declaration held by `attribute`: the
    attribute itself with underscores as hyphens."""
    if not _ATTRIBUTE.fullmatch(attribute):
        raise MovieError(
            f"{where}: '{attribute}' cannot name a {what}; the attribute holding "
            f"a declaration is its name in the document, so it is written in "
            f"lower-case letters, digits and underscores")
    return attribute.replace('_', '-')


def kind_of(class_name):
    """The kind a class publishes: its name as a slug, a hyphen before each
    capitalised word (`LeonardoSplit` is `leonardo-split`, `HTMLCard` is
    `html-card`)."""
    spaced = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', class_name)
    spaced = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', spaced)
    return spaced.replace('_', '-').lower()


def json_value(value, where):
    """`value` as JSON data, refused naming `where` if it is anything else:
    text, a whole or finite number, true or false, null, a list or a mapping
    with text keys, all the way down."""
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if math.isfinite(value):
            return value
    elif isinstance(value, list):
        return [json_value(item, where) for item in value]
    elif isinstance(value, dict):
        if all(isinstance(key, str) for key in value):
            return {key: json_value(item, where) for key, item in value.items()}
    raise MovieError(f"{where}: {value!r} is not a JSON value; a prop is text, a number, "
                     f"True or False, None, a list or a dict of them")


def prop_kind(value):
    """The document's kind of a JSON value, or None for null."""
    if isinstance(value, bool):
        return 'boolean'
    if isinstance(value, (int, float)):
        return 'number'
    if isinstance(value, str):
        return 'string'
    if isinstance(value, list):
        return 'list'
    if isinstance(value, dict):
        return 'object'
    return None


def module_path(value, where):
    """A stage module as written: a path ending in a TypeScript or
    JavaScript extension."""
    if not isinstance(value, str) or not value.endswith(MODULE_SUFFIXES):
        raise MovieError(f"{where}: module {value!r} is not a stage module; name the "
                         f"TypeScript or JavaScript file that draws it (.ts, .tsx, .js or .jsx), "
                         f"relative to this file")
    return value


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


def exact_seconds(seconds):
    """A number of seconds as the decimal its author wrote, exactly: read
    through its shortest form, so `1.2` is 6/5 and not the binary double
    nearest it (ADR-016). Sums of these are exact; `seconds_written` gives
    them back."""
    if isinstance(seconds, float):
        return Fraction(repr(float(seconds)))
    return Fraction(int(seconds))


def seconds_written(total):
    """An exact sum of seconds as the document writes it: the integer when it
    is whole, otherwise the double nearest it, whose shortest form is the
    sum's decimal (three steps of 1.2 s end at 3.6, never at
    3.5999999999999996)."""
    return int(total) if total.denominator == 1 else float(total)


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


def shared_views(outgoing, incoming, views):
    """The view elements two shots, in document form, both place: the keys
    of `views` in both shots' places, in the incoming shot's order."""
    held = set(outgoing['places'].values())
    return [key for key in incoming['places'].values() if key in views and key in held]


def no_view_in_both(outgoing, incoming):
    """The words a reframe without a view element in both shots is refused
    in, by the declarations and by both runtimes' document checks."""
    return (f'a reframe from shot {outgoing} into shot {incoming} moves a view element both '
            f'shots place, and there is no view element in both')
