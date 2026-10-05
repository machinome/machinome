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

Frames and mates
----------------

In the example above one physical pin is stated twice: the arm's
``render()`` places the forearm with arithmetic, and the forearm's class
states the elbow line again, and the two agree only because the numbers
were worked out together. An assembly CAD design states it once: a
connector on each part, and how the two meet. So can a machine.

A **frame** is a connector a part declares on itself, in its own rest
frame: an origin ``at`` and a right-handed triad whose ``z`` is, by
default, the line a revolute mate turns about. A **mate** is one
sentence in the assembly that holds both parts, written from the frame
that moves:

.. code-block:: python

    from machinome.motion.joints import Revolute
    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from machinome.parameters import Length
    from solid2 import cube

    class Forearm(Solid2Node):
        hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))

        def render(self):
            return cube([20, 20, 160])

    class UpperArm(AssemblyNode):
        reach = Length(160)
        elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))

        forearm = Forearm()

        elbow = forearm.hinge.on(elbow_pin,
                                 Revolute(range=(-135, 135), unit='deg'))

There is no ``render()`` and no joint on ``Forearm``. The mate compiles,
when the arm is built, to three things this page already describes (a
mate that holds a part rather than freeing it compiles to the first
alone, as the end of this section shows):

- the forearm's **rest placement**, the rotation and translation that
  put ``hinge`` onto ``elbow_pin``, origin on origin and ``x``, ``y``,
  ``z`` onto ``x``, ``y``, ``z``: here ``rotate(90, [1, 0, 0])`` then
  ``translate`` to ``(0, 241.5, 68)``, applied after ``render()``, exactly
  as if written there;
- a **joint on the forearm**, a ``Revolute`` about the moving frame's
  ``z`` through its ``at`` unless the freedom states its own line (see
  below), in the forearm's own frame, carrying the
  freedom's range and unit. It is a joint of the forearm's class like any
  other, placed after the joints the class declares itself, and the
  forearm keeps its name and its build identity;
- a **coordinate on the arm** under the mate's name. ``arm.elbow`` reads
  and binds as a joint's coordinate does, ``declared_ports`` reports it,
  and a relation, a driver or a derived coordinate names it as any other
  end (``elbow.drives(belt.travel, ratio=...)`` in the arm's body,
  ``angle.drives(arm.elbow)`` from above). The forearm's joint is bound
  through it and through nothing else: binding ``arm.forearm.elbow`` by
  hand or by a relation is refused, naming ``arm.elbow``. Left unbound,
  the forearm rests at the mate's rest placement.

``x`` matters. It fixes the attitude about ``z``, and so the zero of the
mate's coordinate: with the forearm's ``x`` left out the two lines still
meet, but the forearm rests turned 120 degrees about ``(1, 1, 1)``. Left
out, ``x`` is the next principal axis after a principal ``z`` (``+X`` for
``+Z``, ``+Y`` for ``+X``, ``+Z`` for ``+Y``, negated for a negated
``z``); a ``z`` along no principal axis must state its ``x``.

A connector need not be a joint frame. An assembly CAD design's
connectors say where one part is attached to another, and their ``z``
often stands across the line the part turns about, or points down it
the other way. The freedom may then state that line itself, in the
moving part's own frame, the frame a joint its class declared would be
written in. Here is a robot arm's shoulder whose connector's ``z`` lies
across the joint line, the line being the link's own ``z``:

.. code-block:: python

    from machinome.motion.joints import Revolute
    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from solid2 import cube

    class Link(Solid2Node):
        bore = Frame(at=(0, 0, 68), z=(0, 1, 0), x=(-1, 0, 0))

        def render(self):
            return cube([30, 30, 200])

    class Shoulder(AssemblyNode):
        shoulder_pin = Frame(at=(0, 0, 123))

        link = Link()

        shoulder = link.bore.on(
            shoulder_pin,
            Revolute(axis=(0, 0, 1), at=(0, 0, 0), range=(-90, 90),
                     unit='deg'))

The frames still place the link, connector onto connector: it rests
turned 180 degrees about ``(0, 0.7071, 0.7071)`` and translated to
``(0, -68, 123)``, and that rest is the zero of ``shoulder``. The
freedom fixes only the line the link turns about from there: the link's
own ``z`` through the link's own origin. ``axis`` and ``at`` are each
optional, and each one left out is the moving frame's, so a freedom may
state the axis alone, the anchor alone, both or neither. ``at=(0, 0, 0)``
written is the moving part's origin, not the frame's: left out, the
anchor here would be ``(0, 0, 68)``, a point on the same line, turning
the link the same way. Nothing checks a stated line against the frames;
an anchor is any point on its line. A stated line holds no parameter or
formula, because it is written in the assembly and read in the moving
part's frame, where a parameter would resolve against the wrong node.
Its ``axis`` may instead be one function of the assembly, as the end of
this section shows; its ``at`` is three numbers.

