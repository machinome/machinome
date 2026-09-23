Running mechanics
=================

Under a root declaring ``time = Time.running()`` a simulation owns the
machine's coordinates and moves them by increments. This page states
what that changes: what the run banks, how it takes requests, how it
reads a law, where it stops, and what it refuses.

The bank
--------

``sim.state`` is the whole bank: every driver **and** every joint
coordinate of the linked tree, including joints on leaves, site-declared
joints and all six coordinates of a ``Free``, by the qualified ids the
document publishes. Plain ports and derived coordinates are not in it;
they are calculations over the state, recomputed by the ordinary render
on every tick. The initial bank is the untimed rest pose at the requested
driver values, so ``Sim(machine, dt, state={'crank': 30.0})`` starts
where the relations put the machine at a crank of thirty. A joint
coordinate the rest render leaves unbound is refused at construction,
naming it: the run needs a rest value for every coordinate it keeps the
history of, and the ordinary guarded rest default supplies one:

.. code-block:: python

    def simulate(self):
        if self.slide.travel.value is None:
            self.slide.travel = 4.0

An unconditional hand binding of a run-owned joint in ``simulate()``
raises ``DoublyBound`` at construction: that is a law written
imperatively, and it belongs in a relation. Plain ports may still be fed
in ``simulate()`` from owned coordinates, a spring's height or a readout,
but an imperatively fed port cannot source a compiled law into a banked
coordinate. One tree has one run owner: constructing a new ``Sim`` over
it releases the previous one.

Commands, not bindings
----------------------

.. code-block:: python

    sim = Sim(machine, 0.1)

    turn = sim.move('crank', by=10.0, duration=1.0)   # travel
    sim.move('carriage', to=40.0, duration=0.5)       # land
    spin = sim.rate('spindle', 90.0)                  # until released
    sim.trigger('Advance')                            # an instruction

    sim.run(1.0)
    sim.rate('spindle', 0)

    turn.status                     # 'completed'
    turn.admitted                   # 10.0, in design units

Only a declared driver can be moved, by qualified id, and each has one
owner at a time: a second move or rate on an owned input is refused
naming both. Travel and destinations are design units; the bank stays in
native units. ``duration`` is a whole number of ticks, zero included: a
zero-duration move settles at the current tick. Every request returns a
handle reporting ``status`` (``active``, ``completed``, ``blocked``,
``refused``, ``cancelled``), ``requested``, ``admitted`` and
``remaining``; a completed command leaves ``sim.commands`` the tick it
finishes. ``handle.cancel()`` retires a command where it stands, and a
replacement is accepted the same tick.

An instruction states either where its drivers land or how far they
travel, ``Instruction({'crank': 40.0}, duration=0.5)`` or
``Instruction(by={'crank': 10.0}, duration=0.5)``, and both forms publish
as buttons under a running root. ``sim.trigger(name)`` returns one handle
per target input; an already-owned input refuses the instruction rather
than replacing its move.

Controls on parts
-----------------

A ``controls`` table beside ``instructions`` puts a request on the part
itself: ``Button(part, instruction)`` is a press submitting that
instruction; ``Turn(part, input)`` is a drag about the rotational
coordinate the part rides and ``Slide(part, input)`` a drag along a
translational one, each issued as relative moves on ``input``. A control
moves nothing itself and carries no state; ownership, admission, stops
and outcomes are what ``trigger``, ``move`` and ``rate`` state, and a
blocked drag reports blocked with no hidden backlog.

``part`` is a node, written as a relation's path ends are; ``input`` is
the ``Driver`` declaration, never an id string. The gesture's axis and
pivot are read off the tree, and ``per_unit``, how far the part moves per
unit of the input, is **measured** from the compiled program at the rest
bank, never declared, because a number stated twice is a number that
drifts. When a body has two freedoms, a crank that both lifts and turns,
``coordinate=`` names the joint declaration the gesture means; it may
select a joint further up the part's ancestry but never one on another
branch. The framework never guesses which part a hand means: a dial
moved by two things has no inferrable gesture, and the author declares
it. Refusals name their facts where they exist: at class definition
(a part the class does not hold, a repeated child, a drag over a driver
the class does not declare), at compile (a part no run-owned coordinate
poses, a ``Turn`` over a non-rotational coordinate, a drag whose input
does not reach the coordinate, naming the inputs that do) and at
publication (a drag that moves the part by nothing at rest). A control
under a root that does not declare ``Time.running()`` is refused.

Driving retained motion from time
---------------------------------

The root's running clock can be an explicit, read-only source of a
relation. Given a joint-bearing ``Shaft``, this machine advances six
degrees per second with no driver and no startup command:

