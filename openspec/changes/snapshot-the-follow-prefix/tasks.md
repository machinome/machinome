Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`.

- Every framework command runs as
  `env -C <bench> PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1 /home/asa/devel/machinome/.venv/bin/<tool> ...`.
- `<project>` is `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x`
  (branch `main`, head `1f3dc22` at Stage P). It is read and run, never
  written.
- `<scratch>` is the campaign scratchpad's `cycle8/` directory
  (`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle8/`).
  It holds Stage P's `repro.py`, `curta_measure.py`, `candidate.py`,
  `pytest_candidate.py`, `snapshot_microbench.py`, `test_red_probe.py`, and
  the scratch build directory `build/`.
- A Curta command runs as
  `env -C <scratch> PYTHONPATH=<bench>:<project> PYTHONDONTWRITEBYTECODE=1 SOLID_BUILD_DIR=<scratch>/build taskset -c 14 /home/asa/devel/machinome/.venv/bin/<tool> ...`,
  with `-p no:cacheprovider` for pytest, so nothing is written in the
  project.
- `<focused tests>` = `tests/test_follow_prefix_cache.py
  tests/test_running_follow.py tests/test_following_contact_repro.py`.
- `<corpus tests>` = `tests/test_running_corpus.py
  tests/test_clocked_corpus.py tests/test_time_drive_corpus.py`.

Rules for the whole cycle:

- One test run of ours at a time. Check first with
  `ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome snapshot\|[m]achinome build'`.
- Every test marked RED is run and seen red, for the reason it names,
  before the code that turns it green.
- Never write a committed corpus. If any task shows a level, landing,
  stop, bank or corpus value changing, stop: record the difference in
  `evidence.md` and report.
- Record every command and its result in `evidence.md` as you go, in the
  shape of `openspec/changes/archive/2026-10-06-keep-the-corpus-cursor-honest/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`), the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench) and the
  project head (`git -C <project> rev-parse --short HEAD`). Copy the
  sources of `<scratch>/repro.py` and `<scratch>/curta_measure.py` into
  `evidence.md`, because the scratchpad is not durable.
- [ ] 1.2 Run `<scratch>/repro.py` from the bench. Expect proposal.md's
  output: one walk, a miss `Propagation` with `follow_cuts`, a hit
  `mappingproxy` on which all six attributes raise `AttributeError`.
- [ ] 1.3 Run `pytest -q -p no:cacheprovider <focused tests> <corpus tests>`
  and record the counts and wall time.
- [ ] 1.4 Curta baseline, one run at a time:
  `pytest -p no:cacheprovider -q --durations=0 <project>/simulation/test_radial_positioning_ball.py`
  (Stage P: 4 passed in 260.98 s);
  `pytest -p no:cacheprovider -q --durations=0 "<project>/simulation/test_mechanistic.py::MechanisticCurtaTest::test_subtraction_borrows_through_both_registers_and_addition_undoes_it"`
  (Stage P: 1 passed in 212.17 s); and `python <scratch>/curta_measure.py
  bench` (Stage P: 178.676 s wall, bank SHA-256
  `167ea1cd4849c606a22e9457081c329495cd747f149ab19dbefa2288b18b1fcf`).
  Record counts, per-test durations, wall times and the SHA-256.

## 2. Red test

- [ ] 2.1 RED. Add design.md Decision 3's
  `test_a_reused_prefix_is_the_propagation_its_walk_produced` to
  `FollowPrefixCacheTest` in `tests/test_follow_prefix_cache.py`, after
  `test_exact_fraction_bits_and_distinct_edges_miss`, with
  `from machinome.simulation.trajectory import Propagation` among the
  imports. Run it on the unmodified code and record the failure line:
  `mappingproxy({...}) is not an instance of <class
  'machinome.simulation.trajectory.Propagation'>`.

## 3. The change

- [ ] 3.1 `machinome/simulation/trajectory.py`: add `from types import
  MappingProxyType` and design.md Decision 1's `FrozenPropagation` after
  `Propagation`.
