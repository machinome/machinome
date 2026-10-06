=========
Machinome
=========

**Source code for machines**

.. image:: https://github.com/machinome/machinome/actions/workflows/python-app.yml/badge.svg?branch=main
   :target: https://github.com/machinome/machinome/actions/workflows/python-app.yml
   :alt: Build status

.. image:: https://img.shields.io/pypi/v/machinome.svg
   :target: https://pypi.org/project/machinome/
   :alt: PyPI version

.. image:: https://readthedocs.org/projects/machinome/badge/?version=latest
   :target: https://machinome.readthedocs.io/en/latest/
   :alt: Documentation status

Machinome is a Python framework for describing a whole machine in source
code: its parts, the dimensions they share, the joints they move on, the
relations that connect one movement to another, the inputs a person
operates, and what the machine remembers. Geometry, operating behaviour
and tests belong to one description, so a design can be inspected, changed
and checked as a whole.

A gear ratio connects the gears you see to the movement you test. An input
moves the parts it drives. A spring follows the mechanism that compresses
it. A calculator keeps its digits when the crank returns to rest. These
relationships are written in the machine's source, where a reader can
follow them, a change propagates through them, and a test holds them.

Parts are supplied in their natural form: CadQuery and build123d solids,
OpenSCAD, SolidPython and JSCAD geometry, STEP and STL files from a vendor
or an earlier design, sheet parts cut from a profile, and flexible
springs, belts and cables described with
`molejo <https://molejo.readthedocs.io>`_. Machinome describes how they
belong together.

A machine's source
==================

The manual's tutorial builds a hand-cranked tally counter: a crank on a
base, two drums on the crank's arbor, and a post to read them against.
Here is its revolution-counter stage, every moving part placed by a frame
on a frame; the framework's own test suite builds it:

.. code-block:: python

    class Drum(CadQueryNode):
        """A number drum: a ring that runs on the arbor."""

        color = '#2b2d42'

        bore = Length(8.2, min=1)

        axle = Frame()                  # the bore's line, z up

        def render(self):
            return (cq.Workplane('XY')
                    .circle(DRUM_RADIUS).circle(self.bore / 2)
                    .extrude(DRUM_HEIGHT))


    class Counter(AssemblyNode):
        """The drums follow the crank at a fixed ratio: a revolution counter."""

        shaft = Length(8.0, min=1)
        clearance = Length(0.1, min=0)
        arm_length = Length(40.0, min=10)
        arm_height = Length(40.0, min=1)
        post_offset = Length(28.0, min=1)
        post_height = Length(36.0, min=1)

        bore = shaft + 2 * clearance

        units_seat = Frame(at=(0, 0, UNITS_SEAT))
        tens_seat = Frame(at=(0, 0, TENS_SEAT))

        crank = Driver(default=0.0, range=(0.0, 3600.0), unit='deg')

        base = Base(bore=bore, post_offset=post_offset, post_height=post_height)
        handle = Crank(diameter=shaft, arm_length=arm_length,
                       arm_height=arm_height)
        units_drum = Drum(bore=bore)
        tens_drum = Drum(bore=bore)

        turn = handle.arbor.on(base.axle, Revolute())
        units = units_drum.axle.on(units_seat, Revolute())
        tens = tens_drum.axle.on(tens_seat, Revolute())

        crank.drives(turn)
        turn.drives(units, ratio=0.1)
        units.drives(tens, ratio=0.1)

        def check(self):
            if self.arm_length + KNOB_RADIUS > PLATE_LENGTH / 2:
                raise ValueError(
                    f'{self.name}: an arm of {self.arm_length} mm hangs the knob '
                    f'past the plate, which is {PLATE_LENGTH} mm long')

The dimensions the parts share sit on the assembly and are passed to the
parts that need them, ``bore`` derived once from two of them. ``crank`` is
a driver, an input with a range and a unit. ``axle`` is the drum's
connector; the three mates in ``Counter`` put the crank's arbor on the
base's bore and each drum's axle on its seat, free to turn. ``drives``
connects the mates' coordinates: the crank turns the units drum at a tenth
of its speed, and the units drum the tens drum. ``check`` refuses a crank
arm that would hang the knob past the plate. Turn the crank, in the browser
or in a test, and everything that depends on it follows.

``Base`` and ``Crank`` are in the same module,
`docs/tutorial/counter/readme.py <https://github.com/machinome/machinome/blob/main/docs/tutorial/counter/readme.py>`_,
with the imports this excerpt relies on. The
`joints <https://machinome.readthedocs.io/en/latest/concepts/joints.html>`_ page explains frames and mates, and
the tutorial builds the counter one lesson at a time, from a part to a
machine that counts.

What the framework does
=======================

``machinome develop`` watches the project, rebuilds the parts whose source
changed and reuses the rest, and serves the machine to the browser, where
the viewer shows the assembly, its movement and its controls, and a reader
drags the crank. ``machinome test`` runs the project's tests: that two
parts do not interfere, that a piece is one body, that a fit allows its
intended motion, that an assembly stands under gravity, and scenarios that
drive a sequence of inputs and check what happens along it, at the tick it
happens. Parts with B-rep geometry are compared on the B-rep engine and
mesh parts on the mesh engine, and a verdict once decided is kept between
runs.

