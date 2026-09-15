# Design — import the artifact by path

## The mechanism as it stands

`InternalNode.as_scad` (internal.py:131) collects `child.assemble(self.root)`
for every child and unions the results; `self.root` is the ROOT node's source
directory, set once at construction (`base.py:702`, `self.root = self.basedir`)
and handed down unchanged through `_prepare` (`base.py:844-849`). Two places
turn a child into SCAD text, and they disagree:

- `import_optimized()` (`base.py:908-914`) — for a rigid node whose STL is
  current — emits
  `os.path.join(os.path.relpath(self.basedir, self.root), self.local_stl)`:
  a path relative to the ROOT NODE'S build directory.
- every leaf's `as_scad` emits the bare basename `local_stl`
  (`base.py:821`, `exact_leaf.py:99`, `adapters/jscad.py:94`,
  `adapters/stl.py:201`) or `local_snapshot_stl(values)`
  (`flexible.py:324`): a path relative to THE LEAF'S OWN build directory.

`assemble()` (`base.py:807-841`) takes the first for a rigid node — in both
of its branches, since the `else` branch materialises the artifact and then
calls `import_optimized()` too — and the second for a node that is not rigid,
which is exactly the flexible leaf (`flexible.py:92`, `rigid = False`) and
an assembly (`assembly.py:365`). A non-rigid node's `import_optimized()`
falls through to `self._colorize(self.model)`, so the leaf's own bare
spelling is what reaches the parent.

That is the whole finding. Measured (`evidence.md`): a cross-package parent
gets `../parts-RigidLeaf-….stl` for the rigid and exact leaves — correct
here only because the parent IS the root — and the bare
`parts-FlexLeaf-…-….stl` for the flexible one, on both the first build and
the second. The addendum in the cycle briefing predicted a bare name for
rigid and exact leaves on the FIRST build; the measurement refutes that, for
the reason above: the `else` branch ends in `import_optimized()` as well.
The briefing's conclusion — that the bare name is what a cross-package
parent gets for a flexible leaf, always — holds.

An intermediate assembly is broken the other way: its own `.scad` holds
paths anchored on the ROOT's build directory, and it is not the root, so
`_build/deep/sim/sub/deep/group-….scad` imports `../parts-RigidLeaf-….stl`
and misses.

`optimize = False` produces no import at all — the geometry is inlined
(`base.py:825-834`) — so that path was never affected. Measured too.

## The anchor this change picks

**One anchor for the tree, re-anchored by the file that holds it.**

1. Every framework-emitted artifact import is built relative to the BUILD
   DIRECTORY of the build — `get_build_dir(self.src)`, the directory the
   artifact layout mirrors the source tree under, `_build/` or
   `_build/<model>/`. So a leaf in `sim/` is spelled
   `sim/parts-RigidLeaf-….stl` inside the assembled tree, whichever node is
   the root and whichever node inlines it. This is the same anchor the
   published document already uses for its `model` entries (measured in
   `evidence.md`: `"model": "sim/parts-RigidLeaf-….stl"`), so the two
   descriptions of an artifact finally agree.
2. When a node writes its OWN `.scad`, it re-anchors those paths onto its own
   build directory, prefixing `os.path.relpath(<build dir>, self.build_dir)`.
   The root's prefix is `.` — its build directory IS the anchor when the root
   sits at the top of the source tree — so a root scad comes out exactly as
   it does today.

Step 2 is not decoration: one assembled child tree is inlined into several
`.scad` files at different depths (an assembly is not rigid, so its parent
inlines its whole tree rather than importing an STL of it), and no single
relative string is correct in two directories. The path therefore cannot be
finished when it is emitted; it is finished when a file is written.

### Telling a framework import from a project's

A project may call `import_stl` in its own `render()`, with a path of its own
meaning. Re-anchoring it would corrupt it. The marker is the Python type:

```python
class _ArtifactImport(import_stl):
    """An import of a build artifact, whose path is anchored on the
    build directory until a .scad file claims it."""
```

`import_stl.__init__` passes the OpenSCAD call name `'import'` to its base
(`solid2/core/builtins/openscad_primitives.py`), so the subclass renders
byte-identically; the marker exists only in Python. Verified against the
installed solid2 in `evidence/probe_reanchor.py`, together with the reason a
`str` subclass on the `file` parameter does NOT work — `import_stl`
normalises it with `_Path(file).as_posix()`, which returns a plain `str`.

