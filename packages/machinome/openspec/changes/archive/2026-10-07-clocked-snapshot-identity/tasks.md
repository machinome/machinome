Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`.
- `<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`,
  branch `main`. Every Curta command runs as
  `env -C <scratch> PYTHONPATH=<bench>:<project> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build /home/asa/devel/machinome/.venv/bin/<tool> ...`,
  with `-p no:cacheprovider` for pytest. Nothing is written in the
  project. Check `git -C <project> status --short` before and after each
  Curta run: it lists the same 4 untracked entries.
- `<scratch>` is the campaign scratchpad's `cycle9/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle9/`).
  It holds Stage P's `repro_bench.py`, `probe_tests.py`,
  `curta_restore.py` and `curta_bounds.py`, a `pyproject.toml` that gives
  the first two a project root, and their `.before.out` logs.
- `<focused>` = `tests/test_clocked_sim.py tests/test_clocked_identity.py
  tests/test_clocked_time.py tests/test_clocked_corpus.py`.

Rules for the whole cycle:

- Run one test run or build of ours at a time.
- Every test marked RED in section 2 is run and seen red, for the reason
  it names, before the code that turns it green.
- `tests/clocked-corpus.json` stays byte-identical. Write nothing in
  `machinome-viewer` or `videomaker`.
- Record every command and its result in `evidence.md` as you go, in the
  shape of `openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [x] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench) and the
  Curta's head (`git -C <project> rev-parse --short HEAD`; `1f3dc22` at
  Stage P). Copy the sources of `<scratch>/probe_tests.py` and
  `<scratch>/curta_restore.py` into `evidence.md`, because the scratchpad
  is not durable.
- [x] 1.2 Run `<scratch>/probe_tests.py` from the bench. Expect
  `<scratch>/probe_tests.before.out`: model equal, identity different for
  the changed range and law, and all three restores accepted.
- [x] 1.3 Run `<scratch>/curta_restore.py` on the Curta. Expect
  `<scratch>/curta_restore.before.out`: three restores accepted, the
  second and third with identities other than the first's.
- [x] 1.4 Run `pytest -p no:cacheprovider -q --durations=5
  <project>/simulation/test_event_driven.py::EventDrivenOperationsTest` on
  the Curta, under `/usr/bin/time -f 'wall %e s'`. Record counts and
  times (Stage P: `11 passed, 57 subtests passed in 36.50s`, wall 37.56 s).
- [x] 1.5 Run `pytest -p no:cacheprovider -q <focused>` and record counts
  and time (Stage P: `145 passed, 195 subtests passed in 6.11s`).

## 2. Tests

- [x] 2.1 In `tests/test_clocked_identity.py`, add the imports
  `from machinome.motion.joints import Revolute`,
  `from machinome.simulation import State` (beside `Driver, Sim`) and
  `from .clocked_project.counter import DIGIT, advance, strokes` (beside
  `Counter, Stateless`). Add `skipping` and `restated` at module level as
  design.md Decision 3 gives them.
- [x] 2.2 RED. Add class `SnapshotIdentityTest(BaseNodeTest)` with
  `test_a_snapshot_carries_the_machines_identity`, as design.md
  Decision 3, test 1. Red today with `AttributeError`.
- [x] 2.3 Guard. Add `test_a_snapshot_restores_into_the_same_machine`, as
  Decision 3, test 2. Green today.
- [x] 2.4 RED. Add `test_a_machine_whose_range_changed_refuses_the_snapshot`,
  as Decision 3, test 3, with the two precondition assertions first. Red
  today with `ValueError not raised`, the preconditions passing.
- [x] 2.5 RED. Add `test_a_machine_whose_commit_law_changed_refuses_the_snapshot`,
  as Decision 3, test 4. Red today with `ValueError not raised`.
- [x] 2.6 Run `pytest -p no:cacheprovider -q
  tests/test_clocked_identity.py::SnapshotIdentityTest` on the unmodified
  code. Record each failure line: three red for the reasons named, one
  green.

## 3. The change

- [x] 3.1 `machinome/simulation/clocked.py`, `ClockedSnapshot`: the slot,
  the third constructor argument and the docstring of design.md
  Decision 1.
- [x] 3.2 `Clocked.__init__` (`self.initial`) and `Clocked.snapshot()`
  pass `self.identity`.
- [x] 3.3 `Clocked.restore`: replace the `model` comparison with the
  identity comparison and message of design.md Decision 2. The
  `isinstance` check and `self._posed(...)` are unchanged.
