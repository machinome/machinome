## 1. Baseline on the unmodified tree

- [x] 1.1 Create `openspec/changes/scad-presentation/evidence.md` in the shape
  of the archived cycles' (`2026-10-03-expression-type/evidence.md`), with the
  bench commit.
- [x] 1.2 The presentation golden (design.md Decision 8): write
  `tests/scad_presentation_golden.py` and its fixture package
  `tests/scad_presentation_project/` (reusing `tests/cross_package_project`
  or `tests/deep_project` for re-anchoring where they serve), covering a
  colour on a leaf and on an assembly, `fn` on a `Solid2Node`, an `optimize =
  False` assembly, a single-child and an empty non-rigid assembly, an assembly
  in another package than its parts, an `StlNode`, an exact leaf, a faceted
  `FusionNode` with a current fused artifact, a numerically bound flexible
  leaf, an `OpenScadNode`, a project leaf overriding `as_scad`, and a
  project's own `import_stl` inside a `Solid2Node` render. It builds under a
  temporary `SOLID_BUILD_DIR` and records the SHA-256 and length of every
  node's `scad_code`, and of every `.scad` file under the build directory
  after one `assemble()` of the root, by path relative to the build
  directory, each file marked with whether its node is SCAD-authored (a
  `Solid2Node`, an `OpenScadNode`, the leaf overriding `as_scad`), in
  `tests/data/scad_presentation_golden.json` with the bench commit. Run twice
  in separate processes, record that both agree. Not collected by pytest; a
  characterisation (`--check`): before and after, every node's `scad_code`
  and every SCAD-authored leaf's file byte-identical and present; after the
  change, every other recorded file absent (design.md Decisions 3 and 8),
  which `--check` reports as expected rather than as a difference.
- [x] 1.3 Run `tests/expression_type_golden.py --check` on the unmodified
  tree; record the summary line.
- [x] 1.4 Run, on the unmodified tree, `tests/test_expression_type.py`,
  `tests/test_scad_engine_seam.py`, `tests/test_openscad_engine.py`,
  `tests/test_openscad_dependency.py`, `tests/test_backend_neutral_materialization.py`,
  `tests/test_scad_import_paths.py`, `tests/test_generation_dedup.py`,
  `tests/test_snapshot.py`, `tests/test_manager_develop.py`,
  `tests/test_flexible_node.py`, `tests/test_stl_node.py`,
  `tests/test_leaf_contract_faceted.py`, `tests/test_node_naming.py`,
  `tests/test_builder_lifecycle.py`, `tests/test_build_publication.py`,
  `tests/test_molejo_adapter.py`; record counts and wall time. One pytest
  process at a time.

## 2. Red tests

- [x] 2.1 `tests/test_scad_presentation.py`, the AST rules (design.md
  Decision 9): outside `machinome/openscad/`, the `solid2` importers are
  exactly `node/solid2.py`, `node/openscad.py` and
  `manager/templates/project/root/__init__.py`, each commented with the
  cycle that removes it (7, 7, 8); the importers of `machinome.openscad` or
  beneath it are exactly `scad_engine.py` and `node/solid2.py` (7). Red: four
  and three extra modules. Shrink `tests/test_expression_type.py`'s two
  lists to the same sets in the same commit (red there too until 4-6).
- [x] 2.2 Same file, no SolidPython and no engine, in subprocesses under
  `tests/exact_engine_absent.py`'s finder, once with `absent=solid2` and once
  with `absent=machinome.openscad`: `machinome build` of an all-STL fixture
  project and of an all-exact fixture project exits 0, writes `viewer.json`
  and every STL (and BREP), leaves no `.scad` under the build directory, and
  logs nothing naming SCAD presentation; on a fixture node, `assemble()`,
  `build_stls()` and `mesh` succeed and `assemble()` returns a
  `machinome.node.presentation` value. Red: `No module named 'solid2'` at
  `node/base.py`'s import; `.scad` files written.
