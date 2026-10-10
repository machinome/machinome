## Why

`workflow/warts.md`, section "3DPrintedClocks", the entry recorded on
10 September 2026 while Wall Clock 22's hanging-weight datum was being
changed:

> **Generated-artifact freshness is not dependable for source-bound CAD
> leaves.** While changing Wall Clock 22's source-derived hanging-weight
> datum, `machinome test wall_clock_22 --faceted` continued to compare an
> older generated assembly pose. Removing only that model's ignored
> `_build/wall_clock_22` cache was needed to force regeneration; the next
> run also tried to reuse a deleted `clock-Pillars...stl` artifact and
> raised `FileNotFoundError`. The artifact identity appears not to include
> every source adapter dependency, and the test artifact index can retain
> paths that the producer no longer restores. A project should never need
> cache deletion for a source edit to reach a spatial assertion. [...]

An investigation on 7 October 2026, at the bench commit `297d9286`, ran
the entry again on a byte-identical scratch copy of
`projects/3DPrintedClocks` (project commit `ec2a05d1`). Two of its three
halves no longer reproduce: an assembly's placement is computed on every
run, so an edit to the weight datum moves the weight at once, and the
retained path that raised `FileNotFoundError` belonged to the OpenSCAD-era
assembly `.scad` files, an artifact kind removed by `748d6d94`. Removing a
leaf's STL, or the whole model build directory, rebuilds cleanly.