- [ ] 3.2 `machinome/simulation/run.py`: import `FrozenPropagation` from
  `.trajectory` with the module's relative imports; in `_constraint_level`
  store `(FrozenPropagation(deltas), MappingProxyType(dict(landings)))`
  and continue with `deltas, landings = saved`, with design.md Decision 2's
  comment. Confirm `python -c 'import machinome.simulation'` from the
  bench still imports cleanly.
- [ ] 3.3 Run 2.1's test: green. Run `<focused tests> <corpus tests>`: the
  counts are 1.3's plus one test, and `git -C <bench> status --short tests/`
  lists only `tests/test_follow_prefix_cache.py`.

## 4. The Curta after the change

- [ ] 4.1 Rerun 1.4's three commands, one at a time. Record counts,
  per-test durations and wall times beside the baseline. The bank SHA-256
  must equal 1.4's. A wall time more than about 5% above the baseline is
  rerun once, both before and after, and the four numbers are recorded;
  the host's own spread was 4.6% between identical runs at Stage P.

## 5. Changelog and manual

- [ ] 5.1 Append this bullet to the one `Unreleased` section of
  `docs/project/changelog.rst`, after its existing bullets:

  ```rst
  * **A reused Follow prefix carries its paths.** When the two Bounds of a
    ``Follow`` target share one walk of their sub-program at a fraction of
    the stretch, the walk is stored as a read-only copy of the propagation
    it produced, with its source motions, Follow cuts and closures, and
    the walk that stores it reads the same copy. It used to be stored as a
    bare mapping of displacements, so a later Bound received a different
    kind of object than the first one. No level, stop or bank changes, and
    the Curta's crank tick costs the same (snapshot-the-follow-prefix).
  ```
- [ ] 5.2 Grep `docs/` (excluding `adrs/` and `releases/`) for
  `prefix_cache`, `prefix replay`, `MappingProxyType` and `Propagation`.
  Confirm that no page says something this change makes wrong, and
  record the result.

## 6. Warts

- [ ] 6.1 Move the bullet "**The Follow prefix cache stores mapping
  proxies where a propagation used to flow.**" of `workflow/warts.md`
  ("# Review of the cycles landed after the 0.7.0 fold (2026-09-23)"),
  verbatim through "...or assert the shape at the hit.", to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`, under a heading
  `` ## `snapshot-the-follow-prefix` `` after the last entry, with a line
  `From "Review of the cycles landed after the 0.7.0 fold (2026-09-23)":`.
  Add a "What shipped" paragraph: the stored prefix is a
  `FrozenPropagation` carrying the walk's displacements and every
  attribute, read-only; the publishing walk continues with it, so a hit and
  a miss hand the rest of `_constraint_level` one shape; the test was red
  first on `TwoSurfaces`; the Curta's banks are bit-identical and its tick
  time unchanged, with 4.1's numbers; no corpus changed. Delete the bullet
  from `warts.md`, leaving the section's other entries.

## 7. Checks

- [ ] 7.1 Run `black --check` and `flake8 --max-line-length=89` on
  `machinome/simulation/trajectory.py`, `machinome/simulation/run.py` and
  `tests/test_follow_prefix_cache.py`. A finding in a line this change did
  not touch is recorded, not fixed.

## 8. Sync and archive

- [ ] 8.1 Sync the delta into `openspec/specs/simulation/spec.md`,
  replacing "Equivalent Follow Bound prefix probes may reuse a successful
  propagation". Diff the requirement against its baseline: only the added
  paragraph and the added scenario differ.
- [ ] 8.2 Archive the change to
  `openspec/changes/archive/2026-10-06-snapshot-the-follow-prefix/`. Then
  `openspec validate --specs` passes.
- [ ] 8.3 Run 2.1's test, `<focused tests>` and `<corpus tests>` once more,
  then the full suite once, alone (`pytest -q -p no:cacheprovider` at the
  bench root), and record the counts and wall times. A failure that is not
  this change's is recorded and stopped on, not worked around. Leave
  everything uncommitted.