- [x] 2.3 Same file, refusals: with each module absent, `scad_code` and
  `generate_scad()` on a fixture `StlNode` subclass raise
  `ScadEngineUnavailable` whose message is the spec's (node name and class,
  "its SCAD text is written by the OpenSCAD engine", the module, `pip install
  solidpython2` or reinstalling machinome, no `machinome[`); a project leaf
  overriding `as_scad` refuses at its materialization naming itself, and
  `machinome build` of a fixture holding it (with `absent=machinome.openscad`)
  fails naming it with no `.scad` written; `Snapshot.handle` with the
  OpenSCAD renderer and the engine absent exits 1 naming the renderer, the
  module and `--renderer web`, before the node is loaded, with a patched
  runner never called, no image and no `.scad` left. Red.
- [x] 2.4 `tests/test_scad_engine_seam.py` (extend): `CONTRACT == 2` on the
  seam and on the provider; a stub provider declaring `1` raises
  `ScadEngineIncompatible` naming `1`, `2` and the provider; with none,
  saying none and naming `2`; `require_scad_engine` returns the provider;
  `OpenScadUnavailable` is a subclass of `ScadEngineUnavailable` and its
  message is unchanged; a counting stub provider sees `scad_text` called once
  for each stale SCAD-authored leaf a fixture build materializes and never by
  `assemble()`, and `require_binary` called by a
  stale `Solid2Node`'s `generate_stl` (with `Popen` patched) and by the
  snapshot renderer (with the runner patched). Red: contract 1, no
  operations.
- [x] 2.5 `tests/test_openscad_engine.py` (extend): `scad_text` of the
  spec's placed, coloured import equals the SolidPython rendering of the same
  calls; a symbolic angle is written as its closed text unquoted; a union of
  none is `union();\n`; `fn=24` prefixes `$fn = 24;\n\n`; `Authored` content is
  rendered as SolidPython renders it; `machinome.openscad` exports neither
  `scad_text` nor `require_binary`. Red.
- [x] 2.6 `tests/test_scad_presentation.py`, the description:
  `machinome.node.presentation` holds the six types; `reanchored` rewrites
  only `ArtifactImport` paths, as `_reanchor_artifact_imports` does today for
  the same paths, never enters `Authored`, and leaves its input unchanged;
  `Rotation.presented(child)`/`Translation.presented(child)` hold the
  operation's own value objects (identity, not copies). Red.
- [x] 2.7 `tests/test_scad_presentation.py`, written only where read (design.md
  Decision 3), with the engine installed: a fixture project
  `tests/scad_where_read_project/` holding an assembly that places a faceted
  `FusionNode`, a numerically bound flexible leaf, an exact or `StlNode`
  leaf and a `Solid2Node` leaf. `machinome build` (a `Builder` with
  `watch=False`) into a temporary build directory leaves exactly one `.scad`,
  the `Solid2Node`'s, byte-identical to its golden entry (1.2), and no
  per-binding snapshot STL of the flexible leaf; `assemble()` of the root
  afterwards writes or rewrites no `.scad`; `Builder` takes no `scad_output`.
  Red: every node's `.scad` written by the build, and the snapshot STL.
- [x] 2.8 Same file, the sweep: the 2.7 fixture's build directory seeded
  with the `.scad` files and currency records the unmodified tree's build
  leaves for the assembly, the fusion, the flexible leaf, the native leaf and
  the root (generated on the unmodified tree, or written at their
  `scad_file` paths with `_publish_scad`), plus the `.scad` of a
  `Solid2Node` under a name no longer in the tree; a successful build ends
  with the `Solid2Node`'s `.scad` and its record as the only `.scad` files
  and records; a second build with the leaf's STL current keeps its `.scad`.
  Red: every seeded `.scad` spared by kind.
