# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The OCCT exact engine: every operation on an exact shape.

The provider of the core's exact engine contract (`machinome.exact_engine`)
and the one address of the exact operations a project calls directly:
`intersect_shapes`, `fuse_shapes`, `placed_shape`, `solid_count` and
`solid_volume`. Each operation is defined here once, under one name.

The currency is the kernel's own object: an `OCP.TopoDS.TopoDS_Shape`, or
one of its subtypes. The engine adds no type around it; every operation
that returns geometry returns one, and `as_shape` admits a CAD front end's
object by the `.wrapped` attribute CadQuery and build123d share.

Everything here is OCP and numpy: the engine imports no CAD front end, no
trimesh, and from the framework only the contract module, for the error
types it raises, and the extras module, for the refusal it raises before
importing OCP when the `occt` extra is not installed. It keeps no state;
caching is its caller's choice.
"""

from itertools import product
import math

from machinome.extras import require_extra

# The OCCT binding is the `occt` extra's: refused here, before it is
# imported, by the line that installs it. The seam
# (`machinome.exact_engine`) reads this refusal as an absent engine.
require_extra('occt', 'the exact engine (machinome.occt.engine)', 'OCP')

import numpy as np
from OCP.Bnd import Bnd_Box
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.BRepAlgoAPI import (BRepAlgoAPI_Common, BRepAlgoAPI_Fuse,
                             BRepAlgoAPI_Section)
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepBuilderAPI import (BRepBuilderAPI_Copy, BRepBuilderAPI_MakeVertex,
                                BRepBuilderAPI_Transform)
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools
from OCP.GCPnts import GCPnts_AbscissaPoint
from OCP.GProp import GProp_GProps
from OCP.gp import gp_Pnt, gp_Trsf
from OCP.Precision import Precision
from OCP.StlAPI import StlAPI_Writer
from OCP.TopAbs import (TopAbs_EDGE, TopAbs_FACE, TopAbs_IN, TopAbs_OUT,
                        TopAbs_SOLID, TopAbs_UNKNOWN, TopAbs_VERTEX)
from OCP.TopExp import TopExp
from OCP.TopoDS import TopoDS, TopoDS_Builder, TopoDS_Compound, TopoDS_Shape
from OCP.TopTools import TopTools_IndexedMapOfShape, TopTools_ListOfShape

from machinome.exact_engine import (ExactCommonInconsistency,
                                    ExactCommonVerificationError)

#: The exact engine contract version this engine implements.
CONTRACT = 1


########################################
# Currency


def as_shape(obj):
    """`obj` as the engine's currency: itself when it is a
    `TopoDS_Shape`, else the `TopoDS_Shape` it carries as `.wrapped`.

    A rewrap, never a translation: nothing is copied, healed or
    tessellated. Anything else is refused naming its type.
    """
    if isinstance(obj, TopoDS_Shape):
        return obj
    wrapped = getattr(obj, 'wrapped', None)
    if isinstance(wrapped, TopoDS_Shape):
        return wrapped
    kind = type(obj)
    raise TypeError(
        f'The OCCT exact engine takes an OCP.TopoDS.TopoDS_Shape, or an '
        f'object carrying one as .wrapped, not {kind.__module__}.'
        f'{kind.__qualname__}')


def compound(shapes):
    """One compound holding every shape given, in order."""
    result = TopoDS_Compound()
    builder = TopoDS_Builder()
    builder.MakeCompound(result)
    for shape in shapes:
        builder.Add(result, shape)
    return result


def read_brep(path):
    """The shape the BREP file at `path` holds."""
    shape = TopoDS_Shape()
    BRepTools.Read_s(shape, path, BRep_Builder())
    if shape.IsNull():
        raise ValueError(f'Could not import {path}')
    return shape


def write_brep(shape, path):
    """Write `shape`'s BREP to `path`.

    Writes whatever triangulation the shape carries alongside its
    topology, so a caller wanting the BREP independent of tessellation
    writes it before `write_stl` meshes the shape.
    """
    BRepTools.Write_s(shape, path)


def write_stl(shape, path, linear_deflection, angular_deflection):
    """Tessellate `shape` at the given deflections and write it to `path`
    as a binary STL, and nothing else.

    The deflection is relative to each edge's size and the mesher runs in
    parallel, as CadQuery's `exportStl` does; the triangulation is stored
    on the shape.
    """
    BRepMesh_IncrementalMesh(shape, linear_deflection, True,
                             angular_deflection, True)
    writer = StlAPI_Writer()
    writer.ASCIIMode = False
    if not writer.Write(shape, path):
        raise RuntimeError(f'OCCT could not write the STL {path}')


########################################
# Subshapes


def _subshapes(shape, kind, cast):
    found = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, kind, found)
    return [cast(found.FindKey(index))
            for index in range(1, found.Extent() + 1)]


def _solids(shape):
    return _subshapes(shape, TopAbs_SOLID, TopoDS.Solid_s)


def _faces(shape):
    return _subshapes(shape, TopAbs_FACE, TopoDS.Face_s)


def _vertices(shape):
    return _subshapes(shape, TopAbs_VERTEX, TopoDS.Vertex_s)


def _edges(shape):
    """Every edge but the degenerated ones, which have no length."""
    return [edge for edge in _subshapes(shape, TopAbs_EDGE, TopoDS.Edge_s)
            if not BRep_Tool.Degenerated_s(edge)]


def _copy(shape):
    """A private exact copy, geometry included, triangulation not."""
    return BRepBuilderAPI_Copy(shape, True, False).Shape()


########################################
# Composition


def placed_shape(shape, matrix):
    """`shape` placed by the framework's composed 4x4 `matrix`.

    The upper three rows are sent to OCCT as the exact IEEE-754 values the
    matrix holds, with no tolerance or rounding of its own; the result is
    a new shape and the argument is unchanged. Uncached: a caller placing
    one shape by one matrix repeatedly keeps its own memo.
    """
    values = tuple(float(matrix[row, column])
                   for row in range(3) for column in range(4))
    transform = gp_Trsf()
    transform.SetValues(*values)
    return BRepBuilderAPI_Transform(as_shape(shape), transform, True).Shape()


def _boolean(operation, first, second, first_name, second_name):
    algorithm = {
        'intersection': BRepAlgoAPI_Common,
        'fusion': BRepAlgoAPI_Fuse,
    }[operation]()
    try:
        # OCCT's default Boolean can amend its argument subshapes in place.
        # Keep that result mode: its protected mode gave an invalid common on
        # a real Curta pose where the default result is valid. Instead give
        # the default kernel private exact copies of both reusable operands.
        left, right = _copy(first), _copy(second)
        arguments = TopTools_ListOfShape()
        arguments.Append(left)
        tools = TopTools_ListOfShape()
        tools.Append(right)
        algorithm.SetArguments(arguments)
        algorithm.SetTools(tools)
        algorithm.SetRunParallel(True)
        algorithm.Build()
        if not algorithm.IsDone():
            raise RuntimeError('kernel reported not-done')
        return algorithm.Shape()
    except Exception as error:
        raise RuntimeError(
            f"Exact {operation} failed for {first_name} and "
            f"{second_name}: {error}"
        ) from error


def fuse_shapes(first, second, first_name, second_name):
    """The native fuse of two placed shapes, on private copies of both."""
    return _boolean('fusion', as_shape(first), as_shape(second),
                    first_name, second_name)


########################################
# Comparison and measurement


def intersect_shapes(first, second, first_name, second_name):
    """Intersect native shapes; refuse a witnessed false-empty OCCT common.

    This is the shape-level entry point for exact project diagnostics as well
    as managed assertions.  A finite native section/interior search catches
    *demonstrated* contradictory empties only when the witness is resolved
    beyond native face tolerances; no witness is not a universal
    certificate that every OCCT Boolean is correct.  No faceted fallback,
    fuzzy tolerance or replacement volume is used.
    """
    first, second = as_shape(first), as_shape(second)
    common = _boolean('intersection', first, second, first_name, second_name)
    if _solids(common):
        return common
    try:
        witness = _false_empty_witness(first, second)
    except Exception as error:
        raise ExactCommonVerificationError(
            f'Exact common of {first_name} and {second_name} was empty, '
            f'but its independent native-interior check failed: {error}') from error
    if witness is not None:
        raise ExactCommonInconsistency(
            f'Exact common of {first_name} and {second_name} was empty '
            f'despite a point strictly inside both native solids: '
            f'{witness}. No overlap volume was inferred.')
    return common


def _distance(first, second):
    """The minimal distance between two shapes, measured as CadQuery's
    `Shape.distance` measures it."""
    calculation = BRepExtrema_DistShapeShape(first, second)
    calculation.SetMultiThread(True)
    return calculation.Value()


def _resolved_interior(solid, point):
    """Require separation beyond each boundary face's native tolerance.

    A zero-tolerance classifier can report IN for a rounded point actually
    on a contact face.  The tolerance belongs to the B-rep's uncertainty,
    not to an overlap verdict: this only decides whether a candidate is
    reliable enough to contradict an empty Boolean.
    """
    faces = _faces(solid)
    if not faces:
        raise RuntimeError('classified solid has no boundary faces')
    vertex = BRepBuilderAPI_MakeVertex(
        gp_Pnt(point.X(), point.Y(), point.Z())).Vertex()
    for face in faces:
        tolerance = BRep_Tool.Tolerance_s(face)
        distance = _distance(face, vertex)
        if not (math.isfinite(tolerance) and tolerance >= 0 and
                math.isfinite(distance) and distance >= 0):
            raise RuntimeError('invalid native face tolerance or distance')
        if distance <= tolerance:
            return False
    return True


def _length(edge):
    return GCPnts_AbscissaPoint.Length_s(BRepAdaptor_Curve(edge))


def _position_at(edge, fraction):
    """The point at `fraction` of the edge's arc length, as `(x, y, z)`."""
    curve = BRepAdaptor_Curve(edge)
    length = GCPnts_AbscissaPoint.Length_s(curve)
    parameter = GCPnts_AbscissaPoint(
        curve, length * fraction, curve.FirstParameter()).Parameter()
    point = curve.Value(parameter)
    return (point.X(), point.Y(), point.Z())


