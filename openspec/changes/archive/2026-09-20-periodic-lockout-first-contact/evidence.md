# Periodic lockout first-contact evidence

Date: 2026-09-20. Implementation and caller acceptance complete; archived,
not integrated.

## Identity

- Framework base: `8d2bd71171be81f13ba5dd492851ed8b3a9ababb`.
- Ratified planning commit: `c2023b146856c0b6516f04e69a6e92fb7bc152a0`.
- Branch/worktree: `periodic-lockout-first-contact`, under framework `WTs/`.
- Curta: `c76f230836ce3a91cc960564a1e1f0b3a7e9232b`, `direct-operation`, actual
  root `/mnt/data/machinome-projects/Calculators/Curta-Type-I-3x`.
- Workspace venv: `/home/asa/devel/machinome-studio/.venv`.
- Commands use the isolated framework first on `PYTHONPATH`, single-threaded
  BLAS/OMP and an 8 GiB virtual-memory cap. No viewer or primary-framework edit.

## Red first and framework checks

The original source-backed diagnosis and measured levels are in
`workflow/docs/curta-periodic-lockout-first-contact.md`.

- Added framework reproduction before runtime edits: **10 failing cases,
  4 passing tests, 2.25 s**. Failures include both bound directions, endpoint
  returning to equal or lower clearance, later revolutions, replay and retry.
  Failures are the real `StopInvariantError`, not a mocked expected value.
- Unmodified focused baseline: **169 tests + 135 subtests pass, 10.01 s**
  (`running_stops`, retained-coordinate delivery, running time drives, corpus,
  play and ancestor constraints).
- Initial implementation against that baseline plus new reproduction:
  **175 tests + 143 subtests pass, 9.69 s**.
- New corpus-coverage refusal was proved red: **1 failure, 10 tests + 8
  subtests pass, 1.36 s**, before adding its coverage rule and fixture.
- Regenerated running corpus: **23 scenarios, 20 machines, 381 ticks,
  295,783 bytes**. Existing scenarios have no changes; the periodic case is
  added. Corpus and periodic suite: **29 tests + 81 subtests pass, 2.11 s**.
- Mutation test restores the old endpoint-only group selection in process:
  the new producer case raises the original invariant; restored implementation
  replays it successfully. Coverage mutations remove the case, its actual
  stop, blocked outcome, long target or replay and must be refused.
- Additional tests cover time admission and retry without clock stoppage,
  simultaneous contacts, relieving and disengaged candidates, transactional
  failure and the still-refused compound-only push.
- Full framework suite: **3,488 tests + 2,011 subtests pass; 4 skipped,
  53 warnings; 409.79 s**. Warnings concern deprecated backend/legacy test
  APIs and legacy render-time reads, not failures of this contact path.
- Final expanded focused matrix (including the last two candidate tests and
  a second time-drive retry tick added during the full run): **233 tests +
  153 subtests pass, 9.32 s**. Includes periodic contacts, running stops,
  corpus, running time drives and their corpus, play/review, ancestor
  constraints and clocked bounds.

## Actual Curta

`python -m unittest simulation.test_periodic_lockout -v`:
**4/4 pass, 77.521 s**. Fixed-long, periodic-short, periodic-long and
periodic-timed all stop correctly with the ones shaft retained at 189.6°.

Broader acceptance `python -m unittest simulation.test_result_locking -v`:
**6/6 tests pass, 466.480 s**. This includes all five flats and later
revolutions with exact snapshot replay, .05° backward relief, idle retention
and retry; the immediate long request; normal complete tooth passages;
five different withdrawal phases; numerical agreement of the two profile
forms; and four legal 1080° requests, including subtraction height.

Tested executor SHA-256 (`machinome/simulation/run.py`, including final
comments): `fc10530b15c2003adf1d351192808bcfc650ff38d92313324dad4789d06d920f`.

The separate `evidence/curta_contact.py` records actual admitted poses then
checks complete printed parts in the native and faceted kernels; it is a
cycle diagnostic, not a new framework dependency or mechanical law.

Seven actual long-request admitted poses (all five flats and withdrawals
115°/123°) pass complete-part geometry: **14/14 zero-volume intersections**
across native OCCT and published faceted meshes. A separate posed .2°
overtravel produces positive overlap in **14/14 negative controls**, ranging
from 0.000224114 to 0.002518215 mm³. No positive volume is discarded.
Raw results: `evidence/curta-contact.jsonl`. Motion was run first using the
diagnostic's `--motion-only` option; its seven emitted values were passed
unchanged to the same sequential kernel loop. The default diagnostic runs
both stages together and reproduces this check.

OpenSCAD snapshots rendered and inspected at actual crank
125.22323837227304°, shaft 189.60000000000002°:

- Project `_build_running/periodic-stop-iso.png`, camera
  `0,0,0,55,0,25,250`.
- Project `_build_running/periodic-stop-axis.png`, camera
  `0,0,0,0,0,0,250`.

Both use `simulation/ones_lockout.py:OnesLockoutBench`, `--autocenter
--viewall --projection ortho --imgsize 1200x900` and the two `--drive`
values above. They show the complete bell and keyed ones upper stack in the
expected common frame without detached material. The images do not resolve
the exact angular clearance; the complete-solid/mesh checks establish it.
Images and build artifacts remain ignored in the project, not vendored here.

ADR-135 records the implemented decision and amends ADR-113; the index,
architecture synthesis and running-simulation documentation are updated.
Corpus SHA-256: `4d937550b5fb5d5d6bc6b9e5f51428cb4cc106edab2286bb54975470c0005cc1`.

## Cycle closure

Both affected baseline requirements were synchronized and compared in full
against their ratified deltas. All **34 baseline specs validate strictly**.
The supported archive command preserved `.openspec.yaml` and moved the cycle
to `openspec/changes/archive/2026-09-20-periodic-lockout-first-contact/`.
At archive time all 14 implementation/acceptance tasks were complete; its
two still-open checkboxes were the archive operation itself and final
validation/commit bookkeeping, completed as part of closure rather than
represented as finished beforehand. Specs were not skipped semantically:
`--skip-specs` avoided reapplying the already synchronized, verified content.

The selected integration target remains clean framework `main` at `8d2bd71`.
After archival, corpus regeneration is byte-identical and the final focused
matrix again passes **233 tests + 153 subtests, 9.61 s**. All 34 baseline
specs again validate strictly and the Git whitespace check is clean.
Integration and worktree teardown require separate authority and are not part
of this archived implementation result. No push, release or viewer change.

## Consumer boundary and secondary observation

The producer's corpus is the viewer handoff. No viewer mutation or browser
parity is claimed, and the general Curta restraint remains experimental and
unselected by its manifest. This cycle does not complete operating Curta.

While adding replay evidence, the existing corpus generator and replay helper
were observed to retain their record-list cursor across `restore()`, although
restoration clears the run's records. An immediate new stop in the same script
step is therefore omitted from that step's corpus log. No runtime fix is
implied: direct snapshot tests compare the real records correctly. The new
corpus scenario restores on its own step, records that state, then reissues
the long request on the next step, so both real stops are present. The corpus
cursor finding is deferred; no unrelated harness behavior is changed here.
