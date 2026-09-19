
.. _quickstart:

==========
Quickstart
==========

Requirements
============

Always needed:

* **Linux** — other platforms are currently untested and unsupported.
* **Python 3.11 or newer**.

Needed for OpenSCAD-family parts:

* **OpenSCAD** — builds the STL files of OpenSCAD-based nodes
  (``Solid2Node``, ``OpenScadNode``) and renders OpenSCAD snapshots.
  The project template ``machinome new`` scaffolds starts from a
  ``Solid2Node``, so the quickstart path below needs it. A project
  whose parts are all OCCT-backed (``CadQueryNode``, ``Build123dNode``
  and the sheet leaves) builds, tests and exports without it.

Optional:

* The **jscad** CLI (from npm), if you want to write nodes in
  JavaScript with ``JScadNode``.

Everything else — CadQuery, build123d, trimesh, `molejo
<https://molejo.readthedocs.io>`_ for flexible parts — comes with
``pip install machinome``. The **browser viewer** is a separate package,
`machinome-viewer <https://github.com/machinome/machinome-viewer>`_,
installed through the ``viewer`` extra; without it, ``machinome develop`` opens
no interactive viewer and tells you to install the extra. The two are licensed
differently — the framework under Apache-2.0, the viewer under AGPL-3.0-only —
which is why they are separate packages you install separately.

Installation
============

This manual targets Machinome 0.7, in preparation, the successor to
solid-node 0.6.0. See :doc:`upgrading` if you have an existing project.
The framework and matching viewer source can be installed now; the
package-index commands below apply after publication.

Start by creating a virtual environment for your project

.. code-block:: bash

    $ python -m venv myproject-env
    $ source myproject-env/bin/activate

For a source installation, install matching framework and viewer
checkouts into that environment. Building the viewer from source also
needs Node.js 22 or newer; its package build installs and compiles its
browser dependencies.

.. code-block:: bash

    $ python -m pip install /path/to/machinome-framework /path/to/machinome-viewer

Once the renamed source revisions are available on the public branches,
obtain those checkouts with:

.. code-block:: bash

    $ git clone https://github.com/machinome/machinome-framework.git
    $ git clone https://github.com/machinome/machinome-viewer.git
    $ python -m pip install ./machinome-framework ./machinome-viewer

Use the matching source revisions supplied with the release preparation;
``main`` can advance after this manual was validated. Record those revisions
with your project. The framework clone does not need example submodules
to install or to create a project.

.. note::

   At this documentation revision, the matching viewer rename and the
   three example-project migrations are committed locally but still need
   to be pushed to their public repositories. Installing arbitrary public
   heads does not yet reproduce the validated source combination.

After publication, install from the package index with the browser viewer:

.. code-block:: bash

    $ python -m pip install "machinome[viewer]>=0.7,<0.8"

or without an interactive viewer

.. code-block:: bash

    $ python -m pip install "machinome>=0.7,<0.8"

For the default project template, make sure you have openscad
installed. On Debian-based systems:

.. code-block:: bash

    $ sudo apt-get install openscad

Upgrading from 0.5.x
====================

0.6 moves ``cadquery`` to 2.7 and adds ``build123d``, which share one
large binary OCCT wheel whose versions cannot coexist. **Upgrade by
recreating the virtual environment and reinstalling**, not with an
in-place ``pip install -U``. Moving from 0.6 to 0.7 also requires the
source and configuration rename in :doc:`upgrading`.

Create your project
===================

Create a new project with a starting structure

.. code-block:: bash

    $ machinome new myproject
    $ cd myproject

Start the development loop. The browser viewer opens by default and requires the
``viewer`` extra installed above. With no argument, `machinome develop` operates
on the project's model, declared as
`model = "myproject.myproject:Myproject"` in the `pyproject.toml`
manifest `machinome new` just wrote for you.

.. code-block:: bash

    $ machinome develop

Open the link http://localhost:8000 in your browser. If another program will
consume the published build directory, run the watch loop without an
interactive viewer:

.. code-block:: bash

    $ machinome develop --no-web

OpenSCAD remains available for authoring ``OpenScadNode`` and ``Solid2Node``
geometry, SCAD output, and fixed-pose snapshots; it is no longer a
``machinome develop`` viewer.

Open `myproject/myproject.py` file in your preferred code editor and
see your model update in the viewer as you modify the code.

Drive it
========

Once you have seen the static part, try adding one input. Replace the
scaffolded class with an assembly that lifts it:

.. code-block:: python

    from machinome.node import AssemblyNode, Solid2Node
    from machinome.simulation import Driver
    from solid2 import cube, cylinder, translate

    class Block(Solid2Node):

        def render(self):
            return translate(-25, -25, 0)(
                cube(50, 50, 50)
            ) - cylinder(r=10, h=100)

    class Myproject(AssemblyNode):

        lift = Driver(default=0.0, range=(0.0, 80.0), unit='mm')

        block = Block()

        def simulate(self):
            self.block.translate([0, 0, self.lift])

Here ``block = Block()`` declares a child; every assembly instance
gets its own block. ``lift`` is a runtime input, so it is read in
``simulate()``, not in the method that makes the geometry.

Save, and the viewer grows a ``lift`` slider: drag it and the block
follows. That slider travels with the model into every export and
embed — see :doc:`Driving a machine <driving>`. (The module now holds
two node classes, so if you kept the scaffolded test, declare its node
with ``node = Myproject`` — see :doc:`Testing <testing>`.)

Build artifacts
===============

Check the `_build` directory for the artifacts of your project: an STL
per leaf part, plus a `.brep` beside it for OCCT-backed parts (the
exact geometry) and a `.dxf` beside sheet parts (the nominal cut
profile).

From here, continue with the tutorial: :doc:`Modeling parts
<leaf-nodes>`.
