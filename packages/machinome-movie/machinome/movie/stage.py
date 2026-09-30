"""What is on screen: sets with their slots, the elements a chapter declares
and shots place in them, the actions a cue performs on elements, and the
joins between shots.

A set is a layout and an element is content; the set does not know what it
holds. The tool ships the sets `Frame` and `Split` and the elements `View`,
the source panel, `Title` and `Picture`; a project declares its own sets and
elements by subclassing `Set` and `Element` with the stage module that draws
them. Python says what and when; the stage module says how it looks.
"""

import re
import types

from .anchors import Anchor, time_value
from .names import (MovieError, declaring_class, ease, entrance, json_value, kind_of,
                    module_path, number, pair, prop_kind, slug, SLUG)
from .take import Camera, Layer, Source, Still
from .text import TOKEN

#: Set kinds the stage runtime ships: two for movies, three for YAML
#: episodes. A project set cannot take one of them.
SHIPPED_SETS = ('frame', 'split', 'paper', 'paper-split', 'source-only')
#: Element kinds the tool ships.
SHIPPED_ELEMENTS = ('view', 'source', 'title', 'picture')
#: Names the classes use for their own questions, so no slot or prop may take them.
_RESERVED = ('slots', 'props', 'base', 'actions', 'project')
_MACHINERY = (types.FunctionType, staticmethod, classmethod, property)


def _shipped(cls):
    return cls.__module__ == 'machinome_movie' or cls.__module__.startswith('machinome_movie.')


def _own_kind(cls, where):
    written = vars(cls).get('kind')
    if written is None:
        return kind_of(cls.__name__)
    if not isinstance(written, str) or not SLUG.fullmatch(written):
        raise MovieError(f"{where}: kind {written!r} is not a kind; a kind is lower-case "
                         f"letters, digits and hyphens, as leonardo-split")
    return written


##############################################
# Sets and slots

class Slot:
    """A named place on a set that holds one element, whatever it is."""

    def __init__(self, *holds, **options):
        self._written = holds or options
        self.name = self.attribute = self.set = None

    def __set_name__(self, owner, name):
        self.attribute, self.set = name, owner

    def __get__(self, instance, owner=None):
        # A fresh key on every read, so a slot written twice in one dict
        # literal stays two keys and can be refused.
        return Placement(self, owner)


class Placement:
    """A slot read off a set: the key a shot places an element under."""

    def __init__(self, slot, through):
        self.slot, self.through = slot, through


class Set:
    """A layout with named slots and its own chrome. A set's slots are the
    ones its own body declares: a derived set inherits the chrome and the
    module, not the layout."""

    kind = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        where = f'Set {cls.__name__}'
        own = dict(vars(cls))
        cls.kind = _own_kind(cls, where)
        cls._slots = {}
        for name, value in own.items():
            if not isinstance(value, Slot):
                continue
            if value._written:
                raise MovieError(f"{where}: slot {name} is declared as Slot{value._written!r}; a "
                                 f"set does not know what it holds, so a slot is Slot()")
            value.name = slug(name, f'{where}.{name}', 'slot')
            cls._slots[value.name] = value
        cls._props = {}
        if _shipped(cls):
            return
        if cls.kind in SHIPPED_SETS:
            raise MovieError(f"{where}: its kind {cls.kind} is a set the tool ships; name the "
                             f"project's set differently or write kind = \"...\"")
        module_path(getattr(cls, 'module', None), where)
        for name, value in own.items():
            if name.startswith('_') or name in ('module', 'kind') or isinstance(value, (Slot,) + _MACHINERY):
                continue
            if name in _RESERVED:
                raise MovieError(f"{where}: '{name}' is the name the set answers a question by; "
                                 f"call the prop or slot something else")
            cls._props[name] = json_value(value, f'{where}: prop {name} (a class attribute) must be JSON')

    @classmethod
    def slots(cls):
        """The set's own slots, by name, in declaration order."""
        return dict(cls._slots)

    @classmethod
    def props(cls):
        """The static props the set's component receives."""
        return dict(cls._props)

    @classmethod
    def base(cls):
        """The set this one derives from, or None."""
        for klass in cls.__mro__[1:]:
            if klass is Set:
                return None
            if isinstance(klass, type) and issubclass(klass, Set):
                return klass
        return None

    @classmethod
    def project(cls):
        """Whether the project draws this set, rather than the tool."""
        return not _shipped(cls)

    @classmethod
    def module_owner(cls):
        return declaring_class(cls, 'module')


class Frame(Set):
    """The whole picture, one slot, no chrome."""

    kind = 'frame'
    stage = Slot()


