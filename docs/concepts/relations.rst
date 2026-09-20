Relations
=========

A joint says where a body may move; a **relation** says that one
coordinate's motion *is* another's. It is written as a statement in a
class body, over declarations, and the verb needs no import:

.. code-block:: python

    class Movement(AssemblyNode):
        power  = TrainArbor(index=0)
        centre = TrainArbor(index=1)
        escape = TrainArbor(index=2)

        power.drives(centre, law=going_train)
        centre.drives(escape, law=going_train)

Either end may be a port, a joint, a child declaration (standing for its
class's one joint; a class with none or several is refused where the
relation is written, with the advice to name the coordinate), a path
through declared children, a derived coordinate, or, as the source only,
a ``Driver`` or a ``State``. A path is checked against the classes where
it is written, so a misspelt segment is a class-definition error.
Nothing may drive a ``Driver``: its value belongs to the instant.

Direction is mechanical; solving is not
---------------------------------------

``a.drives(b)`` says what turns what. Which way the framework *solves* it
is decided on every run, from whichever end is bound at that instant:
forward through the law when the driver end is bound, backward through
its inverse when the driven one is. The train above is written
power-first and solved escape-first when ``simulate()`` binds the
escapement, with nothing reordered.

Every relation of a class is attempted at the end of that instance's
simulate phase, parents before children. What one instance's own attempt
cannot yet reach is **deferred**, not refused: it is held until every
assembly in the tree has had its phase, and only then resolved or
refused. That is what lets a chain be stated inside the class that owns
it, a going train inside ``Train``, with only the escapement bound two
levels up in ``Movement``. An ancestor may source from a coordinate a
descendant's relations solve, and reads fresh on every re-pose.

A subclass may replace a base's **named** relation, keeping the base's
position in the solve:

.. code-block:: python

    class Actuator(AssemblyNode):
        drive = input_angle.drives(rotor.spin, ratio=8.0)

    class Preview(Actuator):
        drive = free_run.drives(Actuator.rotor.spin, ratio=1.0)

A relation with no name, or a name no base used, stays additive.

Laws
----

``ratio=`` and ``offset=`` are the shorthand for ``Affine(ratio,
offset)``, ``driven = ratio * driver + offset``, from
``machinome.motion.couplings``. Both faces are ordinary arithmetic, so a
symbolic read produces an expression and a number a number, and it
inverts itself.

Anything else is a ``law=`` callable of your own, called exactly once per
relation at realization, with the two realized nodes that own the
coordinates, driver first, and returning the law:

.. code-block:: python

    def going_train(driver, driven):
        return Affine(ratio=-driver.wheel_teeth / driven.pinion_teeth,
                      offset=registration(driver, driven))

Because it is handed the realized nodes, it reads whatever they have: a
built library object, a resolved parameter, a copy's ``index``. The
framework looks nothing up; there is no registry of mechanism shapes and
no vocabulary of gears. A returned object needs a ``forward(x)``, and an
``inverse(y)`` if the relation may ever be read backwards; a plain
function is forward-only. ``ratio=`` or ``offset=`` together with
``law=`` is refused.

A law's arithmetic is ``machinome.math``'s: it must apply to a symbolic
value, because the same law is published to the browser, and it may not
branch on its arguments in Python. For gear, screw, slider-crank, delta
and linkage formulas, reuse `Machinome Mechanics
<https://machinome-mechanics.readthedocs.io/en/latest/reference/index.html>`_
inside your law; its manual owns the helpers' frames, signs and domains.

Several coordinates at an end
-----------------------------

A source group is written with ``&``, chaining flat; a driven group is a
tuple or ``&``:

.. code-block:: python

    (count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)
    (x & y & z).drives((rod.spin, rod.lean, rod.swing, rod.rise), law=delta_rod)

    def pawl_deflection(sources, driven):
        def law(count, next_count):
            ...
        return law

