Machinome: Source code for machines
===================================

Machinome is a Python framework for describing a whole machine in source
code. Its parts, the dimensions they share, the joints they move on, the
relations that connect one movement to another, the inputs a person
operates, and what the machine remembers belong to one description. Change
a shared dimension and every part that depends on it changes with it. Turn
a crank and the mechanism follows its declared relationships. Write a test
for the clearance that must hold through the movement, and a scenario for
the sequence of inputs that must leave the machine where the design says.

A machine's source can be posed from its inputs, run with its history
retained, or operated as a machine with memory: a printer's axes and belts,
a clock's train and escapement, a calculator's cranks and stored digits.
Simulation and tests make its behaviour inspectable and repeatable. The
optional browser viewer lets other people explore and operate the same
machine from a shared web page.

Parts can be authored in CadQuery, build123d, OpenSCAD, SolidPython or
JSCAD, imported from STEP or STL, cut from sheet profiles, or described as
flexible springs, belts and cables. Those are ways to supply the pieces.
Machinome describes how they belong together.

This is the manual for Machinome |release|, released on |release_date|.
Read :doc:`why` for the idea in one page, :doc:`install <start/install>`
to set up, then build a machine that counts in the
:doc:`tutorial <tutorial/01-part>`. The machines the framework grew on
are shown live on `machinome.org <https://machinome.org/>`_, each beside
its source; the :doc:`examples` page says what to look for there.

.. toctree::
   :maxdepth: 1
   :hidden:

   why

.. toctree::
   :maxdepth: 1
   :caption: Start

   start/install
   start/first-machine

.. toctree::
   :maxdepth: 1
   :caption: Tutorial: a machine that counts

   tutorial/01-part
   tutorial/02-input
   tutorial/03-dimensions
   tutorial/04-relations
   tutorial/05-buttons
   tutorial/06-fit
   tutorial/07-scenario
   tutorial/08-running
   tutorial/09-clocked
   tutorial/10-share

.. toctree::
   :maxdepth: 1
   :caption: How-to guides

   howto/backends
   howto/imported-parts
   howto/sheet-parts
   howto/flexible-parts
   howto/fusion
   howto/markings
   howto/repeat-and-vary
   howto/timeline
   howto/several-models
   howto/fast-tests
   howto/simulate-existing

.. toctree::
   :maxdepth: 1
   :caption: How it works

   concepts/node-tree
   concepts/rest-and-motion
   concepts/values
   concepts/joints
   concepts/relations
   concepts/execution-models
   concepts/running
   concepts/clocked
   concepts/publishing

.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/cli
   reference/api
   reference/assertions
   reference/sphinx
   reference/manuals

.. toctree::
   :maxdepth: 1
   :caption: Project

   project/status
   project/changelog
   project/upgrading
   project/contributing
