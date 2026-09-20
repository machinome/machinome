Values: parameters, constants, ports
====================================

Every value a node uses is one of three things.

.. list-table::
   :header-rows: 1

   * - layer
     - says
     - lives
     - example
   * - parameter
     - what is built
     - the declaration; propagates to children; enters build identity
     - ``bore = Length(30.0)``
   * - constant
     - where it sits
     - bare Python, read in ``render()``
     - ``BANK_HALF = 45.0``
   * - port
     - how it runs
     - the declaration; bound at runtime; never identity
     - ``crank = RotationalPort()``

The rule that separates the first two is the wrapper: **wrapped is a
parameter, bare is a constant**. A ``Length(...)`` propagates, enters the
build identity and can be set by a parent or from the command line. A
bare number in a module or class body is invisible to the framework,
because Python already provides constants. Placement arithmetic, lookup
tables and naming logic are constants and ordinary code in ``render()``.

Ports are the third layer: a unit-tagged value slot a node declares and
its parent binds on every ``simulate()``, by ``connect()`` or by
assignment, with the sink's scale applied. A driver is an input to the
machine; a port is a connection point between parts. A joint's
coordinate is a port the joint owns (:doc:`joints`).

Two further class-body declarations are none of the three: the root's
time base, ``time = Time(loop=...)``, ``Time.running()`` or
``Time.elapsed()``, which says what ``self.time`` means
(:doc:`execution-models`), and a rigid part's marking, which says what
the part carries on its surface and adds no solid
(:doc:`/howto/markings`).

Where names come from
---------------------

Every kind, the ``Quantity`` base below and the errors a bad declaration
raises come from ``machinome.parameters``, and nothing else does. Node
classes come from ``machinome.node``; ports and the declared time base
from ``machinome.motion.ports``; joints from ``machinome.motion.joints``;
drivers, states, instructions and the simulation from
``machinome.simulation``. A module's import block therefore says which of
its names build the machine, which move it, and which drive it:

.. code-block:: python

    from machinome.node import AssemblyNode, CadQueryNode
    from machinome.parameters import Count, Flag, Length
    from machinome.motion.ports import RotationalPort, Time
    from machinome.motion.joints import Revolute
    from machinome.simulation import Driver, State

Kinds
-----

``Length``
    A linear dimension in millimetres. Signed by default, since a
    station can sit at ``-5.2``; ``min=0`` opts into non-negativity.

``Angle``
    In degrees. Its own quasi-dimension: this is what refuses
    ``phase + rotor_fraction`` and lets trigonometry demand an angle.

``Count``
    A whole number of things: teeth, cylinders, sides. Resolves to an
    ``int`` and refuses ``2.5``.

``Ratio``
    A dimensionless fraction, and what a length over a length is.

``Flag``
    A boolean selector. Outside the algebra; it gates structure through
    ``omit()``.

``Scalar``
    The escape hatch: a number the algebra does not check.

Every kind takes an optional default and, for the numeric ones, ``min=``
and ``max=``. Constraints are checked when the node is constructed, and a
violation raises naming the class, the parameter and the rule. A value is
coerced to its kind, so ``Piston(diameter=30)`` and
``Piston(diameter=30.0)`` are one part. On an instance a declared
parameter reads as a plain number; on the class it is the symbolic token.
Assigning to one on an instance raises; pass the value to the
constructor. A declaration may omit its default; the parent must then
supply the value, and loading such a node directly needs ``--set``.

A declared name may not shadow an attribute a base class carries
(``name``, ``time``, ``mesh``, ``children``, ``color``, a sheet part's
``thickness``); class definition raises. A declarative class rejects
positional arguments and unknown keywords with a ``TypeError`` listing
the declared names: declaration order is a reading order, not a call
signature.

Declared beside the constructor form
------------------------------------

.. code-block:: python

    class Piston(CadQueryNode):             # declared

        diameter     = Length(29.4, min=0)
        crown_height = Length(18.0, min=0)
        skirt_depth  = Length(12.0, min=0)

        total_height = crown_height + skirt_depth

        def render(self):
            return (cq.Workplane("XY")
                    .circle(self.diameter / 2)
                    .extrude(self.total_height))

    class Shaft(CadQueryNode):              # constructor form, still supported

        def __init__(self, diameter=4.8, length=30.0, name=None):
            self.diameter = diameter
            self.length = length
            super().__init__(diameter=diameter, length=length, name=name)

Compared with the constructor form, three things are gone: the
``__init__`` signature, the ``self.x = x`` lines, and the
``super().__init__(x=x, ...)`` call. The last one mattered most: the
build identity of a constructor-form node is hashed over what reaches
``super().__init__()``, so forgetting one keyword silently gave two
different parts one cached artifact. With declarations the framework
owns the identity, complete by construction. Nothing forces a migration;
a class that declares nothing keeps the constructor form, and the two mix
in one tree. A migrated class that forwarded every keyword with float
defaults keeps its identity; one that forgot a keyword, or passed an
integer where a float kind now resolves, re-keys once.

