Joints
======

A joint says where a body may move, next to the body, once. It owns one
coordinate (``Free`` owns six) and that coordinate is a port: reading the
joint on an instance gives the port slot, assigning to it binds through
the same path ``connect()`` uses, and ``declared_ports`` reports it under
the joint's name. Binding the coordinate moves the body: the framework
composes the motion the joint describes onto the node's rest placement.

The four joints, from ``machinome.motion.joints``:

``Revolute(axis, at=(0, 0, 0), range=None, unit='deg')``
    turns the body about the line through ``at`` along ``axis``.

``Prismatic(axis, at=(0, 0, 0), range=None, unit='mm')``
    slides the body along ``axis``. ``at`` does not affect the placement,
    a translation along a line is the same wherever the line is taken to
    pass; it is carried as the declared position of the slide for a
    reader or a consumer.

``Orbit(axis, at=(0, 0, 0), carries=(0, 0, 0), range=None, unit='deg')``
    carries a point of the body round a line while the body's own
    attitude stays fixed: a cycloidal disk on its eccentric, a
    connecting rod's big end. The eccentric radius and the starting
    phase are never typed; they derive from ``carries``, the point of
    the body that travels, and the line. A ``carries`` that lies on the
    line derives a radius of zero and is refused by name at the first
    binding.

``Free(at=(0, 0, 0), angle_unit='deg', length_unit='mm')``
    floats a body on all six freedoms: ``pose.roll``, ``pose.pitch``,
    ``pose.yaw``, ``pose.x``, ``pose.y``, ``pose.z``, each an ordinary
    coordinate reached by its dotted name and bound by assignment or by
    a relation, never by a wiring keyword. Its composition is fixed,
    ``R(roll, x̂) · R(pitch, ŷ) · R(yaw, ẑ) · T(x, y, z)`` about ``at``
    in the body's own frame's fixed directions, so the translation is
    outermost and displaces along those directions rather than along
    whatever the rotations turned the body to. An unbound coordinate
    places nothing, and binding any one re-places the whole joint. No
    ``axis`` and no ``range``: a free body has no travel to bound. Three
    angles gimbal-lock at ``pitch = ±90°``, as any three-angle attitude
    does.

The frame rule
--------------

**A joint is stated in the frame of whoever declares it, and there are
two declarers.**

Written in a **class body**, ``axis``, ``at`` and ``carries`` are read in
that body's own rest frame, the frame its own ``render()`` states its
geometry in, one rest placement away from wherever its parent puts it.
``at`` defaults to the body's own origin, the case of a wheel turning on
its own bearing. Because the joint's operations are placed innermost,
before the rest placement, **a body its parent rotates carries its joint
line with it**: a shared class placed at several sites, or several
attitudes, states one declaration and gets the right line everywhere.

.. code-block:: python

    class Forearm(AssemblyNode):
        elbow = Revolute(axis=(0, 1, 0), at=(0, 0, 81.5),
                         range=(-135, 135), unit='deg')

    class Arm(AssemblyNode):
        angle = Driver(default=0.0, unit='deg')
        forearm = Forearm()

        def render(self):
            self.forearm.rotate(90, [1, 0, 0])
            self.forearm.translate([0, 241.5, 68])

        def simulate(self):
            self.forearm.elbow = self.angle

The elbow is 81.5 mm up the forearm along the forearm's own ``y``. The
framework applies ``translate([0, 0, -81.5])``, ``rotate(angle, [0, 1,
0])``, ``translate([0, 0, 81.5])``, innermost, before the rest placement,
which is the arithmetic every robot arm otherwise writes by hand to carry
a parent-frame pivot into a part's own coordinates. Nothing here needs to
know that the parent also turns the forearm and moves it out along the
arm. An ``at`` that restates the parent's placement is a bug, a double
offset, never a requirement.

Passed as a **keyword where a parent declares a child**, a joint is the
parent's own statement about a child it is placing, read in the parent's
frame, with ``at`` defaulting to the parent's origin:

