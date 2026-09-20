.. _example-pascaline:

================
Pascaline module
================

A simulation of `José Campos's modular mechanical calculator
<https://www.printables.com/model/28807-mechanical-calculator-modular-design>`_,
a Pascaline built from identical decimal columns, using its downloaded
meshes with project-authored corrections to the carry tooth layers and
the number drum's mounting phase. The model is three alternating columns
with their top covers, and it **runs**: the root declares
``Time.running()``, so the simulation owns every dial and every arbor of
the tree and moves them by increments. A dial asked to add a digit twice
leaves its register at two digits rather than back at one, and a column's
carry accumulates in the column above it.

Each column's input arbor declares its **ratchet stop**: the last seated
tooth is a bound on that arbor's own coordinate, so forward entry is free
and ``Back one`` is reported blocked, having admitted whatever fraction
of a digit the dial had gained past the tooth. The number windows start
with nine above and zero below, so the upper subtraction row reads the
digitwise complement of the addition row.

.. machinome:: examples/pascaline/docs/_exports/pascaline
   :height: 620px

Press **Add one** nine times and read 009 on the addition row. Press it
once more: units rolls to 0 and tens advances to 1. Each dial is itself a
**control**: clicking a dial is that column's ``Add one``, ``Add ten`` or
``Add hundred``, and dragging one enters a digit for every 36 degrees it
is swept. Drag it the other way and the page answers ``blocked after 0
digit`` with the drum standing still.

What it shows
=============

* Every relation into a coordinate the run owns is stated into a joint
  coordinate: the dials into each column's drum arbor, the carry from the
  column below's arbor into this one's, with the readouts following.
* The corrected carry uses forty-tooth receiving rings and a conjugate
  intermittent cam, advancing the next column by one digit during 9 to 0.
* The ratchet's blade is a flexible part, explicitly authorised by the
  project owner, and the untouched original STL stays as its reference.
* A version 5 document publishes the four instructions as buttons, the
  three arbors' seated-tooth bounds and the six controls that put those
  requests on the dials, and the project's browser test drives that page
  in headless Chromium on the real meshes.

This validates a corrected simulation, not the performance of a printed
original. End covers remain unplaced, and the ratchet is prescribed
kinematics with a reverse-travel bound, not a force model.

Open the example
================

.. code-block:: bash

   git submodule update --init docs/examples/pascaline
   cd docs/examples/pascaline
   python scripts/download_sources.py
   python scripts/prepare_sources.py
   machinome develop

The repository commits no source geometry: the two scripts download the
pinned Printables files, with no login, and extract the 3MF objects in
their own frames.

The `Foundry repository
<https://github.com/machinome-foundry/Pascaline-module/tree/576dc6b>`_
holds the model, its tests and its own OpenSpec records at the revision
this page shows.

Licences
========

The simulation's software and documentation are Machinome Foundry work
under the GNU Affero General Public License, version 3 or later. The
original geometry is José Campos's, published on Printables under a
Creative Commons Attribution licence whose version the listing does not
state; the project's ``NOTICE`` carries the attribution, the repository
commits none of the meshes, and no other terms are claimed for them. The
corrected rings and carry cam the simulation generates keep the hubs,
bores and journals of the original parts, so they carry the same
attribution terms rather than the software grant.
Machinome and its own tutorial source remain Apache-2.0.
