Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Framework commands run as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle17/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle17/`),
which holds the Stage P scripts `networkx_hidden.py`, `red_test_sketch.py`,
`repair_count_survey.py` and `so_arm100_mesh.py`. `<project>` is
`/home/asa/devel/machinome/projects/Robotic-Arms/SO-ARM100` (branch
`frames-and-mates`), read only: never edit, build or commit in it, never
address it through `/mnt/data`, never `cd` into it. One build or test run of
ours at a time (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` first). Record every command and its result in
`evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`; the
scratchpad is not durable, so copy outputs verbatim.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome,
  trimesh; print(machinome.__file__, trimesh.__version__)'` prints a path
  under the bench and `4.4.9`), and `pip show trimesh networkx` (Stage P:
  trimesh requires only numpy; networkx 3.6.1 is required by nothing).
- [x] 1.2 `env -C <bench> HIDE_NETWORKX=1 PYTHONPATH=<bench> <venv>/python
  <scratch>/networkx_hidden.py` and the same with `HIDE_NETWORKX=0` (Stage
  P: with `networkx` refused, the four open fixtures raise
  `ModuleNotFoundError` at `repair.py:261 fill_holes` through the assertion
  and `_body_count`, while `repair=False` counts 1, 1, 1, 2; with it present
  every count is the expected one at both `repair` values). Record the
  table of design.md, Context, 3.
- [x] 1.3 `env -C <bench> TMPDIR=<scratch>/tmp PYTHONPATH=<bench>
  <venv>/python <scratch>/red_test_sketch.py` (Stage P: exit 0, both lines
  `ModuleNotFoundError`).
- [x] 1.4 SO-ARM100 baseline: `touch <scratch>/project-marker`; then, one at
  a time, `env -C <bench> PYTHONPATH=<bench> <venv>/python
  <scratch>/so_arm100_mesh.py simulation/<suite>.py` for `parts`,
  `hardware`, `so_arm100`, each once as written and once with
  `--hide-networkx`; then `find <project> -newer <scratch>/project-marker
  -not -path '*/.git/*'` (must print nothing) and `git -C <project> status
  --short` (must be empty). Stage P: present 4/5/12 passed, 0 failed;
  refused 3 passed 1 failed, 5 passed, 11 passed 1 failed, both failures
  `ModuleNotFoundError`. Record each summary line, failing test and time.
- [x] 1.5 `pytest -q -p no:cacheprovider tests/test_connectivity.py
  tests/test_mesh_engine_dependency.py`; record the counts and time.
- [x] 1.6 Read the repair survey's result into evidence: `tail -1` of
  `<scratch>/repair_count_survey.log` if it still exists, else re-run
  `env -C <bench> PYTHONPATH=<bench> <venv>/python
  <scratch>/repair_count_survey.py` (stdout and stderr to a log in
  `<scratch>`; about 85 s). Stage P: `465 meshes, 157 not watertight, 0
  counts differ, 0 errors`.

## 2. Red tests

- [x] 2.1 `tests/test_connectivity.py`: add the fixture helpers
  `open_box(missing=1)`, `open_tube()` and `open_pair()` beside `one_body`
  and `two_bodies`, as design.md, Decision 3 describes.
- [x] 2.2 Add class `CountWithoutRepairTest` with
  `test_open_meshes_are_counted_where_networkx_is_absent`,
  `test_counts_are_the_bodies_the_mesh_holds` and
  `test_counts_match_the_repairing_split` (skipped unless `networkx` is
  importable), as design.md, Decision 3 describes.
- [x] 2.3 Run the class: the first test fails on `ModuleNotFoundError`
  (record the failure output verbatim); the other two pass, and the third
  ran rather than skipped. Record.

## 3. The change

- [x] 3.1 `machinome/test.py`: `_body_count` splits with
  `only_watertight=False, repair=False`, with the docstring of design.md,
  Decision 2.
- [x] 3.2 `machinome/test.py`: `assertNoDisconnectedSolids`'s mesh branch
  reads `bodies = _body_count(cached_base_mesh(solid.stl_file))`.
- [x] 3.3 Run `CountWithoutRepairTest`: all three green, the third not
  skipped. Record.

## 4. Green and validation

- [x] 4.1 Repeat 1.2 and 1.3 on the changed tree: with `networkx` refused,
  every fixture is decided through the assertion and `_body_count` (1, 2,
  1, 1, 1, 2) and no `ModuleNotFoundError` appears; with it present, the
  output equals the baseline's. Record before and after side by side.
- [x] 4.2 Repeat 1.4 with a fresh marker: every refused run equals its
  present run (4, 5 and 12 passed, 0 failed); every present run equals its
  baseline; the project is untouched. Record the six summary lines and
  times before and after.
- [x] 4.3 Repeat 1.5: every test green, the new ones counted.

## 5. Docs and changelog

- [x] 5.1 `docs/project/changelog.rst`, under `Unreleased`, after the
  existing bullets: the bullet of design.md, Decision 4, ending
  `(count-bodies-without-repair)`.
- [x] 5.2 `pytest -q -p no:cacheprovider tests/test_release_records.py
  tests/test_docs_structure.py`: green.

## 6. Records

- [x] 6.1 `workflow/warts.md`: move the entry "**`networkx` is an
  undeclared need of the mesh path.**" from the section "YouCanBuildDog"
  ("Framework" list) verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under a heading
  naming `count-bodies-without-repair` and its section of origin, with a
  "What shipped" paragraph: the repair dropped from both counts, why the
  count cannot move, the fixtures and the 465-file survey, SO-ARM100's
  refused runs before and after, and the red test's name. The section keeps
  its other entries.
- [x] 6.2 `workflow/ongoing/fix-warts-3.md`: a Progress line for this cycle
  after the last one.
- [x] 6.3 `openspec/specs/test-framework/spec.md`: sync the delta, the
  requirement "Connectivity assertions" replaced whole, every carried
  scenario kept and the new one added.
- [x] 6.4 Archive the change to
  `openspec/changes/archive/<date>-count-bodies-without-repair/`; run
  `openspec validate --specs` and record the result.
- [x] 6.5 `black --check` and `flake8 --max-line-length=89` on
  `machinome/test.py` and `tests/test_connectivity.py`, compared against
  `HEAD`; the focused tests of 4.3 once more; then the full suite once,
  alone (`pytest -q -p no:cacheprovider` at the bench root). Record the
  counts and the time. Leave everything uncommitted.