Formulas and the algebra
------------------------

A declared parameter is a symbolic token, and a formula over tokens is a
**derived parameter**, a bare class-body expression:

.. code-block:: python

    class CylinderUnit(AssemblyNode):

        bore           = Length(30.0, min=0)
        wall_clearance = Length(0.3,  min=0)

        piston_diameter = bore - 2 * wall_clearance

        piston = Piston(diameter=piston_diameter)

Read on the instance it is the evaluated value; it cannot be supplied by
a parent, by ``--set`` or by assignment. Every quantity carries a vector
of dimension exponents: products add them, quotients subtract them, and
addition, subtraction and negation need them equal. ``teeth * module`` is
a length; ``bore / stroke`` is dimensionless; ``bore * bore`` is a length
squared, valid whether or not a kind is named for it; ``bore +
pressure_angle`` raises a ``DimensionError`` on ``import``, before any
geometry exists.

The functions of ``machinome.math`` take part. ``sqrt`` needs even
exponents and halves them; ``sin``, ``cos``, ``tan`` need an ``Angle``
and return a dimensionless quantity; ``asin``, ``acos``, ``atan``,
``atan2`` take dimensionless arguments and return an ``Angle``. ``abs``
keeps its argument's kind; ``min`` and ``max`` need their arguments to
agree; ``sign`` gives a dimensionless -1, 0 or 1. ``floor`` and ``ceil``
want a dimensionless argument: they compare a quantity against the whole
numbers, and a whole number has no dimension, so ``floor(bore)`` would
only mean something if millimetres were assumed, which is exactly what
this algebra will not do. Say what you are counting in:

.. code-block:: python

    steps = floor(travel / pitch)      # a dimensionless count
    landed = steps * pitch             # back to a length

The compositions (``clamp``, ``clamp01``, ``ramp``, ``lerp``, ``wrap``,
``piecewise``, ``bump``) carry no rule of their own; what they do to
dimensions falls out of the primitives they compose. One consequence
catches people once: a bound stated as a bare number against a
dimensioned quantity is refused, ``clamp01(bore)`` and ``max(bore, 0.0)``
alike; write ``max(bore, Length(0.0))``. ``wrap`` has the same catch in
its default period of ``360.0``: in a declaration, state
``wrap(bearing, Angle(360.0))``.

The algebra catches dimensional mistakes, a wrong formula shape, a
forgotten factor, mixed kinds, not geometric ones. ``Count`` and
``Ratio`` are both dimensionless, so ``teeth + fraction`` passes.
Comparisons are refused in a declaration; they belong in ``render()`` or
``check()``, on resolved values. A project that needs a kind the
framework does not name subclasses ``Quantity`` with its own exponents
(``class Torque(Quantity): dimension = {'M': 1, 'L': 2, 'T': -2}``), and
``.value`` on any token or formula yields the unchecked form when the
algebra gets in the way.

Declaring children
------------------

A node constructed in a class body is a **declaration**, never an
instance. A class attribute would be one object shared by every parent
instance, eight cylinder units driving one piston, so the framework
records the class and its arguments, and each parent instance realizes
its own child when it is constructed. Tokens passed to a child are passed
by reference and resolved top-down from the root: ``Engine()`` realizes
with defaults, ``Engine(bore=32.0)`` rebinds the root and every derived
value and child follows. A ``Flag`` passes down the same way.

Siblings do not reach into each other for a value:
``ConRod(pin_bore=piston.pin_bore)`` in a class body raises, with the
advice to declare ``pin_bore`` on the parent. They do name each other's
places: reading a port, a joint or another child off a declaration yields
a **path**, ``anchor.turn``, ``shoulder.art2.art3.wrist``, checked
against the classes as you write it, which is what a relation between
two coordinates is written over (:doc:`relations`).

A child's class need not itself be declarative. A legacy class with an
ordinary ``__init__`` is realized by calling it with the resolved
arguments. ``declared_parameters(cls)`` and ``declared_children(cls)``
enumerate a class's declarations without constructing anything.

Guards
------

``min=`` and ``max=`` bound one value. A rule between two is ``check()``:

.. code-block:: python

    class Valve(CadQueryNode):

        stem_diameter = Length(4.0, min=0)
        stop_diameter = Length(6.0, min=0)

        def check(self):
            if self.stop_diameter <= self.stem_diameter:
                raise ValueError(
                    f'{self.name}: stop {self.stop_diameter} must exceed '
                    f'stem {self.stem_diameter}')

The framework calls ``check()`` on a declarative node as soon as its
parameters are resolved, before any child is realized, so a refused root
builds nothing. Whatever it raises propagates unchanged; ``ValueError``
is the convention. The base ``check()`` does nothing, so a subclass
chains ``super().check()``. A class that declares nothing is not called.
