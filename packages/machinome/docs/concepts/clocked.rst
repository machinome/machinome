Clocked mechanics
=================

A machine with a few retained values, closed-form positions between
them, and a commit of those values at each event. This page states the
rules the tutorial's counter used: what a state is, what writes it, how
a request is located, how a bound clips it, and what a clocked root
declares and refuses.

States
------

.. code-block:: python

    from machinome.simulation import Driver, State

    class Counter(AssemblyNode):
        crank = Driver(default=0, unit='deg')
        units = State(default=0, range=(0, 9), dtype=int)
        tens = State(default=0, range=(0, 9), dtype=int)

``State`` takes exactly ``Driver``'s arguments with their meanings, is
declared on any assembly where a driver may be, is read ``self.units``
where a driver's value is read, enters a law as a driver's value does,
and carries a driver's instance-qualified id. Everything that differs is
about **who writes it**, and each refusal names the state:

* ``set_state`` refuses one; a state is settable only as session setup,
  through ``Sim(model, state={...})`` and ``sim.restore``.
* ``drives`` refuses one as its driven end. A state is a good **source**;
  ``units.drives(units_dial.turn, ratio=36.0)`` is how the pose is fed
  from it.
* an ``Instruction`` refuses one among its targets, and a control refuses
  one as its input.
* a state under ``Time(loop=)`` is refused, and under ``Time.running()``
  it is refused with its meaning named and deliberately not implemented.
  Under ``Time.elapsed()`` it is admitted.
* a state no committing relation writes is refused at construction.

The verb that writes it
-----------------------

.. code-block:: python

    def strokes(sources, targets):
        return lambda crank, units, tens: floor(crank / 360)

    def advance(sources, targets):
        return lambda crank, units, tens: ((units + 1) % 10,
                                           (tens + (units == 9)) % 10)

    (crank & units & tens).commits((units, tens), at=strokes, law=advance)

``commits`` sits beside ``drives``, on the same ``&`` groups, and its two
factories follow the law-factory protocol: each is called once at
realization with the realized owners and returns a callable over the
sources' values in written order. Every target is a ``State``; every
source is a ``Driver``, a ``State`` or, under ``Time.elapsed()``, the
clock. A port, a joint or a derived coordinate as a source is refused
saying to name the drivers and states the port follows. A source group
may name a target of the same relation, which is a read of that target's
value before the event; the Curta's clearing threshold reads the digit it
clears.

* ``at`` is exactly **one jump node**: ``floor``, ``ceil``, ``sign`` or a
  comparison. Every **rising** step of it along a request's path is one
  event; a mechanism that commits on the other edge negates its level.
  A sum of jumps, bare arithmetic or ``a % b`` is refused: one event is
  one surface family, and two are two relations.
* ``law`` is evaluated at that one point and never integrated, so every
  jump primitive in it means what it says: ``floor(crank / 360) % 10`` is
  a digit. The ``%`` is Python's floored remainder, and the published
  document says so.
* both read and write **native** values. A ``dtype=int`` state takes the
  nearest whole native unit, rounded once, half to even.
* **several relations may write one state**, at different events. What is
  refused is two answers at one landing: two relations writing one state
  at one landing refuse the whole request naming the state, both
  relations and the landing.
* a relation whose every source is a state is refused at construction:
  nothing a request moves enters its level, so it could never fire.

A request, not a tick
---------------------

.. code-block:: python

    sim = Sim(machine)                  # no dt: there is no clock
    request = sim.move('crank', by=3600.0)

    len(request.commits)                # 10
    sim.state['tens']                   # 1

``Sim(model)`` takes no ``dt``, and a ``dt`` over a clocked root is
refused by name. Construction poses the tree once and holds a bank of
every driver and every state by qualified id; joint coordinates and ports
are not in it, being what the enumeration recomputes from it on every
pose. A request moves **one** declared driver along a straight path in
design units, with every other bank value standing, and returns a
``Request``: ``input``, ``by`` or ``to``, ``origin`` and ``end`` (verbatim
from the bank, in native units), ``admitted`` (design units),
``commits`` in path order, each with its ``fraction``, the input's
``value`` there and the ``targets`` written, and ``stops``.

Events are located **exactly**: an affine level's surfaces by one
division, a kinked level cut at its own breakpoints and each piece solved
the same way, a curved level refused at construction naming the driver
and the primitive. The landing is the nearest representable value on the
far side of the surface, decided by evaluating the branch there and never
by comparing a float to the surface, and that one value serves both the
event's reads and the resumed path, so no event fires twice. Two
crossings are one event exactly when their landings are the same float,
so ten requests of one revolution give the events one request of ten
gives. Every relation firing at one event reads the bank as it stood
before it, so declaration order is not observable. More than a thousand
events of one relation in one request is refused, saying to split the
request.

Between events nothing is retained; a request touches the tree once, at
its end, so it costs about what one pose costs and a commit costs
microseconds. A request is **atomic**: a refused one, a raising law, a
conflict, a bound violated at its end, a final pose the tree refuses,
leaves the bank, the tree and the record as they stood.

A bound stops a request
-----------------------

Under a clocked root a joint's declared ``range`` is a physical stop on
the request path: the travel is clipped to the largest fraction at which
every bound is still satisfied, the driver lands there, and events are
located on the clipped path only.
A range an ancestor adds to a nested joint
(:ref:`ancestor-joint-constraints`) is intersected with the joint's own
and clips the same way; it uses the same solver and is refused for the
same curved levels.

.. code-block:: python

    request = sim.move('lift', by=20.0)

    request.admitted                    # 9.0
    request.stops[0].coordinate         # 'plate.lift'
    request.stops[0].side               # 'high'
    request.stops[0].bound              # 9.0