A frame's arguments follow the joint rule below, resolve to numbers when
the part is built, and are neither identity nor geometry: adding one
changes no artifact. A frame may be declared on any node, an assembly
included, since an assembly's frames are its connectors to the one
above it. ``declared_frames(cls)`` and ``declared_mates(cls)`` enumerate
them off the class.

The **fixed end** is a frame of the assembly itself, written by its bare
name, or ``<child>.<frame>`` of another child the assembly declares,
which then must not move and must not be placed by another mate: the
mated part rests against that child's rest placement, and siblings do
not carry each other. The **moving end** is a frame of a child the
assembly declares directly. The **freedom** is a ``Revolute``, the one
place a ``Revolute`` may leave out its axis, or a ``Prismatic``, which
states its axis here as it does anywhere, or it is left out for a part
that is held (see the end of this section). A stated ``axis`` is three numbers or one function
of the assembly, a stated ``at`` three numbers, and the range a pair of
numbers, ``None``, functions of the coordinate's own value, or
``Bound(expression, reads=(...))``, or one function of the assembly
returning such a pair. A Bound's reads resolve in the **declaring assembly**;
its first argument is the generated child joint's own coordinate. Axis and
anchor still belong to the moving child's rest frame. Reads are evaluated
once the whole tree exists, so a later sibling can supply one. A whole-range
function keeps its once-per-instance timing, including when it returns Bounds.

For example, with ``Handle`` declaring ``origin = Frame()`` and ``Pawl``
declaring a revolute ``turn``, an assembly can state a stop beside its mate
(the part classes and their geometry are omitted):

.. code-block:: python

    class Drive(AssemblyNode):
        pin = Frame()
        handle = Handle()
        pawl = Pawl()
        travel = handle.origin.on(pin, Revolute(range=(0, Bound(
            lambda own, pawl: 90 + pawl, reads=(pawl.turn,)))))
        travel.constrain(range=(None, 100))

``travel`` also names the generated child joint when used as a Bound read,
an added constraint target or an explicit control selection. An ancestor
can use ``drive.travel`` for those same contracts. The physical coordinate
is still ``drive.handle.travel``; neither spelling adds another bank value.
The mate's ordinary relation and binding address remains ``drive.travel``.

When the child already has a joint, name that joint instead of declaring
a fresh freedom. The frames place it at rest without replacing the joint:

.. code-block:: python

    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from machinome.motion.joints import Revolute
    from solid2 import cube

    class Dial(Solid2Node):
        axle = Frame()
        turn = Revolute(axis=(0, 0, 1))

        def render(self):
            return cube(1)

    class Register(AssemblyNode):
        ones_seat = Frame(at=(10, 0, 0))
        ones = Dial()
        ones_mount = ones.axle.on(ones_seat, ones.turn)

        def simulate(self):
            if self.ones.turn.value is None:
                self.ones.turn = 36

``register.ones_mount`` reads exactly ``register.ones.turn`` and either
spelling binds that same coordinate. The handle adds no coordinate to the
assembly: its canonical coordinate id remains ``ones.turn``. Relations,
derived formulas, wiring sources, Bounds, added constraints and explicit
controls may use the handle, but ownership and sole-binding rules still
apply. The joint keeps its original name, order, geometric frame, limits,
factory receivers and binding rules. A class-declared joint still reads
the child; a site-declared joint still reads the parent. Its guarded
``simulate()`` default therefore needs no rewrite.

This form requires an explicit scalar ``Revolute`` or ``Prismatic`` of
the same directly declared moving child, such as ``ones.turn``. A string,
a bare joint declaration, a whole node, a deeper or foreign path, a port,
an ``Orbit`` or a ``Free`` is not an existing-joint freedom. The handle
can have the same name as that child's joint without replacing it.

Refused when the class is created, naming the mate: a mate on a node
that is not an assembly; a moving end that is the assembly's own frame;
either end reached through more than one child, a list or a
``repeat()``; a fixed end on a child that can move or that another mate
places; a second mate on one child; a mate never assigned to a name; a
freedom that is neither a fresh ``Revolute`` nor a fresh ``Prismatic``
nor the explicit existing-joint reference described above,
or, for a fresh freedom, a stated ``axis`` that is neither three numbers nor a function, or
whose stated ``at`` is not three numbers, a function ``at`` included,
or whose stated ``axis`` has no length, or whose range holds a parameter;
a mate with a fresh freedom whose name the moving
child already answers to; and a mate with no freedom named where a
coordinate is named. Refused when the arm is built: a freedom's
function that raises, or returns what the same argument written in
numbers would refuse, naming the assembly, the mate and the argument.
Refused when the arm renders: a ``render()`` that also places a mated
child. A mate publishes nothing new: the document carries its rest
placement as operations and its coordinate, if it has one, as a
binding, at the version the same machine without mates declares.