def _false_empty_witness(first, second):
    """Return one strict shared-interior point, or None after bounded probes.

    The section locates *candidate* boundary crossings, not material.  A
    positive witness needs one offset point classified TopAbs_IN in a solid
    on EACH side at zero tolerance and separated beyond each native face
    tolerance.  A 3-D stencil avoids assuming a sphere
    normal, and its finite budget is deliberately not a completeness claim.
    """
    solids1, solids2 = _solids(first), _solids(second)
    if not solids1 or not solids2:
        return None
    # The independent witness must not amend either caller-owned input.
    # Keep the same default Section mode as the primary Boolean.
    left, right = _copy(first), _copy(second)
    section = BRepAlgoAPI_Section(left, right, False)
    section.Build()
    if not section.IsDone():
        raise RuntimeError('OCCT section reported not-done')
    crossing = section.Shape()
    if crossing.IsNull():
        raise ValueError('Null TopoDS_Shape object')
    edges = _edges(crossing)
    if not edges:
        return None
    spans = []
    for shape in (first, second):
        low, high = bounds(shape)
        spans.extend(span for span in (high[0] - low[0], high[1] - low[1],
                                       high[2] - low[2])
                     if span > 0 and math.isfinite(span))
    if not spans:
        return None
    scale = min(spans)
    steps = (scale * 1e-4, scale * 1e-3, scale * 1e-2)
    directions = [tuple(value / math.sqrt(sum(one * one for one in direction))
                        for value in direction)
                  for direction in product((-1, 0, 1), repeat=3)
                  if any(direction)]
    classifiers1 = [BRepClass3d_SolidClassifier(solid) for solid in solids1]
    classifiers2 = [BRepClass3d_SolidClassifier(solid) for solid in solids2]

    def inside(classifiers, solids, point):
        found = []
        for classifier, solid in zip(classifiers, solids):
            classifier.Perform(point, 0.0)
            # OCCT's Rejected() is a successful outside-by-rejection result,
            # not a failed classification. UNKNOWN is genuinely undecided.
            if classifier.Rejected():
                continue
            state = classifier.State()
            if state == TopAbs_UNKNOWN:
                raise RuntimeError('OCCT solid classifier returned UNKNOWN')
            if state == TopAbs_IN:
                found.append(solid)
        return found

    for edge in edges[:8]:
        if _length(edge) <= 0:
            continue
        for fraction in (.25, .5, .75):
            at = _position_at(edge, fraction)
            for step in steps:
                for direction in directions:
                    coords = tuple(at[i] + step * direction[i]
                                   for i in range(3))
                    point = gp_Pnt(*coords)
                    candidates1 = inside(classifiers1, solids1, point)
                    if not candidates1:
                        continue
                    candidates2 = inside(classifiers2, solids2, point)
                    if (candidates2 and
                            any(_resolved_interior(solid, point)
                                for solid in candidates1) and
                            any(_resolved_interior(solid, point)
                                for solid in candidates2)):
                        return coords
    return None


