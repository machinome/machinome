"""What is on screen: sets with their slots, the elements a chapter
declares and shots place, the actions a cue performs, and the joins
between shots.

Until the React stage exists the sets are exactly the three layouts the
film page draws, and the elements are the view and the source panel; a
project's own set or element is refused where it is declared.
"""

import re

from .anchors import time_value
from .names import MovieError, ease, entrance, number, pair
from .take import Camera, Layer, Source, Still


def _built_in(cls, what):
    if not cls.__module__.startswith('machinome_movie'):
        raise MovieError(
            f"{what} {cls.__name__} is declared by the project; a project's own "
            f"{what.lower()} needs the React stage, which does not exist yet. "
            f"{'Use Paper, PaperSplit or SourceOnly.' if what == 'Set' else 'Use View or Source.panel.'}")


##############################################
# Sets and slots

class Slot:
    """A named place on a set that holds one element."""

    def __init__(self, holds):
        self.holds = holds
        self.name = self.set = None

    def __set_name__(self, owner, name):
        self.name, self.set = name, owner

    def __get__(self, instance, owner=None):
        # A fresh key on every read, so a slot written twice in one dict
        # literal stays two keys and can be refused.
        return Placement(self, owner)


class Placement:
    """A slot read off a set: the key a shot places an element under."""

    def __init__(self, slot, through):
        self.slot, self.through = slot, through


class Set:
    """A layout. A set's slots are the ones its own body declares; a derived
    set inherits the chrome, not the layout."""

    kind = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _built_in(cls, 'Set')

    @classmethod
    def slots(cls):
        return {name: value for name, value in vars(cls).items() if isinstance(value, Slot)}


class Paper(Set):
    """The film page: the model stage alone, with the film's chrome."""

    kind = 'paper'
    stage = Slot('view')

    @staticmethod
    def style(*, background=None, foreground=None, accent=None, font=None, safe_inset=None):
        """The film's look: colours, type and the safe inset."""
        return Style(background=background, foreground=foreground, accent=accent,
                     font=font, safe_inset=safe_inset)


class PaperSplit(Paper):
    """Pinned source on the left, the model on the right."""

    kind = 'paper-split'
    left = Slot('panel')
    right = Slot('view')


class SourceOnly(Paper):
    """Pinned source across the whole picture."""

    kind = 'source-only'
    source = Slot('panel')


class Style:
    _COLOR = re.compile(r'#[0-9a-fA-F]{6}')

    def __init__(self, *, background, foreground, accent, font, safe_inset):
        for name, value in (('background', background), ('foreground', foreground),
                            ('accent', accent)):
            if value is not None and not (isinstance(value, str) and self._COLOR.fullmatch(value)):
                raise MovieError(f"Paper.style: {name}={value!r} is not a '#rrggbb' colour")
        if font is not None and (not isinstance(font, str) or not font.strip()):
            raise MovieError(f'Paper.style: font={font!r} is not a font family')
        if safe_inset is not None:
            number(safe_inset, 'Paper.style: safe_inset')
            if safe_inset >= 0.5:
                raise MovieError(f'Paper.style: safe_inset={safe_inset!r} is not below 0.5')
        self.fields = {'background': background, 'foreground': foreground, 'accent': accent,
                       'fontFamily': font, 'safeInsetFraction': safe_inset}

    def document(self):
        return {key: value for key, value in self.fields.items() if value is not None}


##############################################
# Elements

class Element:
    """Content a chapter declares and its shots place in slots."""

    slot_kind = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        _built_in(cls, 'Element')


