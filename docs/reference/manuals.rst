Sibling manuals
===============

Machinome is one of three packages that release together, and two
libraries it depends on have manuals of their own. Each manual owns its
subject; this one links rather than restates.

`Machinome Viewer <https://machinome-viewer.readthedocs.io/en/latest/>`_
    The browser viewer: installing it, inspecting an assembly, operating
    posed, running and clocked machines, publishing exports and
    snapshots, the complete embedding API with a working host page, and
    compatibility with document versions. The package is
    ``machinome-viewer`` |viewer_version|, AGPL-3.0-only, installed
    through the framework's ``viewer`` extra.

`Machinome Mechanics <https://machinome-mechanics.readthedocs.io/en/latest/>`_
    Twelve formulas for gears, lead screws, slider-cranks, linear deltas
    and planar linkages, each stating its frame, its zero and its sign,
    with a worked motion law. The package is ``machinome-mechanics``
    |mechanics_version|, Apache-2.0, installed through the ``mechanics``
    extra and imported from ``machinome_mechanics``.

`Machinome Foundry <https://github.com/machinome-foundry>`_
    The GitHub organisation holding simulations of open-source machines
    built with Machinome, the three :doc:`examples </examples>` among
    them. Each repository sits beside the design it simulates and states
    the design's licence and the simulation's.

`molejo <https://molejo.readthedocs.io>`_
    The analytic representation of flexible parts, springs, belts,
    cables and filament, that ``MolejoNode`` evaluates. An ordinary
    dependency of the framework, pinned by minor version.

`CadQuery <https://cadquery.readthedocs.io>`_, `build123d <https://build123d.readthedocs.io>`_, `SolidPython <https://github.com/jeff-dh/SolidPython>`_, `OpenSCAD <https://openscad.org/documentation.html>`_, `JSCAD <https://openjscad.xyz/>`_
    The modelling libraries a leaf's ``render()`` speaks. Machinome
    documents what a leaf must return; each library documents how to
    make it.
