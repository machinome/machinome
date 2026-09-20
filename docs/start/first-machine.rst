Your first machine
==================

Ten minutes: a project, one part, one input, and a slider in the browser
that moves it.

Create a project
----------------

.. code-block:: bash

    $ machinome new myproject
    $ cd myproject

``machinome new`` writes a package with one starter part, a companion test
file with two whole-model contracts, a ``.gitignore`` and a
``pyproject.toml`` manifest naming the model:

.. code-block:: toml

    [tool.machinome]
    model = "myproject.myproject:Myproject"

Start the development loop:

.. code-block:: bash

    $ machinome develop

and open http://localhost:8000. The viewer shows the starter part, a box
with a hole. Every time you save a source file, the parts that changed are
rebuilt and the page reloads. Leave it running.

Give it an input
----------------

The starter part is written in SolidPython and needs OpenSCAD. Replace the
whole of ``myproject/myproject.py`` with a CadQuery block and an assembly
that lifts it:

.. literalinclude:: ../tutorial/counter/first_machine.py
   :language: python
   :lines: 2-

Then point the manifest at the assembly:

.. code-block:: toml

    [tool.machinome]
    model = "myproject.myproject:Lifter"

Save. The viewer now shows the block and a ``lift`` slider. Drag it and
the block rises.

Three things happened in those twenty lines:

* ``Block`` is a **leaf**: its ``render()`` returns a solid from a
  modelling library, and the framework builds the part from it.
* ``Lifter`` is an **assembly**. ``block = Block()`` declares a child; the
  assembly places it. ``lift`` is a **driver**: a named input with a
  default, a range for the slider, and a unit.
* ``simulate()`` is where the input is read. It runs on every instant with
  ``self.lift`` bound to whatever the slider holds, and the translation
  it applies is that instant's motion. The expression travels into the
  published model unevaluated, so dragging the slider moves the block
  without running any Python.

The starter test file still works: its two contracts check that every
printed piece is one body and that no two pieces interfere. Run them:

.. code-block:: bash

    $ machinome test

Look in the build directory
---------------------------

``_build/`` holds what the build produced: an STL per part, a ``.brep``
beside it with the exact geometry of an OCCT-backed part, and the
``viewer.json`` document that the viewer reads. Nothing in it is edited
by hand.

Next
----

The :doc:`tutorial </tutorial/01-part>` builds a machine that counts: a
crank, two digit drums, the relations between them, the tests that prove
the fit, and the memory that makes it a counter. Each chapter ends with a
machine you can drive.
