5. Buttons
==========

A slider answers "what does this pose look like". A machine also has
operations: home the axis, count to ten, return to rest. Those are
**instructions**, and the viewer makes them buttons.

Declare the moves
-----------------

.. literalinclude:: counter/c05_buttons.py
   :language: python
   :lines: 2-

An ``Instruction`` names driver targets in design units and a duration in
seconds. Declared in an ``instructions`` table on the assembly that owns
the move, it becomes a button in the viewer and a ``trigger()`` in
simulations and in the browser API. Triggering one ramps every named
driver from its current value to the target over the duration and lands
exactly on it; triggering another while one runs replaces the ramp.

The module is short because it changes nothing else: ``Counter`` here
subclasses chapter four's and adds the table. In your project, add the
table to the class you have.

.. machinome:: /_exports/counter-05
   :height: 420px

Press **Count to ten** and watch the tens drum step at the end. Press
**Rest**.

Where a control belongs
-----------------------

The viewer scopes controls by assembly: an assembly's sliders and buttons
appear when that assembly is focused, and a breadcrumb walks focus down
into subassemblies that declare inputs and back up. A root that declares
nothing shows no controls, even when its children declare plenty. So
declare a move on the assembly it belongs to: an axis's travel on the
axis, the whole machine's ``Home`` on the machine. The counter is one
assembly, so everything is at the top.

An instruction's targets resolve relative to the declaring assembly, and
a driver's public name is its **instance-qualified id**: the dotted path
of the attributes that hold its assembly, then the driver's name. A
machine with two axes of one class has ``x_axis.position`` and
``y_axis.position``, one string each, the same string in the published
document, in ``set_state`` and in an instruction's targets.

Relative moves
--------------

An instruction may also state travel instead of a destination:
``Instruction(by={'crank': 360.0}, duration=2.0)`` turns the crank once
from wherever it stands. Under a posed machine like this one, a relative
instruction drives a simulation but is not published as a button; from
:doc:`chapter eight <08-running>` on, where the machine keeps its
history, both forms become buttons, and "turn once" is the button a
counter wants.

Next: :doc:`06-fit`.
