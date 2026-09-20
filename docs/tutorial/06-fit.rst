6. Prove the fit
================

The drums run on the arbor with a tenth of a millimetre of clearance,
and the post stands clear of the drums. Both are true because the
numbers say so. This chapter makes them contracts: tests that fail when
the geometry stops agreeing, proved red before they are trusted green.

Whole-machine contracts
-----------------------

``machinome new`` wrote ``counter/test_counter.py`` with two tests. Keep
them, and name the node so the runner knows which class in the module
they judge:

.. literalinclude:: counter/test_c06_fit.py
   :language: python
   :lines: 1-13

A test file beside a module is that module's **companion**; the runner
builds the model, hands it over as ``self.node``, and runs every
``test_`` method. ``assertNoSolidInterference`` walks the tree down to
the topmost rigid part on every branch and certifies that no two of
those parts share volume at the instant under test.
``assertNoDisconnectedSolids`` certifies that each of them is one body.

Prove they catch something
--------------------------

A test that has never failed is a hope. Move the post into the drums
without touching the code, from the shell:

.. code-block:: bash

    $ machinome test --set post_offset=22
    Running CounterFitTest.test_the_parts_do_not_interfere.FAIL!
    ...
    AssertionError: base should not interfere with units_drum (intersection volume 69.26840085194019)

    Ran 3 tests in 1.31 seconds: 2 passed, 1 failed

The exact kernel measured 69 cubic millimetres of shared material, and the
message names both parts. Run again without the override and the test
passes. Now it is evidence.

A fit, from both sides
----------------------

"The drums do not interfere with the arbor" is not the contract a drum
needs. A drum with a ten-millimetre bore would pass it. The contract is
that the arbor **locates** the drum: free to move within its clearance,
held beyond it.

.. literalinclude:: counter/test_c06_fit.py
   :language: python
   :pyobject: CounterFitTest.test_the_drums_run_on_the_arbor

``assertFreeWithin`` displaces the drum along the given direction, in the
drum's own frame, and requires no contact; ``assertBlockedBeyond``
displaces it further and requires contact. The pair closes the loophole
each would leave alone: a snug bore passes the first, a loose one passes
the second, only a fit passes both. Rotation is the default perturbation;
``along=`` selects a displacement instead.

Red first, again:

.. code-block:: bash

    $ machinome test --set clearance=1.0
    Running CounterFitTest.test_the_drums_run_on_the_arbor.FAIL!
    ...
    AssertionError: units_drum should be blocked displaced 0.5mm along [1, 0, 0] against handle (no intersection)

    Ran 3 tests in 1.27 seconds: 2 passed, 1 failed

One millimetre of clearance is a rattle, and the test says so.

Promote the lesson into a guard
-------------------------------

The interference test caught a post at 22 mm after building the parts.
The rule it caught can be stated before anything is built:

.. literalinclude:: counter/c06_fit.py
   :language: python
   :lines: 2-

.. code-block:: bash

    $ machinome test --set post_offset=22
    Error: Counter: a post 22.0 mm from the axis cuts into drums of radius 20.0 mm

A guard refuses what the numbers already rule out; a test finds what only
the geometry shows. Keep both. ``check()`` runs before any child is
realized; the tests run on built solids.

Which kernel decided
--------------------

Every intersection above was decided on the **exact** kernel: the drums,
the crank and the base are OCCT solids, so boundary contact is exactly
empty and there is no tolerance anywhere. A part that has no exact
geometry, an imported STL or an OpenSCAD part, is compared on its mesh.
A whole run can be switched to meshes for speed, and
:doc:`/howto/fast-tests` shows when and how; a release run stays exact.

Next: :doc:`07-scenario`.
