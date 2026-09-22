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

Everything else comes with the package: CadQuery, build123d, trimesh,
and `molejo <https://molejo.readthedocs.io>`_ for flexible parts.

Two packages, two licences
--------------------------

The framework is one package, ``machinome``, licensed Apache-2.0. The
browser viewer is a separate package, `machinome-viewer
<https://github.com/machinome/machinome-viewer>`_, licensed AGPL-3.0-only,
and the framework reaches it only as a separate process. The ``viewer``
extra installs it. Without it the framework builds, tests, exports with
``--no-widget``, watches with ``machinome develop --no-web`` and takes
OpenSCAD snapshots; with it, ``machinome develop`` opens the interactive
viewer, and every export carries the viewer page.

Install
-------

Create a virtual environment for your projects and install the framework
with the viewer:

.. code-block:: bash

    $ python -m venv machines
    $ source machines/bin/activate
    $ python -m pip install "machinome[viewer]"

Or without an interactive viewer:

.. code-block:: bash

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
