## Why

An assembly that sits in a different Python package from the parts it places
renders those parts as nothing, and says the build succeeded.

`projects/Robots/Thor` met it (`workflow/warts.md`, "# Robots/Thor
(2026-09-07)", last bullet): an `AssemblyNode` under `simulation/tools/`
holding a `MolejoNode` declared in `simulation/` emitted

    import(file = "flexibles-ElbowBelt-...stl", origin = [0, 0]);

into `_build/simulation/tools/`, where that STL does not exist — it is in
`_build/simulation/`. OpenSCAD resolves an `import()` relative to the file
that holds it, finds nothing, warns, and renders the rest. `solid snapshot`
reports success. The project's author lost a snapshot cycle to a belt he
thought was broken, and `projects/Robots/Thor` still has no belt-viewing
helper under `tools/` because moving the assembly beside the leaf was the
only cure.

Measured here on a two-package fixture built twice (`evidence.md`), the
framework spells a child's artifact TWO different ways and neither is right
in general:

| what the parent's `.scad` holds | spelling | resolves from the parent's own build directory? |
| --- | --- | --- |
| rigid leaf (`Solid2Node`) | `../parts-RigidLeaf-….stl` | yes — by luck: the path is relative to the ROOT's build directory, and the root IS the parent here |
| exact leaf (`CadQueryNode`) | `../parts-ExactLeaf-….stl` | yes, same luck |
| flexible leaf (`MolejoNode`) | `parts-FlexLeaf-…-….stl` | **NO** — a bare name, on every build |
| an intermediate assembly's OWN `.scad`, three packages from the root | `../parts-RigidLeaf-….stl` | **NO** — the path is anchored on the ROOT's build directory, not on the file that holds it |

Both spellings come from the same missing rule: the framework has no
definition of what an artifact import is relative TO. `import_optimized()`
(base.py:908-914) anchors on the root node's source directory; every leaf's
`as_scad` (exact_leaf.py:99, flexible.py:324, jscad.py:94, stl.py:201,
base.py:821) emits a bare basename, which is an anchor on the leaf's own
directory. They agree only when the parent and the leaf live in one package,
which is why this looked like a molejo bug for a year.

The silence is the second half of the cost. OpenSCAD 2021.01 reports
`WARNING: Can't open import file '…'` and exits 0; the renderer
(`solid_node/viewers/openscad.py:28-30`) captures that stream and logs it at
DEBUG, so nothing reaches the maker but a smaller machine in a PNG.

## What Changes

- Every `import(file = …)` the framework writes into a generated `.scad`
  SHALL resolve, from the directory of the `.scad` that holds it, to the
  artifact it names — for every leaf kind, at every depth, whatever package
  the parent is declared in and whether or not the artifact was already
  current. A parent in another package SHALL render exactly the geometry a
  parent beside the leaf renders.
- A path a PROJECT wrote itself — `import_stl(...)` inside its own
  `render()` — SHALL be left exactly as the project wrote it.
- `solid snapshot --renderer openscad` SHALL fail, naming the file and the
  `.scad` that imports it, when OpenSCAD reports it could not open an
  imported file, and SHALL write no image; today it reports success. Every
  other warning, error or deprecation OpenSCAD reports SHALL reach the
  operator's log rather than only the debug stream; its progress output
  stays on the debug stream.
- **Out of scope**, recorded so it is not read into this change: the
  published document (`viewer.json`) already names artifacts relative to the
  build directory and is correct — nothing here changes it; and the web
  renderer, which reads that document and never opens a `.scad`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `build-pipeline`: gains "Generated SCAD imports resolve from the file that
  holds them" — the anchoring rule the artifact layout never stated.
- `cli`: gains "A snapshot never silently drops geometry OpenSCAD could not
  open" — the snapshot command's failure contract for an unresolvable
  import.

## Impact

- `solid_node/node/base.py` — one anchored-path helper and one marker type
  for a framework-emitted import; `assemble()` (line 821) and
  `import_optimized()` (908) use them; `scad_code` (1019) re-anchors on the
  node's own build directory before rendering.
- `solid_node/node/exact_leaf.py:99`, `solid_node/node/flexible.py:324`,
  `solid_node/node/adapters/jscad.py:94`,
  `solid_node/node/adapters/stl.py:201` — emit the anchored import.
- `solid_node/node/adapters/openscad.py:77` — its own `scad_code` override
  must re-anchor through the same seam.
- `solid_node/viewers/openscad.py` — reports what OpenSCAD said;
  `solid_node/manager/snapshot.py` — turns an unopenable import into a
  non-zero exit.
- `tests/` — a new cross-package fixture package and its tests; existing
  scad expectations are unaffected (they are all root-anchored roots, which
  the rule reproduces exactly — see design.md, "What does not move").
- Projects: `projects/Robots/Thor` can put its belt-viewing helper back
  under `tools/`. No project source changes are required by this change.
- New ADR-116: what an artifact import is relative to is a durable
  convention two layers depend on, and the answer is not obvious.