.. code-block:: python

    class Rack(AssemblyNode):
        screw = ZScrew(turn=Revolute(axis=(0, 0, 1), unit='deg'))

    class MotorDrive(AssemblyNode):
        gear_screws = GearLockScrew(
            orbit=Revolute(axis=(0, 0, 1), unit='deg')).repeat(2)

This is for the bought bearing, the fastener, the shared catalogue class
that carries no joint of its own: where the parent's origin already is
the line, no anchor is needed at all. The sentence a reader gets wrong:
**a child the parent translates swings about the parent's origin, not its
own**, unless ``at`` names the child's placement. One declaration serves
every copy of a ``repeat()``, resolving the same arguments once against
the parent, each copy's operations carried through its own rest
placement. An ``Orbit``'s ``carries`` keeps its asymmetry: written at a
site it is a point of the parent's frame; defaulted it is still the
child's own origin, so the two defaults never collapse onto the line.

The two forms are told apart by the **value**, never by the keyword: a
coordinate the declaring class already owns is a wiring (below); a fresh
``Revolute(...)`` belonging to no class yet is a site declaration; one
declared on some third class is refused. A site joint is not a parameter
and never enters the child's identity. A site joint of a name the child's
class already declares replaces it whole and keeps its slot in the
composition order; a new name is appended after the class-declared
joints. The one cost: a site joint's operations are carried through the
inverse of the child's rest placement, so a body whose rest placement
carries a value the framework cannot evaluate numerically refuses a site
joint by name where a class-declared one would not.

Arguments
---------

Each of ``axis``, ``at``, ``range`` and ``carries`` may be a number, a
declared-parameter token, a formula over them, or, for the whole
argument, a callable of the realized declarer, called once at
realization; none enters the build identity. A ``repeat()`` copy's
``index`` does not exist yet when its joint arguments resolve, so derive
a per-copy joint argument from the parent's placement, or drive the
per-copy difference through a broadcast relation's ``law=``.

Range
-----

``range=(lo, hi)`` in ``unit``. Either bound may be ``None`` (unbounded
on that side), a one-argument callable over the joint's own coordinate,
or ``Bound(expression, reads=(...))``, a callable over that coordinate
and the coordinates it names:

.. code-block:: python

    turn = Revolute(axis=(1, 0, 0),
                    range=(lambda turn: 36 * floor(turn / 36), None))

That is a ten-tooth ratchet: the lower bound is the last seated tooth and
there is no upper bound. A bound that is not satisfied at its own
argument, ``lambda turn: turn + 1``, forbids every value and the first
binding says so by name.

What a range does depends on the execution model. Posed, a numeric
binding outside it raises ``JointRangeError`` naming the node's path, the
joint, the value, the range and the unit, and nothing clamps; a symbolic
binding is not checked, because its value is not yet known. Running, the
range is a **physical stop** that blocks the inputs pushing the
coordinate (:doc:`running`). Clocked, it clips a request's path before
any event is located (:doc:`clocked`). A ``Bound`` with reads is judged
when the enumeration closes over the values then bound, and is a
constraint along a running tick's path; it reads drivers, states and
joint coordinates, never a plain port or a derived coordinate, and never
the bounded coordinate itself.

.. _ancestor-joint-constraints:

Constraints from an ancestor
----------------------------

Two parts that must not meet often live in different nested assemblies:
a crank in the drive, a shaft in a bank of shafts. Neither can read the
other's coordinate, because a ``Bound`` reads only within the class that
declares the joint. Their common ancestor can, and it states the limit
in its own class body on the joint it names, without moving either part
or replacing its joint:

.. code-block:: python

    class Machine(AssemblyNode):
        time = Time.running()
        crank = Driver(default=0)
        drive = Drive()
        bank = ShaftBank()
        crank.drives(drive.disc.turn)

        drive.disc.turn.constrain(range=(None, Bound(
            lambda own, shaft: 120 + shaft, reads=(bank.ones.turn,))))