Re-anchoring walks `_children` and rewrites `_params['file']` on a
`copy.deepcopy` of the model, so the tree the parent inlines is untouched
(same probe). Both attributes are solid2 privates; the rewrite is confined to
one helper in `base.py` so a solid2 change lands in one place.

### Where it lives

- `AbstractBaseNode.artifact_import(path)` — build the anchored
  `_ArtifactImport` for one of this node's artifact files. Every emitter
  calls it: `base.py:821`, `import_optimized()`, `exact_leaf.py:99`,
  `flexible.py:324`, `adapters/jscad.py:94`, `adapters/stl.py:201`.
  `import_optimized()`'s own `relpath(self.basedir, self.root)` computation
  disappears into it, and with it the last use of `self.root` for paths.
- `AbstractBaseNode._model_for_own_scad()` — the deep-copied, re-anchored
  model. `scad_code` (`base.py:1019`) renders that instead of
  `_require_model()`, and `OpenScadNode.scad_code`
  (`adapters/openscad.py:77`), which overrides it, calls the same seam.
  `generate_scad` reads `scad_code`, including the deferred path through
  `phase.defer_scad` (`base.py:1037-1044`), so both publication routes are
  covered by one change.

### What does not move

- `scad_code` is a node's OWN presentation and is not how a parent inlines a
  child — a parent uses `assemble()`. So re-anchoring inside `scad_code`
  cannot leak into a parent's text.
- Existing SCAD expectations in `tests/test_scad_stl.py` (including the
  `deep_project` ones that read `one/two/three/simple_cylinder-….stl`) are
  all taken from a node loaded AS THE ROOT, whose prefix is `.`. They stay
  byte-identical. The `assertIn(node.local_stl, str(assembled))` assertions
  in `test_stl_node.py`, `test_sheet_leaf.py`, `test_build123d_adapter.py`
  and `test_backend_neutral_materialization.py` stay true because an
  anchored path ENDS with `local_stl`.
- `viewer.json`, the export document, the web renderer and every mesh path
  read artifacts by their own file paths and never parse a `.scad`.

## Alternatives rejected

- **Absolute paths in the generated `.scad`.** Correct everywhere with no
  re-anchoring pass, and rejected: it puts the developer's home directory
  into a build artifact, makes a build directory non-relocatable, and would
  rewrite about twenty SCAD expectations in `tests/test_scad_stl.py` into
  machine-dependent text. The framework's build artifacts are relative today
  and stay that way.
- **Pass the importing node's directory down through `assemble()`.** The
  natural reading of "resolve from the parent's directory", and impossible:
  a non-rigid child's assembled tree is inlined into more than one `.scad`
  at more than one depth, so there is no single importer to anchor on at
  emission time. This is precisely what the re-anchor step exists to handle.
- **Keep the root anchor and only fix the leaves that emit a bare name.**
  Smaller — it would fix the Thor reproduction and nothing else — and
  leaves every intermediate assembly's own `.scad` wrong, which is the same
  bug wearing the other hat. The rule would still be unstatable.
- **Anchor on the project root instead of the build directory.** Identical
  for a project with no declared models; wrong for a declared model, whose
  artifacts live under `_build/<model>/` (ADR-073). The build directory is
  the directory the artifact tree actually mirrors, and the one the
  published document already uses.
- **Rewrite the `.scad` TEXT with a regular expression when writing it.**
  No solid2 privates, and rejected: an `OpenScadNode` embeds the project's
  own OpenSCAD source verbatim in its `scad_code`, imports and all, and a
  textual pass cannot tell that source's `import()` from the framework's.
- **Check at build time that every emitted import exists.** Rejected on a
  measurement, not on taste: a rigid leaf's STL is rendered by an
  asynchronous OpenSCAD process (`base.py:1078-1108`), so the parent's
  `.scad` is legitimately written before the artifact it names exists. The
  check belongs where the file is read, which is the renderer.

## The second requirement: the silence

Measured (`evidence/probe_openscad_missing.py`, OpenSCAD 2021.01): an
unopenable import produces `WARNING: Can't open import file '<absolute
path>', import() at line N` **on stdout**, a return code of 0, and a written
PNG. `OpenScadRenderer.render` (`viewers/openscad.py:26-30`) runs with
`check=True, capture_output=True` and then `logger.debug(result.stdout)`, so
the message is captured and thrown away below the default log level;
`manager/snapshot.py:215-218` only catches `CalledProcessError`, which never
comes.

