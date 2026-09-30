"""The take a movie films: the posed loop of a machinome model, with its
marks, and what is declared beside it for the camera: cameras, layers,
source excerpts and stills.

A part is named by the model class's own declarations (`Mill.feed.pawl`)
and resolved here to the names the export gives it.
"""

import math
import os

from machinome.motion.couplings import PathRef
from machinome.node.declarative import ChildDeclaration, declared_children

from .anchors import Anchor, time_value
from .names import (MovieError, declaring_class, ease, module_directory, number,
                    slug)


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
    """Something declared on a Loop: it belongs to the first loop that
    holds it and is named by that loop's attribute."""

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
        """The element that shows `source` beside or instead of the model."""
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

    def show(self, *, area=None, fit=None, enter=None, leave=None, view=()):
        """Show the still over the stage or the frame, for a cue's span."""
        from .stage import Picture

        return Picture(self, area=area, fit=fit, enter=enter, leave=leave, view=view)


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
        keyframes = []
        for at, value, curve in self.keys:
            key = {'at': at.document() if isinstance(at, Anchor) else at,
                   'seconds': seconds(value)}
            if curve is not None:
                key['ease'] = curve
            keyframes.append(key)
        return {'from': keyframes[0]['seconds'], 'to': keyframes[-1]['seconds'],
                'keyframes': keyframes}


def _same_time(a, b):
    if isinstance(a, Anchor) or isinstance(b, Anchor):
        return a == b
    return a == b


class Loop:
    """The posed loop of a model: the trivial take. A subclass carries
    `model`, `export`, `marks`, `readiness` and its camera declarations."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        where = f'Loop {cls.__name__}'
        for attribute in ('model', 'export', 'readiness'):
            if getattr(cls, attribute, None) is None:
                raise MovieError(f'{where} needs {attribute}')
        if not isinstance(cls.model, type):
            raise MovieError(f'{where}: model is the node class, not {cls.model!r}')
        if not isinstance(cls.export, str) or not cls.export:
            raise MovieError(f'{where}: export is the path of the export directory')
        if not isinstance(cls.readiness, str) or not cls.readiness.strip():
            raise MovieError(f'{where}: readiness says what the export does and does not show')
        marks = getattr(cls, 'marks', None) or {}
        for name, seconds in marks.items():
            if not isinstance(name, str) or not name:
                raise MovieError(f'{where}: mark {name!r} is not a name')
            number(seconds, f'{where}: mark {name}')
        cls.marks = dict(marks)
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
    def declarations(cls, kind):
        """What the loop declares of `kind`, by attribute, bases first."""
        found = {}
        for klass in reversed(cls.__mro__):
            if klass is Loop or not issubclass(klass, Loop):
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
        model seconds, or mark names."""
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
