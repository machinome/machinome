.. _example-metamaquina2:

=============
Metamaquina 2
=============

The `Metamaquina 2 <https://github.com/machinome-foundry/Metamaquina2/tree/c916f9b5f09ba27faaab9225fff0cdf6342fc00c>`_
is a real product: a Brazilian open-hardware RepRap 3D printer, originally
authored in OpenSCAD. Its Machinome model reads the original ``.scad``
sources in place, each leaf reaching one OpenSCAD module, and the
simulation layer adds a control surface and motion to the existing
design, without changing one of its files. It is the worked case of
:doc:`howto/simulate-existing`.

The machine declares ``x``, ``y`` and ``z`` drivers and machine-level
instructions (``Rest``, ``CenterX``, ``PresentBed``, ``HomeZ``), so the
model below shows buttons at the top layer and sliders down the
breadcrumb. Its filament path, GT2 belts, bed springs and extruder idler
spring are flexible parts whose shape follows the machine's state. It is
a **posed** machine: ask for an axis position and the printer stands
there.

.. machinome:: examples/metamaquina2/docs/_exports/metamaquina2
   :height: 620px

Press **PresentBed** and step into ``x_axis`` on the breadcrumb to drive
the carriage by hand.

Open the example
================

From a framework source checkout:

.. code-block:: bash

   git submodule update --init docs/examples/metamaquina2
   cd docs/examples/metamaquina2
   machinome develop

This example needs OpenSCAD, because its parts read the original
``.scad`` sources. The sources and the simulation stay in the printer's
own repository.

Licences
========

The Metamaquina 2 design keeps the GNU General Public License grants its
source files state, version 3 or later for the main assembly and the
gears, with their authors' notices. The simulation layer is Machinome
Foundry work in two parts, each Python file saying which. The loaders,
probes, base classes, helpers and tests are original software under the
GNU Affero General Public License, version 3 or later. The modules that
integrate or adapt the printer's own geometry, placement and assembly are
under the GNU General Public License, version 3 only, so that the design
they carry keeps its terms. The `Foundry repository
<https://github.com/machinome-foundry/Metamaquina2>`_ holds the split in
its ``NOTICE`` and ``CREDITS``. Machinome and its own tutorial source
remain Apache-2.0.
