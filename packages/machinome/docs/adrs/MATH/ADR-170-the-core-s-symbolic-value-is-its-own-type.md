# ADR-170: The Core's Symbolic Value Is Its Own Type

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`expression-type`](../../../openspec/changes/archive/2026-10-03-expression-type/)
**Amends:**
- [ADR-101: Motion sharing begins at construction](ADR-101-motion-sharing-begins-at-construction.md) — the SolidPython-compatible facade
- [ADR-056: Signals, drivers, ports, and stepped simulation](../NODE/ADR-056-signals-drivers-ports-and-stepped-simulation.md) — the `DriverToken` representation clause
**Related to:**
- [ADR-022: Cross-runtime degree-trig parity](ADR-022-cross-runtime-degree-trig-parity-for-t-expressions.md)
- [ADR-080: A shared subexpression is named once](../EXPORT/ADR-080-a-shared-subexpression-is-named-once.md)
- [ADR-171: The OpenSCAD engine is `machinome.openscad`](../NODE/ADR-171-the-openscad-engine-is-machinome-openscad.md) — where a SolidPython value is read

## Context and Problem Statement

Animation time, driver reads, port values and everything `machinome.math`
returns for them were `GraphValue`s (`machinome/scad_expression.py`), a
handle on the core's own immutable `ExpressionNode` that subclassed
SolidPython's `OpenSCADConstant`. The lean-core campaign takes OpenSCAD out
of the core before the package split, whose requirement turns on the
core's required dependencies; solidpython2 (LGPL-2.1-or-later) was reached
from five core modules for this facade alone. Read against the code, the
base class supplied seven inherited operator names that called straight
back into `GraphValue`, a truth refusal, and an `isinstance` target; SCAD
output and every serialization read the value through `str()`, the core's
own closed text. Only two things were load-bearing: recognising a value
SolidPython itself built, and Python's reflected priority when such a
value stood on the left of a framework value.

## Decision Drivers

- No core module imports SolidPython for an expression; importing
  `machinome.math` imports none.
- The symbolic value defined once, at one address, by the core.
- Unchanged arithmetic, comparisons, degree math, evaluation, text, SCAD
  bytes and document bytes; no document version moves.
- A truth test must not become a silent branch inside a framework
  `except TypeError`.
- No construction cost regression.

## Considered Options

1. **`GraphValue` at `machinome.expression_graph`, deriving from nothing**
   (chosen)
2. An `OpenSCADConstant`-compatible shim kept in the core
3. An engine-supplied subclass the core instantiates when SolidPython is
   installed
4. The type in `machinome.math`, or a new module
5. Renaming the type `Expression`

## Decision Outcome

`GraphValue`, with `as_node`, `call`, `symbol`, `get_animation_time`,
`depends_on_time`, `scalar` and `restore_scalar`, lives in
`machinome.expression_graph` beside `ExpressionNode`;
`machinome.scad_expression` is removed (no alias module). The class
subclasses `object` and defines every operator it supports: `+ - * / %`,
`**` published as `^`, their reflections, the six comparisons returning
graphs, unary `-`, `abs()` as the `abs` call, `float()` of a value with no
free input. Each operator builds its node directly. It defines `__eq__`, so
it stays unhashable; it is not iterable; `+value` is a `TypeError`.
`str()` and `value` stay `machinome.core.expressions.scad_expression` of
the node, byte for byte.

**Truth.** `__bool__` raises `machinome.expression_graph.SymbolicTruthError`,
an `Exception` and deliberately not a `TypeError` (25 framework sites catch
`TypeError`; SolidPython's refusal was a bare `Exception`, which none of
them catch). Its message names the value by its bounded `repr` and the
remedy: compose with `machinome.math` (`min`, `max`, `clamp`, `sign`), or
bind the drivers first.

**Recognition** is one predicate, `symbolic(value)`: a plain `int` or
`float` is decided first, by its class and without a call, and is never
symbolic; a `GraphValue` is its node; an `ExpressionNode` itself; anything
else is symbolic only when the OpenSCAD engine resolves and adopts it
(ADR-171). The ten former `isinstance(value, OpenSCADConstant)` sites in
`machinome.math` and the simulation call it, with every refusal's wording
unchanged. `machinome.math` answers its own symbolic question without the
engine for a declared quantity or formula, its third face.

**A SolidPython operand on the left** of a framework value now runs
SolidPython's own operator, which builds a SolidPython text constant
embedding the framework value's closed text; the framework reads it back
through the engine wherever it reaches `machinome.math`, a law, a bound, an
operation or a flexible parameter, with the same evaluation and free
inputs. On the right, nothing changes.

### Why not a shim (option 2) or an engine subclass (option 3)

Both keep reflected priority and change no behaviour, and both leave the
core's value a SolidPython instance: the shim imports SolidPython for an
expression, the goal's negation; the engine subclass makes every value the
core builds a SolidPython instance whenever SolidPython is installed, the
shim by the back door, and puts a lookup on every construction site.

### Why not `machinome.math` or a new module (option 4)

The node layer, the motion layer, the serializer and the simulation need
the type without the vocabulary; `GraphValue.evaluate` imports
`machinome.math` for its numeric faces, which would become a self-import.
`GraphValue` is a handle on an `ExpressionNode`; one module holds both.

### Why not `Expression` (option 5)

`machinome.parameters.Expression` is the declared face's formula, imported
by `machinome.math`; two `Expression`s would misread at every call site.

## Consequences

- `import machinome.math` loads no SolidPython (28.8 ms to 14.3 ms,
  median of five); native operations cost one to six Python calls fewer
  each, `abs(t)` the same.
- No SCAD byte, operation serialization, document field or version,
  recipe or clocked identity changes: the deep validation's 24 `.scad`
  files were byte-identical and the Curta's clocked block hashed the same.
- `isinstance(x, OpenSCADConstant)` is false for a framework value; code
  asking "is this symbolic" asks `machinome.expression_graph.symbolic`.
  machinome-mechanics' tests asked the old way and are corrected in that
  repository.
- A chain kept with a SolidPython operand on the left is SolidPython's own
  text building, linear in the text per step, as any explicitly expanded
  project text already was.
- `machinome.scad_expression` imports fail with Python's own
  `ModuleNotFoundError`; its names move one-for-one (`moved-names.toml`).

## References

- `machinome/expression_graph.py`, `machinome/math.py`,
  `machinome/simulation/{program,clocked,profile}.py`
- `tests/test_expression_type.py`, `tests/test_expression_faces.py`,
  `tests/test_expression_type_cost.py`, `tests/expression_type_golden.py`
- `openspec/specs/motion-expression-sharing/spec.md` ("A symbolic value is
  the framework's own type", "Supported legacy expressions retain their
  behavior")