.. code-block:: python

    class Machine(AssemblyNode):
        time = Time.running()
        shaft = Shaft()
        time.drives(shaft.turn, ratio=6)

    sim = Sim(Machine(), dt=0.02)
    sim.run(2)
    assert abs(sim.state['shaft.turn'] - 12) < 1e-9
    assert sim.commands == ()

For an operating enable, name both sources in their written order:

.. code-block:: python

    def enabled_rotation(owners, target):
        return lambda seconds, enabled: 6 * seconds * (enabled > 0.5)

    class Switchable(AssemblyNode):
        time = Time.running()
        enabled = Driver(default=1, range=(0, 1))
        shaft = Shaft()
        (time & enabled).drives(shaft.turn, law=enabled_rotation)

Turning the enable off holds the shaft; turning it on later resumes from
the held position, because the change of gate branch is subtracted like
any jump. This is an incremental **position law**, not a velocity
callback: continuous pieces contribute ``f(end) - f(start)``, so a law
``seconds**2`` stopped from time 1 to 3 resumes with an increment of
``4**2 - 3**2`` during the next second; it neither catches up on missed
travel nor restarts a private clock. Declare mechanical phase as a joint
coordinate when phase must be retained.

A physical stop clips the affected time-drive relation for the rest of
that tick; all targets of that relation and its downstream train share
the stop, an independent time-drive relation keeps going, and
``sim.time`` continues. The stopped relation retries on the next tick,
with no backlog and no command. Time appears in neither the bank nor the
command table: it cannot be moved, rated or targeted, and construction,
inspection and publication advance nothing. ``self.time`` remains valid
for an ordinary absolute transform, but assigning it to a run-owned joint
in ``simulate()`` is a second binding and is refused; name ``time``
explicitly in the relation. Time supplies seconds, not gravity, torque or
an escapement frequency; those remain the model's own laws. A program
with a time drive publishes document version 11, as does every new
running export that carries no ``Follow`` relation.

One law, two readings
---------------------

Laws are the same ``drives`` laws a posed machine uses, compiled once at
construction by applying them to symbolic sources in the direction the
rest pose solved each relation. Running, a law is **integrated**: a
continuous law moves its driven coordinate by ``f(end) - f(start)`` from
where it stood.

**A law that jumps.** A law may contain ``floor``, ``ceil``, ``sign``,
``%`` or a comparison, and a periodic mechanism usually does. Over one
tick the run cuts the path at every crossing of every jump surface it
meets; on each piece every jump node holds one branch, read at the
piece's midpoint; and the increment is the sum of the branch-substituted
law's change over the pieces. So a pinion driven by a tooth window stands
at 4 at rest, 76 after one crank turn and 148 after two, and the tick in
which the crank passes 360 contributes exactly zero. Every crossing
inside the tick is found, not only the difference of its ends. The five
primitives cross where their level quantity reaches a surface:
``floor(x)`` and ``ceil(x)`` at every integer, ``sign(x)`` at zero, ``a
% b`` over ``a / b`` at every nonzero integer, a comparison over ``a -
b`` at zero. ``wrap`` is built on ``ceil`` and integrates through the
same door; ``piecewise`` is a sum of ``clamp01`` terms with no jump in
it.

**Disengagement** is a law's own business: a gate factor in a
multi-source law, or a zero-slope region of a single-source one.

.. code-block:: python

    def clutch(sources, target):
        return lambda shaft, sleeve: -2 * shaft * (sleeve > 0.5)

    (shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)

The wheel holds while the sleeve is out and takes the travel after
engagement only on the tick the sleeve closes. A law naming several
sources takes one straight path in their joint space. A gate does not
block the input command; a joint range does.

**Solved or searched.** Where a followed quantity is affine in its
sources, a sum, a constant multiple, a division by a constant, its
crossings are solved by one division, exactly. Where it is piecewise
affine, which is what ``abs``, ``min``, ``max`` and every profile built on
them (``clamp``, ``clamp01``, ``ramp``, ``piecewise``) make it, the path
is cut at its kinks and each piece solved. Anything else, ``sin``,
``sqrt``, a product of two moving quantities, is sampled at 64
sub-intervals and each bracketed crossing bisected: correct, slower by
tens of evaluations per crossing, and less exact by the bisection's
tolerance; a quantity that turns twice inside one sub-interval is
outside the guarantee, and the answer is a smaller ``dt``. A tick that
would cross more than a thousand surfaces of one law is refused naming
the relation, the coordinate, the primitive and the count. If a running
machine is slower than you expect, this is where to look first: the same
profile written with ``clamp01`` costs almost nothing.

The run pays for deciding which part of a searched expression can change
once per followed quantity per tick, not once per sample, so a law that
reaches through a long chain of parts that stand still this tick is
charged only for the part that moves.

