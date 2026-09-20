.. _examples:

========
Examples
========

Three real machines, one for each way a machine runs. Each has its own
page and one live model, and each comes from the **Machinome Foundry**,
the GitHub organisation at `github.com/machinome-foundry
<https://github.com/machinome-foundry>`_ where simulations of open-source
machines built with Machinome are kept: printers, calculators, clocks,
robot arms and hands, actuators, lab equipment and more, each beside the
design it simulates, each stating the design's own licence and the
simulation's. Browse it for a machine like the one you are building.
The three here are machines to explore after the tutorial, not code to
copy into a first project.

.. toctree::
   :maxdepth: 1

   example-metamaquina2
   example-pascaline
   example-curta

:doc:`example-metamaquina2`
   A **posed** machine. An open-hardware RepRap 3D printer whose original
   OpenSCAD design is read in place; three axis drivers, machine-level
   instructions, and belts, springs and filament as flexible parts.

:doc:`example-pascaline`
   A **running** machine. Three decimal columns of a modular Pascaline
   with a corrected carry; the simulation owns every dial and arbor,
   each input arbor has a ratchet stop, and every dial is itself a
   control a reader turns by hand.

:doc:`example-curta`
   A **clocked** machine. A 3x-scale Curta Type I whose setting levers,
   crank, carriage and clearing ring make requests, whose registers are
   retained states written at events, and whose interlocks are bounds
   that hold one part while another is off rest.

The framework tracks the three Foundry repositories as Git submodules and
builds their exports when this manual is built; it does not copy their
design source. Each page names the pinned revision it shows and the
licences that apply, as the Foundry's licensing policy records them: the
simulation software the Foundry writes is under the GNU Affero General
Public License, version 3 or later, wherever the design's own terms permit
it, and a design keeps its own licence.
