Machinome: Source code for machines
========================================

Machinome is a Python framework for describing a whole machine in source
code. Its parts, dimensions, connections, movement and operating rules
belong to one description. Change a shared dimension and the parts that
depend on it change together. Turn a handle and the mechanism follows its
declared relationships. Write a test for the clearance that must hold
through the movement.

A machine's source binds its pieces into a working whole. It can describe
a printer's axes and belts, a clock's gear train and escapement, or a
calculator's cranks and stored digits. Named inputs let a person operate
the model; simulation and tests make its behaviour inspectable and
repeatable. The optional browser viewer lets other people explore and
operate the same machine from a shared web page.

Parts can be authored in CadQuery, build123d, OpenSCAD, SolidPython or
JSCAD, imported from STEP or STL, cut from sheet profiles, or described as
flexible springs, belts and cables. These are ways to supply the pieces;
Machinome describes how they belong together.

Start with the :doc:`quickstart`, then follow the tutorial: model a part,
assemble a base and pointer, animate it, and test a pin's fit. Continue
with shared parameters, joints, inputs and scenarios. The three
:doc:`example machines <examples>` keep their complete designs in their
own repositories.

.. note::

   This is the **Machinome 0.7 manual (release in preparation)**. Machinome is the
   continuation of **solid-node 0.6.0**; the project and GitHub organisation
   have been renamed to avoid confusion with Tim Berners-Lee's Solid
   project. The new name has no affiliation with that project.
   See :doc:`upgrading` for the migration and :doc:`quickstart` for
   source installation while the framework and matching viewer await
   publication.

.. toctree::
   :maxdepth: 1
   :caption: Getting started

   why-machinome
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
   markings
   node-tree
   expression-graphs
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