**A law that reads the coordinate it drives.** Name the driven
coordinate on both sides of one relation and the law reads it, taking
the value the coordinate holds at the start of each piece:

.. code-block:: python

    GAP = 0.5   # the gap's half-width: the mechanism's clearance

    def missing_tooth(sources, target):
        def law(ring, wheel):
            shifted = wheel + GAP
            return ring * (shifted - 360 * floor(shifted / 360) >= 2 * GAP)
        return law

    (ring & wheel.turn).drives(wheel.turn, law=missing_tooth)

A dial swept from any digit runs to its gap and stops, the ring goes on
sweeping past it, releasing the ring keeps the partial clearing, and
sweeping an already-cleared dial does not turn it. The rules: the read
must be a **switch** (with every jump replaced by its branch the law must
no longer name the coordinate; a bare ``%`` still carries the slope and
is refused); the relation drives exactly one coordinate, a joint the run
banks; it binds nothing at rest, so the joint's rest value is the
author's guarded default; and it needs a run. State the disengaged region
as a band with the mechanism's own width, entered from either side: after
a cut the coordinate is committed at the nearest representable value on
the far side of the surface, so a dial standing in its gap reads the
same branch on every later tick and survives a snapshot bit for bit. A
gate whose disengaged state is a single value has no width and is not
promised to hold. A cut of such a law is a crossing, never a stop. A
document carrying one is version 6.

**A selection decides which sources a law reads.** A machine whose
dependencies are selected by where one of its own parts stands (a Curta's
fixed carry lever, tripped by whichever dial the carriage brought under
it) has a cyclic union of dependencies. The selection is the comparison
the model already writes, a term multiplied by a gate on the selecting
coordinate, and a cycle every selection breaks is a **block**: one entry
of the program, ordered once per piece of a tick. The block's selectors
are located first, the stretch cut at their surfaces, and on each piece
the branches read at the midpoint decide which dependencies are active
and in what order the members run. A selection change alone moves
nothing; a block relation binds nothing at rest; a piece that still
cannot be ordered refuses the tick naming the piece, the branches and
the relations on the cycle. Determined sources retain their actual stroke,
dwell and landing timing through the block and through ordinary chains;
additional selector cuts do not replace that motion by endpoint ramps.
New running documents, including blocks, declare version 11, or 12
when they carry a ``Follow`` relation.

**Retained clearance.** ``Play(low, high)`` is the narrow running law for
a follower separated from its source by backlash or clearance: it holds
inside the interval, is collected at either flank, and is released when
the source reverses. Each play source is a run-owned driver or the output
of another play edge in one linear chain; anything else is refused. A
new document carrying one is version 11.

**Two moving surfaces.** ``Follow(lower=, upper=)`` is the narrower law
for a retained coordinate that rests freely between two independently
moving, authored boundaries, a ball between a bell and a collar: either
surface pushes it only on contact, and it stays where a retreating
surface left it, ``max(lower, min(retained, upper))`` at every certified
piece of the tick. Its two sources are inputs, held bank coordinates or
unbranched affine chains; the lower and upper ``Bound`` relations on the
same coordinate must state the same two surfaces, and they locate the
first contact at which the surfaces become incompatible, checking the
certified cuts as well as the uniform samples. Other ancestry, a curved
boundary or a contact too narrow to represent is refused, not
approximated; the follower feeds no other relation. A document carrying
one is version 12.

A range is a physical stop
--------------------------

Under a running root a joint's declared ``range`` is a mechanical limit,
not a refusal of the tick. When a tick would take a banked coordinate
outside a bound, the run locates the fraction of the tick at which it
reaches that bound, commits it there exactly, and the tick commits like
any other. What stops with it is the **connected group**: every input
whose own movement over that stretch pushes the stopped coordinate, and
everything those inputs alone determine. An input that does not reach
it, or reaches it only through a law that is currently disengaged, runs
its full tick. The tick becomes two segments, each integrated by the
procedure above, and the earliest stop is always taken first. A command
whose input is stopped is retired ``blocked`` with the travel it actually
admitted, fractional within the tick, and never resumes: the caller
issues a new command.

A bound given as a callable of the joint's own coordinate is compiled
once and evaluated once per tick from the committed bank, so within a
tick the bound is a number: that is the ratchet of
:doc:`/tutorial/08-running`, admitting the same travel whether a reverse
is taken in one tick or forty. A ``Bound`` that reads other coordinates
is a **constraint** evaluated along the tick's path: whenever a read
moves, it is sampled at 64 fractions and bisected, and the stop blocks
every input whose motion carries the constraint outward, through the
bounded coordinate or through what it reads. That is how an interlock
stops the key's withdrawal without moving the plug.

