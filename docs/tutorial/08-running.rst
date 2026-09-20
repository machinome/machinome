8. A machine with history
=========================

Everything so far poses the counter from the crank's value. Ask for a
crank of 720 and the drums stand where two turns put them, whatever
happened before. A real counter is operated: turned, and turned again,
and its crank has a ratchet so it cannot be turned back. This chapter
gives the counter history.

Declare the time base
---------------------

.. literalinclude:: counter/c08_running.py
   :language: python
   :pyobject: Counter
   :end-before: shaft = Length

``time = Time.running()`` on the root selects **running mechanics**. A
simulation over this root owns every driver and every joint coordinate of
the tree, keeps their history, and moves them by increments: a crank
turned ten degrees twice leaves the arbor at twenty, not back at ten.

The ratchet
-----------

A joint's ``range`` is a physical stop under a running root. The crank's
ratchet has ten teeth per turn; it may not turn back past the last tooth
it passed:

.. literalinclude:: counter/c08_running.py
   :language: python
   :pyobject: Crank

Either bound may be a number, ``None`` for no bound on that side, or a
function of the joint's own coordinate. ``36 * floor(turn / 36)`` is the
last seated tooth: the lower bound moves up with the crank and never down.
The function is compiled once, like a law, and evaluated once per tick
from the committed value, so within a tick the bound is a number.

Commands, not bindings
----------------------

Everything else in the class is chapter seven's. The instructions and the
new ``controls`` table:

.. literalinclude:: counter/c08_running.py
   :language: python
   :start-at: instructions = {
   :end-before: def render
   :dedent: 4

A running simulation takes **requests** rather than snapshots. Under a
running root both instruction forms publish, so ``Turn once`` is a
button, and a **control** puts the request on the part: ``Turn(handle,
crank)`` lets a reader drag the crank itself, and ``Button(handle, 'Turn
once')`` makes a click on it one turn. A control moves nothing by itself;
it names a request the run already accepts, so what a drag admits is
exactly what a command would.

.. machinome:: /_exports/counter-08
   :height: 420px

Press **Turn once** ten times, or drag the crank round. Then press **Back
a bit**: the panel reports it blocked, having admitted nothing, because
the crank stands on a tooth.

The same in Python:

.. literalinclude:: counter/test_c08_running.py
   :language: python
   :pyobject: RunningCounterTest

``sim.move('crank', by=30.0, duration=0.5)`` requests travel;
``sim.trigger(name)`` makes the request an instruction states and returns
its command handles. Every handle reports ``status`` (``active``,
``completed``, ``blocked``, ``refused``, ``cancelled``) and the travel it
``admitted``. A blocked command reports what it made before the stop and
never resumes: the caller decides what to do next.

Read the second test as a mechanism. After a full turn the crank stands
on a tooth, so a reverse request admits nothing. Thirty degrees forward,
then a hundred back: blocked at the tooth, having admitted exactly minus
thirty. One tooth of backlash, and no more, whether the reverse is one
request or ten.

What the run integrates
-----------------------

The laws are chapter four's, unchanged, and that deserves a sentence.
``window(60)`` says where the drum *is* for a crank angle; after a whole
revolution it reads what it read before. Running, the law is
**integrated**: the run locates every crossing of ``floor`` inside a
tick, subtracts the jump, and adds the continuous travel, so ten turns
leave the units drum at 360 and the tens drum at 36. A jump never moves a
part; a law that could only ever jump is refused, because it states
arithmetic and not a mechanism. :doc:`/concepts/running` states what is
solved exactly, what is searched, and what the run refuses.

``sim.state`` is now the whole bank: the crank *and* every joint
coordinate, by qualified id. ``sim.snapshot()`` captures it, with the tick
and the active commands; ``sim.restore()`` puts the run back;
``sim.reset()`` returns to the rest pose.

Next: :doc:`09-clocked`.
