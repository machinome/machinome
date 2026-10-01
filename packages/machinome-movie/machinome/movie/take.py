"""The take a movie films, and what is declared beside it for the camera:
cameras, layers, source excerpts and stills.

A take is a `Loop`, the posed loop of a machinome model with its marks (the
trivial take), or a `Take`, the steps a clocked machine is asked to make
with the seconds each is drawn over and the marks its shots cut on, which
evaluation records through the framework's simulation.

A part is named by the model class's own declarations (`Mill.feed.pawl`)
and resolved here to the names the export gives it.
"""

import math
import os
import re

from machinome.motion.couplings import PathRef
from machinome.node.declarative import ChildDeclaration, declared_children

from .anchors import Anchor, time_value
from .names import (MovieError, declaring_class, ease, module_directory, number,
                    slug)


_MARK = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')


def part_path(model, part, where):
    """`(written, names)`: the declaration path as written and the export
    path it names, the root's name excluded."""
    if isinstance(part, ChildDeclaration):
        root, segments = part, ()
        written = f'{model.__name__}.{part._name}'
    elif isinstance(part, PathRef):
        root, segments = part.root, part.segments
        written = f'{model.__name__}.{part.written}'
    else:
        raise MovieError(f"{where}: {part!r} is not a part; name a part by its "
                         f"declaration, as {model.__name__}.<child>")
    if root._name is None or declared_children(model).get(root._name) is not root:
        raise MovieError(f"{where}: {written} is not a part {model.__name__} declares")
    names = [_export_name(root, root._name)]
    klass = root.node_class
    for segment in segments:
        declaration = declared_children(klass).get(segment)
        if not isinstance(declaration, ChildDeclaration):
            raise MovieError(f"{where}: {written} does not end on a part; "
                             f"'{segment}' of {klass.__name__} is not a child")
        names.append(_export_name(declaration, segment))
        klass = declaration.node_class
    return written, names


def _export_name(declaration, attribute):
    name = declaration.kwargs.get('name')
    return name if isinstance(name, str) and name else attribute


class _Declared:
    """Something declared on a take (a Loop or a Take): it belongs to the
    first take that holds it and is named by that take's attribute."""

    kind = 'declaration'
    loop = None
    name = None

    def __set_name__(self, owner, name):
        if self.loop is None:
            self.loop, self.name = owner, name

    def document_name(self):
        return slug(self.name, f'{self.loop.__name__}.{self.name}', self.kind)

    def declared_for(self, loop):
        return self.loop is not None and isinstance(loop, type) and issubclass(loop, self.loop)


class Camera(_Declared):
    """A camera setup on the model: where it stands, what it looks at."""

    kind = 'camera'

    def __init__(self, *, position, target, fov, up=(0, 0, 1)):
        self.position, self.target, self.up = (self._vector(v, n) for v, n in
                                               ((position, 'position'), (target, 'target'), (up, 'up')))
        if (isinstance(fov, bool) or not isinstance(fov, (int, float))
                or not 0 < fov < 180):
            raise MovieError(f'Camera fov={fov!r} is not a field of view in degrees')
        self.fov = fov

    @staticmethod
    def _vector(value, name):
        if (not isinstance(value, (tuple, list)) or len(value) != 3
                or not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                           and math.isfinite(v) for v in value)):
            raise MovieError(f'Camera {name}={value!r} is not three numbers')
        return list(value)

    def document(self):
        return {'position': self.position, 'target': self.target, 'up': self.up,
                'fov': self.fov}


class Layer(_Declared):
    """Parts a view can hide together."""

    kind = 'layer'

    def __init__(self, *parts):
        if not parts:
            raise MovieError('A Layer names at least one part')
        self.parts = parts


class Source(_Declared):
    """A pinned excerpt of a Python file: inclusive, one-based lines."""

    kind = 'source excerpt'

    def __init__(self, file, *, lines):
        if not isinstance(file, str) or not file:
            raise MovieError(f'Source needs a file path, not {file!r}')
        if (not isinstance(lines, tuple) or len(lines) != 2
                or not all(isinstance(n, int) and not isinstance(n, bool) for n in lines)
                or not 1 <= lines[0] <= lines[1]):
            raise MovieError(f'Source {file}: lines={lines!r} is not (first, last)')
        self.file, self.lines = file, lines

    @staticmethod
    def panel(source):
        """The element that shows `source` in a slot: typed and emphasised on
        cue."""
        from .stage import SourcePanel

        return SourcePanel(source)


