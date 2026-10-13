Sibling manuals
===============

.. needs:: none

The browser viewer and the mechanics helpers are documented in this
manual, under :doc:`/reference/viewer/index` and
:doc:`/reference/mechanics/index`; the libraries below have manuals of
their own. Each manual owns its subject; this one links rather than
restates.

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
