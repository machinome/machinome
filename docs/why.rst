Why Machinome
=============

Source code for machines
------------------------

A machine is made of parts and the relationships between them. A shaft
fits a bearing; a gear turns another gear; a spring changes shape as a
valve moves; a counter's drum advances one digit at the end of each turn
of its crank. Dimensions must agree, motion must reach the right parts,
and the assembly must meet the requirements of its design.

Machinome puts those relationships in source code. A model describes
what the parts are, where they belong, what can move, what drives that
movement, and what the machine remembers. Geometry, operation and tests
share that description, so a design can be inspected, changed and
checked as a whole.

Describe what belongs together
------------------------------

Declare shared dimensions on an assembly and pass them to its parts. A
bore and the shaft made for it can follow the same parameter. Derived
values express a relationship once; guards refuse combinations the design
does not admit.

The assembly tree names the pieces and their placement. A joint names a
body's freedom, and a relation connects one coordinate to another through
a ratio or a mechanism law. Change a ratio and the motion you see and the
motion a test checks change together.

Describe how it operates
------------------------

A driver is a handle a person or a program can move. An instruction names
an operation such as homing an axis or turning a crank once. A control
puts that request on the part itself, so a reader turns the crank by
dragging it. Ports carry values between assemblies and into flexible
parts, so a belt or a spring follows the mechanism that acts on it.

Some machines can be posed from their inputs alone. Others depend on what
happened before. A running machine advances its coordinates through time,
locating the crossings of its laws and stopping at its mechanical stops. A
machine with declared ``State`` values retains memory at events: a
calculator keeps its digits after the crank returns to rest. These are
explicit modelling choices; :doc:`concepts/execution-models` states what
each one owns.

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
------------------------------

Tests state concrete requirements: these parts must not interfere, this
piece must be one body, this fit must allow its intended motion, this
assembly must stand under gravity. Exact geometry is compared on the OCCT
kernel; mesh geometry on faceted comparisons. A scenario adds a sequence
of inputs and checks what happens along it, at the tick it happens.

These checks give evidence about the model and the states tested. They
do not calculate every physical effect, and they do not establish that a
mechanism can be manufactured and operated safely. Physical prototypes,
material choices and manufacturing review still matter.

Share a machine people can explore
----------------------------------

Incremental builds reuse unchanged geometry while you edit. The optional
Machinome Viewer shows the assembly, its movement and its controls, and
lets a reader operate a running or a remembering machine in the browser.
Exports carry the model to a static web page; readers inspect its parts
and operate its inputs without installing a CAD stack.

The framework is Apache-2.0. The independent browser viewer is
AGPL-3.0-only, and example designs retain their own licences. Publishing
a design's source keeps its dimensions, relationships and tests available
to the next person who needs to repair or adapt it.

Start with :doc:`start/install`, open the :doc:`examples`, or browse the
`Machinome Foundry <https://github.com/machinome-foundry>`_, the GitHub
organisation where simulations of open-source machines built this way
are kept.
