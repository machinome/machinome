4. One coordinate drives another
================================

A counter counts on drums. This chapter adds two, relates them to the
crank, and replaces a ratio with a law of the machine's own.

The drum
--------

Create ``counter/drum.py``:

.. literalinclude:: counter/c04_relations.py
   :language: python
   :pyobject: Drum

A ring with a bore, a ``turn`` joint on its own axis, and something new:
a **marking**. ``digits`` wraps a drawing of the ten digits around the
drum's rim in white. A marking is not a solid and not a child; it adds
no volume, changes no test and enters no build identity. It says what the
part carries on its surface. The artwork is an SVG beside the module,
and its X axis is arc length on the drum, so it is exactly one
circumference wide. :doc:`/howto/markings` has the details; the
tutorial's artwork comes from a twenty-line generator, ``make_digits.py``,
in the same directory.

Two drums at a ratio
--------------------

Add the drums to the machine and relate them:

.. literalinclude:: counter/c04_relations.py
   :language: python
   :pyobject: RatioCounter

Two relations are new. ``handle.turn.drives(units_drum.turn, ratio=0.1)``
says the units drum turns a tenth of what the crank turns, and the tens
drum a tenth of that. Either end of a relation is a coordinate: a joint,
a port, or a driver as the source. ``ratio=`` and ``offset=`` are the
shorthand for an affine law, and an affine law inverts itself, so the
same relation can be solved from either end.

``render()`` places the drums on the arbor. Placement at rest goes in
``render()``; it runs once. The relations move the drums; they are solved
on every instant.

Save and drag the crank. The drums turn continuously, a revolution
counter, and the digits slide past the post. That is a real machine, but
it is not a tally counter.

A law of your own
-----------------

A tally counter's drum stands still for most of a turn and steps one
digit at the end of it. That is not a ratio. It is a **law**: a function
of the driving coordinate that the framework can evaluate in Python and
publish to the browser.

.. literalinclude:: counter/c04_relations.py
   :language: python
   :pyobject: window

``window(60)`` returns a law factory. The framework calls it once, when
the machine is realized, with the two nodes that own the coordinates, and
what it returns is the law: a callable from the driving angle to the
driven one. The arithmetic is ``machinome.math``'s, not Python's own
``math``: ``floor`` and ``clamp01`` there work on plain numbers in tests
and on symbolic values in the build, so the same formula runs in the
browser. A Python ``if`` on the angle would not, because in the browser
there is no value to branch on.

Read the formula once. ``36 * floor(angle / 360)`` is thirty-six degrees
per completed turn: one digit. ``clamp01(...)`` rises from 0 to 1 over
the last ``width`` degrees of the current turn and holds at 0 or 1
outside it. So the drum stands, steps, stands.

Now the machine, with the ratio lines replaced:

.. literalinclude:: counter/c04_relations.py
   :language: python
   :pyobject: Counter

The tens drum is driven by the units drum, not by the crank, through the
same law with a narrower window: the last thirty-six degrees of the units
drum's turn, which is exactly its 9 to 0 step. That is a carry, stated as
what it is.

.. machinome:: /_exports/counter-04
   :height: 420px

Drag the crank slowly through 300 to 360 degrees and watch the units drum
step. Drag through nine turns and watch the tens drum step during the
tenth.

What the framework did with the chain
-------------------------------------

Three relations, and none of them says in which order to solve. Every
relation of a class is attempted at the end of the class's simulate
phase, from whichever end is bound: the crank driver binds
``handle.turn``, which binds ``units_drum.turn``, which binds
``tens_drum.turn``. A relation that cannot be solved yet waits for the
one it depends on; a coordinate two relations would both bind is refused
by name; a relation whose driven end is the bound one and whose law has
no inverse is refused too. :doc:`/concepts/relations` lists each refusal
and its reason, and shows relations over several coordinates at once,
broadcasts over repeated parts, and derived coordinates.

Next: :doc:`05-buttons`.