A test that holds a machine's connectors to a design reads them back
rather than restating them. ``resolved_frames(node)``, from
``machinome.node.frames``, gives a built node's frames as numbers, by
name, in the order the class declares them; ``declared_mates(cls)``
gives each mate, off the class. With the arm above:

.. code-block:: python

    from machinome.motion.mates import declared_mates
    from machinome.node.frames import resolved_frames

    arm = UpperArm(reach=150)

    pin = resolved_frames(arm)['elbow_pin']
    pin.at                      # (0.0, 150.0, 68.0)

    hinge = resolved_frames(arm.forearm)['hinge']
    hinge.x, hinge.y, hinge.z   # (1, 0, 0), (0, 0, -1), (0, 1, 0)

    elbow = declared_mates(UpperArm)['elbow']
    elbow.moving.written        # 'forearm.hinge'
    elbow.fixed.name            # 'elbow_pin'
    elbow.freedom.range         # (-135, 135)
    elbow.freedom.anchor_written  # False

The read takes a built node, not a class, because a frame's arguments
may read the node's parameters, as ``elbow_pin`` reads ``reach``: the
class holds the declaration, and ``declared_frames(UpperArm)`` reports
it as written, while ``UpperArm(reach=150)`` resolves it to
``(0.0, 150.0, 68.0)``. Given a class, a child read off a class body, or
a node whose frames have not resolved yet (from its own ``check()``),
the read raises ``TypeError``; reading ``arm.elbow_pin`` still gives the
declaration. Each resolved frame has ``at`` in floats, unit ``x``, ``y`` and
``z``, and ``rotation()``, the 3×3 whose columns are those directions.
Supplying both directions explicitly retains full floating-point precision:
``z`` is normalized, ``x`` projected across it and normalized, and ``y`` is
their cross product, without component snap. Even an explicit default
``z=(0, 0, 1)`` counts: ``Frame(z=(0, 0, 1), x=...)`` retains precision,
whereas ``Frame(x=...)`` with ``z`` omitted keeps the old snapped path.
Omitted ``x`` or ``x=None`` also keeps that path: components within ``1e-9``
of ``0``, ``1`` or ``-1`` become those integers, with the same principal
inference and zero/parallel refusals. These are the same cached numbers the
mate composes, not a separately altered readout; read them, do not assign.
Final mate angle/axis snap and Joint axis snapping remain unchanged.

A mate's ``name`` is its coordinate's, when it states a freedom. Its ``moving`` end reads
``written`` as ``'<child>.<frame>'``; its ``fixed`` end is either such a
reference, for a frame of another child, or, for a frame of the assembly
written by its bare name, that ``Frame``, read by its ``name``. Its
``freedom`` is the ``Revolute`` or ``Prismatic`` as written, or ``None`` for a mate that holds a part: ``axis`` is
``None`` unless stated, ``range`` and ``unit`` as written, and an
``axis`` or ``range`` stated as a function reads as that function,
without calling it. ``at`` is the mate's anchor only when
``anchor_written`` is true; left out, it reads ``(0, 0, 0)``, and the
anchor is the moving frame's origin. So the line a mate turns its child
about, or slides it along, is ``freedom.axis``, else the moving frame's
resolved ``z``, through ``freedom.at`` when written, else through the
moving frame's resolved ``at``. What a function returned for a built
machine is not one of these reads.

A handed design mounts one part mirrored on each side, and the sides
may differ in more than where the part sits: the line it turns about,
and how far it turns. A frame may already be a function of the node
that declares it. A freedom's ``axis`` and ``range`` may each be one
function too, of the assembly that states the mate:

.. code-block:: python

    from machinome.motion.joints import Revolute
    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from machinome.parameters import Flag
    from solid2 import cube

    class Link(Solid2Node):
        origin = Frame()

        def render(self):
            return cube([20, 20, 100])

    class Mount(AssemblyNode):
        left = Flag(False)
        pin = Frame(at=lambda node: (0, 62.5 if node.left else -62.5, 0))

        link = Link()

        turn = link.origin.on(pin, Revolute(
            axis=lambda node: (0, 1, 0) if node.left else (0, -1, 0),
            range=lambda node: (-200, 80) if node.left else (-80, 200),
            unit='deg'))

    left, right = Mount(left=True), Mount(left=False)

