# Historical candidate implementation and validation

This is the earlier pre-v11 checkpoint, retained as chronological evidence.
Its pending gates, source hashes and primary HEAD are historical, not current.
See [completion-evidence.md](completion-evidence.md) for the final paired state.

2026-09-22. Uncommitted implementation after planning commit `5f90739`.
Not integrated, archived, published, or adopted into Curta. The viewer gate
is measured and unresolved; see `viewer-parity.md`.

## Implemented shape

`trajectory.py` carries request-local evaluators over the common request
fraction. Affine segments are exact endpoint representations only where the
folded, currently active branch proves them affine; curved segments retain
their evaluators. Restriction preserves the original timing. Evaluations are
memoized only inside that propagation. A fresh propagation is created for
each request, stop segment, and independent attribution replay.

Ordinary demanded sources and selected block members use those paths.
`_Walk` exposes the pieces it actually traverses, retaining jump subtraction,
far-side landing, and held inactive dependencies. An inherited breakpoint's
right boundary belongs to the preceding piece, so it cannot erase a landing.
Range probes and supported moving-contact samples consult those same paths.
An exact affine source retains the existing arithmetic fast path.

Play and its downstream observers remain on their existing clearance-aware
prefix executor; their net displacement is not labelled an affine path.
No project law, constraint, command, oracle, or source file was changed.

## Additional red/green evidence

- A new source-kink boundary regression initially found no recorded landing
  instead of one at request fraction .125. Inclusive ownership of that
  internal boundary now records it once; the focused selection/read/jump
  suite passed 141 tests and 422 subtests after the correction.
- A contact-observed compact carry on the unchanged framework base gives
  higher.turn 2 instead of 3.5. The candidate test gives 3.5 and checks that
  contact sampling makes zero prefix replays when all paths are available.
- Restricted curved-path queries are repeatable; a shared source evaluation
  is reused without advancing state. Restore/partition/reverse tests exercise
  fresh request-local paths rather than retaining the prior request's cache.
- The broader Play adversarial test caught an incorrect affine label on a
  downstream observer (dial 47.142857142853245 instead of 63). The explicit
  untraced-Play propagation guard corrects this; no expectation was changed.

Two existing expectations intentionally changed, rather than bulk-regenerating
goldens: `LandedCarry` higher.turn is 3.5 rather than 3 for the measured
simultaneous crank/selection movement, and its higher gate crossing is at
fraction .125 rather than .25. The gate opens when the lever physically reaches
.5, not halfway through an endpoint chord. The existing committed corpus and
document identity fixtures remain unchanged.

## Failed/interrupted exploratory runs

Earlier candidates treated inactive nonlinear branches as curved motion,
causing expensive repeated evaluation down the carry chain. Two diagnostic
runs using periodic faulthandler traces exited 139; their cause is not proved,
and they are not successful evidence. Later progress-only profiling, without
that tracing, identified the branch-classification issue. Superseded slow
prefix and constrained replays were explicitly interrupted; they are not
counted as passes. Constant/active-branch classification and reuse of already
determined contact paths removed the observed evaluation cascade.

## Independent project evidence, not executor acceptance

The previously launched native station-8 profile check completed 23,556 checks
with zero failures. The unadopted collar trial's arithmetic suite completed
three tests in 8,209.898 seconds. Those are independent results recorded in
the project `_build_checks/` logs. Neither proves this executor change or
authorizes a new default operating model. No whole-machine geometry or visual
acceptance is claimed; station-10/11 native checks and whole-machine adoption
remain outside this framework validation.

Final candidate replay records and timings are retained under `evidence/`.
Each public-API replay names the three production-file SHA-256 values and
prints full banks, status, admitted travel, and per-request wall time.
Tests run with the worktree first and unchanged canonical Curta repository
second on PYTHONPATH, using the workspace virtual environment. Concurrent
workers make wall times observational, not a controlled benchmark.

## Final validation at this pause

- Unchanged Curta diagnostic suite: **4 passed in 89.878 s**, versus the
  base's one pass and three failures. Every bulk request reaches crank 180,
  ones 724, tens 704, and first lever 0. Full output is retained in
  `evidence/candidate-tests-final.json`.
- Framework running, document/corpus, selection, self-read, jump, stop, Play,
  following-contact, contact-proof, ancestor-constraint and periodic-constraint
  suites: **543 passed, 699 subtests passed in 45.86 s**. The two existing
  render/driver deprecation warnings remain. No committed corpus was changed.
- Final constrained eleven-station replay: the bulk and twelve-portion final
  banks match bit for bit, every request completes, and each run admits 90.
  The bulk move takes 15.865 s; preparation plus both replays takes 61.665 s.
  Complete banks and exact source hashes are in
  `evidence/candidate-constrained-final.json`.
- Final six- and seven-station bulk moves take 7.556 s and 9.251 s;
  preparation plus bulk takes 16.809 s and 19.153 s respectively.
  See `evidence/candidate-prefixes-final.json`.
- The earlier unconstrained whole/partition comparison also matches every
  bank float exactly; its distinct, pre-contact-reuse hashes are retained in
  `evidence/candidate-full-partition.json`, not relabelled as final content.
- Strict OpenSpec validation and `git diff --check` pass. Planning commit
  remains the sole commit above the recorded base. Implementation remains
  uncommitted; 12 of 16 tasks are checked, with viewer disposition and the
  completed-record phase still pending.

The three final production SHA-256 values are:

```
d01ad13cbe1adf0e9d92a912701b3beadc4ed5570a837bd85d140e5ef294fbd0  program.py
938adcd2cc09536e4b1c0bf2ae1c929c91ea1f83e5c7c2aff5b42486eacc4bff  run.py
a399c5fb2ad54cd29499d15fd2fe137baebd7842c1183e1e5e2fda2031c4dda2  trajectory.py
```

Curta's diagnostic test, running laws, and carry-constraint reproduction hashes
still equal the base evidence in `red-curta.json`. The project has only its
two pre-existing untracked media files; the viewer worktree remains clean;
framework primary remains at `e6a42c8` with its unrelated untracked
`docs/examples/v8-engine/` preserved. No repository was integrated or pushed.
