3. Dimensions in one place
==========================

The crank's arbor is 8 mm and the base's bore is 8.2 mm. Those two
numbers agree because you typed them to agree. This chapter makes the
machine own that agreement: one declared shaft diameter, one declared
clearance, and every part that needs the bore reads the same derived
value.

Typed parameters
----------------

A **parameter** is a declared, typed value that decides what gets built.
Replace the literals in the base with declarations:

.. literalinclude:: counter/c03_dimensions.py
   :language: python
   :pyobject: Base

``Length(8.2, min=1)`` declares a length in millimetres with a default and
a lower bound. Inside ``render()``, ``self.bore`` is a plain float. The
kinds come from ``machinome.parameters``: ``Length``, ``Angle``, ``Count``
(an integer), ``Ratio``, ``Flag`` (a boolean) and ``Scalar`` (unchecked).
Node classes come from ``machinome.node``, drivers from
``machinome.simulation``, and joints and ports from ``machinome.motion``,
so an import block says which names build the machine, which move it and
which drive it.

Notice what stayed a bare constant: ``PLATE_LENGTH``, ``POST_DEPTH`` and
the others at the top of the module. The rule is **wrapped is a
parameter, bare is a constant**. A parameter propagates to children,
enters the part's build identity and can be set from a parent or the
command line. A bare number is ordinary Python: where things sit, lookup
tables, naming, never what is built.

The crank gets the same treatment:

.. literalinclude:: counter/c03_dimensions.py
   :language: python
   :pyobject: Crank

Declare once, pass down
-----------------------

Now the assembly declares the dimensions the parts share and hands them
down:

.. literalinclude:: counter/c03_dimensions.py
   :language: python
   :pyobject: Counter

``bore = shaft + 2 * clearance`` is a **derived parameter**: a formula
over declared tokens, written bare in the class body. It cannot be set by
anyone; it follows its inputs. The child declarations pass tokens by
reference, so ``Counter(shaft=10.0)`` rebuilds the crank at 10 mm and the
base with a 10.2 mm bore, and the two agree by construction.

The formula is checked for dimensions when the module is imported. A
length plus a length is a length; a length plus an angle raises a
``DimensionError`` before any geometry exists. :doc:`/concepts/values`
has the algebra.

``check()`` guards a rule between two parameters. The framework calls it
as soon as the parameters are resolved and before any child is realized,
so a refused counter builds nothing. Here: a knob that hangs past the
plate is refused by name.

Vary the design from the shell
------------------------------

Because the root's parameters are declared, every command that loads the
model can set them:

.. code-block:: bash

    $ machinome develop --set arm_length=30
    $ machinome build --set shaft=10 --set clearance=0.2
    $ machinome develop --set arm_length=50
    counter: an arm of 50.0 mm hangs the knob past the plate, which is 100.0 mm long

A value is parsed by the parameter's kind and checked by its constraints.
An unknown name fails listing the settable parameters; a derived
parameter cannot be set. Artifacts for different values coexist in the
build directory, keyed by their values, so switching back is a cache hit.

What a driver is not
--------------------

``--set shaft=10`` changes what is built: a new arbor, a new bore, new
STL files. Dragging the ``crank`` slider changes nothing that is built;
it moves parts that exist. That is the line between a parameter and a
driver, and it is also why a driver's value never enters a part's build
identity: two counters at different crank angles share every artifact.

Next: :doc:`04-relations`.
