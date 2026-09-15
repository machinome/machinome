# Evidence — import the artifact by path

Everything below was measured on this worktree at `b8409cc`, with
`PYTHONPATH=$PWD` and `/home/asa/devel/libresolid-studio/.venv`, OpenSCAD
2021.01, before any change to the framework.

## The fixture

`evidence/probe_cross_package.py` writes a throwaway project outside the
repository and builds it with the real `solid build`. The project declares
four models:

    sim/parts.py         RigidLeaf(Solid2Node), ExactLeaf(CadQueryNode),
                         FlexLeaf(MolejoNode, height port), UnoptimizedLeaf
    sim/tools/bench.py   Bench       — places all three leaf kinds
                         UnoptBench  — places the optimize=False leaf
    sim/samebench.py     SameBench   — the control, beside the leaves
    sim/sub/deep/group.py   Group    — an intermediate assembly
    sim/tools/deep_bench.py DeepBench — a root over that intermediate

Run:

    PYTHONPATH=$PWD python \
      openspec/changes/import-the-artifact-by-path/evidence/probe_cross_package.py \
      /tmp/probe --save openspec/changes/import-the-artifact-by-path/evidence/generated

Each model is built twice; every generated `.scad` is printed after each
pass, with each `import(file = …)` checked for existence **relative to the
directory holding that `.scad`** — which is how OpenSCAD resolves it. The
generated files are kept under `evidence/generated/` (the state after the
second pass).

## The measurement

`Bench`, in `sim/tools/`, over leaves declared in `sim/` — the Thor shape.
`_build/bench/sim/tools/bench-Bench-3f8c65be8e28.scad`, identical after
build 1 and build 2:

```
union() {
	import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	translate(v = [20, 0, 0]) {
		import(file = "../parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	}
	translate(v = [40, 0, 0]) {
		import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
	}
}
    OK   ../parts-RigidLeaf-5c13fc621640.stl
    OK   ../parts-ExactLeaf-d20b313b0496.stl
    MISS parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl
```

### Leaf kind × build → path form

| leaf kind | build 1 | build 2 | resolves from the parent's build directory? |
| --- | --- | --- | --- |
| rigid (`Solid2Node`) | `../parts-RigidLeaf-5c13fc621640.stl` | identical | yes, both builds |
| exact (`CadQueryNode`) | `../parts-ExactLeaf-d20b313b0496.stl` | identical | yes, both builds |
| flexible (`MolejoNode`) | `parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl` | identical | **no**, both builds |
| rigid, `optimize = False` | no import at all — `cylinder(h = 12, r = 4);` inlined | identical | n/a |

The briefing's addendum predicted a bare name for the rigid and exact leaves
on the FIRST build (on the reading that `assemble()`'s `else` branch returns
`self.model`). **Refuted by the measurement above**: `assemble()`
(`base.py:825-834`) materialises the artifact in that branch and then
returns `self.import_optimized()` as well, so by the time the path is
spelled the STL is current and the root-relative form is taken. The
briefing's other prediction — a bare name for every flexible leaf, always —
**is confirmed**, on both passes.

The rigid and exact leaves are correct here by coincidence:
`import_optimized()` anchors on the ROOT NODE's directory
(`base.py:910`, `os.path.relpath(self.basedir, self.root)`), and in this
fixture the root IS the importing parent. Change that and it breaks:

### The same bug from the other side — an intermediate assembly

`DeepBench` (root, `sim/tools/`) → `Group` (`sim/sub/deep/`) → `RigidLeaf`
(`sim/`). Both generated files hold the SAME string, and it resolves in only
one of them:

```
=== _build/deep/sim/sub/deep/group-Group-34ca0e766088.scad
import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    MISS ../parts-RigidLeaf-5c13fc621640.stl

=== _build/deep/sim/tools/deep_bench-DeepBench-0bc412547ce1.scad
import(file = "../parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
    OK   ../parts-RigidLeaf-5c13fc621640.stl
```

An assembly is not rigid (`assembly.py:365`), so its parent inlines its whole
tree rather than importing an STL of it: one emitted string lands in two
`.scad` files at two depths. That is the measurement behind design.md's
claim that no single relative string can be finished at emission time.

### The control — a parent beside its parts

`SameBench`, in `sim/` with the leaves. Every import is a bare basename and
every one of them resolves:

```
union() {
	import(file = "parts-RigidLeaf-5c13fc621640.stl", origin = [0, 0]);
	import(file = "parts-ExactLeaf-d20b313b0496.stl", origin = [0, 0]);
	import(file = "parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl", origin = [0, 0]);
}
    OK   parts-RigidLeaf-5c13fc621640.stl
    OK   parts-ExactLeaf-d20b313b0496.stl
    OK   parts-FlexLeaf-a286075d8c7e-b4c4c1059a7c.stl
```

This is why the bug only ever appeared to projects that put a viewing helper
in a sub-package, and why moving the assembly beside the leaf cured it.

