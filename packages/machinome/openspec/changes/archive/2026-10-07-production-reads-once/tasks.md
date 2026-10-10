Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
  with `-p no:cacheprovider` for pytest.
- `<scratch>` is the campaign scratchpad's `cycle10/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle10/`).
  It holds Stage P's `repro_doubling.py`, `repro_assemble.py`,
  `repro_missing.py` and `test_draft_red.py`, a `pyproject.toml` that gives
  them a project root, their `.before.out` logs, and `curta-overlay/`.
  Scratch scripts run as
  `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/python <scratch>/<script>`.
- `<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
  branch `main` (`1f3dc22` at Stage P). `<scratch>/curta-overlay/` holds a
  copy of the production slice's `production/` package from the worktree
  `<project>/WTs/production-layer-3x` (`7c9121e`), its `__pycache__`
  directories removed and the one line
  `from machinome.node import AssemblyNode, StepNode` of
  `production/test_production.py` rewritten as
  `from machinome.node.assembly import AssemblyNode` and
  `from machinome.node.step import StepNode`; beside it, symbolic links
  `simulation`, `pyproject.toml` and `CAD` to the same names in
  `<project>` (the test hashes those sources by its own file's location).
  If the scratchpad has lost it, rebuild it that way. The Curta command,
  `<curta>`, is:

  ```sh
  env -C <scratch>/curta-overlay PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="<bench>:<project>:<scratch>/curta-overlay" \
    SOLID_BUILD_DIR=<scratch>/curta-build \
    /usr/bin/time -f 'wall %e s' /home/asa/devel/machinome/.venv/bin/python \
    -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp \
    --rootdir=<scratch>/curta-overlay \
    <scratch>/curta-overlay/production/test_production.py
  ```

  Nothing is written in the project: check `git -C <project> status
  --short` before and after each Curta run; it lists the same 4 untracked
  entries.
- `<focused>` = `tests/test_model_consumption.py tests/test_production.py
  tests/test_production_documentation.py`.

Rules for the whole cycle:

- Run one test run or build of ours at a time.
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- Write nothing in any project. Record every command and its result in
  `evidence.md` as you go, in the shape of
  `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench), the Curta's
  head (`git -C <project> rev-parse --short HEAD`) and the slice's head
  (`git -C <project>/WTs/production-layer-3x rev-parse --short HEAD`).
  Copy the sources of `<scratch>/repro_doubling.py` and
  `<scratch>/repro_missing.py`, and the overlay recipe above, into
  `evidence.md`, because the scratchpad is not durable.
- [x] 1.2 Run `<scratch>/repro_doubling.py` (filter out its ` INFO -`
  lines). Expect `<scratch>/repro_doubling.before.out`: one operation and
  content `f435a10c` in the facade-only, lifecycle-only and
  facade-then-lifecycle orders; two operations and a regenerated content
  `fd3b003d` in the lifecycle-then-facade order, for `Pair` and `Holder`.
  Run `<scratch>/repro_assemble.py`: `b.operations 1 -> 2` for both.
- [x] 1.3 Run `<scratch>/repro_missing.py`. Expect
  `<scratch>/repro_missing.before.out`: `ModelInputChangedError: input
  observation failed` from `Production(model)` and `ModelSnapshot(model)`,
  for the root's files and the child's.
- [x] 1.4 Run the slice's own README command from its worktree, with the
  scratch build directory:
  `env -C <project>/WTs/production-layer-3x PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="<bench>:<project>/WTs/production-layer-3x" SOLID_BUILD_DIR=<scratch>/curta-build /home/asa/devel/machinome/.venv/bin/python -m pytest -q -p no:cacheprovider --basetemp=<scratch>/curta-basetemp production/test_production.py`.
  Record its collection error (`ImportError: module 'machinome.node' has
  no attribute 'AssemblyNode'`), the reason the overlay is used.
- [x] 1.5 Run `<curta>`. Record counts and times (Stage P: `6 passed in
  119.02s`, wall 120.10 s, warm build directory).
- [x] 1.6 Run `pytest -q -p no:cacheprovider <focused>` and record counts
  and time (Stage P: `52 passed, 4 warnings in 7.55s`).

## 2. Tests

