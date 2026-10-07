Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratchpad>` is
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad`;
`<scratch>` is `<scratchpad>/cycle19` (the probe `probe_repro.py`, the
probe project `repro/`, the catalogue scan `scan_facades.py` and its logs);
`<copy>` is `<scratchpad>/I1/proj`, the investigation's scratch copy of
3DPrintedClocks, with its tools `<scratchpad>/I1/state.py` and
`<scratchpad>/I1/probe_pose.py`. `projects/3DPrintedClocks` is READ-ONLY:
it is only run, unchanged, with a scratch `SOLID_BUILD_DIR` and
`PYTHONDONTWRITEBYTECODE=1`; every edit experiment happens in `<copy>`.
One test run, build or snapshot of ours at a time: before each, check
`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`
in its own call. Every test marked RED is run and seen red, for the reason
it names, before the code that turns it green. Record every command and its
result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [x] 1.2 Run `pytest -q -p no:cacheprovider tests/test_source_set.py
  tests/test_files.py tests/test_source_closure_index.py`; record counts
  and wall time (Stage P: 26 passed in 4.90 s).
- [x] 1.3 Copy the sources of `<scratch>/probe_repro.py` and of every file
  under `<scratch>/repro/` into `evidence.md` (the scratchpad is not
  durable). Run the probe three times, one at a time, with fresh build
  directories (`SOLID_BUILD_DIR=<scratch>/build-a-<mode>`): unpatched,
  `FIX=1`, `FIX=naive` (design.md, Context, has the command); record each
  output. Expect design.md's three blocks.
- [x] 1.4 Copy `<scratch>/scan_facades.py` into `evidence.md` and rerun it
  (`python -B <scratch>/scan_facades.py`, stdout to a new log in
  `<scratch>/logs/`); record its summary and the per-project table of
  design.md, "What the catalogue loses". If a project other than the four
  named there appears, stop and report it before section 3.
- [x] 1.5 Unchanged project, baseline. With a fresh scratch build
  directory `<scratch>/build-real` and the unmodified bench, run in
  `projects/3DPrintedClocks` (read-only):
  `env -C /home/asa/devel/machinome/projects/3DPrintedClocks PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build-real PYTHONPATH=<bench> /usr/bin/time -v timeout 3000 /home/asa/devel/machinome/.venv/bin/machinome test wall_clock_22 --mesh --volume-epsilon 0.001 --set facing=0`,
  cold, then again warm. Record counts (expect 25 tests, 19 passed, 6
  failed, the six named in design.md), wall times, and
  `python <scratchpad>/I1/state.py save <scratch>/build-real <scratch>/logs/real-warm.json`
  after the warm run. Confirm with `git -C <project> status --short` before
  and after that the project is untouched (` M screenshots/wall_clock_03.png`
  and `?? WTs/` are not ours).

## 2. Red tests

- [x] 2.1 Fixture, `tests/source_set_project/` (each new file with the
  licence header the fixture's files carry):
  - `library/__init__.py`: a docstring saying it is a library facade
    beside the nodes, then `from .measures import *  # noqa: F401,F403`;
  - `library/measures.py`: a docstring, then `WIDTH = 3`;
  - `wide.py`: `class Wide(CadQueryNode)` rendering
    `cq.Workplane('XY').box(WIDTH, 2, 2)` from `from .library import WIDTH`,
    docstring: a leaf whose dimension comes through a sibling package's
    `__init__.py`;
  - `peg.py`: `class Peg(CadQueryNode)` doing `from . import dimensions`
    and rendering `cq.Workplane('XY').box(1, 1, dimensions.HEIGHT)`,
    docstring: reaches a sibling module through its own package, whose
    `__init__.py` is the root assembly;
  - `__init__.py`: import `Wide` and `Peg` beside the existing imports (the
    root assembly imports every node; `Assembly.render` unchanged), and its
    docstring's "the source walk must follow only the modules a statement
    names and never the package it traverses" becomes "never the package
    containing the module that imports through it".
- [x] 2.2 RED `tests/test_source_set.py`, `SourceSetTest`, the scenario "A
  module behind a sibling package's `__init__` is tracked":
  `test_a_module_behind_a_sibling_package_init_is_tracked` asserts
  `MEASURES` and `LIBRARY_INIT` are in `realpaths(Wide())` and
  `PACKAGE_INIT` is not (module constants beside `DIMENSIONS`). Red today:
  `MEASURES` is not in the set.
- [x] 2.3 RED same class,
  `test_editing_a_module_behind_a_sibling_package_init_invalidates_the_artifact`,
  in the shape of `test_editing_an_imported_module_invalidates_the_artifact`:
  build `Wide()`, assert `_up_to_date(stl_file)`; `edit_source(self,
  MEASURES)` and move its mtime 10 s ahead; a fresh `Wide()` is not up to
  date. Red today: it reports up to date. `setUp`/`tearDown` restore
  `MEASURES`'s times as they do `DIMENSIONS`'s.
- [x] 2.4 GUARD same class, the scenario "A package containing the importer
  is not followed": `test_the_importers_own_package_init_is_not_tracked`
  asserts `DIMENSIONS` is in `realpaths(Peg())` and `PACKAGE_INIT`,
  `os.path.realpath(Cyl().src)` and `os.path.realpath(Lonely().src)` are
  not. Green before and after. Its docstring says why `Cyl` cannot be this
  witness (`from .dimensions import` never offers the package; design.md,
  Context).
- [x] 2.5 GUARD, unedited: `test_package_init_is_not_tracked`,
  `test_unrelated_node_is_not_invalidated`,
  `test_library_modules_are_not_tracked` and the rest of 1.2.
- [x] 2.6 Run 1.2's set on the unmodified tree with 2.1-2.4 in place;
  record 2.2 and 2.3 red with their failure lines, everything else green.

## 3. The change

- [x] 3.1 `machinome/node/sources.py`, design.md Decision 1:
  `_parse_project_imports` passes `path` to `_project_file(name, root,
  importer)`; `_project_file` drops an `__init__.py` only when
  `os.path.commonpath((package, importer)) == package` for its package
  directory; its docstring names `importer`; the comment above the test is
  rewritten to say which `__init__.py` is dropped, which is followed, and
  why, naming this change. Nothing else in the file changes.
- [x] 3.2 Run 1.2's set: 2.2 and 2.3 green, 2.4 and 2.5 green; record.
- [x] 3.3 Rerun `<scratch>/probe_repro.py` unpatched against the changed
  bench with a fresh build directory; record that it now prints the
  `FIX=1` block of design.md.

## 4. Validation in the originating project

- [x] 4.1 Edit experiment on `<copy>` (fresh build directory
  `<scratch>/build-copy`): run the documented `machinome test wall_clock_22
  --mesh --volume-epsilon 0.001 --set facing=0` in `<copy>` cold; record
  counts and time; `state.py save` the build directory.
- [x] 4.2 In `<copy>/clocks/plates.py` (a scratch file; one Edit), change
  `self.bottom_pillar_r = self.plate_distance / 2` (around line 1356, under
  `if self.heavy:`) to `self.bottom_pillar_r = self.plate_distance / 2 +
  3.0`. Run `<scratchpad>/I1/probe_pose.py` in `<copy>` with
  `SOLID_BUILD_DIR=<scratch>/build-copy`; record that the pillar's STL on
  disk now has extents `[14.469, 37.096, 31.1]` and `up_to_date=True` after
  the build, and `state.py diff` against 4.1's record (expect the pillar
  STLs and BREPs and their records replaced, where the bench rewrote
  nothing). Measure the pillar BREP's extents with
  `cq.Shape.importBrep(<pillar .brep path>).BoundingBox()` (a small scratch
  script under `<scratch>`, its source copied into `evidence.md`): expect
  37.1, where the bench left 31.1.
