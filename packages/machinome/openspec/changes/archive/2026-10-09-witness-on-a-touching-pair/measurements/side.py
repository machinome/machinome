"""Proposer's sketch: the nearest-boundary side of a point in a solid, and a
witness search that consults it before each classifier. Scratch only."""
import math
from itertools import product
import machinome.engine.brep as brep
from OCP.BRep import BRep_Tool, BRep_Builder
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_SupportType
from OCP.BRepGProp import BRepGProp_Face
from OCP.Extrema import Extrema_ExtFlag_MIN
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS, TopoDS_Compound
from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape
from OCP.gp import gp_Pnt, gp_Vec, gp_Pnt2d
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepClass3d import BRepClass3d_SolidClassifier

IN_FACE = BRepExtrema_SupportType.BRepExtrema_IsInFace
ON_EDGE = BRepExtrema_SupportType.BRepExtrema_IsOnEdge
STATS = {}


def bump(key, n=1):
    STATS[key] = STATS.get(key, 0) + n


class Boundary:
    """One solid's boundary for the side test: its shells as one compound and
    its edge-to-face map."""

    def __init__(self, solid):
        self.solid = solid
        compound = TopoDS_Compound(); builder = BRep_Builder()
        builder.MakeCompound(compound)
        explorer = TopExp_Explorer(solid, TopAbs_SHELL)
        while explorer.More():
            builder.Add(compound, explorer.Current()); explorer.Next()
        self.boundary = compound
        self.edge_faces = TopTools_IndexedDataMapOfShapeListOfShape()
        TopExp.MapShapesAndUniqueAncestors_s(solid, TopAbs_EDGE, TopAbs_FACE,
                                             self.edge_faces)

    def side(self, coords):
        """'OUT', 'IN', 'ON' (within the nearest support's face tolerance) or
        None (undecided: a vertex, a failed extrema, an ambiguous sign)."""
        point = gp_Pnt(*coords)
        vertex = BRepBuilderAPI_MakeVertex(point).Vertex()
        extrema = BRepExtrema_DistShapeShape()
        extrema.LoadS1(vertex); extrema.LoadS2(self.boundary)
        extrema.SetFlag(Extrema_ExtFlag_MIN)
        extrema.Perform()
        if not extrema.IsDone() or extrema.NbSolution() < 1:
            return None
        distance = extrema.Value()
        if not (math.isfinite(distance) and distance >= 0):
            return None
        verdicts = set()
        for n in range(1, extrema.NbSolution() + 1):
            kind = extrema.SupportTypeShape2(n)
            near = extrema.PointOnShape2(n)
            away = gp_Vec(near, point)
            if kind == IN_FACE:
                face = TopoDS.Face_s(extrema.SupportOnShape2(n))
                tolerance = BRep_Tool.Tolerance_s(face)
                if not (math.isfinite(tolerance) and tolerance >= 0):
                    return None
                if distance <= tolerance:
                    return 'ON'
                u, v = extrema.ParOnFaceS2(n)
                normals = [self._normal(face, u, v)]
            elif kind == ON_EDGE:
                edge = TopoDS.Edge_s(extrema.SupportOnShape2(n))
                if BRep_Tool.Degenerated_s(edge) or not BRep_Tool.SameParameter_s(edge):
                    bump('undecided_edge_parameter')
                    return None
                (t,) = extrema.ParOnEdgeS2(n)
                faces = self.edge_faces.FindFromKey(edge)
                normals = []
                for face in faces:
                    face = TopoDS.Face_s(face)
                    tolerance = BRep_Tool.Tolerance_s(face)
                    if not (math.isfinite(tolerance) and tolerance >= 0):
                        return None
                    if distance <= tolerance:
                        return 'ON'
                    first = last = 0.0
                    pcurve = BRep_Tool.CurveOnSurface_s(edge, face, first, last)
                    uv = pcurve.Value(t)
                    normals.append(self._normal(face, uv.X(), uv.Y()))
                if len(normals) == 1 and BRep_Tool.IsClosed_s(
                        edge, TopoDS.Face_s(faces.First())):
                    normals = normals * 2  # a seam: one face on both sides
                if len(normals) != 2:
                    bump('undecided_edge_faces_' + str(len(normals)))
                    return None
            else:
                bump('undecided_vertex')
                return None
            total = gp_Vec(0, 0, 0)
            for normal in normals:
                if normal is None:
                    return None
                total = total.Added(normal)
            if total.Magnitude() < 1e-6:
                return None
            cosine = away.Dot(total) / (away.Magnitude() * total.Magnitude())
            if abs(cosine) < (0.9 if kind == IN_FACE else 0.1):
                bump('undecided_sign')
                return None
            verdicts.add('OUT' if cosine > 0 else 'IN')
        return verdicts.pop() if len(verdicts) == 1 else None

    @staticmethod
    def _normal(face, u, v):
        at, normal = gp_Pnt(), gp_Vec()
        BRepGProp_Face(face).Normal(u, v, at, normal)
        if normal.Magnitude() < 1e-12:
            return None
        return normal.Normalized()