- [x] 2.1 In `tests/test_model_consumption.py`, after
  `test_rigid_rest_placements_reused_by_normal_lifecycle`, add `MeshBox`,
  `OffsetPair`, `HeldPair` and
  `test_binding_after_a_build_keeps_rest_placements`, parametrized over
  `OffsetPair` and `HeldPair`, as design.md Decision 4 gives them. RED
  today for both parameters at the first operations comparison
  ("Left contains one more item: <machinome.node.operations.Translation
  …>").
- [x] 2.2 In the same module, add
  `test_missing_source_is_refused_at_construction` (RED today with
  `ModelInputChangedError: input observation failed`) and
  `test_source_deleted_after_binding_is_still_a_change` (guard, green
  today), as Decision 4.
- [x] 2.3 In `tests/test_production.py`, after
  `test_bad_constructor_inputs_fail_immediately`, add
  `test_missing_model_source_is_refused_at_binding`, as Decision 4. RED
  today with `ModelInputChangedError`.
- [x] 2.4 Run the five new test cases on the unmodified code:
  `pytest -q -p no:cacheprovider tests/test_model_consumption.py -k
  "binding_after_a_build or missing_source or deleted_after_binding"
  tests/test_production.py -k missing_model_source` (or the equivalent
  node ids). Record each failure line: four red for the reasons named, one
  green.

## 3. The change

- [x] 3.1 `machinome/model.py`, `ModelSnapshot.occurrences`, the
  non-assembly branch of `walk`: reuse `_prepared_rendered` when it is set,
  render under the structure-only flag only when it is not, validate both,
  as design.md Decision 1.
- [x] 3.2 `machinome/model.py`: `import errno`, and in
  `ModelSnapshot._capture_existing` the check before `observe_input`, as
  Decision 2.
- [x] 3.3 `machinome/production/profile.py`, `Production.__init__`: the
  reworded `except OSError` branch, as Decision 3.
- [x] 3.4 Run the five new test cases: all green. Run `<focused>`: 1.6's
  count plus five, all passing.
- [x] 3.5 `git -C <bench> status --short` lists only
  `machinome/model.py`, `machinome/production/profile.py`,
  `tests/test_model_consumption.py`, `tests/test_production.py` and the
  change directory.

## 4. The reproductions and the originating project after the change

- [x] 4.1 Run `<scratch>/repro_doubling.py`: one operation and content
  `f435a10c` in all four orders, the regenerated content included, for
  `Pair` and `Holder`. Run `<scratch>/repro_assemble.py`:
  `b.operations 1 -> 1` for both. Record the output.
- [x] 4.2 Run `<scratch>/repro_missing.py`: `ProductionExportError:
  RootProduction cannot bind: Root 'Root' names an input file that does
  not exist: <path>` and `FileNotFoundError` naming `Root 'Root'` for the
  root's files; the same naming `Nut 'nut'` for the child's. Record the
  output.
- [x] 4.3 Run `<curta>` again against the same build directory. Expect
  1.5's counts. Record the times beside 1.5's, and the unchanged
  `git status --short`.

## 5. Records

- [x] 5.1 Append design.md Decision 5's bullet to the one `Unreleased`
  section of `docs/project/changelog.rst`, after its existing bullets.
- [x] 5.2 Grep `docs/` (excluding `adrs/` and `releases/`) for
  `ModelSnapshot`, `ModelInputChangedError`, `ProductionExportError`,
  `missing` and `render()` near "once". Confirm that no page says
  something this change makes wrong, and record the result
  (`docs/reference/api.rst`'s production and model-consumption paragraphs
  are expected to stay true).

## 6. Warts

- [x] 6.1 Move the two items of the section "## Findings from the
  adversarial review of the framework cycle `production-layer` (4 October
  2026)" of `workflow/warts.md` verbatim, from "- **Defect: binding a
  production after a build doubles the placements of" to its
  "**Untriaged.**", and from "- **A missing input file at binding escapes
  `Production(model)` as the facade's own error.**" to its
  "**Untriaged.**", to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`.
  Put them under a heading `` ## `production-reads-once` ``, after the
  last entry, with a line "From "Findings from the adversarial review of
  the framework cycle `production-layer` (4 October 2026)", items 1 and
  2:". Add a "What shipped" paragraph: the walk reads a built rigid
  internal node from preparation's render; the facade refuses a missing
  source with `FileNotFoundError` and `Production(model)` with
  `ProductionExportError`, both naming the node and the path; the red
  tests and the guard; the reproductions before and after; the Curta
  slice's counts and times, through the overlay, and why the overlay.
  Delete the two items from `warts.md`; the section's introduction and
  other items stay.
- [x] 6.2 File design.md Open Questions 2 and 3 in `warts.md` as a new
  section "## Findings from the framework cycle `production-reads-once`
  (2026-10-07)", after the section "## Findings from the framework cycle
  `clocked-snapshot-identity` (2026-10-07)". Two bullets, each with its
  facts and "**Untriaged.**": **A missing source on a child that only
  `render()` creates still reads as a changed input** (met by the lazy
  structural walk, not at construction; the Stage P reproduction from
  `<scratch>/test_draft_red.py::test_render_created_child_missing_input_at_first_read`
  prints `ModelInputChangedError input observation failed:
  /nonexistent/render-made.txt`; confirm it after the change), and **A
  source changed between a verified load and binding escapes
  `Production(model)` as `ModelInputChangedError`** (confirm with a
  scratch run in the shape of
  `VerifiedModelGenerationTest.test_changed_executed_source_cannot_be_bound_as_verified`,
  binding a `Production` instead of a `ModelSnapshot`, and record the
  output). If the orchestrator's review answered either question
  otherwise, follow the answer.

## 7. Sync and archive

- [x] 7.1 Sync the deltas into `openspec/specs/model-consumption/spec.md`
  and `openspec/specs/production-assets/spec.md`, replacing the three
  modified requirements. Diff each against its baseline: each differs only
  in its added sentence and its added scenario.
- [x] 7.2 Archive the change to
  `openspec/changes/archive/<date>-production-reads-once/`. Then
  `openspec validate --specs` passes.
- [x] 7.3 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/model.py`, `machinome/production/profile.py`,
  `tests/test_model_consumption.py` and `tests/test_production.py`.
- [x] 7.4 Run `<focused>` once more, then the full suite once, alone
  (`pytest -q -p no:cacheprovider` at the bench root), and record counts
  and wall time. A failure that is not this change's is recorded and
  stopped on, not worked around. Leave everything uncommitted.
