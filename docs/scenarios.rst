
.. _scenarios:

================================
Simulating and testing scenarios
================================

:doc:`Driving a machine <driving>` by hand answers "what does this
pose look like". A **scenario** answers the questions after that: does
the carriage clear the stop on the way home, when does it arrive, what
did the whole run look like. For those, the machine is stepped
deterministically in Python by `solid_node.simulation`.

The stepped loop
================

A `Sim` steps one assembly with a fixed time step:

.. code-block:: python

    from solid_node.simulation import Sim

    sim = Sim(machine, dt=0.02)

Its instants are **integer tick counts**: the clock advances tick by
tick, ``sim.time`` is ``tick * dt`` in seconds, and an instant that is
not a whole number of ticks is rejected rather than rounded. That is
what makes a scenario deterministic — the same program over the same
machine takes the same ticks and lands on the same values, every run,
on every platform.

Inside a simulation, ``self.time`` in your ``simulate()`` reads this
stepped clock, in seconds. The normalized 0..1 ``$t`` of the
:doc:`animation timeline <animation>` is untouched outside
simulations; the two are different clocks for different jobs.

A scenario is scheduled, then run:

.. code-block:: python

    sim.at(0.0).trigger('Home')                # due at t=0, fires first
    sim.every(0.1, check_clearance, machine)   # a cadence, every 5 ticks
    sim.at(2.5).run(lambda s: log(s.state))    # any callable, given the sim
    sim.run(3.0)                               # step 150 ticks

* ``at(t)`` schedules an action for one instant — triggering an
  instruction or running a callable. Actions due at the current tick
  fire **before** the first step, so ``at(0.0).trigger(...)`` is not
  one tick late.
* ``every(period, fn, *args)`` calls ``fn`` on a cadence. This is how
  a scenario keeps an invariant under watch — an interference check
  every tenth of a second — and ``sim.cadence_costs`` reports what
  each cadence cost, so an expensive geometric check is a visible,
  chosen expense.