What remains is one mechanism: **a leaf does not track all the code it
runs.** `machinome/node/sources.py`, `_project_file`, drops every
`__init__.py` the import walk reaches. Wall Clock 22's movement is built
through the project's own library by `from clocks import (AnchorEscapement,
Assembly, ..., SimpleClockPlates, Weight)`, and `clocks/__init__.py` is
eighteen `from .x import *` lines. The walk drops that file, so it never
reaches the modules behind it: the clock's leaves track 3 of the 30
`clocks/` modules they execute (`cq_svg.py`, `types.py`, `utility.py`,
reached through named submodule imports elsewhere). An edit to the
bottom-pillar radius in `clocks/plates.py` therefore leaves every artifact
"current": the pillar STL and BREP on disk keep the old shape (31.1 mm)
while the live render has the new one (37.1 mm), the run rewrites no file,
and `machinome test` checks collisions on the old pillars and plates
placed by the new values (the live `frame_bottom` moved from -15.55 to
-18.55). Nothing warns. Deleting one pillar STL by hand then regenerates
that STL with the new shape while its BREP keeps the old one, so one leaf
holds two artifacts that disagree.

The same gap reproduces on the bench in the shape of the suite's own
fixture (design.md, Context): a leaf doing `from .library import WIDTH`,
where `library/__init__.py` is `from .measures import *`, tracks only its
own file; after it is built, an edit to `library/measures.py` leaves its
STL up to date.

This contradicts `build-pipeline`'s "Mtime-equality caching": "Where the
contributing set cannot be determined exactly, the system SHALL track more
files rather than fewer." The code follows a sentence of ADR-033, "The walk
... never follows the `__init__.py` of a package it traverses", whose stated
reason covers only a package that contains the importing file: in the
conventional layout that file is the root assembly's own source, so
following it would make every node depend on every node. A sibling
library package such as `clocks` is not that case.

## What Changes

- **The import walk follows the `__init__.py` of a package that does not
  contain the importing file.** When a tracked module names a project
  package in an import (`from clocks import Weight`, `from .library import
  WIDTH`, `import clocks`) and that package's directory does not contain
  the module, its `__init__.py` joins the node's tracked set and the walk
  continues through what it imports. The `__init__.py` of a package that
  contains the importing module (the module's own package or one above it,
  which is where a root assembly lives) is still never followed, for
  ADR-033's reason. Everything else in the walk is unchanged: modules
  outside the project root and the framework are not tracked, relative
  imports are resolved through the interpreter, and the per-file import
  cache stays keyed on the file's observation, since the new test depends
  only on the importing file's own path.
- **One rebuild after upgrading** for every project whose nodes import
  through a sibling package. Their tracked sets grow, so their artifacts
  are re-derived once and then report current. In the catalogue that is
  3DPrintedClocks (every clock model, through `clocks/__init__.py` and
  `simulation/shared/__init__.py`) and the projects whose node modules
  import a submodule of a sibling package whose `__init__.py` is empty
  (the set gains that empty file); design.md, "What the catalogue loses",
  gives the scan.
- `machinome develop` watches the files it now tracks, because the watch
  loop consumes the same set: an edit to `clocks/plates.py` is noticed.

**Deliberately out**, with the reason:

- the parent packages of a dotted import (`from clocks.types import X`
  executes `clocks/__init__.py`, but the walk still follows only
  `clocks.types`). The imported name comes from the module the statement
  names, not from the parents Python runs on the way to it; following
  every parent would add every library facade to every node that names one
  of its submodules, a cost no finding asks for;
- a library module reaching its own package's facade (`clocks/plates.py`
  doing `from . import X` where `X` is re-exported by `clocks/__init__.py`
  from another module). That `__init__.py` contains the importer and stays
  unfollowed, so such a name is tracked only if the node reaches the facade
  some other way. `clocks/` never imports its own facade (a grep of the
  library finds no `from . import` or `from clocks import`), and the scan
  finds no other catalogue library with a non-empty `__init__.py` that a
  node module imports from outside it;
- tracking every module the generation imported
  (`SourceGeneration.imported_paths`), which ADR-033 rejected because it
  attributes every module to every node;
- a workaround in the project (importing named submodules instead of the
  facade): the spec puts the obligation on the framework, and
  3DPrintedClocks is read-only to this cycle;
- the two halves of the entry that no longer reproduce (the stale pose and
  the retained path): nothing to change; they close with the entry, their
  measurements recorded in the resolved record.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `build-pipeline`: "Mtime-equality caching" — the source-set paragraph
  says which package `__init__.py` files a node tracks (a package named by
  a tracked module that does not contain it) and which it does not (a
  package that contains the importing module), and why; two scenarios
  added ("A module behind a sibling package's `__init__` is tracked", "A
  package containing the importer is not followed"), every existing
  scenario carried.
- `source-closure-cost`: "The tracked source set is unchanged" — the set
  the indexed package lookup must reproduce is the one `build-pipeline`
  defines, rather than the one the system produced when that requirement
  was written; its three scenarios carried unchanged.

## Impact

- Code: `machinome/node/sources.py` only (`_parse_project_imports` passes
  the importing file to `_project_file`, which drops an `__init__.py` only
  when its package directory contains that file; the comment above the test
  and the module's own wording follow).
- Tests: `tests/test_source_set.py` (two red tests and one guard),
  `tests/source_set_project/` (a sibling package `library/` with
  `__init__.py` and `measures.py`, a leaf `wide.py` importing through it, a
  leaf `peg.py` reaching a sibling module through `from . import`, and
  the fixture `__init__.py` importing both, as a root assembly does).
- Records: an amendment to ADR-033 (dated section; the header's
  "Amended by" line and the ADR index entry follow), `docs/architecture.md`
  (the invariant that repeats ADR-033's sentence), the manual's
  `docs/concepts/node-tree.rst` (its bullet "The walk never follows a
  package's `__init__.py`"), and one changelog bullet saying that projects
  importing through a sibling package rebuild once.
- Artifacts: no artifact path, identity, recipe or document field changes;
  only which sources an artifact's currency is computed over.
- Cost, measured on Wall Clock 22's scratch copy with the rule patched into
  one process: `load_node` 10.7 s against 11.0-11.2 s; the first build
  after the change re-derives the model (288 files, 32.6 s), a warm build
  then rewrites nothing in 0.42 s (0.17 s today).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change narrows a sentence of an accepted ADR to the case its own rationale
covers and keeps the spec's stated direction ("more files rather than
fewer"); it is proposed as an ADR amendment within that mandate, for the
orchestrator's adversarial review. It is validated in the originating
project, 3DPrintedClocks, on a scratch copy for the edit experiment and on
the unchanged project for the one-time rebuild and the warm run; the
project itself is not edited.