Some machines are posed from their inputs alone. Others depend on what
happened before: a running machine advances its coordinates through time,
locating the crossings of its laws and stopping at its mechanical stops,
and a machine with declared state retains memory at events, as a
calculator keeps its digits after the crank returns to rest. Each is an
explicit modelling choice, and the viewer operates all three.

With the viewer installed, ``machinome export`` writes the machine as a
static web page, with its inputs and controls, that any file host serves
and a reader operates without installing a CAD stack. ``machinome
snapshot`` photographs a pose, ``machinome import-step`` scaffolds
declarative source from a STEP assembly, and ``machinome vet`` checks,
statically, that a project stays inside the framework's universe.

These tests and simulations give evidence about the model and the states
tested. They do not calculate every physical effect, and they do not
establish that a mechanism can be manufactured and operated safely.

Install
=======

Machinome is one package, licensed GPL-2.0-or-later or
CERN-OHL-S-2.0-or-later, at the recipient's choice. The browser viewer is
a separate package,
`Machinome Viewer <https://github.com/machinome/machinome-viewer>`_,
licensed AGPL-3.0-or-later, which the framework reaches only as a separate
process; the ``viewer`` extra installs it. The CAD kernels are extras too,
each named for the module that needs it, so a project installs only what
its parts use. Install the framework with the viewer and CadQuery, which
the tutorial models with, and start a project:

.. code-block:: bash

   pip install "machinome[viewer,cadquery]"
   machinome new myproject
   cd myproject
   machinome develop

The other kernel extras are ``build123d``, ``step`` (CadQuery's STEP
reader), ``molejo``, ``openscad`` and ``solid2`` (SolidPython; the OpenSCAD
executable is installed separately), ``jscad`` and ``stl``; ``brep`` and
``mesh`` install the kernels of the two comparison engines, and ``all``
installs every one. A module whose kernel is missing says so at the line
that imports it, with the line that installs it. ``mechanics`` installs
`Machinome Mechanics <https://machinome-mechanics.readthedocs.io>`_, an
independent package of gear, screw, cam, belt and linkage formulas.

Without the viewer the framework builds, tests, exports with
``--no-widget``, watches with ``machinome develop --no-web`` and takes
fixed-pose OpenSCAD snapshots with the ``openscad`` extra; with it,
``machinome develop`` opens the interactive viewer and every export carries
the viewer page. Machinome runs on Linux with Python 3.11 or newer; other
platforms are untested.

Documentation
=============

The `user manual <https://machinome.readthedocs.io/en/latest/>`_ is organised by what a
reader wants to do:

* `Why Machinome <https://machinome.readthedocs.io/en/latest/why.html>`_ is the idea in one page;
  `Install <https://machinome.readthedocs.io/en/latest/start/install.html>`_ and
  `Your first machine <https://machinome.readthedocs.io/en/latest/start/first-machine.html>`_ set up and move a
  part from a slider in ten minutes.
* The `tutorial <https://machinome.readthedocs.io/en/latest/tutorial/01-part.html>`_ builds a machine that
  counts, from a part to a machine with memory, one lesson per chapter,
  every chapter's code real and tested.
* The `how-to guides <https://machinome.readthedocs.io/en/latest/howto/backends.html>`_ are one job per page:
  parts in each modelling library, imported STEP and STL parts, sheet
  parts, flexible parts, markings, several models in one project, fast
  tests, and giving an existing design a simulation.
* `How it works <https://machinome.readthedocs.io/en/latest/concepts/node-tree.html>`_ explains the node tree,
  values, relations, joints, rest and motion, running and clocked
  machines, and publishing.
* The `reference <https://machinome.readthedocs.io/en/latest/reference/cli.html>`_ covers the command line, the
  API, the assertions, the Sphinx extension and the sibling manuals.
* The `changelog <https://machinome.readthedocs.io/en/latest/project/changelog.html>`_,
  `upgrading <https://machinome.readthedocs.io/en/latest/project/upgrading.html>`_ from an earlier version, and
  the `project status <https://machinome.readthedocs.io/en/latest/project/status.html>`_.

Real machines built with Machinome, printers, clocks and calculators among
them, are shown live on `machinome.org <https://machinome.org/>`_, each
beside its design source and licence; their simulations are kept in the
`Machinome Foundry <https://github.com/machinome-foundry>`_ organisation,
each beside the design it simulates. The framework, the viewer and the
mechanics package live under `machinome <https://github.com/machinome>`_.

Licence
=======

Machinome is licensed GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the
recipient's choice; see `LICENSE <LICENSE>`_. Machinome Viewer is a
separate AGPL-3.0-or-later package. The designs simulated with Machinome
keep their own licences.

Contributing
============

Machinome is developed empirically from real mechanical projects: a
requirement begins as something a machine needs, and the change is
validated in the machine that asked for it. Design and implementation are
AI-assisted; `AI-USE.md <AI-USE.md>`_ records which agents, since when,
and how the history marks their work. `CONTRIBUTING.rst <CONTRIBUTING.rst>`_
says how to set up a development environment, run the tests and propose a
change under the repository's spec-first discipline, and
`docs/contributor-briefing.md <docs/contributor-briefing.md>`_ is the
orientation to the code. Report issues and propose changes at
https://github.com/machinome/machinome.