- [x] 4.3 Revert the edit (one Edit), confirm with
  `diff -rq -x __pycache__ <copy>/clocks /home/asa/devel/machinome/projects/3DPrintedClocks/clocks`
  (no output), rerun the documented test in `<copy>`: 25 tests, 19 passed,
  6 failed; then once more warm and `state.py diff`: no artifact
  rewritten. Record times.
- [x] 4.4 Unchanged project against the changed bench, into 1.5's
  `<scratch>/build-real`: the documented test twice. The first re-derives
  the model once (record the `state.py diff` against
  `real-warm.json` and the time); the second rewrites nothing. Counts stay
  25/19/6. Project `git status --short` unchanged.

## 5. Words and records

- [x] 5.1 `docs/adrs/NODE/ADR-033-import-closure-source-set-and-up-to-date-leaf-path.md`:
  append design.md Decision 2's amendment section; extend the header's
  `**Amended by:**` line as written there. `docs/adrs/README.md`: ADR-033's
  entry gains `, amended 2026-10-07`.
- [x] 5.2 `docs/architecture.md`: the invariant sentence of design.md
  Decision 4. `grep -n "__init__" docs/architecture.md` afterwards: no
  other sentence states that the walk never follows a package's
  `__init__.py`.
- [x] 5.3 `docs/concepts/node-tree.rst`, "Freshness": the bullet of
  design.md Decision 4. `grep -rn "__init__" docs --include=*.rst` outside
  `docs/adrs/`: no other page states the old rule.
- [x] 5.4 `docs/project/changelog.rst`: design.md Decision 4's bullet under
  the existing `Unreleased` section. Run `tests/test_release_records.py`.
- [x] 5.5 `black --check` and `flake8 --max-line-length=89` on
  `machinome/node/sources.py`, `tests/test_source_set.py` and the new
  fixture files.

## 6. Findings record

- [x] 6.1 Move, verbatim, the entry "Generated-artifact freshness is not
  dependable for source-bound CAD leaves" from `workflow/warts.md`
  (section "3DPrintedClocks"; delete the section heading if the entry was
  its only one) to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## \`follow-a-sibling-packages-init\``, with a "What shipped"
  paragraph: the rule, the red-then-green tests, the probe, the copy's
  pillar edit (STL and BREP both 37.1 mm), the unchanged project's one
  rebuild and warm run, and the two halves that no longer reproduce with
  the investigation's measurements (the stale pose: placements are live;
  the retained path: the OpenSCAD-era `.scad` assemblies removed by
  `748d6d94`).
- [x] 6.2 In `warts.md`, "Planned, never done", delete the line
  "**Generated-artifact freshness** (3DPrintedClocks, the first entry).
  Investigation never started; ...", which this cycle closes.
- [x] 6.3 `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this
  cycle.

## 7. Sync, archive, suite

- [x] 7.1 Sync the two MODIFIED requirements into
  `openspec/specs/build-pipeline/spec.md` and
  `openspec/specs/source-closure-cost/spec.md` (`openspec archive
  follow-a-sibling-packages-init --yes`, or by hand and then
  `--skip-specs`); check each carried scenario appears once.
- [x] 7.2 `openspec validate --specs` passes, and the archived folder is
  `openspec/changes/archive/<date>-follow-a-sibling-packages-init/`.
- [x] 7.3 Run 1.2's set once more, then the full suite (`pytest` at the
  bench root, alone); record counts and wall time. A test that fails
  because a fixture node's tracked set grew (design.md, "What the
  catalogue loses", last paragraph) is reported with its reason, not
  edited to pass. Leave everything uncommitted and report.
