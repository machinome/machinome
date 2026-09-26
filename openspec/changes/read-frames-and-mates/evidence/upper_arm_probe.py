# Planning probe for `read-frames-and-mates` (evidence/finding.md, section 4,
# last paragraph): the manual's `UpperArm`, realized with `reach=150`.
#
# Run from a scratch directory holding a `pyproject.toml` with an empty
# `[tool.machinome]` table, with `SOLID_BUILD_DIR` pointing at scratch and
# `PYTHONDONTWRITEBYTECODE=1`. Not a test; nothing imports it.

import sys
sys.path[:0] = ['/home/asa/devel/machinome/machinome/WTs/read-frames-and-mates']
from solid2 import cube
from machinome.motion.joints import Revolute
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.base import AbstractBaseNode
from machinome.node.frames import Frame, RESOLVED_KEY
from machinome.parameters import Length
from machinome.motion.mates import declared_mates

class Forearm(Solid2Node):
    hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))
    def render(self): return cube([20, 20, 160])

class UpperArm(AssemblyNode):
    reach = Length(160)
    elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))
    forearm = Forearm()
    elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135), unit='deg'))

class Plain(Solid2Node):
    def render(self): return cube(1)

print(type(UpperArm.forearm), isinstance(UpperArm.forearm, AbstractBaseNode))
arm = UpperArm(reach=150)
print(type(arm.forearm), type(arm.forearm).__mro__[:3])
print(arm.__dict__.get(RESOLVED_KEY))
print(arm.forearm.__dict__.get(RESOLVED_KEY))
print(Plain().__dict__.get(RESOLVED_KEY, 'absent'))
m = declared_mates(UpperArm)['elbow']
print(m.name, m.moving.written, m.moving.frame, m.fixed, m.fixed.name, m.freedom.axis, m.freedom.at, m.freedom.anchor_written, m.freedom.range, m.freedom.unit)
print(arm.elbow, type(arm.elbow))
arm.render()
print([o.serialized for o in arm.forearm.operations])
