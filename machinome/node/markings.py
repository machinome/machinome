# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""What a part CARRIES on its surface, and is not made of.

A calculator's answer is the angular position of a printed number roll.
Model one and the register is computed correctly and is unreadable,
because the digits are not on the part -- and the only way to put them
there was to declare each glyph as its own leaf, which invents parts no
maker handles, gives them volume, and puts phantom solids in front of
every clearance, interference and disconnected-solid contract. A
**marking** is the honest way to say it:

    from machinome.node.markings import Marking, Svg, Wrapped

    class ResultsDial(CadQueryNode):

        digits = Marking(
            Svg('results_dial.svg'),
            Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45)),
            color='#FFFFFF',
        )

A marking is a fourth thing a class body may declare, beside a
parameter, a child and a coordinate -- and the interesting thing about
it is what it is NOT. It is not a node, it has no volume, it is not a
child, it is not a printed piece, and it does not identify the part's
artifacts: it is not a `Declaration`, so it never reaches
`identity_values` or `_build_uniq_id`, which is the whole mechanism
behind "adding a decal cannot change an artifact key". What it does
produce is one surface mesh beside the part's own `.stl`, in the part's
own adjusted frame, with a currency of its own: edit the artwork and
only the decal is rebuilt.

Nothing heavier than the standard library is imported here -- the one
framework import, `require_source_file`, is the admission every
source-bound leaf already makes and imports nothing itself. build123d
is reached inside the artwork reduction, trimesh inside the mesh build
and numpy inside the placement arithmetic, for the reason
`Build123dSheetNode`'s docstring gives: `machinome.node` is on every
`machinome` invocation's path and build123d costs about 1.6 s.
"""

import logging
import math
import os
import re
import sys

from .sources import require_source_file


logger = logging.getLogger('node.markings')

# How nearly parallel two declared directions may be before the second
# leaves nothing of itself across the first. Loose enough to catch a
# direction stated in another unit or scale, tight enough that a real
# angle survives.
_PARALLEL_TOLERANCE = 1e-9


def _is_marking(value):
    """Whether `value` is a marking declaration.

    Duck-typed on `marking_kind`, exactly as a control is recognized by
    `control_kind`: `NodeMeta.__new__` asks the same question without
    importing this module, so `machinome/node/declarative.py` keeps
    importing nothing new.
    """
    return getattr(type(value), 'marking_kind', None) == 'marking'


def declared_markings(node_class):
    """Every marking declared on `node_class`, by attribute, in
    declaration order.

    Walks `reversed(node_class.__mro__)` in the shape of
    `declared_children`, later classes winning, so a marking is
    inherited like any class attribute -- including from a PLAIN MIXIN
    that is not a node at all, which is exactly how a project spells
    `class FittedDialType1(ClearingGearFit, ResultsDialType1)`.

    One deliberate difference from `declared_children`: a subclass
    assigning `None` to the attribute REMOVES the inherited entry, so a
    variant part can be the same solid without its label. `None` is
    unambiguous -- a `Marking` has no falsy state.

    Not cached, deliberately: `declared_children` memoizes because it is
    read once per realized child on every construction, while this is
    read once per node per build pass and a stale answer would survive a
    reloaded class in a develop session.
    """
    found = {}
    for klass in reversed(node_class.__mro__):
        for attribute, value in vars(klass).items():
            if _is_marking(value):
                found[attribute] = value
            elif value is None and attribute in found:
                del found[attribute]
    return found


##############################################
# Artwork


class Svg:
    """A marking's artwork: an SVG file beside the module that declared
    the marking.

    `path` is relative to the directory of the Python module whose class
    body wrote the `Marking`, so a subclass inheriting a marking reads
    the file the declaring module meant, and a marking written in a
    plain mixin reads the file beside the mixin. It is refused through
    `require_source_file`, the call every source-bound leaf already
    makes, so a missing artwork fails in the same family as a missing
    STL source.

    `scale`, when given, multiplies every artwork coordinate -- for a
    file authored in something other than millimetres. It is a property
    of the FILE, which is why it is here and not on a placement. It must
    be POSITIVE: a negative scale mirrors the artwork plane, which
    reverses the winding `tessellate()` just oriented and renders every
    glyph backwards, and zero collapses the artwork to a point.
    """

    marking_kind = 'artwork'

    def __init__(self, path, scale=None):
        if scale is not None and (not isinstance(scale, (int, float))
                                  or scale <= 0):
            raise ValueError(
                f'Svg(scale={scale!r}): scale is a positive number -- the '
                f'factor every artwork coordinate is multiplied by. A '
                f'negative scale mirrors the artwork plane, which reverses '
                f'the winding of every triangle after its region was '
                f'oriented and renders every glyph backwards; a zero scale '
                f'collapses the artwork to a point.')
        self.path = path
        self.scale = scale
        #: The resolved absolute path, set when the declaring class is
        #: created (see `Marking.resolve`).
        self.resolved = None

    def resolve(self, directory, owner, attribute):
        """The absolute path of this artwork, refused when it is not a
        file that is there.

        `owner` is the class whose body WROTE the marking -- the mixin
        where there is one -- because `require_source_file` composes its
        message from that class's own module, and saying a path was
        resolved against a module it was not resolved against would be
        worse than saying nothing. The exceptions are that function's,
        unchanged: `MissingSourceFile` (a `FileNotFoundError`) for a
        path that is not there, `ValueError` for one that is not a
        regular file, each carrying `.filename` so develop-mode reload
        repair watches the artwork and retries when it appears.

        Resolved afresh every time a class carrying this marking is
        created rather than remembered from the first: a subclass in
        another module must be seen to resolve against the DECLARING
        module and not against its own, and an artwork that has gone
        must refuse the next class as it refused the first.
        """
        path = os.path.realpath(os.path.join(directory, self.path))
        require_source_file(owner, attribute, self.path, path)
        self.resolved = path
        return path

    def regions(self) -> list:
        """The drawing's CLOSED regions, each one face carrying its
        enclosed regions as holes.

        The file's own origin is kept (`align=None`) rather than moved
        to the drawing's minimum corner, which is what makes `origin=`
        meaningful and what makes two artworks authored on one sheet
        register with each other. Its Y axis is flipped into model
        orientation (`flip_y=True`, build123d's default), because SVG's
        Y grows downward and the model's does not -- so a drawing
        authored in a drawing program reads the right way up and its
        faces sit at negative Y.

        Open paths are ignored and COUNTED, in one line at INFO naming
        the file: a drawing's sheet border is an open path that
        registers the artwork and is not part of it -- the Curta's own
        `results_dial.svg` carries a border that measures its roll's
        unwrapped circumference exactly -- and dropping it silently
        would leave a modeller wondering why the digits do not sit where
        the drawing says. Artwork with no closed region at all is
        refused: a decal with nothing in it is a mistake, not an empty
        decal.

        build123d is imported HERE rather than at module scope: it costs
        about 1.6 s and `machinome.node` is on every `machinome`
        invocation's path, so only a build that actually reduces an
        artwork pays for it.
        """
        import build123d as b3d

        path = self.resolved or self.path
        shapes = b3d.import_svg(path, align=None)
        faces = [shape for shape in shapes if isinstance(shape, b3d.Face)]
        ignored = len(shapes) - len(faces)
        logger.info('%s: %d open path(s) ignored, %d closed region(s) read',
                    path, ignored, len(faces))
        if not faces:
            raise ValueError(
                f'{path} holds no closed region: a marking is the drawing\'s '
                f'closed regions, and this file has none -- every path in it '
                f'is open. Close the outlines the marking is meant to carry.')
        return faces

    def tessellate(self, tolerance):
        """The artwork as flat triangles: `(vertices, triangles)`, the
        vertices an `(N, 2)` array of artwork coordinates and the
        triangles an `(M, 3)` array of indices into them.

        Each region is oriented to `+Z` before it is meshed, so the
        triangles' winding is a property of THIS PRODUCER and not of the
        drawing tool or of a transitive dependency's fix-up pass: the
        framework's own placement maths already maps artwork `+Z`
        outward by construction -- `Flat` builds its frame so
        `x_axis x y_axis` is the declared normal, and `Wrapped` maps
        artwork `(u, v)` so its tangents' cross product is the outward
        radial direction -- so orienting the artwork here is what makes
        the built decal face away from the part, whichever way the
        artwork's own regions came out of the drawing.

        Each region is then meshed in its own plane through OCCT's
        incremental mesher, which respects the holes the face carries,
        so a digit's counter is a hole in the decal and not a second
        patch of colour over it. `scale` multiplies the result, because
        it is a property of the FILE: a drawing authored in inches is
        the same drawing at a different size.
        """
        import build123d as b3d
        import numpy as np

        vertices = []
        triangles = []
        for face in self.regions():
            if face.normal_at().Z < 0:
                face = b3d.Face(face.wrapped.Complemented())
            points, facets = face.tessellate(tolerance)
            offset = len(vertices)
            vertices.extend((point.X, point.Y) for point in points)
            triangles.extend((a + offset, b + offset, c + offset)
                             for a, b, c in facets)
        placed = np.array(vertices, dtype=float)
        if self.scale is not None:
            placed = placed * self.scale
        return placed, np.array(triangles, dtype=np.int64)

    def __repr__(self):
        if self.scale is None:
            return f'Svg({self.path!r})'
        return f'Svg({self.path!r}, scale={self.scale!r})'


##############################################
# Placement

# Three-component vector arithmetic, in plain Python and on plain
# tuples. A placement's frame is three vectors resolved once, at
# declaration, and numpy is reached only where there is bulk to move
# (`place` below), which is what keeps this module's import free of
# anything but the standard library.


def _vector(value, what, owner):
    try:
        x, y, z = (float(component) for component in value)
    except (TypeError, ValueError):
        raise ValueError(
            f'{owner}: {what} is {value!r}, which is not a point or a '
            f'direction. State it as three numbers, (x, y, z).') from None
    return (x, y, z)


def _dot(first, second):
    return sum(a * b for a, b in zip(first, second))


def _cross(first, second):
    return (first[1] * second[2] - first[2] * second[1],
            first[2] * second[0] - first[0] * second[2],
            first[0] * second[1] - first[1] * second[0])


def _scale(vector, factor):
    return tuple(component * factor for component in vector)


def _minus(first, second):
    return tuple(a - b for a, b in zip(first, second))


def _normalize(vector, what, owner):
    length = math.sqrt(_dot(vector, vector))
    if length == 0:
        raise ValueError(
            f'{owner}: {what} is {vector!r}, which has no direction. A '
            f'placement needs a direction to work from.')
    return _scale(vector, 1.0 / length)


def _artwork_origin(origin, owner):
    try:
        x, y = (float(component) for component in origin)
    except (TypeError, ValueError):
        raise ValueError(
            f'{owner}: origin is {origin!r}, which is not an artwork '
            f'point. State it as two numbers, (x, y).') from None
    return (x, y)


class Flat:
    """A marking on a plane: through `at`, with the given `normal`,
    artwork X along `x_axis` orthogonalized against that normal and
    artwork Y along `normal x x_axis`.

    `origin` is the artwork point that lands on `at`. Vectors need not
    be unit length.
    """

    marking_kind = 'placement'

    #: One stamp: a plane is not a circle and nothing repeats on it.
    repeats = 1

    def __init__(self, at, normal, x_axis, origin=(0, 0)):
        self.at = at
        self.normal = normal
        self.x_axis = x_axis
        self.origin = origin

        self._at = _vector(at, 'at', 'Flat')
        self._origin = _artwork_origin(origin, 'Flat')
        normal_hat = _normalize(_vector(normal, 'normal', 'Flat'),
                                'normal', 'Flat')
        declared_x = _vector(x_axis, 'x_axis', 'Flat')
        in_plane = _minus(declared_x,
                          _scale(normal_hat, _dot(declared_x, normal_hat)))
        if math.sqrt(_dot(in_plane, in_plane)) <= _PARALLEL_TOLERANCE:
            raise ValueError(
                f'Flat(normal={normal!r}, x_axis={x_axis!r}): the x axis is '
                f'parallel to the normal, so it leaves nothing in the plane '
                f'to run artwork X along. State an x axis across the normal.')
        self._x = _normalize(in_plane, 'x_axis', 'Flat')
        self._y = _cross(normal_hat, self._x)
        self._normal = normal_hat

    def max_edge(self, tolerance):
        """No limit: a plane is flat, so a triangle spanning it is the
        surface and not an approximation of one."""
        return None

    def place(self, points, repeat=0):
        """Artwork points `(N, 2)` mapped into the part's own adjusted
        frame, as an `(N, 3)` array.

        `P(u, v) = at + u x + v y`, where `u, v` is the artwork point
        shifted so that the declared `origin` lands on `at`.
        """
        import numpy as np

        artwork = np.asarray(points, dtype=float).reshape(-1, 2)
        shifted = artwork - np.array(self._origin)
        return (np.array(self._at)
                + np.outer(shifted[:, 0], np.array(self._x))
                + np.outer(shifted[:, 1], np.array(self._y)))

    def __repr__(self):
        return (f'Flat(at={self.at!r}, normal={self.normal!r}, '
                f'x_axis={self.x_axis!r})')


class Wrapped:
    """A marking wrapped onto a cylinder: artwork X is ARC LENGTH around
    `axis`, artwork Y is height ALONG it from `at`.

    A point at artwork x therefore sits at the angle
    `start + degrees(x / radius)`, measured right-handed about `axis`
    from a zero direction that is stated rather than inferred --
    `zero=` when it is given, and otherwise the next principal axis in
    right-hand order (`+Z` wraps from `+X`, `+X` from `+Y`, `+Y` from
    `+Z`).

    `pitch`, in degrees, stamps the whole artwork every `pitch` degrees
    around the circle, for an artwork that is one repeated unit.
    """

    marking_kind = 'placement'

    def __init__(self, axis, radius, at, start=0, origin=(0, 0),
                 pitch=None, zero=None):
        self.axis = axis
        self.radius = radius
        self.at = at
        self.start = start
        self.origin = origin
        self.pitch = pitch
        self.zero = zero

        if not isinstance(radius, (int, float)) or radius <= 0:
            raise ValueError(
                f'Wrapped(radius={radius!r}): a wrap radius is a positive '
                f'number of millimetres -- it is what turns artwork X into '
                f'an angle.')
        self._at = _vector(at, 'at', 'Wrapped')
        self._origin = _artwork_origin(origin, 'Wrapped')
        self._axis = _normalize(_vector(axis, 'axis', 'Wrapped'),
                                'axis', 'Wrapped')
        self._zero = self._zero_direction()
        self._binormal = _cross(self._axis, self._zero)
        self.repeats = self._repeat_count()

    def _zero_direction(self):
        """The direction artwork x = 0 sits in, stated or derived.

        Stated, it is projected perpendicular to the axis and refused
        when it is parallel to it. Derived, it is

            e0 = normalize(shift(a) - (shift(a) . a) a)

        where `shift` is the cyclic shift `(a1, a2, a3) -> (a3, a1, a2)`,
        a 120 degree rotation about (1, 1, 1). For a principal axis that
        lands exactly on the next principal axis in right-hand order --
        +Z from +X, +X from +Y, +Y from +Z, -Z from -X -- and for a
        general axis it is deterministic and continuous away from the
        one direction where it is undefined, the axis parallel to
        (1, 1, 1), which is refused rather than silently chosen.
        """
        if self.zero is not None:
            stated = _vector(self.zero, 'zero', 'Wrapped')
            across = _minus(stated,
                            _scale(self._axis, _dot(stated, self._axis)))
            if math.sqrt(_dot(across, across)) <= _PARALLEL_TOLERANCE:
                raise ValueError(
                    f'Wrapped(axis={self.axis!r}, zero={self.zero!r}): the '
                    f'zero direction is parallel to the axis, so it names no '
                    f'point on the cylinder. State a zero across the axis.')
            return _normalize(across, 'zero', 'Wrapped')

        shifted = (self._axis[2], self._axis[0], self._axis[1])
        across = _minus(shifted,
                        _scale(self._axis, _dot(shifted, self._axis)))
        if math.sqrt(_dot(across, across)) <= _PARALLEL_TOLERANCE:
            raise ValueError(
                f'Wrapped(axis={self.axis!r}): the angular zero cannot be '
                f'derived for this axis -- it is the one direction the '
                f'derivation is undefined for. State it: '
                f'zero=(x, y, z), any direction across the axis.')
        return _normalize(across, 'zero', 'Wrapped')

    def _repeat_count(self):
        """How many times the whole artwork is stamped around the
        circle.

        A pitch that does not divide 360 leaves the last copy
        overlapping the first with no honest answer about which wins, so
        it is refused naming the value and the nearest whole count.
        """
        if self.pitch is None:
            return 1
        if not isinstance(self.pitch, (int, float)) or self.pitch <= 0:
            raise ValueError(
                f'Wrapped(pitch={self.pitch!r}): a pitch is a positive '
                f'number of degrees between one stamp of the artwork and '
                f'the next.')
        count = 360.0 / self.pitch
        nearest = round(count)
        if abs(count - nearest) > 1e-9:
            raise ValueError(
                f'Wrapped(pitch={self.pitch!r}): a pitch has to divide the '
                f'circle a whole number of times, and 360 / {self.pitch!r} '
                f'is {count!r}. The nearest whole count is {nearest}, which '
                f'is a pitch of {360.0 / nearest!r} degrees.')
        return int(nearest)

    def max_edge(self, tolerance):
        """The longest chord this wrap may span and still sit within
        `tolerance` of the cylinder: `2 * sqrt(2 R t - t^2)`, the chord
        whose sagitta is exactly `t`.

        Two vertices of a flat triangle wrapped by their coordinates
        alone describe a CHORD, not an arc, so without this the decal
        cuts across the surface it is supposed to lie on -- by 0.1 mm at
        R = 9.45 for an artwork whose regions span millimetres of arc.
        """
        radius = float(self.radius)
        return 2.0 * math.sqrt(max(2.0 * radius * tolerance
                                   - tolerance * tolerance, 0.0))

    def place(self, points, repeat=0):
        """Artwork points `(N, 2)` wrapped onto the cylinder, as an
        `(N, 3)` array in the part's own adjusted frame.

        Artwork X is ARC LENGTH, so a point at artwork x sits at the
        angle `start + degrees(x / radius)` measured right-handed about
        the axis from the zero direction, and artwork Y is height along
        the axis from `at`. `repeat` is which stamp this is, for a
        placement that declares a pitch.
        """
        import numpy as np

        artwork = np.asarray(points, dtype=float).reshape(-1, 2)
        shifted = artwork - np.array(self._origin)
        offset = math.radians(self.start)
        if self.pitch is not None:
            offset += math.radians(self.pitch * repeat)
        angle = offset + shifted[:, 0] / self.radius
        return (np.array(self._at)
                + np.outer(shifted[:, 1], np.array(self._axis))
                + self.radius * (np.outer(np.cos(angle),
                                          np.array(self._zero))
                                 + np.outer(np.sin(angle),
                                            np.array(self._binormal))))

    def __repr__(self):
        return (f'Wrapped(axis={self.axis!r}, radius={self.radius!r}, '
                f'at={self.at!r})')


##############################################
# The declaration


#: The tessellation precision a part that declares none is meshed at:
#: the framework's historical default, the same number
#: `ExactLeafNode.linear_deflection` and `FusionNode.linear_deflection`
#: carry. An `StlNode` declares neither, so its decals are meshed at
#: this -- which is why it is in the marking artifact's producer recipe
#: (`AbstractBaseNode._artifact_recipe`) and not only in its sources.
DEFAULT_DEFLECTION = 0.1


#: A node's colour, in the one form `_colorize` accepts (`base.py`).
_COLOR = re.compile(r'#[0-9A-Fa-f]{6}\Z')


def validated_color(color, node_class, attribute):
    """A marking's colour, refused with `ValueError` as a node's is.

    Required, unlike a node's, and refused where it is written: a
    declaration whose colour is missing declared nothing at all, and
    saying so at class creation is earlier and more legible than a
    colourless decal in a viewer.
    """
    if not isinstance(color, str) or _COLOR.match(color) is None:
        raise ValueError(
            f"{node_class.__name__}.{attribute} declares color={color!r}. A "
            f"marking's colour is required and reads in the format #RRGGBB, "
            f"exactly as a node's own colour does.")
    return color


class Marking:
    """The artwork a part carries, where it sits, and in what colour.

    An ordinary class attribute, deliberately NOT a data descriptor and
    NOT a `Declaration`. Not a `Declaration`, so `declared_parameters`
    never sees it and it can never reach `identity_values` or
    `_build_uniq_id`; not a descriptor, so `self.digits` on an instance
    returns the marking itself, which is useful in a test and inert
    everywhere else -- and cannot be mistaken for a child, since
    automatic child naming scans the instance `__dict__` and a class
    attribute is never in it.

    `color` is required, unlike a node's: a part with no colour has a
    sensible default appearance, while a decal with no colour is
    invisible, which means the declaration did nothing.
    """

    marking_kind = 'marking'

    def __init__(self, artwork, placement, color=None):
        self.artwork = artwork
        self.placement = placement
        self.color = color
        self._name = None
        #: The class whose body wrote this marking, and the directory of
        #: its module -- captured in `__set_name__`, which Python calls
        #: whatever the owner's metaclass, so a plain mixin captures its
        #: own module exactly as a node class does.
        self._owner = None
        self._directory = None

    @property
    def name(self):
        """The attribute this marking was declared under."""
        return self._name

    def __set_name__(self, owner, name):
        if self._name is not None and self._name != name:
            raise TypeError(
                f"'{name}' on {owner.__name__} is the marking already named "
                f"'{self._name}': a marking is one drawing on one part, so "
                f"it cannot be assigned under two names. Declare a second "
                f"marking.")
        self._name = name
        if self._owner is None:
            self._owner = owner
            module = sys.modules.get(owner.__module__)
            source = getattr(module, '__file__', None)
            if source is not None:
                self._directory = os.path.dirname(os.path.realpath(source))

    def declared_on(self, node_class, attribute):
        """Refuse this marking on `node_class`, or resolve its artwork.

        Called from `NodeMeta.__new__` through `_validate_markings`,
        which has already refused a non-rigid node and a name clash. A
        malformed marking is refused HERE, where the class exists and
        the attribute is known, so the error names both -- the reason
        `_validate_controls` gives for validating a control where it is
        written.
        """
        if getattr(type(self.artwork), 'marking_kind', None) != 'artwork':
            raise TypeError(
                f"{node_class.__name__}.{attribute} is a marking whose "
                f"artwork is {self.artwork!r}, which names no drawing. A "
                f"marking's first argument is its artwork: "
                f"Svg('label.svg').")
        if getattr(type(self.placement), 'marking_kind', None) != 'placement':
            raise TypeError(
                f"{node_class.__name__}.{attribute} is a marking whose "
                f"placement is {self.placement!r}, which says nowhere. A "
                f"marking's second argument is where on the part it sits: "
                f"Wrapped(...) or Flat(...).")
        validated_color(self.color, node_class, attribute)
        directory = self._directory
        if directory is None:
            module = sys.modules.get(node_class.__module__)
            source = getattr(module, '__file__', None)
            if source is None:
                raise TypeError(
                    f"{node_class.__name__}.{attribute} is a marking whose "
                    f"declaring module has no file, so its artwork "
                    f"{self.artwork!r} cannot be resolved against one.")
            directory = os.path.dirname(os.path.realpath(source))
        self.artwork.resolve(directory, self._owner or node_class, attribute)

    def surface(self, tolerance):
        """This marking's surface as an open sheet of triangles in the
        part's adjusted frame: `(vertices, faces)`.

        The artwork is meshed flat, subdivided where the placement needs
        it -- a wrap, so that no edge spans more chord than `tolerance`
        allows -- and then mapped point by point. There is NO offset:
        the sheet sits on the nominal cylinder or plane, because any
        separation a renderer needs to avoid z-fighting is that
        renderer's constant and not a claim about where the part's
        surface is.

        The result is deliberately not watertight. It is a surface, not
        a solid: nothing in the framework imports it as a part, fuses
        it, or measures its volume.

        trimesh is imported here rather than at module scope, for the
        reason build123d is (see `Svg.regions`).
        """
        import numpy as np
        import trimesh

        points, triangles = self.artwork.tessellate(tolerance)
        limit = self.placement.max_edge(tolerance)
        if limit is not None and len(triangles):
            flat = np.column_stack([points, np.zeros(len(points))])
            flat, triangles = trimesh.remesh.subdivide_to_size(
                flat, triangles, limit)
            points = flat[:, :2]

        vertices = []
        faces = []
        for repeat in range(self.placement.repeats):
            faces.append(triangles + len(points) * repeat)
            vertices.append(self.placement.place(points, repeat=repeat))
        return np.vstack(vertices), np.vstack(faces)

    def mesh_bytes(self, tolerance):
        """This marking's surface as the bytes of a binary STL."""
        import numpy as np
        import trimesh

        vertices, faces = self.surface(tolerance)
        mesh = trimesh.Trimesh(vertices=np.asarray(vertices, dtype=np.float64),
                               faces=np.asarray(faces, dtype=np.int64),
                               process=False)
        return trimesh.exchange.stl.export_stl(mesh)

    def __repr__(self):
        return (f'Marking({self.artwork!r}, {self.placement!r}, '
                f'color={self.color!r})')
