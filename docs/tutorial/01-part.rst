1. A part
=========

The machine this tutorial builds is a tally counter: a crank on a base,
two digit drums on the crank's arbor, and a post to read them against.
Turn the crank once and the units drum advances one digit; turn it ten
times and the tens drum advances one. By chapter nine the counter
remembers its count between strokes. Every chapter ends with a machine
you can drive in the browser, and every chapter's code is real source in
the framework's repository, built and tested with it. When you are done,
the `Machinome Foundry <https://github.com/machinome-foundry>`_ has real
machines built the same way.

Start from a fresh project, as in :doc:`/start/first-machine`:

.. code-block:: bash

    $ machinome new counter
    $ cd counter
    $ machinome develop

The base
--------

The first part is the base: a plate with a bore through it for the
crank's arbor, and an upright post beside the bore. The post is where a
reader will read the drums. Replace ``counter/counter.py`` with:

.. literalinclude:: counter/c01_part.py
   :language: python
   :lines: 2-

and point the manifest at it:

.. code-block:: toml

    [tool.machinome]
    model = "counter.counter:Base"

Save, and the viewer shows the plate:

.. machinome:: /_exports/counter-01
   :height: 360px

What a leaf is
--------------

``Base`` is a **leaf node**: one part, built by one modelling library. A
leaf has one job, ``render()``, which returns a solid in that library's
own vocabulary. Here it is a CadQuery ``Workplane``: a box moved down so
its top face is at ``z = 0``, a hole cut through it, and a post united to
it. The framework tessellates the solid into an STL for the viewer and
keeps the exact geometry in a ``.brep`` beside it for tests.

Leaves come in several kinds, one per modelling technology, and they all
work the same way from the outside. ``CadQueryNode`` and ``Build123dNode``
are exact and need nothing installed beyond the package. ``Solid2Node``
and ``OpenScadNode`` are OpenSCAD's, ``JScadNode`` is JSCAD's, and three
more bring in parts from files or describe parts that flex.
:doc:`/howto/backends` puts the same part in each. The tutorial stays with
CadQuery so that nothing here needs OpenSCAD.

``color`` is a class attribute the viewer and the exports honour. A hex
string; anything else is refused.

Two coordinates worth noting now, because the crank will use them: the
bore is at the origin, and the plate's top face is at ``z = 0``. A part's
own geometry is written in its own frame; where it sits in the machine is
the assembly's business, in the next chapter.

Next: :doc:`02-input`.