So: the renderer inspects both captured streams, logs them at a level a
normal run shows, and raises when a line reports a file it could not open;
`snapshot.py` turns that into `exit 1` with no image. This is string
matching against one tool's message, and the design admits the coupling: a
future OpenSCAD that renames the warning silently returns the command to
today's behaviour. That is acceptable because it is the SECOND guard — the
first is the spec rule above, tested by reading the generated `.scad`, which
depends on no OpenSCAD text at all. It is kept in this change because the
cost recorded in the wart was not the wrong path, it was the hour spent
believing a correct belt was broken.

The matched text and the version it was measured against are recorded beside
the code, and the renderer names the `.scad` it was rendering so the report
is actionable even if OpenSCAD's own wording drifts.

## ADR

**ADR-116 — an artifact import is anchored on the build directory and
re-anchored by the file that holds it** (BUILD; next free number, checked
against `docs/adrs/README.md`, whose highest is 115). It is a durable
convention rather than a bug fix: it fixes the meaning of every path the
node layer writes into SCAD, states why that meaning cannot be settled at
emission time, and makes the SCAD document and the published document agree
on how an artifact is named. It extends ADR-073 (per-model build
directories, which is why the anchor is the build directory and not the
project root) and cites ADR-086 (state-dependent SCAD publishes at assembly
phase completion — the deferred publication path that must go through the
same seam).

## Risks

- **solid2 privates.** `_children` and `_params` are not public API. Confined
  to one helper; a solid2 upgrade that renames them fails loudly in the new
  path-resolution tests rather than silently emitting bad paths.
- **A project subclassing a leaf adapter and overriding `as_scad`.** It will
  keep emitting a bare name, which stays correct for a parent in its own
  package and wrong for one elsewhere — exactly today's behaviour, no worse.
  The legacy `as_scad` seam is already recognised by
  `_uses_legacy_scad_materialization` (`leaf.py:90-104`); this change does
  not extend it.
- **Deep-copying the model per `.scad` write.** One copy per node per build
  of an object tree the build already renders to text; the render itself is
  the larger cost. The copy is skipped only when the prefix is `.`, which is a root
  declared at the top of the source tree — the test fixtures, not a real
  project, whose models live under `simulation/`. Every real project pays
  the copy on every `.scad` write; task 2.9 measures it.

## Reviewer's notes (ratification, 2026-09-15)

Ratified with the mechanism as designed — the anchored `_ArtifactImport`
and the re-anchoring copy at write time — and three corrections applied
above rather than returned for revision:

1. **The copy is not free.** The prefix is `.` only for a root declared at
   the top of the source tree, which is where the test fixtures sit and
   where no real project's models sit (`simulation/…` throughout this
   workspace). The "pays nothing" claim is withdrawn; the implementer
   measures the copy (task 2.9). The cost is bounded — one copy per node per
   `.scad` write, coalesced per phase under ADR-086 — and the render to text
   is of the same order, so the design stands.
2. **Normalise the re-anchored path.** Prefixing `relpath(build_dir,
   self.build_dir)` literally gives `../sim/x.stl` for a parent beside its
   parts and `./x.stl` for a top-level root, neither byte-identical to today.
   The spelling is `os.path.relpath(os.path.join(build_dir, anchored),
   self.build_dir)` (task 2.1), which the same-package control and the
   `test_scad_stl.py` expectations then hold to.
3. **OpenSCAD's output.** The default log level is INFO
   (`solid_node/core/logging.py`), and a render prints about eight progress
   lines, so "everything OpenSCAD reports" would put them on every snapshot.
   Narrowed to warnings, errors and deprecations at WARNING; progress stays
   at DEBUG (spec, proposal, task 2.5).

One inaccuracy left in "The mechanism as it stands", noted here rather
than rewritten because the fix does not depend on it: for a `Solid2Node`
the `else` branch does not materialise the STL synchronously — the render
is an asynchronous OpenSCAD job (`generate_stl`, `StlRenderStart`), so on
the very first pass `import_optimized()` falls through to `self.model`,
the inlined `cube(…)`, which carries no path at all; the builder's later
pass, once the job has landed, takes the root-relative import the
measurement shows. The exact, STL and JScad leaves materialise inside
`as_scad`, so their first pass already imports. Either way no bare name
reaches a parent from those kinds, which is what the measurement says.