def witness(first, second, mode='side-first'):
    """The bench's _false_empty_witness, with each operand's side test asked
    before its classifier: a point OUT of, or ON, every solid of an operand by
    the side test is skipped without a classifier."""
    solids1, solids2 = brep._solids(first), brep._solids(second)
    if not solids1 or not solids2:
        return None
    left, right = brep._copy(first), brep._copy(second)
    section = brep.BRepAlgoAPI_Section(left, right, False)
    section.Build()
    if not section.IsDone():
        raise RuntimeError('OCCT section reported not-done')
    crossing = section.Shape()
    edges = brep._edges(crossing)
    if not edges:
        return None
    spans = []
    for shape in (first, second):
        low, high = brep.bounds(shape)
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
    classifiers1 = [brep.BRepClass3d_SolidClassifier(s) for s in solids1]
    classifiers2 = [brep.BRepClass3d_SolidClassifier(s) for s in solids2]
    boundaries1 = [Boundary(s) for s in solids1]
    boundaries2 = [Boundary(s) for s in solids2]

    def classified_in(classifier, point):
        bump('classify')
        classifier.Perform(point, 0.0)
        if classifier.Rejected():
            return False
        state = classifier.State()
        if state == brep.TopAbs_UNKNOWN:
            raise RuntimeError('OCCT solid classifier returned UNKNOWN')
        return state == brep.TopAbs_IN

    def possible(boundaries, coords):
        kept = []
        for index, boundary in enumerate(boundaries):
            bump('side')
            verdict = boundary.side(coords)
            bump('side_' + str(verdict))
            if verdict not in ('OUT', 'ON'):
                kept.append(index)
        return kept

    def inside(classifiers, solids, kept, point):
        return [(classifiers[i], solids[i]) for i in kept
                if classified_in(classifiers[i], point)]

    def resolved(candidates, point):
        margins = [(c, brep._resolved_interior(s, point)) for c, s in candidates]
        return [(c, m) for c, m in margins if m is not None]

    def corroborated(coords, c1, c2, margin):
        for axis in range(3):
            for sign in (1, -1):
                probe = list(coords)
                probe[axis] += sign * margin / 2
                probe = gp_Pnt(*probe)
                if not (classified_in(c1, probe) and classified_in(c2, probe)):
                    return False
        return True

    faces1 = sum(len(brep._faces(x)) for x in solids1)
    faces2 = sum(len(brep._faces(x)) for x in solids2)
    swap = faces2 < faces1

    def small_first(coords, point):
        # the fewer-faced operand's classifier, then both side tests, then
        # the other operand's classifier
        cs, ss, bs = (classifiers2, solids2, boundaries2) if swap else (classifiers1, solids1, boundaries1)
        co, so, bo = (classifiers1, solids1, boundaries1) if swap else (classifiers2, solids2, boundaries2)
        everyone = list(range(len(ss)))
        small = inside(cs, ss, everyone, point)
        if not small:
            return None
        kept_other = possible(bo, coords)
        if not kept_other:
            return None
        kept_small = possible(bs, coords)
        small = [(c, x) for c, x in small if any(c is cs[i] for i in kept_small)]
        if not small:
            return None
        other = inside(co, so, kept_other, point)
        if not other:
            return None
        return (other, small) if swap else (small, other)

    for edge in edges[:8]:
        if brep._length(edge) <= 0:
            continue
        for fraction in (.25, .5, .75):
            at = brep._position_at(edge, fraction)
            for step in steps:
                for direction in directions:
                    coords = tuple(at[i] + step * direction[i] for i in range(3))
                    point = gp_Pnt(*coords)
                    if mode == 'small-first':
                        found = small_first(coords, point)
                        if found is None:
                            continue
                        candidates1, candidates2 = found
                        margins1 = resolved(candidates1, point)
                        if not margins1:
                            continue
                        margins2 = resolved(candidates2, point)
                        if any(corroborated(coords, c1, c2, min(m1, m2))
                               for c1, m1 in margins1 for c2, m2 in margins2):
                            return coords
                        continue
                    kept1 = possible(boundaries1, coords)
                    if not kept1:
                        continue
                    kept2 = possible(boundaries2, coords)
                    if not kept2:
                        continue
                    candidates1 = inside(classifiers1, solids1, kept1, point)
                    if not candidates1:
                        continue
                    candidates2 = inside(classifiers2, solids2, kept2, point)
                    if not candidates2:
                        continue
                    margins1 = resolved(candidates1, point)
                    if not margins1:
                        continue
                    margins2 = resolved(candidates2, point)
                    if any(corroborated(coords, c1, c2, min(m1, m2))
                           for c1, m1 in margins1 for c2, m2 in margins2):
                        return coords
    return None