class Still(_Declared):
    """A picture file, with its credit and rights recorded for the release."""

    kind = 'still'

    def __init__(self, file, *, credit, rights, upscale=None):
        if not isinstance(file, str) or not file:
            raise MovieError(f'Still needs a file path, not {file!r}')
        for name, value in (('credit', credit), ('rights', rights)):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise MovieError(f'Still {file}: {name} is text or None, not {value!r}')
        if upscale is not None:
            number(upscale, f'Still {file}: upscale', positive=True)
        self.file, self.credit, self.rights, self.upscale = file, credit, rights, upscale


class Simulation:
    """Model time for one shot: a linear span, or keys on anchors."""

    def __init__(self, loop, start=None, end=None, keys=None):
        self.loop, self.start, self.end, self.keys = loop, start, end, keys

    def marks(self):
        values = [self.start, self.end] if self.keys is None else [v for _, v, _ in self.keys]
        return [v for v in values if isinstance(v, str)]

    def check(self, until, narration, where):
        known = self.loop.marks
        for mark in self.marks():
            if mark not in known:
                declared = ', '.join(known) or 'no marks'
                raise MovieError(f"{where}: model: unknown mark '{mark}' of "
                                 f"{self.loop.__name__}, which declares {declared}")
        if issubclass(self.loop, Take):
            values = [self.start, self.end] if self.keys is None else [v for _, v, _ in self.keys]
            for value in values:
                if not isinstance(value, str) and not 0 <= value <= self.loop.length:
                    raise MovieError(f"{where}: model: take time {value} s is outside the take "
                                     f"{self.loop.__name__}, 0 to {self.loop.length} s")
        if self.keys is None:
            return
        for index, (at, _, _) in enumerate(self.keys):
            if isinstance(at, Anchor):
                at.check(narration, f'{where}: model key {index}')
        first, last = self.keys[0][0], self.keys[-1][0]
        if isinstance(first, Anchor) or first != 0:
            raise MovieError(f"{where}: model keys must start at the shot's start, "
                             f"with a first key at 0")
        if not _same_time(last, until):
            raise MovieError(f"{where}: model keys must end at the shot's end, with a "
                             f"last key at its until")

    def document(self):
        def seconds(value):
            return {'mark': value} if isinstance(value, str) else value

        if self.keys is None:
            return {'from': seconds(self.start), 'to': seconds(self.end)}
        keys = []
        for at, value, curve in self.keys:
            key = {'at': at.document() if isinstance(at, Anchor) else at,
                   'seconds': seconds(value)}
            if curve is not None:
                key['ease'] = curve
            keys.append(key)
        return {'keys': keys}


def _same_time(a, b):
    if isinstance(a, Anchor) or isinstance(b, Anchor):
        return a == b
    return a == b


class _Take:
    """What every take declares and checks alike: `model`, `export`,
    `readiness` and its camera declarations, owned by the take that holds
    them. `Loop` and `Take` add their own time."""

    #: The word a refusal names the take's kind by.
    _what = 'take'

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if '_what' in vars(cls):
            # Loop and Take themselves: the kinds, not a take.
            return
        where = f'{cls._what} {cls.__name__}'
        for attribute in ('model', 'export', 'readiness'):
            if getattr(cls, attribute, None) is None:
                raise MovieError(f'{where} needs {attribute}')
        if not isinstance(cls.model, type):
            raise MovieError(f'{where}: model is the node class, not {cls.model!r}')
        if not isinstance(cls.export, str) or not cls.export:
            raise MovieError(f'{where}: export is the path of the export directory')
        if not isinstance(cls.readiness, str) or not cls.readiness.strip():
            raise MovieError(f'{where}: readiness says what the export does and does not show')
        cls._time(where)
        for name, value in vars(cls).items():
            if isinstance(value, _Declared) and value.loop is not cls:
                raise MovieError(
                    f"{where}.{name}: this {value.kind} is declared on "
                    f"{value.loop.__name__}; declare a new one here, or derive "
                    f"{cls.__name__} from {value.loop.__name__}")
        cls._layer_paths = {}
        for name, layer in cls.declarations(Layer).items():
            cls._layer_paths[name] = [part_path(cls.model, part, f'{where}.{name}')
                                      for part in layer.parts]

    @classmethod
    def _time(cls, where):
        """Check and derive the take's time: its marks, and a Take's steps."""

    @classmethod
    def declarations(cls, kind):
        """What the take declares of `kind`, by attribute, bases first."""
        found = {}
        for klass in reversed(cls.__mro__):
            if not issubclass(klass, _Take) or '_what' in vars(klass):
                continue
            for name, value in vars(klass).items():
                if isinstance(value, kind):
                    found[name] = value
        return found

    @classmethod
    def export_directory(cls):
        base = module_directory(declaring_class(cls, 'export'))
        return os.path.normpath(os.path.join(base, cls.export))

    @classmethod
    def run(cls, start, end):
        """Model time running linearly from `start` to `end` over the shot:
        model seconds of a loop or take seconds of a take, or mark names."""
        where = f'{cls.__name__}.run'
        for value in (start, end):
            if not isinstance(value, str):
                number(value, where)
        return Simulation(cls, start=start, end=end)

    @classmethod
    def keys(cls, keys):
        """Model time keyed on shot instants: `{anchor: mark}` or
        `{anchor: (mark, ease)}`, the first at 0 and the last at the shot's
        until. The ease shapes the segment that ends at its key."""
        where = f'{cls.__name__}.keys'
        if not isinstance(keys, dict) or len(keys) < 2:
            raise MovieError(f'{where} takes a mapping of at least two keys')
        written = []
        for at, value in keys.items():
            time_value(at, where)
            curve = None
            if isinstance(value, tuple):
                if len(value) != 2:
                    raise MovieError(f'{where}: {value!r} is not (mark, ease)')
                value, curve = value[0], ease(value[1], where)
            if not isinstance(value, str):
                number(value, where)
            written.append((at, value, curve))
        return Simulation(cls, keys=written)