def solid_count(shape):
    """The number of solids in `shape`."""
    return len(_solids(as_shape(shape)))


def solid_volume(shape):
    """The sum of the volumes of the solids in `shape`."""
    total = 0
    for solid in _solids(as_shape(shape)):
        properties = GProp_GProps()
        BRepGProp.VolumeProperties_s(solid, properties)
        total += properties.Mass()
    return total


def bounds(shape):
    """The shape's optimal axis-aligned bounding box, as
    `((xmin, ymin, zmin), (xmax, ymax, zmax))`."""
    box = Bnd_Box()
    BRepBndLib.AddOptimal_s(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return ((xmin, ymin, zmin), (xmax, ymax, zmax))


def face_bounds(shape):
    """One local AABB per face of `shape`, in the kernel's face order.

    Each is taken with ``BRepBndLib.Add_s(face, box, False)`` -- OCCT's own
    tolerance enlargement, no triangulation. ``useTriangulation=False``
    keeps a face box a pure function of the exact surface: with ``True``
    the box would depend on whether a triangulation happens to be attached
    and at what deflection, which an STL export or a viewer read can
    change on a shape a caller is already holding. It is also conservative
    by construction -- bounding a face from its surface's own
    poles/parametric bounds plus its tolerance is outward-only slack,
    never inward -- where `bounds` instead calls ``AddOptimal_s``, a
    tighter but slower route unnecessary for a superset test.

    Returns an ``(F, 2, 3)`` float64 array, ``(0, 2, 3)`` for a shape with
    no faces.
    """
    faces = _faces(shape)
    boxes = np.empty((len(faces), 2, 3), dtype=np.float64)
    for index, face in enumerate(faces):
        box = Bnd_Box()
        BRepBndLib.Add_s(face, box, False)
        xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
        boxes[index, 0, :] = (xmin, ymin, zmin)
        boxes[index, 1, :] = (xmax, ymax, zmax)
    return boxes


def _representative_points(solids):
    """One point per solid of ``solids`` -- its first vertex -- or ``None``
    if any solid carries no vertex at all (a full torus is the realistic
    case): the guard does not invent a representative."""
    points = []
    for solid in solids:
        vertices = _vertices(solid)
        if not vertices:
            return None
        point = BRep_Tool.Pnt_s(vertices[0])
        points.append(gp_Pnt(point.X(), point.Y(), point.Z()))
    return points


def _classified_out(points, partner_solids, tolerance):
    """``True`` iff every point in ``points`` classifies strictly outside
    every solid in ``partner_solids``.

    One classifier is loaded per SOLID of the partner -- never one loaded
    from a compound, since `BRepClass3d_SolidClassifier` is specified for
    a solid and the containment proof rests on that -- and `Perform` is
    called once per representative point against it. A rejected
    classification, an OCCT exception, or any state other than outside
    declines the whole guard rather than being treated as a pass.
    """
    for partner_solid in partner_solids:
        try:
            classifier = BRepClass3d_SolidClassifier(partner_solid)
            for point in points:
                classifier.Perform(point, tolerance)
                if classifier.Rejected() or classifier.State() != TopAbs_OUT:
                    return False
        except Exception:
            return False
    return True


def mutually_outside(first, second):
    """The containment guard (ADR-092, step 3): ``True`` iff no solid of
    either placed shape lies inside, or on the boundary of, any solid of
    the other.

    Both directions are required and neither is redundant: a shape wholly
    inside the other has boundaries that do not meet either, so only the
    CONTAINED shape's own representative points reveal it. Declines (never
    a wrong answer) on a shape with no solids on either side -- there is
    then nothing to load a classifier from -- or a solid with no vertex.
    """
    solids1 = _solids(first)
    solids2 = _solids(second)
    if not solids1 or not solids2:
        return False
    points1 = _representative_points(solids1)
    points2 = _representative_points(solids2)
    if points1 is None or points2 is None:
        return False
    tolerance = Precision.Confusion_s()
    return (_classified_out(points1, solids2, tolerance)
            and _classified_out(points2, solids1, tolerance))
