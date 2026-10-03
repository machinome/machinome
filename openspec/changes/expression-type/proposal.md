## Why

The lean-core campaign's "Layers" ruling (pilot, 3 October 2026,
`workflow/ongoing/lean-core.md`) builds layer 1, the internal architecture of
the whole split, OpenSCAD included, before layer 2, the package split for
licensing, whose requirement is that a GPL-2.0-only project, which is an
OpenSCAD project, can import machinome with no Apache-2.0 code beneath it. That
turns on the core's own grant and its required dependencies, and a package's
licence matches its provider's (pilot, 2 October 2026). solidpython2, the
LGPL-2.1-or-later library behind `Solid2Node`, is today a required dependency
the core reaches from twelve files; the pilot wants OpenSCAD out of the core
before the package split (relayed by the orchestrator, 3 October 2026). Cycles
5 to 8 of the plan do that; this is cycle 5, "the core's own expression type in
place of solid2's `OpenSCADConstant` facade".

The twelve importers (AST walk of `machinome/` at edff84e, 3 October 2026),
by what they take:

| file | takes | role | cycle |
|---|---|---|---|
| `machinome/math.py` | `OpenSCADConstant` | the expression facade | 5 |
| `machinome/scad_expression.py` | `OpenSCADConstant` | the expression facade (`GraphValue` subclasses it) | 5 |
| `machinome/simulation/clocked.py` | `OpenSCADConstant` | the expression facade (law acceptance) | 5 |
| `machinome/simulation/program.py` | `OpenSCADConstant` | the expression facade (law and bound acceptance) | 5 |
| `machinome/simulation/profile.py` (lazy) | `OpenSCADConstant` | the expression facade (`profile_overlap`) | 5 |
| `machinome/node/base.py` | `scad_render`, `import_stl`, `color` | SCAD presentation | 6 |
| `machinome/node/operations.py` | `rotate`, `translate` | SCAD presentation (`.scad()`) | 6 |
| `machinome/node/internal.py` | `union` | SCAD presentation | 6 |
| `machinome/node/flexible.py` | `union` | SCAD presentation | 6 |
| `machinome/node/solid2.py` | `scad_render` | the `Solid2Node` leaf | 7 |
| `machinome/node/openscad.py` | `scad_render`, `get_scad_file_as_dict`, `resolve_scad_filename` | the `OpenScadNode` leaf | 7 |
| `machinome/manager/templates/project/root/__init__.py` | `cube`, `cylinder`, `translate` | the scaffolded project's shape | 8 |

