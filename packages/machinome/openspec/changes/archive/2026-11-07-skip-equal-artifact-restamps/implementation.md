# Implementation and caller evidence

Completed implementation, 2026-11-07; root accepted WT caller evidence and
authorized closure. Local integration and installed plain delivery remain
root-owned and pending the exact two-commit handoff review.

Base: clean primary `main` at
`b0829b39809e64e889e56eb9bececa57cd3430ad`.
Planning-only commit: `750a361d0ff51c50063f3636f0258d6529f68fae`.
Managed WT/branch: `skip-equal-artifact-restamps`, slot 15.

## Implemented correction

Only `machinome/currency.py::restamp` changes production behavior. It uses
`operator.index` to preserve the existing ns integer/index admission protocol,
stats the artifact in its best-effort error boundary, and returns before
`os.utime` when integer mtime already exactly matches. Differing timestamps
retain the same utime operation. No tolerance, rounding, source-content shortcut,
record skip or guard weakening was introduced. `_content_verified`,
`currency.record`, `_artifact.py`, `core/pieces.py` and publication retries are
unchanged. No API, dependency, viewer/Studio, document-version or lamp change.

The index normalization followed root's bounded review finding: ordinary
`int == float` could otherwise admit an exactly equal float the prior
`os.utime(ns=...)` rejected. A targeted matching-float test failed against the
first equality shortcut and passed with the preserved index protocol.

## Red and green

- Two real source-owned matching-mtime fallback methods each exercise STL and
  BREP. Before the production edit, all four subcases raised the original
  `ArtifactChanged` at `ArtifactSnapshot.validate`, after digest/fingerprint
  upgrade assertions passed. `evidence/red.log`: pytest exit 1, four failed
  subcases/two method counters passed, 23 deselected, 4.51 s.
- Matching-float refusal red: `evidence/input-red.log`, one failure because
  TypeError was not raised by the first shortcut, 0.28 s.
- Final focused proof: five tests/four subtests passed, 23 deselected, 2.77 s,
  including best-effort stat/utime errors. `evidence/green.log`.
- Planned 12-module regression gate: **226 tests and 60 subtests passed**, no
  skips, five existing dependency/deprecation warnings, 22.57 s.
  `evidence/regressions.log`. This includes real changed-mtime STL/BREP,
  coarse-filesystem, source-content/fingerprint, recipe, migration, generation,
  replacement and persistent piece-fact boundaries. No broader suite was
  needed after these passed.

All native-backed tests used `/tmp/enigma-native-secondary-20261107.lock`.
The worktree owns its uv environment from the unchanged lock: Python 3.12.3,
Machinome/CQ-node/STEP-node/engines/viewer 0.9.0, CadQuery 2.7.0 and molejo 0.2.0.
Exact editable paths and source hashes are in `evidence/environment.json`.
Final currency source SHA-256:
`db79b8a7afad2b43a7e3a8e5b2a1d7cc2233e784ec3579e6cbfb4936886e142e`.
Original `_artifact.py` SHA-256:
`a5f386b92a20f59c6d2b432d90f46bf275095f2206314a7550187fdc76232547`.
Original `core/pieces.py` SHA-256:
`84a16d79e65b4ba64a3b5636a6d42fb9a8c336875c96570e27acf7e913609932`.

## Originating project

One ordinary canonical build ran from
`/mnt/data/machinome-projects/enigma-i`, frozen project
`60c6d8cb6193d67fecb410d0a1b0a8571938f37d`, using this worktree's executable
and its unmodified declared `CandidateMachineInspection` reference/build root.
It had no sitecustomize, syscall tracing or behavior hook. Source/assets/runtime
and source hashes were pinned; the secondary lock serialized native work.

Result: **exit 0 in 64.303 s**, no timeout, all inputs/core source unchanged,
all **543** referenced model byte hashes unchanged, and no `errors.json`.
Document SHA-256 stayed
`f6ffa7958cf787d2d5b06f246a11d380ef4b3851f8585756a653650629ddbf6a`.
Models-before/after ledger SHA-256 is identical:
`8fc7973666b99cbdb1b7a4f81115b872bcf1ef77e006b2c8a1f0525344816985`.
Receipt SHA-256:
`07f0ce28dffc55d3973f0190382def0266e106ddc74cedd02c03517c6bceec40`.

Raw project evidence remains durably under
`sources/derived/artifact-restamp-correction-v1/wt-core/`; exact copies are in
`evidence/enigma-wt/`. Only JSON/log/recipe metadata is retained here, not Enigma
geometry. Root reviewed and accepted this WT caller outcome before closure.

## Limits and handoff

This proves the independently justified no-op correction and one ordinary
WT-runtime build success. It does **not** identify the unknown delayed-ctime
writer or establish general filesystem causality. Prior failed/plain and
successful/traced receipts remain unchanged in the origin project. No build was
automatically repeated to obtain a pass, no cache was purged/rewritten by hand,
and no consistency guard was relaxed.

No ADR or architecture-synthesis update is warranted: this preserves accepted
exact currency/source/strong-identity architecture. The added build-pipeline
requirement makes no-op desired-state behavior explicit. The delta is synchronized
to the core baseline before archival; only that added requirement is merged.

Root owns the authorized clean-base fast-forward and the **one** ensuing plain
workspace-executable canonical build on frozen main `60c6d8c`. The shared core is
already editable at primary: inspect module resolution/source SHA after FF and
reinstall only if needed. Its post-integration receipt belongs to originating
project evidence and the final handoff; do not make a third framework commit or
claim installed delivery before that result. This agent will not integrate,
push, publish or implement the separate pending lamp API.
