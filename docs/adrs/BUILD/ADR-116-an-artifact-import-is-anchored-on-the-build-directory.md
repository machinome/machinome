# ADR-116: An Artifact Import Is Anchored on the Build Directory

**Status:** Accepted
**Date:** 2026-09-15
**Change:** `import-the-artifact-by-path`
**Extends:**
- [ADR-073: Named Project Models and Per-Model Build Directories](ADR-073-named-project-models-and-per-model-build-directories.md)
**Cites:**
- [ADR-086: State-Dependent SCAD Publishes at Assembly Phase Completion](ADR-086-state-dependent-scad-publishes-at-assembly-phase-completion.md)

## Context and Problem Statement

`projects/Robots/Thor` (`workflow/warts.md`, "Robots/Thor") put an
`AssemblyNode` under `simulation/tools/`, placing a `MolejoNode` declared in
`simulation/`. The generated `.scad` held
`import(file = "flexibles-ElbowBelt-….stl", origin = [0, 0]);` — a bare
basename, resolved against `simulation/tools/`, where that file does not
exist; it sits in `simulation/`. OpenSCAD warns and renders the rest;
`solid snapshot` reports success. The project's author lost a build cycle
to a belt he thought was broken, and the project still has no
belt-viewing helper under `tools/` because moving the assembly beside the
leaf was the only cure.

Measured on a two-package fixture built twice
(`openspec/changes/import-the-artifact-by-path/evidence.md`), the
framework spelled a child's artifact TWO different ways and neither is
right in general:

- `import_optimized()` (`base.py`, pre-change) anchored a rigid leaf's
  import on `os.path.relpath(self.basedir, self.root)` — the ROOT node's
  own source directory — correct only when the root happens to be the
  importing parent.
- Every leaf's `as_scad` emitted the bare basename `local_stl` — an anchor
  on the LEAF's own directory — correct only when the parent sits beside
  the leaf.

They agreed only when the parent and the leaf lived in one package, which
is why the bug read as a molejo defect for a year: a flexible leaf's
`as_scad` always took the bare-basename branch, and the coincidence held
everywhere the author had tried it. Broken the other way too: an
intermediate assembly's own `.scad`, several packages below the root,
held a path anchored on the ROOT's directory and did not resolve from its
own.

The framework had no definition of what an artifact import is relative
TO.

## Decision Drivers

- A parent declared in ANY package relative to a part it places must
  render exactly the geometry a parent beside that part renders — for
  every leaf kind, at every depth, whether or not the artifact was
  already current when the tree was assembled.
- A path a project wrote itself, inside its own `render()`, must be
  reproduced exactly as written.
- The framework's build artifacts stay relative — no developer home
  directory, no non-relocatable build directory — and the ~20 existing
  SCAD expectations in `tests/test_scad_stl.py` must not become
  machine-dependent text.
- One assembled child tree is inlined into more than one `.scad` file at
  more than one depth (a non-rigid assembly is never imported as an STL,
  only inlined), so no single string emitted once can be correct in every
  file that holds it.

## Considered Options

1. **One anchor for the tree — the build directory — re-anchored by the
   file that holds it, at the moment that file is written.** Chosen.
2. **Absolute paths in the generated `.scad`.** Correct everywhere with no
   re-anchoring pass; rejected because it puts the developer's home
   directory into a build artifact, makes a build directory
   non-relocatable, and would turn every SCAD expectation in
   `tests/test_scad_stl.py` into machine-dependent text.
3. **Pass the importing node's directory down through `assemble()`.** The
   natural reading of "resolve from the parent's directory", and
   impossible: a non-rigid child's assembled tree is inlined into more
   than one `.scad` at more than one depth, so there is no single importer
   to anchor on at emission time.
4. **Keep the root anchor and only fix the leaves that emit a bare name.**
   Smaller, and it would fix the Thor reproduction and nothing else,
   leaving every intermediate assembly's own `.scad` wrong — the same bug
   wearing the other hat, and still unstatable as a rule.
5. **Anchor on the project root instead of the build directory.**
   Identical for a project with no declared models; wrong for a declared
   model (ADR-073), whose artifacts live under `_build/<model>/` rather
   than mirroring the project root directly.
6. **Rewrite the `.scad` TEXT with a regular expression when writing it.**
   No solid2 privates, and rejected: an `OpenScadNode` embeds a project's
   own OpenSCAD source verbatim in its `scad_code`, imports and all, and a
   textual pass cannot tell that source's `import()` from the framework's.
7. **Check at build time that every emitted import exists.** Rejected on a
   measurement: a rigid leaf's STL is rendered by an asynchronous OpenSCAD
   process, so the parent's `.scad` is legitimately written before the
   artifact it names exists. The check belongs where the file is read
   (the renderer, see below), not where it is written.

## Decision

Every framework-emitted artifact import is built relative to the BUILD
DIRECTORY of the build (`get_build_dir(self.src)` — the directory the
artifact layout mirrors the source tree under, `_build/` or
`_build/<model>/`, ADR-073) — the same anchor the published document
(`viewer.json`) already uses for its `model` entries. A leaf in `sim/` is
therefore spelled `sim/parts-RigidLeaf-….stl` inside the assembled tree,
whichever node is the root and whichever node later inlines it.

