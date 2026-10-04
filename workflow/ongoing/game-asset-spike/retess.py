"""Spike helper: re-tessellate every B-rep a document's meshes came from at a
coarser deflection, writing STLs under OUT_DIR at the same relative paths.

Runs in the workspace venv (needs OCP). Throwaway; writes only under OUT_DIR.

usage: retess.py VIEWER_JSON OUT_DIR [--linear MM] [--angular RAD]
"""
import argparse, json, os, sys, time
import numpy as np
import trimesh
from OCP.TopoDS import TopoDS_Shape, TopoDS
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepTools import BRepTools
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
from OCP.TopLoc import TopLoc_Location


def read_brep(path):
    shape = TopoDS_Shape()
    BRepTools.Read_s(shape, path, BRep_Builder())
    return shape


def tessellate(shape, linear, angular):
    BRepTools.Clean_s(shape)
    BRepMesh_IncrementalMesh(shape, linear, False, angular, True)
    verts, faces = [], []
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        tri = BRep_Tool.Triangulation_s(face, loc)
        if tri is not None:
            trsf = loc.Transformation()
            base = len(verts)
            for i in range(1, tri.NbNodes() + 1):
                p = tri.Node(i).Transformed(trsf)
                verts.append((p.X(), p.Y(), p.Z()))
            flip = face.Orientation() == TopAbs_REVERSED
            for i in range(1, tri.NbTriangles() + 1):
                t = tri.Triangle(i)
                a, b, c = t.Value(1), t.Value(2), t.Value(3)
                if flip:
                    a, c = c, a
                faces.append((base + a - 1, base + b - 1, base + c - 1))
        exp.Next()
    return np.array(verts, float), np.array(faces, np.int64)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('document')
    ap.add_argument('out')
    ap.add_argument('--linear', type=float, default=0.5)
    ap.add_argument('--angular', type=float, default=0.5)
    args = ap.parse_args()
    doc = json.load(open(args.document))
    base = os.path.dirname(args.document)
    models = set()

    def walk(n):
        if 'model' in n:
            models.add(n['model'])
        for c in n.get('children') or []:
            walk(c)
    walk(doc['root'])

    t0 = time.time()
    rows = []
    fine_total = coarse_total = 0
    for rel in sorted(models):
        brep = os.path.join(base, rel[:-4] + '.brep')
        fine = trimesh.load(os.path.join(base, rel), force='mesh')
        v, f = tessellate(read_brep(brep), args.linear, args.angular)
        out = os.path.join(args.out, rel)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        m = trimesh.Trimesh(v, f, process=True)
        m.export(out)
        rows.append(dict(model=rel, fine=len(fine.faces), coarse=len(m.faces), watertight=bool(m.is_watertight)))
        fine_total += len(fine.faces)
        coarse_total += len(m.faces)
    report = dict(linear=args.linear, angular=args.angular, models=len(rows), fine_distinct=fine_total,
                  coarse_distinct=coarse_total, seconds=round(time.time() - t0, 1), rows=rows)
    json.dump(report, open(os.path.join(args.out, 'retess.json'), 'w'), indent=1)
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}))


if __name__ == '__main__':
    main()
