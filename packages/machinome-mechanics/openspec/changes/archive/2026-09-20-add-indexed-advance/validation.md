# Indexed advance validation

## Package

Planning commit `4dfa22034262b6e6052e2c12dd96de0957204432`.
Tested uncommitted `machinome_mechanics/indexing.py` SHA-256
`9fe0bbbc644b1e87cb86a1c87c9af61741bc70965300b90ebe62ad33aad6b5f6`.
All commands used workspace Python, the cycle root on PYTHONPATH and
OPENBLAS_NUM_THREADS=1 / OMP_NUM_THREADS=1.

- Red: focused collection failed ImportError before indexed_advance existed.
- Formula implementation passed its fourteen new tests. First full run had
  197 passes and the expected documentation inventory failure until the new
  manual entry was added. Final full `python -m pytest -q`: 198 tests and
  24 subtests passed in 2.15 s, under 768 MiB address-space, 45 CPU and
  60 wall-second limits.
- Tests cover signed/multiple turns, five shifted origins, callback-once and
  absolute phase, current Pascaline numeric stroke, offset/discontinuous
  callbacks, signed/zero increments, nonlinear independent divmod oracle,
  callback exception identity, actual Solid2 angle and all-operand expressions.
- Strict Sphinx doctests: 160 passed, 2.28 s, 141112 KiB maximum RSS, in sole
  systemd unit indexed-parent-doctest with MemoryMax=768M, MemorySwapMax=0,
  RuntimeMaxSec=60. No warning or error in final run.
- Strict HTML `python -m sphinx -q -b html -n -W --keep-going docs
  /tmp/mechanics-indexed-html`: passed under 768 MiB address-space/45 CPU/60 wall.
- `python scripts/check-dist`: wheel/sdist builds, strict metadata and both
  installed numeric/deferred smokes passed outside the checkout under
  768 MiB address-space/90 CPU/120 wall. Uploads nothing; no shared repointing.
- Four strict OpenSpec items and git diff --check passed.

Independent Sol review verified source hash, formula, frames, callback and
continuity contract, actual deferred all-operand tests and both live consumer
adapters. Focused tests repeated 14/14 in 0.16 s under 768 MiB address-space,
60 wall seconds and threads1. A first command incorrectly named a nonexistent
bench-local venv; the corrected workspace executable passed. This is not a
product failure. No blocking defect found. Review explicitly excludes arbitrary
Python callback support, nonfinite input validation, mechanical callback
geometry certification and CAD (those are not package test claims).

Framework/viewer remained clean at
`8d2bd71171be81f13ba5dd492851ed8b3a9ababb` and
`4355da1a7f64dacd7d86eb27dbdfdf7ced94598f` around package checks.

## Earlier-cycle integration audit

Independent Sol read-only audit verified all eleven prior package integration
commits are ancestors of mechanics main at 44f9e649; all eleven archives have
validation records and completed tasks, and all eleven new requirements are
in the baseline. All 45 recorded consumer adoption commits across 20 distinct
repositories exist and are ancestors of their recorded original branch refs.
The four metadata follow-ups also remain on those original main branches.
This checks ancestry, not equality with an older commit after later cycles.
No inconsistency found; no project import, CAD or mutation was used by the audit.

This is not a claim that every historical full project suite passed: archive
records retain Thor and Dragon baseline failures, Kossel's preserved projection
defect, Prusa and Kossel unrelated tests, renderer fallbacks, Spiderbot's
faceted-only CAD coverage, Albert's packaging gap, Strand's legacy executable
gap and bounded-run limits for CycloidalDrive and Leonardo. The final campaign
ledger must distinguish affected helper evidence from full-project certification.

## Consumers

Both Sol migrations and bounded empirical gates passed. CAD imports/probes/
tests/builds/captures were serialized under the same 768 MiB process-tree,
zero-swap, threads1 cap, never increased (300 wall seconds maximum per gate).
Parent repeat probes used 60-second service limits. No unrelated astrarium
process was touched.

### Deepseek sawmill

Original main base `15fdf591411c20a7f88138d4b9c5bb5d1d1b2800`;
Sol commit `52160e1510f1295709023f36a5c5010d3247b3e2` on
mechanics-indexed-advance. The original hook/min/clamp/asin solve is retained
in `_ratchet_stroke`; only completed-turn accumulation is delegated. The
four-turn reset stays outside, rev_phase stays for pawl lift, and all geometry,
controls, harmonic and rolling helpers are unchanged. Existing source README
is still applicable; tool-only pyproject has no distribution manifest to edit.