* ``trigger(name)`` starts a declared `Instruction`: a `RampProgram`
  advances each target from its current value as a pure function of
  the tick, and **lands exactly on target**. An integer-typed driver
  ramps integer-exactly (``start + delta*k//n``) — every intermediate
  value is a whole native unit, with no accumulated float error.
* ``run(duration)`` steps the loop. Each tick binds a full snapshot of
  qualified driver values plus the global ``time``, so nested
  assemblies render numerically, and appends to ``sim.trajectory`` —
  the recorded ``(tick, states)`` history of the whole run.

``sim.state`` is the live bank of driver values by qualified id, the
same ids `set_state` and the document's driver table use.

Scenario tests
==============

`ScenarioTest` packages the loop for a test suite. Declare the node,
the step, and whether the scenario needs geometry:

.. code-block:: python

    from solid_node.simulation import ScenarioTest

    from .axis import Axis

    class AxisScenarioTest(ScenarioTest):
        node = Axis
        dt = 0.02
        meshes = True    # this scenario asserts on geometry

        def test_homing_stays_clear_of_the_stop(self):
            sim = self.simulation()
            arrived = []

            sim.at(0.0).trigger('Home')
            sim.every(0.1, self.assertNoSolidInterference, self.node)
            sim.at(2.5).run(lambda s: arrived.append(s.state['x']))
            sim.run(3.0)

            self.assertEqual(arrived, [0])
            self.assertEqual(sim.assertion_stats[0], 30)

Every scenario gets a **fresh** simulation from ``self.simulation()``
— the state bank is the whole of what a run mutates, so two scenarios
of one class share nothing but the geometry they were built from, and
each starts from the declared driver defaults.

``meshes = True`` is what makes the run build STLs; a scenario about
state alone should not pay for them. With meshes on, the geometric
assertions of the :doc:`test framework <testing>` work inside a
cadence: the homing test above proves clearance thirty times along the
move, and its counterpart proves the *teeth* — an instruction that
deliberately drives into the stop must be caught at the exact tick the
overlap appears:

.. code-block:: python

        def test_a_crash_is_caught_at_the_tick_it_appears(self):
            sim = self.simulation()

            sim.at(0.0).trigger('Crash')
            sim.every(0.1, self.assertNoSolidInterference, self.node)

            with self.assertRaises(AssertionError):
                sim.run(3.0)

            self.assertEqual(sim.tick, 75)

A scenario that only ever passes is not evidence; write the run that
must fail, and assert where it fails.

One class, both runners
=======================

A `ScenarioTest` is a `TestCase`. As a companion test of a node file
it runs under ``solid test`` like any other; imported into a pytest
module it runs under plain ``pytest``. Neither runner is modified for
it, and nothing in a scenario is written for one runner or the other —
under the CLI, ``node`` is the built instance the runner hands over;
under pytest it is the declared class and the scenario builds it.

Choosing dt
===========

``dt`` is part of the scenario's meaning, not a tuning knob: the crash
test above asserts tick 75 *because* ``dt = 0.02`` makes the carriage
travel 0.15mm per tick. Pick a step that resolves the finest motion
the scenario judges, declare it on the class, and let the tick
arithmetic be exact from there.


Running a machine that keeps its history
========================================

Everything above poses the machine from the current driver values. Under
a root declaring :ref:`Time.running() <animation>` — ``time =
Time.running()``, the second time base — a simulation instead OWNS the
machine's coordinates and moves them by increments, so a crank turned ten
degrees twice leaves its arbor at forty rather than back at twenty.

``sim.state`` is then the whole BANK: every driver **and** every joint
coordinate of the linked tree, by the same qualified ids the document
publishes. Plain ports and derived coordinates are not in it — they are
calculations over the state, recomputed by the ordinary render on every
tick. The initial bank is the untimed rest pose at the requested driver
values, so ``Sim(machine, dt, state={'crank': 30.0})`` starts where the
relations put the machine at a crank of thirty. A joint coordinate the
rest render leaves unbound is refused at construction, naming it: the run
needs a rest value for every coordinate it keeps the history of.

Commands, not bindings
----------------------

A running simulation takes requests rather than snapshots:

.. code-block:: python

        sim = Sim(machine, 0.1)

        turn = sim.move('crank', by=10.0, duration=1.0)   # travel
        sim.move('carriage', to=40.0, duration=0.5)       # land
        spin = sim.rate('spindle', 90.0)                  # until released
        sim.trigger('Advance')                            # an instruction

        sim.run(1.0)
        sim.rate('spindle', 0)          # completes the rate

        turn.status                     # 'completed'
        turn.admitted                   # 10.0, in design units

Only a declared driver can be moved, and each has ONE OWNER at a time: a
second move or rate on an input another command holds is refused naming
both. Every request returns a handle reporting ``active``, ``completed``,
``blocked``, ``refused`` or ``cancelled`` and the travel actually
admitted; a completed command leaves ``sim.commands`` the tick it
finishes, so a long run accumulates none. ``duration`` is a whole number
of ticks, zero included — a zero-duration move settles at the current
tick without advancing the clock.

``handle.cancel()`` stops a command where it stands: it is retired at
once reporting ``cancelled`` with the travel it had actually admitted,
its input is free from the moment ``cancel()`` returns, and it admits
nothing more. A replacement is accepted the same tick, with no tick
passing in between:

.. code-block:: python

        turn = sim.move('crank', by=10.0, duration=1.0)
        sim.run(0.3)
        turn.cancel()
        turn.status                     # 'cancelled'
        turn.admitted                   # 3.0, what it made before the cancel

        sim.move('crank', by=5.0, duration=0.5)   # accepted at once

Cancelling a command already retired — ``completed``, ``blocked``,
``refused`` or ``cancelled`` — keeps what it reported and does nothing
else, so cancelling twice is cancelling once.

An instruction works the same way, and now states either where its
drivers land or how far they travel:

.. code-block:: python

    instructions = {
        'Park':    Instruction({'crank': 40.0}, duration=0.5),
        'Advance': Instruction(by={'crank': 10.0}, duration=0.5),
    }

``by=`` is a relative ramp under every time base: untimed and looping it
ramps each driver from where it stands, and under a running root it
becomes ``move(by=)``. A relative instruction is not published in the
document's instructions table yet — the shipped viewer reads ``targets``
off every entry — so declare one for a scenario before you declare one
for a button.

A law that jumps
----------------

A law may contain a **jump** — ``floor``, ``ceil``, ``sign``, ``%`` or a
comparison — and a periodic mechanism usually does. The Curta's tooth
window is the illustration: a pinion that turns 72 degrees while one
tooth is engaged, once per crank revolution.

.. code-block:: python

    def periodic_window(source, target):
        return lambda angle: 4 + 72 * clamp01(
            (angle - 360 * floor(angle / 360) - 113.5) / 11.25)

    crank.drives(pinion.turn, law=periodic_window)

Absolutely, that law can only say where the pinion IS for a crank angle:
after a whole revolution it reads exactly what it read before. Running,
it is INTEGRATED, and the jump is subtracted. Over one tick the run cuts
the path the sources take at every crossing of every jump surface it
meets; on each piece every jump node holds one branch, read at the
piece's midpoint; and the increment is the sum of the branch-substituted
law's change over the pieces. So the pinion stands at ``4`` at rest, at
``76`` after one crank turn and at ``148`` after two, and the tick in
which the crank passes 360 degrees contributes exactly zero.

Every crossing inside the tick is found, not only the difference of its
ends: a crank turned far enough to pass three tooth windows in one tick
adds three throws. The five primitives cross where their LEVEL QUANTITY
reaches a surface — ``floor(x)`` and ``ceil(x)`` over ``x`` at every
integer, ``sign(x)`` over ``x`` at zero, ``a % b`` over ``a / b`` at
every NONZERO integer (``%`` is ``fmod``, which takes the sign of the
dividend and is continuous where ``a / b`` crosses zero), and a
comparison over ``a - b`` at zero. :func:`~solid_node.math.wrap` is
built on ``ceil`` and integrates through the same door — a wrapped law
reads as the unwrapped travel — and :func:`~solid_node.math.piecewise`
needs nothing of its own, being a sum of ``clamp01`` terms with no jump
in it at all.

DISENGAGEMENT is a law's own business, and both its shapes are now
expressible: a gate factor in a multi-source law, or the zero-slope
region of a single-source one.

.. code-block:: python

    def clutch(sources, target):
        return lambda shaft, sleeve: -2 * shaft * (sleeve > 0.5)

    (shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)

The wheel holds while the sleeve is out, drives while it is in, and on
the tick in which the sleeve travels from ``0`` to ``1`` takes the travel
AFTER engagement only — never the value the gate factor would have jumped
to. A law naming several sources takes one straight path in their joint
space, which is what makes a clutch closing while a shaft turns one
question rather than two.

Two things are refused, and one more can refuse a tick:

* a law that can move its coordinate **only by jumping** — ``floor(turns)``
  alone — because every jump is subtracted, so such a law can never move
  anything. It states arithmetic, not a mechanism.
  ``9 * enabled + floor(turns)`` is not refused: ``enabled`` still
  carries slope, and the running reading simply gives the turns nothing;
* a jumping law whose driven ends are all **intermediates** — a plain
  port, a derived coordinate. A subtracted jump implies a history, and
  only a coordinate the run owns keeps one; an intermediate is
  recomputed from the bank on every tick, so it would snap while the
  joint behind it moved smoothly. State the relation into the joint
  coordinate and let the port follow it;
* a tick that would cross more than a thousand surfaces of one law is
  refused naming the relation, the coordinate, the primitive and the
  count, and commits nothing. A ``dt`` that coarse is not resolving the
  mechanism.

A level quantity that is AFFINE in the sources along the path — which is
every periodic law in practice — has its crossings solved exactly, all of
them. So does a PIECEWISE AFFINE one: ``abs``, ``min`` and ``max`` are
continuous selections, each returning one of its operands exactly, so a
level built over them — every ``clamp``, ``clamp01``, ``ramp`` and
``piecewise`` profile — is cut at its own kinks and each piece solved,
with nothing recorded at a kink and nothing sampled. Anything else — a
``sin``, a ``sqrt``, a product of two moving quantities — is sampled at
64 sub-intervals and each bracketed crossing bisected; a level quantity
that turns twice inside one sub-interval is outside that guarantee, and
the answer to it is a smaller ``dt``.

A law that reads the coordinate it drives
`````````````````````````````````````````

Every law above is a function of coordinates OTHER than the one it
drives. Some mechanisms are not: whether a rack turns a dial can depend
on where that dial itself is standing. The Curta is cleared by sweeping a
ring carrying two nine-tooth racks past the register dials, and a rack
turns a dial only while its teeth reach it AND the dial is not already
standing at its missing-tooth zero. Name the coordinate on BOTH sides of
one relation and the law READS it:

.. code-block:: python

    def missing_tooth(sources, target):
        def law(ring, wheel):
            shifted = wheel + GAP
            return ring * (shifted - 360 * floor(shifted / 360) >= 2 * GAP)
        return law

    (ring & wheel.turn).drives(wheel.turn, law=missing_tooth)

The law is handed that coordinate's owner exactly as it is handed any
source's, and what it reads there is the value the coordinate HOLDS —
never a value the same application is about to give it. So a dial swept
from any digit runs to its gap and stops; the ring goes on sweeping past
it to reach the dials beyond; releasing the ring part way keeps the
partial clearing, and resuming continues from there; and sweeping an
already-cleared dial does not turn it again.

**The read must be a SWITCH.** With every jump node replaced by its
branch — the skeleton the jump plan already builds — the law must no
longer name the driven coordinate. A read that survives the skeleton
enters the law continuously, which makes the relation a differential
equation that ``f(end) - f(start)`` does not define, and it is refused at
construction naming the relation. ``%`` alone is not a switch: with the
quotient fixed, ``a % b`` reads ``a - q·b``, which still carries the
coordinate's slope. Pass the read through ``floor``, ``ceil``, ``sign``
or a comparison.

**The tick is integrated in two layers.** The jump nodes that do NOT
depend on the driven coordinate partition the path exactly as any other
law's do, their branches read at the midpoints. Inside each of those
pieces the nodes that DO depend on it are WALKED: their branches are
read at the piece's LEFT END, with the driven coordinate at the value it
retains there and every other source at that same fraction; with the
branches fixed the coordinate's own path is an ordinary evaluation; the
piece is cut at the first surface any dependent level reaches; and the
next piece is decided the same way. A law with no self-read takes the
path above with nothing rebuilt at all.

**After a cut the coordinate is committed at the FAR SIDE of the
surface**, at the nearest representable value — the same rule as "a
stopped coordinate is committed AT its bound exactly", transposed to a
surface that is not stated in the coordinate's own units. That is what
makes a dial that reached its gap read the same branch on every later
tick, whatever the ring does, and survive a snapshot and a restore bit
for bit.

**A gate's disengaged state must have WIDTH**, and the width is the
mechanism's own clearance. A missing tooth is a GAP: a band about the
zero, entered from either side, so the dial stops at the edge it arrives
at — the lower one swept forward, the upper one swept backward. Write the
clearance as the band's half-width, as ``GAP`` does above. A gate whose
disengaged state is a single value of the coordinate — ``wheel % 360 >
0`` — is not a gap: it holds only where the far side of its surface
happens to be the disengaged region, and the framework cannot tell a
knife edge from a band, because the distinction is numeric and not
syntactic. State the width.

Three more things follow:

* **the dial's rest value is the author's own.** Such a relation binds
  NOTHING at rest, so the dial declares its rest default in the guarded
  ``simulate()`` idiom, and a dial with none is refused at construction
  by the run's "needs a rest value for every joint coordinate";
* **it drives ONE coordinate.** A driven GROUP one of whose members the
  source group names — itself or a sibling — is refused at class
  definition. A broadcast is admitted: each copy is its own record with
  one driven end reading itself;
* **it needs a run.** Under any other time base the relation is refused
  by name at the close of the enumeration: it states increments, and only
  a run integrates those.

A cut of a self-read law is a CROSSING, not a stop: it stops no input and
retires no command. A declared range on the same coordinate still stops
it, exactly as it stops any other, and wins where both fall in one
segment. And a document whose program carries such a law is a **version
6** document, because a consumer that read it as ``f(end) - f(start)``
would have the read at both ends, freeze the branch and move the part by
a different mechanism in silence.

A selection decides which sources a law reads
--------------------------------------------

A machine whose dependencies are SELECTED by where one of its own parts
stands has a CYCLIC union: a Curta's fixed carry lever is tripped by the
dial the carriage has brought under it and advances the dial beyond that
one, so which dial it reads and which dial it drives both follow the
carriage. :doc:`driving` states how such a machine is written -- every
association a comparison factor on the carriage's own joint coordinate.
Here is what a run does with it.

A cycle every selection breaks is a **BLOCK**: one entry of the program,
ordered once per PIECE of a tick. Over a stretch the block's selectors
are located first, the stretch is cut at each of their surfaces, and on
each piece the branches read at the MIDPOINT decide which dependencies
are active, in what order the members run, and what each of them reads.
A member is then integrated over the piece by the rules that already
govern it -- the jump partition, and the walk of a law that reads the
coordinate it drives -- with its selectors held at the branch the block
read, not located again.

What a block reports for a coordinate some piece LANDED at a gate is the
absolute value it has advanced that coordinate to by the stretch's END --
the landing plus every later piece's increment -- because the run commits
a reported landing absolutely and would otherwise discard the motion
after it.

A selector crossing is a CROSSING and not a stop: it stops no input and
retires no command. A declared range on a coordinate the block drives
still stops it, located through the block's own searched path and
committed at its bound. An input that reaches a stopped block coordinate
ONLY through a selection that is inactive over the stretch is not stopped
by it, and admits its whole travel.

A tick whose piece still cannot be ordered is REFUSED, naming the piece,
the selector branches it was read under and the relations on the cycle.
It commits nothing, exactly as a conflict does.

A document whose program carries a block is a **version 7** document.
The published ORDER of a block's members is a listing, not an execution
order: a runtime that executed them in it would move the machine by
whatever that order happened to give, silently, and by a different amount
for each order it might have chosen. No key is added for a block -- a
consumer re-derives it from the edges' own ``needs`` and ``gives``, and
its selectors from the published ``level`` of each plan's jumps.

A range is a physical stop
--------------------------

Under a running root a joint's declared ``range`` is a MECHANICAL LIMIT,
not a refusal of the tick. When a tick would take a banked coordinate
outside a bound — and further outside than it stood at the start — the
run locates the fraction ``t*`` of the tick at which it reaches that
bound, commits it there EXACTLY, and the tick commits like any other.
Both bounds stay inclusive, so a move landing exactly on one is no stop
at all.

What stops with it is the CONNECTED GROUP: every input whose own
movement over that stretch pushes the stopped coordinate, and everything
those inputs alone determine. An input that does not reach it, or reaches
it only through a law that is currently disengaged — an open clutch, a
carry outside its window — runs its full tick, and a coordinate
determined by both a stopped input and a free one goes on moving on what
the free one contributes. The tick becomes two segments, ``[0, t*]`` and
``[t*, 1]``, each integrated by exactly the procedure above; the second
is examined for a further stop, and the earliest ``t*`` is always taken
first. The tick stays atomic: a conflict or an unintegrable law in any
segment commits nothing.

A command whose input is stopped is retired reporting ``blocked``, with
the travel it ACTUALLY admitted — fractional within the tick, in design
units. A blocked command NEVER resumes: nothing remembers the travel it
did not make, and a later tick does not continue it. The caller issues a
new command, which may move away from the stop or push into it again and
be blocked at once with ``0`` admitted. A ``rate`` on a stopped input is
retired ``blocked`` too. Where one instruction names several inputs, each
handle reports for itself: the free one is not held back.

.. code-block:: python

    rack = Slide(travel=Prismatic(axis=(1, 0, 0), range=(None, 50.0),
                                  unit='mm'))

    steer.drives(rack.travel, ratio=1.0)
    motor.drives(wheel.turn, ratio=3.0)

With the rack at ``45`` and the motor running, ``move('steer', by=10,
duration=0.1)`` at ``dt = 0.1`` leaves the rack at exactly ``50``, the
steering handle ``blocked`` with ``5.0`` of ``10`` admitted, and the
wheel with its full 27 degrees for that tick.

Either bound may be ``None``, meaning unbounded on that side, or a
CALLABLE of one argument stating the bound as an expression over the
joint's OWN coordinate. That is a ratchet:

.. code-block:: python

    turn = Revolute(axis=(1, 0, 0),
                    range=(lambda turn: 36 * floor(turn / 36), None))

The lower bound is the last seated tooth and there is no upper bound,
because forward rotation is free. Under a running root the expression is
compiled once, like a law, and evaluated ONCE PER TICK from the committed
bank, so within a tick the bound is a number and the self-reference is
well defined; a jump in it is evaluated rather than integrated, which is
what makes the tooth pitch a tooth pitch. Untimed and looping it is
evaluated at THE VALUE BEING BOUND, exactly as a number bound is compared
against it, so the same declaration poses and runs. A bound that is not
satisfied at its own argument forbids every value, and the first binding
says so by name.

From ``40``, a reverse of ``-10`` blocks at exactly ``36`` having
admitted ``-4``; a further reverse blocks at once with ``0``; ``+4`` is
free; and the reverse after that blocks at ``36`` again. That is
retention, and it admits the same travel whether the move is taken in one
tick, four or forty. ``t*`` is EXACT wherever every edge between the
pushing inputs and the stopped coordinate is affine — every ratio, every
wiring, every linear formula — and wherever the determining law is
PIECEWISE affine, which is solved on the piece the bound actually lies
in; for a curved upstream edge the stopped
coordinate is still committed at its bound exactly, while the group's
other coordinates are stopped at a ``t*`` located on the linearized path.

A ``Driver``'s own declared ``range`` is untouched by all of this: it is
presentation metadata, and nothing clamps to it, because a machine driven
past its declared travel is a crash a simulation must be able to SHOW. A
stop is a joint's, not a driver's. Untimed and looping documents are
unchanged too: there a range REFUSES a binding outside it, and never
clamps or stops.

Snapshot, restore, reset, record
--------------------------------

``sim.snapshot()`` is a value: the bank, the tick, ``dt``, the active
commands and the program's identity. ``sim.restore(snapshot)`` puts the
run back, refusing a snapshot taken over a different machine or a
different ``dt`` before it touches anything, and ``sim.reset()`` restores
``sim.initial`` — the rest pose. Recording is explicit and bounded:
``record=None`` keeps nothing and ``sim.trajectory`` reads empty, while
``record=64`` keeps a ring of the most recent sixty-four ticks. A run
that never wraps cannot keep every tick, and ``every()`` sees each one as
it happens.

``record=N`` keeps a second ring of the same length, read through
``sim.crossings``: the most recent ``N`` crossings located inside a tick,
each naming the tick, the relation as written, the driven coordinate, the
primitive that jumped, the surface it reached and the fraction of the
tick at which it did. ``record=None`` keeps none and builds none, and
restore and reset clear every ring. A surface reached exactly at a tick's
own boundary is not inside any tick, so it is integrated — correctly, and
contributing nothing — without appearing in the record. Where a stop cut
the tick into segments, each crossing is still recorded at its fraction
OF THE TICK, whichever segment located it.

``record=N`` keeps a THIRD ring, read through ``sim.stops``: the most
recent ``N`` stops, each naming the tick, the coordinate that stopped,
which bound it reached and that bound's evaluated value, the fraction of
the tick at which it was reached, and the inputs the stop blocked. A stop
is appended only when the tick commits, and ``record=None`` keeps none
and builds none.

What a running root publishes
-----------------------------

A running root's document is a **version 5** document. Beside the
geometry it always published it carries a ``program`` object: what
compile time decided about the machine, and nothing the tick computes —
the coordinate table with each bank id's kind, rest value, unit and
domain, the intermediates, the compiled edges in program order with
their expressions and jump plans, the spans, the candidate table of
which inputs reach what, the program identity, the clock name and the
constants the algorithm is defined by. And every joint's placement in
the tree is published as its own coordinate's qualified id, so a
consumer poses the geometry from a bank it committed rather than from
the law read absolutely at the driver values, which is the whole
difference between a machine that accumulates and one that snaps back.

Both instruction forms travel under version 5 — ``targets`` and ``by``,
each entry carrying exactly one of them — where versions 2 to 4 publish
only the absolute form.

A tree that declares :ref:`controls <controls-on-parts>` carries a
``controls`` table beside ``instructions``: which part a person presses
and which part a person turns, with the coordinate, the joint node, the
axis, the point it turns about and the measured ``per_unit`` of each
gesture. It is additive within version 5, and a tree that declares none
omits the key and publishes the document it always did. See
:doc:`Driving a machine <driving>`.

The bump is not additive, and a consumer that cannot read version 5
refuses the document by name rather than rendering part of a machine it
does not understand. ``solid build``, ``solid develop`` and ``solid
export`` publish it anyway and warn once, naming the version written,
the versions the installed viewer renders and the viewer's package
version; ``solid snapshot --renderer web`` refuses before it starts the
browser, because a capture is a one-shot. A browser that RUNS the
machine is the viewer package's own next release.

Under a running root the clock leaves the document too: the model's
``self.time`` publishes as the free name ``time``, declared as
``program.clock``, which a runtime binds to elapsed simulation seconds
and a consumer with no run binds to zero. The bare ``$t`` preview a
Python read gets is unchanged.

What this release refuses
-------------------------

Each of these is refused by name, and each is a later cycle's to lift:

* a law that cannot be applied to a symbol — one written over Python's
  own ``math`` rather than :doc:`solid_node.math <api-reference>`;
* a relation into a coordinate the run owns whose SOURCE is a plain port
  an author's ``simulate()`` binds: state that value as a relation, or
  give the part a joint;
* an author's ``simulate()`` that binds a run-owned coordinate
  unconditionally — that is a law written imperatively, and it belongs in
  a relation. The rest-default idiom, binding under ``if ... is None``,
  keeps working: it binds once, at the rest render;
* a law that READS the coordinate it drives CONTINUOUSLY — one whose
  skeleton still names it, a bare ``%`` included. The read must pass
  through a node that is piecewise constant in it; anything else is a
  differential equation, not an increment.

A tick that refuses commits nothing: the bank, the tick count and the
posed tree stand as they were, and the commands that moved an input in
it are retired reporting ``refused``.

One limit is stated rather than refused: a coordinate that leaves its
range and RETURNS within one tick is not stopped, because the detection
compares the tick's committed value. It cannot happen where the
determiner is affine along the path — the common case, and every case in
practice — nor where it is piecewise affine and MONOTONE between its
kinks; anywhere else the answer is a smaller ``dt``, as it is for a jump
surface crossed twice inside one sub-interval.


Running a machine that keeps a FEW values
=========================================

A running root retains every coordinate and integrates every law at a
fixed cadence. Some machines do not need that. A **clocked** machine has
a few retained values, closed-form positions between them, and a commit
of the retained values at each event — a calculator whose registers
change only at the end of a crank stroke, and whose interlocks hold
everything else still while the crank is off rest.

Declare the retained value beside the drivers:

.. code-block:: python

    from solid_node.simulation import Driver, State

    class Counter(AssemblyNode):
        crank = Driver(default=0, unit='deg')
        units = State(default=0, range=(0, 9), dtype=int)
        tens = State(default=0, range=(0, 9), dtype=int)

``State`` takes exactly ``Driver``'s arguments with exactly their
meanings, is read ``self.units`` exactly as a driver's value is, and
carries the same instance-qualified id. Everything that differs is about
who WRITES it: ``set_state`` refuses one by name, an ``Instruction`` and
a control cannot target one, and ``crank.drives(units)`` is refused. A
state may be a SOURCE of ``drives`` — that is how the pose is fed from
it — and it is written by exactly one thing.

The verb that writes it
-----------------------

.. code-block:: python

    def strokes(sources, targets):
        return lambda crank, units, tens: floor(crank / 360)

    def advance(sources, targets):
        return lambda crank, units, tens: (
            (units + 1) % 10, (tens + (units == 9)) % 10)

    class Counter(AssemblyNode):
        ...
        (crank & units & tens).commits((units, tens),
                                       at=strokes, law=advance)

``commits`` sits beside ``drives``, on the same ``&`` groups, and its
two factories follow the law-factory protocol the rest of the motion
layer already uses: each is called ONCE, at realization, with the
realized owners, and returns a callable over the sources' values in
written order. Neither is handed an event object or any per-tick state.

``at`` states the EVENT and is exactly one jump node — ``floor(x)``,
``ceil(x)``, ``sign(x)``, or a comparison. Every RISING step of it along
a request's path is one event. ``law`` states the value written there.
A source group MAY name its own target, which is a READ of that target's
value: the Curta's clearing threshold is a function of the digit the
dial is standing at, so ``at`` reads the digit it commits.

Both read and write NATIVE values — the bank's own units. A ``dtype=int``
state takes the nearest whole native unit, rounded once, at the commit; a
scaled one takes what the law returned, unrescaled.

SEVERAL relations may write one state. A register digit is written at the
stroke end, by the arithmetic of the crank turn, and again at the clearing
reach, by the ring sweeping past its rack — two events, two inputs, and one
relation states one ``at``. What is refused is two answers for one value at
ONE event: if two relations firing at one landing would write the same
state, the REQUEST is refused, naming the state, both relations and the
landing, and it commits nothing. Two children of one class each declare
their own state, so ``a.digit`` and ``b.digit`` are two states and one
relation may write both.

A committing relation whose sources are ALL states is refused at
construction: a state is constant between events, so nothing a request moves
enters its level and it could never fire.

A request, not a tick
---------------------

.. code-block:: python

    sim = Sim(machine)                  # no dt: there is no clock
    request = sim.move('crank', by=3600.0)

    len(request.commits)                # 10
    sim.state['tens']                   # 1

A request moves ONE declared driver along a straight path, and every
rising crossing on it is located EXACTLY — solved by one division on an
affine level, one division per sub-interval on a kinked one — and never
searched. A level the moving driver CURVES is refused at construction,
naming the driver and the primitive: a clocked model's whole value is
that its events are exact.

Two relations are ONE event exactly when their far-side landings are the
same floating-point value. No tolerance decides it, so ten requests of
one revolution give the same events as one request of ten.

Only RISING steps fire. Dragging the crank backwards through
``floor(crank / 360)`` commits nothing — which is what the anti-reversal
pawl of a real machine gives. A mechanism that commits on the other edge
negates its own level, ``floor(-crank / 360)``.

A commit is evaluated at ONE POINT and never integrated, so every jump
primitive in a commit law means what it says: ``floor(crank / 360) % 10``
is a digit, where under a running root a law of that shape is refused as
arithmetic. Every relation firing at one event reads the bank as it stood
BEFORE it, so the order of two lines in a class body is not observable.

Between events nothing is retained. A pose is the ordinary untimed
enumeration over the drivers and the states, and nothing else: ``time``
is not in the bank, and a clocked pose leaves ``self.time`` the symbolic
``$t`` exactly as the build path does. A request touches the tree ONCE,
at its end — which is why a request costs about what one pose costs and
a commit costs microseconds.

``sim.state`` is the bank; ``sim.snapshot()``, ``sim.restore()``,
``sim.initial`` and ``sim.reset()`` act on it, and ``Sim(model,
state={...})`` opens a session at chosen values. Those two are the only
ways to set a state: everything else about it is the machine's.

What a clocked model refuses today
----------------------------------

* **Publication.** A tree that declares a ``State`` is refused by every
  document producer, naming the states: the document version that
  carries them is not defined yet. Rendering, assembling, STL building,
  ``solid test`` and an OpenSCAD snapshot are untouched, so a clocked
  model is built, tested and photographed exactly as any other.
* **A time base.** A ``State`` under ``Time(loop=)`` is refused — a loop
  replays from zero and would replay every commit — and under
  ``Time.running()`` it is refused too, with its meaning named and
  deliberately not implemented.
* **A bound as a stop on a request path.** A violated joint ``range`` is
  still an impossible POSE, raised on the pose the request ends at — and a
  refused pose refuses the whole REQUEST: the bank, the tree and the
  recorded events stand exactly as they stood, rather than the request
  stopping where the machine stops and keeping what it committed on the
  way.
* **The cadence surface.** ``run``, ``at``, ``every``, ``time``,
  ``tick``, ``rate``, ``trigger``, ``commands``, ``program``,
  ``crossings`` and ``stops`` are each refused by name. A clocked model
  has no clock.
* A port, joint coordinate or derived coordinate as a SOURCE; a
  broadcast ``commits`` over a ``.repeat()`` child; a request naming more
  than one input; an instruction or a control under a clocked root.