class Split(Set):
    """Two containers side by side."""

    kind = 'split'
    left = Slot()
    right = Slot()


class Style:
    """The movie's palette and type, which its root set reads."""

    _COLOR = re.compile(r'#[0-9a-fA-F]{6}')

    def __init__(self, *, background=None, foreground=None, accent=None, font=None,
                 safe_inset=None):
        for name, value in (('background', background), ('foreground', foreground),
                            ('accent', accent)):
            if value is not None and not (isinstance(value, str) and self._COLOR.fullmatch(value)):
                raise MovieError(f"Style: {name}={value!r} is not a '#rrggbb' colour")
        if font is not None and (not isinstance(font, str) or not font.strip()):
            raise MovieError(f'Style: font={font!r} is not a font family')
        if safe_inset is not None:
            number(safe_inset, 'Style: safe_inset')
            if safe_inset >= 0.5:
                raise MovieError(f'Style: safe_inset={safe_inset!r} is not below 0.5')
        self.fields = {'background': background, 'foreground': foreground, 'accent': accent,
                       'fontFamily': font, 'safeInsetFraction': safe_inset}

    def document(self):
        return {key: value for key, value in self.fields.items() if value is not None}


##############################################
# Elements

class Element:
    """Content a chapter declares and its shots place in slots. A project's
    element declares its `module` and its `Action`s; an instance's keyword
    arguments are its props."""

    kind = None
    loop = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if _shipped(cls):
            return
        where = f'Element {cls.__name__}'
        for klass in cls.__mro__[1:]:
            if klass is Element:
                break
            if _shipped(klass):
                raise MovieError(f"{where} derives from the tool's {klass.__name__}; a project's "
                                 f"element derives from Element")
        if 'kind' in vars(cls):
            raise MovieError(f"{where}: an element's kind is its class name's slug, "
                             f"{kind_of(cls.__name__)}; it is not written")
        cls.kind = kind_of(cls.__name__)
        if not SLUG.fullmatch(cls.kind):
            raise MovieError(f"{where}: its kind {cls.kind!r} is not a kind; name the class "
                             f"with letters and digits")
        if cls.kind in SHIPPED_ELEMENTS:
            raise MovieError(f"{where}: its kind {cls.kind} is an element the tool ships; name "
                             f"the project's element differently")
        module_path(getattr(cls, 'module', None), where)
        for name, value in vars(cls).items():
            if name.startswith('_') or name in ('module', 'kind') or isinstance(value, _MACHINERY):
                continue
            if isinstance(value, Action):
                value.check(cls)
                continue
            raise MovieError(f"{where}: '{name}' is neither its module, an Action nor a method; "
                             f"an element's props are given where a chapter declares it, as "
                             f"{cls.__name__}({name}=...)")

    def __init__(self, *args, **props):
        cls = type(self)
        if cls is Element or _shipped(cls):
            raise MovieError('Element is the base of the elements a project declares; declare a '
                             'subclass with its module and actions')
        where = f'{cls.__name__}'
        if args:
            raise MovieError(f'{where}: props are given by name, not positional, as '
                             f'{cls.__name__}(name=value)')
        self.props = {}
        for name, value in props.items():
            written = json_value(value, f'{where}: prop {name} must be JSON')
            if prop_kind(written) is None:
                raise MovieError(f'{where}: prop {name} is None, which has no kind; a prop is '
                                 f'text, a number, True or False, a list or a dict')
            self.props[name] = written

    @classmethod
    def actions(cls):
        """The actions the element declares, by name, with their parameters'
        kinds."""
        found = {}
        for klass in reversed(cls.__mro__):
            for value in vars(klass).values():
                if isinstance(value, Action):
                    found[value.name] = value.kinds()
        return found

    @classmethod
    def project(cls):
        return not _shipped(cls)

    @classmethod
    def module_owner(cls):
        return declaring_class(cls, 'module')

    def document(self):
        return {'kind': self.kind, 'props': dict(self.props)}

    def check(self, where):
        """Refuse what the element names that its take does not declare."""