- [x] 2.9 Same file, the snapshot on demand: `Snapshot.handle` of the 2.7
  fixture's root with the OpenSCAD renderer (its runner patched, a stub
  reading the `.scad` it is given and writing the image) gives OpenSCAD the
  root's `.scad` at its `scad_file`, its text the root's `scad_code` after
  the same keyframe, every `import(file = ...)` in it resolving from its
  directory, and no other node's `.scad` except the `Solid2Node`'s beside
  it; two snapshots at `--time 0` and `--time 0.5` give each pose's text in
  turn. Corrected 4 October 2026 (design.md Decision 3, "Correction"): after
  the render the root's `.scad` and its record are gone, also when OpenSCAD
  fails; a SCAD-authored root keeps its own; a root `.scad` an interrupted
  render left is removed by a build that republishes the same document. With
  `--renderer web` (the browser renderer's capture patched) no `.scad` is
  written beyond the `Solid2Node`'s materialization. Red: every node's
  `.scad` written by the snapshot's `assemble()` under either renderer, and
  the root's spared by the following build.
- [x] 2.10 Characterisation, green before and after (Decision 9, "Develop"):
  with `has_bundle` patched false, `Develop.handle` exits 1 with
  `INSTALL_REMEDY` and starts neither `Popen` nor `Process`; the develop
  builder as `run_builder` constructs it (`scad_output=False` on the
  unmodified tree; no such parameter after the change) of a fixture mixing
  one `Solid2Node` with exact leaves writes that leaf's `.scad` and no
  other.
- [x] 2.11 Run 2.1-2.10 on the unmodified source in one pytest process;
  record every red test and its reason, verbatim, and the green
  characterisations.

## 3. The description

- [x] 3.1 `machinome/node/presentation.py`: `ArtifactImport`, `Color`,
  `Rotate`, `Translate`, `Union`, `Authored` (immutable; values held by
  reference) and `reanchored(description, build_dir, own_build_dir)`; no
  import of `solid2` or of the engine.
- [x] 3.2 `node/operations.py`: `Rotation.presented(child)` and
  `Translation.presented(child)` in place of `.scad()`; drop the `solid2`
  import.

## 4. The engine and the seam

- [x] 4.1 `machinome/scad_engine.py`: `CONTRACT = 2`; the remembered missing
  module; `ScadEngineUnavailable`; `require_scad_engine(needed_by, reason,
  alternative=None)` with the two remedies of design.md Decision 4; the
  module docstring listing the contract's operations and the requiring paths.
- [x] 4.2 `machinome/openscad/engine.py`: `CONTRACT = 2`;
  `scad_text(description, fn=None)` mapping each description type to the
  SolidPython call of design.md's table and `Authored` content through,
  `scad_render`, the `$fn` prefix; `require_binary(...)` delegating to
  `machinome.openscad.binary.require_openscad` at call time.
- [x] 4.3 `machinome/openscad/binary.py`: `OpenScadUnavailable` derives from
  `machinome.scad_engine.ScadEngineUnavailable`, its message unchanged.

## 5. The node modules

- [x] 5.1 `node/base.py`: no `solid2` and no `machinome.openscad` import;
  `artifact_import` returns `ArtifactImport`; `_colorize` returns `Color`;
  `assemble()` builds the description through `operation.presented` and
  calls `generate_scad()` nowhere (its two calls go; no skip log exists);
  the predicate `scad_authored` (provisional), false on
  `AbstractBaseNode`; `_model_for_own_scad` uses `reanchored` (no deep
  copy); `_ArtifactImport` and `_reanchor_artifact_imports` removed;
  `scad_code` asks `require_scad_engine(f'node {name} ({qualname})', 'its
  SCAD text is written by the OpenSCAD engine').scad_text(..., fn=self.fn)`;
  a non-description `as_scad` result held as `Authored`; `generate_stl`
  resolves the binary through `require_scad_engine(...).require_binary(...)`
  with today's words. The runner (`stl_builder_command_for`, `Popen`,
  `StlRenderStart`) is untouched.
- [x] 5.2 `node/internal.py` and `node/flexible.py`: `Union` in place of
  `union()`; drop the `solid2` import. Every docstring naming "a solid2
  object" for the presentation says "presentation description".
- [x] 5.3 `node/openscad.py`: `scad_code` takes its module call from the
  engine's `scad_text` of `_model_for_own_scad()`; `scad_authored = True`;
  its `render()` and SolidPython parsing stay (cycle 7). `node/solid2.py`:
  `scad_authored = True` and nothing else (its imports stay, cycle 7).
  `node/leaf.py`: `scad_authored` answers `_uses_legacy_scad_materialization()`
  (false on `FlexibleNode`, as that predicate already is).