class Loop(_Take):
    """The posed loop of a model: the trivial take. A subclass carries
    `model`, `export`, `marks`, `readiness` and its camera declarations."""

    _what = 'Loop'

    @classmethod
    def _time(cls, where):
        marks = getattr(cls, 'marks', None) or {}
        for name, seconds in marks.items():
            if not isinstance(name, str) or not _MARK.fullmatch(name):
                raise MovieError(f"{where}: mark {name!r} is not a name; a mark is named "
                                 f"with letters, digits and underscores, as pull_start")
            number(seconds, f'{where}: mark {name}')
        cls.marks = dict(marks)


##############################################
# A clocked take

class Move:
    """A step of a take: move one input of the machine to a value (`to=`) or
    by a travel (`by=`), in design units, drawn over `over` seconds."""

    def __init__(self, input, *, to=None, by=None, over=None):
        self.input, self.to, self.by, self.over = input, to, by, over


class Trigger:
    """A step of a take: make the request an instruction of the model
    states, drawn over the duration the instruction declares."""

    def __init__(self, instruction):
        self.instruction = instruction


class Mark:
    """A name for the instant after the step before it (0 before every
    step), which shots cut on."""

    def __init__(self, name):
        self.name = name


class Planned:
    """A step of a take as its class resolved it: its document `id`, its
    `at` and `duration` in take seconds, what the framework is asked
    (`input` with `to` or `by` for a move, `instruction` for a trigger),
    and the step as written, for refusals."""

    def __init__(self, kind, written, duration, *, input=None, to=None, by=None,
                 instruction=None):
        self.kind, self.written, self.duration = kind, written, duration
        self.input, self.to, self.by, self.instruction = input, to, by, instruction
        self.id = self.at = None