### What the published document says about the same artifacts

`_build/bench/viewer.json`, same build:

```json
"model": "sim/parts-RigidLeaf-5c13fc621640.stl"
"model": "sim/parts-ExactLeaf-d20b313b0496.stl"
```

Build-directory-relative, unambiguous, and correct — the document path has
never had this bug. That is the anchor this change adopts for the SCAD path
as well.

## What OpenSCAD does with an import it cannot open

`evidence/probe_openscad_missing.py`, calling OpenSCAD exactly as
`solid_node/viewers/openscad.py` does (`check=True`, `capture_output=True`):

```
openscad: /usr/bin/openscad
OpenSCAD version 2021.01
returncode: 0
--- stdout (the only stream the renderer logs)
WARNING: Can't open import file '/…/does-not-exist.stl', import() at line 3
Compiling design (CSG Products normalization)...
…
--- stderr (discarded by the renderer today)

image written: True
```

Three facts for the design:

1. The warning goes to **stdout**, not stderr, on 2021.01.
2. The return code is **0**, so `check=True` raises nothing and
   `manager/snapshot.py:216`'s `CalledProcessError` handler never runs.
3. The renderer does capture that stdout and then calls
   `logger.debug(result.stdout)` (`viewers/openscad.py:29-30`) — below the
   default level, so nothing reaches the maker. The image is written, minus
   the part, and the command prints `Snapshot saved to …`.

Reproduced end to end on the fixture itself:

    xvfb-run -a openscad -o bench.png --imgsize 400,300 --autocenter \
        --viewall bench-Bench-3f8c65be8e28.scad

warns about the flexible leaf's STL, exits 0, and writes
`evidence/generated/bench-missing-flexible-leaf.png` — the rigid box and the
exact box, and no helix at x = 40 at all.

## Feasibility of the proposed mechanism

`evidence/probe_reanchor.py`, against the installed solid2:

```
str subclass survives construction: False

--- as the parent inlines it
union() {
	import(file = "sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
--- re-anchored for a .scad one directory deeper
union() {
	import(file = "../sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
--- the tree the parent inlines is untouched
union() {
	import(file = "sim/a.stl", origin = [0, 0]);
	import(file = "vendor/x.stl", origin = [0, 0]);
}
```

So: a subclass of `import_stl` renders byte-identically (it passes the call
name `'import'` to its base) and is the marker that separates a framework
artifact import from the project's own; a `str` subclass on the `file`
parameter is NOT, because `import_stl` normalises it with
`_Path(file).as_posix()`; and re-anchoring a deep copy leaves the tree a
parent inlines untouched.

## Existing coverage checked

- `tests/deep_project/` is a nested-package fixture, but every model in it
  is a parent ABOVE its children (`third_level.py` → `one/` → `one/two/` →
  `one/two/three/`), and each is exercised as the ROOT. It cannot produce
  this bug: the root anchor and the importing directory coincide. There is
  no cross-package parent — an assembly in a SIBLING or DEEPER package than
  the leaf it places — anywhere in `tests/`.
- No existing test reads a generated `.scad` FILE and resolves its imports
  against disk. `tests/test_scad_stl.py` compares `self.solid.scad_code`
  text for a node loaded as the root; `tests/test_stl_node.py`,
  `tests/test_sheet_leaf.py`, `tests/test_build123d_adapter.py` and
  `tests/test_backend_neutral_materialization.py` assert
  `node.local_stl in str(assembled)`, a substring check that an anchored
  path still satisfies.
- `tests/test_snapshot.py` patches `OPENSCAD_RENDERER.render` and
  `find_xvfb_run`; the renderer takes its subprocess runner as an argument
  (`manager/snapshot.py:215`, `run` from `subprocess`), so a fake runner can
  deliver OpenSCAD's warning text without OpenSCAD.

## Noticed and left out of scope

- **A rigid leaf's own `.scad` stops describing its geometry after the first
  build.** Build 1 writes `_build/bench/sim/parts-RigidLeaf-….scad` as
  `cube(size = [10, 10, 10]);`; build 2 rewrites it as
  `import(file = "parts-RigidLeaf-….stl");` — `assemble()` sets
  `self.model = import_stl(self.local_stl)` on the up-to-date path
  (`base.py:819-821`) and then calls `generate_scad()`. The file that is
  supposed to be able to regenerate the STL becomes a file that imports it.
  It resolves (same directory), so it is not this change's bug; it is a
  separate finding for `workflow/warts.md`.
- A `FusionNode`'s `.scad` is written the same self-importing way, but its
  STL is produced natively (`fusion.py:93-140`, OCCT or manifold3d) and
  never by OpenSCAD from that `.scad`, so no geometry is at risk there.
- `self.mesh_scad_file` / `self.mesh_stl_file` are vestigial — nothing
  writes or reads them (the baseline spec says so, and a grep of
  `solid_node/` confirms only the assignment at `base.py:670-671`).
