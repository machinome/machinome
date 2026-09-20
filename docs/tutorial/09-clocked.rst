9. A machine that remembers
===========================

A running counter keeps every coordinate's history and integrates every
law on every tick. A tally counter needs less than that and more: two
digits, retained between strokes, and a pose that is a plain function of
the crank and those digits. That is a **clocked** machine, and it is the
last thing the counter becomes.

Declare what is remembered
--------------------------

Drop ``time = Time.running()`` and declare the memory beside the driver:

.. literalinclude:: counter/c09_clocked.py
   :language: python
   :start-at: crank = Driver
   :end-at: tens = State
   :dedent: 4

A ``State`` takes exactly a ``Driver``'s arguments with their meanings, is
read as ``self.units`` where a driver's value is read, and carries the
same kind of qualified id. Everything that differs is about **who writes
it**: no slider, no ``set_state``, no instruction. A state is written by
the machine, at an event, through a committing relation.

The pose reads the memory
-------------------------

.. literalinclude:: counter/c09_clocked.py
   :language: python
   :start-at: def phase
   :end-before: class Counter

``units_pose`` is chapter four's window over the crank's phase within its
current turn, plus thirty-six degrees per remembered digit. ``tens_pose``
is the same window, gated so that it moves only while the units drum is
carrying a 9. A law over several coordinates joins them with ``&`` and
takes one argument per source, in the written order.

``strokes`` and ``advance`` are the **event** and the **write**.
``floor(crank / 360)`` rises once per completed turn; ``advance`` returns
the two digits after that turn, the tens carrying when the units were 9.

.. literalinclude:: counter/c09_clocked.py
   :language: python
   :start-at: crank.drives(handle.turn)
   :end-at: commits(
   :dedent: 4

``commits`` sits beside ``drives``. Its ``at`` is exactly one jump
node, ``floor``, ``ceil``, ``sign`` or a comparison, and every rising
step of it along a request is one event. Its ``law`` is evaluated at that
one point and never integrated, so ``% 10`` there means what it says.

The whole machine:

.. literalinclude:: counter/c09_clocked.py
   :language: python
   :pyobject: Counter

A request, not a tick
---------------------

.. literalinclude:: counter/test_c09_clocked.py
   :language: python
   :pyobject: ClockedCounterTest

``Sim(Counter())`` takes no ``dt``: there is no clock. A request moves one
driver along a straight path, and every rising step of every ``at`` along
that path is located exactly, by one division on an affine level, never
searched. Twelve turns in one request commit twelve events and leave the
digits at 1 and 2. Ninety-nine plus one carries to zero-zero in one event
that writes both digits. A request touches the tree once, at its end, so
it costs about what one pose costs.

The ratchet is still a stop. Under a clocked root a joint's ``range``
clips the request's path before any event is located: a reverse stroke
from a tooth admits nothing, reports the stop, and leaves the bank where
it was.

A button is a request
---------------------

.. code-block:: python

    instructions = {
        'Turn once': Instruction(by={'crank': 360.0}, duration=2.0),
    }

Under a clocked root an instruction is one request and names exactly one
driver. ``sim.trigger('Turn once')`` makes it and returns it, with both
ends of the path and every commit in path order. The ``duration`` means
nothing to the machine; it says how long a viewer **draws** the stroke,
walking the crank from origin to end and applying each commit at its
fraction, one pose per frame, with the machine doing no work in the frame
loop.

.. machinome:: /_exports/counter-09
   :height: 420px

Press **Turn once**: the crank turns over two seconds, the units drum
steps in the last sixty degrees, and the ``units`` readout changes at the
end of the stroke. Nudge the crank backwards: blocked at the tooth. Press
ten times and watch the carry.

What this model is
------------------

The counter is now three things at once, and each is a separate,
declared choice: a machine whose parts are exact solids with tests over
them, whose pose is a function of one input and two remembered digits,
and whose memory changes only at events the machine locates exactly. It
publishes a document that carries its compiled events and constraints, so
the viewer and a Python session agree on every landing.
:doc:`/concepts/clocked` states the rules in full, including the clock a
clocked machine can declare with ``Time.elapsed()``, and
:doc:`/concepts/execution-models` puts the three models side by side.

Next: :doc:`10-share`.
