# Finite profile contact: bounded evidence

This change is a pointwise numeric capability for an existing running Bound,
not an installed Curta contact law or a continuous-collision certificate.

## Origin and red proof

- Project: `projects/Calculators/Curta-Type-I-3x`; source-native four-cover
  probe `reverser-native-profile-cover-intersection-4035917.jsonl`, SHA-256
  `f81c846514f0432cacf9cfcf0158c344dc0dabe6091173d073d5d82cd7182c5e`.
  Native exact outside remainder was zero for these four exploratory source
  covers. Standalone mesh had positive outside remainder for both drum
  segments (5.579560203210584 and 5.620713790041652 mm³), so native-only
  covers are **not** accepted for project adoption.
- Native-plus-standalone-mesh exploratory four-cover input:
  `reverser-native-and-mesh-profile-cover-4035917.jsonl`, SHA-256
  `68ff82c84ff1faf157409b8a2e30708e71c63fd70d7c980f461a7b736c54577a`.
  Eight placed source-witness records:
  `reverser-native-and-mesh-profile-witnesses-4035917.jsonl`, SHA-256
  `6b2f0848a51abb9aff1cdc90ec4b2d13f8f904e2b25f9e4ea817647608b13b66`.
  Their one-tooth contact sequence is 0,0,1,0 and nine-tooth is 1,0,1,0.
- Old direct expression SAT would require 591 × 1072 = 633,552 pairs for one
  pinion/nine-tooth drum pairing. The retained `capped_sat_probe.py` is a
  byte-for-byte copy (SHA-256 `feba57d109e421ceb42013fef43f6113014dd599359b4f25a8b6c6d0d9e30b8e`)
  of the actual-data diagnostic, limited to 256 pairs/50,000 nodes/12 CPU s.
  It measured 3,343, 12,637, 25,029, 49,833 distinct graph nodes after
  16, 64, 128, 256 pairs. No full unbounded graph was attempted.
- Before implementation, tests failed on the missing public module/import,
  unavailable path node evaluation, running Bound symbolic-vocabulary refusal,
  absent v13 table, and missing current-source documentation. The first test
  assumed finite angle conversion could overflow; mathematical review proved
  multiplying finite binary64 by the specified factor <1 cannot, so the
  planning commit was amended to `8442918` and that test corrected before
  implementation validation. A late immutability regression also failed red:
  ordinary `del profile._polygons` succeeded despite assignment refusal.
  `ConvexProfile.__delattr__` now refuses deletion, and the focused profile
  suite passes without changing the v13 wire or numeric contact behavior.
  Final runtime source SHA-256 is
  `5e7a530f7f187de1b2fe763bc702d1350ebbf8d9aac4c260185bd4cf505e32f4`
  for `profile.py` and
  `4897001583bcc3f424c094dae23edcf8ccb44e83ff881447498f648c149cbb52`
  for `run.py`.

## Scoped producer and paired consumer checks

- Independent actual-data numeric run built four profiles from indexed native
  loops **plus separate explicit mesh loops**: 694/689/306/1222 polygons,
  2394/2374/1101/3866 vertices. Python and viewer both matched all eight
  source-witness 0/1 decisions; neither classified the huge-translation
  collapsed-edge case as clearance. Python per-pose CPU was .008–.051 s after
  .55 s four-profile construction; viewer .002–.046 s after .15 s load.
  These are bounded measurements, not whole-machine speed claims.
- Independent actual-cover symbolic probe measured 23 unique graph nodes per
  contact. A running Bound document contained two profile entries and a
  188-character scalar `profileOverlap(...)` expression; JSON was 302,353
  bytes. Reordering two polygons changed program identity, and restore under
  the changed table refused. The viewer loaded that actual-cover v13 document
  and reproduced the blocked .5 request and restore/retry. The paired small
  fixture `tests/fixtures/profile_overlap_v13.json` and exact IEEE-bit
  `profile_overlap_v13_outcome.json` are checked by both repositories.
