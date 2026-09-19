"""The smallest tree that carries the finding.

A RUNNING root with a `Prismatic` on a ROOT-LEVEL LEAF (`slide`), the same
joint on a leaf one level down inside a sub-assembly (`arm.slide`), and a
`Free` on a third leaf (`floater`), which places SEVERAL operations for one
binding.  `BenchBody` is the identical tree with no time base: the untimed
control.
"""
from solid2 import cube

from solid_node.motion.joints import Free, Prismatic
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode, Solid2Node
from solid_node.simulation import Driver, Instruction


class Slide(Solid2Node):
    """A carriage travelling along one line: a joint on a LEAF."""

    travel = Prismatic(axis=(1, 0, 0), unit='mm')

    def render(self):
        return cube([10, 6, 6], center=True)


class Floater(Solid2Node):
    """A body with six freedoms: one joint, several operations."""

    pose = Free(at=(0, 0, 0))

    def render(self):
        return cube([6, 6, 6], center=True)


class Bed(Solid2Node):
    def render(self):
        return cube([60, 30, 2], center=True)


class Arm(AssemblyNode):
    """A SUB-ASSEMBLY holding a leaf with the same joint: the runner
    checkpoints only the ROOT's own children, so this one is never
    restored."""

    slide = Slide()

    def render(self):
        self.slide.translate([0.0, 10.0, 8.0])


class BenchBody(AssemblyNode):
    """The machine with no time base: the untimed control."""

    push = Driver(default=0.0, range=(0.0, 20.0), unit='mm')
    rise = Driver(default=0.0, range=(0.0, 20.0), unit='mm')

    bed = Bed()
    slide = Slide()
    floater = Floater()
    arm = Arm()

    push.drives(slide.travel)
    push.drives(arm.slide.travel)
    # Every one of the six, because a running simulation owns them all and
    # needs a rest value for each.
    rise.drives(floater.pose.x, ratio=0.5)
    rise.drives(floater.pose.y, ratio=0.25)
    rise.drives(floater.pose.z)
    rise.drives(floater.pose.roll, ratio=2.0)
    rise.drives(floater.pose.pitch, ratio=-1.0)
    rise.drives(floater.pose.yaw, ratio=3.0)

    instructions = {
        'Push': Instruction(by={'push': 5.0}, duration=0.5),
        'Lift': Instruction(by={'rise': 3.0}, duration=0.5),
    }

    def render(self):
        self.slide.translate([0.0, 0.0, 4.0])
        self.floater.translate([0.0, -10.0, 4.0])


class Bench(BenchBody):
    """The same machine, running."""

    time = Time.running()
