Three ways a machine runs
=========================

Everything a machine does at an instant is a pose: the tree enumerated
with its inputs bound. What differs between machines is what they keep
between instants, and the framework has three answers, selected by what
the root declares.

.. list-table::
   :header-rows: 1
   :widths: 18 30 26 26

   * - Machine
     - Declares
     - Simulation
     - What is kept
   * - **Posed**
     - nothing, or ``Time(loop=)``
     - ``Sim(machine, dt=0.02)``
     - nothing: the pose follows the current inputs
   * - **Running**
     - ``time = Time.running()``
     - ``Sim(machine, dt=0.02)``
     - every driver and every joint coordinate, moved by increments
   * - **Clocked**
     - a ``State`` anywhere in the tree
     - ``Sim(machine)``
     - the declared states, written at events; a clock under ``Time.elapsed()``

Posed
-----

A posed machine is a function of its inputs. Ask for a crank of 720 and
the drums stand where two turns put them, whatever happened before. Its
drivers are sliders, its absolute instructions are buttons, and its
timeline is the looping ``$t`` of :doc:`/howto/timeline`, with
``Time(loop=)`` giving the loop a duration in seconds.

``Sim(machine, dt)`` steps it on integer ticks: ``sim.time`` is ``tick *
dt``, and an instant that is not a whole number of ticks is refused.
``sim.at(t).trigger(name)`` and ``sim.at(t).run(callable)`` schedule
actions (those due at the current tick fire before the first step);
``sim.every(period, fn, *args)`` calls a function on a cadence, and
``sim.cadence_costs`` reports what each cost; ``sim.run(duration)``
steps, binding every driver and the clock on every tick and appending to
``sim.trajectory``. A triggered instruction ramps its targets from their
current values and lands exactly on target; an integer-typed driver ramps
integer-exactly. ``sim.state`` is the bank of driver values by qualified
id and nothing else: joints, ports and derived coordinates are recomputed
from the drivers on every tick. ``ScenarioTest`` packages the loop for a
test suite (:doc:`/tutorial/07-scenario`).

Running
-------

A running machine is operated: cranked twice, executing a program,
advanced a step at a time, and its pose depends on where it already
stood. Under ``time = Time.running()`` the simulation owns every driver
and every joint coordinate of the tree, keeps their history, and moves
them by increments through requests: ``move``, ``rate``, ``trigger``, and
the controls a reader operates on the parts. A law is integrated rather
than evaluated, a jump in it is located and subtracted, and a joint's
range is a physical stop that blocks the inputs pushing it. The clock
itself may drive a relation, for a machine that runs on its own. Both
instruction forms are buttons. :doc:`running` has the rules.

Clocked
-------

A clocked machine has a few retained values, closed-form positions
between them, and a commit of the retained values at each event: a
calculator whose registers change only at the end of a stroke. A
``State`` anywhere in the tree selects it; ``Sim(machine)`` takes no
``dt``, because there is no clock unless the root declares one, and it
takes requests, each a straight path of one input along which every
rising event is located exactly. A joint's range clips the path. An
instruction is one request over one driver, drawn by a consumer over its
declared duration. :doc:`clocked` has the rules.

The time base and the state discipline are independent
-------------------------------------------------------

Three spellings of ``time`` on the root say what ``self.time`` means, and
one declaration says what the machine keeps:

.. list-table::
   :header-rows: 1
   :widths: 30 23 23 24

   * - time base
     - no ``State``
     - a ``State``
     -
   * - undeclared
     - posed, ``$t`` from 0 to 1
     - clocked, no clock
     -
   * - ``Time(loop=seconds)``
     - posed, ``$t`` times the loop
     - **refused**: a loop replays from zero and would replay every commit
     -
   * - ``Time.elapsed()``
     - posed, indistinguishable from undeclared
     - clocked, with a banked clock
     -
   * - ``Time.running()``
     - running
     - **refused**, with its meaning named and deliberately not implemented
     -

``Time.elapsed()`` is elapsed seconds that never wrap, without the
running mechanics: it says what ``time`` means and nothing about what a
simulation owns. Declare ``Time`` only as ``time``, on an assembly, on
the root; descendants read the root's base, ``Root.time.mode`` reads
``'loop'``, ``'running'`` or ``'elapsed'``, and ``Time()`` with no base
is refused naming the spellings.

Choosing
--------

Posed answers "what does this pose look like" and "does the sequence of
inputs leave the machine clear", cheaply, on any machine. Choose running
when the machine accumulates, when a law is periodic, when a stop must
block an input, or when a reader should turn a part by hand and feel the
ratchet. Choose clocked when the machine's memory is a few values that
change at events and everything else is a function of them; it costs one
pose per request, whatever the stroke, and locates every event exactly.
The tutorial's counter is written all three ways
(:doc:`/tutorial/07-scenario`, :doc:`/tutorial/08-running`,
:doc:`/tutorial/09-clocked`), and the :doc:`examples </examples>` page
points at a real machine of each kind.