class View(Element):
    """A camera on a take. Its camera persists across the shots of its
    chapter; `move` changes it inside a shot."""

    slot_kind = 'view'

    def __init__(self, loop, *, camera, hide=()):
        self.loop, self.camera, self.hide = loop, camera, list(hide)

    def check(self, where):
        from .take import Loop

        if not (isinstance(self.loop, type) and issubclass(self.loop, Loop)):
            raise MovieError(f'{where}: a View looks at a Loop, not {self.loop!r}')
        _check_camera(self.camera, self.loop, where)
        for layer in self.hide:
            if not isinstance(layer, Layer) or not layer.declared_for(self.loop):
                owner = getattr(getattr(layer, 'loop', None), '__name__', None)
                raise MovieError(f'{where}: hide names {getattr(layer, "name", layer)!r}'
                                 f'{f", a layer of {owner}," if owner else ""} which is not a '
                                 f'layer declared on {self.loop.__name__}')

    def move(self, camera, *, until, ease=None):
        """Move from the current camera to `camera`, from the cue's anchor
        to `until`, along the easing curve."""
        return Move(self, camera, until, ease)

    def highlight(self, *parts, others=None):
        """Tint `parts` for the cue's span; keep, dim or ghost the others."""
        return Highlight(self, parts, others)


class SourcePanel(Element):
    """A pinned source excerpt, typed and emphasised on cue."""

    slot_kind = 'panel'

    def __init__(self, source):
        if not isinstance(source, Source) or source.loop is None:
            raise MovieError(f'Source.panel shows a Source declared on a Loop, not {source!r}')
        self.source = source
        self.loop = source.loop

    def type(self, *, through_line, over):
        """Type the excerpt through `through_line` over `over` seconds from
        the cue's anchor."""
        return Type(self, through_line, over)

    def emphasize(self, *words, hold=0):
        """Light `words` of the excerpt's last line as they are spoken in
        the cue's phrase, and hold them `hold` seconds after it ends."""
        return Emphasize(self, words, hold)


def _check_camera(camera, loop, where):
    if not isinstance(camera, Camera):
        raise MovieError(f'{where}: {camera!r} is not a Camera')
    if not camera.declared_for(loop):
        owner = camera.loop.__name__ if camera.loop is not None else 'no Loop'
        raise MovieError(f"{where}: camera {camera.name or '(unnamed)'} is declared on "
                         f"{owner}, not on {loop.__name__}, the take the view looks at")


##############################################
# Actions

class Action:
    """What a cue does. `element` is the element it acts on, if any;
    `spans` says whether it shows something from the cue's anchor to its
    until."""

    element = None
    spans = False
    label = 'action'


class Move(Action):
    label = 'move'

    def __init__(self, view, camera, until, curve):
        where = f"move to {getattr(camera, 'name', camera)}"
        self.element, self.camera = view, camera
        self.until = time_value(until, where)
        self.ease = None if curve is None else ease(curve, where)


class Highlight(Action):
    label = 'highlight'
    spans = True

    def __init__(self, view, parts, others):
        if not parts:
            raise MovieError('highlight names at least one part')
        if others is not None and others not in ('keep', 'dim', 'ghost'):
            raise MovieError(f'highlight: others={others!r} must be keep, dim or ghost')
        self.element, self.parts, self.others = view, parts, others


class Type(Action):
    label = 'type'

    def __init__(self, panel, through_line, over):
        if isinstance(through_line, bool) or not isinstance(through_line, int):
            raise MovieError(f'type: through_line={through_line!r} is not a line number')
        self.element, self.through_line = panel, through_line
        self.over = number(over, 'type: over', positive=True)


class Emphasize(Action):
    label = 'emphasize'

    def __init__(self, panel, words, hold):
        if not words or not all(isinstance(w, str) and w for w in words):
            raise MovieError(f'emphasize names the words to light, not {words!r}')
        self.element, self.words, self.hold = panel, list(words), number(hold, 'emphasize: hold')


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


