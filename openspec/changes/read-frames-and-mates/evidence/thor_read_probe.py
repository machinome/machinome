# Planning probe for `read-frames-and-mates` (evidence/finding.md, section 4).
#
# Read-only against Thor: run from a scratch directory, never from Thor, as
#
#   SOLID_BUILD_DIR=<scratch>/build PYTHONDONTWRITEBYTECODE=1 \
#       /home/asa/devel/machinome/.venv/bin/python -B thor_read_probe.py
#
# with Thor's checkout on its branch `state-the-mate-line`. It compares the
# resolved frame each constructed declarer caches with the triad Thor's
# `simulation/test_frames.py` re-derives, and prints each root-chain mate's
# ends and freedom. Not a test; nothing imports it.

import sys, time, importlib, math
sys.path[:0] = ['/home/asa/devel/machinome/machinome/WTs/read-frames-and-mates',
                '/home/asa/devel/machinome/projects/Robotic-Arms/Thor']
import machinome; print(machinome.__file__)
from machinome.node.frames import declared_frames, RESOLVED_KEY
from machinome.motion.mates import declared_mates
from simulation.tools.emit_frames import ROOT_CHAIN, MODULES, default_x
def cls(n): return getattr(importlib.import_module('simulation.'+MODULES[n]), n)
def unit(v):
    l = math.sqrt(sum(a*a for a in v)); return tuple(a/l for a in v)
def cross(a,b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
worst = 0
for e in ROOT_CHAIN:
    for owner, fname in ((e.parent, e.fixed), (e.child_class, e.moving)):
        C = cls(owner); t = time.time(); inst = C(); dt = time.time()-t
        r = inst.__dict__[RESOLVED_KEY][fname]
        f = declared_frames(C)[fname]
        z = unit(tuple(float(v) for v in f.z))
        x = unit(tuple(float(v) for v in f.x)) if f.x else default_x(z)
        d = dict(at=tuple(float(v) for v in f.at), x=x, y=cross(z,x), z=z)
        dev = max(abs(a-b) for k in 'at x y z'.split() for a,b in zip(getattr(r,k), d[k]))
        worst = max(worst, dev)
        print(f'{owner}.{fname}: construct {dt:.3f}s dev {dev:.2e} resolved {r!r} types {[type(c).__name__ for c in r.z]}')
    m = declared_mates(cls(e.holder))[e.mate]
    fr = m.freedom
    print('  mate', m.name, m.described(), type(m.moving).__name__, getattr(m.moving,'written',None), type(m.fixed).__name__, getattr(m.fixed,'written',None) or m.fixed.name, 'axis', fr.axis, 'at', fr.at, fr.anchor_written, 'range', fr.range, fr.unit)
print('worst', worst)
