Repeat a unit and vary a design
===============================

An engine has eight identical cylinder units at different stations. A
windmill may or may not be fitted with its guard. A rack holds a left
panel and a right panel that are not the same part. Each of these is
structure, and structure is declared.

Identical units
---------------

``repeat(count)`` declares ``count`` identical children: one geometry, one
build identity, one cached artifact, ``count`` placements. A quantity line
on a bill of materials.

.. code-block:: python

    from machinome.node import AssemblyNode
    from machinome.parameters import Count, Length

    STATION_PITCH = 44.0
    BANK_HALF = 45.0
    ROD_OFFSET = 5.2

    class Cylinders(AssemblyNode):

        count = Count(8, min=2)
        bore = Length(30.0, min=0)

        units = CylinderUnit(bore=bore).repeat(count)

        def render(self):
            for index, unit in enumerate(self.units):
                pin = index // 2
                side = 1 if index % 2 == 0 else -1
                unit.rotate(side * BANK_HALF, [1, 0, 0])
                unit.translate([STATION_PITCH * pin - side * ROD_OFFSET, 0, 0])

Per-unit variation never lives in the declaration. Placement variation is
``enumerate`` plus constants in ``render()``. Drive variation is either
uniform port feeding in ``simulate()`` (``unit.crank = angle + phase``) or
a **broadcast relation**: one relation whose driven end reaches through
the repeat, with a per-copy ``law=`` that reads the copy's own ``index``
(:doc:`/concepts/relations`). Children that differ geometrically are
different parts.

Every copy carries its 0-based position as ``index``, a plain attribute
that never enters the part's identity. A driver declared on a repeated
child cannot be qualified, because ``units-3`` is not an identifier;
drive identical units through ports.

Different units
---------------

Enumerated, different children are a plain literal list, named
``<attr>-0``, ``<attr>-1``, and so on:

.. code-block:: python

    plates = [PanelLeft(width=frame_width), PanelRight(width=frame_width)]

A list comprehension in a class body cannot see class-level names, so
``[Unit(bore=bore) for _ in range(8)]`` raises ``NameError`` for
``bore``; that is Python's scoping, and identical units are ``repeat``. A
comprehension over what it can see does declare: ``[Clip(kind=k) for k in
KINDS]`` over a module-level table is an enumerated list like a literal
one. Indices are identity and never renumber: an omitted ``units-3``
leaves ``units-4`` as ``units-4``.

Optional structure
------------------

A ``Flag`` is a boolean parameter, and ``omit()`` in ``render()`` removes
a declared child from the machine for that realization:

.. code-block:: python

    from machinome.parameters import Flag, Length, Ratio

    class Windmill(AssemblyNode):

        overall_height = Length(400.0, min=0)
        rotor_fraction = Ratio(0.36, min=0, max=1)
        guard_installed = Flag(True)

        rotor_radius = overall_height * rotor_fraction

        tower = TowerBody(height=overall_height)
        rotor = Rotor(radius=rotor_radius)
        guard = Guard()

        def render(self):
            if not self.guard_installed:
                self.guard.omit()

An omitted part is structurally absent: different mass, different bill
of materials, absent from exports and from a fused solid, never built.
That is not the same as hiding a part in the viewer. Every child is
always declared, so the tree's vocabulary is complete at import time, and
``render()`` selects presence.

**Structure varies with parameters, never with time.** A machine does
not gain and lose parts per frame, and the children a fusion holds are
its build identity. Decide ``omit()`` from declared parameters only, in
``render()``: calling it from ``simulate()`` raises.

Vary from the shell
-------------------

Because the root's parameters are declared, every command that loads a
node can set them:

.. code-block:: bash

    $ machinome build engine.py --set bore=32.0 --set count=6
    $ machinome develop windmill.py --set guard_installed=false
    $ machinome develop tower.py --set height=300

A value is parsed by the parameter's kind, a float for ``Length``,
``Angle``, ``Ratio`` and ``Scalar``, an integer for ``Count``, ``true``
or ``false`` for ``Flag``, and checked by its constraints. An unknown name
fails listing the settable parameters; a derived parameter cannot be set;
a root that declares nothing refuses the flag. A parameter declared
without a default (``height = Length(min=0)``) has no sensible value of
its own, so the parent supplies it, and loading such a node directly
needs ``--set``. A develop session reapplies overrides on every rebuild.

Artifacts for different parameter sets coexist in the build directory,
keyed by their values, so switching back is a cache hit, and a child
whose parameters do not depend on the changed value is not rebuilt.