The law's two arguments are shaped by the sentence: a side naming one
coordinate hands its owner, a side naming several hands the tuple of
owners in written order, so a six-source law still takes two arguments.
``forward`` is called with one positional argument per source, in written
order, and returns one value for one driven end or a sequence of exactly
as many values for several; a wrong-shaped return is refused by name
where it is applied. A group names at least two coordinates, none twice,
none on both sides of one relation.

A relation naming several coordinates at either end is read **forward
only**, whatever its law offers: recovering several sources from several
driven values means comparing or solving values, which the framework does
not do. ``ratio=``, ``offset=`` and the bare default are refused with a
group. Guidance: if the combination is linear, write a derived coordinate
and keep both directions; if it is not, write a multi-source law and
accept losing the reverse.

Derived coordinates
-------------------

A linear formula over coordinates is itself a coordinate of the class:

.. code-block:: python

    class Art2(AssemblyNode):
        shoulder = Revolute(axis=(0, 0, 1), unit='deg')
        art3 = Art3()

        relative_elbow = art3.elbow - shoulder
        relative_elbow.drives(elbow_pulley.turn)

``+``, ``-``, unary ``-`` and scaling by a number or a declared parameter
are all it does; a product of two coordinates, or any other function of
one, is refused where it is written and pointed at ``law=``. It reads on
an instance as a bound port slot, is reported by ``declared_ports``, takes
its domain and unit from its terms, and solves in both directions: from
its terms when they are all bound, and for its one remaining term when it
is bound itself.

Broadcasts over a repeated child
--------------------------------

A relation whose driven end reaches through a ``repeat()`` is a
**broadcast**: one relation, written once, resolving to one per realized
copy, with ``law=`` called once per copy and the copy as its second
argument, so a per-copy sign, phase or rank reads ``bead.index``:

.. code-block:: python

    earth.drives(earth_beads.travel, law=earth_lift)

    def earth_lift(column, bead):
        rank = bead.index
        return lambda level: clamp(level, rank) * column.stroke

``ratio=`` and ``offset=`` resolve once against the declaring instance
and every copy shares that one ``Affine``. A repeated end is a driven end
only: as a source it is refused at class definition, because a source is
one value and the copies hold one each. A driven group that fans out over
a repeat resolves to one record per copy.

Refusals
--------

Solving refuses by name rather than posing a machine it cannot justify.
Each is its own error kind in ``machinome.motion.couplings``, naming the
node paths, the relation as written and the ends:

``UnreachedCoordinate``
    nothing bound either end of a relation, and nothing reached it; or a
    derived coordinate is bound while two of its terms are not.

``DoublyBound``
    something else already bound the coordinate this relation would bind:
    your own ``simulate()``, a wiring, or another relation. Two relations
    that would give the *same* value are refused too: the framework
    cannot compare two symbolic expressions to decide whether they agree,
    and a silent first-writer-wins would hide a real modelling mistake.
    This one is never deferred; a contradiction is not a question of
    timing.

``NotInvertible``
    the driven end is the bound one, so the law has to be read backwards,
    and it offers no inverse, or the relation is a broadcast or names
    several coordinates at an end.

``PrematureRead``
    your own ``simulate()`` read a coordinate that a relation, a derived
    coordinate or a wiring of your own class bound only afterwards, so
    the value it read was not this run's. The rest-default guard, ``if
    self.turn.value is None: self.turn = 0``, is not refused: it reads a
    slot the author itself then binds.

Wirings take part in the same solve, so passing a coordinate down from a
coordinate a relation solves works without ordering anything by hand. At
the start of each run the framework clears what was bound during the
previous run, so every instant re-solves from fresh bindings.

Under a running root a law is also read as an increment, with its jumps
located and subtracted, and some laws are refused that pose perfectly
well; under a clocked root a ``commits`` relation writes states at
events. :doc:`running` and :doc:`clocked` state those rules.
