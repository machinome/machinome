.. _examples:

========
Examples
========

Three machines show Solid Node applied to larger projects. Each has its
own page and live model, and each design lives in an independent source
repository. They are examples to explore after the step-by-step tutorial,
not code that you need to copy into your first project.

.. toctree::
   :maxdepth: 1

   example-v8-engine
   example-metamaquina2
   example-clock-01

:doc:`example-v8-engine`
   An engine with nested rotating and reciprocating assemblies, a timing
   drive, and flexible valve springs. Follow how motion reaches the
   pistons and valves through the assembled mechanism.

:doc:`example-metamaquina2`
   An open-hardware 3D printer built around its original OpenSCAD design,
   with axis controls, machine instructions, belts, springs and filament.

:doc:`example-clock-01`
   A pendulum clock from Luke Wallin's 3DPrintedClocks, with a gear train,
   escapement, motion works and pendulum. Its Solid Node model is read
   from an external repository, not reimplemented in these docs.

The example repositories retain their own licences. The framework tracks
them as external Git submodules and builds their viewer exports; it does
not copy their design source into the tutorial. Release-preview checkouts
need the matching example revisions. See the source links on each page.

Models used in the tutorial
===============================

The tutorial builds a small demonstration clock from a disc, a pointer
and a pin, one step at a time. Those examples belong to the framework,
under its Apache-2.0 licence; they are not derived from 3DPrintedClocks.

Small exports under ``docs/_exports/`` illustrate those steps
(:doc:`assemblies`, :doc:`animation`, :doc:`testing`), the knob
fusion (:doc:`fusion`), backend and sheet examples (:doc:`leaf-nodes`)
and the two-axis plotter (:doc:`driving`).
