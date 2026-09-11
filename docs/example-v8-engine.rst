.. _example-v8-engine:

=========
V8 engine
=========

The V8 engine demonstrates an assembled mechanism with rotating shafts,
reciprocating pistons, a timing drive and valves. Its nested rotations and
translations exercise the same motion in Python tests, OpenSCAD and the
browser viewer.

The valve springs are flexible parts: each spring's height follows the
valve it seats through a connected port, so the springs compress as the
engine turns. Orbit around the model and follow the motion from the crank
to the pistons and valve train.

.. solid-node:: examples/v8-engine/docs/_exports/v8-engine
   :height: 620px

You can check the project source code at its Github page: https://github.com/LibreSolid/example-v8-engine

Open the external example
=========================

From a framework source checkout with the matching preview installed:

.. code-block:: bash

   git submodule update --init docs/examples/v8-engine
   cd docs/examples/v8-engine
   solid develop

The example owns its source and tests; the framework documentation embeds
its export. See also :doc:`example-metamaquina2` and
:doc:`example-clock-01`.
