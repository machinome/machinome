Solid Node: design a machine
================================

Solid Node is a Python framework for designing machines. Describe their
parts, how they fit together, and the relationships that make them move.
Build assemblies with declared parameters, joints and mechanical
relations; operate them interactively; and test their geometry through
a movement.

Use the modelling tools that suit your design: CadQuery, build123d,
OpenSCAD, SolidPython and JSCAD, alongside imported STEP and STL parts,
sheet profiles and flexible parts. Solid Node supplies the assembly
structure, motion, tests, incremental builds and shared viewer.

Start with the :doc:`quickstart`, then follow the tutorial one change
at a time: model a part, assemble a base and pointer, animate the pointer,
and test a pin's fit. Continue with parameters, joints, controls and
scenarios. The tutorial is a small framework-owned demonstration, separate
from the three complete machines in :doc:`examples`.

.. note::

   This manual describes **0.7, in preparation**. The latest published
   framework release is 0.6.0. See :doc:`upgrading` for migration and
   :doc:`quickstart` for installation.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   why-solid-node
   quickstart
   upgrading

.. toctree::
   :maxdepth: 2
   :caption: Tutorial

   leaf-nodes
   assemblies
   animation
   testing
   declaring
   motion
   driving
   scenarios
   fusion

.. toctree::
   :maxdepth: 1
   :caption: Example machines

   examples

.. toctree::
   :maxdepth: 2
   :caption: Guides

   flexible-parts
   node-tree
   viewer
   embedding

.. toctree::
   :maxdepth: 1
   :caption: Reference

   cli
   api-reference
   status-and-roadmap
   contributing
   changelog