class Action:
    """An action a project's element can perform on cue, with typed
    parameters: `light = Action(job=str)`."""

    KINDS = {str: 'string', int: 'number', float: 'number', bool: 'boolean'}

    def __init__(self, **params):
        self.params = params
        self.attribute = self.name = self.owner = None

    def __set_name__(self, owner, name):
        self.attribute, self.owner = name, owner

    def check(self, element):
        where = f'Element {element.__name__}'
        self.name = slug(self.attribute, f'{where}.{self.attribute}', 'action')
        for param, kind in self.params.items():
            if kind not in self.KINDS:
                raise MovieError(f"{where}: action {self.name}: parameter {param} is typed "
                                 f"{getattr(kind, '__name__', kind)!s}; a parameter is str, int, "
                                 f"float or bool")

    def kinds(self):
        return {param: self.KINDS[kind] for param, kind in self.params.items()}

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        def perform(*args, **params):
            return self.perform(instance, args, params)
        perform.__name__ = self.attribute
        return perform

    def perform(self, element, args, params):
        where = f'{type(element).__name__}.{self.name}'
        if args:
            raise MovieError(f'{where}: parameters are given by keyword, as '
                             f'{self.attribute}({", ".join(f"{p}=..." for p in self.params)})')
        for param in params:
            if param not in self.params:
                declared = ', '.join(self.params) or 'no parameters'
                raise MovieError(f'{where}: the action does not declare the parameter {param}; '
                                 f'it declares {declared}')
        for param, kind in self.params.items():
            if param not in params:
                raise MovieError(f'{where}: the parameter {param} is missing')
            value = params[param]
            if kind is bool:
                right = isinstance(value, bool)
            elif kind is int:
                right = isinstance(value, int) and not isinstance(value, bool)
            elif kind is float:
                right = (isinstance(value, (int, float)) and not isinstance(value, bool)
                         and value == value and value not in (float('inf'), float('-inf')))
            else:
                right = isinstance(value, str)
            if not right:
                wanted = 'a whole number' if kind is int else self.KINDS[kind]
                raise MovieError(f'{where}: the parameter {param} is {value!r}, and the action '
                                 f'declares it {self.KINDS[kind]}; give {wanted}')
        return Cued(element, self.name, spans=True, params=dict(params))


class View(Element):
    """A camera on the take. The camera continues across the shots of its
    chapter; `move` changes it inside a shot, and the marks point into it."""

    kind = 'view'

    def __init__(self, loop, *, camera, hide=()):
        self.loop, self.camera, self.hide = loop, camera, list(hide)

    def check(self, where):
        from .take import Loop

        if not (isinstance(self.loop, type) and issubclass(self.loop, Loop)):
            raise MovieError(f'{where}: a View looks at a Loop, not {self.loop!r}')
        check_camera(self.camera, self.loop, where)
        for layer in self.hide:
            if not isinstance(layer, Layer) or not layer.declared_for(self.loop):
                owner = getattr(getattr(layer, 'loop', None), '__name__', None)
                raise MovieError(f'{where}: hide names {getattr(layer, "name", layer)!r}'
                                 f'{f", a layer of {owner}," if owner else ""} which is not a '
                                 f'layer declared on {self.loop.__name__}')

    def document(self):
        written = {'kind': 'view', 'camera': self.camera.document_name()}
        if self.hide:
            written['hide'] = [layer.document_name() for layer in self.hide]
        return written

    def move(self, camera, *, until, ease=None):
        """Move from the current camera to `camera`, from the cue's anchor to
        `until`, along the easing curve."""
        where = f"move to {getattr(camera, 'name', camera)}"
        fields = {'camera': camera, 'until': time_value(until, where)}
        if ease is not None:
            fields['ease'] = _ease(ease, where)
        return Cued(self, 'move', fields=fields)

    def highlight(self, *parts, others=None):
        """Tint `parts` for the cue's span; keep, dim or ghost the others."""
        if not parts:
            raise MovieError('highlight names at least one part')
        fields = {'parts': list(parts)}
        if others is not None:
            if others not in ('keep', 'dim', 'ghost'):
                raise MovieError(f'highlight: others={others!r} must be keep, dim or ghost')
            fields['others'] = others
        return Cued(self, 'highlight', spans=True, fields=fields)

    def ring(self, part, *, enter=None, leave=None):
        """An ellipse drawn around a part, for the cue's span."""
        return Cued(self, 'ring', spans=True,
                    fields=_mark('ring', part, enter, leave, ('fade', 'draw')))

    def label(self, part, text, *, offset=None, enter=None, leave=None):
        """Words beside a part, for the cue's span; `offset` is a fraction of
        the view's box."""
        if not isinstance(text, str) or not text.strip():
            raise MovieError(f'label: a label needs its text, not {text!r}')
        fields = _mark(f"label '{text}'", part, enter, leave, ('fade',))
        fields['text'] = text
        if offset is not None:
            fields['offset'] = pair(offset, f"label '{text}': offset")
        return Cued(self, 'label', spans=True, fields=fields)

    def arrow(self, part, text=None, *, place, enter=None, leave=None):
        """An arrow from words placed in the view's box to a part."""
        if text is not None and (not isinstance(text, str) or not text.strip()):
            raise MovieError(f'arrow: the text is words or None, not {text!r}')
        fields = _mark(f"arrow '{text}'", part, enter, leave, ('fade', 'draw'))
        if text is not None:
            fields['text'] = text
        fields['place'] = pair(place, f"arrow '{text}': place")
        return Cued(self, 'arrow', spans=True, fields=fields)