- [x] 5.4 `node/leaf.py`, `node/exact_leaf.py`, `node/stl.py`,
  `node/jscad.py`, `node/sheet_leaf.py`: docstrings of `as_scad` and
  `artifact_import` (the description; the engine writes SCAD); no behaviour
  change.

## 6. The build and the snapshot command

- [x] 6.1 `viewers/openscad.py`: `OpenScadRenderer.require_engine()` calls
  `require_scad_engine('the OpenSCAD snapshot renderer', 'it renders the SCAD
  the OpenSCAD engine writes', 'use --renderer web')`;
  `OpenScadRenderer.present(node)` writes the root's `.scad` on demand
  (`node.generate_scad()`, at the root's `scad_file`); `render` resolves the
  binary through the provider's `require_binary` with today's words and, in
  a `finally`, removes the root's `.scad` and its record once OpenSCAD has
  read it, unless the root is SCAD-authored (correction of 4 October 2026);
  no `machinome.openscad` import. (Method names provisional.)
- [x] 6.2 `manager/snapshot.py`: for the OpenSCAD renderer, calls
  `require_engine()` before the node is loaded, and `present(node)` inside
  the project build lock right after `assemble()`, so the root's `.scad` is
  written for the snapshot's pose; the web renderer calls neither; catches
  `ScadEngineUnavailable` from the seam in place of `OpenScadUnavailable`,
  printing the message and exiting 1; no `machinome.openscad` import.
- [x] 6.3 `core/builder.py`: `_present_scad_if_requested`, its two calls and
  the `assembly` phase they open are removed, and `Builder` loses
  `scad_output`; `_sweep_unreferenced_artifacts` no longer spares `.scad` by
  suffix in `kept()`, walks `self.node`'s tree and adds to `referenced` the
  build-relative `scad_file` of every node whose `scad_authored` holds (its
  currency record follows through `currency.describes`), and drops
  `collect_snapshots`; the comment there says why. `manager/develop.py`:
  `run_builder` loses `scad_output` (its one caller passed false).

## 7. Existing tests

- [x] 7.1 Tests rendering `assemble()`'s or `as_scad()`'s result with
  `scad_render`, or comparing it to SolidPython objects
  (`test_generation_dedup.py`, `test_stl_node.py`, `test_sheet_leaf.py`,
  `test_build123d_adapter.py`, `test_molejo_adapter.py`, `test_two_pipes.py`,
  `test_leaf_contract_faceted.py`, `test_source_set.py`,
  `test_backend_neutral_materialization.py` and any other the suite finds)
  render through `scad_engine().scad_text(...)`; their asserted text is
  unchanged.
- [x] 7.2 Tests that read a `.scad` a build, a snapshot or `assemble()` left
  for a node that is not SCAD-authored (`test_scad_import_paths.py`,
  `test_build_publication.py`, `test_snapshot.py`, `test_two_pipes.py`,
  `test_generation_dedup.py`'s assembled cases and any other the suite
  finds) call `generate_scad()` on that node first, keeping their asserted
  text, or, where build output is their subject, assert the file's absence.
  `test_builder_lifecycle.py`'s
  `test_the_sweep_spares_inputs_locks_and_in_flight_temporaries` drops
  `part.scad` from what is spared (it is now removed) and a sibling test keeps
  a SCAD-authored `part`'s `.scad`. Tests constructing `Builder` or
  `run_builder` with `scad_output` drop it. No test is weakened: each change
  is recorded in the evidence with the test's name and why.
- [x] 7.3 Tests patching `machinome.node.base.require_openscad` patch
  `machinome.openscad.binary.openscad_binary` (or the seam's
  `require_scad_engine`) instead; tests importing `OpenScadUnavailable` keep
  importing it from `machinome.openscad.binary`.
- [x] 7.4 Tests of `Rotation.scad`/`Translation.scad` move to `presented`.
- [x] 7.5 `tests/expression_type_golden.py --check` (0 differences) and
  `tests/scad_presentation_golden.py --check` (0 differences; the
  presentation files reported absent as expected); record both.
- [x] 7.6 The full framework suite, one process; record counts and wall time
  against 1.4's files and the last full run on the campaign line.

## 8. Docs

- [x] 8.1 `docs/architecture.md`: the SCAD presentation paragraphs (the core
  describes, the engine writes; `assemble()` without the engine), the
  operations' consumers (`.scad()` is `presented()`), the re-anchoring
  paragraph (ADR-116 over the core's description), the source map rows for
  `node/presentation.py`, `scad_engine.py` and `openscad/engine.py`.
- [x] 8.2 `docs/concepts/publishing.rst`: the build directory holds a
  `.scad` only for an OpenSCAD-family part (a `Solid2Node`, an `OpenScadNode`,
  a leaf overriding `as_scad`), from `build` and `develop` alike; the
  root's is written by `machinome snapshot --renderer openscad` only while
  OpenSCAD draws it, and every build removes any `.scad` no current part
  writes;
  `docs/reference/api.rst`: `LeafNode.as_scad` and `artifact_import` as the
  delta says, and `assemble()` writing no file.
- [x] 8.3 `docs/project/changelog.rst`, under Unreleased, the bullet:

  > **The SCAD presentation is the OpenSCAD engine's:** machinome's node
  > base no longer imports SolidPython. ``assemble()`` composes a
  > description of the node's SCAD presentation (artifact imports, colours,
  > rotations, translations, unions and the geometry an OpenSCAD-family part
  > authored) and the OpenSCAD engine, ``machinome.openscad``, writes the
  > ``.scad`` text from it, byte for byte as before. ``assemble()`` therefore
  > needs neither SolidPython nor the engine, and it writes no file of SCAD:
  > without them a project of exact, STEP or STL parts builds, tests,
  > exports and publishes, while asking for SCAD text (``scad_code``,
  > ``generate_scad()``, an OpenSCAD-family part, ``machinome snapshot
  > --renderer openscad``) refuses naming the missing module and its
  > install.
  >
  > **Breaking, for OpenSCAD users: a ``.scad`` is written only where
  > machinome reads it.** ``machinome build`` writes the ``.scad`` of an
  > OpenSCAD-family part (a ``Solid2Node``, an ``OpenScadNode``, a part
  > overriding ``as_scad``), from which OpenSCAD renders its STL, and no
  > other: it no longer writes the ``.scad`` of an assembly, of a fusion or
  > of a flexible part (nor of an exact, STEP, STL, JSCAD or sheet part, nor
  > a flexible part's per-pose snapshot STL), and the next build removes
  > those an earlier build left in the build directory. A machine's SCAD
  > text is ``node.scad_code``, for any node; ``machinome snapshot
  > --renderer openscad`` writes the root's ``.scad`` for the pose it
  > renders only while OpenSCAD draws it, and removes it afterwards. Every
  > ``.scad`` a
  > build writes is the text OpenSCAD renders the part's STL from, byte for
  > byte what it was, except that the file of a coloured OpenSCAD-family
  > part declaring ``optimize = False`` is no longer overwritten with its
  > coloured presentation after the render (corrected 4 October 2026,
  > design.md Decision 8). This also fixes a defect: a later build, test
  > or export process no longer replaces the ``.scad`` of a current
  > OpenSCAD-family part with an import of its own STL. Breaking for code outside
  > projects: ``assemble()``, ``as_scad()`` and ``artifact_import()`` return
  > machinome's presentation description instead of a SolidPython object
  > (render it with the engine's ``scad_text``), ``Rotation.scad()`` and
  > ``Translation.scad()`` are removed, and ``Builder`` no longer takes
  > ``scad_output``; no project uses any of them. ``OpenScadUnavailable`` is
  > now a ``machinome.scad_engine.ScadEngineUnavailable`` (ADR-172,
  > ADR-173).

- [x] 8.4 `workflow/ongoing/lean-core.md`: the "Empirical validation" table
  gains the row for `scad-presentation` (Locks/Pin_tumbler_lock, why, the
  result in one sentence, the evidence path); "Where the core reaches each
  kernel" says the SCAD presentation is the engine's (`node/base.py`,
  `operations.py`, `internal.py`, `flexible.py` import no solid2; the
  remaining importers are the two leaves and the template); "Import paths"'
  OpenSCAD engine row adds that the provider writes SCAD text; "Layers" item
  6 is marked done with its ADRs and evidence path, and records that the
  `develop` fallback it named was removed by ADR-103 before the campaign, and
  the pilot's decision of 3 October 2026 on design.md Decision 3: option A, a
  `.scad` written only where a path reads it (a SCAD-authored leaf's for its
  STL, the root's on demand for the OpenSCAD snapshot renderer), with option
  B (every build's `.scad` kept when the engine is installed) rejected
  because those deliverables served a reader machinome does not have.

## 9. Stop and report (the applier)

- [ ] 9.1 With 1 to 8 done and the suite green, stop before any commit and
  report to the orchestrator: the diff stat, the red and green results, the
  suite's counts, both goldens' summaries. The applier spawns no agent and
  runs neither validation below.

## 10. Empirical validation (the orchestrator)

- [ ] 10.1 **Deep, Locks/Pin_tumbler_lock,** by a validator subagent the
  orchestrator briefs and launches, from design.md Decision 11:
  - *Where.* `/home/asa/devel/machinome/projects/Locks/Pin_tumbler_lock`, on
    the branch `lean-core-validation` in a worktree under the project's own
    `WTs/`; never merged, never pushed. Everything with `PYTHONPATH=<bench>`
    and the workspace venv, into scratch build directories, one process at a
    time.
  - *Legs.* After 9.1, the change uncommitted in the bench, compared with the
    fifth cycle's after leg the orchestrator holds (a4a1f84): `machinome
    build`; `machinome test --faceted`; `machinome export --set key_delta=0
    -o <scratch>`; the SHA-256 of every `.scad` under the scratch build
    directory and of `manifest.json` (not the STL). Expected: the same test
    counts; after the build leg, exactly 11 `.scad` files, the `OriginalPart`
    (`Solid2Node`) leaves' `simulation/parts-*.scad`, each byte-identical to
    the file the fifth cycle's single-process build wrote for the same path
    (its snapshot before leg; corrected 4 October 2026: not its three-process
    after leg, whose `parts-*` files were mostly self-imports a later
    process's `assemble()` wrote, design.md Decision 8), and no
    `simulation/lock-PinTumblerLock-*.scad`, `simulation/lock-Plug-*.scad`
    or `simulation/flexibles-PenSpring-*.scad`, nor the `PenSpring`'s
    per-binding snapshot STL; after all three legs, every `.scad` a
    `simulation/parts-*.scad`, and every `lock-*` and `flexibles-*` file of
    the fifth cycle's 24 absent;
    `manifest.json` identical or differing only in OpenSCAD's STL-derived
    noise as recorded by the fifth cycle.
  - *Snapshot on demand.* `machinome snapshot --renderer openscad -o
    <scratch>/lock.png --imgsize 640x480` on the root after those legs, into
    the same scratch build directory: the PNG exists, its size recorded (not
    its bytes); no `simulation/lock-PinTumblerLock-*.scad` afterwards (the
    renderer removes it once drawn, design.md Decision 3, "Correction"; the
    framework tests pin what OpenSCAD is given), no `lock-Plug-*` or
    `flexibles-*` `.scad`, and the 11 `parts-*` files remain. Then
    `machinome build` into the same directory: the 11 `parts-*` files
    remain and no other `.scad`. Then the snapshot with
    `machinome.openscad.engine` unfindable (a `sitecustomize` carrying
    `tests/exact_engine_absent.py`'s finder, `absent=machinome.openscad.engine`,
    on `PYTHONPATH`): expected a refusal naming the OpenSCAD snapshot
    renderer, `machinome.openscad.engine`, reinstalling machinome and
    `--renderer web`, exit 1, no PNG and no root `.scad`. (Before the change
    the same command writes an image: the engine is not asked for
    presentation.)
  - *Lingering files.* A fresh scratch build directory seeded with `cp -a`
    of the project's own `_build/` (31 `.scad` files from earlier builds on
    3 October 2026: `lock-*`, `flexibles-*`, `poses-*`, `_probe_old-*` and
    other parameter sets' `parts-*`; record the count found), then
    `machinome build` into it. Expected, whether or not the build changes
    the copied `viewer.json`: exactly the 11 `parts-*.scad` of
    the current tree remain, each with its currency record; every other
    `.scad` and its record is gone. The project's `_build/` is only read.
  - *Develop, without a display.* A script: with
    `machinome.manager.develop.has_bundle` patched false, `Develop.handle`
    exits 1 with the viewer remedy, neither `Popen` nor `Process` called; and
    `Builder('simulation.lock:PinTumblerLock', watch=False,
    lifecycle=True).start()` (the change removes `scad_output`) in a
    subprocess into a scratch build directory: expected the 11 `Solid2Node`
    `.scad` files and no other, the set the fifth cycle's develop builder
    wrote and, after this change, what `machinome build` writes.
  - *Migration.* None expected. If anything must change, stop and report.
  - *Must not change:* anything in the bench or the framework; any project
    file.
- [ ] 10.2 **Engine absent, OpenAstroMount** (optional, the orchestrator's
  call on cost), read-only in `/home/asa/devel/machinome/projects/OpenAstroMount`
  with `PYTHONDONTWRITEBYTECODE=1`: `machinome build` into a scratch build
  directory with `solid2` unfindable (the finder, `absent=solid2`). Expected
  after: exit 0, `viewer.json`, every STL and BREP, no `.scad`, nothing
  logged about SCAD presentation. (Before: `ModuleNotFoundError` for
  `solid2`.)
- [ ] 10.3 **Shallow, the universe,** run by the orchestrator from the
  workspace root: `scripts/load-projects --bench <bench> --moved
  scripts/load-projects.d/exact-engine.toml
  scripts/load-projects.d/leaf-contract.toml
  scripts/load-projects.d/backend-switch.toml
  scripts/load-projects.d/lean-install.toml
  scripts/load-projects.d/expression-type.toml
  <bench>/openspec/changes/scad-presentation/moved-names.toml --timeout 300
  --json <bench>/openspec/changes/scad-presentation/load-projects.json`.
  Expected: no row for this cycle; carried: `3D-Printers/Voron-2`,
  `Actuators/Internal-Cycloidal-Actuator`, `Robots/YouCanBuildDog`,
  `Robots/openvmp` (`don1`) `expected`; `3DPrintedClocks` `wall_clock_41` and
  `Robotic-Arms/Dum-E` `unexpected`, pre-existing; six `no-model`. Any other
  row returns to the orchestrator with its output before integration.
- [ ] 10.4 A failed validation returns to the orchestrator with the
  project's output; nothing is fixed in a project. The orchestrator hands the
  reports to the paused applier.

## 11. Records, ADRs, specs, commit (the applier, after 10)

- [ ] 11.1 Fold 10.1-10.3 into the evidence, verbatim where they quote a
  message, a hash or a summary line.
- [ ] 11.2 Write ADR-172 (`docs/adrs/NODE/`, the core describes its SCAD
  presentation and the OpenSCAD engine writes it: the description, contract
  2, expressions as values, the binary through the seam; amends ADR-102's
  compatibility consumer, ADR-116's re-anchoring mechanism and ADR-171's list
  of direct reaches, which gain status lines and amendment sections) and
  ADR-173 (`docs/adrs/BUILD/`, SCAD is written only where it is read: a
  SCAD-authored leaf's `.scad` for its STL, the root's on demand by the
  OpenSCAD snapshot renderer in the build directory and removed by it once
  drawn, the builder no longer presenting, the sweep keeping a `.scad` by
  reference and applying that rule on every successful build, unchanged
  document included (the correction of 4 October 2026, with the applier's
  evidence of the sweep's trigger); option B recorded as
  rejected and why; `require_scad_engine` and its remedies; amends ADR-102's
  consequences, ADR-046's refusal family and ADR-086, whose assembly-phase
  coalescing loses its production producer), each recording the pilot's
  ruling on design.md Decision 3 (A, 3 October 2026) and the orchestrator's
  acceptance of Decision 6.
- [ ] 11.3 Sync the seven delta specs into `openspec/specs/`, archive the
  change with `openspec archive scad-presentation`, copy `moved-names.toml`
  to the workspace's `scripts/load-projects.d/scad-presentation.toml` (the
  orchestrator commits that copy in the workspace), validate `--strict`, and
  make the implementation commit on `v0.8-scad-presentation`.
