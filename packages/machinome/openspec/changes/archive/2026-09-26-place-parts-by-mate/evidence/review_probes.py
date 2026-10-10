"""Adversarial probes the review makes itself, outside the suite."""
import math, random, sys
import numpy as np
from machinome.node import AssemblyNode, Frame
from machinome.node.adapters.cadquery import CadQueryNode
from machinome.motion.joints import Revolute
from machinome.motion.mates import _axis_angle
from machinome.simulation import Driver
from machinome.node.operations import Rotation
from machinome.node.base import _compose_world_matrix

# 1. axis-angle round trip on random rotations, all quadrants
random.seed(7)
worst = 0.0
for _ in range(2000):
    axis = np.array([random.uniform(-1, 1) for _ in range(3)]); axis /= np.linalg.norm(axis)
    angle = random.choice([random.uniform(0.01, 179.99), 180.0, 90.0, 120.0, 135.0, 179.999999])
    R = Rotation(angle, list(axis), None).matrix()[:3, :3]
    got = _axis_angle([[float(R[i][j]) for j in range(3)] for i in range(3)])
    a2, ax2 = got
    R2 = Rotation(a2, list(ax2), None).matrix()[:3, :3]
    worst = max(worst, float(np.abs(R2 - R).max()))
print('1. axis-angle round trip, worst matrix residue over 2000 rotations:', worst)
assert worst < 1e-9

# 2. a three-link chain: mated vs hand-placed, compared at several angles
class Link(CadQueryNode):
    def render(self):
        import cadquery as cq
        return cq.Workplane('XY').box(10, 10, 10)

class Tip(Link):
    pass

class ForearmM(AssemblyNode):
    hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))
    wrist_pin = Frame(at=(0, 0, 111.5), z=(0, 1, 0))
    tip = Tip()
    wrist = tip.seat.on(wrist_pin, Revolute(range=(-105, 105), unit='deg')) if False else None

# Tip needs a frame first; redo with proper declaration order
class TipM(Link):
    seat = Frame(at=(0, 0, 0), z=(1, 0, 0), x=(0, 0, 1))

class ForearmM(AssemblyNode):
    hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))
    wrist_pin = Frame(at=(0, 0, 111.5), z=(0, 1, 0))
    body = Link()
    tip = TipM()
    wrist = tip.seat.on(wrist_pin, Revolute(range=(-105, 105), unit='deg'))

class ArmM(AssemblyNode):
    elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))
    plate = Link()
    forearm = ForearmM()
    elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135), unit='deg'))

class RootM(AssemblyNode):
    a = Driver(default=0.0, range=(-135, 135), unit='deg')
    b = Driver(default=0.0, range=(-105, 105), unit='deg')
    arm = ArmM()
    a.drives(arm.elbow)
    b.drives(arm.forearm.wrist)

# hand-placed twin, the way Thor writes it today
class TipH(Link):
    wrist = Revolute(axis=(1, 0, 0), unit='deg')

class ForearmH(AssemblyNode):
    elbow = Revolute(axis=(0, 1, 0), at=(0, 0, 81.5), unit='deg')
    body = Link()
    tip = TipH()
    def render(self):
        self.tip.rotate(90.0, [0, 0, 1]); self.tip.translate([0, 0, 111.5])

class ArmH(AssemblyNode):
    plate = Link()
    forearm = ForearmH()
    def render(self):
        self.forearm.rotate(90.0, [1, 0, 0]); self.forearm.translate([0, 241.5, 68])

class RootH(AssemblyNode):
    a = Driver(default=0.0, range=(-135, 135), unit='deg')
    b = Driver(default=0.0, range=(-105, 105), unit='deg')
    arm = ArmH()
    a.drives(arm.forearm.elbow)
    b.drives(arm.forearm.tip.wrist)

def world(node):
    return _compose_world_matrix(node)

def poses(root):
    root.render()
    out = {}
    for name, n in (('forearm', root.arm.forearm), ('tip', root.arm.forearm.tip), ('body', root.arm.forearm.body)):
        out[name] = np.array(world(n), dtype=float)
    return out

worst = 0.0
for a, b in [(0, 0), (30, 0), (0, 45), (-90, 20), (60, -40), (135, 105), (-135, -105)]:
    m, h = RootM(), RootH()
    m.set_state(a=a, b=b); h.set_state(a=a, b=b)
    pm, ph = poses(m), poses(h)
    for k in pm:
        worst = max(worst, float(np.abs(pm[k] - ph[k]).max()))
print('2. mated chain vs hand-placed twin, worst pose deviation over 7 bindings x 3 bodies:', worst)
assert worst < 1e-9

# 3. fixed end on a child hand-placed with a ROTATION and a translation
class Base(Link):
    seat = Frame(at=(0, 0, 79), z=(0, 0, 1))
class HousingM(Link):
    foot = Frame(at=(0, 0, 0), z=(0, 0, 1))
class RootB(AssemblyNode):
    base = Base()
    housing = HousingM()
    slew = housing.foot.on(base.seat, Revolute(unit='deg'))
    def render(self):
        self.base.rotate(90.0, [0, 0, 1]); self.base.translate([5, 0, 3])
r = RootB(); r.render()
W = np.array(world(r.housing), dtype=float)
expect = np.array(Rotation(90.0, [0,0,1], None).matrix(), dtype=float); expect[:3, 3] = [5, 0, 82]
print('3. fixed end on a rotated+translated child: housing world matrix residue:', float(np.abs(W - expect).max()))
assert np.abs(W - expect).max() < 1e-9
print('all probes pass')
