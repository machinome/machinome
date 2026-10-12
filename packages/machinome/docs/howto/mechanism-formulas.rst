Using helpers in a Machinome model
==================================

A mechanics function calculates a relationship. A Machinome motion law
connects that relationship to a driver or joint in your machine. This
example connects a crank-angle input to the height of a piston.

Create a directory for the example and save
:download:`pyproject.toml <examples/pyproject.toml>` there:

.. literalinclude:: examples/pyproject.toml
   :language: toml

This identifies the directory as a Machinome project. If you are adding
the example to an existing project, keep that project's own manifest.

Connect an input to a joint
---------------------------

The piston has a prismatic joint along Z and a connecting-rod length.
The engine supplies a crank radius and an angular input. A law factory
receives the source and target owners and reads their resolved dimensions.
Save this as :download:`slider_crank.py <examples/slider_crank.py>`:

.. literalinclude:: examples/slider_crank.py
   :language: python

Run Python from the directory containing that file, then try the model:

.. doctest::

   >>> from slider_crank import Engine
   >>> engine = Engine()
   >>> _ = engine.set_state(crank=0)
   >>> _ = engine.render()
   >>> engine.piston.rise.value
   75.0
   >>> _ = engine.set_state(crank=180)
   >>> _ = engine.render()
   >>> engine.piston.rise.value
   45.0

This is a complete example of the relation, using empty assemblies to
focus on the coordinates. Define node classes in a file, as above;
Machinome tracks their source files. Add your project's piston and crank geometry
to make a visible machine. The :doc:`slider-crank frame <reference/cranks>`
places the piston on the along axis: in this example, Z. Its height is
measured from the crank centre, so author the piston at its small-end
joint or apply the corresponding rest offset to its geometry.

The outer function reads dimensions once the objects exist. The returned
function accepts the changing crank angle, which can be numeric or
symbolic. Changing ``Engine(crank_radius=20)`` therefore changes the law
using the new dimension, without rewriting the formula.

The ``law=`` form describes forward motion. Having an inverse helper
such as ``screw_angle`` does not automatically make a relation invertible;
declare that behaviour through the framework's `relation laws
<https://machinome.readthedocs.io/en/latest/concepts/relations.html>`_
when needed.

Symbolic inputs
---------------

The same formula also accepts the framework's symbolic values. Under a
declared timeline, ``self.time`` in a node's ``simulate()`` is such a
value, and a helper called with it returns a deferred expression rather
than a number:

.. code-block:: python

   from machinome_mechanics import piston_height

   class Engine(AssemblyNode):

       def simulate(self):
           angle = 360 * self.time
           self.piston.translate([0, 0, piston_height(angle, 15, 60)])

That expression is what the framework publishes to the browser viewer
and writes into its animated builds; it is evaluated there, not sampled
in Python. The package's own test suite checks that every helper agrees
with itself on numbers and on symbolic values. The relation-law example
above lets the framework supply the changing input for you, which is the
form to prefer.

.. _declared-parameters:

Static calculations from declared parameters
--------------------------------------------

Use numeric values for a static phase calculation in a class body.
Save this as :download:`gear_phase.py <examples/gear_phase.py>` in the
same project directory:

.. literalinclude:: examples/gear_phase.py
   :language: python

.. doctest::

   >>> from gear_phase import GearPair
   >>> GearPair().initial_driven
   172.5

This ``.value`` calculation uses the declaration's default values at class
definition time. It is a static number: overriding an instance parameter
does not recompute it. Use a law factory over the resolved owners for
relationships that must follow instance dimensions. Passing declared
dimensional tokens directly to these helpers is not a supported general
formula interface; the dimension algebra can reject the calculation.

Next, choose a formula from :doc:`reference/index`. The framework's
`values page <https://machinome.readthedocs.io/en/latest/concepts/values.html>`_
explains parameters, formulas and the ``.value`` escape, and its
`relations page <https://machinome.readthedocs.io/en/latest/concepts/relations.html>`_
explains how drivers, joints and project laws fit together.
