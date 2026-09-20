.. _example-curta:

============
Curta Type I
============

A simulation of `Marcus Wu's 3x-scale Curta Type I
<https://github.com/machinome-foundry/Curta-Type-I-3x/tree/0db199f>`_,
the hand-held mechanical calculator, built from its published CAD. The
clocked model is the third of the project's three siblings: the same
fitted machine, whose requests retain digits and latches rather than a
pose tree.

Eight setting levers, the crank, the carriage lift and shift, the
reversing lever and the clearing ring are the inputs; the result and
turns-counter digits are **states**, written at events: the end of a
crank stroke advances the registers, the clearing ring sweeping past a
dial resets it, and the checks that hold one part while another is off
rest are **bounds** that clip a request's path. ``Turn crank`` is one
request over one driver, and the viewer draws it over six seconds with
every carry firing where the machine located it. The digits on the number
rolls are markings.

.. machinome:: examples/curta/docs/_exports/curta
   :height: 620px

Set a digit on a lever, press **Turn crank** and read the result dials.
Lift and shift the carriage, and try to shift it mid-stroke: the request
is admitted at zero travel with its stop named. Sweep the clearing ring
to reset the registers.

What it shows
=============

* A machine with twenty-three inputs and eighteen retained states whose
  pose between events is a closed-form function of them, so a request
  costs one pose whatever the stroke.
* Committing relations whose events are located exactly along the
  request path, several of them writing one state at different events,
  and a clearing threshold that reads the digit it clears.
* Interlocks as ``Bound`` ranges reading other coordinates: the ratchet
  on the crank, the carriage held while the crank is off rest, the
  clearing ring held while the carriage is up.
* A document at version 8, carrying the compiled events and constraints,
  which the viewer executes with the same landings a Python session
  finds.

The project also keeps a running sibling under ``Time.running()`` and a
fast posed one, all three in one repository with named models.

Open the example
================

.. code-block:: bash

   git submodule update --init docs/examples/curta
   cd docs/examples/curta
   machinome models
   machinome develop clocked_curta

Licences
========

Two licences apply, by scope. The independent simulation software, the
loaders, the laws and the operating models, is Machinome Foundry work
under the GNU Affero General Public License, version 3 or later. Marcus
Wu's original CAD, the adapted geometry and the design-derived
corrections (the cover fits and the clearing-seat fit) remain under the
Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
licence, and so does every export that contains that geometry, the model
on this page included. The `Foundry repository
<https://github.com/machinome-foundry/Curta-Type-I-3x>`_ states the split
file by file. The calculator itself was designed by Curt Herzstark.
Machinome and its own tutorial source remain Apache-2.0.
