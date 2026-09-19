Why Machinome
=============

Source code for machines
------------------------

A machine is made of parts and the relationships between them. A shaft
fits a bearing; a gear turns another gear; a spring changes shape as a
valve moves. Dimensions must agree, motion must reach the right parts,
and the assembly must meet the requirements of its design.

Machinome puts those relationships in source code. A model describes
what the parts are, where they belong, what can move, what drives that
movement, and what the machine remembers. Geometry, operation and tests
share that description, so a design can be inspected, changed and
checked as a whole.

Describe what belongs together
-------------------------------

Declare shared dimensions on an assembly and pass them to its parts.
A bore and the piston made for it can follow the same parameter.
Derived values express the relationship once; guards reject combinations
the design does not admit.

The assembly tree names the pieces and their placement. Joints name a
body's freedoms, and relations connect coordinates through a ratio or a
mechanism law. In :doc:`Clock 01 <example-clock-01>`, the hands follow
the modelled gear train. Changing a ratio changes the motion you see and
the motion a test checks.

Describe how it operates
------------------------

A driver is a handle a person or program can move. Instructions name
operations such as homing an axis or turning a crank. Ports carry values
between assemblies and into flexible parts, so the belt or spring follows
the mechanism that acts on it.

Some machines can be posed from their inputs alone. Others depend on
what happened earlier. A running simulation advances coordinates through
time, locating crossings and mechanical stops along the way. A machine
with declared ``State`` values retains memory at events: a calculator
can keep its digits after its crank returns to rest. An elapsed clock
can supply events for a clocked machine. These are explicit modelling
choices, described in :doc:`scenarios`.

Supply the parts in their natural form
--------------------------------------

Keep useful design source. CadQuery and build123d provide exact solids;
OpenSCAD, SolidPython and JSCAD supply their own geometry. Import a
vendor's STEP part or an existing STL, derive a sheet part and its DXF
from one profile, or use a molejo shape for a flexible spring, belt or
cable. :doc:`Metamaquina 2 <example-metamaquina2>` reads the printer's
original OpenSCAD parts in place.

A project may use one of these throughout or combine several. Machinome
adds the shared structure, relationships and operating behaviour around
those parts.

Check the design as it changes
-------------------------------

Tests state concrete requirements: these parts must not interfere,
this piece must be connected, this fit must allow its intended motion,
or this assembly must be supported under gravity. Exact geometry uses
the OCCT kernel; mesh geometry uses faceted comparisons. A scenario
adds an input sequence and checks what happens through it.

These checks give evidence about the model and the states tested.
They do not calculate every physical effect or establish that a
mechanism can be manufactured and operated safely. Physical prototypes,
material choices and manufacturing review still matter.

Share a machine people can explore
-----------------------------------

Incremental builds reuse unchanged geometry while you edit. The optional
Machinome Viewer shows the assembly, its movement and its controls.
Exports carry the model to a static website; readers can inspect its
parts and operate the declared inputs without installing a CAD stack.

The framework is Apache-2.0. The independent browser viewer is
AGPL-3.0-only, and example designs retain their own licences.
Publishing a design's source keeps its dimensions, relationships and
tests available to the next person who needs to repair or adapt it.

Start with :doc:`quickstart`, or explore the :doc:`examples`.