- `scripts/check-indexed-advance`: nineteen actual bound signed/seam/reset
  numeric inputs, seven repeated model reposes and eight actual bound deferred
  evaluations passed against independently restated old math. 3.80 s,
  525556 KiB RSS.
- `machinome test --exact simulation/test_feed.py`: 5/5, 3.47 s,
  527612 KiB; root exact: 10/10, 12.18 s, 608824 KiB.
- Root build plus fresh OpenSCAD image passed together in 12.00 s,
  526212 KiB. Normalized time 0.9340277777777778 corresponds to wheel angle
  1345 degrees, inside the reset. Parent inspected
  `_build/indexed-advance-reset.png`: coherent wheel/sash/rod/bed/carriage/log;
  feed is occluded, so exact ratchet/reset evidence comes from laws and tests,
  not the whole-machine image.
- Parent reviewed complete adapter/probe/doc diff and raw gate summaries.
  Record: `docs/indexed-advance.md`; logs outside build are
  /tmp/leonardo-indexed-advance-probe.log,
  /tmp/leonardo-indexed-advance-feed-exact.log,
  /tmp/leonardo-indexed-advance-root-exact.log and
  /tmp/leonardo-indexed-advance-build-image.log.
- Parent independently repeated the actual native probe after consumer
  completion: pass in 3.39 s, 526060 KiB RSS, indexed-parent-sawmill unit.

### Pascaline-module

Original main base `576dc6baad4b41223357659b31041f79d8a95dd0`.
Sol consumer commit `84012b7bd09a7fb41b5ace5b59547bff0a7cb1f3` on
mechanics-indexed-advance, clean and unmerged at final review.
The pure local segment callback retains current one-segment 325..359 geometry,
36-degree throw, zero lead and origin325; handed_on delegates only turn
accounting. Two multisource carried-column laws and trailing idler are
unchanged. Forty-tooth geometry, controls and source transforms are unchanged.
Metadata adds machinome-mechanics>=0.1.0, with already-compatible Python>=3.12;
README now explains founded source use without stale campaign-worktree claims.

- `docs/probes/indexed_advance.py`: independent old loop, eighteen signed/seam
  numeric values, eighteen one-call/absolute-phase checks, 54 actual deferred
  values across both multisource carry relations and trailing idler (nonzero
  independent entry coordinates), seven direct reposes and three chained/
  replay states. Includes drums (342,342,18) -> (360,360,36) -> exact midcarry
  return. Passed in 4.01 s, 499716 KiB RSS.
- Native full Pascaline root faceted 37/37 (228.25 s test, 232.00 wall,
  675264 KiB) and exact 37/37 (227.84 s test, 231.46 wall, 662380 KiB) passed.
  Includes independent contact/clearance, wrong-gain mutation, arithmetic,
  repeated entry, carry/replay and ratchet admission contracts. Separate module
  and standalone-ratchet suites were not rerun; no broader suite claim.
- Root build passed in 142.95 s, 517152 KiB RSS.
- Fresh web rest (9.45 s, 500444 KiB) and units_entry=9.5 midcarry (142.80 s,
  429080 KiB), covers/bases off, passed. Parent inspected both: coherent exposed
  three-column train, visible driven drum/gear change. Occluded contact is
  established by CAD contracts, not asserted from pixels.
- Initial web --projection=ortho was rejected (0.23 s, 40352 KiB); the custom
  negative camera was then forwarded as a separate --view argument and rejected
  (132.17 s, 523140 KiB). Default-camera captures succeeded; neither package
  nor framework/viewer was modified to fix these out-of-scope tooling issues.
- Logs/images retained outside build in ignored `_evidence/indexed-advance/`:
  probe.log, root-faceted.log, root-exact.log, build.log,
  snapshot-rest-unsupported-projection.log, snapshot-rest.log,
  snapshot-rest-default-camera.log, snapshot-midcarry.log, rest.png,
  midcarry-9.5.png. Commands/source identity/limits are in
  `docs/indexed-advance-verification.md`.
- Parent read all adapter, metadata, README, probe and evidence changes,
  strengthened both actual multisource/deferred and chain/replay coverage,
  checked raw results and independently reran the retained probe: pass in
  3.71 s, 525640 KiB RSS, indexed-parent-pascaline unit.

Final framework/viewer heads remain clean at the identities above. The new
baseline requirement is synced and byte-for-byte compared with its delta;
four strict OpenSpec items and diff-check pass. Local guarded integration and
post-merge checks follow archival; final campaign ledger records their exact
commits and outcomes separately, without claiming integration in advance.
