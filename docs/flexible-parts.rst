Flexible parts
==============

Rigid motion changes a part's placement. A spring compressing or a cable
bending changes the part's shape. Machinome represents these with
``FlexibleNode``; its ``MolejoNode`` adapter uses
`molejo <https://molejo.readthedocs.io>`_ shape descriptions.

The small tutorial clock uses rigid parts. For a worked flexible-part
example, follow the valve spring in :ref:`the MolejoNode guide
<flexible-parts>`: declare its height port, describe the helix, then
connect that height from its owning assembly. The
:doc:`V8 engine <example-v8-engine>` shows this in a complete machine.

The pattern
-----------

Declare input ports on the flexible leaf, then describe a molejo shape
with named parameters in ``render()``. Connect those inputs from the
owning assembly. A cord could receive its free-end position from a
weight's translation; a spring could receive its length from the two
seats that compress it.

A flexible leaf has no independent time. Its owner supplies the state,
so the same shape description can be evaluated in a numeric test or
in the browser as a control moves.

The browser receives a serializable shape specification instead of a
different STL for each frame. Flexible leaves cannot be children of a
rigid fusion: a changing shape is not one fixed printed solid.

See :ref:`the MolejoNode guide <flexible-parts>` for runnable shape
examples, port wiring, export behaviour and exact-geometry limitations.
