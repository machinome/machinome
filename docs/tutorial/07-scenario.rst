7. Step it through a move
=========================

Chapter six judged the counter at rest. A machine is used in motion:
does the arm clear the post on the way round, at every angle, and if it
did not, at which angle does it hit? A **scenario** answers that by
stepping the machine deterministically in Python.

An instruction to step
----------------------

A scenario triggers instructions, so give the counter the move a counter
makes. Chapter five noted that a relative instruction is not a button on
a posed machine; it is exactly right for a scenario:

.. literalinclude:: counter/c07_scenario.py
   :language: python
   :lines: 2-

The scenario
------------

Create ``counter/test_counter.py`` beside the fit tests, or add to it:

.. literalinclude:: counter/test_c07_scenario.py
   :language: python
   :pyobject: CounterScenarioTest

A ``ScenarioTest`` declares the node it steps, the step ``dt`` in seconds,
and whether the scenario needs meshes. ``self.simulation()`` gives every
test a fresh ``Sim`` over a fresh machine at the declared driver
defaults, so two scenarios share nothing.

Read the first test as a script. ``sim.at(0.0).trigger('Turn once')``
schedules the instruction for the first tick. ``sim.every(0.1, ...)``
calls an assertion on a cadence, every five ticks here, with whatever
arguments follow it. ``sim.run(2.0)`` steps a hundred ticks. Each tick
binds every driver and the clock, so the whole tree poses numerically,
and the cadence check runs against that pose. At the end the crank stands
at 360 exactly, because a ramp lands on its target, and the check ran
twenty times.

The instants are **integer ticks**: ``sim.time`` is ``tick * dt``, and an
instant that is not a whole number of ticks is refused rather than
rounded. That is what makes a scenario deterministic on every machine.

Prove the check has teeth
-------------------------

The second test builds a counter whose arm is too low, ``arm_height=34``
against a post 36 high, and runs the same move under the same cadence. It
must fail, and it must fail where the arm meets the post. It does, at tick
70, which is 252 degrees of crank:

.. code-block:: text

    AssertionError: base should not interfere with handle (intersection volume 0.021128907240890615)

The test does not merely expect an error; it asserts the tick. A scenario
that only ever passes is not evidence. Write the run that must fail and
assert where it fails; then the passing run means something.

Run both:

.. code-block:: bash

    $ machinome test
    Ran 5 tests in 2.31 seconds: 5 passed, 0 failed

One class, both runners
-----------------------

A ``ScenarioTest`` is a ``TestCase``. As a companion test it runs under
``machinome test`` like the fit tests; imported into a pytest module it runs
under plain ``pytest``, unmodified. Under the CLI ``self.node`` is the
built instance the runner hands over; under pytest it is the declared
class and the scenario builds it.

Choosing ``dt``
---------------

``dt`` is part of the scenario's meaning, not a tuning knob. The crash
test asserts tick 70 *because* a step of 0.02 s makes the crank travel
3.6 degrees per tick. Pick the step that resolves the finest motion the
scenario judges, declare it on the class, and let the tick arithmetic be
exact from there.

What ``sim.state`` holds
------------------------

For this counter, ``sim.state`` is the bank of driver values by qualified
id: ``{'crank': 360.0}``. The drums' angles are not in it; they are
recomputed from the crank on every tick, and a scenario reads them off the
posed tree. A machine that keeps its own history banks more than its
drivers, and that is the next chapter.

Next: :doc:`08-running`.
