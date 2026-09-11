.. _motion:

================================
Giving the pointer a joint
================================

In :doc:`animation`, we turned the pointer with
``self.pointer.rotate(angle, [0, 0, 1])``. That is still a valid
way to move a part. Now we will name that freedom so another part or
input can drive it.

This chapter extends the small tutorial clock. It does not use the
external Clock 01 design.

1. Name the rotation
====================

Open ``myproject/pointer.py``. Add an import and one declaration
inside the existing ``Pointer`` class; leave its geometry unchanged:

.. code-block:: python

   from solid_node.motion.joints import Revolute

   class Pointer(Solid2Node):
       turn = Revolute(axis=(0, 0, 1), unit="deg")
       # Keep the render() method from the previous chapter.

A revolute joint gives the pointer one angular coordinate. Its axis
passes through the pointer's origin along local Z, just where the pin
passes through it. The joint does not create a hole or change the mesh;
it describes how the body moves.

A joint written on a class uses that body's own coordinate frame.
If an assembly later translates or rotates the pointer, its joint
travels with it.

2. Bind the coordinate
======================

In ``SimpleClock.simulate()``, replace the call to
``rotate()`` with an assignment:

.. code-block:: python

   def simulate(self):
       self.pointer.turn = -360 * self.time

Save and play the model. It should make the same clockwise turn as
before. At timeline 0.25 it should still point a quarter-turn from its
starting direction. We changed how the motion is expressed, not its
meaning.

Do not keep both the assignment and the old ``rotate()``:
binding the joint already applies the rotation.

3. Supply an independent input
==============================

For a manually positioned pointer, replace the time-driven binding with
a driver and relation. Add the import and declarations to
``myproject/myproject.py``:

.. code-block:: python

   from solid_node.simulation import Driver

   class SimpleClock(AssemblyNode):
       angle = Driver(default=0, range=(-360, 0), unit="deg")
       base = ClockBase()
       pointer = Pointer()

       angle.drives(pointer.turn)

Remove the old ``simulate()`` for this variant. The driver is now
the source of the pointer angle; time no longer supplies it. Drag
``angle`` to -90 in the browser and compare it with the quarter-turn
pose from step 2.

A driver is an input. A joint is a freedom of a body. The relation
connects the two. A numeric range on a driver describes its control
surface; it is not a mechanical stop.

4. Relate a second coordinate
=============================

A second pointer can follow the first at a different ratio. Try this
variant after the one-pointer control works:

.. code-block:: python

   class SimpleClock(AssemblyNode):
       angle = Driver(default=0, range=(-360, 0), unit="deg")
       base = ClockBase()
       pointer = Pointer()
       follower = Pointer()

       angle.drives(pointer.turn)
       pointer.turn.drives(follower.turn, ratio=0.5)

       def render(self):
           self.follower.translate([0, 0, 12])

At -180 degrees on the input, the first pointer turns -180 and the
follower turns -90. The follower is lifted 12 mm so these demonstration
pointers do not occupy the same layer.

This relation prescribes a ratio; it does not create a pair of gears.
A model of actual gears must also describe their teeth, placement and
registration and test the resulting fit. That is a reason to explore the
complete :doc:`example machines <examples>` after learning the API.

Where to go next
====================

Use a ``Prismatic`` joint for a sliding part. The other joint kinds,
placement-site frames, invertible laws and multi-coordinate relations
are covered in :doc:`driving` and :doc:`api-reference`.

Continue with :doc:`driving` to add instructions and connect inputs
through nested assemblies, then :doc:`scenarios` to test an input
sequence rather than one pose.
