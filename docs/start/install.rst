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
  snapshots of ``machinome snapshot``. A project whose parts are all
  OCCT-backed (``CadQueryNode``, ``Build123dNode``, ``StepNode`` and the
  sheet leaves) builds, tests and exports without it. The tutorial's
  machine is one of those, so you can follow it without OpenSCAD. The
  starter part that ``machinome new`` writes is a ``Solid2Node``, which
  is why :doc:`first-machine` replaces it first thing.

Optional:

* The **jscad** command from npm, to write parts in JavaScript with
  ``JScadNode``.

The package itself brings trimesh, SolidPython and the mesh engine. The
CAD kernels are extras, so a project installs only the ones its parts use.

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
   * - ``machinome[occt]``
     - ``machinome.occt.engine``
     - the OCCT kernel of the exact engine, which every extra above
       installs too
   * - ``machinome[all]``
     - every module above
     - every kernel

``Solid2Node``, ``OpenScadNode``, ``JScadNode`` and ``StlNode`` need no
extra. Without its extra, importing a module refuses with the line that
installs it, for example::

    ModuleNotFoundError: machinome.node.cadquery (CadQueryNode) needs
    cadquery, which is not installed; install it with
    'pip install "machinome[cadquery]"'

The same refusal answers ``from machinome.node import CadQueryNode`` and
``machinome import-step``. A project that imports ``cadquery`` or
``build123d`` itself, in its own modules, needs the extra of that name.

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
none for a project whose parts are all OpenSCAD, JSCAD or STL:

.. code-block:: bash

    $ python -m pip install "machinome[viewer,all]"
    $ python -m pip install machinome

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