def _mark(where, part, enter, leave, enters):
    fields = {'part': part}
    for key, value, kinds in (('enter', enter, enters), ('leave', leave, ('fade',))):
        written = entrance(value, f'{where}: {key}', kinds)
        if written is not None:
            fields[key] = written
    return fields


class SourcePanel(Element):
    """A pinned source excerpt, typed and emphasised on cue."""

    kind = 'source'

    def __init__(self, source):
        if not isinstance(source, Source) or source.loop is None:
            raise MovieError(f'Source.panel shows a Source declared on a Loop, not {source!r}')
        self.source = source
        self.loop = source.loop

    def document(self):
        return {'kind': 'source', 'source': self.source.document_name()}

    def type(self, *, through_line, over):
        """Type the excerpt from where the typing stopped through
        `through_line`, over `over` seconds from the cue's anchor."""
        if isinstance(through_line, bool) or not isinstance(through_line, int):
            raise MovieError(f'type: through_line={through_line!r} is not a line number')
        return Cued(self, 'type', fields={'throughLine': through_line,
                                          'over': number(over, 'type: over', positive=True)})

    def emphasize(self, *words, hold=None):
        """Light tokens of the excerpt as their words are spoken in the cue's
        phrase, and hold them `hold` seconds after it ends. A word is a
        token spelled as it is spoken, or `(spoken words, token)`."""
        if not words:
            raise MovieError('emphasize names the words to light')
        pairs = []
        for word in words:
            if isinstance(word, str):
                word = (word, word)
            if (not isinstance(word, tuple) or len(word) != 2
                    or not all(isinstance(part, str) and part.strip() for part in word)):
                raise MovieError(f'emphasize: {word!r} is not one of its words; a word is a token '
                                 f'as it is spoken, or ("spoken words", "token")')
            spoken, token = word
            if not TOKEN.fullmatch(token):
                raise MovieError(f"emphasize: '{token}' is not a source token; a token is an "
                                 f"identifier, dots included, as feed.pawl.turn")
            pairs.append({'spoken': spoken, 'token': token})
        fields = {'words': pairs}
        if hold is not None:
            fields['hold'] = number(hold, 'emphasize: hold')
        return Cued(self, 'emphasize', fields=fields)


class Reveal:
    """How a title's words appear."""

    def __init__(self, timing):
        self.timing = timing

    @classmethod
    def spoken(cls):
        """Each word appears as the narrator speaks it."""
        return cls('spoken')

    def document(self):
        return {'timing': self.timing}


class Title(Element):
    """Words in a slot: a title with an optional subtitle, shown on cue."""

    kind = 'title'

    def __init__(self, text, *, subtitle=None):
        if not isinstance(text, str) or not text.strip():
            raise MovieError(f'A Title needs its text, not {text!r}')
        if subtitle is not None and (not isinstance(subtitle, str) or not subtitle.strip()):
            raise MovieError(f"Title '{text}': subtitle={subtitle!r} is not text")
        self.text, self.subtitle = text, subtitle

    def document(self):
        written = {'kind': 'title', 'text': self.text}
        if self.subtitle is not None:
            written['subtitle'] = self.subtitle
        return written

    def show(self, *, enter=None, leave=None, reveal=None):
        """Show the title for the cue's span, with fades and an optional
        spoken reveal."""
        where = f"Title '{self.text}'.show"
        fields = _entrances(where, enter, leave)
        if reveal is not None:
            if not isinstance(reveal, Reveal):
                raise MovieError(f'{where}: reveal is Reveal.spoken(), not {reveal!r}')
            fields['reveal'] = reveal.document()
        return Cued(self, 'show', spans=True, fields=fields)