A constraint an ancestor adds to a nested joint
(:ref:`ancestor-joint-constraints`) is the same kind of stop. Its own
coordinate stays frozen at the value committed when the tick began
while its reads follow the attempted motion, so a moving read can never
overrun a standing target. Which inputs the stop blocks is judged **at
the contact**, not by comparing the level at the two ends of the whole
request: each candidate input is tried alone across the located
obstruction, and it is blocked if its motion carries the level outward
there. A periodic lockout therefore stops a long crank request at its
first closing contact even when the requested endpoint lies in a later
open window, with no hidden splitting of the request and no cap of one
turn. The remainder of a blocked request is discarded; relief does not
resume it, and the caller issues a new command. Under a time drive only
the pushing relation stops, and elapsed time and unrelated drives
continue. Two limits remain. A forbidden interval that fits entirely
between two of the 64 samples can be missed. And an obstruction that
needs several inputs together, none of which pushes alone, is refused
transactionally rather than resolved.

Where the threshold a coordinate lands on is itself moving, because
another part carries it, the landing is oriented by the two parts'
relative motion, not by the driven part's own direction; a threshold that
overtakes a part travelling the other way is still found. Two parts that
follow one another exactly, one carrying the other's contact level, are
recognised as such by an exact check of the affine law between them, so
a rounding residue of a few ulps is not mistaken for a departure. Neither
adds a tolerance: a nonzero relative motion, however small, is real.

The stop's fraction is exact wherever every edge between the pushing
inputs and the stopped coordinate is affine or piecewise affine; for a
curved upstream edge the stopped coordinate is still committed at its
bound exactly while the group's other coordinates stop on the linearized
path. A coordinate that leaves its range and returns within one tick is
not stopped; it cannot happen where the determiner is affine, and
elsewhere the answer is a smaller ``dt``. A ``Driver``'s own ``range`` is
untouched by all of this: it is presentation, and a machine driven past
its declared travel is a crash a simulation must be able to show.

Snapshot, restore, reset, record
--------------------------------

``sim.snapshot()`` is a value: the bank, the tick, ``dt``, the active
commands and the program's identity. ``sim.restore(snapshot)`` puts the
run back, refusing a snapshot over a different machine or ``dt``;
``sim.reset()`` restores ``sim.initial``. Recording is explicit and
bounded: ``record=None`` keeps nothing, ``record=64`` keeps rings of the
most recent sixty-four ticks in ``sim.trajectory``, of located crossings
in ``sim.crossings`` (the relation, the coordinate, the primitive, the
surface and the fraction of the tick) and of stops in ``sim.stops`` (the
coordinate, which bound, its evaluated value, the fraction and the inputs
blocked). ``every()`` sees each tick as it happens without a recording.

What a running root refuses
---------------------------

Each by name: a law written over Python's ``math`` rather than
``machinome.math``; a relation into a banked coordinate whose source is a
plain port an author's ``simulate()`` binds; an author's ``simulate()``
that binds a run-owned coordinate unconditionally; a law that could only
ever jump (``floor(turns)`` alone), because every jump is subtracted; a
jumping law whose driven ends are all intermediates, which cannot retain
a history; a law that reads the coordinate it drives continuously; a root
driver named like a joint anywhere in the tree (``turn`` beside
``plug.turn``); a ``repeat()`` child that owns a joint, because
``drivers-0`` is not a legal id. A refused tick commits nothing, and the
commands that moved an input in it retire ``refused``.

``sim.stops`` entries name the blocked driver ids in ``inputs`` and, in a
separate ``time_drives`` tuple, the blocked time-drive relations.

What it publishes
-----------------

A running root's document declares version 11, or 12 when its program
carries a ``Follow`` edge, and carries a ``program``
beside the geometry: the coordinate table with each bank id's kind, rest
value, unit and domain, the compiled edges in program order with their
expressions and jump plans, the candidate table of which inputs reach
what, the program identity and the clock name. Every joint's placement is
published as its own coordinate's id, so a consumer poses the geometry
from a bank it committed rather than from the law read absolutely, which
is the whole difference between a machine that accumulates and one that
snaps back. The model's ``self.time`` publishes as the free name ``time``
bound to elapsed simulation seconds. A tree that declares controls
carries a ``controls`` table beside ``instructions``, additively. A
program with time-driven relations lists them as ``program.time_drives``,
each naming the edge that reads ``time``. Source-timing semantics participate
in the program identity: endpoint-era snapshots refuse restore into newly
compiled programs before changing state. Re-export with the corrected
producer and use a viewer supporting its version; do not lower the document
version manually. Posed, looping and clocked version selection is unchanged.
:doc:`publishing` has the version table.