Five of them import solid2 for an expression and nothing else. Of what solid2's
type supplies to those five, only one thing is load-bearing and cannot be had
without it: recognising a value SolidPython itself built (`solid2.
get_animation_time()`, `scad_inline(...)`, or text SolidPython's own operators
produced), which a ratified requirement keeps accepted
(`motion-expression-sharing`, "Supported legacy expressions retain their
behavior") and which machinome-mechanics' own suite and five project probes
exercise. The rest is spelling: the operator dispatch it lends `GraphValue`
calls straight back into `GraphValue`, its truth refusal is one method, and
SCAD output reads the value through `str()`, which is already the core's own
text (design.md, "What the facade is").

## What Changes

- **The core's symbolic value is its own type.** `GraphValue`, with its
  helpers (`as_node`, `call`, `symbol`, `get_animation_time`,
  `depends_on_time`, `scalar`, `restore_scalar`), moves to
  `machinome.expression_graph` beside `ExpressionNode`, and derives from no
  SolidPython class. It defines every operator it used to inherit; asking it
  for its truth raises `machinome.expression_graph.SymbolicTruthError`, an
  `Exception` subclass as SolidPython's refusal was, with machinome's own
  bounded message. `str()` stays the core's closed scalar text, so every
  standalone serialization, every identity listing, every SCAD file and every
  published document is unchanged byte for byte, and the document version
  does not move.
- **BREAKING: `machinome.scad_expression` is removed.** Its names are
  imported from `machinome.expression_graph`. Three project probes import
  `get_animation_time` from it (Pascaline-module, CycloidalDrive, Leonardo
  cam_hammer, all under `docs/probes/`, none loaded by a model).
- **The OpenSCAD engine gets its final address, `machinome/openscad/`,** a
  subpackage whose `__init__.py` defines nothing, as `machinome/occt/` is. Its
  provider module `machinome.openscad.engine` declares `CONTRACT = 1` and
  adopts a SolidPython scalar as the core's graph (`adopt(value)`), the one
  piece of the expression layer that needs solid2. The core reaches it
  through a seam of the exact engine's shape, `machinome.scad_engine`: one
  known provider, a contract version checked at resolve time, absence
  answered by `None`. No path *requires* the engine in this cycle, so the seam
  has no install refusal yet; an absent engine means a SolidPython value is
  not an expression, refused by the existing "neither a number nor an
  expression" messages, unchanged.
- **BREAKING (framework-internal): the OpenSCAD binary locator moves** from
  `machinome/openscad.py` to `machinome/openscad/binary.py`, unchanged,
  because the package takes the module's name. `require_openscad`,
  `openscad_binary` and `OpenScadUnavailable` are imported from there. No
  project imports them (grep of `projects/`, 3 October 2026).
- **A SolidPython operand on the left of an operator** now yields
  SolidPython's own text constant, as SolidPython computes it, which the
  framework reads back when the value reaches `machinome.math`, a law, a
  bound, an operation or a flexible parameter, with the same evaluation and
  free inputs. Before, the subclass relation let `GraphValue`'s reflected
  method win. On the right, and inside `machinome.math`, nothing changes.
- **No core module outside `machinome/openscad/` imports a SolidPython
  expression name**, and importing `machinome.math` or
  `machinome.expression_graph` imports no SolidPython at all. The remaining
  solid2 importers are exactly the SCAD presentation, the two OpenSCAD leaves
  and the template, which cycles 6 to 8 move.
- **The three faces of `machinome.math` stay one semantics**: its function
  bodies, `SYMBOLIC_BUILTINS` and degree conventions are unchanged, and a new
  test holds numeric, symbolic and declared faces to the same values.

Deferred, by the plan's layering and recorded in design.md: the SCAD
presentation behind the seam and `assemble()` without it (cycle 6); the binary
runner, `Solid2Node` and `OpenScadNode` over the engine, the `openscad` extra
and the seam's install refusal naming it (cycle 7); the template (cycle 8).

## Capabilities

### New Capabilities

- `scad-engine-dependency`: the seam, in the core. The OpenSCAD engine as a
  conditional, versioned provider resolved through `machinome.scad_engine`:
  its one provider, its contract version and mismatch refusal, what absence
  means for a SolidPython value, and that it is the only core module naming
  the provider.
- `openscad-engine`: the engine, `machinome.openscad`. The package that
  exports nothing, the provider's contract version and its adoption of
  SolidPython scalars, and the binary locator's address. It governs behaviour
  that leaves the core with the directory, so it leaves with the code.

### Modified Capabilities

- `motion-expression-sharing`: a new requirement that a symbolic value is the
  framework's own type (no SolidPython class, no SolidPython import, unchanged
  text and outputs, machinome's truth refusal); and "Supported legacy
  expressions retain their behavior" restated for a SolidPython operand
  recognised through the OpenSCAD engine, and for one on the left of an
  operator.

## Impact

- **Code.** New: `machinome/openscad/__init__.py`, `machinome/openscad/
  engine.py`, `machinome/openscad/binary.py` (the old `machinome/openscad.py`,
  moved), `machinome/scad_engine.py`. Removed: `machinome/scad_expression.py`,
  `machinome/openscad.py`. Changed: `machinome/expression_graph.py` (gains the
  value type), `math.py`, `simulation/{clocked,program,profile}.py`,
  `node/{operations,flexible,qualified,assembly,solid2,base}.py`,
  `core/serializer.py`, `viewers/openscad.py`, `manager/snapshot.py`, and
  docstrings naming solid2's `$t` (`motion/ports.py`, `motion/couplings.py`,
  `node/assembly.py`, `node/qualified.py`).
- **Public interface.** What a project spells does not change:
  the studio's contract skill (`machinome-studio/shop-skills/machinome-api/
  SKILL.md`) never names `OpenSCADConstant`, `GraphValue` or
  `machinome.scad_expression`; `self.time`, drivers, ports, laws and
  `machinome.math` read and compose as before. Project code that checks
  `isinstance(x, OpenSCADConstant)` on a framework value would see `False`;
  no project does (grep, 3 October 2026). Moved names are listed in
  `moved-names.toml` for the sweep and the one-path rewrite script.
- **Artifacts and documents.** None change: no document field or version, no
  SCAD byte, no recipe or clocked identity (the expression type's module is in
  none of them; `str()` is). The persistent verdict store starts afresh once,
  as on every framework source change (ADR-156).
- **Docs.** `docs/architecture.md` (the expression paragraph and source map),
  the changelog's Unreleased section, the `math.py` docstring, and the
  campaign plan (the validation table row; "Import paths" gains
  `machinome.openscad`).
- **Downstream.** machinome-mechanics is expected to keep passing (validation
  task 10.3): its tests use SolidPython
  `$t` through the engine's adoption and read `str()` and
  `machinome.core.expressions`, all unchanged. machinome-viewer carries a
  stray root-level `openscad.py`, outside its package and imported by
  nothing, which imports `machinome.openscad.require_openscad`; a finding for
  that repository, not this cycle's. The studio skill needs no change in this
  cycle.
