Simulate an existing open-source design
=======================================

Most machines worth simulating already have source: an OpenSCAD design,
a folder of STLs, a vendor STEP, a build123d project. Machinome does not
ask for a rewrite. It adds a thin layer beside the design that reads it
as it is, gives it a control surface, and proves what the design claims.
:doc:`Metamaquina 2 </example-metamaquina2>` is the worked case: a
printer authored in OpenSCAD, simulated without changing one ``.scad``
file.

The shape of the layer
----------------------

Keep the design source untouched, under its own licence, and add one
package beside it:

.. code-block:: text

    Metamaquina2/
        Metamaquina2.scad        the design, as published
        ...
        metamaquina2/            the simulation layer
            __init__.py
            parts.py             leaves reading the design
            machine.py           the assembly, drivers, instructions
            test_machine.py      the contracts
        pyproject.toml           [tool.machinome] model = "metamaquina2.machine:Metamaquina2"

Read the parts as they are
--------------------------

Pick the leaf kind that reads the source without copying it:

* an OpenSCAD design: ``OpenScadNode`` per module, or ``Solid2Node`` with
  SolidPython's ``import_scad`` reaching one module of the original file;
* published STLs: ``StlNode`` per part, ``body=`` for a print pack,
  ``adjust()`` for units and orientation (:doc:`imported-parts`);
* a vendor STEP: ``machinome import-step`` scaffolds a part per product
  and an assembly per assembly product at the document's own placements;
* a Python CAD project: ``CadQueryNode`` or ``Build123dNode`` leaves that
  import the project's own functions and return their solids.

Each leaf tracks its source, so editing the design rebuilds the parts that
read it.

Size the control surface to the machine
---------------------------------------

Declare the inputs the machine actually has, on the assembly that owns
each: an axis's travel on the axis, the whole printer's ``Home`` on the
printer. A joint per moving body, a relation per mechanical link, a
driver per handle, an instruction per operation a user performs. Do not
add inputs the machine does not have; a simulation that can pose the
design into states the real machine cannot reach proves less, not more.
Pick the execution model by what the machine keeps
(:doc:`/concepts/execution-models`).

A small demo set
----------------

Two or three instructions that show the machine doing its job, ``Rest``,
``Home``, ``Present the bed``, are worth more than a slider per screw.
They are what a reader presses first, and what a scenario triggers.

Prove what the design claims
----------------------------

Write the contracts the design implies and prove each one red first:
parts that must not interfere at rest and through a move, pieces that
must be one body, fits that must locate and still run free, an assembly
that must stand under gravity, a sequence of inputs that must leave the
machine where the design says. Where the design does not meet its own
claim, say so in the test with a measured allowance rather than a silent
tolerance, and record the finding beside the layer.

What the layer does not do
--------------------------

It does not certify the design. Simulation describes declared kinematics,
state transitions and stops; it is not a dynamics solver, and geometric
tests establish their stated contracts, not material strength, friction
or manufacturability. It also does not relicense anything: the design
keeps its licence, the layer carries its own, and a page or an export
that shows the design says where it came from.
