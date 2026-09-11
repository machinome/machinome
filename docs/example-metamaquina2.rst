.. _example-metamaquina2:

=============
Metamaquina 2
=============

The `Metamaquina 2 <https://github.com/LibreSolid/Metamaquina2>`_ is a
real product: a Brazilian open-hardware RepRap 3D printer, originally
authored in OpenSCAD. Its Solid Node model reads the original ``.scad``
sources in place, each leaf reaching one OpenSCAD module through solid2.
The simulation adds controls and motion to that existing design.

The machine declares ``x``, ``y`` and ``z`` drivers and machine-level
instructions (``Rest``, ``CenterX``, ``PresentBed``, ``HomeZ``), so
the widget below shows buttons at the top layer and sliders down the
breadcrumb. Its filament path, GT2 belts, bed springs and extruder
idler spring are flexible parts whose shape follows the machine's
state.

.. solid-node:: examples/metamaquina2/docs/_exports/metamaquina2
   :height: 620px

Open the external example
=========================

From a framework source checkout with the matching preview installed:

.. code-block:: bash

   git submodule update --init docs/examples/metamaquina2
   cd docs/examples/metamaquina2
   solid develop

This example needs OpenSCAD because its parts read the original
``.scad`` sources. Those sources and the simulation stay in the
printer's own repository.

See also :doc:`example-v8-engine` and :doc:`example-clock-01`.
