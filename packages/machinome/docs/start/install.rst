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
* **FreeCAD** 1.1.4, extracted, to read native FreeCAD assemblies with
  ``FreeCADAssemblyNode`` (:doc:`/howto/freecad-assemblies`).

The package itself brings trimesh. Its node types, the CAD kernels,
SolidPython and the engines are extras, so a project installs only the ones
its parts use.

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
     - the package ``machinome-node-cadquery``, with CadQuery, for
       ``CadQueryNode``
   * - ``machinome[build123d]``
     - ``machinome.node.build123d``
     - the package ``machinome-node-build123d``, with build123d, for
       ``Build123dNode``, ``Build123dSheetNode`` and the SVG artwork of
       :doc:`markings </howto/markings>`
   * - ``machinome[step]``
     - ``machinome.node.step``
     - the package ``machinome-node-step``, with CadQuery's STEP reader,
       for ``StepNode``, ``StepAssembly`` and ``machinome import-step``
   * - ``machinome[molejo]``
     - ``machinome.node.molejo``
     - the package ``machinome-node-molejo``, with `molejo
       <https://molejo.readthedocs.io>`_ with its B-rep evaluator, for
       ``MolejoNode``
   * - ``machinome[brep]``
     - ``machinome.engine.brep``
     - the B-rep engine, the package ``machinome-engine-brep``, with the
       OCCT kernel; every extra above installs it too
   * - ``machinome[mesh]``
     - ``machinome.engine.mesh``
     - the mesh engine, the package ``machinome-engine-mesh``, with
       manifold3d, for every comparison on meshes: a part without B-rep
       geometry, ``machinome test --mesh``, ``assertAssemblySupported``, a
       fusion of such parts
   * - ``machinome[openscad]``
     - ``machinome.node.openscad``
     - the package ``machinome-node-openscad``, with SolidPython, for
       ``OpenScadNode``, the OpenSCAD writer and the OpenSCAD snapshot
       renderer of ``machinome snapshot``
   * - ``machinome[solid2]``
     - ``machinome.node.solid2``
     - the package ``machinome-node-solid2``, with SolidPython, for
       ``Solid2Node``; it installs ``machinome-node-openscad`` too
   * - ``machinome[jscad]``
     - ``machinome.node.jscad``
     - the package ``machinome-node-jscad``, for ``JScadNode``, which runs
       the ``jscad`` command from npm, which no Python package installs
   * - ``machinome[stl]``
     - ``machinome.node.stl``
     - the package ``machinome-node-stl``, for ``StlNode``, which reads
       with trimesh, which comes with the package
   * - ``machinome[freecad]``
     - ``machinome.node.freecad``
     - the package ``machinome-node-freecad``, for ``FreeCADAssemblyNode``
       and ``FreeCADJoint``, which read a native assembly through FreeCAD,
       a program no Python package installs, found through
       ``MACHINOME_FREECAD_ROOT`` (:doc:`/howto/freecad-assemblies`)
   * - ``machinome[all]``
     - every module above
     - every extra above

``machinome[jscad]`` and ``machinome[stl]`` install their node types'
packages and no kernel; a bare install carries no node type. ``JScadNode``
and ``StlNode`` parts are compared on their meshes, by the mesh engine, so
a project that tests them installs ``machinome[mesh]``.
Without its extra, importing a module refuses with the line that installs
it, for example::

    ModuleNotFoundError: the cadquery node type (CadQueryNode) needs
    machinome.node.cadquery, which is not installed; install it with
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

Packages and licences
---------------------

The framework is the package ``machinome``, with its engines and its node
types in packages of their own that its extras install
(``machinome-engine-brep``, ``machinome-engine-mesh``,
``machinome-node-cadquery``, ``machinome-node-build123d``,
``machinome-node-step``, ``machinome-node-molejo``,
``machinome-node-openscad``, ``machinome-node-solid2``,
``machinome-node-jscad``, ``machinome-node-stl`` and
``machinome-node-freecad``), with the mechanics helpers in
``machinome-mechanics``, with the browser viewer in ``machinome-viewer``, the
machinome skills in ``machinome-skills`` and the films in
``machinome-movie``, all licensed |framework_licence|, at the recipient's
choice. The framework reaches the
viewer only as a separate process. The ``viewer`` extra installs it.
Without it the framework builds, tests, exports with
``--no-widget``, watches with ``machinome develop --no-web`` and takes
OpenSCAD snapshots with the ``openscad`` extra; with it, ``machinome
develop`` opens the interactive viewer (:doc:`/howto/browser-viewer`), and
every export carries the viewer page. A host that only serves or captures
published documents installs ``machinome-viewer`` alone, which brings the
framework it is numbered with.

Install
-------

Create a virtual environment for your projects and install the framework
with the viewer and CadQuery, which the tutorial models with:

.. code-block:: bash

    $ python -m venv machines
    $ source machines/bin/activate
    $ python -m pip install "machinome[viewer,cadquery]"

Name the extras your parts need instead, ``all`` for every kernel, or,
for a project of STL parts, ``stl`` with ``mesh``:

.. code-block:: bash

    $ python -m pip install "machinome[viewer,all]"
    $ python -m pip install "machinome[stl,mesh]"

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

Four more extras exist: ``mechanics`` installs the :doc:`mechanics helpers
</reference/mechanics/index>`, ``machinome.mechanics``, gear, screw, crank,
cam, delta, linkage, rolling and belt formulas (the distribution
``machinome-mechanics``, version |mechanics_version|); ``skills`` installs
the :doc:`machinome skills </howto/assistant-skills>` for assistants and the
command ``machinome skills`` (the distribution ``machinome-skills``);
``movie`` installs the films of a machine, ``machinome.movie`` and the
command ``machinome movie`` (the distribution ``machinome-movie``), whose
Node side is a second step, run with your Node 22 or newer, and whose
Chromium and FFmpeg are documented steps of :doc:`/howto/film-a-movie`:

.. code-block:: bash

    $ python -m pip install "machinome[movie]"
    $ machinome movie setup

and ``web-snapshot`` installs the viewer with its headless browser driver
for transparent photographs; Chromium itself is a second step,
``playwright install chromium``. None is needed to start.

Upgrading
---------

Coming from Machinome 0.7? Read :doc:`/project/upgrading` first: 0.8
moves the kernels into extras, imports every name from its module and
renames the engines' flags, with no aliases. Coming from solid-node 0.6 or
earlier, the same page maps the names renamed for 0.7; a 0.5 environment
must be recreated rather than upgraded in place.

Next: :doc:`first-machine`.