- A separate project installed-cover performance trial (uncommitted at the
  time of measurement; subsequently checkpointed by the project) exposed
  repeat work, not a new solver requirement: one 0→18°/.1-s tick called the
  predicate 1,560 times, with 780 distinct exact pair keys, and prepared
  profiles 3,120 times although only 136 exact placement keys were distinct.
  Baseline CPU was 13.72 s. The framework's bounded per-integration cache
  candidate took 8.331651 CPU s and made only 136 `_placed` calls; ordered
  contact input/result SHA-256
  `46cdac2bff6972f1cf4f3b9ba2a2ac1204c3a306212cbb0fac2cc9eb31582cd4`
  and full 214-bank IEEE-bit SHA-256
  `3e44081383251e2e2c12b91a58f03336ff887a465e840b8a26d88788d686983d`
  matched the uncached baseline. A following zero-duration request prepared
  eight profiles in a fresh scope rather than inheriting the tick's cache.
  The paired viewer's separate installed-Curta one-tick check reported
  2.163→1.705 CPU s, 780 pair hits, 1,424 placement hits and 136 retained
  placements. It then loaded the pinned one-tick Python bank oracle
  (`/tmp/curta-installed-profile-one-tick-bank.json`, SHA-256 prefix
  `1872b5a9`), comparing the same program identity, command status,
  admitted bits, tick, zero stops and every one of 214 named IEEE-754
  coordinate bits. The shared canonical JSON `[name,bits]` SHA-256 was
  `c0eee932cdbd18a5b9384060aa104669b4d0ca7b17386323f6cce2ed9159ecf7`
  in both runtimes. The Python run's earlier `3e440813...` hash encoded
  names/bits differently, so those two aggregate hashes were never a valid
  direct equality test. Viewer implementation and full gate remain recorded
  by its own change.
  These single paired measurements support this local reuse only, not a
  general interactive frame-rate claim. Independent recursive
  `sys.getsizeof` instrumentation (not RSS, excluding program-owned profile
  objects) found ~0.50 MB in 780 pair entries and ~14.69 MB in 136 placed
  entries for this tick; the largest one placed value was ~0.60 MB. At the
  1,024/256 entry caps and this workload's largest-placement size, a rough
  bound is ~154 MB placements plus ~0.66 MB pair keys. There is no universal
  byte ceiling because the public profile itself has no arbitrary size cap;
  all entries are released at integration exit.
  The process-local installed-tick probe is retained byte-for-byte as
  `probe_curta_installed_performance.py`, SHA-256
  `74537ac2388a94feeab1feb820cbf1f84b77d5c42be5551079bc08df78a8b484`;
  it reads the exploratory 27-profile installed reference record SHA-256
  `d41e1b46ee7f4c92b61d2ddae586f01242574213942d7dd93f0e9c4aefad01a3`.
- The bounded two-case **source-cover** local trial was also paired under
  identical current project source hashes, input SHA, CPU10 and one already
  built `SOLID_BUILD_DIR`; only a process-local diagnostic context patch
  disabled reuse in the control (no repository rollback). Both modes passed
  the same two tests and made exactly 1,334 predicate calls. Cache-on took
  82.037 CPU s (Sim init 12.335, moves 3.654, run 63.078) with 757 placed
  preparations; cache-off took 121.934 CPU s (Sim init 13.282, moves 4.028,
  run 101.587) with 2,660 preparations. Cache-on had 659 pair and 733
  placement insertions across attempts, 377 distinct placement keys and no
  evictions. The 32.7% paired total CPU decrease is for these two tests,
  not a full-machine frame-rate claim. An earlier **unpaired** 119.394-s
  uncached run and 166.664-s candidate run used separate fresh build dirs;
  their contrary totals are retained as uncontrolled observations, not
  evidence of a cache regression or gain. `probe_curta_source.py --instrument`
  and `--uncached` retain the comparison seam without altering project or
  framework runtime source.