class Picture(Element):
    """A still of the take in a slot, shown on cue with fades and a keyed
    pan and zoom."""

    kind = 'picture'

    def __init__(self, still, *, fit=None):
        if not isinstance(still, Still) or still.loop is None:
            raise MovieError(f'A Picture shows a Still declared on a Loop, not {still!r}')
        if fit not in (None, 'contain', 'cover'):
            raise MovieError(f'Picture {still.name}: fit {fit!r} must be contain or cover')
        self.still, self.fit, self.loop = still, fit, still.loop

    def document(self):
        written = {'kind': 'picture', 'still': self.still.document_name()}
        if self.fit is not None:
            written['fit'] = self.fit
        return written

    def show(self, *, enter=None, leave=None, view=()):
        """Show the picture for the cue's span; each view key is `(at,
        center, zoom[, ease])`, `at` a time or an anchor."""
        where = f'Picture {self.still.name}.show'
        fields = _entrances(where, enter, leave)
        keys = []
        for index, key in enumerate(view):
            here = f'{where}: view[{index}]'
            if not isinstance(key, tuple) or len(key) not in (3, 4):
                raise MovieError(f'{here}: {key!r} is not (at, center, zoom[, ease])')
            written = {'at': time_value(key[0], here), 'center': pair(key[1], here),
                       'zoom': number(key[2], here, positive=True)}
            if len(key) == 4:
                written['ease'] = _ease(key[3], here)
            keys.append(written)
        if keys:
            fields['view'] = keys
        return Cued(self, 'show', spans=True, fields=fields)


def _entrances(where, enter, leave):
    fields = {}
    for key, value in (('enter', enter), ('leave', leave)):
        written = entrance(value, f'{where}: {key}', ('fade',))
        if written is not None:
            fields[key] = written
    return fields


def check_camera(camera, loop, where):
    if not isinstance(camera, Camera):
        raise MovieError(f'{where}: {camera!r} is not a Camera')
    if not camera.declared_for(loop):
        owner = camera.loop.__name__ if camera.loop is not None else 'no Loop'
        raise MovieError(f"{where}: camera {camera.name or '(unnamed)'} is declared on "
                         f"{owner}, not on {loop.__name__}, the take the view looks at")


##############################################
# Actions performed on cue

class Cued:
    """An action of a cue: what `element` does, named `name`. `fields` are
    its document fields as written (cameras, parts and anchors are resolved
    when the chapter compiles); `params` a project action's parameters.
    `spans` says whether it shows something from the cue's anchor to its
    until."""

    def __init__(self, element, name, *, spans=False, fields=None, params=None):
        self.element, self.name, self.spans = element, name, spans
        self.fields = fields or {}
        self.params = params


##############################################
# Joins

class _Join:
    kind = None
    directions = False
    colors = False

    def __init__(self, duration, *, ease=None, direction=None, color=None):
        where = type(self).__name__
        self.duration = number(duration, where, positive=True)
        self.ease = None if ease is None else _ease(ease, where)
        if direction is not None and (not self.directions or direction not in ('left', 'right')):
            raise MovieError(f'{where}: direction {direction!r} must be left or right, on a wipe or slide')
        if color is not None and (not self.colors or not (isinstance(color, str)
                                                          and Style._COLOR.fullmatch(color))):
            raise MovieError(f"{where}: color {color!r} must be '#rrggbb', on a fade")
        self.direction, self.color = direction, color

    def document(self):
        written = {} if self.kind is None else {'kind': self.kind}
        written['duration'] = self.duration
        for key in ('direction', 'color', 'ease'):
            value = getattr(self, key)
            if value is not None:
                written[key] = value
        return written


def _ease(name, where):
    return ease(name, where)


class Transition(_Join):
    """How a shot comes in from the shot before it."""


class Dissolve(Transition):
    kind = 'dissolve'

    def __init__(self, duration, *, ease=None):
        super().__init__(duration, ease=ease)


class Fade(Transition):
    kind = 'fade'
    colors = True

    def __init__(self, duration, *, color=None, ease=None):
        super().__init__(duration, ease=ease, color=color)


class Wipe(Transition):
    kind = 'wipe'
    directions = True

    def __init__(self, duration, *, direction=None, ease=None):
        super().__init__(duration, ease=ease, direction=direction)


class Slide(Transition):
    kind = 'slide'
    directions = True

    def __init__(self, duration, *, direction=None, ease=None):
        super().__init__(duration, ease=ease, direction=direction)


class FadeIn(_Join):
    """The film fades up from a colour at its head."""

    colors = True

    def __init__(self, duration, *, color=None, ease=None):
        super().__init__(duration, ease=ease, color=color)


class FadeOut(_Join):
    """The film fades down to a colour at its tail."""

    colors = True

    def __init__(self, duration, *, color=None, ease=None):
        super().__init__(duration, ease=ease, color=color)
