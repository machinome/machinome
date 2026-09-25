.. _examples:

========
Examples
========

Real machines built with Machinome are shown on `machinome.org
<https://machinome.org/>`_. Its `Foundry <https://machinome.org/foundry/>`_
keeps a simulation of an open-source machine beside the design it
simulates, shows it live in the browser, and states the design's own
licence and the simulation's: printers, calculators, clocks, robot arms
and hands, actuators, lab equipment and more. Browse it for a machine
like the one you are building. They are machines to explore after the
tutorial, not code to copy into a first project.

Look for one of each way a machine runs:

A **posed** machine
   A RepRap 3D printer whose original OpenSCAD design is read in place:
   three axis drivers, machine-level instructions, and belts, springs and
   filament as flexible parts. Ask for an axis position and the printer
   stands there.

A **running** machine
   A calculator built from decimal columns, whose simulation owns every
   dial and arbor and moves them by increments: a dial asked to add a
   digit twice leaves its register at two digits, a carry accumulates in
   the column above, each input arbor has a ratchet stop, and every dial
   is itself a control a reader turns by hand.

A **clocked** machine
   A hand-held calculator whose setting levers, crank, carriage and
   clearing ring make requests, whose registers are retained states
   written at events, and whose interlocks are bounds that hold one part
   while another is off rest.

The source of every simulation, with its tests and its records, is kept
in the `Machinome Foundry <https://github.com/machinome-foundry>`_
organisation on GitHub.
