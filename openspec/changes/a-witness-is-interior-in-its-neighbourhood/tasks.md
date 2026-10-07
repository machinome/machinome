Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`.
`<scratch>` is the campaign scratchpad's `cycle18/` directory
(`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle18`),
holding `test_neighbourhood_sketch.py`, `neighbourhood_patch.py`,
`astro_pair.py`, `curta_measure.py` and `probe_sphere.py`. Projects are
read-only: run them with `PYTHONDONTWRITEBYTECODE=1` and a `SOLID_BUILD_DIR`
under `<scratch>`, and confirm `git status --short` and `HEAD` unchanged
after each. Voron-2 is not run. One test run or project run of ours at a
time; check `ps -eo pid,args | grep '[p]ytest\|[m]achinome test'` first.
Every test marked RED is run and seen red, for the reason it names, before
the code that turns it green. Record every command and its result in
`evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import machinome;
  print(machinome.__file__)'` prints a path under the bench). Copy into it
  the sources of `<scratch>/astro_pair.py`, `<scratch>/curta_measure.py` and
  `<scratch>/neighbourhood_patch.py` (the scratchpad is not durable).
- [ ] 1.2 Run `pytest -q -p no:cacheprovider tests/test_brep_common_guard.py
  tests/test_resolved_brep_witness.py tests/test_engine_package.py`; record
  counts and wall time (Stage P, the first two files: 13 passed, 7 subtests
  passed).
- [ ] 1.3 OpenAstroMount before: in
  `/home/asa/devel/machinome/projects/OpenAstroMount` on
  `exact-engine-validation` (`58e46cd`), `env -C <project>
  PYTHONPATH=<bench> PYTHONDONTWRITEBYTECODE=1
  SOLID_BUILD_DIR=<scratch>/astro-build /usr/bin/time -v
  /home/asa/devel/machinome/.venv/bin/machinome test --brep
  --no-verdict-store simulation/mount.py`; record the summary line, the
  failing test and witness, the wall time and `uptime`'s load average
  before and after (expected 8 passed, 1 failed, `BrepCommonInconsistency`
  at `(-2.0242287706088176, 265.5583117280026, 442.97547336608244)`).
- [ ] 1.4 Run `<scratch>/astro_pair.py <scratch>` from the bench with the
  same environment; record (Stage P: bench refused after 27.6 s, proposed
  returned 0 solids after 36.9 s, one resolved candidate rejected).
- [ ] 1.5 Run `<scratch>/curta_measure.py <scratch>` from
  `/home/asa/devel/machinome/projects/Calculators/Curta-Type-I-3x` with
  `PYTHONPATH=<bench>:<project>`, `PYTHONDONTWRITEBYTECODE=1` and
  `SOLID_BUILD_DIR=<scratch>/curta-build`; record (Stage P: both ±0.2 mm
  pairs refused by bench and proposed at the same witnesses, design.md
  Context table).

## 2. Red tests

- [ ] 2.1 Write `tests/test_witness_neighbourhood.py` with the four tests of
  design.md, Proof plan: a lone inside reading is not a witness (the sketch
  in `<scratch>/test_neighbourhood_sketch.py`, first class);
  `_resolved_interior` reports the margin; an undecided neighbour refuses;
  a slab of shared interior is still refused, its witness inside the slab.
- [ ] 2.2 Run the file on the unmodified tree. RED: the first with
  `BrepCommonInconsistency` at `(5.7735026918962585e-05, 0.999942264973081,
  0.24994226497308103)`; the second because `_resolved_interior` returns
  `True`; the third with `BrepCommonInconsistency` where
  `BrepCommonVerificationError` naming `UNKNOWN` is expected. GREEN: the
  slab. Record the output. If a test is not red for its stated reason, fix
  the test, not the expectation, and record why.

## 3. The change

- [ ] 3.1 `machinome/engine/brep.py`, `_resolved_interior`: return `None`
  where it returned `False`, and the smallest face distance where it
  returned `True`; docstring says so (design.md, Decision 1).
