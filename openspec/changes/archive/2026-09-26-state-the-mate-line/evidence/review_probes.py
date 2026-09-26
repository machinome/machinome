"""Adversarial probes of state-the-mate-line, outside the suite."""
import math
import numpy as np

from machinome.motion.joints import Revolute
from machinome.motion.mates import declared_mates
from machinome.node import AssemblyNode
from machinome.node.base import _compose_world_matrix
from machinome.node.frames import Frame
from machinome.parameters import Length
from machinome.simulation import Driver
from tests.mate_project import arm, line, verbatim

H = math.sqrt(0.5)


def rot(deg, axis):
    a = np.array(axis, float)
    a /= np.linalg.norm(a)
    t = math.radians(deg)
    c, s = math.cos(t), math.sin(t)
    x, y, z = a
    R = np.eye(4)
    R[:3, :3] = [[c + x*x*(1-c), x*y*(1-c) - z*s, x*z*(1-c) + y*s],
                 [y*x*(1-c) + z*s, c + y*y*(1-c), y*z*(1-c) - x*s],
                 [z*x*(1-c) - y*s, z*y*(1-c) + x*s, c + z*z*(1-c)]]
    return R


def trans(v):
    T = np.eye(4)
    T[:3, 3] = v
    return T


PLATE = trans((7, 11, 13))


def world(node):
    return np.asarray(_compose_world_matrix(node), float)


def check(label, got, expected):
    dev = float(np.abs(got - expected).max())
    print(f"{label}: max deviation {dev:.3e}", "OK" if dev < 1e-9 else "FAIL")


# 1. Verbatim shoulder at 47 vs hand-derived expectation and vs twin.
h = line.VerbatimShoulder(); h.shoulder = 47; h.render()
M = trans((0, -68, 123)) @ rot(180, (0, H, H)) @ rot(47, (0, 0, 1)) @ PLATE
check("shoulder@47 vs hand matrix", world(h.art2.plate), M)
t = verbatim.HandShoulder(); t.art2.shoulder = 47; t.render()
check("shoulder@47 vs twin", world(h.art2.plate), world(t.art2.plate))

# 2. Wrist at -63.
w = line.VerbatimWrist(); w.wrist = -63; w.render()
M = trans((0, 0, 111.5)) @ rot(90, (0, 0, 1)) @ rot(-63, (1, 0, 0)) @ PLATE
check("wrist@-63 vs hand matrix", world(w.art56.plate), M)
tw = verbatim.HandWrist(); tw.art56.wrist = -63; tw.render()
check("wrist@-63 vs twin", world(w.art56.plate), world(tw.art56.plate))

# 3. Yaw at 30 stated vs by frame (reversed z): the two differ by 60 deg.
y = line.VerbatimYaw(); y.yaw = 30; y.render()
M = trans((0, 0, -1)) @ rot(180, (0, 1, 0)) @ rot(30, (0, 0, 1)) @ PLATE
check("yaw@30 stated vs hand matrix", world(y.art4.plate), M)
r = verbatim.ReversedYawByFrame(); r.yaw = 30; r.render()
M2 = trans((0, 0, -1)) @ rot(180, (0, 1, 0)) @ rot(-30, (0, 0, 1)) @ PLATE
check("yaw@30 by frame vs hand matrix (turns -30 about +z)", world(r.art4.plate), M2)

# 4. Anchored housing vs MatedHousing: same pose at 30; also at 200 (out of any range? none declared).
a = line.AnchoredHousing(); a.shoulder = 30; a.render()
b = arm.MatedHousing(); b.shoulder = 30; b.render()
for name in ('art2',):
    check("anchored vs framed housing art2", world(getattr(a, name)), world(getattr(b, name)))

# 5. Sentinel identity survives.
m = declared_mates(line.VerbatimShoulder)['shoulder']
print("joint.at is freedom.at:", m.joint.at is m.freedom.at, "| written:", m.freedom.anchor_written)
m2 = declared_mates(verbatim.ReversedYawByFrame)['yaw']
print("no line: joint.axis is frame.z:", m2.joint.axis is verbatim.Art4.bore.z,
      "| joint.at is frame.at:", m2.joint.at is verbatim.Art4.bore.at)


# 6. Refusals and acceptances beyond the suite.
def attempt(label, make):
    try:
        cls = make()
    except TypeError as error:
        print(f"REFUSED {label}: {error}")
    else:
        mate = declared_mates(cls)['swing']
        print(f"ACCEPTED {label}: axis={mate.joint.axis!r} at={mate.joint.at!r}")


class Pin(verbatim.Link):
    hinge = Frame()


def driver_in_at():
    class A(AssemblyNode):
        lift = Driver(default=1.0, unit='deg')
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(at=(0, 0, lift)))
    return A


def whole_token():
    class A(AssemblyNode):
        lift = Length(5)
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(at=lift))
    return A


def numpy_axis():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(axis=np.array([0.0, 0.0, 1.0])))
    return A


def numpy_int_axis():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(axis=np.array([0, 0, 1])))
    return A


def list_axis():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(axis=[0, 0, 1]))
    return A


def string_axis():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(axis='xyz'))
    return A


def tiny_axis():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(axis=(0, 0, 1e-10)))
    return A


def none_component():
    class A(AssemblyNode):
        pin = Frame()
        part = Pin()
        swing = part.hinge.on(pin, Revolute(at=(0, None, 0)))
    return A


for label, make in (('driver in at', driver_in_at), ('whole token', whole_token),
                    ('numpy float axis', numpy_axis), ('numpy int axis', numpy_int_axis),
                    ('list axis', list_axis), ('string axis', string_axis),
                    ('tiny axis', tiny_axis), ('None component', none_component)):
    attempt(label, make)

# 7. The class-declared axis-less refusal outside a mate is unchanged.
try:
    class Loose(verbatim.Link):
        turn = Revolute(unit='deg')
except TypeError as error:
    print("axis-less outside a mate:", error)