When a node writes its OWN `.scad`, that build-wide path is re-anchored
onto the node's own build directory: `os.path.relpath(os.path.join(<build
dir>, <anchored path>), self.build_dir)`, normalised so a root declared at
the top of the source tree and a parent beside its parts reproduce
today's text byte for byte. This re-anchoring is not decorative: one
assembled child tree is inlined into several `.scad` files at different
depths, and no single relative string is correct in two directories — the
path cannot be finished when it is emitted, only when a file is written.

The marker separating a framework-emitted import from a path a project
wrote itself is the Python type, `_ArtifactImport(import_stl)`: `import_stl`
passes the OpenSCAD call name `'import'` to its base, so the subclass
renders byte-identically, and the marker exists only in Python (a `str`
subclass on the `file` parameter does not survive — `import_stl`
normalises it with `_Path(file).as_posix()`, returning a plain `str`).
Re-anchoring walks a `copy.deepcopy` of the model and rewrites `_params['file']`
on every `_ArtifactImport` it finds, so the tree a parent inlines is
untouched; both attributes are solid2 privates, and the rewrite is
confined to one helper (`_reanchor_artifact_imports`) so a solid2 upgrade
that renames them fails loudly there rather than silently emitting a bad
path.

`AbstractBaseNode.artifact_import(path)` builds the anchored import for
one of a node's own artifact files; every emitter (`assemble()`'s
up-to-date branch, `import_optimized()`, and every leaf kind's `as_scad`)
calls it. `AbstractBaseNode._model_for_own_scad()` returns the deep-copied,
re-anchored model; `scad_code` renders it instead of the un-anchored
`_require_model()`, and `OpenScadNode.scad_code`, which overrides
`scad_code`, calls the same seam. `scad_code` is a node's OWN presentation,
never how a parent inlines a child (a parent uses `assemble()`), so
re-anchoring inside it cannot leak into a parent's text.

### The silence, separately guarded

OpenSCAD 2021.01 reports an unopenable import as
`WARNING: Can't open import file '<path>', import() at line N` on stdout,
with a return code of 0 — `solid snapshot`'s renderer captured that stream
and logged it at `DEBUG`, below the default level, so nothing reached the
maker but a smaller machine in a PNG (evidence, `probe_openscad_missing.py`).
The renderer now inspects both captured streams, promotes any line
OpenSCAD marks `WARNING`/`ERROR`/`DEPRECATED` to a level a normal run
shows (progress output stays at `DEBUG`), and raises a named error
(`OpenScadImportError`, carrying the missing file and the `.scad` that
imported it) when a line reports a file it could not open;
`solid snapshot` catches that error, writes the message to stderr, exits
1, and removes whatever image OpenSCAD wrote. This is string matching
against one tool's message and is explicitly the SECOND guard: the first
is the anchoring rule above, verified by reading the generated `.scad` and
checking the named path on disk, which depends on no OpenSCAD text at
all. It is kept because the cost the Thor finding recorded was not the
wrong path — it was the build cycle spent believing a correct belt was
broken.

## Consequences

- A parent declared in any package relative to the parts it places
  renders the same geometry a parent beside those parts renders, for
  every artifact-emitting leaf kind, at every depth, on the first build
  and on every build after.
- Every node whose build directory is not the build-wide anchor — every
  node of a project whose models live under a package such as
  `simulation/`, i.e. every real project — pays one `copy.deepcopy` of its
  own model per `.scad` write. Measured on the largest real assembly
  fixture the test suite builds (24 leaves): about 1.4 ms total across 25
  `.scad` writes, under 0.7 ms for the costliest single call (evidence.md,
  "The deep-copy cost"). Not free, but small next to the OpenSCAD
  subprocess render each `.scad` eventually feeds.
- `self.root`, previously read by `import_optimized()` for this anchoring,
  is no longer read for any path; it remains set and propagated
  (`base.py:__init__`, `_prepare`; `internal.py`'s `as_scad`/`materialize`)
  because nothing else in this change depended on removing it, and no
  other reader was found.
- `solid snapshot --renderer openscad` fails loudly, naming the missing
  file and the `.scad` that imported it, instead of reporting success over
  a picture with a silently missing part.
- Out of scope, and left as findings for `workflow/warts.md`: a rigid
  leaf's own `.scad` stops describing its geometry after the first build
  (it becomes a self-import of the STL it is meant to regenerate), and
  `mesh_scad_file`/`mesh_stl_file` are vestigial. Neither is this
  anchoring bug.
- `viewer.json`, the export document and the web renderer are unaffected:
  they name artifacts by their own paths and never parse a `.scad`.

## References

- `solid_node/node/base.py` (`_ArtifactImport`, `artifact_import`,
  `_model_for_own_scad`, `_reanchor_artifact_imports`)
- `solid_node/node/exact_leaf.py`, `solid_node/node/flexible.py`,
  `solid_node/node/adapters/{jscad,stl,openscad}.py`
- `solid_node/viewers/openscad.py` (`OpenScadImportError`)
- `solid_node/manager/snapshot.py`
- `tests/cross_package_project/`, `tests/test_scad_import_paths.py`,
  `tests/test_snapshot.py`
- `openspec/changes/import-the-artifact-by-path/` (proposal, design,
  evidence)
- Originating project: `projects/Robots/Thor`. `workflow/warts.md`,
  "Robots/Thor".