- [ ] 3.2 Same file, `_false_empty_witness`: classify through one local
  reading shared by the search and the neighbours; keep each IN solid with
  its own classifier; for a candidate IN both, measure margins, drop the
  unresolved, and accept the candidate only when, for some resolved pair,
  the six axis points at half the smaller margin are IN that pair's two
  solids; otherwise continue the search. Docstrings of `_false_empty_witness`
  and `intersect_shapes` name the neighbourhood.
- [ ] 3.3 Nothing else in the engine changes: the stencil, budget, order,
  messages and errors are as before.

## 4. Green

- [ ] 4.1 Run `tests/test_witness_neighbourhood.py`,
  `tests/test_brep_common_guard.py`, `tests/test_resolved_brep_witness.py`,
  `tests/test_engine_package.py` and `tests/test_verdict_store.py`; all
  green, the two guard files unedited. Record.
- [ ] 4.2 `black --check` and `flake8 --max-line-length=89` on
  `machinome/engine/brep.py` and `tests/test_witness_neighbourhood.py`.

## 5. Project validation

- [ ] 5.1 OpenAstroMount after: the command of 1.3; expect 9 passed. Record
  the summary line, wall time and load averages; confirm the project's `git
  status --short` and `HEAD` unchanged and its `_build` untouched.
- [ ] 5.2 Re-run `<scratch>/curta_measure.py` against the changed bench: its
  `bench` lines now run the real implementation; both ±0.2 mm pairs must
  still be refused. Record; confirm the Curta project unchanged.
- [ ] 5.3 Record in evidence that Voron-2 was not run, and why (design.md,
  Proof plan).

## 6. Records

- [ ] 6.1 `docs/adrs/TEST-FRAMEWORK/ADR-142-a-shared-interior-witness-refuses-an-empty-exact-common.md`:
  add "## Amendment — 2026-10-07: A Witness Is Interior in Its
  Neighbourhood" after the first amendment: the OpenAstroMount reading, the
  neighbourhood rule and its reason, the skipped candidate, the Curta pairs
  still refused, link to this change's archived evidence.
  `docs/adrs/README.md`: ADR-142's index line notes it is amended
  2026-09-23 and 2026-10-07.
- [ ] 6.2 `docs/architecture.md`, the guard paragraph (around line 2428):
  the witness's six neighbours at half its smaller face distance must be
  inside both too; a contradicted candidate is skipped.
- [ ] 6.3 `docs/reference/assertions.rst`, the `intersect_shapes`
  paragraph: the same, in one clause added to the witness sentence.
- [ ] 6.4 `docs/project/changelog.rst`, one bullet under `Unreleased`: an
  empty common is no longer refused on one inside reading that its own
  neighbourhood contradicts; OpenAstroMount's bearing seat is clearance;
  name the change (a-witness-is-interior-in-its-neighbourhood).
- [ ] 6.5 Move the warts entry "OpenAstroMount — a scenario test refused by
  the exact common guard (3 October 2026)" verbatim from `workflow/warts.md`
  to `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under a heading
  naming this change, with a "What shipped" paragraph (including that
  Voron-2 was not re-run).
- [ ] 6.6 Record in `workflow/warts.md` what the orchestrator decides on
  design.md's Open Questions 1 and 2 (the Voron-2 re-run owed; the shallow
  sphere blind spot), if the orchestrator so decides.

## 7. Sync, archive, final checks

- [ ] 7.1 Sync the delta specs into `openspec/specs/brep-engine/spec.md` and
  `openspec/specs/test-framework/spec.md`.
- [ ] 7.2 Archive the change to
  `openspec/changes/archive/<date>-a-witness-is-interior-in-its-neighbourhood/`;
  `openspec validate --all` (or the archived change's specs) passes.
- [ ] 7.3 Focused tests of 4.1 once more, then the full suite once, alone
  (`pytest -q -p no:cacheprovider` at the bench root); record counts and
  wall time.
- [ ] 7.4 Leave everything uncommitted and report.