class Take(_Take):
    """The take of a clocked machine: the steps it is asked to make, each
    drawn over its seconds, and the marks the shots cut on. A subclass
    carries `model`, `export`, `readiness`, `steps` and its camera
    declarations; its class derives `schedule` (the steps resolved),
    `length` (take seconds) and `marks`. Evaluation records what the machine
    did through the framework's simulation."""

    _what = 'Take'

    @classmethod
    def _time(cls, where):
        if 'marks' in vars(cls):
            raise MovieError(f"{where}: a Take writes no marks; its marks are its Mark(...) "
                             f"steps, each the instant after the step before it")
        steps = getattr(cls, 'steps', None)
        if steps is None:
            raise MovieError(f'{where} needs steps')
        if not isinstance(steps, (list, tuple)):
            raise MovieError(f'{where}: steps is a list of Move, Trigger and Mark, not {steps!r}')
        schedule, marks, after = [], {}, {}
        at, pending = 0, None
        for index, step in enumerate(steps):
            here = f'{where}: steps[{index}]'
            if isinstance(step, Mark):
                written = f'Mark({step.name!r})'
                if not isinstance(step.name, str) or not _MARK.fullmatch(step.name):
                    raise MovieError(f"{here}, {written}: a mark is named with letters, digits and "
                                     f"underscores, as set_23")
                if step.name in marks:
                    raise MovieError(f"{here}, {written}: the mark '{step.name}' is named twice")
                if pending is not None:
                    raise MovieError(f"{here}, {written}: the marks '{pending}' and '{step.name}' "
                                     f"name one instant; a mark is the instant after the step "
                                     f"before it, so put a step between them or keep one")
                marks[step.name], after[step.name], pending = at, len(schedule) - 1, step.name
                continue
            pending = None
            if isinstance(step, Move):
                planned = cls._move(step, here)
            elif isinstance(step, Trigger):
                planned = cls._trigger(step, here)
            else:
                raise MovieError(f'{here}, {step!r}, is not a step; a step is a Move, a Trigger '
                                 f'or a Mark')
            planned.id, planned.at = f'step-{len(schedule) + 1}', at
            schedule.append(planned)
            at = at + planned.duration
        if not schedule:
            raise MovieError(f'{where} has no steps; a take makes at least one Move or Trigger')
        cls.schedule, cls.length, cls.marks = tuple(schedule), at, marks
        # The index of the step each mark follows, -1 for the initial bank.
        cls._after = after

    @classmethod
    def _attribute(cls, value):
        """The attribute that holds `value` on the model or a base, or None."""
        for klass in cls.model.__mro__:
            for name, held in vars(klass).items():
                if held is value:
                    return name
        return None

    @classmethod
    def _move(cls, step, here):
        from machinome.simulation import Driver

        model = cls.model.__name__
        attribute = None if isinstance(step.input, str) else cls._attribute(step.input)
        named = (repr(step.input) if attribute is None else f'{model}.{attribute}')
        written = 'Move(' + ', '.join([named] + [f'{key}={value!r}' for key, value in
                                                 (('to', step.to), ('by', step.by), ('over', step.over))
                                                 if value is not None]) + ')'
        if (step.to is None) == (step.by is None):
            raise MovieError(f'{here}, {written}: a move gives exactly one of to= (where the input '
                             f'lands) and by= (how far it travels), in design units')
        for key, value in (('to', step.to), ('by', step.by)):
            if value is not None and not _finite(value):
                raise MovieError(f'{here}, {written}: {key}={value!r} is not a number')
        if not _finite(step.over) or step.over <= 0:
            raise MovieError(f'{here}, {written}: over={step.over!r} is not a positive number of '
                             f'seconds; a move is drawn over the seconds over= gives')
        if isinstance(step.input, str) and step.input:
            input = step.input
        elif isinstance(step.input, Driver):
            if attribute is None:
                raise MovieError(f'{here}, {written}: this Driver is not a driver {model} declares; '
                                 f'name the model\'s own, as {model}.<driver>, or its qualified id')
            input = attribute
        elif attribute is not None:
            raise MovieError(f'{here}, {written}: {model}.{attribute} is a '
                             f'{type(step.input).__name__}, not a driver; a move moves a driver '
                             f'the model declares')
        else:
            raise MovieError(f'{here}, {written}: {step.input!r} is not a driver; name the model\'s '
                             f'own, as {model}.<driver>, or its qualified id')
        return Planned('move', written, step.over, input=input, to=step.to, by=step.by)

    @classmethod
    def _trigger(cls, step, here):
        from machinome.simulation import Instruction

        model = cls.model.__name__
        table = getattr(cls.model, 'instructions', None)
        table = table if isinstance(table, dict) else {}
        value = step.instruction
        if isinstance(value, str):
            name, written = value, f'Trigger({value!r})'
            if name not in table:
                raise MovieError(f"{here}, {written}: '{name}' is not an instruction of {model}'s "
                                 f"instructions table, which declares {', '.join(table) or 'none'}")
        elif isinstance(value, Instruction):
            name = next((key for key, held in table.items() if held is value), None)
            if name is None:
                raise MovieError(f"{here}, Trigger({value!r}): this Instruction is not one "
                                 f"{model}'s instructions table holds; name it by its key")
            written = f'Trigger({model}.instructions[{name!r}])'
        else:
            raise MovieError(f"{here}, Trigger({value!r}): a trigger names an instruction of "
                             f"{model}'s instructions table")
        duration = table[name].duration
        if not _finite(duration) or duration <= 0:
            raise MovieError(f"{here}, {written}: the instruction '{name}' declares a duration of "
                             f"{duration} s; a trigger is drawn over its instruction's duration, "
                             f"so it must be positive")
        return Planned('trigger', written, duration, instruction=name)


def _finite(value):
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value))