class Title(Action):
    """Words on the frame over the picture: a title with an optional
    subtitle, or a line at the top, lower third or centre."""

    label = 'title'
    spans = True
    POSITIONS = ('title', 'top', 'lower-third', 'center')

    def __init__(self, text, *, position='title', subtitle=None, enter=None, leave=None,
                 reveal=None):
        where = f"Title '{text}'"
        if not isinstance(text, str) or not text.strip():
            raise MovieError(f'A Title needs its text, not {text!r}')
        if position not in self.POSITIONS:
            raise MovieError(f"{where}: position {position!r} must be title, top, "
                             f"lower-third or center")
        if position != 'title' and (subtitle is not None or enter is not None or leave is not None):
            raise MovieError(f"{where}: subtitle, enter and leave belong to a title "
                             f"(position 'title'), not to position '{position}'")
        if subtitle is not None and (not isinstance(subtitle, str) or not subtitle.strip()):
            raise MovieError(f'{where}: subtitle={subtitle!r} is not text')
        if reveal is not None and not isinstance(reveal, Reveal):
            raise MovieError(f'{where}: reveal is Reveal.spoken(), not {reveal!r}')
        self.text, self.position, self.subtitle, self.reveal = text, position, subtitle, reveal
        self.enter = entrance(enter, f'{where}: enter', ('fade',))
        self.leave = entrance(leave, f'{where}: leave', ('fade',))

    def document(self, start, end):
        written = {'from': start, 'to': end, 'text': self.text, 'position': self.position}
        for key, value in (('subtitle', self.subtitle), ('enter', self.enter),
                           ('leave', self.leave)):
            if value is not None:
                written[key] = value
        if self.reveal is not None:
            written['reveal'] = self.reveal.document()
        return written


class _Annotation(Action):
    """A mark that points at a part and follows it."""

    spans = True
    ENTER = ('fade', 'draw')

    def _entrances(self, where, enter, leave):
        self.enter = entrance(enter, f'{where}: enter', self.ENTER)
        self.leave = entrance(leave, f'{where}: leave', ('fade',))

    def document(self, start, end, part):
        written = {'from': start, 'to': end, 'kind': self.label, 'part': part}
        for key in ('text', 'place', 'offset', 'enter', 'leave'):
            value = getattr(self, key, None)
            if value is not None:
                written[key] = value
        return written


class Ring(_Annotation):
    """An ellipse drawn around a part."""

    label = 'ring'

    def __init__(self, part, *, enter=None, leave=None):
        self.part = part
        self._entrances('Ring', enter, leave)


class Label(_Annotation):
    """Words beside a part."""

    label = 'label'
    ENTER = ('fade',)

    def __init__(self, part, text, *, offset=None, enter=None, leave=None):
        if not isinstance(text, str) or not text.strip():
            raise MovieError(f'A Label needs its text, not {text!r}')
        self.part, self.text = part, text
        self.offset = None if offset is None else pair(offset, f"Label '{text}': offset")
        self._entrances(f"Label '{text}'", enter, leave)


class Arrow(_Annotation):
    """An arrow from words placed on the frame to a part."""

    label = 'arrow'

    def __init__(self, part, text=None, *, place, enter=None, leave=None):
        if text is not None and (not isinstance(text, str) or not text.strip()):
            raise MovieError(f'An Arrow text is words or None, not {text!r}')
        self.part, self.text = part, text
        self.place = pair(place, f"Arrow '{text}': place")
        self._entrances(f"Arrow '{text}'", enter, leave)


class Picture(Action):
    """A still shown over the stage or the frame."""

    label = 'show'
    spans = True

    def __init__(self, still, *, area, fit, enter, leave, view):
        where = f'{still.name}.show'
        if area not in (None, 'stage', 'frame'):
            raise MovieError(f'{where}: area {area!r} must be stage or frame')
        if fit not in (None, 'contain', 'cover'):
            raise MovieError(f'{where}: fit {fit!r} must be contain or cover')
        self.still, self.area, self.fit = still, area, fit
        self.enter = entrance(enter, f'{where}: enter', ('fade',))
        self.leave = entrance(leave, f'{where}: leave', ('fade',))
        self.view = []
        for index, key in enumerate(view):
            here = f'{where}: view[{index}]'
            if not isinstance(key, tuple) or len(key) not in (3, 4):
                raise MovieError(f'{here}: {key!r} is not (at, center, zoom[, ease])')
            written = {'at': time_value(key[0], here), 'center': pair(key[1], here),
                       'zoom': number(key[2], here, positive=True)}
            if len(key) == 4:
                written['ease'] = ease(key[3], here)
            self.view.append(written)


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
