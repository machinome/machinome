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
    ``machinome-viewer`` |viewer_version|, AGPL-3.0-or-later,
    installed through the framework's ``viewer`` extra.

`Machinome Mechanics <https://machinome-mechanics.readthedocs.io/en/latest/>`_
    Twenty-four formulas for gears, lead screws, slider-cranks, cams,
    indexed advance, linear deltas, planar linkages, rolling motion and
    belts, each stating its frame, its zero and its sign, with a worked
    relation law. The package is ``machinome-mechanics``
    |mechanics_version|, Apache-2.0, installed through the ``mechanics``
    extra and imported from ``machinome_mechanics``.

`machinome.org <https://machinome.org/>`_
    The site of the whole ecosystem. Its Foundry shows simulations of
    open-source machines built with Machinome live in the browser, each
    beside the design it simulates, stating the design's licence and the
    simulation's; the :doc:`examples </examples>` page says what to look
    for there. The source of every simulation is kept in the `Machinome
    Foundry <https://github.com/machinome-foundry>`_ organisation on
    GitHub.

`molejo <https://molejo.readthedocs.io>`_
    The analytic representation of flexible parts, springs, belts,
    cables and filament, that ``MolejoNode`` evaluates. An ordinary
    dependency of the framework, pinned by minor version.

`CadQuery <https://cadquery.readthedocs.io>`_, `build123d <https://build123d.readthedocs.io>`_, `SolidPython <https://github.com/jeff-dh/SolidPython>`_, `OpenSCAD <https://openscad.org/documentation.html>`_, `JSCAD <https://openjscad.xyz/>`_
    The modelling libraries a leaf's ``render()`` speaks. Machinome
    documents what a leaf must return; each library documents how to
    make it.