Every ``node`` here is the mount. A freedom's function is called with
the assembly that states the mate, the node whose class body it is
written in, as the frame's function is, and never with the moving part,
which here has no ``left`` at all. It is called once, when the assembly
builds the moving part: the assembly's own parameters, frames and
joints are resolved by then, and every child it declares before the
moving part is built, but nothing is rendered yet. What it returns is
taken as the same argument written in numbers is: an ``axis`` of three
numbers with a direction, read in the moving part's own frame, and a
``range`` pair of the kinds above. The left link rests at
``(0, 62.5, 0)`` and turns about ``(0, 1, 0)`` within ``(-200, 80)``;
the right one rests at ``(0, -62.5, 0)`` and turns about ``(0, -1, 0)``
within ``(-80, 200)``. A stated ``at`` stays three numbers.

A gripper's fingers do not turn: each slides along a line of its own,
and a two-finger gripper moves them equally and oppositely. The freedom
may be a ``Prismatic``:

.. code-block:: python

    from machinome.motion.joints import Prismatic
    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from solid2 import cube

    class Finger(Solid2Node):
        origin = Frame()

        def render(self):
            return cube([4, 2, 6], center=True)

    class Palm(AssemblyNode):
        left_seat = Frame(at=(81.7, 21, 0))
        right_seat = Frame(at=(81.7, -21, 0))

        left_finger = Finger()
        right_finger = Finger()

        left_grip = left_finger.origin.on(
            left_seat, Prismatic(axis=(0, 1, 0), range=(-11, 20), unit='mm'))
        right_grip = right_finger.origin.on(
            right_seat, Prismatic(axis=(0, -1, 0), range=(-11, 20), unit='mm'))

        left_grip.drives(right_grip)

The part then slides along the line instead of turning about it, by the
same rules: the frames fix where it rests, and so the zero of its
coordinate; ``at`` and ``range`` are taken as a ``Revolute`` freedom's;
an ``axis`` or a ``range`` may be one function of the assembly. A
``Prismatic`` always states its ``axis``, here as anywhere: only a
``Revolute`` freedom may leave its axis to the moving frame. A stated
``at`` moves nothing on a slide, since a translation along a line is the
same wherever the line is taken to pass; it is carried as the joint's
anchor. The mate gives the finger a ``Prismatic`` joint, and the
coordinate on the palm is a length, in ``'mm'`` unless the freedom
states a unit. The two coordinates are related like any others, so
binding ``palm.left_grip = 10`` moves the left finger 10 along
``(0, 1, 0)`` and the right one 10 along ``(0, -1, 0)``, each from its
seat.

A servo, a bearing or a screw does not move of its own: it is held,
bolted, pressed or seated where the part that holds it says. A mate may
leave its freedom out for a part that is held:

.. code-block:: python

    from machinome.node.assembly import AssemblyNode
    from machinome.node.solid2 import Solid2Node
    from machinome.node.frames import Frame
    from solid2 import cube

    class Servo(Solid2Node):
        ears = Frame(at=(0, -5.5, 0))

        def render(self):
            return cube([12, 23, 22], center=True)

    class Shin(AssemblyNode):
        servo_seat = Frame(at=(-0.98, -4, -7), z=(1, 0, 0), x=(0, 0, 1))

        servo = Servo()

        bolted = servo.ears.on(servo_seat)

The mate places the servo, connector onto connector, as a mate with a
freedom does: it rests turned 180 degrees about ``(0.7071, 0, 0.7071)``
and translated to ``(-0.98, -9.5, -7)``, its ears on the seat. It gives
the servo nothing else, no joint and no coordinate: the servo is a
``Servo`` itself, ``declared_ports(Shin)`` is empty, and ``shin.bolted``
reads the mate, whose ``freedom`` is ``None``; assigning to it, or
naming it as a relation's end, a term, a wiring or a path, is refused.
The part moves only as the assembly that declares it moves, so a held
part is declared in the class of the part that holds it: the servo in
the shin that carries it, and its screws beside it in an assembly of
servo and screws, each screw held on one of the servo's ears. The fixed
end still does not move, and the held
part may declare joints, children and mates of its own, all inside the
placement. The mate is named like any other. Its operations may take
another form than a hand placement's with the same placement: one
rotation where a hand writes two, ``rotate(90, [0, 1, 0])`` then
``rotate(180, [1, 0, 0])``.

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
descendant joint, or a moving mate, bare in its declaring assembly or by
path from an ancestor. A mate target installs the contribution on its
generated child joint. A rigid mate owns no coordinate and is refused, as
are a node, a port, a driver, a state, a ``repeat()``
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
order, with no instance constructed. A ``Revolute`` written without an
axis is refused anywhere but as a mate's freedom.