``constrain`` needs no import. It targets one explicitly named scalar
descendant joint: not a node, a port, a driver, a state, a ``repeat()``
broadcast or one coordinate of a ``Free``. The joint keeps its owner, its
axis and anchor, its place in the composition order, its geometry, its
coordinate id and its own ``range``. Each side of the added range is
``None``, a number, a parameter expression the ancestor owns, a callable
of the joint's own coordinate, or a ``Bound`` whose reads resolve in the
ancestor's subtree; the joint's own coordinate is always the first
argument, so it is not repeated in ``reads``. A whole-range callable and
``(None, None)`` are refused here, as are duplicate and unused reads.

Contributions **intersect**. The joint's own range and every constraint
on it, from any ancestor and through inheritance, are combined by the
largest lower and the smallest upper limit: adding ``(-10, 120)`` to a
joint declared ``(0, 90)`` still permits ``0`` to ``90``, and an empty
numeric intersection is refused. There is no spelling that removes or
replaces a contribution. A subclass inherits its base's constraints and
may add its own; a constraint whose target the subclass no longer has
fails by name rather than vanishing, and each instance of a class
resolves its own reads.

The result is an ordinary range on the existing coordinate, so each
execution model treats it as it treats any range. Posed, every
contribution is judged once the relations have settled, and a read that
is still unknown defers only its own contribution. Running, it is a
physical stop, judged along the tick's path where it reads a moving
coordinate (:doc:`running`). Clocked, it clips the request
(:doc:`clocked`). Nothing new is published: the effective limits are the
spans the document already carries, and changing them changes the
program's identity, so a snapshot taken under the old limits does not
restore under the new ones.

Composition
-----------

The joints of one class compose in **declaration order, innermost
first**, whatever order their coordinates are bound in:

.. code-block:: python

    class Chassis(AssemblyNode):
        roll  = Revolute(axis=(1, 0, 0), unit='deg')   # innermost
        pitch = Revolute(axis=(0, 1, 0), unit='deg')
        yaw   = Revolute(axis=(0, 0, 1), unit='deg')
        lift  = Prismatic(axis=(0, 0, 1), unit='mm')   # outermost

Base-class joints come before a subclass's, and a subclass redeclaring
an inherited joint keeps the position the base gave it. There is no
ordering keyword: reorder the declarations to restack. A joint's axis
and anchor are never carried through anything, neither the rest
placement nor a sibling joint's motion. Hand-written motion in
``simulate()`` composes outside the whole joint block, keeping its own
call order.

Passing a coordinate down
-------------------------

Several parts often turn as one body. Hand a child the parent's
coordinate by naming a port or joint the child declares:

.. code-block:: python

    class Arbor(AssemblyNode):
        turn = Revolute(axis=(0, 0, 1), unit='deg')

        wheel = Wheel(turn=turn)
        pinion = Pinion(turn=turn)

That keyword is a **wiring**, not a parameter: it says which value
reaches the child at each instant, never what geometry is built, so it is
absent from the child's parameters and identity. The framework rebinds it
from the parent's end after every ``simulate()`` of the parent, applying
the child end's scale. A wiring the child cannot receive fails at class
definition naming both classes; a wired coordinate has exactly one
binder, so binding the child's end by hand in the parent is refused. A
joint owning several coordinates cannot be wired whole.

Refusals
--------

Refused at realization, naming the class, the joint and the argument: an
undeclared token, a two-component or zero-length ``axis``, a reversed
``range``. Refused at class definition: a name that is both a joint and a
port on one class; a site keyword naming a port, a parameter or any
other attribute the child already answers to; two site joints of one
name; a site joint and a wiring naming the same coordinate. Assigning to
a ``Free`` as a whole is refused naming its six coordinates.
``declared_joints(cls)`` enumerates a class's joints, in composition
order, with no instance constructed.
