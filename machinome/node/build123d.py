# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The build123d leaves: `Build123dNode`, `Build123dSheetNode`, and the
reducer of `Svg` artwork.

One module per technology (the `node-model` capability): both node types
and the artwork reducer drive the one kernel, build123d, so they share one
address, `machinome.node.build123d`, and one extra, `machinome[build123d]`.
They stay distinct types -- a `Build123dNode` renders a solid it authored,
a sheet part's solid is derived from its authored profile.

build123d itself is imported inside the functions that use it, never at
import: importing build123d costs about 2.4 seconds, which a project that
names this module only to declare a node, or never builds an artwork,
should not pay.
"""

import logging

from machinome.engine import require_brep_engine
from machinome.extras import require_extra
from machinome.node.brep_leaf import BrepLeafNode
from machinome.node.sheet_leaf import SheetLeafNode

# Refused here, without the `build123d` extra, by the line that installs
# it; the check imports nothing.
require_extra('build123d',
              'machinome.node.build123d (Build123dNode, Build123dSheetNode, '
              'the Svg artwork reducer)',
              'build123d')


def build123d_shape(rendered):
    """The kernel shape of a build123d render result, or None if
    ``rendered`` did not come from build123d.

    build123d is a front end over OCCT: every object of it wraps a single
    TopoDS_Shape, exposed as ``.wrapped``, which is the B-rep engine's
    currency itself (ADR-160). Taking that shape is therefore the whole
    conversion, and every consumer after it -- placement, fuse, common,
    BREP persistence, volume -- needs no backend special case, so a fusion
    may freely mix build123d with any other B-rep backend.

    build123d is recognised by module name rather than imported.
    ``machinome.node`` resolves its adapters on first use, and importing
    build123d costs about 1.6 seconds, which a project modelling in another
    backend should not pay.

    A builder is not itself geometry: ``with BuildPart() as part:`` is
    build123d's headline idiom, and returning the builder rather than its
    ``.part`` is the first mistake a user makes, so the finished part is
    taken. Returning None rather than raising leaves the diagnosis to
    Build123dNode.validate(), which can name the node.
    """
    if not type(rendered).__module__.startswith('build123d'):
        return None
    if not hasattr(rendered, 'wrapped'):
        rendered = getattr(rendered, 'part', None)
    return getattr(rendered, 'wrapped', None)


class Build123dNode(BrepLeafNode):
    """
    Represents a 3D object created using the build123d tool.

    build123d is a boundary-representation backend over the same OCCT that
    CadQueryNode uses, so the B-rep leaf contract -- brep, shape(),
    present() -- is BrepLeafNode's. What is build123d's own is the namespace
    and the solid-shaped-result rule below.

    Note that this module never imports build123d. See build123d_shape().
    """

    namespace = 'build123d'

    def shape_from_rendered(self, rendered):
        return build123d_shape(rendered)

    def validate(self, rendered):
        """Reject anything but a solid, on top of the inherited list and
        namespace checks.

        The namespace cannot carry this adapter alone. build123d's solids,
        sketches and curves are all under the `build123d` namespace -- Part
        and Compound in build123d.topology.composite, Solid in
        build123d.topology.three_d, but also Rectangle in
        build123d.objects_sketch and Line in build123d.objects_curve -- so
        `namespace` admits a sketch as readily as a part. Left to itself, a
        returned sketch would fail later and far less legibly, inside the STL
        export.

        The check stays here rather than on BrepLeafNode because it is not
        the B-rep leaf contract's: a CadQuery render is legitimately a
        Workplane, which is not a solid until shape_from_rendered unwraps
        it. The solids are counted by the B-rep engine.
        """
        super().validate(rendered)

        shape = build123d_shape(rendered)
        if shape is None or not require_brep_engine(
                f'B-rep leaf {self.name}',
                'its render result is checked for a solid'
                ).solid_count(shape):
            raise Exception(
                f"{self.name} is a Build123dNode and should render a "
                f"build123d solid -- a Part, Solid or Compound, or a builder "
                f"whose .part is one -- not {type(rendered).__name__}"
            )


# How far off the XY plane a profile may sit and still count as on it.
# Loose enough for the rounding a placement composes, tight enough that a
# profile authored on another plane is caught.
_PLANE_TOLERANCE = 1e-6


def _export_dxf(face, path):
    """Write one validated planar face as a nominal cut file at `path`.

    Nominal: the authored profile at model scale, in millimeters, with no
    kerf or other machine compensation. Compensation is a property of a
    machine and a material, not of the part, and the persisted BREP keeps
    the exact profile available to a future offsetting exporter.

    build123d's own DXF exporter is used rather than a tessellation, so a
    circular hole reaches the cutter as a circle at its modelled radius
    instead of a polygon that would cut tight.

    Deliberately a private, single-purpose function rather than a method:
    it converts a validated face to a file and knows nothing about nodes,
    so a second sheet backend can be given its own without either growing
    a backend switch (ADR-047's pattern). It writes bytes and nothing else:
    the sheet base publishes the file, stamped and recorded, through
    `publish_artifact` -- what is written is build123d's business, how it
    is published the core's.
    """
    import build123d as b3d

    exporter = b3d.ExportDXF(unit=b3d.Unit.MM)
    exporter.add_shape(face)
    exporter.write(path)


class Build123dSheetNode(SheetLeafNode):
    """A sheet part authored as a build123d profile.

    The whole adapter is the backend-specific hooks SheetLeafNode declares
    -- reduce a profile result to its planar faces, say whether a face lies
    on the XY plane, extrude it, write it as a cut file. The contract around
    them is the sheet base's, and the B-rep leaf contract under that is
    BrepLeafNode's: the
    extrusion is an ordinary build123d Part, so namespace validation,
    the rewrap to the engine's currency, and the STL/BREP writes are the
    ones every other B-rep adapter already goes through.

    This is not a Build123dNode, though both are defined in this module.
    Both drive build123d, but a Build123dNode renders a solid it authored,
    while a sheet part's solid is derived and only its profile is
    authored -- and the two must stay distinct types, since `isinstance`
    distinguishes them that way.

    Like Build123dNode, it imports build123d only inside the hooks that use
    it, never at import time.
    """

    namespace = 'build123d'

    def profile(self):
        """The part's cut profile: a build123d `Sketch`, a `Face`, or a
        `BuildSketch` builder holding one."""
        raise NotImplementedError(
            f"{self.__class__} is a Build123dSheetNode and must implement "
            "profile(), returning a build123d sketch, face or BuildSketch")

    def profile_faces(self, profile):
        """The planar faces of a build123d profile result.

        Empty for anything that is not a planar 2D object, so the sheet
        base can name the type the node produced: a solid has solids, a
        curve has no faces at all, and a foreign object is not build123d's.
        A solid is the interesting rejection -- Build123dNode would accept
        it, and its six planar faces would otherwise read as six parts.

        A builder is not itself geometry. `with BuildSketch() as sketch:`
        is build123d's headline sketch idiom, so the finished `.sketch` is
        taken, exactly as Build123dNode takes a builder's `.part`.
        """
        if not type(profile).__module__.startswith('build123d'):
            return []
        if not hasattr(profile, 'wrapped'):
            profile = getattr(profile, 'sketch', None)
        if getattr(profile, 'wrapped', None) is None:
            return []
        if profile.solids() or profile.shells():
            return []
        return [face for face in profile.faces() if face.is_planar]

    def lies_on_xy_plane(self, face):
        normal = face.normal_at()
        if abs(abs(normal.Z) - 1) > _PLANE_TOLERANCE:
            return False
        box = face.bounding_box()
        return (abs(box.min.Z) <= _PLANE_TOLERANCE
                and abs(box.max.Z) <= _PLANE_TOLERANCE)

    def extrude(self, face):
        """The profile swept along +Z by the thickness.

        The direction is given explicitly rather than left to the face's
        own normal, so a profile authored with a reversed normal still
        yields the part the contract promises: from the XY plane up to
        Z = thickness.
        """
        import build123d as b3d

        return b3d.extrude(face, amount=self.thickness, dir=(0, 0, 1))

    def write_dxf(self, face, path):
        _export_dxf(face, path)


##############################################
# The reducer of `Svg` artwork

#: The artwork reducer contract version this module implements. The markings
#: module (`machinome.node.markings`) declares the version it speaks and
#: refuses this module when the two differ (ADR-162's pattern).
SVG_REDUCER_CONTRACT = 1

#: The reduction's one log line keeps the logger it was written under, so a
#: build's log reads as it did before the reducer moved here.
logger = logging.getLogger('node.markings')


def svg_regions(path) -> list:
    """The drawing's CLOSED regions, each one build123d face carrying its
    enclosed regions as holes.

    The file's own origin is kept (`align=None`) rather than moved to the
    drawing's minimum corner, which is what makes a marking's `origin=`
    meaningful and what makes two artworks authored on one sheet register
    with each other. Its Y axis is flipped into model orientation
    (`flip_y=True`, build123d's default), because SVG's Y grows downward and
    the model's does not -- so a drawing authored in a drawing program reads
    the right way up and its faces sit at negative Y.

    Open paths are ignored and COUNTED, in one line at INFO naming the file:
    a drawing's sheet border is an open path that registers the artwork and
    is not part of it -- the Curta's own `results_dial.svg` carries a border
    that measures its roll's unwrapped circumference exactly -- and dropping
    it silently would leave a modeller wondering why the digits do not sit
    where the drawing says. Artwork with no closed region at all is refused:
    a decal with nothing in it is a mistake, not an empty decal.
    """
    import build123d as b3d

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


def svg_triangles(path, tolerance):
    """The artwork at `path` as flat triangles, unscaled: `(vertices,
    triangles)`, the vertices an `(N, 2)` array of artwork coordinates and
    the triangles an `(M, 3)` array of indices into them.

    Each region is oriented to `+Z` before it is meshed, so the triangles'
    winding is a property of THIS PRODUCER and not of the drawing tool or of
    a transitive dependency's fix-up pass: the markings' placement maths
    maps artwork `+Z` outward by construction -- `Flat` builds its frame so
    `x_axis x y_axis` is the declared normal, and `Wrapped` maps artwork
    `(u, v)` so its tangents' cross product is the outward radial direction
    -- so orienting the artwork here is what makes the built decal face away
    from the part, whichever way the artwork's own regions came out of the
    drawing.

    Each region is then meshed in its own plane through OCCT's incremental
    mesher, which respects the holes the face carries, so a digit's counter
    is a hole in the decal and not a second patch of colour over it. The
    artwork's `scale` is the file's property and is the caller's to apply.
    """
    import build123d as b3d
    import numpy as np

    vertices = []
    triangles = []
    for face in svg_regions(path):
        if face.normal_at().Z < 0:
            face = b3d.Face(face.wrapped.Complemented())
        points, facets = face.tessellate(tolerance)
        offset = len(vertices)
        vertices.extend((point.X, point.Y) for point in points)
        triangles.extend((a + offset, b + offset, c + offset)
                         for a, b, c in facets)
    return (np.array(vertices, dtype=float),
            np.array(triangles, dtype=np.int64))
