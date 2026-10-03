# ADR-171: The OpenSCAD Engine Is `machinome.openscad`, Reached for Expressions Through `machinome.scad_engine`

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`expression-type`](../../../openspec/changes/archive/2026-10-03-expression-type/)
**Amends:** [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md) — the binary locator's module
**Related to:**
- [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — the exact engine's package, the precedent
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md)
- [ADR-170: The core's symbolic value is its own type](../MATH/ADR-170-the-core-s-symbolic-value-is-its-own-type.md)

## Context and Problem Statement

With the core's symbolic value its own type (ADR-170), one piece of the
expression layer still needs SolidPython: recognising a value SolidPython
built (`solid2.get_animation_time()`, `scad_inline(...)`, or the text its
own operators produce), which the `motion-expression-sharing` requirement
keeps accepted and machinome-mechanics' users exercise. The campaign's
import-path rules put an engine at `machinome.<name>`, a package whose
`__init__.py` defines nothing, reached from the core by a try-import of one
known provider with a contract version (`machinome.exact_engine`, ADR-161,
ADR-162). `machinome/openscad.py`, the ADR-046 binary locator, already held
the name.

## Decision Drivers

- The SolidPython-specific code at the engine's final address, so it leaves
  the core with the directory.
- The core names the provider in one place and checks its version.
- No path requires the engine yet: without it a SolidPython value is simply
  not an expression.
- A plain number never consults the engine.

## Considered Options

1. **The package `machinome.openscad` now, with `engine.py` (adoption) and
   `binary.py` (the locator), and the seam `machinome.scad_engine`** (chosen)
2. Adoption in `machinome/node/solid2.py`
3. Adoption in a temporary core module, the package deferred to cycle 7
4. A renderer at the engine's address that turns the core's expression into
   OpenSCAD syntax

## Decision Outcome

**The package.** `machinome/openscad/__init__.py` is a docstring.
`machinome.openscad.engine` declares `CONTRACT = 1` and `adopt(value)`: for
a SolidPython `OpenSCADConstant` (which covers `ScadValue` and
`scad_inline`), the node the core's own parser reads from its text, or a
`raw` node carrying the text when it is outside the language; `None` for
anything else. It keeps the node it read on the constant and reads again
only if the constant's text was replaced, so a value asked twice on its way
into one call (is it symbolic, then its node) is parsed once.
`machinome.openscad.binary` is `machinome/openscad.py` moved unchanged:
`openscad_binary`, `require_openscad`, `OpenScadUnavailable`. A package of
the same name shadows the module, so the move is forced, and the address is
also the locator's final one.

**The seam.** `machinome.scad_engine`, of `machinome.exact_engine`'s shape:
`CONTRACT = 1`, `PROVIDER = 'machinome.openscad.engine'`, `scad_engine()`
resolving once per process (`lru_cache`), `None` when the import fails with
a `ModuleNotFoundError` naming `machinome.openscad`, the provider or
`solid2` (no SolidPython installed, no SolidPython value to adopt), any
other import error propagating, and `ScadEngineIncompatible` naming the
provider and both versions, not cached, for a provider declaring another
version or none. It has no `require_` function and no install refusal: no
path requires the engine in this cycle, and the `openscad` extra does not
exist until the cycle that declares it. Importing the seam imports neither
the provider nor SolidPython.

**What still reaches the package directly.** `node/base.py`,
`node/solid2.py`, `viewers/openscad.py` and `manager/snapshot.py` import
`machinome.openscad.binary`: the SCAD presentation and the runner, which
the campaign's next cycles move behind the seam. A test lists them by name
so those cycles shrink the list.

### Why not `node/solid2.py` (option 2)

Adoption is not a node type, and rule 1 puts what is not a node type at
`machinome.<name>`; the plan moves solid2 and OpenSCAD out as one package.

### Why not later (option 3)

The binary runner's cycle would move adoption a second time.

### Why no renderer (option 4)

The core's closed text is OpenSCAD's scalar syntax and is also its
standalone serialization, its clocked identity, its diagnostics and what
downstream tests parse; solid2 embeds a value by `str()`. A renderer called
by `__str__` would make the core need the engine to name its own
expressions; one called only by the presentation would be an identity
function with one caller.

## Consequences

- `require_openscad`, `openscad_binary` and `OpenScadUnavailable` are
  imported from `machinome.openscad.binary`; `from machinome.openscad
  import require_openscad` fails with Python's "cannot import name".
  machinome-viewer carries a stray root-level `openscad.py` that imports the
  old spelling and is imported by nothing.
- With the engine absent, a SolidPython value meets the existing refusals
  unchanged: the numeric face's `TypeError` in `machinome.math`, "... which
  is neither a number nor an expression over its sources." from a law.
- An operation over a SolidPython constant never read before costs 128 to
  144 Python calls, within 10 % of 0.7.1's 125 and 135.

## References

- `machinome/scad_engine.py`, `machinome/openscad/{__init__,engine,binary}.py`
- `tests/test_scad_engine_seam.py`, `tests/test_openscad_engine.py`,
  `tests/test_expression_type.py`
- `openspec/specs/scad-engine-dependency/spec.md`,
  `openspec/specs/openscad-engine/spec.md`