Each ``Stop`` names the bounded coordinate, the side, the bound as it
evaluated at the landing, the coordinate's value there, the input's value
and the fraction of the requested travel. A request stopped at **zero**
travel is admitted, not refused: it moves nothing, fires nothing and
reports its stop, which is what an interlock does.

At construction the simulation composes, for every bounded coordinate and
every coordinate a ``Bound`` reads, one expression chain over the bank by
substitution through the relations the rest render resolved: wirings,
derived coordinates, ``law=`` relations, intermediate ports. A ranged
coordinate nothing binds is admitted as a constant; a ranged coordinate
the author's ``simulate()`` binds by hand is refused at construction (the
guarded rest default falls on that side, because the framework cannot
tell a guard's constant from a computed pose; state the relation that
moves the coordinate, or drop the range). A chain through a law that is
not an expression, a ``Bound`` whose reads no chain reaches, a level the
moving driver curves, or a free name surviving the chain is refused
naming the joint, the side and where the chain broke.

The bound's own coordinate takes the value it held when the request
**started**, one number for the whole request, while each ``reads=``
coordinate takes its value along the path. That is the ratchet: the floor
is the last seated tooth, giving one tooth of backlash whether the
reverse is one long request or ten short ones. A part that may not move
while another is off rest is a **freeze**, stated by letting both bounds
read the coordinate's own committed value:

.. code-block:: python

    def rest(turn):
        return turn - 360 * floor(turn / 360) < 1

    knob = Selector(travel=Prismatic(
        axis=(1, 0, 0), unit='mm',
        range=(Bound(lambda travel, turn: travel * (1 - rest(turn)),
                     reads=(crank_dial.turn,)),
               Bound(lambda travel, turn: travel + (54 - travel) * rest(turn),
                     reads=(crank_dial.turn,)))))

At rest the pair is ``(0, 54)`` and the knob is free; off rest both
bounds evaluate to what the knob held when the request started, so it may
not move in either direction while the crank runs its stroke. The clip is
computed once, over the bank the request began from, and not recomputed
between events, so one long request and two short ones split at an event
can admit different travels when a bound reads a state that event writes.
Where a commit carries a bounded coordinate out of range the request is
refused whole. A pose that is not a request, construction, ``state=``,
``restore``, is judged by the ordinary enumeration: a machine cannot be
put where it cannot be.

A button is a request
---------------------

Under a clocked root an instruction is **one request**: ``by={id:
travel}`` is ``move(id, by=travel)`` and ``targets={id: value}`` is
``move(id, to=value)``, and ``sim.trigger(name)`` makes it and returns
it. It names exactly one driver; two, none, or a state are refused at
simulation construction, so no document carries an instruction a
consumer cannot play. The declared ``duration`` means nothing to the
machine: it says how long a consumer draws the transition, walking the
input from ``origin`` to ``end`` and applying each commit at its
fraction, one pose per frame, with the machine solving once and doing no
work in the frame loop.

A machine with a clock
----------------------

Declare ``time = Time.elapsed()`` on the root and the clock joins the
bank, in seconds, starting at ``0.0``. ``sim.time``, ``sim.state['time']``,
``Sim(model, state={'time': 4.0})``, snapshots and reset all treat it as
one more banked value, and a request moves it with the same verb,
``move('time', by=seconds)``, under the same one-moving-input rule.
Elapsed seconds never reverse: a request that would move time backwards
is refused naming both instants; zero is admitted and fires nothing.

``time`` is a source of a committing relation exactly as a driver is, so
a pendulum's release is an event on the clock, located exactly because
it is affine in time. It may be named only in the class body that
declares the base; named in a body declaring ``Time(loop=)`` or
``Time.running()`` it is refused at class definition, and in a body
declaring no base Python resolves ``time`` as a module global. Nothing
stops a clock: a time request is never clipped, a coordinate a commit
carries out of range at some instant is an impossible pose and the
request is refused whole, and a compiled chain may not follow the clock.

Testing
-------

There is no ``ScenarioTest`` for a clocked machine, because it has no
cadence. The idiom is a plain ``TestCase`` driving a fresh ``Sim(model)``
per test and asserting the bank, the commits and the stops, with every
expectation computed by hand: a test that asks the law what the answer is
passes whatever the implementation did. Assert an interlock from both
sides, the travel it admits and the zero travel it admits when it holds;
assert a refusal by the name in its message (``ClockedError`` for a
construction refusal, ``JointRangeError`` for the end-of-request
judgement); assert that a refused request left the bank unchanged.
Geometry is asserted on the posed node with the ordinary assertions.

What it publishes and refuses
-----------------------------

A tree that declares a ``State`` publishes **document version 8**,
carrying ``states`` beside ``drivers`` (a state is never a handle a
person may move) and a top-level ``clocked`` object: every committing
relation with its sources, its ``at`` as one jump node and its level, one
law expression per target; every compiled constraint as its chain, bound
and jump plan; the clock name; an ``identity`` digest so a bank saved
against one machine is refused against another. The version is read off
the root's declaration and dominates: a clocked root publishes 8 whatever
else its tree holds. The build poses the initial bank, every driver and
state at its default, so a clocked model is built, tested and
photographed as any other.

Refused by name: the cadence surface (``run``, ``at``, ``every``,
``tick``, ``rate``, ``commands``, ``program``, ``crossings``), and
``time`` unless the root declares ``Time.elapsed()``; a request naming a
state, a joint or more than one input; a control under a clocked root,
which is why a version 8 document never carries a ``controls`` key; a
commit that is not a number the machine can stand at (an infinity or a
NaN refuses the whole request); a bound reading a plain port; a
broadcast ``commits`` over a ``repeat()``.