- [x] 3.4 `tests/test_clocked_sim.py::BoundTest::test_a_restore_whose_pose_is_refused_changes_nothing`:
  take
  `saved = sim.snapshot()` and build
  `ClockedSnapshot(saved.model, {'crank': 0.0, 'value': 3}, saved.identity)`.
  Its assertions are unchanged.
- [x] 3.5 Run `tests/test_clocked_identity.py::SnapshotIdentityTest`: four
  green. Run `<focused>`: 1.5's counts plus four tests, all passing.
- [x] 3.6 `git -C <bench> status --short tests/` lists only
  `tests/test_clocked_identity.py` and `tests/test_clocked_sim.py`, and no
  corpus file.

## 4. The originating project after the change

- [x] 4.1 Run `<scratch>/curta_restore.py` on the Curta. Expect the fresh
  instance accepted with result digits `[4, 1, 0, 0]`, and the changed
  range and the other module each refused with `ValueError` naming
  `EventDrivenCurta(...)` and both identities. Record the output.
- [x] 4.2 Run 1.4's command again. Expect the same counts. Record the
  times beside 1.4's.
- [x] 4.3 Run `<scratch>/probe_tests.py` from the bench. Expect the same
  machine accepted and the two variants refused.

## 5. Records

- [x] 5.1 `docs/architecture.md`: the clause of design.md Decision 4 in
  the clocked bank paragraph.
- [x] 5.2 Append design.md Decision 4's bullet to the one `Unreleased`
  section of `docs/project/changelog.rst`, after its existing bullets.
- [x] 5.3 Grep `docs/` (excluding `adrs/` and `releases/`) for
  `ClockedSnapshot`, `restore` and `snapshot` near `clocked`. Confirm that
  no page says something this change makes wrong, and record the result.
  `docs/concepts/joints.rst:645-648` is expected to read true now.

## 6. Warts

- [x] 6.1 Move item 4 of the section "# Three findings from filming the
  clocked Curta (1 October 2026, found by Videomaker's curta-video
  campaign)" of `workflow/warts.md` verbatim, from "4. **The framework's
  clocked snapshot carries no identity, the viewer's does.**" to "Found
  by `sim-identity` (its `evidence.md`, finding 1).", to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`. Put it under a
  heading `` ## `clocked-snapshot-identity` ``, after the last entry, with
  a line "From "Three findings from filming the clocked Curta (1 October
  2026, found by Videomaker's curta-video campaign)", item 4:". Add a
  "What shipped" paragraph: the snapshot carries the identity, `restore`
  compares it, the three red tests and the guard, the Curta's script
  before and after, and the Curta's operation tests' counts and times.
  Delete the item from `warts.md`; the section's other items stay.
- [x] 6.2 File design.md Open Question 1 in `warts.md` as a new section
  "## Findings from the framework cycle `clocked-snapshot-identity`
  (2026-10-07)", after the section "## Findings from the framework cycle
  `keep-the-corpus-cursor-honest` (2026-10-06)". One bullet, **A declared driver or
  state range is neither enforced on a clocked bank nor part of the
  clocked identity**, with the facts: the scratch run's identities for a
  changed state range and a changed driver range; `Sim(Counter(),
  state={'units': 15})` accepted; the identity's definition in the export
  spec and ADR-128 lists compiled joint bounds only. Add
  "**Untriaged.**", unless the orchestrator's review answered otherwise.

## 7. Sync and archive

- [x] 7.1 Sync the delta into `openspec/specs/simulation/spec.md`,
  replacing the two modified requirements. Diff each against its baseline:
  "A clocked simulation solves a request path event by event" differs
  only in the `restore` clause; "A clocked simulation publishes its
  machine's identity" differs only in its last paragraph and the three
  added scenarios.
- [x] 7.2 Archive the change to
  `openspec/changes/archive/<date>-clocked-snapshot-identity/`. Then
  `openspec validate --specs` passes.
- [x] 7.3 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/simulation/clocked.py`, `tests/test_clocked_identity.py` and
  `tests/test_clocked_sim.py`.
- [x] 7.4 Run `<focused>` once more, then the full suite once, alone
  (`pytest -q -p no:cacheprovider` at the bench root), and record counts
  and wall time. A failure that is not this change's is recorded and
  stopped on, not worked around. Leave everything uncommitted.