- Shared numeric/malformed conformance corpus:
  `tests/fixtures/profile_overlap_numeric_corpus.json`, SHA-256
  `6d381e9c31c8633e4f3618b2ea0506a53638a2551c032760271503cb0ab92483`.
  It includes inclusive shared edge/vertex, one-ULP strict gap, signed-zero
  result, huge finite angle, distant-AABB collapse refusal, repeated/zero
  edges, pentagram and valid collinear input. Producer focused tests passed
  17 tests and 14 subtests, including eager first-error order and failed-bind
  atomicity. Viewer paired corpus status is recorded by its owning cycle.
- Existing-source Curta local trial, run from project root with this worktree
  first on `PYTHONPATH`, reused the project's own local axial Bound acceptance
  methods with only its angular flag replaced. Both the long blocked request
  and alternate retained-phase withdrawal passed: 2 tests, 0 failures,
  0 errors, 119.394 CPU seconds (198.137 wall). The input was the exploratory
  four-cover SHA above; the trial used only its source-placed pinion/nine-drum
  pair at one crank/lift pose. It did not edit the project or adopt a
  production law. Project source hashes at completion: `running.py`
  `b183dc508ce308ce8acc8a075a3827fa26f0bdab1207138208faaec5e8b91484`,
  `reverser_contact_trial.py`
  `6c98d38d288ea55250bc8ab0a2842435562658d457c850344ba6d89e8354262e`.
  To reproduce after verifying framework main contains the tested archived
  change and checking the named project source pins, from the canonical Curta
  project root run:

  ```sh
  taskset -c 10 env SOLID_BUILD_DIR=/home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x/_build_checks/profile_contact_source_replay PYTHONPATH=/home/asa/devel/machinome-studio/machinome:/home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 /home/asa/devel/machinome-studio/.venv/bin/python /home/asa/devel/machinome-studio/machinome/openspec/changes/archive/2026-09-23-convex-profile-contact-predicate/probe_curta_source.py --profiles /home/asa/devel/machinome-studio/projects/Calculators/Curta-Type-I-3x/_build_checks/reverser-native-and-mesh-profile-cover-4035917.jsonl
  ```
- An incremental strict Sphinx HTML build (`python -m sphinx -b html -n -W
  --keep-going docs docs/_build/html`) passed and its rendered status and
  unreleased changelog show the current-source capability without altering
  released teaching pages. A **fresh** strict output-dir build, however,
  failed on three missing ignored example export directories (normally
  generated by `.readthedocs.yaml` pre-build jobs) and five unrelated
  pre-existing cross-reference warnings in `reference/api.rst`/`Sim`
  docstrings. A fresh strict build from **clean matching baseline**
  `d1638e2790155ddb683b4af6d9c54752d09ec3b9` reproduced the exact same
  eight diagnostics; the candidate reported no new profile/status/changelog
  warning. The ignored exports are generated in Read the Docs' documented
  pre-build jobs, which also install external packages and fetch source meshes;
  this local capability cycle did not download them or fabricate placeholders.
  The incremental green result is not presented as a clean fresh manual gate.
  The final-source full framework suite, run with the workspace venv as
  `.venv/bin/python -m pytest -q tests`, passed 3,655 tests, 4 skipped,
  2,153 subtests, 53 warnings in 455.00 s. It includes both the late
  post-placement SAT-failure cache regression and the deletion-refusal
  regression. All runtime source in the paired project tests and final
  framework suite used the whole-call uncertain-key fallback.

## Limits and project obligations

Pointwise 0/1 contact does not certify an unsampled path; the existing Bound
sampling/bisection behavior is unchanged. The project must still establish
complete installed-print cover (including axial slabs and actual posed
solids/meshes), retained-phase operating admission and performance before
adopting this flag. A separate installed-profile project trial is underway;
its findings do not become a framework success by implication. No CAD,
epsilon, mesh healing, timestep change, or universal tangency guarantee is
introduced here.
