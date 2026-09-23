# Evidence — exact absolute running endpoint

The originating Curta project is `projects/Calculators/Curta-Type-I-3x`, on the
unchanged `CompiledReverserTrial` mechanical graph. Its browser-preparation
oracle reported nine direct requests in
`_build_checks/reverser-asymmetric-browser-da9808a-04.json`: after a
completed `reverser_height.move(to=-4.9425)` and a completed crank request,
`reverser_height.move(to=3.9075)` reported `blocked` even though its bank was
one binary64 unit beyond the inclusive target. The first absolute move also
landed one unit beside its stated target. This was command endpoint arithmetic,
not a new contact tolerance or a reverser geometry finding.
The cycle branched from framework `8d0fd15`; the paired viewer cycle began
from viewer `b976a17`. The final project oracle ran on project `85c8710`.

The public minimal reproducer in `tests/test_absolute_move_target.py` uses a
running `Driver` and `Prismatic` with an inclusive upper Bound at `3.9075`.
The old code stored only `target-current` and reconstructed its terminal as
`current+delta`: from `-4.942499999999999`, adding `8.85` yields
`3.9075000000000006`, falsely outside. The new code retains the once-converted
target separately from the unchanged delta/interior ramp. Red-first controls
covered static and reading Bounds, both rounding directions, signed zero,
timed/snapshot/replay, actual earlier stops, `by` unchanged, and malformed
optional snapshot sidecars. Later controls covered a legal sqrt endpoint whose
rounded additive endpoint was outside its domain, a comparison-cut law, a
selected cyclic block, a Play-to-curved-law chain, Follow, and 63 interior
fractions across a wrapped-law second request. A huge builtin integer target
own-snapshot is accepted without converting it to float.

No tolerance, post-hoc status relabel, geometry waiver, solver sample change,
or project-specific branch was added. The exact target is offered only on a
full successful `to` terminal propagation; a stopped partial segment is
replayed on its legacy travel. In a running planned law, the endpoint remains
an integrated value across the authored cuts, not a static pose.
For a final restricted planned piece, `Sources.along()` reads the actual
restricted Motion at each point; the retained source delta is used only as a
nonzero movement flag for jump-path construction, not as substitute point
arithmetic. The multicut running tests and the mismatched-endpoint Wrapped
second-request interior bit corpus pass; no separate partial-cut defect was
reproduced.

## Gates

- Pre-final adjacent running matrix: 153 tests and 496 subtests passed
  (`tests/test_absolute_move_target.py`, `test_running_follow.py`,
  `test_running_play.py`, `test_running_jumps.py`, `test_running_paths.py`,
  `test_running_reads.py`).
- First full framework suite on an earlier candidate: 3,678 passed,
  4 skipped, 2,167 subtests, 53 warnings in 409.58 s. This is not the
  final-source gate because the scoped Follow/Play terminal guard and
  huge-integer snapshot check were subsequently refined.
- Final-candidate full suite: 3,680 passed, 4 skipped, 2,230 subtests,
  53 warnings in 402.94 s (`taskset -c 11 .../.venv/bin/python -m pytest
  -q tests --tb=line`). This ran against the frozen runtime hashes below;
  `tests/test_running_document.py::ByteIdentityTest` compares unaffected
  published document bytes to committed base fixtures.
- Final hosted Curta report06: nine Python/browser statuses and each of
  their 214 named IEEE-754 bank bits agree; the exact-target withdrawal
  completes, retry/replay/relief agree, and the actual lever pointer sequence
  C,C,B records the expected stop at `1.0594999999999941` with no browser
  errors. JSON:
  `projects/Calculators/Curta-Type-I-3x/_build_checks/reverser-asymmetric-browser-85c8710-06.json`
  SHA-256 `3a77aeec6f3779b11fa6aaf23602aaecdd23e3a3782ce82ab2b15e311d0cc433`;
  inspected PNG SHA-256
  `71aed3d5e7182aa9d824ec5f74483a82d2765f4d47e3b30bf342db730a18d97b`;
  terminal log SHA-256
  `ed24b500ddfc2c656772e8eec8f2f7f73f89091d76e4ee34936d7a8e620a102f`.
  Producer runtime hashes below; viewer bundle SHA-256
  `41bd9f1ea95162e8cbbaafef8a247f84cada95ff63082533dce2cdc91e77d58e`.
  Program graph/source geometry were unchanged.
- Merged-base validation remains for local integration after this cycle's
  implementation commit.

The previous hosted Curta paired report
`_build_checks/reverser-asymmetric-browser-ffafa3f-05.json` (SHA-256
`a01dd2374990b641b24fafb239269f1c410ef4397b621190b8d88d61e1d47afa`)
passed all nine Python/JS statuses and all 214 named coordinate bits, including
the newly completed final withdrawal, and the actual pointer C,C,B sequence.
It imported an earlier endpoint candidate, so it is evidence of the design
seam, not acceptance of the final runtime source. Report06 above supplies
that final-source paired acceptance.

Final-candidate runtime SHA-256:
`machinome/simulation/run.py`
`95a7f23420fa9e67c1b94d1e3446bead1f07380e0ac94b2cc322f1f239d5fa01`,
`machinome/simulation/trajectory.py`
`96483106789792d99a9413beb9e585b2eab5e64063778ec583d327d46d2bd679`.
During report06, a brief alternative `_sources` guard was written and then
reverted to this exact source hash. The report process had imported the
frozen module before the temporary disk edit; its nine Python stages had
already printed before the discrepancy was noticed. No claim rests on that
transient variant. A read-only call-path review found that `Sources.along()`
uses the actual restricted Motion for point values; the stored movement flag
does not substitute an oversized endpoint delta. No concrete defect was
reproduced and the frozen source was retained.
