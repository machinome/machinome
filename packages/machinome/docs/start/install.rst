Install
=======

.. needs:: none

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
  ``CadQueryNode`` where CadQuery is and SolidPython is not; with neither,
  ``machinome new`` refuses naming both extras.

The package itself brings trimesh. Its node types, the CAD kernels,
SolidPython and the engines are extras, so a project installs only the ones
its parts use.

.. _extras:

The extras
----------

Every package of the set beyond the framework is installed by an extra,
and every page of this manual says at its top which extras it needs. A
node type lives in one module, ``machinome.node.<name>``, installed by the
extra of the same name: the extra is the last component of the module's
address.

.. extras::

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

The framework is the package ``machinome``, and every package its extras
install, listed above, is licensed |framework_licence|, at the recipient's
choice. The framework reaches the
browser viewer through its seam of viewers as the viewer named ``web``, in
its own process. The ``viewer`` extra installs it.
Without it the framework builds, tests, exports with
``--no-widget``, watches with ``machinome develop --no-web`` and takes
OpenSCAD snapshots with the ``openscad`` or ``viewer-openscad`` extra; with it, ``machinome
develop`` opens the interactive viewer (:doc:`/howto/browser-viewer`), and
every export carries the viewer page. A host that only serves or captures
published documents installs ``machinome-viewer`` alone, which brings the
framework it is numbered with.

Install
-------

Create a virtual environment for your projects and install the framework
with the viewer, CadQuery and build123d, which the tutorial models with
(build123d draws the digits on its drums):

.. code-block:: bash

    $ python -m venv machines
    $ source machines/bin/activate
    $ python -m pip install "machinome[viewer,cadquery,build123d]"

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

Upgrading
---------

Coming from Machinome 0.8? Read :doc:`/project/upgrading` first: 0.9
releases every package of the set together and moves the mechanics helpers
and the viewer under ``machinome``, with no aliases. Coming from 0.7, the
same page lists the moves of 0.8: the kernels in extras, every name imported
from its module and the engines' flags renamed. Coming from solid-node 0.6
or earlier, it maps the names renamed for 0.7; a 0.5 environment must be
recreated rather than upgraded in place.

Next: :doc:`first-machine`.
