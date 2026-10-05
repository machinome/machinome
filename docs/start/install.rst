Install
=======

Requirements
------------

Always needed:

* **Linux.** Other platforms are untested.
* **Python 3.11 or newer.**

Needed only for OpenSCAD-family parts and OpenSCAD snapshots:

* **OpenSCAD**, the executable. It builds the STL files of
  ``Solid2Node`` and ``OpenScadNode`` parts and renders the fixed-pose
  snapshots of ``machinome snapshot``, which also need the ``openscad``
  extra below. A project whose parts all have B-rep geometry
  (``CadQueryNode``, ``Build123dNode``, ``StepNode`` and the sheet leaves)
  builds, tests and exports without it. The tutorial's machine is one of
  those, so you can follow it without OpenSCAD. The starter part that
  ``machinome new`` writes is a ``Solid2Node`` where SolidPython is
  installed (``machinome[solid2]``, ``machinome[all]``), and a
  ``CadQueryNode`` where only ``machinome[cadquery]`` is; with neither,
  ``machinome new`` refuses naming both extras.

Optional:

* The **jscad** command from npm, to write parts in JavaScript with
  ``JScadNode``.

The package itself brings trimesh. The CAD kernels, SolidPython and the
mesh engine are extras, so a project installs only the ones its parts use.

CAD kernels are extras
----------------------

Each leaf type lives in one module, ``machinome.node.<name>``, and a leaf
whose kernel is not part of the package is installed by the extra of the
same name: the extra is the last component of the module's address.

.. list-table::
   :header-rows: 1
   :widths: 26 34 40

   * - Extra
     - Module
     - Installs, for
   * - ``machinome[cadquery]``
     - ``machinome.node.cadquery``
     - CadQuery, for ``CadQueryNode``
   * - ``machinome[build123d]``
     - ``machinome.node.build123d``
     - build123d, for ``Build123dNode``, ``Build123dSheetNode`` and the
       SVG artwork of :doc:`markings </howto/markings>`
   * - ``machinome[step]``
     - ``machinome.node.step``
     - CadQuery's STEP reader, for ``StepNode``, ``StepAssembly`` and
       ``machinome import-step``
   * - ``machinome[molejo]``
     - ``machinome.node.molejo``
     - `molejo <https://molejo.readthedocs.io>`_ with its B-rep evaluator,
       for ``MolejoNode``
   * - ``machinome[brep]``
     - ``machinome.engine.brep``
     - the OCCT kernel of the B-rep engine, which every extra above
       installs too
   * - ``machinome[mesh]``
     - ``machinome.engine.mesh``
     - manifold3d, for the mesh engine, for every comparison on meshes: a
       part without B-rep geometry, ``machinome test --mesh``,
       ``assertAssemblySupported``, a fusion of such parts
   * - ``machinome[openscad]``
     - ``machinome.node.openscad``
     - SolidPython, for ``OpenScadNode``, the OpenSCAD writer and the
       OpenSCAD snapshot renderer of ``machinome snapshot``
   * - ``machinome[solid2]``
     - ``machinome.node.solid2``
     - SolidPython, for ``Solid2Node``; it installs ``machinome[openscad]``
       too
   * - ``machinome[jscad]``
     - ``machinome.node.jscad``
     - nothing: ``JScadNode`` runs the ``jscad`` command from npm, which no
       Python package installs
   * - ``machinome[stl]``
     - ``machinome.node.stl``
     - nothing: ``StlNode`` reads with trimesh, which comes with the
       package
   * - ``machinome[all]``
     - every module above
     - every extra above

``machinome[jscad]`` and ``machinome[stl]`` install nothing today; they
exist so that every node type has the extra of its name, and a project that
names them keeps its install line when the node types become packages of
their own. ``JScadNode`` and ``StlNode`` parts are compared on their meshes,
by the mesh engine, so a project that tests them installs
``machinome[mesh]``.
Without its extra, importing a module refuses with the line that installs
it, for example::

    ModuleNotFoundError: machinome.node.cadquery (CadQueryNode) needs
    cadquery, which is not installed; install it with
    'pip install "machinome[cadquery]"'

The same refusal answers ``from machinome.node.cadquery import
CadQueryNode``, the import every ``CadQueryNode`` part makes (each node
class is imported from its module; the root of ``machinome.node`` exports
nothing), and ``machinome import-step``. A project that imports ``cadquery`` or
``build123d`` itself, in its own modules, needs the extra of that name, and
one that imports ``manifold3d`` or calls ``trimesh.boolean`` needs
``machinome[mesh]``.

Without the mesh engine, each path that needs it refuses at its point of use
naming ``pip install "machinome[mesh]"``, and ``machinome test`` on the
mesh engine refuses at its start, before it builds anything. A project
whose every compared part has B-rep geometry needs it only for
``assertAssemblySupported`` and for runs on the mesh engine.

Two packages, two licences
--------------------------

The framework is one package, ``machinome``, licensed GPL-2.0-or-later or CERN-OHL-S-2.0-or-later
at the recipient's choice. The
browser viewer is a separate package, `machinome-viewer
<https://github.com/machinome/machinome-viewer>`_, licensed AGPL-3.0-or-later,
and the framework reaches it only as a separate process. The ``viewer``
extra installs it. Without it the framework builds, tests, exports with
``--no-widget``, watches with ``machinome develop --no-web`` and takes
OpenSCAD snapshots; with it, ``machinome develop`` opens the interactive
viewer, and every export carries the viewer page.

Install
-------

Create a virtual environment for your projects and install the framework
with the viewer and CadQuery, which the tutorial models with:

.. code-block:: bash

    $ python -m venv machines
    $ source machines/bin/activate
    $ python -m pip install "machinome[viewer,cadquery]"

Name the extras your parts need instead, ``all`` for every kernel, or
``mesh`` for a project whose parts are all OpenSCAD, JSCAD or STL:

.. code-block:: bash

    $ python -m pip install "machinome[viewer,all]"
    $ python -m pip install "machinome[mesh]"

If you will author OpenSCAD or SolidPython parts, install OpenSCAD too. On
Debian-based systems:

.. code-block:: bash

    $ sudo apt-get install openscad

Check the installation
----------------------

.. code-block:: bash

    $ machinome viewer

prints one line naming the installed viewer bundle, its ``apiVersion``
and the ``documentVersions`` it reads. This manual matches viewer
|viewer_version|, API |viewer_api|, reading document versions
|document_versions|. Without the viewer the command names the extra to
install and exits 1.

Two more extras exist: ``mechanics`` installs `Machinome Mechanics
<https://machinome-mechanics.readthedocs.io/en/latest/>`_, twenty-four
gear, screw, crank, cam, delta, linkage, rolling and belt formulas
(version |mechanics_version|), and ``web-snapshot`` installs the viewer with its
headless browser driver for transparent photographs. Neither is needed to
start.

Upgrading
---------

Coming from solid-node 0.6 or earlier? Read :doc:`/project/upgrading`
first: the packages, imports, command and configuration were renamed for
0.7, and a 0.5 environment must be recreated rather than upgraded in
place.

Next: :doc:`first-machine`.
