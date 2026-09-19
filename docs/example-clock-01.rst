.. _example-clock-01:

=====================
Clock 01
=====================

Clock 01 comes from **3DPrintedClocks**, Luke Wallin's open-source clock
project. The original designs and clock-building instructions are at
`github.com/MrBunsy/3DPrintedClocks
<https://github.com/MrBunsy/3DPrintedClocks>`_.

Its straightforward vertical layout makes the mechanism easy to follow:
a powered arbor drives the gear train, the escapement regulates its
motion, and the motion works drive the hands. The pendulum swings behind
the plates.

.. machinome:: examples/3dprintedclocks/docs/_exports/clock01
   :height: 620px

Press play to follow the pendulum and escapement. Increase playback speed
to see the hands advance across the twelve-hour timeline. The model's
pendulum adjustments let you explore how calibration changes its rate.

Open the external example
=========================

The Machinome simulation lives in the
`external simulation repository
<https://github.com/machinome/3DPrintedClocks/tree/b089545bfcb8bbb507e480c6381010cd8281fb89/simulation/wall_clock_01>`_.
That repository adapts the original project linked above; the framework
docs neither copy nor reimplement its clock design.

From a framework source checkout with the matching preview installed:

.. code-block:: bash

   git submodule update --init docs/examples/3dprintedclocks
   cd docs/examples/3dprintedclocks
   machinome develop wall_clock_01

To build or test it there:

.. code-block:: bash

   machinome build wall_clock_01
   machinome test wall_clock_01
   machinome export -o docs/_exports/clock01 wall_clock_01

These commands run the external repository's own model and tests.
The full geometric tests can take much longer than opening a cached model.
The simulation prescribes motion; it is not a dynamics solver or a
manufacturing certification.

Licence of the external design
===============================

3DPrintedClocks uses
`CERN-OHL-S v2
<https://github.com/MrBunsy/3DPrintedClocks/blob/master/LICENCE_cern_ohl_s_v2.txt>`_.
When distributing modified covered source, preserve notices, identify
changes and keep the applicable licence. When distributing clocks or
parts made from it, provide recipients the corresponding **Complete
Source**, or its source location—not just STL files or a viewer export.
See the project's licence and notices for the complete terms.

That is the external clock project's licence. Machinome and its own
tutorial source remain Apache-2.0. See also :doc:`example-v8-engine`
and :doc:`example-metamaquina2`.
